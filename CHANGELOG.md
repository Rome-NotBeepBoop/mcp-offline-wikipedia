# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-06-09
### Added
- **Multi-archive support** — set `WIKI_ZIM_DIR` to a folder and every `.zim` file inside is loaded and searched automatically. No config changes needed when adding new archives — just drop a new `.zim` file in the folder.
- Search results now include a source label showing which archive the article came from (e.g. `Black hole  [wikipedia_en_wp1-0.8_nopic_2026-04]`).
- `get_article` now searches across all loaded archives and returns the first match.
- `WIKI_ZIM_DIR` environment variable (preferred over `WIKI_ZIM_PATH`). Both are still supported; `WIKI_ZIM_DIR` takes priority.
- Startup logs now print the Python executable path and libzim version to aid debugging.
### Changed
- `get_archives()` replaces `get_archive()` internally, returning a list of `(label, Archive)` tuples.
- All log messages now include the archive label (e.g. `[wikipedia_en_wp1...]`) for easier multi-archive debugging.
- All MCP config examples updated to use `WIKI_ZIM_DIR` instead of `WIKI_ZIM_PATH`.

## [1.0.1] - 2026-06-09
### Fixed
- Corrected tool names in README (`search_wikipedia` / `get_article`) to match the actual MCP server implementation.
- Fixed LM Studio MCP config example: removed incorrect `src/` path prefix and changed `.venv` to `venv` to match the installation instructions.
- Bumped minimum `libzim` requirement from `>=3.1.0` to `>=3.10.0` — older versions cannot open ZIM archives produced by Kiwix in 2026 and will raise `Error opening ZIM file`.
### Added
- Troubleshooting entry for macOS `~/Documents` permissions — LM Studio is blocked from reading ZIM files stored there unless Full Disk Access is granted. Workaround: move the `.zim` file to a custom folder like `~/kiwix-zim/`.
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