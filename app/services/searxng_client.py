"""SearXNG async client — primary search engine."""

import os
import logging
import httpx
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SEARXNG_BASE_URL = os.getenv("SEARXNG_BASE_URL", "http://localhost:8888")
REQUEST_TIMEOUT = 15


async def search(query: str, num_results: int = 10) -> List[Dict]:
    """
    Fetch search results from SearXNG.

    Returns a list of dicts: [{title, snippet, url}, ...]
    Returns empty list on any error.
    """
    params = {
        "q": query,
        "format": "json",
        "language": "en",
        "pageno": 1,
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            resp = await client.get(f"{SEARXNG_BASE_URL}/search", params=params)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("results", [])[:num_results]:
            results.append({
                "title":   item.get("title", ""),
                "snippet": item.get("content", ""),
                "url":     item.get("url", ""),
            })
        return results

    except Exception as exc:
        logger.warning(f"SearXNG error for query '{query}': {exc}")
        return []
