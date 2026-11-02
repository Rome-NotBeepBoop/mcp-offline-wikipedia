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
Developer Tools / Knowledge & Research

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
1. **Automated agent installation:** Ask your agent to set up the server. An agent with shell access (such as Claude Code or a terminal-enabled workspace) inspects prerequisites (Python 3.10+, git), clones the pinned release tag (`v1.1.1`), creates an isolated virtual environment, installs dependencies, and tests archive loading.
2. **Safe config merging:** Automatically backs up your client config (`config.json.bak.<timestamp>`) and merges the `offline-wikipedia` server entry into `mcpServers` without overwriting or disrupting any existing MCP tools.
3. **Structured retrieval coaching:** Unprepared LLMs frequently stumble with offline ZIM archives by asking conversational sentences ("what happened in 1789?"), passing unstripped archive tags (`get_article("Title [archive_label]")`), or guessing non-existent titles. This skill guides the agent through the two-step retrieval workflow, keyword formulation rules, title sanitization, and context window budgeting.

---

## Compatibility & Requirements

- **Role Separation:** The *installing agent* requires shell access (e.g. Claude Code or a Cursor terminal agent). The *target client* being configured can be any supported MCP environment on the same machine (Claude Desktop, Cursor, Claude Code).
- **Automated Install OS Support:** macOS and Linux. Windows users can follow the included manual setup steps.
- **Python & Git:** Python 3.10 or higher and Git installed on system PATH.
- **ZIM Archives:** Requires at least one Kiwix `.zim` archive (e.g. English Wikipedia Mini nopic, ~2 GB) stored on your local disk (e.g. in `~/kiwix-zim/`).
- **Chat-Only Clients (e.g. LM Studio):** Plain LM Studio chat does not offer terminal access. Complete manual terminal steps are provided for the user.
- **Post-Install Restart Notice:** MCP clients load newly configured servers on startup. After your agent finishes setup, restart your client and re-invoke the agent.

---

## File Scopes

During installation, the agent operates strictly within:
- **Install Directory:** `~/.local/share/mcp-offline-wikipedia` (or user-chosen path).
- **Client MCP Configs:** `~/Library/Application Support/Claude/claude_desktop_config.json`, `~/.config/Claude/claude_desktop_config.json`, or `.cursor/mcp.json`.
- **Archive Directory:** Reads local Kiwix `.zim` files in the user's chosen folder (e.g. `~/kiwix-zim/`).

---

## Use Cases

1. **Air-Gapped & Offline Coding:** Research algorithms, math theorems, historical context, or libraries without an internet connection.
2. **Privacy-Preserving Fact Checking:** Consult complete encyclopedic snapshots without leaking research topics or IP addresses to third-party search engines.
3. **Bandwidth-Constrained Environments:** Perform rapid local lookups while traveling, on planes, or in remote locations with zero network latency.

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

---

## Real Demonstration Transcript

The following transcript was captured directly from a live test run against a real Kiwix archive (`wikipedia_en_wp1-0.8_nopic_2026-04.zim`):

### Part 1: Automated Configuration Run
**Agent executes the inline merge script against the client config:**
```text
Backup created: ~/.config/Claude/claude_desktop_config.json.bak.1793618912
Updated config: ~/.config/Claude/claude_desktop_config.json
Config contents:
{
  "mcpServers": {
    "existing-server": {
      "command": "echo"
    },
    "offline-wikipedia": {
      "command": "~/.local/share/mcp-offline-wikipedia/venv/bin/python",
      "args": [
        "~/.local/share/mcp-offline-wikipedia/src/mcp-wiki-server.py"
      ],
      "env": {
        "WIKI_ZIM_DIR": "~/kiwix-zim",
        "WIKI_MAX_CHARS": "15000"
      }
    }
  }
}
```

**Pre-flight archive verification output:**
```text
Opened 'wikipedia_en_wp1-0.8_nopic_2026-04': 897,784 entries, full-text index: True
Archive loaded: wikipedia_en_wp1-0.8_nopic_2026-04 | Entries: 897,784 | Full-text: True
Verification SUCCESS!
```

*(User restarts the client application to load the newly registered MCP server)*

---

### Part 2: Post-Restart Research Lookup
**User:**
> "What is Alan Turing famous for according to offline Wikipedia?"

**Real Tool Call 1 — `search_wikipedia`:**
`search_wikipedia(query="Alan Turing", num_results=3)`

**Real Server Output:**
```text
Found 3 result(s) for 'Alan Turing':

  1. Alan Turing  [wikipedia_en_wp1-0.8_nopic_2026-04]
  2. Turing machine  [wikipedia_en_wp1-0.8_nopic_2026-04]
  3. Turing test  [wikipedia_en_wp1-0.8_nopic_2026-04]

Use get_article(title) with one of the titles above (without the [archive] label).
```

**Real Tool Call 2 — `get_article` (with clean title):**
`get_article(title="Alan Turing")`

**Real Server Output:**
```text
=== Alan Turing  [wikipedia_en_wp1-0.8_nopic_2026-04] ===

Alan Turing
OBE FRS
Turing in 1951
Born: Alan Mathison Turing (23 June 1912 – 7 June 1954)
Alma mater: University of Cambridge (MA), Princeton University (PhD)
Known for: Cryptanalysis of the Enigma, Turing machine, Turing test, Turing pattern...

Alan Mathison Turing was an English mathematician, computer scientist, logician, cryptanalyst, philosopher, and theoretical biologist. He was highly influential in the development of theoretical computer science, providing a formalisation of the concepts of algorithm and computation with the Turing machine...
```

**Synthesized Agent Response:**
> According to the offline Wikipedia snapshot (`wikipedia_en_wp1-0.8_nopic_2026-04`), **Alan Turing** (1912–1954) was an English mathematician, logician, and computer scientist widely regarded as the father of theoretical computer science and artificial intelligence.
> 
> His primary achievements include:
> 1. **The Turing Machine (1936):** A foundational mathematical model of computation formalizing algorithmic calculation.
> 2. **Codebreaking at Bletchley Park:** Playing a pivotal role in cracking German ciphers, including the Enigma machine, during World War II.
> 3. **The Turing Test (1950):** Introducing an operational benchmark for machine intelligence.
> 4. **Morphogenesis:** Pioneering mathematical biology with "The Chemical Basis of Morphogenesis".
