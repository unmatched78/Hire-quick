"""
Custom Exception Classes

Defines custom exceptions for the application with proper HTTP status codes
and error messages for consistent error handling.
"""

from typing import Any, Dict, Optional


class BaseHTTPException(Exception):
    """Base HTTP exception class"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(BaseHTTPException):
    """Raised when request validation fails"""
    
    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 422, details)


class AuthenticationException(BaseHTTPException):
    """Raised when authentication fails"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 401, details)


class AuthorizationException(BaseHTTPException):
    """Raised when authorization fails"""
    
    def __init__(
        self,
        message: str = "Access denied",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 403, details)


class NotFoundException(BaseHTTPException):
    """Raised when a resource is not found"""
    
    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 404, details)


class ConflictException(BaseHTTPException):
    """Raised when there's a conflict with the current state"""
    
    def __init__(
        self,
        message: str = "Conflict with current state",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 409, details)


class RateLimitException(BaseHTTPException):
    """Raised when rate limit is exceeded"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 429, details)


class FileUploadException(BaseHTTPException):
    """Raised when file upload fails"""
    
    def __init__(
        self,
        message: str = "File upload failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 400, details)


class AIServiceException(BaseHTTPException):
    """Raised when AI service fails"""
    
    def __init__(
        self,
        message: str = "AI service error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 503, details)


class EmailServiceException(BaseHTTPException):
    """Raised when email service fails"""
    
    def __init__(
        self,
        message: str = "Email service error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 503, details)


class DatabaseException(BaseHTTPException):
    """Raised when database operation fails"""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 500, details)


class ExternalServiceException(BaseHTTPException):
    """Raised when external service fails"""
    
    def __init__(
        self,
        message: str = "External service error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 503, details)