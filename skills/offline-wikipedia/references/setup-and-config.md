# Setup and Configuration Guide for Offline Wikipedia MCP

This reference guide provides full configuration examples and troubleshooting instructions for integrating the **Offline Wikipedia MCP Server** into different AI coding harnesses and clients.

---

## 1. Client Configurations

Always use the **full absolute path** to the virtual environment Python (`venv/bin/python` or `venv\Scripts\python.exe`), rather than system `python3`. This ensures `libzim` and the required C-bindings are loaded properly.

### Claude Desktop

Edit your Claude Desktop configuration file:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux (unofficial builds):** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "offline-wikipedia": {
      "command": "/absolute/path/to/mcp-offline-wikipedia/venv/bin/python",
      "args": [
        "/absolute/path/to/mcp-offline-wikipedia/src/mcp-wiki-server.py"
      ],
      "env": {
        "WIKI_ZIM_DIR": "/path/to/kiwix-zim/",
        "WIKI_MAX_CHARS": "15000"
      }
    }
  }
}
```

### Cursor

Add to your Cursor MCP settings (`.cursor/mcp.json` in workspace or Global Settings → Features → MCP):

```json
{
  "mcpServers": {
    "offline-wikipedia": {
      "command": "/absolute/path/to/mcp-offline-wikipedia/venv/bin/python",
      "args": [
        "/absolute/path/to/mcp-offline-wikipedia/src/mcp-wiki-server.py"
      ],
      "env": {
        "WIKI_ZIM_DIR": "/path/to/kiwix-zim/"
      }
    }
  }
}
```

### Claude Code

Configure using the `claude mcp add` CLI command (`--scope user` for global access across all projects, or `--scope project` for local directory scope):

```bash
claude mcp add --scope user offline-wikipedia \
  -e WIKI_ZIM_DIR=/path/to/kiwix-zim/ \
  -e WIKI_MAX_CHARS=15000 \
  -- /absolute/path/to/mcp-offline-wikipedia/venv/bin/python /absolute/path/to/mcp-offline-wikipedia/src/mcp-wiki-server.py
```

### LM Studio

Navigate to **Developer → mcp.json** and configure:

```json
{
  "mcpServers": {
    "offline-wikipedia": {
      "command": "/absolute/path/to/mcp-offline-wikipedia/venv/bin/python",
      "args": [
        "/absolute/path/to/mcp-offline-wikipedia/src/mcp-wiki-server.py"
      ],
      "env": {
        "WIKI_ZIM_DIR": "/path/to/kiwix-zim/",
        "WIKI_MAX_CHARS": "15000"
      }
    }
  }
}
```

---

## 2. Environment Variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `WIKI_ZIM_DIR` | Preferred | — | Directory path containing one or more `.zim` files. All archives in this folder are auto-loaded. |
| `WIKI_ZIM_PATH` | Fallback | — | Single `.zim` file path (legacy single-archive mode). |
| `WIKI_MAX_CHARS` | Optional | `15000` | Maximum number of characters returned per article to protect context window limits. |

---

## 3. macOS Sandboxing & Permission Notice

macOS enforces Transparency, Consent, and Control (TCC) restrictions on user personal folders:
- ❌ Do **NOT** store `.zim` archives inside `~/Documents/`, `~/Desktop/`, or `~/Downloads/`. Subprocesses spawned by MCP host applications will be blocked with an `Operation not permitted` or `Error opening ZIM file` error.
- ✅ Store archives in a dedicated directory in your home folder, e.g. `~/kiwix-zim/`.

---

## 4. Verification

Run the bundled diagnostic script to ensure everything is wired correctly:

```bash
python scripts/verify_setup.py --zim-dir ~/kiwix-zim/
```
