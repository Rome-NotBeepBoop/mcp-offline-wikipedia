# Agensi Marketplace Listing: Offline Wikipedia MCP

Copy and paste the sections below directly into the **Agensi Creator Dashboard** when publishing the skill.

---

## Listing Metadata

### Name (< 60 chars)
Offline Wikipedia (Kiwix MCP Setup & Research)

### Summary (< 300 chars, no markdown asterisks)
Equips your AI agent to automatically install, configure, and search the open-source Offline Wikipedia MCP server on macOS or Linux. Includes safe client config merging, pre-flight verification, and guided two-step retrieval coaching across local Kiwix ZIM archives.

### Price
$1.00 USD (one-time)

### Category
Research & Analysis

### Tags
`wikipedia`, `mcp`, `kiwix`, `offline`, `air-gapped`, `research`, `knowledge-base`, `local-ai`

---

## Permissions to Tick in Agensi Dashboard
- [x] **Terminal / Shell Execution** (Required during installation to clone repo, create venv, and run pip)
- [x] **Read Files** (To inspect existing client MCP configs and verify `.zim` archives)
- [x] **Write Files** (To write backup files and merge the server entry into client MCP config)
- [x] **Network Access** (Used exclusively during setup to clone the GitHub repo and install PyPI dependencies; runtime is 100% offline)
- [x] **Environment Variables** (To set `WIKI_ZIM_DIR` and `WIKI_MAX_CHARS` in client MCP config)

---

## Full Description

Turn your AI agent into an offline encyclopedic researcher.

The underlying **Offline Wikipedia MCP Server** is completely open source (MIT licensed) on GitHub (`Rome-NotBeepBoop/mcp-offline-wikipedia`). Anyone can install it manually by reading the README.

**What does this $1 Agensi Skill give you?**
It provides an automated agent setup workflow and guided retrieval coaching:
1. **Automated agent installation:** Ask your agent to set up the server. An agent with shell access (such as Claude Code or a terminal-enabled workspace) inspects prerequisites, clones the pinned release tag (`v1.1.2`), creates an isolated virtual environment, installs dependencies, and tests archive loading.
2. **Safe config merging:** Automatically backs up your client config (`config.json.bak.<timestamp>`) and merges the `offline-wikipedia` server entry into `mcpServers` without overwriting or disrupting any existing MCP tools.
3. **Structured retrieval coaching:** Unprepared LLMs frequently stumble with offline ZIM archives by asking conversational sentences ("what happened in 1789?"), passing unstripped archive tags (`get_article("Title [archive_label]")`), or guessing non-existent titles. This skill guides the agent through the two-step retrieval workflow, keyword formulation rules, title sanitization, and context window budgeting.

---

## Compatibility & Requirements

- **Role Separation:** The *installing agent* requires shell access (e.g. Claude Code or a Cursor terminal agent). The *target client* being configured can be any supported MCP environment on the same machine (Claude Desktop, Cursor, Claude Code).
- **Automated Install OS Support:** macOS and Linux. Windows users can follow the included manual setup steps.
- **Python & Git:** Python 3.10–3.14 (tested and verified on 3.10, 3.11, 3.12, 3.13, 3.14) and Git installed on system PATH.
- **ZIM Archives:** Requires at least one Kiwix `.zim` archive (e.g. English Wikipedia Mini nopic, ~2 GB) stored on your local disk (e.g. in `~/kiwix-zim/`).
- **Chat-Only Clients (e.g. LM Studio):** Plain LM Studio chat does not offer terminal access. Complete manual terminal steps are provided for the user.
- **Post-Install Restart Notice:** MCP clients load newly configured servers on startup. After your agent finishes setup, restart your client and re-invoke the agent.

---

## File Scopes

During installation, the agent operates strictly within:
- **Install Directory:** `~/.local/share/mcp-offline-wikipedia` (or user-chosen path).
- **Client MCP Configs:**
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS), `~/.config/Claude/claude_desktop_config.json` (Linux, unofficial builds).
  - Cursor: `.cursor/mcp.json` (workspace) or `~/.cursor/mcp.json` (global).
  - Claude Code: `~/.claude.json` (written via `claude mcp add --scope user`).
- **Archive Directory:** Reads local Kiwix `.zim` files in the user's chosen folder (e.g. `~/kiwix-zim/`).

---

## Use Cases

1. **Air-Gapped & Offline Coding:** Research algorithms, math theorems, historical context, or libraries without an internet connection.
2. **Privacy-Preserving Fact Checking:** Consult large offline snapshots without leaking research topics or IP addresses to third-party search engines.
3. **Bandwidth-Constrained Environments:** Perform rapid local lookups while traveling, on planes, or in remote locations.

---

## Frequently Asked Questions (FAQ)

### Why pay $1 on Agensi when the MCP server is free on GitHub?
The server code is free and MIT licensed. This skill packages the automation: it handles system checks, dependency setup, safe JSON merging with timestamped backups, and coaches the model on optimal query patterns so you do not have to debug paths or JSON syntax manually.

