# Changelog

All notable changes to the Memos Python Client will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-10-24

### Added
- Initial release of the Memos Python Client
- Core client functionality with async/await support
- Authentication support (JWT tokens and username/password)
- Memo operations: create, read, update, delete, search
- Attachment support: upload, download, associate with memos
- Advanced search with filtering capabilities
- Comprehensive error handling and custom exceptions
- Type safety with Pydantic models and type hints
- Poetry-based project structure
- Examples and documentation
- MIT License

### Features
- **Search memos** by keywords, tags, creator, visibility, and date ranges
- **CRUD operations** for memos with full field support
- **Attachment handling** for images and files with MIME type detection
- **Multiple authentication methods** (JWT preferred)
- **Rich filtering** with CEL-like expressions
- **Async context manager** support for proper resource cleanup
- **Comprehensive models** with validation and type safety
- **Error handling** with specific exception types
- **Python 3.8+** compatibility

### Technical
- Built with modern Python async/await patterns
- Uses httpx for HTTP client functionality
- Pydantic v2 for data validation and serialization
- Poetry for dependency management
- Comprehensive type hints throughout
- Follows REST API conventions
- Support for both REST and future gRPC protocols

## [Unreleased]

### Planned
- gRPC client implementation
- Batch operations for memos
- Caching layer for improved performance
- Rate limiting and retry logic
- WebSocket support for real-time updates
- Plugin system for extensibility
