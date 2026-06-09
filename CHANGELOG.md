# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-06-09
### Fixed
- Corrected tool names in README (`search_wikipedia` / `get_article`) to match the actual MCP server implementation.
- Fixed LM Studio MCP config example: removed incorrect `src/` path prefix and changed `.venv` to `venv` to match the installation instructions.
- Bumped minimum `libzim` requirement from `>=3.1.0` to `>=3.10.0` — older versions cannot open ZIM archives produced by Kiwix in 2026 and will raise `Error opening ZIM file`.
### Added
- Troubleshooting entry for macOS `~/Documents` permissions — LM Studio is blocked from reading ZIM files stored there unless Full Disk Access is granted. Workaround: move the `.zim` file to the home directory.
- Troubleshooting entry explaining the "wrong Python" problem: always use the venv Python in your MCP config, not the system `python3`, to ensure the correct `libzim` is used.
- Warning in the LM Studio config section emphasising that the venv Python path must be used.

## [1.0.0] - 2026-06-08
### Added
- Initial release of the Offline Wikipedia MCP Server.
- `search_wikipedia` tool utilizing `libzim` full-text index and fallback suggestion search.
- `get_article` tool for extracting clean HTML-to-plaintext entries.
- Double-checked threading lock for concurrent MCP execution.
- Context window protection via `WIKI_MAX_CHARS` environment variable.
- Support for LM Studio, Claude Desktop, and Cursor.