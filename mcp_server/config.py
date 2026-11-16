"""Server-wide configuration.

Values can be overridden with environment variables so the same code can be
pointed at a different workspace without edits.
"""

import os
from pathlib import Path

#: Human-readable name advertised to MCP clients.
SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "File Operations MCP Server")

#: Sandbox root. Every file the server touches must live inside this folder.
#: Defaults to the current working directory, exactly like the original lab.
BASE_DIR: Path = Path(os.getenv("MCP_BASE_DIR", Path.cwd())).resolve()

#: Number of chunks ``write_file`` splits content into for progress reporting.
WRITE_PROGRESS_STEPS: int = int(os.getenv("MCP_WRITE_PROGRESS_STEPS", "10"))

#: Delay (seconds) between chunks, purely so progress is visible in the demo.
WRITE_PROGRESS_DELAY: float = float(os.getenv("MCP_WRITE_PROGRESS_DELAY", "0.05"))
