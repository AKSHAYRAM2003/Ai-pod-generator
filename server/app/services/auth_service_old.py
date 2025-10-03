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
    TokenRefreshResponse
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
    """Authentication service for user management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register_user(
        self, 
        registration_data: UserRegistrationRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserRegistrationResponse:
        """Register a new user"""
        try:
            # Validate input data
            await self._validate_registration_data(registration_data)
            
            # Check for existing user
            await self._check_user_exists(registration_data.email, registration_data.username)
            
            # Create user
            user = await self._create_user(registration_data)
            
            # Create default preferences
            await self._create_default_preferences(user.id)
                 # Generate email verification code
        verification_code = email_service.generate_verification_code()
        verification_token = await self._create_email_verification_code(user, verification_code)
        
        # Send verification email
        await email_service.send_verification_code_email(
            user.email,
            user.first_name,
            verification_code
        )
        
        # Log verification code for development
        logger.info(f"🔢 Verification code for {user.email}: {verification_code}")
            
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
            
            logger.info(f"User registered successfully: {user.email}")
            
            return UserRegistrationResponse(
                message="Registration successful. Please check your email to verify your account.",
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
        token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> EmailVerificationResponse:
        """Verify user email address"""
        try:
            # Find and validate token
            verification_token = await self._get_valid_verification_token(token)
            
            # Get user
            user = verification_token.user
            
            # Update user status
            user.is_email_verified = True
            user.status = UserStatus.ACTIVE
            
            # Mark token as used
            verification_token.is_used = True
            verification_token.used_at = datetime.utcnow()
            
            # Generate JWT tokens
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
            
            logger.info(f"Email verified successfully: {user.email}")
            
            return EmailVerificationResponse(
                message="Email verified successfully",
                access_token=access_token,
                refresh_token=refresh_token_obj.token,
                token_type="bearer",
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except Exception as e:
            await self.db.rollback()
            if isinstance(e, (ValidationException, NotFoundException, AuthenticationException)):
                raise
            logger.error(f"Email verification failed for token {token}: {str(e)}")
            raise AppException("Email verification failed", status_code=500, error_code="VERIFICATION_FAILED")
    
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
            
            # Load user preferences
            await self.db.refresh(user, ['user_preferences'])
            
            # Commit transaction
            await self.db.commit()
            
            logger.info(f"User logged in successfully: {user.email}")
            
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
    
    async def refresh_token(
        self,
        refresh_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TokenRefreshResponse:
        """Refresh access token using refresh token"""
        try:
            # Find and validate refresh token
            token_obj = await self._get_valid_refresh_token(refresh_token)
            
            # Generate new access token
            access_token = SecurityUtils.create_access_token({"sub": str(token_obj.user_id)})
            
            # Update token usage
            token_obj.used_at = datetime.utcnow()
            
            await self.db.commit()
            
            return TokenRefreshResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except Exception as e:
            await self.db.rollback()
            if isinstance(e, (NotFoundException, AuthenticationException)):
                raise
            logger.error(f"Token refresh failed: {str(e)}")
            raise AppException("Token refresh failed", status_code=500, error_code="TOKEN_REFRESH_FAILED")
    
    async def resend_verification_email(self, email: str) -> bool:
        """Resend email verification"""
        try:
            user = await self._get_user_by_email(email)
            
            if not user:
                raise NotFoundException("User not found", "user")
            
            if user.is_email_verified:
                raise ValidationException("Email is already verified")
            
            # Invalidate old tokens
            await self._invalidate_verification_tokens(user.id)
            
            # Create new verification token
            verification_token = await self._create_email_verification_token(user)
            
            # Send verification email
            await email_service.send_verification_email(
                user.email,
                user.first_name,
                verification_token.token
            )
            
            await self.db.commit()
            
            logger.info(f"Verification email resent to: {user.email}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            if isinstance(e, (NotFoundException, ValidationException)):
                raise
            logger.error(f"Failed to resend verification email to {email}: {str(e)}")
            raise AppException("Failed to resend verification email", status_code=500, error_code="EMAIL_SEND_FAILED")
    
    # Private helper methods
    
    async def _validate_registration_data(self, data: UserRegistrationRequest) -> None:
        """Validate registration data"""
        # Validate email format
        SecurityUtils.validate_email_format(data.email)
        
        # Validate password strength
        SecurityUtils.validate_password_strength(data.password)
        
        # Validate names
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
    
    async def _create_email_verification_token(self, user: User) -> EmailVerificationToken:
        """Create email verification token"""
        token = EmailVerificationToken(
            token=SecurityUtils.generate_random_token(),
            user_id=user.id,
            email=user.email,
            expires_at=datetime.utcnow() + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
        )
        
        self.db.add(token)
        return token
    
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
    
    async def _get_valid_verification_token(self, token: str) -> EmailVerificationToken:
        """Get and validate verification token"""
        query = select(EmailVerificationToken).options(
            selectinload(EmailVerificationToken.user)
        ).where(
            and_(
                EmailVerificationToken.token == token,
                EmailVerificationToken.is_used == False,
                EmailVerificationToken.expires_at > datetime.utcnow()
            )
        )
        
        result = await self.db.execute(query)
        token_obj = result.scalar_one_or_none()
        
        if not token_obj:
            raise NotFoundException("Invalid or expired verification token", "token")
        
        return token_obj
    
    async def _get_valid_refresh_token(self, token: str) -> RefreshToken:
        """Get and validate refresh token"""
        query = select(RefreshToken).where(
            and_(
                RefreshToken.token == token,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            )
        )
        
        result = await self.db.execute(query)
        token_obj = result.scalar_one_or_none()
        
        if not token_obj:
            raise AuthenticationException("Invalid or expired refresh token")
        
        return token_obj
    
    async def _invalidate_verification_tokens(self, user_id: int) -> None:
        """Invalidate all verification tokens for a user"""
        query = select(EmailVerificationToken).where(
            and_(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.is_used == False
            )
        )
        
        result = await self.db.execute(query)
        tokens = result.scalars().all()
        
        for token in tokens:
            token.is_used = True
            token.used_at = datetime.utcnow()
    
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
            metadata=json.dumps(metadata) if metadata else None
        )
        
        self.db.add(audit_log)
