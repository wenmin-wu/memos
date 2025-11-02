"""
Memo data model and related types.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from .attachment import Attachment


class Visibility(str, Enum):
    """Visibility levels for memos."""
    UNSPECIFIED = "VISIBILITY_UNSPECIFIED"
    PRIVATE = "PRIVATE"
    PROTECTED = "PROTECTED"
    PUBLIC = "PUBLIC"


class State(str, Enum):
    """State of memos."""
    UNSPECIFIED = "STATE_UNSPECIFIED"
    NORMAL = "NORMAL"
    ARCHIVED = "ARCHIVED"


class Location(BaseModel):
    """Location information for a memo."""
    placeholder: Optional[str] = Field(None, description="Placeholder text for location")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (-90 <= v <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (-180 <= v <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v


class MemoProperty(BaseModel):
    """Computed properties of a memo."""
    has_link: bool = Field(False, description="Whether memo contains links")
    has_task_list: bool = Field(False, description="Whether memo contains task lists")
    has_code: bool = Field(False, description="Whether memo contains code blocks")
    has_incomplete_tasks: bool = Field(False, description="Whether memo has incomplete tasks")


class Memo(BaseModel):
    """Memo data model."""

    # Core fields
    name: str = Field(description="Resource name: memos/{memo}")
    state: State = Field(State.NORMAL, description="State of the memo")
    creator: str = Field(description="Creator resource name: users/{user}")

    # Timestamps
    create_time: datetime = Field(description="Creation timestamp")
    update_time: datetime = Field(description="Last update timestamp")
    display_time: Optional[datetime] = Field(None, description="Display timestamp")

    # Content
    content: str = Field(description="Memo content in Markdown format")
    snippet: str = Field("", description="Plain text snippet of content")

    # Metadata
    visibility: Visibility = Field(Visibility.PRIVATE, description="Visibility level")
    tags: List[str] = Field(default_factory=list, description="Tags extracted from content")
    pinned: bool = Field(False, description="Whether memo is pinned")

    # Relations
    attachments: List["Attachment"] = Field(default_factory=list, description="Attached files")
    relations: List["MemoRelation"] = Field(default_factory=list, description="Memo relations")
    reactions: List["Reaction"] = Field(default_factory=list, description="Emoji reactions")

    # Optional fields
    parent: Optional[str] = Field(None, description="Parent memo resource name")
    location: Optional[Location] = Field(None, description="Location information")
    memo_property: Optional[MemoProperty] = Field(None, description="Computed properties", alias="property")

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.startswith("memos/"):
            raise ValueError("Memo name must start with 'memos/'")
        return v

    @field_validator("creator")
    @classmethod
    def validate_creator(cls, v: str) -> str:
        if not v.startswith("users/"):
            raise ValueError("Creator must start with 'users/'")
        return v

    @field_validator("parent")
    @classmethod
    def validate_parent(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.startswith("memos/"):
            raise ValueError("Parent must start with 'memos/'")
        return v

    @property
    def memo_id(self) -> str:
        """Extract the memo ID from the resource name."""
        return self.name.split("/", 1)[1] if "/" in self.name else self.name

    @property
    def creator_id(self) -> str:
        """Extract the creator ID from the resource name."""
        return self.creator.split("/", 1)[1] if "/" in self.creator else self.creator

    @property
    def parent_id(self) -> Optional[str]:
        """Extract the parent memo ID from the resource name."""
        if self.parent:
            return self.parent.split("/", 1)[1] if "/" in self.parent else self.parent
        return None


class MemoRelationType(str, Enum):
    """Types of memo relations."""
    UNSPECIFIED = "TYPE_UNSPECIFIED"
    REFERENCE = "REFERENCE"
    COMMENT = "COMMENT"


class MemoRelation(BaseModel):
    """Relation between memos."""
    memo: "MemoReference" = Field(description="Source memo")
    related_memo: "MemoReference" = Field(description="Related memo")
    type: MemoRelationType = Field(description="Type of relation")


class MemoReference(BaseModel):
    """Reference to a memo in relations."""
    name: str = Field(description="Memo resource name: memos/{memo}")
    snippet: str = Field("", description="Plain text snippet")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.startswith("memos/"):
            raise ValueError("Memo name must start with 'memos/'")
        return v


class Reaction(BaseModel):
    """Emoji reaction to a memo."""
    name: str = Field(description="Reaction resource name: reactions/{reaction}")
    creator: str = Field(description="Creator resource name: users/{user}")
    content_id: str = Field(description="Content resource name: memos/{memo}")
    reaction_type: str = Field(description="Emoji reaction type")
    create_time: datetime = Field(description="Creation timestamp")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.startswith("reactions/"):
            raise ValueError("Reaction name must start with 'reactions/'")
        return v

    @field_validator("creator")
    @classmethod
    def validate_creator(cls, v: str) -> str:
        if not v.startswith("users/"):
            raise ValueError("Creator must start with 'users/'")
        return v

    @field_validator("content_id")
    @classmethod
    def validate_content_id(cls, v: str) -> str:
        if not v.startswith("memos/"):
            raise ValueError("Content ID must start with 'memos/'")
        return v


# Update forward references
Memo.model_rebuild()
MemoRelation.model_rebuild()
