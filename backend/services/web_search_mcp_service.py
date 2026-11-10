"""Optional Brave Search MCP client for the Tribal AI Chatbot.

Starts the configured MCP server over stdio for each search. Search failures are
non-fatal: ChatService continues with its existing RAG/LLM path.
"""
from __future__ import annotations

import html
import json
import os
import re
from urllib.parse import urlparse
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from backend.config.logger import logger
from backend.config.settings import settings


def _collect_result_items(value: Any) -> list[dict[str, str]]:
    """Normalize common MCP/Brave result shapes into title/url/snippet records."""
    items: list[dict[str, str]] = []

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            title = node.get("title") or node.get("name")
            url = node.get("url") or node.get("link")
            snippet = node.get("description") or node.get("snippet") or node.get("content")
            if isinstance(url, str) and url.startswith(("https://", "http://")):
                items.append({
                    "title": str(title or url).strip(),
                    "url": url.strip(),
                    "snippet": str(snippet or "").strip(),
                })
            for key, child in node.items():
                if key not in {"title", "name", "url", "link", "description", "snippet", "content"}:
                    visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    deduped: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        if item["url"] not in seen:
            seen.add(item["url"])
            deduped.append(item)
    return deduped



_NEWS_TERMS = (
    "news", "headline", "headlines", "breaking", "current affairs",
    "latest update", "latest updates", "today's", "today", "this morning",
)


def _is_news_query(query: str) -> bool:
    normalized = query.casefold()
    return any(term in normalized for term in _NEWS_TERMS)


def _prepare_search_query(query: str) -> str:
    """Nudge broad current-news questions toward individual story pages."""
    if not _is_news_query(query):
        return query.strip()

    normalized = query.casefold()
    if any(term in normalized for term in ("india", "indian")):
        region = "India"
    else:
        region = ""

    # Keep the user's intent and add article-oriented terms. Avoid hard-coded
    # publisher restrictions so Brave can find relevant sources broadly.
    core = query.strip().rstrip("?!.")
    return f"{core} {region} latest news reports individual articles headlines".strip()


def _article_score(item: dict[str, str]) -> int:
    """Rank article-like URLs above publisher section/home pages."""
    parsed = urlparse(item.get("url", ""))
    path = parsed.path.strip("/")
    title = item.get("title", "").casefold()
    snippet = item.get("snippet", "").casefold()
    score = 0

    if path:
        segments = [segment for segment in path.split("/") if segment]
        score += min(len(segments), 5) * 3
        if len(segments) >= 3:
            score += 5
        if re.search(r"/(live|article|articles|news|story|stories|[0-9]{4})", "/" + path, re.I):
            score += 3
    else:
        score -= 12

    if any(word in title for word in ("latest news", "news home", "top headlines", "india news")):
        score -= 8
    if len(title.split()) >= 7 and not any(word in title for word in ("latest news", "top headlines")):
        score += 3
    if len(snippet) > 100:
        score += 2
    if "..." in snippet or "..." in title:
        score -= 1
    return score


class WebSearchMCPService:
    def __init__(self) -> None:
        self.enabled = bool(settings.WEB_SEARCH_ENABLED and settings.BRAVE_SEARCH_API_KEY.strip())

    def _server_params(self) -> StdioServerParameters:
        command = settings.WEB_SEARCH_MCP_COMMAND.strip() or "npx"
        try:
            args = json.loads(settings.WEB_SEARCH_MCP_ARGS)
        except (TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError("WEB_SEARCH_MCP_ARGS must be a JSON array.") from exc
        if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
            raise RuntimeError("WEB_SEARCH_MCP_ARGS must be a JSON array of strings.")
        env = os.environ.copy()
        env["BRAVE_API_KEY"] = settings.BRAVE_SEARCH_API_KEY.strip()
        return StdioServerParameters(command=command, args=args, env=env)

    async def search(self, query: str, limit: int | None = None) -> tuple[str, list[str]]:
        """Return bounded web context and source labels; empty values on failure."""
        if not self.enabled or not query.strip():
            return "", []
        limit = max(1, min(int(limit or settings.WEB_SEARCH_MAX_RESULTS), 10))
        search_query = _prepare_search_query(query)
        try:
            async with stdio_client(self._server_params()) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_result = await session.list_tools()
                    search_tool = next(
                        (tool for tool in tools_result.tools if tool.name == "brave_web_search"),
                        None,
                    )
                    if search_tool is None:
                        logger.warning("Brave Search MCP server did not expose brave_web_search.")
                        return "", []
                    schema = getattr(search_tool, "inputSchema", {}) or {}
                    properties = schema.get("properties", {}) if isinstance(schema, dict) else {}
                    arguments: dict[str, Any] = {"query": search_query}
                    if "count" in properties:
                        arguments["count"] = max(1, min(int(limit), 10))
                    elif "limit" in properties:
                        arguments["limit"] = max(1, min(int(limit), 10))
                    result = await session.call_tool(search_tool.name, arguments)
                    structured = getattr(result, "structuredContent", None)

                    text_blocks = [
                        block.text
                        for block in (getattr(result, "content", []) or [])
                        if getattr(block, "type", None) == "text"
                        and isinstance(getattr(block, "text", None), str)
                    ]
                    parsed_items: list[dict[str, str]] = []
                    if structured is not None:
                        parsed_items.extend(_collect_result_items(structured))

                    if not parsed_items:
                        for block_text in text_blocks:
                            try:
                                block_data = json.loads(block_text)
                            except (json.JSONDecodeError, TypeError):
                                continue
                            parsed_items.extend(_collect_result_items(block_data))

                    # Deduplicate URLs and normalize encoded HTML in snippets.
                    records: list[dict[str, str]] = []
                    seen_urls: set[str] = set()
                    for item in parsed_items:
                        url = item.get("url", "").strip()
                        if not url or url in seen_urls:
                            continue
                        seen_urls.add(url)
                        item["title"] = html.unescape(item.get("title", "")).strip()
                        item["snippet"] = html.unescape(item.get("snippet", "")).strip()
                        records.append(item)

                    if records:
                        if _is_news_query(query):
                            records.sort(key=_article_score, reverse=True)
                        records = records[:limit]
                        context_lines: list[str] = []
                        sources: list[str] = []

                        for index, item in enumerate(records, start=1):
                            title = item["title"] or item["url"]
                            url = item["url"]
                            snippet = re.sub(r"\s+", " ", item.get("snippet", "")).strip()
                            context_lines.append(
                                f"[{index}] {title}\n"
                                f"URL: {url}\n"
                                f"Snippet: {snippet or 'No snippet provided.'}"
                            )
                            sources.append(f"Web: {title} — {url}")

                        logger.info(
                            "Brave results parsed | count=%s | news_query=%s | query=%r",
                            len(records),
                            _is_news_query(query),
                            search_query,
                        )
                        return "\n\n".join(context_lines), sources

                    logger.warning(
                        "Brave MCP returned no parseable search records. Text blocks: %s",
                        len(text_blocks),
                    )
                    fallback = "\n".join(text_blocks).strip()
                    if fallback:
                        return fallback[:6000], []
                    return "", []
        except Exception:
            logger.exception("Web Search MCP request failed; continuing without web context.")
            return "", []


web_search_mcp_service = WebSearchMCPService()
