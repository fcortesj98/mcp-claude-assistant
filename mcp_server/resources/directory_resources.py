"""Directory resources: list the contents of the project root (``dir://.``)."""

from datetime import datetime
from pathlib import Path

from mcp_server import config
from mcp_server.core.paths import get_path

DIR_URI = "dir://."


def _describe(item: Path) -> dict:
    """Return the metadata dictionary for one directory entry."""
    stat = item.stat()
    return {
        "name": item.name,
        "path": str(item.relative_to(config.BASE_DIR)),
        "type": "directory" if item.is_dir() else "file",
        "size": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
    }


async def list_files_resource() -> dict:
    """List files and directories in ``BASE_DIR`` as a static MCP resource.

    Returns:
        ``{"items": [...]}`` with name, path, type, size and timestamps for
        each entry (directories first, then alphabetical), or ``{"error": ...}``.
    """
    try:
        path = get_path(".")
        if not path.is_dir():
            return {"error": f"{path} is not a valid directory"}
        entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        return {"items": [_describe(item) for item in entries]}
    except Exception as e:
        return {"error": f"Error listing files: {e}"}


#: ``(uri, function)`` pairs registered by ``mcp_server.resources``.
RESOURCES = [(DIR_URI, list_files_resource)]
