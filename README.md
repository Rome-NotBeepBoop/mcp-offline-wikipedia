# Offline Wikipedia MCP Server 📚🔌

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![MCP SDK](https://img.shields.io/badge/MCP-SDK-green.svg)](https://github.com/modelcontextprotocol/python-sdk)

A fast, completely offline [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that connects local or cloud LLMs to locally downloaded Kiwix Wikipedia archives (`.zim` files).

This project bridges the gap between Large Language Models (running locally in **LM Studio**, **Claude Desktop**, or **Cursor**) and massive offline knowledge bases. By using the official Python MCP SDK and `libzim`, your LLM can search and read full Wikipedia articles **without an internet connection**.

## ✨ Features

- 🔍 **Smart search** — uses full-text index search with automatic fallback to title/prefix search
- 📄 **Direct article lookup** — retrieve a specific article by exact title, bypassing search
- 🧹 **Clean output** — strips HTML, scripts, tables, citation numbers `[1]`, and `[edit]` markers
- ✂️ **Configurable truncation** — prevent context-window overflows with `WIKI_MAX_CHARS`
- 🔒 **Thread-safe** — double-checked locking for safe use in concurrent MCP environments
- 📦 **Any `.zim` file** — works with Wikipedia, Wiktionary, Stack Overflow, and other Kiwix archives

## 🛠️ Tools Exposed to the LLM

| Tool | Description |
|---|---|
| `search_offline_wiki(query)` | Fuzzy-search the archive for the best matching article |
| `get_offline_wiki_article(title)` | Fetch a specific article by its exact title |

## 📥 Step 1 — Download a Wikipedia `.zim` Archive

Because LLMs only process text, it is highly recommended to download a **"mini"** or **"nopic"** (no pictures) version to save massive amounts of disk space.

1. Go to the **Kiwix Library**: [https://library.kiwix.org/?lang=eng&q=wikipedia](https://library.kiwix.org/?lang=eng&q=wikipedia)
2. Recommended files:
   - **Wikipedia English (Mini)** — text, lists, and tables. No images. (~10–15 GB)
   - **Wikipedia English (Maxi)** — full Wikipedia with images. (~100 GB+)
3. Save the `.zim` file to a **permanent path** on your computer (you'll reference it in the config below).

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

You need to tell your MCP client (Claude Desktop, Cursor, etc.) where the server script and your `.zim` file are. Replace the example paths below with your actual paths.

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "offline-wikipedia": {
      "command": "/absolute/path/to/mcp-offline-wikipedia/venv/bin/python",
      "args": ["/absolute/path/to/mcp-offline-wikipedia/mcp_wiki_server.py"],
      "env": {
        "WIKI_ZIM_PATH": "/absolute/path/to/your/wikipedia.zim",
        "WIKI_MAX_CHARS": "15000"
      }
    }
  }
}
```

### Cursor

Add the following to your Cursor MCP config (`.cursor/mcp.json` in your project, or the global config):

```json
{
  "mcpServers": {
    "offline-wikipedia": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": ["/absolute/path/to/mcp_wiki_server.py"],
      "env": {
        "WIKI_ZIM_PATH": "/absolute/path/to/wikipedia.zim"
      }
    }
  }
}
```

### LM Studio

In LM Studio, go to **Developer → MCP Servers → Add Server** and fill in:
- **Command:** `/absolute/path/to/venv/bin/python`
- **Args:** `/absolute/path/to/mcp_wiki_server.py`
- **Env:** `WIKI_ZIM_PATH=/absolute/path/to/wikipedia.zim`

## 🌍 Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `WIKI_ZIM_PATH` | ✅ Yes | — | Absolute path to your `.zim` archive |
| `WIKI_MAX_CHARS` | No | `15000` | Max characters returned per article |

## ❓ Troubleshooting

**`WIKI_ZIM_PATH environment variable is missing`**
→ Make sure the `env` block is present in your MCP client config with the correct path.

**`ZIM archive not found at: ...`**
→ Double-check the path. On Windows, use forward slashes or escaped backslashes: `C:/Users/you/wiki.zim`.

**Server starts but the LLM says it can't find any articles**
→ Some `.zim` files don't have a full-text index. The server will automatically fall back to title search, but results may be less accurate for vague queries. Try using the exact article title.

**High memory usage**
→ The `.zim` archive is loaded into memory on first use. Larger archives (Maxi) will use more RAM. The Mini/nopic version is recommended for most use cases.

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change. Pull requests should target the `main` branch.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-improvement`)
3. Commit your changes (`git commit -m 'Add some improvement'`)
4. Push to your branch (`git push origin feature/my-improvement`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
