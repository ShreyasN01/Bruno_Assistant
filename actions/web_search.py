"""
Bruno Assistant - Web Search

Handles opening web searches and URLs in the default browser.
"""

import urllib.parse
import webbrowser


def search_web(query: str) -> str:
    """Open a Google search in the default browser.

    Args:
        query: The search query string.

    Returns:
        A string describing the result of the operation.
    """
    try:
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        webbrowser.open(url)
        return f"Searching the web for: {query}"
    except Exception as e:
        return f"Error performing web search: {str(e)}"


def open_url(url: str) -> str:
    """Open a specific URL in the default browser.

    Automatically prepends https:// if no scheme is provided.

    Args:
        url: The URL to open.

    Returns:
        A string describing the result of the operation.
    """
    try:
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        webbrowser.open(url)
        return f"Opened {url} in your browser."
    except Exception as e:
        return f"Error opening URL: {str(e)}"
