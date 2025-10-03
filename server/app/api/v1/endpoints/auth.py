from fastapi import APIRouter, Depends, HTTPException, Request, status, Form, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from app.core.database import get_db
from app.core.security import SecurityUtils
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    EmailVerificationRequest,
    EmailVerificationResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    UserLoginRequest,
    UserLoginResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
    PasswordResetRequest,
    PasswordResetVerifyRequest,
    PasswordResetResponse,
    ErrorResponse,
    GoogleOAuthRequest,
    GoogleOAuthResponse,
    UserProfileUpdateRequest
)
from app.core.exceptions import (
    ValidationException,
    ConflictException,
    NotFoundException,
    AuthenticationException,
    AppException
)

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer(auto_error=False)


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Extract client IP and user agent from request"""
    # Get real IP address (considering proxy headers)
    ip_address = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or
        request.headers.get("X-Real-IP") or
        request.client.host if request.client else None
    )
    
    user_agent = request.headers.get("User-Agent")
    return ip_address, user_agent


@router.post(
    "/register",
    response_model=UserRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user account with email verification required",
    responses={
        201: {"description": "User registered successfully"},
        400: {"model": ErrorResponse, "description": "Validation error"},
        409: {"model": ErrorResponse, "description": "Email or username already exists"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def register(
    registration_data: UserRegistrationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account"""
    try:
        ip_address, user_agent = get_client_info(request)
        
        auth_service = AuthService(db)
        response = await auth_service.register_user(
            registration_data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"User registration successful: {registration_data.email}")
        return response
        
    except (ValidationException, ConflictException) as e:
        logger.warning(f"Registration validation error: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"detail": e.detail, "error_code": e.error_code}
        )
    except AppException as e:
        logger.error(f"Registration app error: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"detail": e.detail, "error_code": e.error_code}
        )
    except Exception as e:
        logger.error(f"Unexpected registration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"detail": "Registration failed", "error_code": "REGISTRATION_FAILED"}
        )


