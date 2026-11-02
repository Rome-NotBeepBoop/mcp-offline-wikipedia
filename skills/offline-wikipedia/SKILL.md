---
name: offline-wikipedia
description: Use when answering factual, scientific, historical, or biographical questions offline, or when installing, configuring, or verifying the offline Wikipedia MCP server from local Kiwix ZIM archives.
license: MIT
compatibility: Python 3.10+, git, shell access for automatic installation (macOS and Linux)
metadata:
  author: Rome-NotBeepBoop
  version: "2.0.0"
allowed-tools: search_wikipedia get_article Bash
---

# Offline Wikipedia MCP: Install & Usage Guide

## Overview

This skill guides agents through:
1. **Automated Setup:** Installing, configuring, and verifying the [offline-wikipedia MCP server](https://github.com/Rome-NotBeepBoop/mcp-offline-wikipedia) when the MCP tools are not yet present.
2. **Retrieval Coaching:** Executing the optimal two-step lookup workflow (`search_wikipedia` → clean title → `get_article`) across local Kiwix `.zim` archives.

> [!NOTE]
> **Role Separation:** The *installing agent* running this skill must have shell/terminal access (e.g., Claude Code, Cursor terminal agent). However, the *target client* being configured can be any supported environment on the system (e.g., configuring Claude Desktop or Cursor).
> 
> **OS Support:** Automated installation is supported on **macOS and Linux**. Windows users should follow the manual setup path.

---

## 🛡️ Safety Rules

Before executing any commands or editing files:
1. **Never download multi-GB archives automatically:** Point users to https://library.kiwix.org and ask before initiating any large downloads.
2. **Never overwrite client configs:** Always create a timestamped backup (`config.json.bak.<timestamp>`) before modifying configuration files.
3. **Merge, never replace:** Only add or update the `"offline-wikipedia"` key inside `"mcpServers"`. Preserve all other existing servers and custom client settings.
4. **Never run destructive commands:** Do not execute blanket delete commands (`rm -rf`) without explicit user confirmation.
5. **Zero secret exposure:** This MCP server is entirely local and offline; never add API keys or credentials to its configuration.
6. **No fabricated knowledge:** If the tools are not yet installed or an article is not found, never guess or simulate Wikipedia text from internal memory pretending it came from the server.

---

## Step 0: Tool Detection & Capability Check

Before answering queries or running installation:

1. **Check available tools:**
   - Are `search_wikipedia` and `get_article` present in the current session?
   - **YES:** Skip immediately to the [Usage Section](#usage-section).
   - **NO:** Proceed to step 2 below.

2. **Check environment capabilities:**
   - Does this agent have shell/command execution capabilities on macOS or Linux?
     - **YES:** Proceed to the [Automated Install Flow](#automated-install-flow).
     - **NO (e.g. chat-only LM Studio, or Windows):** Provide the user with the [Manual Installation Path](#manual-installation-path).

---

## Automated Install Flow (macOS & Linux)

Follow these numbered steps sequentially when tools are missing and shell access is available.

### 1. Check System Prerequisites

Run a shell check to verify Python and git:

```bash
git --version && python3 -c "import sys; assert sys.version_info >= (3, 10), 'Python 3.10+ required'; print('Python OK:', sys.version)"
```

- If `git` is missing: Stop and prompt the user to install Git.
- If Python < 3.10 or missing: Stop and prompt the user to install Python 3.10 or higher.

### 2. Identify Client & Archive Directory

Ask the user or confirm:
1. **Target MCP Client:**
   - **Claude Desktop**
   - **Cursor**
   - **Claude Code** (configured via CLI command)
   - *Other client:* Prompt the user to provide their client's MCP configuration file location. Do not guess unsupported paths.
2. **Kiwix Archive Folder (`WIKI_ZIM_DIR`):** Where does the user store their `.zim` files?
   - If the user already has `.zim` files: Confirm the path (e.g. `~/kiwix-zim/`).
   - If the user has **no** `.zim` files: Direct them to [https://library.kiwix.org](https://library.kiwix.org). Recommend starting with **Wikipedia English Mini (nopic)** (~2 GB, ~897,000 core articles). **Never download multi-GB files without explicit confirmation.**

> [!NOTE]
> **Shell Variable Persistence & Path Expansion:**
> - In many agent harnesses, each tool call runs in an independent subshell session. Variables like `$INSTALL_DIR` or `$WIKI_ZIM_DIR` do NOT automatically persist across separate commands. Always re-declare them in each command invocation, or use evaluated literal absolute paths.
> - Always store and pass `$WIKI_ZIM_DIR` as an expanded, resolved absolute path (e.g. `/Users/username/kiwix-zim` rather than a literal `~`), before passing it to `cd`, Python scripts, `claude mcp add`, or JSON configs.

### 3. macOS TCC Sandbox Warning

On macOS, transparency, consent, and control (TCC) restrictions prevent sandboxed subprocesses from accessing personal folders:
- ❌ **Do NOT store `.zim` files in:** `~/Documents`, `~/Desktop`, or `~/Downloads`. The MCP server will fail with `Error opening ZIM file` or `Operation not permitted`.
- ✅ **Recommended location:** Create and use a dedicated home subdirectory: `mkdir -p ~/kiwix-zim`.

### 4. Clone Repo & Set Up Virtual Environment

Clone the repository at pinned release tag `v1.1.1` into a permanent location (default: `~/.local/share/mcp-offline-wikipedia` or user-specified folder):

```bash
INSTALL_DIR="$HOME/.local/share/mcp-offline-wikipedia"
mkdir -p "$(dirname "$INSTALL_DIR")"

git clone --branch v1.1.1 --depth 1 https://github.com/Rome-NotBeepBoop/mcp-offline-wikipedia.git "$INSTALL_DIR"
```

> [!CRITICAL]
> If the `git clone` command fails (for example, if the release tag `v1.1.1` has not yet been pushed to GitHub), **STOP immediately and inform the user**. Do not silently fall back to other branches without user knowledge.

Once cloned:
```bash
cd "$INSTALL_DIR"
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
```

> [!IMPORTANT]
> The server script is located at `src/mcp-wiki-server.py` inside the repository. Always reference the venv Python (`$INSTALL_DIR/venv/bin/python`).

### 5. Verify Installation & Archive Loading

Verify that `libzim` and the archives in the user's chosen `$WIKI_ZIM_DIR` can be opened by the newly created virtual environment:

```bash
"$INSTALL_DIR/venv/bin/python" -c "
import os, sys
from libzim.reader import Archive

zim_dir = os.path.expanduser(sys.argv[1])
assert os.path.isdir(zim_dir), f'Directory not found: {zim_dir}'
zims = [os.path.join(zim_dir, f) for f in os.listdir(zim_dir) if f.endswith('.zim')]
assert len(zims) > 0, f'No .zim files found in {zim_dir}'

for z in zims:
    a = Archive(z)
    print(f'Archive loaded: {os.path.basename(z)} | {a.entry_count:,} entries | Full-text: {a.has_fulltext_index}')
print('Verification SUCCESS!')
" "$WIKI_ZIM_DIR"
```

If verification fails, review the directory path and permissions before editing client configuration.

### 6. Configure MCP Client

> [!IMPORTANT]
> **Path Expansion Rule:** In JSON configuration files, never use unexpanded tildes (`~`) or placeholder variables (`$INSTALL_DIR`). Substitute the full, evaluated absolute paths (e.g. `/Users/username/.local/share/mcp-offline-wikipedia/venv/bin/python`).

#### Client Options:

##### Option A: Claude Code (CLI command)
If configuring Claude Code, run the official CLI command (`--scope user` for global access across all projects, or `--scope project` for local directory scope):
```bash
claude mcp add --scope user offline-wikipedia \
  -e WIKI_ZIM_DIR="$WIKI_ZIM_DIR" \
  -e WIKI_MAX_CHARS="15000" \
  -- "$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/src/mcp-wiki-server.py"
```

##### Option B: Claude Desktop & Cursor (JSON Config File)

* **Claude Desktop:**
  * macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
  * Linux (unofficial builds): `~/.config/Claude/claude_desktop_config.json`
* **Cursor:**
  * Workspace: `.cursor/mcp.json`
  * Global: `~/.cursor/mcp.json`

Run the following inline Python script to safely back up and merge the configuration:

```bash
python3 -c "
import os, sys, json, time, shutil

target_path = os.path.expanduser(sys.argv[1])
venv_python = os.path.abspath(os.path.expanduser(sys.argv[2]))
server_script = os.path.abspath(os.path.expanduser(sys.argv[3]))
zim_dir = os.path.abspath(os.path.expanduser(sys.argv[4]))
max_chars = sys.argv[5] if len(sys.argv) > 5 else '15000'

os.makedirs(os.path.dirname(target_path), exist_ok=True)

if os.path.exists(target_path):
    backup_path = f'{target_path}.bak.{int(time.time())}'
    shutil.copy2(target_path, backup_path)
    print(f'Backup created at: {backup_path}')
    with open(target_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f'ERROR: Invalid JSON in {target_path}: {e}', file=sys.stderr)
            sys.exit(1)
else:
    data = {}

if 'mcpServers' not in data:
    data['mcpServers'] = {}

data['mcpServers']['offline-wikipedia'] = {
    'command': venv_python,
    'args': [server_script],
    'env': {
        'WIKI_ZIM_DIR': zim_dir,
        'WIKI_MAX_CHARS': str(max_chars)
    }
}

with open(target_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'Successfully merged offline-wikipedia into {target_path}')
" "<CONFIG_PATH>" "$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/src/mcp-wiki-server.py" "$WIKI_ZIM_DIR" "15000"
```

##### Option C: Any Other Client
Do not guess configuration paths. Ask the user for their client's MCP configuration file path, check that client's official documentation, and use the merge script above.

### 7. Client Restart Notice & Post-Restart Test

> [!CRITICAL]
> **MCP clients load new tools ONLY on startup.** Newly configured MCP servers will NOT appear in the current active session.
>
> 1. Tell the user: **"Installation and configuration are complete. Please restart your MCP client (e.g. quit and reopen Claude Desktop / Cursor)."**
> 2. Instruct the user to re-invoke the agent after restart with a test prompt: *"What is a Turing machine according to offline Wikipedia?"*

### 8. Quick Troubleshooting

- **`Neither WIKI_ZIM_DIR nor WIKI_ZIM_PATH is set`**: Ensure the `env` block is present in the client config under `offline-wikipedia`.
- **`Error opening ZIM file`**:
  - macOS folder restriction: Move `.zim` files out of `~/Documents`, `~/Desktop`, or `~/Downloads` into `~/kiwix-zim/`.
  - Python mismatch: Confirm `command` points to the venv Python (`venv/bin/python`), which has `libzim>=3.10.0`.
- **`No .zim files found`**: Confirm `WIKI_ZIM_DIR` contains files ending in `.zim`.
- **Missing full-text index**: The server automatically falls back to title suggestion search.

---

## Manual Installation Path (Windows or Chat-Only Clients)

For Windows users or clients without command execution capabilities (e.g., LM Studio):

1. **Terminal setup:** Open your terminal and run:
   ```bash
   git clone --branch v1.1.1 --depth 1 https://github.com/Rome-NotBeepBoop/mcp-offline-wikipedia.git
   cd mcp-offline-wikipedia
   python -m venv venv
   # On macOS/Linux:
   ./venv/bin/pip install -r requirements.txt
   # On Windows:
   venv\Scripts\pip.exe install -r requirements.txt
   ```
2. **Download archive:** Download a `.zim` file (e.g. English Wikipedia Mini nopic) from [https://library.kiwix.org](https://library.kiwix.org) into a dedicated folder (e.g. `~/kiwix-zim/` or `C:/kiwix-zim/`).
3. **Configure LM Studio:**
   - In LM Studio, go to **Developer → mcp.json**.
   - Add `"offline-wikipedia"` under `"mcpServers"` pointing to your venv's Python and `src/mcp-wiki-server.py`.
   - Set `"WIKI_ZIM_DIR"` to the absolute path of your archive folder.
4. **Restart the client application.**

---

## Usage Section

Follow these operational rules when `search_wikipedia` and `get_article` are active.

### The Two-Step Retrieval Workflow

```
[User Question]
      │
      ▼
1. Extract topic noun phrase / keywords
      │
      ▼
2. Call search_wikipedia(query="<keyword>", num_results=5)
      │
      ▼
3. Select exact title & STRIP archive label [...]
      │
      ▼
4. Call get_article(title="<clean_title>")
      │
      ▼
5. Synthesize factual response with archive attribution
```

### 1. Formulate Keyword Queries

Search queries **must be specific topic keywords or proper nouns**, formatted like Wikipedia article titles.

| ❌ Poor (Conversational / Sentences) | ✅ Optimal (Keywords / Proper Nouns) |
|---|---|
| `"who was Alan Turing and what did he invent?"` | `"Alan Turing"` |
| `"why did the Roman Empire collapse?"` | `"Fall of the Western Roman Empire"` |
| `"how do black holes form in astrophysics?"` | `"Black hole"` |
| `"what is the speed of light in vacuum?"` | `"Speed of light"` |

*Reason:* The underlying searcher calculates keyword density and title prefixes. Conversational padding (`who was`, `how do`, `tell me about`) degrades ranking relevance.

### 2. Clean Title Contract

`search_wikipedia` outputs results formatted as:
```text
Found 5 result(s) for 'Alan Turing':

  1. Alan Turing  [wikipedia_en_wp1-0.8_nopic_2026-04]
  2. Turing machine  [wikipedia_en_wp1-0.8_nopic_2026-04]
  3. Turing test  [wikipedia_en_wp1-0.8_nopic_2026-04]
```

- ✅ **Always strip the archive label:** Pass `get_article(title="Alan Turing")`.
- ❌ **The `[archive_label]` suffix fails:** Passing `"Alan Turing  [wikipedia_en_wp1-0.8_nopic_2026-04]"` causes title lookup to fail completely.
- ⚠️ **Strip leading numbers:** While a leading `"1. Alan Turing"` might occasionally resolve via full-text fallback if an index exists, it fails on archives without a full-text index and can misroute to numbered articles. Always pass the clean title.

### 3. Context Management & Truncation

- Articles exceeding `WIKI_MAX_CHARS` (default 15,000 characters) end with `...[Article truncated. Set the WIKI_MAX_CHARS env var to raise the limit.]`.
- Retrieve **1 to 2 articles per turn** maximum. Do not mass-fetch articles.
- Cite the source archive in your response (e.g. *"According to the offline Wikipedia archive..."*).

### 4. Zero-Result Strategy

If `search_wikipedia` returns `"No articles found for '...'"`:
1. Strip adjectives or qualifiers (e.g., `"19th century steam locomotive"` → `"Steam locomotive"`).
2. Broaden to root scientific or historical concepts (e.g., `"CRISPR-Cas9 mechanism"` → `"CRISPR"`).
3. Try standard alternative spellings (e.g., `"World War I"` vs `"First World War"`).

---

## Rationalizations & Red Flags

| Rationalization | Reality |
|---|---|
| *"I'll guess the title and call `get_article` directly."* | ZIM title lookup requires exact titles. Guessing wastes turns on `Not found` errors. Always search first. |
| *"I can pass a full sentence query to search_wikipedia."* | Sentences dilute keyword density in Xapian index. Convert questions to topic noun phrases. |
| *"I can pass the raw search output line to get_article."* | Suffixes like `[archive_label]` cause lookup to fail. Strip brackets and numbers. |
| *"I'll answer from internal memory and pretend it's from Wikipedia."* | Fabricating offline source data violates accuracy requirements. Run the install flow or report missing articles honestly. |

### Red Flags — STOP and Correct
- 🚩 Calling `get_article` before calling `search_wikipedia` on unfamiliar topics.
- 🚩 Passing strings with question marks `?` into `search_wikipedia`.
- 🚩 Passing `[...]` tags into `get_article`.
- 🚩 Overwriting a client config without creating a backup file first.
