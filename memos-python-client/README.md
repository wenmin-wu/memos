# Memos Python Client

A comprehensive Python client library for the [Memos](https://github.com/usememos/memos) note-taking application.

## Features

- 🔍 **Search memos** by keywords, tags, and filters
- 📝 **CRUD operations** for memos (create, read, update, delete)
- 📎 **Attachment support** for images and files
- 🔐 **Multiple authentication methods** (JWT tokens, session-based)
- 🚀 **Async/await support** for high performance
- 🛡️ **Type safety** with Pydantic models and type hints
- 📚 **Rich filtering** with advanced query capabilities

## Installation

```bash
pip install memos-client
```

Or using Poetry:

```bash
poetry add memos-client
```

## Quick Start

```python
import asyncio
from memos_client import MemosClient, Visibility

async def main():
    # Initialize client
    client = MemosClient(
        base_url="https://your-memos-instance.com",
        access_token="your-jwt-token"
    )
    
    # Search memos
    memos = await client.search_memos(
        query="python development",
        tags=["programming", "tutorial"],
        limit=10
    )
    
    # Create a new memo
    memo = await client.create_memo(
        content="# My Python Notes\n\nSome important notes...",
        visibility=Visibility.PRIVATE,
        tags=["python", "notes"]
    )
    
    # Update the memo
    updated_memo = await client.update_memo(
        memo_id=memo.name,
        content="# Updated Python Notes\n\nUpdated content...",
    )
    
    # Get specific memo
    retrieved_memo = await client.get_memo(memo.name)
    
    print(f"Created memo: {retrieved_memo.snippet}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Authentication

### JWT Token (Recommended)

```python
client = MemosClient(
    base_url="https://your-memos-instance.com",
    access_token="your-jwt-token"
)
```

### Username/Password

```python
client = MemosClient(
    base_url="https://your-memos-instance.com",
    username="your-username",
    password="your-password"
)
```

## Advanced Usage

### Complex Search Queries

```python
from datetime import datetime, timedelta

# Search with multiple filters
memos = await client.search_memos(
    filter={
        "content.contains": "machine learning",
        "visibility": Visibility.PUBLIC,
        "create_time.after": datetime.now() - timedelta(days=30),
        "tags.any": ["ai", "ml", "data-science"]
    },
    order_by="create_time desc",
    limit=50
)
```

### Working with Attachments

```python
# Upload and attach an image
attachment = await client.upload_attachment(
    file_path="screenshot.png",
    filename="project_screenshot.png"
)

# Create memo with attachment
memo = await client.create_memo(
    content="Here's the latest project screenshot:",
    attachments=[attachment.name]
)

# Download attachment
binary_data = await client.get_attachment_binary(
    attachment_name=attachment.name,
    filename=attachment.filename
)
```

### Batch Operations

```python
# Create multiple memos
memo_contents = [
    "First memo content",
    "Second memo content",
    "Third memo content"
]

memos = await client.create_memos_batch(
    contents=memo_contents,
    visibility=Visibility.PRIVATE
)
```

## API Reference

### MemosClient

The main client class providing access to all Memos API functionality.

#### Methods

- `search_memos(query, tags, filter, limit, ...)` - Search memos with filters
- `get_memo(memo_id)` - Retrieve a specific memo
- `create_memo(content, visibility, tags, attachments, ...)` - Create a new memo
- `update_memo(memo_id, content, tags, ...)` - Update an existing memo
- `delete_memo(memo_id)` - Delete a memo
- `upload_attachment(file_path, filename, ...)` - Upload a file attachment
- `get_attachment_binary(attachment_name, filename)` - Download attachment data

### Models

#### Memo

```python
class Memo(BaseModel):
    name: str  # Resource name: memos/{memo}
    content: str  # Markdown content
    visibility: Visibility
    tags: List[str]
    create_time: datetime
    update_time: datetime
    creator: str
    attachments: List[Attachment]
    # ... other fields
```

#### Attachment

```python
class Attachment(BaseModel):
    name: str  # Resource name: attachments/{attachment}
    filename: str
    type: str  # MIME type
    size: int
    create_time: datetime
    memo: Optional[str]  # Associated memo
    # ... other fields
```

## Development

### Setup

```bash
git clone https://github.com/wenmin-wu/memos-python-client.git
cd memos-python-client
poetry install
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=memos_client

# Run specific test file
poetry run pytest tests/unit/test_client.py
```

### Code Quality

```bash
# Format code
poetry run black memos_client tests

# Sort imports
poetry run isort memos_client tests

# Lint code
poetry run ruff check memos_client tests

# Type checking
poetry run mypy memos_client
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## Support

- 📖 [Documentation](https://github.com/wenmin-wu/memos-python-client/docs)
- 🐛 [Issue Tracker](https://github.com/wenmin-wu/memos-python-client/issues)
- 💬 [Discussions](https://github.com/wenmin-wu/memos-python-client/discussions)
