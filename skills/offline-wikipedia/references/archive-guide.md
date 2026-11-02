# Kiwix ZIM Archive Guide

This guide covers archive selection, download recommendations, and indexing behavior for the Offline Wikipedia MCP Server.

---

## 1. Where to Download Kiwix Archives

Kiwix archives are available freely under open content licenses:
- **Kiwix Library:** [https://library.kiwix.org/](https://library.kiwix.org/)
- Direct filter for English Wikipedia: `https://library.kiwix.org/?lang=eng&q=wikipedia`

---

## 2. Recommended Archives

Always prioritize **"nopic" (no pictures)** versions. LLMs process text; image data inflates download sizes significantly without providing value to text-based models.

| Archive | Size & Entries | Description & Use Case |
|---|---|---|
| **Wikipedia English (wp1 / Mini, nopic)** | **~2 GB**<br>*(Verified: 897,784 entries)* | **Recommended default.** Curated selection of high-importance articles. Fast, compact, and covers major historical, scientific, and biographical topics. |
| **Wikipedia English (Maxi, nopic)** | Varies by dump (~20–30+ GB) | Full English Wikipedia without images. Complete coverage including obscure topics and small entities. |
| **Wiktionary (nopic)** | Varies by language/dump | Dictionary entries, definitions, etymologies, and pronunciations. |
| **Other Kiwix Archives** (Stack Overflow, MDN, Gutenberg) | Varies by dump | Specialized knowledge bases. Any `.zim` archive can be loaded by the server. |

*Note: Archive file sizes and entry counts change with each periodic Kiwix scrape release. Check [library.kiwix.org](https://library.kiwix.org/) for current release sizes.*

---

## 3. Storage & Multi-Archive Organization

The server loads every `.zim` file found in `WIKI_ZIM_DIR`. You can place multiple knowledge bases into one directory:

```text
~/kiwix-zim/
├── wikipedia_en_wp1-0.8_nopic_2026-04.zim
└── other_archive_nopic.zim
```

When querying:
- `search_wikipedia` scans across all loaded archives and tags results with their source filename (e.g. `[wikipedia_en_wp1-0.8_nopic_2026-04]`).
- `get_article` searches across archives in order until the first matching article is found.

---

## 4. Indexing & Search Strategies

Kiwix `.zim` files utilize two search mechanisms:
1. **Full-Text Index (Xapian):** Ranks articles by semantic relevance and keyword density inside the body text.
2. **Title Suggestion Index (Prefix Match):** High-speed prefix lookup on exact article titles.

The MCP server leverages both:
- If a full-text index is present, it retrieves ranked results first, then tops up remaining slots with title prefix suggestions.
- If an archive lacks a full-text index, the server smoothly falls back to title suggestions without throwing errors.
