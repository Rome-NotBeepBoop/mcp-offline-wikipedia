import os
import sys
import logging
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from libzim.reader import Archive
from libzim.search import Query, Searcher
from libzim.suggestion import SuggestionSearcher

# Configure logging to write to stderr.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("offline-wiki-mcp")

# Initialize FastMCP Server
mcp = FastMCP("Offline Wikipedia")

# Read settings from environment variables with safe defaults
ZIM_PATH = os.environ.get("WIKI_ZIM_PATH")
MAX_ARTICLE_CHARS = int(os.environ.get("WIKI_MAX_CHARS", 15000))  # Customizable via env

# Thread-safe global reference
_archive = None


def get_archive() -> Archive:
    """Returns the globally loaded ZIM archive instance."""
    global _archive
    if _archive is None:
        validate_environment()
        logger.info(f"Loading ZIM archive into memory: {ZIM_PATH}")
        _archive = Archive(ZIM_PATH)
    return _archive


def validate_environment():
    """Validates environment setup immediately to catch configuration mistakes early."""
    if not ZIM_PATH:
        logger.error("WIKI_ZIM_PATH environment variable is completely missing.")
        raise ValueError(
            "WIKI_ZIM_PATH environment variable is missing. "
            "Please configure it in your MCP client settings file."
        )
    if not os.path.exists(ZIM_PATH):
        logger.error(f"ZIM archive file not found at path: {ZIM_PATH}")
        raise FileNotFoundError(f"ZIM archive file not found at: {ZIM_PATH}")


@mcp.tool()
def search_offline_wiki(query: str) -> str:
    """
    Search the offline Kiwix Wikipedia (.zim) archive for an article matching the query,
    extract its plain text content, and return it to provide up-to-date or contextual knowledge.

    Args:
        query: The exact search term or article topic to look up.
    """
    logger.info(f"Received search query: '{query}'")

    try:
        archive = get_archive()
        path = None

        # Strategy 1: Attempt Full-Text Index Search
        if archive.has_fulltext_index:
            try:
                searcher = Searcher(archive)
                search_query = Query().set_query(query)
                search_operation = searcher.search(search_query)

                if search_operation.getEstimatedMatches() > 0:
                    results = list(search_operation.getResults(0, 1))
                    if results:
                        path = results[0]
                        logger.info("Match found via full-text index.")
            except Exception as search_err:
                logger.warning(f"Full-text indexing error: {search_err}")

        # Strategy 2: Fallback to Title Suggestion Search (Prefix/binary search)
        if not path:
            try:
                suggestion_searcher = SuggestionSearcher(archive)
                suggestion_operation = suggestion_searcher.suggest(query)
                if suggestion_operation.getEstimatedMatches() > 0:
                    results = list(suggestion_operation.getResults(0, 1))
                    if results:
                        path = results[0]
                        logger.info("Match found via suggestion/title search.")
            except Exception as sug_err:
                logger.warning(f"Title suggestion search error: {sug_err}")

        if not path:
            logger.info(f"No match found for query: '{query}'")
            return f"No articles found matching the query: '{query}' in the offline archive."

        # Fetch the entry from the path pointer
        entry = archive.get_entry_by_path(path)

        # Follow redirects seamlessly
        if entry.is_redirect:
            entry = entry.get_redirect_entry()

        logger.info(f"Extracting content for article: {entry.title}")

        # Extract raw HTML content
        item = entry.get_item()
        html_content = bytes(item.content).decode("utf-8", errors="ignore")

        # Parse and clean up the HTML into readable plain text
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove noisy elements that bloat context windows or provide no text value
        for element in soup(["script", "style", "noscript", "header", "footer", "nav", "table", "sup", "img"]):
            element.decompose()

        raw_text = soup.get_text(separator="\n")

        # Normalize text
        lines = (line.strip() for line in raw_text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = "\n".join(chunk for chunk in chunks if chunk)

        if not clean_text.strip():
            logger.warning(f"Article '{entry.title}' returned empty text.")
            return f"Article '{entry.title}' was found, but contains no readable text content."

        # Truncate to prevent context window overflows
        if len(clean_text) > MAX_ARTICLE_CHARS:
            clean_text = clean_text[:MAX_ARTICLE_CHARS] + "\n\n...[Content truncated for length]..."

        logger.info("Successfully processed and returning article text.")
        return f"=== Wikipedia Archive Result: {entry.title} ===\n\n{clean_text}"

    except Exception as e:
        logger.error(f"Unhandled exception during tool execution: {str(e)}")
        return f"An error occurred while executing the lookup: {str(e)}"


if __name__ == "__main__":
    logger.info("Starting Offline Wikipedia MCP Server...")

    # Fail fast if environment is misconfigured before running the standard I/O loop
    try:
        validate_environment()
    except Exception as env_err:
        logger.critical(f"Initialization failure: {env_err}")
        sys.exit(1)

    mcp.run()