
import asyncio
from backend.mcp.client import MCPClient

async def main():
    client = MCPClient()

    try:
        print("\nConnecting to MCP server...")
        await client.connect()
        print("Connection successful!")

        print("\nFetching available tools...")
        tools = await client.list_tools()

        for tool in tools:
            print(f"- {tool.name}: {tool.description}")

        print("\nTesting education search...")
        result = await client.call_tool(
            "search_education",
            {
                "query": "tribal education scholarship",
                "language": "english",
                "limit": 3
            }
        )

        for item in result.content:
            if hasattr(item, "text"):
                print(item.text)

        if result.isError:
            print("\nThe MCP tool returned an error.")

    except Exception as error:
        print(f"\nMCP test failed: {error}")

    finally:
        await client.close()
        print("\nMCP connection closed.")

if __name__ == "__main__":
    asyncio.run(main())