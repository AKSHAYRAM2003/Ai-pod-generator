from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import string
import logging
from email_validator import validate_email, EmailNotValidError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import AuthenticationException, ValidationException

logger = logging.getLogger(__name__)

# Password hashing context - with custom bcrypt handling
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto"
)


class SecurityUtils:
    """Security utilities for authentication and validation"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt - truncates to 72 bytes if needed"""
        try:
            # First, ensure password is within 72 bytes (bcrypt limit)
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                # Truncate to 72 bytes, handling UTF-8 properly
                password_bytes = password_bytes[:72]
                # Decode back, handling potential cut-off multi-byte characters
                for i in range(len(password_bytes), max(len(password_bytes) - 4, 0), -1):
                    try:
                        password = password_bytes[:i].decode('utf-8')
                        break
                    except UnicodeDecodeError:
                        continue
            
            return pwd_context.hash(password)
        except Exception as e:
            # If hashing fails for any reason, try with a safer truncation
            logger.error(f"Password hashing error: {e}. Attempting safe truncation.")
            # Take only first 72 characters (not bytes) as a fallback
            safe_password = password[:72]
            return pwd_context.hash(safe_password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash - truncates to 72 bytes if needed"""
        try:
            # Ensure password is within 72 bytes
            password_bytes = plain_password.encode('utf-8')
            if len(password_bytes) > 72:
                # Truncate to 72 bytes, handling UTF-8 properly
                password_bytes = password_bytes[:72]
                # Decode back, handling potential cut-off multi-byte characters
                for i in range(len(password_bytes), max(len(password_bytes) - 4, 0), -1):
                    try:
                        plain_password = password_bytes[:i].decode('utf-8')
                        break
                    except UnicodeDecodeError:
                        continue
            
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            # If verification fails, try with character truncation
            safe_password = plain_password[:72]
            try:
                return pwd_context.verify(safe_password, hashed_password)
            except Exception:
                return False
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError as e:
            raise AuthenticationException(f"Invalid token: {str(e)}")
    
    @staticmethod
    def get_user_id_from_token(token: str) -> int:
        """Extract user ID from JWT token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise AuthenticationException("Invalid token: missing user ID")
            return int(user_id)
        except JWTError as e:
            raise AuthenticationException(f"Invalid token: {str(e)}")
        except ValueError:
            raise AuthenticationException("Invalid token: invalid user ID format")
    
    @staticmethod
    def generate_random_token(length: int = 32) -> str:
        """Generate a random token for email verification, password reset, etc."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def validate_email_format(email: str) -> str:
        """Validate email format and return normalized email"""
        try:
            valid = validate_email(email)
            return valid.email.lower()
        except EmailNotValidError as e:
            raise ValidationException(f"Invalid email format: {str(e)}", "email")
    
    @staticmethod
    def validate_password_strength(password: str) -> None:
        """Validate password strength - simplified for easy registration"""
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            raise ValidationException(
                f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long",
                "password"
            )
        
        # Keep it simple - just minimum length requirement
        # No complex character requirements for easy registration
    
    @staticmethod
    def validate_name(name: str, field_name: str = "name") -> str:
        """Validate and normalize a name field"""
        name = name.strip()
        
        if not name:
            raise ValidationException(f"{field_name.capitalize()} is required", field_name)
        
        if len(name) < 2:
            raise ValidationException(f"{field_name.capitalize()} must be at least 2 characters long", field_name)
        
        if len(name) > 50:
            raise ValidationException(f"{field_name.capitalize()} must be less than 50 characters long", field_name)
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not all(c.isalpha() or c in " -'" for c in name):
            raise ValidationException(f"{field_name.capitalize()} contains invalid characters", field_name)
        
        return name


# HTTP Bearer security scheme
security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Dependency to get the current user from JWT token.
    Usage: current_user: User = Depends(get_current_user)
    """
    from app.models.user import User
    from sqlalchemy import select
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Load user from database using async SQLAlchemy
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user
