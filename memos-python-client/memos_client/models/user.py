"""
User data model and related types.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Role(str, Enum):
    """User roles in the system."""
    UNSPECIFIED = "ROLE_UNSPECIFIED"
    HOST = "HOST"
    ADMIN = "ADMIN"
    USER = "USER"


class User(BaseModel):
    """User data model."""

    # Core fields
    name: str = Field(description="Resource name: users/{user}")
    username: str = Field(description="Unique username")
    email: str = Field("", description="Email address")
    nickname: str = Field("", description="Display name")
    avatar_url: str = Field("", description="Avatar image URL")
    description: str = Field("", description="User description/bio")

    # System fields
    role: Role = Field(Role.USER, description="User role")
    create_time: datetime = Field(description="Account creation time")
    update_time: datetime = Field(description="Last update time")

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.startswith("users/"):
            raise ValueError("User name must start with 'users/'")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        # Basic email validation - could be enhanced with more robust regex
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v.strip()

    @property
    def user_id(self) -> str:
        """Extract the user ID from the resource name."""
        return self.name.split("/", 1)[1] if "/" in self.name else self.name

    @property
    def display_name(self) -> str:
        """Get the display name, falling back to username if nickname is empty."""
        return self.nickname or self.username

    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role in (Role.HOST, Role.ADMIN)

    @property
    def is_host(self) -> bool:
        """Check if user is the host (super admin)."""
        return self.role == Role.HOST
