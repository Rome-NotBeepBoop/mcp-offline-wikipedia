import os
import sys
import logging
import threading
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from libzim.reader import Archive
from libzim.search import Query, Searcher
from libzim.suggestion import SuggestionSearcher

# WARNING: MCP uses stdout for JSON-RPC protocol communication.
# Never print or log to stdout — always use stderr.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("offline-wiki-mcp")

import importlib.metadata
logger.info(f"Python executable: {sys.executable}")
logger.info(f"libzim version: {importlib.metadata.version('libzim')}")

mcp = FastMCP("Offline Wikipedia")

# --- Archive source configuration ---
# Preferred: point WIKI_ZIM_DIR at a folder — every .zim file inside will be loaded.
# Legacy:    point WIKI_ZIM_PATH at a single .zim file (still supported).
WIKI_ZIM_DIR  = os.environ.get("WIKI_ZIM_DIR")
WIKI_ZIM_PATH = os.environ.get("WIKI_ZIM_PATH")  # single-file fallback

# Truncate articles to protect LLM context windows.
# Override with the WIKI_MAX_CHARS environment variable if needed.
MAX_ARTICLE_CHARS = int(os.environ.get("WIKI_MAX_CHARS", 15000))

# Thread-safe lazy-loaded archive list: list of (label, Archive) tuples.
_archives: list[tuple[str, Archive]] = []
_archives_lock = threading.Lock()
_archives_loaded = False


def get_archives() -> list[tuple[str, Archive]]:
    """
    Lazily opens all ZIM archives (thread-safe, double-checked locking).

    Resolution order:
      1. WIKI_ZIM_DIR  — scans the directory and opens every .zim file found.
      2. WIKI_ZIM_PATH — opens a single .zim file (legacy / single-file mode).

    Returns a list of (label, Archive) tuples where label is the filename
    without extension, used to identify the source in search results.
    """
    global _archives, _archives_loaded
    if not _archives_loaded:
        with _archives_lock:
            if not _archives_loaded:
                paths: list[str] = []

                if WIKI_ZIM_DIR:
                    if not os.path.isdir(WIKI_ZIM_DIR):
                        raise NotADirectoryError(
                            f"WIKI_ZIM_DIR is not a directory: {WIKI_ZIM_DIR}"
                        )
                    paths = sorted([
                        os.path.join(WIKI_ZIM_DIR, f)
                        for f in os.listdir(WIKI_ZIM_DIR)
                        if f.endswith(".zim")
                    ])
                    if not paths:
                        raise FileNotFoundError(
                            f"No .zim files found in: {WIKI_ZIM_DIR}"
                        )
                    logger.info(f"Found {len(paths)} .zim file(s) in {WIKI_ZIM_DIR}")

                elif WIKI_ZIM_PATH:
                    if not os.path.exists(WIKI_ZIM_PATH):
                        raise FileNotFoundError(
                            f"ZIM archive not found at: {WIKI_ZIM_PATH}"
                        )
                    paths = [WIKI_ZIM_PATH]

                else:
                    raise ValueError(
                        "Neither WIKI_ZIM_DIR nor WIKI_ZIM_PATH is set. "
                        "Add one to the 'env' block in your MCP client config."
                    )

                for path in paths:
                    try:
                        archive = Archive(path)
                        label = os.path.splitext(os.path.basename(path))[0]
                        _archives.append((label, archive))
                        logger.info(
                            f"Opened '{label}': {archive.entry_count:,} entries, "
                            f"full-text index: {archive.has_fulltext_index}"
                        )
                    except Exception as e:
                        logger.error(f"Failed to open '{path}': {e}")

                if not _archives:
                    raise RuntimeError(
                        "No ZIM archives could be opened. "
                        "Check the paths and that libzim>=3.10.0 is installed."
                    )

                _archives_loaded = True
    return _archives


def _sanitize_query(query: str) -> str:
    """Light cleanup before passing a query to libzim."""
    query = query.strip()
    if len(query) > 120:
        logger.warning(f"Query truncated from {len(query)} to 120 characters.")
        query = query[:120]
    return query


def _extract_text(html_content: str) -> str:
    """Parse HTML from a ZIM entry and return clean plain text."""
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "sup", "img"]):
        tag.decompose()
    raw_text = soup.get_text(separator="\n", strip=True)
    lines = [line for line in raw_text.splitlines() if len(line.strip()) > 2]
    return "\n".join(lines)


def _resolve_entry(archive: Archive, path: str) -> tuple[str, str]:
    """Follow any redirects for a ZIM path and return (title, plain_text)."""
    entry = archive.get_entry_by_path(path)
    if entry.is_redirect:
        entry = entry.get_redirect_entry()
    item = entry.get_item()
    html_content = bytes(item.content).decode("utf-8", errors="ignore")
    return entry.title, _extract_text(html_content)


