"""
Configuration settings for the Memos client.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass
class ClientConfig:
    """Configuration for the Memos client."""
    
    # Server configuration
    base_url: str
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Authentication
    access_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    
    # API preferences
    prefer_grpc: bool = False
    api_version: str = "v1"
    
    # HTTP client configuration
    verify_ssl: bool = True
    follow_redirects: bool = True
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Rate limiting
    rate_limit_requests: Optional[int] = None
    rate_limit_period: float = 60.0  # seconds
    
    # Upload configuration
    max_upload_size: int = 100 * 1024 * 1024  # 100MB
    chunk_size: int = 8192
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._validate_base_url()
        self._validate_auth()
        self._normalize_headers()
    
    def _validate_base_url(self) -> None:
        """Validate the base URL format."""
        if not self.base_url:
            raise ValueError("base_url is required")
        
        # Remove trailing slash
        self.base_url = self.base_url.rstrip("/")
        
        # Validate URL format
        try:
            parsed = urlparse(self.base_url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid base_url format")
        except Exception as e:
            raise ValueError(f"Invalid base_url format: {e}")
    
    def _validate_auth(self) -> None:
        """Validate authentication configuration."""
        has_token = bool(self.access_token)
        has_credentials = bool(self.username and self.password)
        
        if not (has_token or has_credentials):
            raise ValueError(
                "Either access_token or username/password must be provided"
            )
        
        if has_token and has_credentials:
            # Prefer token over credentials
            self.username = None
            self.password = None
    
    def _normalize_headers(self) -> None:
        """Normalize HTTP headers."""
        # Ensure headers dict is mutable
        if not isinstance(self.headers, dict):
            self.headers = dict(self.headers)
        
        # Set default headers
        default_headers = {
            "User-Agent": "memos-python-client/0.1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        # Add default headers if not already present
        for key, value in default_headers.items():
            if key not in self.headers:
                self.headers[key] = value
    
    @property
    def api_base_url(self) -> str:
        """Get the full API base URL."""
        return f"{self.base_url}/api/{self.api_version}"
    
    @property
    def grpc_url(self) -> str:
        """Get the gRPC endpoint URL."""
        # For gRPC, typically use the same host but different port or path
        parsed = urlparse(self.base_url)
        if parsed.port:
            # Assume gRPC is on the same port for this implementation
            return f"{parsed.hostname}:{parsed.port}"
        else:
            # Default ports
            port = 443 if parsed.scheme == "https" else 80
            return f"{parsed.hostname}:{port}"
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        headers = {}
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        return headers
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "prefer_grpc": self.prefer_grpc,
            "api_version": self.api_version,
            "verify_ssl": self.verify_ssl,
            "follow_redirects": self.follow_redirects,
            "rate_limit_requests": self.rate_limit_requests,
            "rate_limit_period": self.rate_limit_period,
            "max_upload_size": self.max_upload_size,
            "chunk_size": self.chunk_size,
            # Note: Sensitive data like tokens/passwords are excluded
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClientConfig":
        """Create configuration from dictionary."""
        return cls(**data)
