import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.mcp.knowledge_tools import search_knowledge, get_knowledge_categories, get_official_links

SERVER_NAME = "Multilingual Education and Daily-Life Assistant"
SUPPORTED_LANGUAGES = ["English", "Hindi", "Manipuri (Meitei Mayek)", "Manipuri (Bengali Script)"]

mcp = FastMCP(SERVER_NAME)

@mcp.tool()
def health_check() -> dict:
    """Check whether the independent MCP server is running."""
    return {
        "status": "healthy",
        "server": SERVER_NAME,
        "languages": SUPPORTED_LANGUAGES
    }

@mcp.tool()
def search_education(query: str, language: str = "english", limit: int = 5) -> dict:
    """Search educational information, learning resources and scholarships."""
    return search_knowledge(query, language, "education", limit)

@mcp.tool()
def search_government_schemes(query: str, language: str = "english", limit: int = 5) -> dict:
    """Search government schemes, policies and welfare information."""
    return search_knowledge(query, language, "government", limit)

@mcp.tool()
def search_daily_life(query: str, language: str = "english", limit: int = 5) -> dict:
    """Search practical daily-life information and guidance."""
    return search_knowledge(query, language, "daily_life", limit)

@mcp.tool()
def search_employment(query: str, language: str = "english", limit: int = 5) -> dict:
    """Search employment, career and skill-development information."""
    return search_knowledge(query, language, "employment", limit)

@mcp.tool()
def search_all_knowledge(query: str, language: str = "english", limit: int = 5) -> dict:
    """Search all available knowledge categories."""
    return search_knowledge(query, language, "all", limit)

@mcp.tool()
def list_knowledge_categories() -> list:
    """List the available knowledge categories."""
    return get_knowledge_categories()

@mcp.tool()
def find_official_links(query: str, limit: int = 10) -> list:
    """Find official resource links stored in the verified knowledge base."""
    return get_official_links(query, limit)

if __name__ == "__main__":
    mcp.run()