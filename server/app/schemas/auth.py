from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class UserStatus(str, Enum):
    """User status enumeration for API responses"""
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class UserRegistrationRequest(BaseModel):
    """Schema for user registration request"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=72, description="User's password (max 72 characters for bcrypt)")
    first_name: str = Field(..., min_length=2, max_length=50, description="User's first name")
    last_name: str = Field(..., min_length=2, max_length=50, description="User's last name")
    username: Optional[str] = Field(None, min_length=3, max_length=30, description="Optional username")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password complexity and length"""
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too long (max 72 bytes)')
        
        # Check password complexity
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, and one number')
        
        return v
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Validate name fields"""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not all(c.isalpha() or c in " -'" for c in v.strip()):
            raise ValueError('Name contains invalid characters')
        
        return v.strip()
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if v is None:
            return v
        
        v = v.strip().lower()
        
        # Check for valid characters (alphanumeric and underscores)
        if not v.replace('_', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, and underscores')
        
        # Must start with a letter or number
        if not (v[0].isalpha() or v[0].isdigit()):
            raise ValueError('Username must start with a letter or number')
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "password": "SecurePass123!",
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe"
            }
        }


class UserRegistrationResponse(BaseModel):
    """Schema for user registration response"""
    message: str = Field(..., description="Success message")
    user_id: int = Field(..., description="Created user ID")
    email: str = Field(..., description="User's email address")
    verification_required: bool = Field(..., description="Whether email verification is required")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Registration successful. Please check your email to verify your account.",
                "user_id": 123,
                "email": "john.doe@example.com",
                "verification_required": True
            }
        }


class EmailVerificationRequest(BaseModel):
    """Schema for email verification request with 6-digit code"""
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")
    
    @validator('code')
    def validate_code(cls, v):
        if not v.isdigit():
            raise ValueError('Code must contain only digits')
        if len(v) != 6:
            raise ValueError('Code must be exactly 6 digits')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "code": "123456"
            }
        }


class UserResponse(BaseModel):
    """Schema for user data in API responses"""
    id: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    username: Optional[str] = Field(None, description="User's username")
    avatar_url: Optional[str] = Field(None, description="User's avatar URL")
    is_verified: bool = Field(..., description="Whether user's email is verified")
    status: UserStatus = Field(..., description="User's account status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "avatar_url": "https://example.com/avatar.jpg",
                "is_verified": True,
                "status": "active",
                "created_at": "2023-01-01T00:00:00Z"
            }
        }


class EmailVerificationResponse(BaseModel):
    """Schema for email verification response"""
    message: str = Field(..., description="Success message")
    user: UserResponse = Field(..., description="User data")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Email verified successfully",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "johndoe",
                    "is_verified": True,
                    "status": "active",
                    "created_at": "2023-01-01T00:00:00Z"
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class ResendVerificationRequest(BaseModel):
    """Schema for resending verification email request"""
    email: EmailStr = Field(..., description="User's email address")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "john.doe@example.com"
            }
        }


class ResendVerificationResponse(BaseModel):
    """Schema for resending verification email response"""
    message: str = Field(..., description="Success message")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Verification email sent successfully"
            }
        }


class UserLoginRequest(BaseModel):
    """Schema for user login request"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")
    remember_me: bool = Field(default=False, description="Extended session duration")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "password": "SecurePass123!",
                "remember_me": False
            }
        }


class UserLoginResponse(BaseModel):
    """Schema for user login response"""
    message: str = Field(..., description="Success message")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: 'UserProfileResponse' = Field(..., description="User profile information")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Login successful",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": 123,
                    "email": "john.doe@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "johndoe",
                    "status": "active",
                    "is_email_verified": True,
                    "avatar_url": None,
                    "created_at": "2024-01-15T10:30:00Z"
                }
            }
        }


class UserProfileResponse(BaseModel):
    """Schema for user profile response"""
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User's email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    username: Optional[str] = Field(None, description="User's username")
    full_name: str = Field(..., description="User's full name")
    display_name: str = Field(..., description="User's display name")
    status: UserStatus = Field(..., description="User's account status")
    is_email_verified: bool = Field(..., description="Email verification status")
    avatar_url: Optional[str] = Field(None, description="User's avatar URL")
    bio: Optional[str] = Field(None, description="User's bio")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 123,
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "full_name": "John Doe",
                "display_name": "johndoe",
                "status": "active",
                "is_email_verified": True,
                "avatar_url": None,
                "bio": "Podcast enthusiast and AI lover",
                "created_at": "2024-01-15T10:30:00Z",
                "last_login_at": "2024-01-20T14:22:00Z"
            }
        }


class UserProfileUpdateRequest(BaseModel):
    """Schema for updating user profile (JSON)"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=50, description="User's first name")
    last_name: Optional[str] = Field(None, min_length=2, max_length=50, description="User's last name")
    username: Optional[str] = Field(None, min_length=3, max_length=30, description="User's username")
    bio: Optional[str] = Field(None, max_length=500, description="User's bio")
    
    class Config:
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "bio": "Podcast enthusiast"
            }
        }


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh request"""
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class TokenRefreshResponse(BaseModel):
    """Schema for token refresh response"""
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "Email already registered",
                "error_code": "EMAIL_CONFLICT"
            }
        }


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr = Field(..., description="User's email address")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "john.doe@example.com"
            }
        }


class PasswordResetVerifyRequest(BaseModel):
    """Schema for password reset verification with code"""
    code: str = Field(..., min_length=6, max_length=6, description="6-digit reset code")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    
    @validator('code')
    def validate_code(cls, v):
        if not v.isdigit():
            raise ValueError('Code must contain only digits')
        if len(v) != 6:
            raise ValueError('Code must be exactly 6 digits')
        return v
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        # Keep it simple - just minimum length requirement
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "code": "123456",
                "new_password": "NewSecurePass123!"
            }
        }


class ResendCodeRequest(BaseModel):
    """Schema for resending verification code"""
    email: EmailStr = Field(..., description="User's email address")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "john.doe@example.com"
            }
        }


class PasswordResetResponse(BaseModel):
    """Response schema for password reset operations"""
    message: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Password reset code sent to your email"
            }
        }
    )


class GoogleOAuthRequest(BaseModel):
    """Schema for Google OAuth request"""
    email: EmailStr = Field(..., description="User's email from Google")
    first_name: str = Field(..., min_length=1, max_length=50, description="User's first name from Google")
    last_name: str = Field(..., min_length=1, max_length=50, description="User's last name from Google")
    google_id: str = Field(..., description="User's Google ID")
    avatar_url: Optional[str] = Field(None, description="User's Google profile picture URL")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "google_id": "108067474914902462493",
                "avatar_url": "https://lh3.googleusercontent.com/..."
            }
        }


class GoogleOAuthResponse(BaseModel):
    """Schema for Google OAuth response"""
    message: str = Field(..., description="Success message")
    user: UserResponse = Field(..., description="User data")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    is_new_user: bool = Field(..., description="Whether this is a new user registration")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Google authentication successful",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "johndoe",
                    "is_verified": True,
                    "status": "active",
                    "created_at": "2023-01-01T00:00:00Z"
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "is_new_user": False
            }
        }


# Forward reference resolution
UserLoginResponse.model_rebuild()
