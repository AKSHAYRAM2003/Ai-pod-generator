from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
import logging
import json

from app.models.user import (
    User, RefreshToken, EmailVerificationToken, PasswordResetToken, 
    UserPreferences, AuditLog, UserStatus, AuditLogAction
)
from app.schemas.auth import (
    UserRegistrationRequest, UserLoginRequest, UserProfileResponse,
    UserRegistrationResponse, EmailVerificationResponse, UserLoginResponse,
    TokenRefreshResponse, EmailVerificationRequest, PasswordResetRequest,
    PasswordResetVerifyRequest, GoogleOAuthRequest, GoogleOAuthResponse,
    UserResponse
)
from app.core.security import SecurityUtils
from app.core.config import settings
from app.core.exceptions import (
    ValidationException, ConflictException, NotFoundException, 
    AuthenticationException, AppException
)
from app.services.email_service import email_service


logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for user management with verification codes"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register_user(
        self, 
        registration_data: UserRegistrationRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserRegistrationResponse:
        """Register a new user and send verification code"""
        try:
            # Validate input data
            await self._validate_registration_data(registration_data)
            
            # Check for existing user
            await self._check_user_exists(registration_data.email, registration_data.username)
            
            # Create user
            user = await self._create_user(registration_data)
            
            # Create default preferences
            await self._create_default_preferences(user.id)
            
            # Generate and send verification code
            verification_code = email_service.generate_verification_code()
            await self._create_email_verification_code(user, verification_code)
            
            # Send verification email
            await email_service.send_verification_code_email(
                user.email,
                user.first_name,
                verification_code
            )
            
            # Log registration
            await self._log_audit_event(
                user.id,
                AuditLogAction.USER_REGISTERED,
                "User registered successfully",
                ip_address,
                user_agent
            )
            
            # Commit transaction
            await self.db.commit()
            
            logger.info(f"✅ User registered successfully: {user.email}")
            logger.info(f"🔢 Verification code sent: {verification_code}")
            
            return UserRegistrationResponse(
                message="Registration successful! Please check your email for verification code.",
                user_id=user.id,
                email=user.email,
                verification_required=True
            )
            
        except Exception as e:
            await self.db.rollback()
            if isinstance(e, (ValidationException, ConflictException)):
                raise
            logger.error(f"Registration failed for {registration_data.email}: {str(e)}")
            raise AppException("Registration failed", status_code=500, error_code="REGISTRATION_FAILED")
    
    async def verify_email(
        self,
        email: str,
        code: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> EmailVerificationResponse:
        """Verify email with 6-digit code using email address"""
        # Get user by email first
        user = await self._get_user_by_email(email)
        if not user:
            raise NotFoundException("User not found")
        
        # Now call the existing method with user_id
        return await self.verify_email_code(
            user.id, code, ip_address, user_agent
        )

    async def verify_email_code(
        self, 
        user_id: int,
        code: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> EmailVerificationResponse:
        """Verify email with 6-digit code"""
        try:
            # Find and validate code
            verification_record = await self._get_valid_verification_code(user_id, code)
            
            # Get user
            user = verification_record.user
            
            # Update user status
            user.is_email_verified = True
            user.status = UserStatus.ACTIVE
            
            # Mark code as used
            verification_record.is_used = True
            verification_record.used_at = datetime.utcnow()
            
            # Generate JWT tokens for automatic login
            access_token = SecurityUtils.create_access_token({"sub": str(user.id)})
            refresh_token_obj = await self._create_refresh_token(user.id, ip_address, user_agent)
            
            # Update last login
            user.last_login_at = datetime.utcnow()
            user.login_count += 1
            
            # Log verification
            await self._log_audit_event(
                user.id,
                AuditLogAction.EMAIL_VERIFIED,
                "Email verified successfully",
                ip_address,
                user_agent
            )
            
            # Send welcome email (non-blocking)
            try:
                await email_service.send_welcome_email(user.email, user.first_name)
            except Exception as e:
                logger.warning(f"Failed to send welcome email to {user.email}: {str(e)}")
            
            # Commit transaction
            await self.db.commit()
            
            logger.info(f"✅ Email verified successfully: {user.email}")
            
            return EmailVerificationResponse(
                message="Email verified successfully! Welcome to AiPod!",
                user=UserResponse(
                    id=str(user.id),
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                    is_verified=user.is_email_verified,
                    status=user.status,
                    created_at=user.created_at
                ),
                access_token=access_token,
                refresh_token=refresh_token_obj.token,
                token_type="bearer",
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except Exception as e:
            await self.db.rollback()
            if isinstance(e, (ValidationException, NotFoundException, AuthenticationException)):
                raise
            logger.error(f"Email verification failed: {str(e)}")
            raise AppException("Email verification failed", status_code=500, error_code="VERIFICATION_FAILED")
    
    async def resend_verification_code(self, email: str) -> Dict[str, str]:
        """Resend verification code"""
        try:
            user = await self._get_user_by_email(email)
            
            if not user:
                # Return success even if user doesn't exist (security)
                return {"message": "If the email is registered, a new verification code has been sent"}
            
            if user.is_email_verified:
                raise ValidationException("Email is already verified")
            
            # Check rate limiting (max 3 codes per hour)
            recent_codes_count = await self._count_recent_verification_codes(user.id)
            if recent_codes_count >= 3:
                raise ValidationException("Too many verification codes sent. Please wait before requesting another.")
            
            # Invalidate old codes
            await self._invalidate_verification_codes(user.id)
            
            # Generate new code
            verification_code = email_service.generate_verification_code()
            await self._create_email_verification_code(user, verification_code)
            
            # Send new code
            await email_service.send_verification_code_email(
                user.email,
                user.first_name,
                verification_code
            )
            
            await self.db.commit()
            
            logger.info(f"🔄 New verification code sent to: {user.email}")
            logger.info(f"🔢 Code: {verification_code}")
            
            return {"message": "New verification code sent to your email"}
            
        except Exception as e:
            await self.db.rollback()
            if isinstance(e, ValidationException):
                raise
            logger.error(f"Failed to resend verification code: {str(e)}")
            raise AppException("Failed to resend verification code", status_code=500, error_code="RESEND_FAILED")
    
    async def login_user(
        self,
        login_data: UserLoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserLoginResponse:
        """Authenticate and login user"""
        try:
            # Find user by email
            user = await self._get_user_by_email(login_data.email)
            
            if not user:
                # Log failed attempt
                await self._log_audit_event(
                    None,
                    AuditLogAction.USER_LOGIN,
                    f"Failed login attempt for {login_data.email}: User not found",
                    ip_address,
                    user_agent
                )
                raise AuthenticationException("Invalid email or password")
            
            # Check password
            if not SecurityUtils.verify_password(login_data.password, user.hashed_password):
                # Increment failed attempts
                user.failed_login_attempts += 1
                user.last_failed_login_at = datetime.utcnow()
                
                # Log failed attempt
                await self._log_audit_event(
                    user.id,
                    AuditLogAction.USER_LOGIN,
                    "Failed login attempt: Invalid password",
                    ip_address,
                    user_agent
                )
                
                await self.db.commit()
                raise AuthenticationException("Invalid email or password")
            
            # Check account status
            if user.status == UserStatus.SUSPENDED:
                raise AuthenticationException("Account suspended. Please contact support.")
            
            if user.status == UserStatus.DEACTIVATED:
                raise AuthenticationException("Account deactivated. Please contact support.")
            
            if not user.is_email_verified:
                raise AuthenticationException("Please verify your email address before logging in.")
            
            # Reset failed attempts on successful password verification
            user.failed_login_attempts = 0
            
            # Generate tokens
            access_token = SecurityUtils.create_access_token({"sub": str(user.id)})
            
            # Create refresh token with extended expiry if remember_me is True
            expires_delta = None
            if login_data.remember_me:
                expires_delta = timedelta(days=30)  # Extended session
            
            refresh_token_obj = await self._create_refresh_token(
                user.id, ip_address, user_agent, expires_delta
            )
            
            # Update login info
            user.last_login_at = datetime.utcnow()
            user.login_count += 1
            
            # Log successful login
            await self._log_audit_event(
                user.id,
                AuditLogAction.USER_LOGIN,
                "User logged in successfully",
                ip_address,
                user_agent
            )
            
            # Commit transaction
            await self.db.commit()
            
            logger.info(f"✅ User logged in successfully: {user.email}")
            
            # Create user profile response
            user_profile = UserProfileResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                full_name=user.full_name,
                display_name=user.display_name,
                status=user.status,
                is_email_verified=user.is_email_verified,
                avatar_url=user.avatar_url,
                bio=user.bio,
                created_at=user.created_at,
                last_login_at=user.last_login_at
            )
            
            return UserLoginResponse(
                message="Login successful",
                access_token=access_token,
                refresh_token=refresh_token_obj.token,
                token_type="bearer",
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user_profile
            )
            
        except Exception as e:
            await self.db.rollback()
            if isinstance(e, AuthenticationException):
                raise
            logger.error(f"Login failed for {login_data.email}: {str(e)}")
            raise AppException("Login failed", status_code=500, error_code="LOGIN_FAILED")
    
    async def send_password_reset_code(self, email: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, str]:
        """Send password reset code"""
        try:
            user = await self._get_user_by_email(email)
            
            # Always return success for security (don't reveal if email exists)
            if not user:
                return {"message": "If the email exists, a reset code has been sent"}
            
            # Generate reset code
            reset_code = email_service.generate_verification_code()
            
            # Create reset record
            reset_record = PasswordResetToken(
                code=reset_code,
                user_id=user.id,
                expires_at=datetime.utcnow() + timedelta(minutes=10),  # 10 minutes
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.db.add(reset_record)
            
            # Send reset email
            await email_service.send_password_reset_code_email(
                user.email,
                user.first_name,
                reset_code
            )
            
            await self.db.commit()
            
            logger.info(f"🔒 Password reset code sent to: {user.email}")
            logger.info(f"🔢 Reset code: {reset_code}")
            
            return {"message": "If the email exists, a reset code has been sent"}
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to send password reset code: {str(e)}")
            # Always return success for security
            return {"message": "If the email exists, a reset code has been sent"}
    
    async def reset_password(
        self,
        email: str,
        code: str,
        new_password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, str]:
        """Reset password using email, code, and new password"""
        # Get the reset token first to find the user
        reset_token = await self._get_valid_reset_code(code)
        user = reset_token.user
        
        # Verify the email matches
        if user.email != email:
            raise AuthenticationException("Invalid reset code")
        
        # Now call the existing method
        return await self.reset_password_with_code(
            code, new_password, ip_address
        )

    async def reset_password_with_code(self, code: str, new_password: str, ip_address: Optional[str] = None) -> Dict[str, str]:
        """Reset password using verification code"""
        try:
            # Find valid reset code
            reset_record = await self._get_valid_reset_code(code)
            
            # Get user and update password
            user = reset_record.user
            new_password_hash = SecurityUtils.hash_password(new_password)
            
            user.hashed_password = new_password_hash
            user.updated_at = datetime.utcnow()
            
            # Mark code as used
            reset_record.is_used = True
            reset_record.used_at = datetime.utcnow()
            
            # Log password reset
            await self._log_audit_event(
                user.id,
                AuditLogAction.PASSWORD_RESET_COMPLETED,
                "Password reset completed successfully",
                ip_address,
                None
            )
            
            await self.db.commit()
            
            logger.info(f"🔒 Password reset completed for: {user.email}")
            
            return {"message": "Password reset successfully! Please login with your new password."}
            
        except Exception as e:
            await self.db.rollback()
            if isinstance(e, (NotFoundException, AuthenticationException)):
                raise
            logger.error(f"Password reset failed: {str(e)}")
            raise AppException("Password reset failed", status_code=500, error_code="RESET_FAILED")
    
    async def verify_email_by_code(
        self,
        code: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> EmailVerificationResponse:
        """Verify email with 6-digit code by finding the token by code alone"""
        try:
            # Find verification token by code
            verification_record = await self.db.execute(
                select(EmailVerificationToken)
                .where(
                    EmailVerificationToken.code == code,
                    EmailVerificationToken.is_used == False,
                    EmailVerificationToken.expires_at > datetime.utcnow()
                )
                .options(selectinload(EmailVerificationToken.user))
            )
            
            verification_record = verification_record.scalar_one_or_none()
            
            if not verification_record:
                raise AuthenticationException("Invalid or expired verification code")
            
            # Now call the existing method with user_id
            return await self.verify_email_code(
                verification_record.user_id, code, ip_address, user_agent
            )

        except Exception as e:
            if isinstance(e, (ValidationException, NotFoundException, AuthenticationException)):
                raise
            logger.error(f"Email verification by code failed: {str(e)}")
            raise AppException("Email verification failed", status_code=500, error_code="VERIFICATION_FAILED")

    async def google_oauth_login(
        self,
        oauth_data: GoogleOAuthRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> GoogleOAuthResponse:
        """Handle Google OAuth login/registration"""
        try:
            # Check if user exists
            existing_user = await self.db.execute(
                select(User).where(User.email == oauth_data.email.lower())
            )
            existing_user = existing_user.scalar_one_or_none()
            
            is_new_user = False
            
            if existing_user:
                # User exists, update Google info if needed
                user = existing_user
                if not user.google_id:
                    user.google_id = oauth_data.google_id
                # Always update avatar from Google to get latest profile picture
                if oauth_data.avatar_url:
                    user.avatar_url = oauth_data.avatar_url
                
                # Verify email if not already verified
                if not user.is_email_verified:
                    user.is_email_verified = True
                    user.status = UserStatus.ACTIVE
                    
            else:
                # Create new user
                is_new_user = True
                user = User(
                    email=oauth_data.email.lower(),
                    first_name=oauth_data.first_name.strip(),
                    last_name=oauth_data.last_name.strip(),
                    google_id=oauth_data.google_id,
                    avatar_url=oauth_data.avatar_url,
                    is_email_verified=True,  # Google emails are pre-verified
                    status=UserStatus.ACTIVE,
                    hashed_password="",  # No password for OAuth users
                    login_count=0
                )
                self.db.add(user)
                await self.db.flush()  # Get user ID
            
            # Generate JWT tokens
            access_token = SecurityUtils.create_access_token({"sub": str(user.id)})
            refresh_token_obj = await self._create_refresh_token(user.id, ip_address, user_agent)
            
            # Update last login
            user.last_login_at = datetime.utcnow()
            user.login_count += 1
            
            # Log authentication
            action = AuditLogAction.USER_REGISTERED if is_new_user else AuditLogAction.USER_LOGIN
            await self._log_audit_event(
                user.id,
                action,
                f"Google OAuth {'registration' if is_new_user else 'login'}",
                ip_address,
                user_agent
            )
            
            # Send welcome email for new users (non-blocking)
            if is_new_user:
                try:
                    await email_service.send_welcome_email(user.email, user.first_name)
                except Exception as e:
                    logger.warning(f"Failed to send welcome email to {user.email}: {str(e)}")
            
            # Commit transaction
            await self.db.commit()
            
            logger.info(f"✅ Google OAuth successful: {user.email} ({'new user' if is_new_user else 'existing user'})")
            
            return GoogleOAuthResponse(
                message=f"Google authentication successful! {'Welcome to AiPod!' if is_new_user else 'Welcome back!'}",
                user=UserResponse(
                    id=str(user.id),
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                    avatar_url=user.avatar_url,
                    is_verified=user.is_email_verified,
                    status=user.status,
                    created_at=user.created_at
                ),
                access_token=access_token,
                refresh_token=refresh_token_obj.token,
                token_type="bearer",
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                is_new_user=is_new_user
            )
            
        except Exception as e:
            await self.db.rollback()
            if isinstance(e, (ValidationException, NotFoundException, AuthenticationException)):
                raise
            logger.error(f"Google OAuth failed: {str(e)}")
            raise AppException("Google authentication failed", status_code=500, error_code="GOOGLE_OAUTH_FAILED")

    # Private helper methods
    
    async def _validate_registration_data(self, data: UserRegistrationRequest) -> None:
        """Validate registration data"""
        SecurityUtils.validate_email_format(data.email)
        SecurityUtils.validate_password_strength(data.password)
        SecurityUtils.validate_name(data.first_name, "first_name")
        SecurityUtils.validate_name(data.last_name, "last_name")
    
    async def _check_user_exists(self, email: str, username: Optional[str] = None) -> None:
        """Check if user already exists"""
        conditions = [User.email == email.lower()]
        
        if username:
            conditions.append(User.username == username.lower())
        
        query = select(User).where(or_(*conditions))
        result = await self.db.execute(query)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            if existing_user.email == email.lower():
                raise ConflictException("Email already registered", "email")
            else:
                raise ConflictException("Username already taken", "username")
    
    async def _create_user(self, data: UserRegistrationRequest) -> User:
        """Create new user"""
        user = User(
            email=data.email.lower(),
            hashed_password=SecurityUtils.hash_password(data.password),
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            username=data.username.lower() if data.username else None,
            status=UserStatus.PENDING_VERIFICATION,
            is_email_verified=False,
        )
        
        self.db.add(user)
        await self.db.flush()  # To get the user ID
        return user
    
    async def _create_default_preferences(self, user_id: int) -> UserPreferences:
        """Create default user preferences"""
        preferences = UserPreferences(user_id=user_id)
        self.db.add(preferences)
        return preferences
    
    async def _create_email_verification_code(self, user: User, code: str) -> EmailVerificationToken:
        """Create email verification code"""
        verification_record = EmailVerificationToken(
            code=code,
            user_id=user.id,
            email=user.email,
            expires_at=datetime.utcnow() + timedelta(minutes=10)  # 10 minutes expiry
        )
        
        self.db.add(verification_record)
        return verification_record
    
    async def _create_refresh_token(
        self,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        expires_delta: Optional[timedelta] = None
    ) -> RefreshToken:
        """Create refresh token"""
        if expires_delta is None:
            expires_delta = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        refresh_token = RefreshToken(
            token=SecurityUtils.generate_random_token(64),
            user_id=user_id,
            expires_at=datetime.utcnow() + expires_delta,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(refresh_token)
        return refresh_token
    
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        query = select(User).where(User.email == email.lower())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_valid_verification_code(self, user_id: int, code: str) -> EmailVerificationToken:
        """Get and validate verification code"""
        query = select(EmailVerificationToken).options(
            selectinload(EmailVerificationToken.user)
        ).where(
            and_(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.code == code,
                EmailVerificationToken.is_used == False,
                EmailVerificationToken.expires_at > datetime.utcnow()
            )
        )
        
        result = await self.db.execute(query)
        code_record = result.scalar_one_or_none()
        
        if not code_record:
            # Increment attempts for rate limiting
            await self._increment_verification_attempts(user_id, code)
            raise NotFoundException("Invalid or expired verification code", "code")
        
        return code_record
    
    async def _get_valid_reset_code(self, code: str) -> PasswordResetToken:
        """Get and validate password reset code"""
        query = select(PasswordResetToken).options(
            selectinload(PasswordResetToken.user)
        ).where(
            and_(
                PasswordResetToken.code == code,
                PasswordResetToken.is_used == False,
                PasswordResetToken.expires_at > datetime.utcnow()
            )
        )
        
        result = await self.db.execute(query)
        reset_record = result.scalar_one_or_none()
        
        if not reset_record:
            raise NotFoundException("Invalid or expired reset code", "code")
        
        return reset_record
    
    async def _count_recent_verification_codes(self, user_id: int) -> int:
        """Count recent verification codes for rate limiting"""
        query = select(EmailVerificationToken).where(
            and_(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.created_at > datetime.utcnow() - timedelta(hours=1)
            )
        )
        result = await self.db.execute(query)
        return len(result.scalars().all())
    
    async def _increment_verification_attempts(self, user_id: int, code: str) -> None:
        """Increment verification attempts for rate limiting"""
        query = select(EmailVerificationToken).where(
            and_(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.code == code,
                EmailVerificationToken.expires_at > datetime.utcnow()
            )
        )
        result = await self.db.execute(query)
        code_record = result.scalar_one_or_none()
        
        if code_record:
            code_record.attempts += 1
    
    async def _invalidate_verification_codes(self, user_id: int) -> None:
        """Invalidate all verification codes for a user"""
        query = select(EmailVerificationToken).where(
            and_(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.is_used == False
            )
        )
        
        result = await self.db.execute(query)
        codes = result.scalars().all()
        
        for code in codes:
            code.is_used = True
            code.used_at = datetime.utcnow()
    
    async def _log_audit_event(
        self,
        user_id: Optional[int],
        action: AuditLogAction,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log audit event"""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=json.dumps(metadata) if metadata else None
        )
        
        self.db.add(audit_log)

    async def update_user_profile(
        self,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> User:
        """Update user profile information"""
        try:
            # Get user
            user = await self.db.get(User, user_id)
            if not user:
                raise NotFoundException("User not found")
            
            # Check if username is taken (if provided and different)
            if username and username != user.username:
                existing_user = await self.db.execute(
                    select(User).where(User.username == username)
                )
                if existing_user.scalar_one_or_none():
                    raise ConflictException("Username already taken")
            
            # Update fields
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if username is not None:
                user.username = username
            if bio is not None:
                user.bio = bio
            if avatar_url is not None:
                user.avatar_url = avatar_url
            
            user.updated_at = datetime.utcnow()
            
            # Log audit event before commit
            await self._log_audit_event(
                user.id,
                AuditLogAction.PROFILE_UPDATED,
                "Profile updated",
                ip_address,
                user_agent
            )
            
            await self.db.commit()
            await self.db.refresh(user)
            
            return user
            
        except AppException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user profile: {str(e)}")
            raise AppException("Failed to update profile")
