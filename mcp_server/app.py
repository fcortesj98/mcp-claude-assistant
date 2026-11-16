"""Server factory: builds a FastMCP instance and registers every primitive."""

from fastmcp import FastMCP

from mcp_server import config
from mcp_server.prompts import register_prompts
from mcp_server.resources import register_resources
from mcp_server.tools import register_tools


def create_server(name: str | None = None) -> FastMCP:
    """Create a fully configured MCP server.

    Args:
        name: Optional server name; defaults to ``config.SERVER_NAME``.

    Returns:
        A ``FastMCP`` instance with all tools, resources and prompts attached.
    """
    mcp = FastMCP(name or config.SERVER_NAME)
    register_tools(mcp)
    register_resources(mcp)
    register_prompts(mcp)
    return mcp


#: Module-level instance, handy for ``fastmcp run mcp_server/app.py:mcp``.
mcp = create_server()
