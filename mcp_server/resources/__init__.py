"""MCP **resources**: application-controlled, read-only data exposed by URI.

Static resources have a fixed URI (``dir://.``); resource *templates* have
parameters in the URI (``file:///{file_name}``).

To add a resource:
    1. Write an ``async def`` function in a module in this package.
    2. Append ``(uri, function)`` to that module's ``RESOURCES`` list.
    3. If it is a new module, add the module to ``_MODULES`` below.
"""

from fastmcp import FastMCP

from mcp_server.resources import directory_resources, file_resources

_MODULES = [file_resources, directory_resources]


def register_resources(mcp: FastMCP) -> None:
    """Register every resource exported by the modules in ``_MODULES``."""
    for module in _MODULES:
        for uri, fn in module.RESOURCES:
            mcp.resource(uri)(fn)
