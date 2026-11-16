import sys
from pathlib import Path

import pytest

# Make the project importable when running `pytest` from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp_server import config  # noqa: E402


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    """Point the server's sandbox at a temp folder with a sample file."""
    monkeypatch.setattr(config, "BASE_DIR", tmp_path.resolve())
    monkeypatch.setattr(config, "WRITE_PROGRESS_DELAY", 0)
    (tmp_path / "hello.py").write_text("print('hello')\n", encoding="utf-8")
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "mod.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path
