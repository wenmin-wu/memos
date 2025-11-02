"""
Memos Python Client Library

A comprehensive Python client for the Memos note-taking application.
"""

from .client import MemosClient
from .config import ClientConfig
from .exceptions import (
    MemosException,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
)
from .models.memo import Memo, Visibility, State, Location
from .models.attachment import Attachment
from .models.user import User

__version__ = "0.1.0"
__author__ = "Wu Wenmin"
__email__ = "wuwenmin1991@gmail.com"

__all__ = [
    # Main client
    "MemosClient",
    "ClientConfig",
    
    # Exceptions
    "MemosException", 
    "AuthenticationError",
    "NotFoundError",
    "ValidationError", 
    "RateLimitError",
    "ServerError",
    
    # Models
    "Memo",
    "Attachment", 
    "User",
    
    # Enums
    "Visibility",
    "State",
    "Location",
]
