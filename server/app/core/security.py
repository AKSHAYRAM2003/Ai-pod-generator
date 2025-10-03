from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import string
from email_validator import validate_email, EmailNotValidError

from app.core.config import settings
from app.core.exceptions import AuthenticationException, ValidationException

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityUtils:
    """Security utilities for authentication and validation"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        # Bcrypt has a 72-byte limit, truncate if necessary
        if len(password.encode('utf-8')) > 72:
            password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        # Bcrypt has a 72-byte limit, truncate if necessary
        if len(plain_password.encode('utf-8')) > 72:
            plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return pwd_context.verify(plain_password, hashed_password)
    
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
