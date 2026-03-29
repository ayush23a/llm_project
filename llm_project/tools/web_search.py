"""Web search tools — Tavily (primary) and DuckDuckGo (fallback)."""

import os
from typing import Tuple, List
from dotenv import load_dotenv

load_dotenv()


def tavily_search(query: str, max_results: int = 5) -> Tuple[str, List[dict]]:
    """
    Search using Tavily API.
    Returns (formatted_results_string, list_of_source_dicts).
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "", []

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query + " Indian government scheme",
            max_results=max_results,
            search_depth="advanced",
        )

        results = response.get("results", [])
        if not results:
            return "", []

        formatted = []
        sources = []
        for r in results:
            formatted.append(f"**{r.get('title', 'N/A')}**\n{r.get('content', '')}\nSource: {r.get('url', '')}\n")
            sources.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "type": "tavily",
            })

        return "\n---\n".join(formatted), sources

    except Exception:
        return "", []


def duckduckgo_search(query: str, max_results: int = 5) -> Tuple[str, List[dict]]:
    """
    Fallback search using DuckDuckGo.
    Returns (formatted_results_string, list_of_source_dicts).
    """
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query + " Indian government scheme",
                max_results=max_results,
            ))

        if not results:
            return "", []

        formatted = []
        sources = []
        for r in results:
            formatted.append(f"**{r.get('title', 'N/A')}**\n{r.get('body', '')}\nSource: {r.get('href', '')}\n")
            sources.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "type": "duckduckgo",
            })

        return "\n---\n".join(formatted), sources

    except Exception:
        return "", []
