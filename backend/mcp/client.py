import os
import sys
from pathlib import Path
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
PROJECT_ROOT = Path(__file__).resolve().parents[2]
class MCPClient:
    def __init__(self):
        self.session = None
        self.exit_stack = AsyncExitStack()

    async def connect(self):
        """Start the MCP server and establish a client session."""
        if self.session is not None:
            return
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "backend.mcp.server"],
            env=os.environ.copy(),
            cwd=str(PROJECT_ROOT)
        )
        read, write = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await self.session.initialize()

    async def list_tools(self):
        """Return the tools exposed by the MCP server."""
        if self.session is None:
            raise RuntimeError("MCP client is not connected.")
        response = await self.session.list_tools()
        return response.tools

    async def call_tool(self, tool_name, arguments):
        """Execute an MCP tool and return its result."""
        if self.session is None:
            raise RuntimeError("MCP client is not connected.")
        return await self.session.call_tool(
            tool_name,
            arguments
        )
    async def close(self):
        """Close the MCP connection and server process."""
        await self.exit_stack.aclose()
        self.session = None