### Will the install script overwrite my existing MCP tools?
No. The skill follows a strict merge-only contract. It first creates a timestamped backup of your config file, verifies existing JSON syntax, preserves all other servers, and adds only the `offline-wikipedia` entry.

### Why don't the tools show up immediately after installation?
MCP hosts (Claude Desktop, Cursor, etc.) only discover new tools when their background process starts. You must restart the client application once after installation completes.

### Where do I get Wikipedia `.zim` files, and how big are they?
You can download them for free from [https://library.kiwix.org](https://library.kiwix.org). We recommend starting with **Wikipedia English Mini (nopic)** (~2 GB), which contains ~897,000 top articles without images. The skill will guide you through this step if you do not have files yet.

### Why do I get "Error opening ZIM file" on macOS?
macOS sandbox restrictions block applications from accessing `~/Documents`, `~/Desktop`, or `~/Downloads`. Always keep your `.zim` files in a dedicated directory like `~/kiwix-zim/`.

### Does it work with LM Studio?
Yes, but manual setup is required. Plain LM Studio chat interfaces do not give agents shell/terminal execution capabilities, so the agent cannot run the install commands for you. The skill provides clear, step-by-step terminal instructions and the exact JSON snippet to paste into LM Studio's Developer → mcp.json settings.

### What does the skill access?
Network access is used exclusively during the initial installation to run `git clone` from GitHub and `pip install` from PyPI. During regular usage, the server operates 100% offline with zero network connectivity. The skill reads and writes to the installation directory (`~/.local/share/mcp-offline-wikipedia`), your chosen `.zim` directory, and your specific client configuration file (`claude_desktop_config.json`, `.cursor/mcp.json`, or `~/.claude.json`). It always creates a timestamped backup before modifying any config file.

---

## Real Demonstration Transcript

> Note: Paths in this transcript are anonymized as `/Users/<you>/...` for privacy; run used a throwaway config copy.

The following transcript was captured directly from an end-to-end clean-room run: cloning release tag `v1.1.2`, creating an isolated virtual environment, verifying against a real archive (`wikipedia_en_wp1-0.8_nopic_2026-04.zim`), merging into a throwaway config copy, and communicating directly with the installed server over MCP stdio:

### 1. Tag Clone & Environment Verification
```bash
$ git clone --branch v1.1.2 --depth 1 https://github.com/Rome-NotBeepBoop/mcp-offline-wikipedia.git /Users/<you>/.local/share/mcp-offline-wikipedia
Cloning into '/Users/<you>/.local/share/mcp-offline-wikipedia'...
HEAD is now at release v1.1.2

$ /Users/<you>/.local/share/mcp-offline-wikipedia/venv/bin/python -c "
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
" /Users/<you>/kiwix-zim
Archive loaded: wikipedia_en_wp1-0.8_nopic_2026-04.zim | 897,784 entries | Full-text: True
Verification SUCCESS!
```

### 2. Config Merge (Throwaway Config Copy)
```text
Backup created at: /Users/<you>/Library/Application Support/Claude/claude_desktop_config.json.bak.1793619572
Successfully merged offline-wikipedia into /Users/<you>/Library/Application Support/Claude/claude_desktop_config.json

Merged configuration:
{
  "mcpServers": {
    "git-server": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-git"
      ]
    },
    "offline-wikipedia": {
      "command": "/Users/<you>/.local/share/mcp-offline-wikipedia/venv/bin/python",
      "args": [
        "/Users/<you>/.local/share/mcp-offline-wikipedia/src/mcp-wiki-server.py"
      ],
      "env": {
        "WIKI_ZIM_DIR": "/Users/<you>/kiwix-zim",
        "WIKI_MAX_CHARS": "15000"
      }
    }
  },
  "preferences": {
    "theme": "dark"
  }
}
```

### 3. Server Responses Captured by Calling the Installed Server Directly Over MCP

**MCP Tool Call: `search_wikipedia("Turing machine", 3)`**
```text
Found 3 result(s) for 'Turing machine':

  1. Turing machine  [wikipedia_en_wp1-0.8_nopic_2026-04]
  2. Turing test  [wikipedia_en_wp1-0.8_nopic_2026-04]
  3. Church–Turing thesis  [wikipedia_en_wp1-0.8_nopic_2026-04]

Use get_article(title) with one of the titles above (without the [archive] label).
```

**MCP Tool Call: `get_article("Turing machine")`**
```text
=== Turing machine  [wikipedia_en_wp1-0.8_nopic_2026-04] ===

Turing machine
is a mathematical model of computation describing an abstract machine
that manipulates symbols on a strip of tape according to a table of rules.
Despite the model's simplicity, it is capable of implementing any
computer algorithm.

The machine operates on an infinite memory tape divided into discrete cells,
each of which can hold a single symbol drawn from a finite set of symbols
called the alphabet of the machine... (excerpt)
```
