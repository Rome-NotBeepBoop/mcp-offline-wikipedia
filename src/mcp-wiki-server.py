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

import sys, importlib.metadata
logger.info(f"Python executable: {sys.executable}")
logger.info(f"libzim version: {importlib.metadata.version('libzim')}")

mcp = FastMCP("Offline Wikipedia")

# Path to the .zim archive file (required)
ZIM_PATH = os.environ.get("WIKI_ZIM_PATH")

# Truncate articles to protect LLM context windows.
# Override with the WIKI_MAX_CHARS environment variable if needed.
MAX_ARTICLE_CHARS = int(os.environ.get("WIKI_MAX_CHARS", 15000))

# Thread-safe singleton — the archive is opened once and reused across all calls.
_archive: Archive | None = None
_archive_lock = threading.Lock()


def get_archive() -> Archive:
    """
    Lazily opens and returns the ZIM archive (thread-safe, double-checked locking).
    Logs archive metadata on first open to aid debugging.
    """
    global _archive
    if _archive is None:
        with _archive_lock:
            if _archive is None:
                if not ZIM_PATH:
                    logger.error("WIKI_ZIM_PATH environment variable is not set.")
                    raise ValueError(
                        "WIKI_ZIM_PATH is not set. "
                        "Add it to the 'env' block in your MCP client config."
                    )
                if not os.path.exists(ZIM_PATH):
                    logger.error(f"ZIM archive not found at: {ZIM_PATH}")
                    raise FileNotFoundError(f"ZIM archive not found at: {ZIM_PATH}")

                logger.info(f"Opening ZIM archive: {ZIM_PATH}")
                _archive = Archive(ZIM_PATH)
                logger.info(
                    f"Archive ready — {_archive.entry_count:,} entries, "
                    f"full-text index: {_archive.has_fulltext_index}"
                )
    return _archive


def _sanitize_query(query: str) -> str:
    """
    Light cleanup before passing a query to libzim.
    Strips whitespace and hard-truncates excessively long strings.
    """
    query = query.strip()
    if len(query) > 120:
        logger.warning(f"Query truncated from {len(query)} to 120 characters.")
        query = query[:120]
    return query


def _extract_text(html_content: str) -> str:
    """Parse HTML from a ZIM entry and return clean plain text."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove elements that add noise without useful content
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "sup", "img"]):
        tag.decompose()

    raw_text = soup.get_text(separator="\n", strip=True)

    # Drop blank lines and stray single-character lines (nav artefacts, stray punctuation)
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
    Search the offline Wikipedia archive and return a list of matching article titles.

    Always call this first to discover article titles, then use get_article() to read
    the full content of the one you want. This two-step flow avoids filling your
    context window unnecessarily.

    IMPORTANT — query format:
      Queries must be specific topic keywords or proper nouns, like a Wikipedia article title.
      Do NOT use questions, sentences, or vague descriptive phrases.

      GOOD: "black hole", "octopus", "French Revolution", "Marie Curie", "photosynthesis"
      BAD:  "tell me facts", "interesting animals", "what is a black hole?", "things in space"

    Args:
        query: A specific topic name or keyword (e.g. "black hole", "Python language").
        num_results: Number of results to return (default 5, max 10).
    """
    query = _sanitize_query(query)
    logger.info(f"search_wikipedia: '{query}', num_results={num_results}")
    num_results = max(1, min(num_results, 10))

    try:
        archive = get_archive()
        seen: set[str] = set()
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
                            if entry.title not in seen:
                                seen.add(entry.title)
                                found_titles.append(entry.title)
                        except Exception:
                            continue
                    logger.info(f"Full-text search: {len(found_titles)} result(s).")
            except Exception as e:
                logger.warning(f"Full-text search error: {e}")

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
                            if entry.title not in seen:
                                seen.add(entry.title)
                                found_titles.append(entry.title)
                        except Exception:
                            continue
                    logger.info(f"Suggestion search topped up to {len(found_titles)} result(s).")
            except Exception as e:
                logger.warning(f"Suggestion search error: {e}")

        if not found_titles:
            return (
                f"No articles found for '{query}'. "
                "Try a shorter or more specific keyword — ideally a proper noun or subject name."
            )

        lines = [f"Found {len(found_titles)} result(s) for '{query}':\n"]
        for i, title in enumerate(found_titles, 1):
            lines.append(f"  {i}. {title}")
        lines.append("\nUse get_article(title) with one of the titles above to read the full article.")
        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Unhandled error in search_wikipedia: {e}")
        return f"Search failed: {e}"


@mcp.tool()
def get_article(title: str) -> str:
    """
    Retrieve the full text of a Wikipedia article by title.

    If you are unsure of the exact title, call search_wikipedia() first to find it.
    Note: this is an offline snapshot and may not reflect the very latest Wikipedia edits.

    Args:
        title: The Wikipedia article title to fetch (e.g. "Black hole", "Rome",
               "Python (programming language)").
    """
    logger.info(f"get_article: '{title}'")

    try:
        archive = get_archive()
        path = None

        # Strategy 1: title suggestion search (best for exact/near-exact title lookup)
        try:
            suggestion_op = SuggestionSearcher(archive).suggest(title)
            if suggestion_op.getEstimatedMatches() > 0:
                results = list(suggestion_op.getResults(0, 1))
                if results:
                    path = results[0]
                    logger.info("Article path resolved via suggestion search.")
        except Exception as e:
            logger.warning(f"Suggestion search error in get_article: {e}")

        # Strategy 2: full-text search fallback
        if not path and archive.has_fulltext_index:
            try:
                search_op = Searcher(archive).search(Query().set_query(title))
                if search_op.getEstimatedMatches() > 0:
                    results = list(search_op.getResults(0, 1))
                    if results:
                        path = results[0]
                        logger.info("Article path resolved via full-text search fallback.")
            except Exception as e:
                logger.warning(f"Full-text search error in get_article: {e}")

        if not path:
            return (
                f"Article '{title}' was not found in the offline archive. "
                f"Try search_wikipedia('{title}') to find a close match."
            )

        article_title, clean_text = _resolve_entry(archive, path)

        if not clean_text.strip():
            return f"Article '{article_title}' was found but contains no readable text."

        if len(clean_text) > MAX_ARTICLE_CHARS:
            clean_text = (
                clean_text[:MAX_ARTICLE_CHARS]
                + "\n\n...[Article truncated. Set the WIKI_MAX_CHARS env var to raise the limit.]"
            )

        logger.info(f"Returning '{article_title}' ({len(clean_text):,} chars).")
        return f"=== Wikipedia: {article_title} ===\n\n{clean_text}"

    except Exception as e:
        logger.error(f"Unhandled error in get_article: {e}")
        return f"Failed to retrieve article: {e}"


if __name__ == "__main__":
    logger.info("Starting Offline Wikipedia MCP Server...")
    # Communicates via stdio (stdin/stdout) as required by the MCP protocol
    mcp.run()