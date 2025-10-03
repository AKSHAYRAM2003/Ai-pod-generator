from typing import Any, Dict, Optional


class AppException(Exception):
    """Base application exception"""
    
    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        error_code: str = "APP_ERROR",
        headers: Optional[Dict[str, Any]] = None,
    ):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        self.headers = headers
        super().__init__(detail)


class ValidationException(AppException):
    """Validation error exception"""
    
    def __init__(self, detail: str, field: Optional[str] = None):
        error_code = f"VALIDATION_ERROR_{field.upper()}" if field else "VALIDATION_ERROR"
        super().__init__(
            detail=detail,
            status_code=400,
            error_code=error_code
        )


class AuthenticationException(AppException):
    """Authentication error exception"""
    
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(
            detail=detail,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationException(AppException):
    """Authorization error exception"""
    
    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            detail=detail,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )


class NotFoundException(AppException):
    """Resource not found exception"""
    
    def __init__(self, detail: str = "Resource not found", resource: Optional[str] = None):
        error_code = f"{resource.upper()}_NOT_FOUND" if resource else "NOT_FOUND"
        super().__init__(
            detail=detail,
            status_code=404,
            error_code=error_code
        )


class ConflictException(AppException):
    """Resource conflict exception"""
    
    def __init__(self, detail: str, resource: Optional[str] = None):
        error_code = f"{resource.upper()}_CONFLICT" if resource else "CONFLICT"
        super().__init__(
            detail=detail,
            status_code=409,
            error_code=error_code
        )


class RateLimitException(AppException):
    """Rate limit exceeded exception"""
    
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            detail=detail,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED"
        )
