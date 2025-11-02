"""
Attachment data model and related types.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Attachment(BaseModel):
    """Attachment data model."""

    # Core fields
    name: str = Field(description="Resource name: attachments/{attachment}")
    create_time: datetime = Field(description="Creation timestamp")
    filename: str = Field(description="Original filename")

    # Content metadata
    type: str = Field(description="MIME type of the attachment")
    size: int = Field(description="Size in bytes")

    # Optional fields
    external_link: Optional[str] = Field(
        None, description="External link if hosted elsewhere"
    )
    memo: Optional[str] = Field(None, description="Associated memo: memos/{memo}")

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat() if v else None}}

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.startswith("attachments/"):
            raise ValueError("Attachment name must start with 'attachments/'")
        return v

    @field_validator("memo")
    @classmethod
    def validate_memo(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.startswith("memos/"):
            raise ValueError("Memo must start with 'memos/'")
        return v

    @field_validator("size")
    @classmethod
    def validate_size(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Size must be non-negative")
        return v

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Filename cannot be empty")
        return v.strip()

    @property
    def attachment_id(self) -> str:
        """Extract the attachment ID from the resource name."""
        return self.name.split("/", 1)[1] if "/" in self.name else self.name

    @property
    def memo_id(self) -> Optional[str]:
        """Extract the memo ID from the associated memo resource name."""
        if self.memo:
            return self.memo.split("/", 1)[1] if "/" in self.memo else self.memo
        return None

    @property
    def is_image(self) -> bool:
        """Check if the attachment is an image."""
        return self.type.startswith("image/")

    @property
    def is_video(self) -> bool:
        """Check if the attachment is a video."""
        return self.type.startswith("video/")

    @property
    def is_audio(self) -> bool:
        """Check if the attachment is audio."""
        return self.type.startswith("audio/")

    @property
    def is_document(self) -> bool:
        """Check if the attachment is a document."""
        document_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "text/plain",
            "text/markdown",
            "text/csv",
        ]
        return self.type in document_types

    def get_file_extension(self) -> str:
        """Get the file extension from filename."""
        if "." in self.filename:
            return self.filename.rsplit(".", 1)[1].lower()
        return ""

    def format_size(self) -> str:
        """Format file size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if self.size < 1024.0:
                return f"{self.size:.1f} {unit}"
            self.size /= 1024.0
        return f"{self.size:.1f} PB"
