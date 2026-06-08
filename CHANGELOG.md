# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-08
### Added
- Initial release of the Offline Wikipedia MCP Server.
- `search_wikipedia` tool utilizing `libzim` full-text index and fallback suggestion search.
- `get_article` tool for extracting clean HTML-to-plaintext entries.
- Double-checked threading lock for concurrent MCP execution.
- Context window protection via `WIKI_MAX_CHARS` environment variable.
- Support for LM Studio, Claude Desktop, and Cursor.