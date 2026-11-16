"""Path helpers that keep every file operation inside ``BASE_DIR``."""

from dataclasses import dataclass
from pathlib import Path

from mcp_server import config


class PathOutsideBaseDirError(ValueError):
    """Raised when a requested path escapes the server's sandbox directory."""


def get_path(relative_path: str) -> Path:
    """Convert a relative path into an absolute path inside ``BASE_DIR``.

    The path is resolved against ``BASE_DIR`` (not the process CWD), so
    ``..`` segments, absolute paths and symlinks that point outside the
    sandbox are rejected.

    Args:
        relative_path: Path supplied by the client, e.g. ``"src/app.py"``.

    Returns:
        Absolute, resolved ``Path`` within ``BASE_DIR``.

    Raises:
        PathOutsideBaseDirError: If the resolved path is outside ``BASE_DIR``.
    """
    base = config.BASE_DIR
    candidate = (base / relative_path).resolve()
    if not candidate.is_relative_to(base):
        raise PathOutsideBaseDirError(f"Path is outside BASE_DIR: {relative_path}")
    return candidate


@dataclass(frozen=True)
class SourceFile:
    """A text file loaded from the sandbox, ready to embed in a prompt."""

    relative_path: str
    content: str
    language: str  # file suffix, e.g. ".py" (empty string when there is none)


def read_source_file(relative_path: str) -> SourceFile:
    """Load a text file from ``BASE_DIR`` for use in a prompt.

    Args:
        relative_path: Path relative to ``BASE_DIR``.

    Returns:
        ``SourceFile`` with the stripped content and its suffix.

    Raises:
        FileNotFoundError: If the path does not exist or is not a file.
        PathOutsideBaseDirError: If the path escapes ``BASE_DIR``.
    """
    path = get_path(relative_path)
    if not path.is_file():
        raise FileNotFoundError(f"Error: {relative_path} is not a valid file")
    return SourceFile(
        relative_path=relative_path,
        content=path.read_text(encoding="utf-8").strip(),
        language=path.suffix.lower(),
    )
