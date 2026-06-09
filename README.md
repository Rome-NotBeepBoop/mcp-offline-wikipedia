# Offline Wikipedia MCP Server 📚🔌

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![MCP SDK](https://img.shields.io/badge/MCP-SDK-green.svg)](https://github.com/modelcontextprotocol/python-sdk)

A fast, completely offline [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that connects local or cloud LLMs to locally downloaded Kiwix archives (`.zim` files).

This project bridges the gap between Large Language Models (running locally in **LM Studio**, **Claude Desktop**, or **Cursor**) and massive offline knowledge bases. By using the official Python MCP SDK and `libzim`, your LLM can search and read full Wikipedia articles — and any other Kiwix archive — **without an internet connection**.

## ✨ Features

- 🔍 **Smart search** — uses full-text index search with automatic fallback to title/prefix search
- 📚 **Multi-archive support** — point at a folder and every `.zim` file inside is loaded automatically
- 📄 **Direct article lookup** — retrieve a specific article by exact title, bypassing search
- 🏷️ **Source labelling** — results show which archive they came from (e.g. `[wikipedia_en_wp1-0.8_nopic_2026-04]`)
- 🧹 **Clean output** — strips HTML, scripts, tables, citation numbers `[1]`, and `[edit]` markers
- ✂️ **Configurable truncation** — prevent context-window overflows with `WIKI_MAX_CHARS`
- 🔒 **Thread-safe** — double-checked locking for safe use in concurrent MCP environments
- 📦 **Any `.zim` file** — works with Wikipedia, Wiktionary, Stack Overflow, and other Kiwix archives

## 🛠️ Tools Exposed to the LLM

| Tool | Description |
|---|---|
| `search_wikipedia(query, num_results)` | Search all loaded archives using full-text index with fallback to title/prefix search |
| `get_article(title)` | Fetch a specific article by its exact title, searching across all loaded archives |

## 📥 Step 1 — Download Kiwix `.zim` Archives

Because LLMs only process text, it is highly recommended to download **"nopic"** (no pictures) versions to save disk space.

1. Go to the **Kiwix Library**: [https://library.kiwix.org/?lang=eng&q=wikipedia](https://library.kiwix.org/?lang=eng&q=wikipedia)
2. Recommended files:
   - **Wikipedia English (wp1/Mini, nopic)** — most important articles, no images (~2 GB)
   - **Wikipedia English (Maxi, nopic)** — full Wikipedia, no images (~22 GB)
3. Save all `.zim` files into a single dedicated folder (e.g. `~/kiwix-zim/`). The server will load every `.zim` file in that folder automatically.

> ⚠️ **macOS users:** Do **not** store your `.zim` files inside `~/Documents`, `~/Desktop`, or `~/Downloads`. macOS restricts app access to those folders and will cause an `Error opening ZIM file`. Use your home directory or a custom folder instead (e.g. `~/kiwix-zim/`).

## 🚀 Step 2 — Installation

```bash
git clone https://github.com/Rome-NotBeepBoop/mcp-offline-wikipedia.git
cd mcp-offline-wikipedia

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Step 3 — Configure Your MCP Client

Replace the example paths below with your actual paths.

> ⚠️ **Always use the full path to the venv Python** (`venv/bin/python`), not the system `python3`. This guarantees the correct `libzim` version is used.

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "offline-wikipedia": {
      "command": "/absolute/path/to/mcp-offline-wikipedia/venv/bin/python",
      "args": ["/absolute/path/to/mcp-offline-wikipedia/mcp_wiki_server.py"],
      "env": {
        "WIKI_ZIM_DIR": "/absolute/path/to/your/kiwix-zim/",
        "WIKI_MAX_CHARS": "15000"
      }
    }
  }
}
```

### Cursor

Add the following to your Cursor MCP config (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "offline-wikipedia": {
      "command": "/absolute/path/to/mcp-offline-wikipedia/venv/bin/python",
      "args": ["/absolute/path/to/mcp-offline-wikipedia/mcp_wiki_server.py"],
      "env": {
        "WIKI_ZIM_DIR": "/absolute/path/to/your/kiwix-zim/"
      }
    }
  }
}
```

### LM Studio

In LM Studio, go to **Developer → mcp.json** and fill in:

```json
{
  "mcpServers": {
    "offline-wikipedia": {
      "command": "/absolute/path/to/mcp-offline-wikipedia/venv/bin/python",
      "args": ["/absolute/path/to/mcp-offline-wikipedia/mcp_wiki_server.py"],
      "env": {
        "WIKI_ZIM_DIR": "/absolute/path/to/your/kiwix-zim/",
        "WIKI_MAX_CHARS": "15000"
      }
    }
  }
}
```

## 🌍 Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `WIKI_ZIM_DIR` | ✅ Preferred | — | Path to a folder — every `.zim` file inside is loaded |
| `WIKI_ZIM_PATH` | Legacy | — | Path to a single `.zim` file (use `WIKI_ZIM_DIR` instead) |
| `WIKI_MAX_CHARS` | No | `15000` | Max characters returned per article |

> `WIKI_ZIM_DIR` takes priority over `WIKI_ZIM_PATH` if both are set.

## ❓ Troubleshooting

**`Neither WIKI_ZIM_DIR nor WIKI_ZIM_PATH is set`**
→ Make sure the `env` block is present in your MCP client config with the correct variable name.

**`ZIM archive not found at: ...`**
→ Double-check the path. On Windows, use forward slashes or escaped backslashes: `C:/Users/you/kiwix-zim/`.

**macOS: `Error opening ZIM file` even though the file exists and the path is correct**
→ macOS restricts app access to `~/Documents`, `~/Desktop`, and `~/Downloads` without explicit permission. LM Studio (and the Python process it spawns) may be silently blocked. Two fixes:
- **Quick fix:** Move your `.zim` files to `~/kiwix-zim/` or any other folder you created yourself, and update `WIKI_ZIM_DIR` accordingly.
- **Proper fix:** Go to **System Settings → Privacy & Security → Files and Folders** and grant LM Studio access to the folder containing your `.zim` files.

**`Error opening ZIM file` — but the file opens fine in a Python terminal**
→ LM Studio is using a different Python than your terminal. Always use the **venv Python** in your MCP config (`venv/bin/python`), not the system `python3`. Verify it has the right libzim:
```bash
/absolute/path/to/venv/bin/python -c "import libzim; print('ok')"
```

**Server starts but the LLM says it can't find any articles**
→ Some `.zim` files don't have a full-text index. The server will automatically fall back to title search, but results may be less accurate for vague queries. Try using the exact article title.

**High memory usage**
→ Each `.zim` archive is loaded on first use. Larger archives (Maxi) will use more RAM. The Mini/nopic version is recommended for most use cases.

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change. Pull requests should target the `main` branch.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-improvement`)
3. Commit your changes (`git commit -m 'Add some improvement'`)
4. Push to your branch (`git push origin feature/my-improvement`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.