@router.post(
    "/verify-email",
    response_model=EmailVerificationResponse,
    summary="Verify email address",
    description="Verify user email address using 6-digit verification code",
    responses={
        200: {"description": "Email verified successfully"},
        400: {"model": ErrorResponse, "description": "Invalid or expired verification code"},
        404: {"model": ErrorResponse, "description": "Verification code not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def verify_email(
    verification_data: EmailVerificationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Verify user email address using 6-digit verification code"""
    try:
        ip_address, user_agent = get_client_info(request)
        
        auth_service = AuthService(db)
        response = await auth_service.verify_email_by_code(
            verification_data.code,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"Email verification successful for code: {verification_data.code}")
        return response
        
    except (NotFoundException, AuthenticationException) as e:
        logger.warning(f"Email verification error: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"detail": e.detail, "error_code": e.error_code}
        )
    except AppException as e:
        logger.error(f"Email verification app error: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"detail": e.detail, "error_code": e.error_code}
        )
    except Exception as e:
        logger.error(f"Unexpected email verification error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"detail": "Email verification failed", "error_code": "VERIFICATION_FAILED"}
        )


@router.post(
    "/resend-verification",
    response_model=ResendVerificationResponse,
    summary="Resend verification email",
    description="Resend email verification to user",
    responses={
        200: {"description": "Verification email sent successfully"},
        400: {"model": ErrorResponse, "description": "Email already verified"},
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def resend_verification(
    resend_data: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Resend email verification"""
    try:
        auth_service = AuthService(db)
        await auth_service.resend_verification_code(resend_data.email)
        
        logger.info(f"Verification email resent to: {resend_data.email}")
        return ResendVerificationResponse(
            message="Verification email sent successfully"
        )
        
    except (NotFoundException, ValidationException) as e:
        logger.warning(f"Resend verification error: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"detail": e.detail, "error_code": e.error_code}
        )
    except AppException as e:
        logger.error(f"Resend verification app error: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"detail": e.detail, "error_code": e.error_code}
        )
    except Exception as e:
        logger.error(f"Unexpected resend verification error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"detail": "Failed to resend verification email", "error_code": "EMAIL_SEND_FAILED"}
        )


@router.post(
    "/login",
    response_model=UserLoginResponse,
    summary="User login",
    description="Authenticate user and return access tokens",
    responses={
        200: {"description": "Login successful"},
        401: {"model": ErrorResponse, "description": "Invalid credentials or unverified email"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def login(
    login_data: UserLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return tokens"""
    try:
        ip_address, user_agent = get_client_info(request)
        
        auth_service = AuthService(db)
        response = await auth_service.login_user(
            login_data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"User login successful: {login_data.email}")
        return response
        
    except AuthenticationException as e:
        logger.warning(f"Login authentication error: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"detail": e.detail, "error_code": e.error_code}
        )
    except AppException as e:
        logger.error(f"Login app error: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"detail": e.detail, "error_code": e.error_code}
        )
    except Exception as e:
        logger.error(f"Unexpected login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"detail": "Login failed", "error_code": "LOGIN_FAILED"}
        )


@router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    summary="Refresh access token",
    description="Get a new access token using refresh token",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"model": ErrorResponse, "description": "Invalid or expired refresh token"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def refresh_token(
    token_data: TokenRefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    try:
        ip_address, user_agent = get_client_info(request)
        
        auth_service = AuthService(db)
        response = await auth_service.refresh_token(
            token_data.refresh_token,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info("Token refresh successful")
        return response
        
    except (NotFoundException, AuthenticationException) as e:
        logger.warning(f"Token refresh error: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"detail": e.detail, "error_code": e.error_code}
        )
    except AppException as e:
        logger.error(f"Token refresh app error: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"detail": e.detail, "error_code": e.error_code}
        )
    except Exception as e:
        logger.error(f"Unexpected token refresh error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"detail": "Token refresh failed", "error_code": "TOKEN_REFRESH_FAILED"}
        )


@router.post(
    "/password-reset/request",
    response_model=PasswordResetResponse,
    summary="Request password reset",
    description="Send password reset code to user's email",
    responses={
        200: {"description": "Password reset code sent successfully"},
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def request_password_reset(
    reset_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset - send 6-digit code to email"""
    try:
        auth_service = AuthService(db)
        await auth_service.send_password_reset_code(reset_data.email)
        
        logger.info(f"Password reset requested for: {reset_data.email}")
        return PasswordResetResponse(
            message="Password reset code sent to your email"
        )
        
    except NotFoundException as e:
        logger.warning(f"Password reset request error: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"detail": e.detail, "error_code": e.error_code}
        )
    except AppException as e:
        logger.error(f"Password reset request app error: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"detail": e.detail, "error_code": e.error_code}
        )
    except Exception as e:
        logger.error(f"Unexpected password reset request error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"detail": "Password reset request failed", "error_code": "PASSWORD_RESET_REQUEST_FAILED"}
        )


@router.post(
    "/password-reset/verify",
    response_model=PasswordResetResponse,
    summary="Reset password with code",
    description="Reset password using 6-digit verification code",
    responses={
        200: {"description": "Password reset successfully"},
        400: {"model": ErrorResponse, "description": "Invalid or expired code"},
        404: {"model": ErrorResponse, "description": "Code not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def verify_password_reset(
    reset_data: PasswordResetVerifyRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Reset password using verification code"""
    try:
        ip_address, user_agent = get_client_info(request)
        
        auth_service = AuthService(db)
        await auth_service.reset_password(
            reset_data.email,
            reset_data.code,
            reset_data.new_password,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"Password reset successful for: {reset_data.email}")
        return PasswordResetResponse(
            message="Password reset successful"
        )
        
    except (NotFoundException, AuthenticationException, ValidationException) as e:
        logger.warning(f"Password reset error: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"detail": e.detail, "error_code": e.error_code}
        )
    except AppException as e:
        logger.error(f"Password reset app error: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"detail": e.detail, "error_code": e.error_code}
        )
    except Exception as e:
        logger.error(f"Unexpected password reset error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"detail": "Password reset failed", "error_code": "PASSWORD_RESET_FAILED"}
        )


@router.post(
    "/google-oauth",
    response_model=GoogleOAuthResponse,
    summary="Google OAuth authentication",
    description="Authenticate user with Google OAuth data",
    responses={
        200: {"description": "Google authentication successful"},
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def google_oauth(
    oauth_data: GoogleOAuthRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth authentication"""
    try:
        ip_address, user_agent = get_client_info(request)
        
        auth_service = AuthService(db)
        response = await auth_service.google_oauth_login(
            oauth_data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"Google OAuth successful: {oauth_data.email}")
        return response
        
    except (ValidationException, ConflictException) as e:
        logger.warning(f"Google OAuth validation error: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"detail": e.detail, "error_code": e.error_code}
        )
    except AppException as e:
        logger.error(f"Google OAuth app error: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"detail": e.detail, "error_code": e.error_code}
        )
    except Exception as e:
        logger.error(f"Unexpected Google OAuth error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"detail": "Google authentication failed", "error_code": "GOOGLE_OAUTH_FAILED"}
        )


@router.patch(
    "/profile",
    response_model=dict,
    summary="Update user profile",
    description="Update user profile information (use JSON for basic updates, form-data for avatar)"
)
async def update_profile(
    request: Request,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update user profile - accepts both JSON and form-data"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token"
        )
    
    try:
        # Get user from token
        user_id = SecurityUtils.get_user_id_from_token(credentials.credentials)
        
        # Check content type to determine if JSON or form-data
        content_type = request.headers.get('content-type', '')
        
        first_name = None
        last_name = None
        username = None
        bio = None
        avatar_url = None
        
        if 'application/json' in content_type:
            # JSON request
            body = await request.json()
            first_name = body.get('first_name')
            last_name = body.get('last_name')
            username = body.get('username')
            bio = body.get('bio')
        elif 'multipart/form-data' in content_type:
            # Form data request - handle avatar upload
            form = await request.form()
            first_name = form.get('first_name')
            last_name = form.get('last_name')
            username = form.get('username')
            bio = form.get('bio')
            avatar = form.get('avatar')
            
            if avatar and hasattr(avatar, 'content_type'):
                # Validate file type
                if not avatar.content_type.startswith('image/'):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid file type. Only images are allowed."
                    )
                
                # Validate file size (5MB limit)
                content = await avatar.read()
                if len(content) > 5 * 1024 * 1024:  # 5MB
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="File too large. Maximum size is 5MB."
                    )
                
                # Compress and resize image
                try:
                    from PIL import Image
                    import io
                    import base64
                    
                    # Open image
                    img = Image.open(io.BytesIO(content))
                    
                    # Convert RGBA to RGB if needed
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = background
                    
                    # Resize image to max 400x400 while maintaining aspect ratio
                    max_size = (400, 400)
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Save as JPEG with compression
                    output = io.BytesIO()
                    img.save(output, format='JPEG', quality=85, optimize=True)
                    compressed_content = output.getvalue()
                    
                    # Encode as base64
                    avatar_url = f"data:image/jpeg;base64,{base64.b64encode(compressed_content).decode()}"
                    
                except Exception as e:
                    logger.error(f"Image processing error: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to process image. Please try a different image."
                    )
        
        ip_address, user_agent = get_client_info(request)
        
        auth_service = AuthService(db)
        user = await auth_service.update_user_profile(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            bio=bio,
            avatar_url=avatar_url,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "is_email_verified": user.is_email_verified,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
        
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/health",
    summary="Authentication service health check",
    description="Check if authentication service is healthy"
)
async def auth_health():
    """Health check endpoint for auth service"""
    return {
        "status": "healthy",
        "service": "authentication",
        "version": "1.0.0"
    }
