
import logging
from typing import Any, Dict, Optional
from backend.mcp.client import MCPClient
logger = logging.getLogger(__name__)

class MCPIntegrationService:
    """
    Isolated service for connecting the chatbot to MCP tools.

    This service does not modify the existing RAG,
    translation, or chat-generation pipeline.
    """
    def __init__(self):
        self.client = MCPClient()
        self.connected = False
    async def connect(self) -> bool:
        """Connect to the MCP server."""
        try:
            if not self.connected:
                await self.client.connect()
                self.connected = True
            logger.info("MCP integration connected successfully.")
            return True
        except Exception as exc:
            logger.exception("MCP connection failed: %s", exc)
            self.connected = False
            return False
    async def disconnect(self) -> None:
        """Close the MCP connection."""
        try:
            if self.connected:
                await self.client.close()
                self.connected = False
            logger.info("MCP integration disconnected.")
        except Exception as exc:
            logger.exception("Error closing MCP connection: %s", exc)
    async def get_available_tools(self) -> list:
        """Return the tools exposed by the MCP server."""
        if not self.connected:
            raise RuntimeError("MCP client is not connected.")
        return await self.client.list_tools()
    async def call_tool(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Call an MCP tool without affecting the existing chatbot."""
        if not self.connected:
            raise RuntimeError("MCP client is not connected.")
        try:
            return await self.client.call_tool(
                tool_name,
                arguments or {},
            )
        except Exception as exc:
            logger.exception(
                "MCP tool '%s' failed: %s",
                tool_name,
                exc,
            )
            raise
    async def search_education(self, query: str) -> Any:
        return await self.call_tool(
            "search_education",
            {"query": query},
        )
    async def search_government_schemes(self, query: str) -> Any:
        return await self.call_tool(
            "search_government_schemes",
            {"query": query},
        )
    async def search_daily_life(self, query: str) -> Any:
        return await self.call_tool(
            "search_daily_life",
            {"query": query},
        )
    async def search_employment(self, query: str) -> Any:
        return await self.call_tool(
            "search_employment",
            {"query": query},
        )
    async def search_all_knowledge(self, query: str) -> Any:
        return await self.call_tool(
            "search_all_knowledge",
            {"query": query},
        )