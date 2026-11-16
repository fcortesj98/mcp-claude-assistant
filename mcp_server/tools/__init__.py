"""MCP **tools**: model-controlled actions that change state.

To add a tool:
    1. Write an ``async def`` function in a module in this package
       (or add it to an existing module).
    2. Append it to that module's ``TOOLS`` list.
    3. If it is a new module, add the module to ``_MODULES`` below.
"""

from fastmcp import FastMCP

from mcp_server.tools import file_tools

_MODULES = [file_tools]


def register_tools(mcp: FastMCP) -> None:
    """Register every tool exported by the modules in ``_MODULES``."""
    for module in _MODULES:
        for fn in module.TOOLS:
            mcp.tool(fn)
