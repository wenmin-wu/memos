"""
Main Memos client implementation.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union

import aiofiles
import httpx

from .auth import AuthManager
from .config import ClientConfig
from .exceptions import (
    AuthenticationError,
    MemosException,
    NetworkError,
    NotFoundError,
    ServerError,
    ValidationError,
)
from .models.attachment import Attachment
from .models.memo import Memo, State, Visibility


class MemosClient:
    """
    Main client for interacting with the Memos API.

    Provides methods for CRUD operations on memos, attachments, and users.
    """

    def __init__(
        self,
        base_url: str,
        access_token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Memos client.

        Args:
            base_url: Base URL of the Memos server
            access_token: JWT access token for authentication
            username: Username for session-based authentication
            password: Password for session-based authentication
            **kwargs: Additional configuration options
        """
        self.config = ClientConfig(
            base_url=base_url,
            access_token=access_token,
            username=username,
            password=password,
            **kwargs,
        )
        self.auth = AuthManager(self.config)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "MemosClient":
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def _ensure_client(self) -> None:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
                follow_redirects=self.config.follow_redirects,
                headers=self.config.headers,
            )

    async def close(self) -> None:
        """Close the HTTP client and clean up resources."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make an authenticated HTTP request.

        Args:
            method: HTTP method
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_data: JSON request body
            data: Form data
            files: File uploads
            headers: Additional headers

        Returns:
            Response data as dictionary

        Raises:
            MemosException: On API errors
        """
        await self._ensure_client()
        assert self._client is not None

        url = f"{self.config.api_base_url}/{endpoint.lstrip('/')}"

        # Get authentication headers
        auth_headers = await self.auth.authenticate()

        # Merge headers
        request_headers = {**self.config.headers}
        if headers:
            request_headers.update(headers)
        request_headers.update(auth_headers)

        try:
            response = await self._client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                data=data,
                files=files,
                headers=request_headers,
            )

            return await self._handle_response(response)

        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", e) from e

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle HTTP response and raise appropriate exceptions.

        Args:
            response: HTTP response object

        Returns:
            Response data as dictionary

        Raises:
            MemosException: On API errors
        """
        try:
            response_data = response.json() if response.content else {}
        except Exception:
            response_data = {}

        if response.status_code == 200 or response.status_code == 201:
            return response_data
        elif response.status_code == 401:
            raise AuthenticationError(
                "Authentication failed",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 403:
            raise AuthenticationError(
                "Access denied - insufficient permissions",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 404:
            raise NotFoundError(
                "Resource not found",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 400:
            raise ValidationError(
                "Validation failed",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code >= 500:
            raise ServerError(
                "Internal server error",
                status_code=response.status_code,
                response_data=response_data,
            )
        else:
            raise MemosException(
                f"HTTP {response.status_code}",
                status_code=response.status_code,
                response_data=response_data,
            )

    # Memo operations

    async def search_memos(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        creator: Optional[str] = None,
        visibility: Optional[Visibility] = None,
        state: State = State.NORMAL,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "display_time desc",
    ) -> List[Memo]:
        """
        Search memos with various filters.

        Args:
            query: Text query to search in memo content
            tags: List of tags to filter by
            creator: Creator username or ID to filter by
            visibility: Visibility level to filter by
            state: Memo state (NORMAL or ARCHIVED)
            limit: Maximum number of results to return
            offset: Number of results to skip
            order_by: Sort order for results

        Returns:
            List of matching memos
        """
        params = {
            "page_size": limit,
            "state": state.value,
            "order_by": order_by,
        }

        # Build filter expression
        filters = []

        if query:
            filters.append(f'content.contains("{query}")')

        if tags:
            tag_filters = [f'tags.any("{tag}")' for tag in tags]
            filters.append(f"({' || '.join(tag_filters)})")

        if creator:
            if not creator.startswith("users/"):
                creator = f"users/{creator}"
            filters.append(f'creator == "{creator}"')

        if visibility:
            filters.append(f'visibility == "{visibility.value}"')

        if filters:
            params["filter"] = " && ".join(filters)

        if offset > 0:
            # For pagination, we'd need to implement page tokens
            # For now, we'll use a simple approach
            pass

        response_data = await self._request("GET", "memos", params=params)

        memos = []
        if "memos" in response_data:
            for memo_data in response_data["memos"]:
                memos.append(Memo(**memo_data))

        return memos

    async def get_memo(self, memo_id: str) -> Memo:
        """
        Get a specific memo by ID.

        Args:
            memo_id: Memo ID or full resource name

        Returns:
            Memo object

        Raises:
            NotFoundError: If memo doesn't exist
        """
        if not memo_id.startswith("memos/"):
            memo_id = f"memos/{memo_id}"

        response_data = await self._request("GET", memo_id)
        return Memo(**response_data)

    async def create_memo(
        self,
        content: str,
        visibility: Visibility = Visibility.PRIVATE,
        tags: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None,
        location: Optional[Dict[str, Any]] = None,
        display_time: Optional[datetime] = None,
        memo_id: Optional[str] = None,
    ) -> Memo:
        """
        Create a new memo.

        Args:
            content: Memo content in Markdown format
            visibility: Visibility level
            tags: List of tags (will be embedded in content)
            attachments: List of attachment resource names
            location: Location information
            display_time: Custom display timestamp
            memo_id: Custom memo ID

        Returns:
            Created memo object
        """
        # Embed tags in content if provided
        memo_content = content
        if tags:
            tag_line = " ".join(f"#{tag}" for tag in tags)
            memo_content = f"{content}\n\n{tag_line}"

        memo_data = {
            "content": memo_content,
            "visibility": visibility.value,
        }

        if display_time:
            memo_data["display_time"] = display_time.isoformat()

        if location:
            memo_data["location"] = location

        request_data = {"memo": memo_data}

        if memo_id:
            request_data["memo_id"] = memo_id

        response_data = await self._request("POST", "memos", json_data=request_data)
        memo = Memo(**response_data)

        # Set attachments if provided
        if attachments:
            await self.set_memo_attachments(memo.name, attachments)
            # Fetch updated memo with attachments
            memo = await self.get_memo(memo.name)

        return memo

    async def update_memo(
        self,
        memo_id: str,
        content: Optional[str] = None,
        visibility: Optional[Visibility] = None,
        tags: Optional[List[str]] = None,
        location: Optional[Dict[str, Any]] = None,
        display_time: Optional[datetime] = None,
        pinned: Optional[bool] = None,
    ) -> Memo:
        """
        Update an existing memo.

        Args:
            memo_id: Memo ID or full resource name
            content: New memo content
            visibility: New visibility level
            tags: New list of tags
            location: New location information
            display_time: New display timestamp
            pinned: Pin/unpin the memo

        Returns:
            Updated memo object
        """
        if not memo_id.startswith("memos/"):
            memo_id = f"memos/{memo_id}"

        # Build update data
        memo_data = {"name": memo_id}
        update_fields = []

        if content is not None:
            if tags:
                tag_line = " ".join(f"#{tag}" for tag in tags)
                memo_data["content"] = f"{content}\n\n{tag_line}"
            else:
                memo_data["content"] = content
            update_fields.append("content")

        if visibility is not None:
            memo_data["visibility"] = visibility.value
            update_fields.append("visibility")

        if location is not None:
            memo_data["location"] = location
            update_fields.append("location")

        if display_time is not None:
            memo_data["display_time"] = display_time.isoformat()
            update_fields.append("display_time")

        if pinned is not None:
            memo_data["pinned"] = pinned
            update_fields.append("pinned")

        request_data = {"memo": memo_data, "update_mask": {"paths": update_fields}}

        response_data = await self._request("PATCH", memo_id, json_data=request_data)
        return Memo(**response_data)

    async def delete_memo(self, memo_id: str) -> None:
        """
        Delete a memo.

        Args:
            memo_id: Memo ID or full resource name
        """
        if not memo_id.startswith("memos/"):
            memo_id = f"memos/{memo_id}"

        await self._request("DELETE", memo_id)

    # Attachment operations

    async def upload_attachment(
        self,
        file_path: Union[str, Path, BinaryIO],
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> Attachment:
        """
        Upload a file attachment.

        Args:
            file_path: Path to file or file object
            filename: Custom filename (defaults to original filename)
            mime_type: MIME type (auto-detected if not provided)

        Returns:
            Created attachment object
        """
        if isinstance(file_path, (str, Path)):
            file_path = Path(file_path)
            if not filename:
                filename = file_path.name

            async with aiofiles.open(file_path, "rb") as f:
                content = await f.read()
        else:
            # File-like object
            content = file_path.read()
            if not filename:
                filename = getattr(file_path, "name", "attachment")

        if not mime_type:
            # Simple MIME type detection based on extension
            import mimetypes

            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                mime_type = "application/octet-stream"

        files = {"file": (filename, content, mime_type)}

        response_data = await self._request("POST", "attachments", files=files)
        return Attachment(**response_data)

    async def get_attachment(self, attachment_id: str) -> Attachment:
        """
        Get attachment metadata.

        Args:
            attachment_id: Attachment ID or full resource name

        Returns:
            Attachment object
        """
        if not attachment_id.startswith("attachments/"):
            attachment_id = f"attachments/{attachment_id}"

        response_data = await self._request("GET", attachment_id)
        return Attachment(**response_data)

    async def get_attachment_binary(
        self, attachment_name: str, filename: str, thumbnail: bool = False
    ) -> bytes:
        """
        Download attachment binary data.

        Args:
            attachment_name: Attachment resource name
            filename: Filename for download
            thumbnail: Whether to get thumbnail version

        Returns:
            Binary file data
        """
        await self._ensure_client()
        assert self._client is not None

        # Use the file endpoint for binary downloads
        url = f"{self.config.base_url}/file/{attachment_name}/{filename}"
        if thumbnail:
            url += "?thumbnail=true"

        auth_headers = await self.auth.authenticate()
        headers = {**self.config.headers, **auth_headers}

        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()
            return response.content
        except httpx.RequestError as e:
            raise NetworkError(f"Failed to download attachment: {e}", e) from e

    async def set_memo_attachments(
        self, memo_id: str, attachment_names: List[str]
    ) -> None:
        """
        Set attachments for a memo.

        Args:
            memo_id: Memo ID or full resource name
            attachment_names: List of attachment resource names
        """
        if not memo_id.startswith("memos/"):
            memo_id = f"memos/{memo_id}"

        # Get attachment objects
        attachments = []
        for name in attachment_names:
            attachment = await self.get_attachment(name)
            attachments.append(attachment.dict())

        request_data = {"attachments": attachments}

        await self._request("PATCH", f"{memo_id}/attachments", json_data=request_data)
