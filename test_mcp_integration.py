
import asyncio

from backend.services.mcp_integration_service import (
    MCPIntegrationService,
)


async def main():
    mcp = MCPIntegrationService()

    try:
        connected = await mcp.connect()

        if not connected:
            print("MCP connection failed.")
            return

        print("\nMCP connected successfully.")

        tools = await mcp.get_available_tools()

        print("\nAvailable MCP tools:")
        for tool in tools:
            print(tool)

        print("\nTesting education search...")

        result = await mcp.search_education(
            "tribal education scholarship"
        )

        print("\nSearch result:")
        print(result)

    except Exception as exc:
        print(f"\nTest failed: {exc}")

    finally:
        await mcp.disconnect()


if __name__ == "__main__":
    asyncio.run(main())