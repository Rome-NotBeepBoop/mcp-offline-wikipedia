import os
import sys
import logging
import threading
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from libzim.reader import Archive
from libzim.search import Query, Searcher
from libzim.suggestion import SuggestionSearcher

# Configure logging to write to stderr.
# WARNING: MCP uses stdout for JSON-RPC protocol communication. Never print or log to stdout.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("offline-wiki-mcp")

# Initialize FastMCP Server
mcp = FastMCP("Offline Wikipedia")

# Read the .zim file path from environment variables
ZIM_PATH = os.environ.get("WIKI_ZIM_PATH")

# Protect LLM context windows by truncating excessively long articles.
# Override with WIKI_MAX_CHARS environment variable if needed.
MAX_ARTICLE_CHARS = int(os.environ.get("WIKI_MAX_CHARS", 15000))

# Thread-safe global reference to avoid re-opening the archive on every tool call
_archive: Archive | None = None
_archive_lock = threading.Lock()


def get_archive() -> Archive:
    """
    Lazily opens and returns the ZIM archive (thread-safe).
    Uses double-checked locking so concurrent calls don't race to initialize.
    """
    global _archive
    if _archive is None:
        with _archive_lock:
            # Re-check inside the lock in case another thread already initialized it
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
    return _archive


def _extract_text(html_content: str) -> str:
    """Parse HTML from a ZIM entry and return clean plain text."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove elements that add noise without useful text
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "sup", "img"]):
        tag.decompose()

    # strip=True handles leading/trailing whitespace per element
    raw_text = soup.get_text(separator="\n", strip=True)

    # Drop blank lines
    lines = [line for line in raw_text.splitlines() if line.strip()]
    return "\n".join(lines)


def _resolve_entry(archive: Archive, path: str) -> tuple[str, str]:
    """
    Given a ZIM path, follow any redirects and return (title, clean_text).
    """
    entry = archive.get_entry_by_path(path)
    if entry.is_redirect:
        entry = entry.get_redirect_entry()

    item = entry.get_item()
    html_content = bytes(item.content).decode("utf-8", errors="ignore")
    return entry.title, _extract_text(html_content)


@mcp.tool()
def search_wikipedia(query: str, num_results: int = 5) -> str:
    """
    Search the offline Kiwix Wikipedia archive and return a list of matching article titles.

    Call this first to find relevant articles, then use get_article() with a title to read
    the full content. This two-step approach avoids flooding your context window unnecessarily.

    Args:
        query: The topic or search term to look up (e.g. "black hole", "Python language").
        num_results: How many results to return. Default is 5, maximum is 10.
    """
    logger.info(f"search_wikipedia: '{query}', num_results={num_results}")
    num_results = max(1, min(num_results, 10))  # clamp to valid range

    try:
        archive = get_archive()
        found_titles: list[str] = []

        # Strategy 1: Full-text index search (most relevant results)
        if archive.has_fulltext_index:
            try:
                searcher = Searcher(archive)
                search_op = searcher.search(Query().set_query(query))
                if search_op.getEstimatedMatches() > 0:
                    for path in search_op.getResults(0, num_results):
                        try:
                            entry = archive.get_entry_by_path(path)
                            if entry.is_redirect:
                                entry = entry.get_redirect_entry()
                            found_titles.append(entry.title)
                        except Exception:
                            continue
                    logger.info(f"Full-text search: {len(found_titles)} result(s).")
            except Exception as e:
                logger.warning(f"Full-text search error: {e}")

        # Strategy 2: Title suggestion search (prefix/binary search fallback or supplement)
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
                            if entry.title not in found_titles:
                                found_titles.append(entry.title)
                        except Exception:
                            continue
                    logger.info(f"Suggestion search topped up results to {len(found_titles)}.")
            except Exception as e:
                logger.warning(f"Suggestion search error: {e}")

        if not found_titles:
            return f"No articles found for '{query}' in the offline archive."

        lines = [f"Found {len(found_titles)} result(s) for '{query}':\n"]
        for i, title in enumerate(found_titles, 1):
            lines.append(f"  {i}. {title}")
        lines.append("\nCall get_article(title) with any of the above titles to read the full article.")
        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Unhandled error in search_wikipedia: {e}")
        return f"An error occurred during search: {e}"


@mcp.tool()
def get_article(title: str) -> str:
    """
    Retrieve the full encyclopedic text of a specific Wikipedia article by title.

    If you are unsure of the exact title, call search_wikipedia() first to find it.
    Note: this is an offline archive and may not reflect the very latest Wikipedia edits.

    Args:
        title: The Wikipedia article title to fetch (e.g. "Black hole", "Rome").
    """
    logger.info(f"get_article: '{title}'")

    try:
        archive = get_archive()
        path = None

        # Strategy 1: Title suggestion search (best for exact/near-exact title lookup)
        try:
            suggestion_op = SuggestionSearcher(archive).suggest(title)
            if suggestion_op.getEstimatedMatches() > 0:
                results = list(suggestion_op.getResults(0, 1))
                if results:
                    path = results[0]
                    logger.info("Article path found via suggestion search.")
        except Exception as e:
            logger.warning(f"Suggestion search error in get_article: {e}")

        # Strategy 2: Full-text search fallback
        if not path and archive.has_fulltext_index:
            try:
                search_op = Searcher(archive).search(Query().set_query(title))
                if search_op.getEstimatedMatches() > 0:
                    results = list(search_op.getResults(0, 1))
                    if results:
                        path = results[0]
                        logger.info("Article path found via full-text search fallback.")
            except Exception as e:
                logger.warning(f"Full-text search error in get_article: {e}")

        if not path:
            return (
                f"Article '{title}' was not found in the offline archive. "
                f"Try search_wikipedia('{title}') to find similar titles."
            )

        article_title, clean_text = _resolve_entry(archive, path)

        if not clean_text.strip():
            return f"Article '{article_title}' was found but contains no readable text."

        if len(clean_text) > MAX_ARTICLE_CHARS:
            clean_text = (
                clean_text[:MAX_ARTICLE_CHARS]
                + "\n\n...[Content truncated. Set WIKI_MAX_CHARS env var to increase the limit.]"
            )

        logger.info(f"Returning '{article_title}' ({len(clean_text)} chars).")
        return f"=== Wikipedia: {article_title} ===\n\n{clean_text}"

    except Exception as e:
        logger.error(f"Unhandled error in get_article: {e}")
        return f"An error occurred retrieving the article: {e}"


if __name__ == "__main__":
    logger.info("Starting Offline Wikipedia MCP Server...")
    # Communicates via stdio (stdin/stdout), as required by the MCP protocol
    mcp.run()