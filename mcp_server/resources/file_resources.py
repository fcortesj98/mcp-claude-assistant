"""File resources: read a file's content via the ``file:///`` URI scheme."""

from mcp_server.core.paths import get_path

#: ``file://`` expects a host; the host is empty (local), hence three slashes.
#: Clients must URL-encode nested paths, e.g. ``file:///src%2Fapp.py``.
FILE_URI_TEMPLATE = "file:///{file_name}"


async def read_file_resource(file_name: str) -> dict:
    """Read the content of a file as an MCP resource template.

    Args:
        file_name: Relative path to the file to read (URL-decoded by FastMCP).

    Returns:
        ``{"file_content": ...}`` on success, or ``{"error": ...}``.
    """
    try:
        path = get_path(file_name)
        if not path.is_file():
            return {"error": f"Error: {file_name} is not a valid file"}
        return {"file_content": path.read_text(encoding="utf-8")}
    except Exception as e:
        return {"error": f"Error reading file: {e}"}


#: ``(uri, function)`` pairs registered by ``mcp_server.resources``.
RESOURCES = [(FILE_URI_TEMPLATE, read_file_resource)]
