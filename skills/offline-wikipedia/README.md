# Offline Wikipedia Agent Skill

An [Agent Skill](https://agentskills.io/) that enables AI agents to automatically install, configure, and search the open-source **Offline Wikipedia MCP Server**.

The underlying MCP server is open source (MIT licensed) and available on GitHub:
👉 [https://github.com/Rome-NotBeepBoop/mcp-offline-wikipedia](https://github.com/Rome-NotBeepBoop/mcp-offline-wikipedia)

---

## 🎯 What This Skill Does

1. **Automated Setup:** Clones the repository, creates a dedicated Python virtual environment, installs dependencies, and safely merges the MCP configuration into the user's client (Claude Desktop, Cursor, Claude Code).
2. **Retrieval Coaching:** Instructs the agent in the optimal two-step lookup workflow (`search_wikipedia` → clean title → `get_article`), keyword formulation, and context management across local Kiwix `.zim` archives.

---

## 📋 Requirements

- **Python 3.10+** and **git**
- **Shell access** for automated installation (chat-only clients like LM Studio can follow manual instructions provided in `SKILL.md`)
- One or more Kiwix `.zim` archives (e.g. from [https://library.kiwix.org](https://library.kiwix.org)) stored in an accessible directory (e.g. `~/kiwix-zim/`)

---

## 📦 Directory Structure

```text
offline-wikipedia/
├── SKILL.md                          # Self-contained main agent instructions
├── README.md                         # Skill overview and requirements
├── references/
│   ├── setup-and-config.md           # Reference client configurations
│   └── archive-guide.md              # Kiwix ZIM archive selection and sizing
└── scripts/
    └── verify_setup.py               # Pre-flight diagnostic verification script
```
