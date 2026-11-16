"""Shared building blocks used by tools, resources and prompts."""

from mcp_server.core.paths import PathOutsideBaseDirError, get_path, read_source_file
from mcp_server.core.schemas import DocumentGeneratorSchema

__all__ = [
    "DocumentGeneratorSchema",
    "PathOutsideBaseDirError",
    "get_path",
    "read_source_file",
]