@mcp.tool()
def search_wikipedia(query: str, num_results: int = 5) -> str:
    """
    Search all loaded offline Kiwix archives and return matching article titles.

    Always call this first to discover article titles, then use get_article() to read
    the full content of the one you want. This two-step flow avoids filling your
    context window unnecessarily.

    Results show which archive each article came from in square brackets, e.g.:
      "Black hole  [wikipedia_en_wp1-0.8_nopic_2026-04]"

    IMPORTANT — query format:
      Queries must be specific topic keywords or proper nouns, like a Wikipedia article title.
      Do NOT use questions, sentences, or vague descriptive phrases.

      GOOD: "black hole", "octopus", "French Revolution", "Marie Curie", "photosynthesis"
      BAD:  "tell me facts", "interesting animals", "what is a black hole?", "things in space"

    Args:
        query: A specific topic name or keyword (e.g. "black hole", "Python language").
        num_results: Number of results to return per archive (default 5, max 10).
    """
    query = _sanitize_query(query)
    logger.info(f"search_wikipedia: '{query}', num_results={num_results}")
    num_results = max(1, min(num_results, 10))

    try:
        archives = get_archives()
        all_results: list[str] = []
        seen: set[str] = set()

        for label, archive in archives:
            found_titles: list[str] = []

            # Strategy 1: full-text index search (best relevance ranking)
            if archive.has_fulltext_index:
                try:
                    search_op = Searcher(archive).search(Query().set_query(query))
                    if search_op.getEstimatedMatches() > 0:
                        for path in search_op.getResults(0, num_results):
                            try:
                                entry = archive.get_entry_by_path(path)
                                if entry.is_redirect:
                                    entry = entry.get_redirect_entry()
                                key = entry.title.lower()
                                if key not in seen:
                                    seen.add(key)
                                    found_titles.append(entry.title)
                            except Exception:
                                continue
                        logger.info(f"[{label}] Full-text: {len(found_titles)} result(s).")
                except Exception as e:
                    logger.warning(f"[{label}] Full-text search error: {e}")

            # Strategy 2: title suggestion search (prefix-based, fills remaining slots)
            remaining = num_results - len(found_titles)
            if remaining > 0:
                try:
                    suggestion_op = SuggestionSearcher(archive).suggest(query)
                    if suggestion_op.getEstimatedMatches() > 0:
                        for path in suggestion_op.getResults(0, remaining):
                            try:
                                entry = archive.get_entry_by_path(path)
                                if entry.is_redirect:
                                    entry = entry.get_redirect_entry()
                                key = entry.title.lower()
                                if key not in seen:
                                    seen.add(key)
                                    found_titles.append(entry.title)
                            except Exception:
                                continue
                        logger.info(f"[{label}] Suggestions topped up to {len(found_titles)} result(s).")
                except Exception as e:
                    logger.warning(f"[{label}] Suggestion search error: {e}")

            for title in found_titles:
                all_results.append(f"{title}  [{label}]")

        if not all_results:
            return (
                f"No articles found for '{query}'. "
                "Try a shorter or more specific keyword — ideally a proper noun or subject name."
            )

        lines = [f"Found {len(all_results)} result(s) for '{query}':\n"]
        for i, entry in enumerate(all_results, 1):
            lines.append(f"  {i}. {entry}")
        lines.append(
            "\nUse get_article(title) with one of the titles above "
            "(without the [archive] label)."
        )
        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Unhandled error in search_wikipedia: {e}")
        return f"Search failed: {e}"


@mcp.tool()
def get_article(title: str) -> str:
    """
    Retrieve the full text of an article by title, searching across all loaded archives.

    The first archive that contains a matching article wins. If you are unsure of the
    exact title, call search_wikipedia() first to find it.
    Note: this is an offline snapshot and may not reflect the very latest edits.

    Args:
        title: The article title to fetch (e.g. "Black hole", "Rome",
               "Python (programming language)").
    """
    logger.info(f"get_article: '{title}'")

    try:
        archives = get_archives()

        for label, archive in archives:
            path = None

            # Strategy 1: title suggestion search (best for exact/near-exact title lookup)
            try:
                suggestion_op = SuggestionSearcher(archive).suggest(title)
                if suggestion_op.getEstimatedMatches() > 0:
                    results = list(suggestion_op.getResults(0, 1))
                    if results:
                        path = results[0]
                        logger.info(f"[{label}] Path resolved via suggestion search.")
            except Exception as e:
                logger.warning(f"[{label}] Suggestion search error in get_article: {e}")

            # Strategy 2: full-text search fallback
            if not path and archive.has_fulltext_index:
                try:
                    search_op = Searcher(archive).search(Query().set_query(title))
                    if search_op.getEstimatedMatches() > 0:
                        results = list(search_op.getResults(0, 1))
                        if results:
                            path = results[0]
                            logger.info(f"[{label}] Path resolved via full-text fallback.")
                except Exception as e:
                    logger.warning(f"[{label}] Full-text search error in get_article: {e}")

            if not path:
                continue  # not in this archive, try the next one

            article_title, clean_text = _resolve_entry(archive, path)

            if not clean_text.strip():
                continue  # empty article, try next archive

            if len(clean_text) > MAX_ARTICLE_CHARS:
                clean_text = (
                    clean_text[:MAX_ARTICLE_CHARS]
                    + "\n\n...[Article truncated. Set the WIKI_MAX_CHARS env var to raise the limit.]"
                )

            logger.info(f"Returning '{article_title}' from [{label}] ({len(clean_text):,} chars).")
            return f"=== {article_title}  [{label}] ===\n\n{clean_text}"

        return (
            f"Article '{title}' was not found in any loaded archive. "
            f"Try search_wikipedia('{title}') to find a close match."
        )

    except Exception as e:
        logger.error(f"Unhandled error in get_article: {e}")
        return f"Failed to retrieve article: {e}"


if __name__ == "__main__":
    logger.info("Starting Offline Wikipedia MCP Server...")
    mcp.run()