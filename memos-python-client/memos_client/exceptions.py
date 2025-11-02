"""
Custom exceptions for the Memos client library.
"""

from typing import Optional, Dict, Any


class MemosException(Exception):
    """Base exception for all Memos client errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
    
    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(MemosException):
    """Raised when authentication fails."""
    
    def __init__(
        self, 
        message: str = "Authentication failed",
        status_code: Optional[int] = 401,
        response_data: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code, response_data)


class AuthorizationError(MemosException):
    """Raised when access is denied due to insufficient permissions."""
    
    def __init__(
        self, 
        message: str = "Access denied - insufficient permissions",
        status_code: Optional[int] = 403,
        response_data: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code, response_data)


class NotFoundError(MemosException):
    """Raised when a requested resource is not found."""
    
    def __init__(
        self, 
        message: str = "Resource not found",
        status_code: Optional[int] = 404,
        response_data: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code, response_data)


class ValidationError(MemosException):
    """Raised when request validation fails."""
    
    def __init__(
        self, 
        message: str = "Validation failed",
        status_code: Optional[int] = 400,
        response_data: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code, response_data)


class RateLimitError(MemosException):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded",
        status_code: Optional[int] = 429,
        response_data: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None
    ) -> None:
        super().__init__(message, status_code, response_data)
        self.retry_after = retry_after


class ServerError(MemosException):
    """Raised when server returns an error (5xx status codes)."""
    
    def __init__(
        self, 
        message: str = "Internal server error",
        status_code: Optional[int] = 500,
        response_data: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code, response_data)


class NetworkError(MemosException):
    """Raised when network-related errors occur."""
    
    def __init__(
        self, 
        message: str = "Network error occurred",
        original_exception: Optional[Exception] = None
    ) -> None:
        super().__init__(message)
        self.original_exception = original_exception


class ConfigurationError(MemosException):
    """Raised when client configuration is invalid."""
    
    def __init__(self, message: str = "Invalid configuration") -> None:
        super().__init__(message)
