# Offline Wikipedia MCP Server 📚🔌

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![MCP SDK](https://img.shields.io/badge/MCP-SDK-green.svg)](https://github.com/modelcontextprotocol/python-sdk)

A fast, completely offline [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that connects local or cloud LLMs to locally downloaded Kiwix Wikipedia archives (`.zim` files).

This project bridges the gap between Large Language Models (running locally in **LM Studio**, **Claude Desktop**, or **Cursor**) and massive offline knowledge bases. By using the official Python MCP SDK and `libzim`, your LLM can search and read full Wikipedia articles **without an internet connection**.

---

## 🛠️ Tools Exposed to the LLM

Once connected, your LLM will automatically see and use these tools:

| Tool | Parameters | Description |
|---|---|---|
| `search_wikipedia` | `query` (str), `num_results` (int) | Fuzzy-searches the `.zim` archive and returns a list of matching article titles. The LLM uses this to find the exact title before reading. |
| `get_article` | `title` (str) | Fetches the full, cleaned plain text of a specific Wikipedia article by its exact title. |

---

## 📖 Usage Example

Here is what happens behind the scenes when you ask your connected LLM a question:

**You:** *"What is the Event Horizon Telescope?"*
1. **LLM internal thought:** *I need to look this up.* -> Calls `search_wikipedia(query="Event Horizon Telescope")`.
2. **MCP Server returns:** `Found: 1. Event Horizon Telescope, 2. Black hole...`
3. **LLM internal thought:** *I will read the first article.* -> Calls `get_article(title="Event Horizon Telescope")`.
4. **MCP Server returns:** The clean text of the article.
5. **LLM replies to you:** *"The Event Horizon Telescope (EHT) is a large telescope array consisting of a global network of radio observatories..."*

---

## 📥 Step 1 — Download a Wikipedia `.zim` Archive

Because LLMs only process text, it is highly recommended to download a **"mini"** or **"nopic"** (no pictures) version to save massive amounts of disk space.

1. Go to the **Kiwix Library**: [https://library.kiwix.org/?lang=eng&q=wikipedia](https://library.kiwix.org/?lang=eng&q=wikipedia)
2. Recommended files:
   - **Wikipedia English (Mini)** — text, lists, and tables. No images. (~10–15 GB)
   - **Wikipedia English (Maxi)** — full Wikipedia with images. (~100 GB+)
3. Save the `.zim` file to a **permanent path** on your computer.

---

## 🚀 Step 2 — Installation & Platform Notes

### Prerequisites & Platform Warnings ⚠️
* **Mac (Apple Silicon / M1/M2/M3):** Installing the `libzim` python package can sometimes fail if you don't have the underlying C++ libraries. If `pip install` fails, install the system library first using Homebrew: `brew install libzim`.
* **Linux (Debian/Ubuntu):** You may need the build essentials: `sudo apt-get install build-essential libzim-dev`.
* **Windows:** Usually works out of the box with standard Python 3.10+.

### Setup

```bash
git clone https://github.com/Rome-NotBeepBoop/mcp-offline-wikipedia.git
cd mcp-offline-wikipedia

# Create a virtual environment (use venv or .venv)
python -m venv .venv

# Activate the environment
source .venv/bin/activate        # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ Step 3 — Configure Your MCP Client

You need to tell your MCP client where the server script and your `.zim` file are. 

### Claude Desktop
Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "offline-wikipedia": {
      "command": "/absolute/path/to/mcp-offline-wikipedia/.venv/bin/python",
      "args": ["/absolute/path/to/mcp-offline-wikipedia/src/mcp_wiki_server.py"],
      "env": {
        "WIKI_ZIM_PATH": "/absolute/path/to/your/wikipedia.zim",
        "WIKI_MAX_CHARS": "15000"
      }
    }
  }
}
```

### LM Studio

In LM Studio, go to Developer → MCP Servers → Edit mcp_config.json and add:
```json
{
  "mcpServers": {
    "offline-wikipedia": {
      "command": "/absolute/path/to/mcp-offline-wikipedia/.venv/bin/python",
      "args": ["/absolute/path/to/mcp-offline-wikipedia/src/mcp_wiki_server.py"],
      "env": {
        "WIKI_ZIM_PATH": "/absolute/path/to/your/wikipedia.zim",
        "WIKI_MAX_CHARS": "15000"
      }
    }
  }
}
```
(Note for Windows users: Ensure all backslashes in your JSON paths are double-escaped like ```C:\\Users\\Name\DIRECTORY```)

## 🤝 Community & Support
* Found a bug? Open an issue using our issue templates.
* Want to contribute? Check out [CONTRIBUTING.md](CONTRIBUTING.md).
* Check the [CHANGELOG.md](CHANGELOG.md) for recent updates.

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.