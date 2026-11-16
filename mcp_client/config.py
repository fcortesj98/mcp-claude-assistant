"""Client configuration, loaded from environment variables / ``.env``."""

import os

from dotenv import load_dotenv

load_dotenv()  # Reads ANTHROPIC_API_KEY and the overrides below from .env

#: Claude model used by the agent (the lab default; override with CLAUDE_MODEL).
MODEL_ID: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")

#: Max tokens per Claude response.
MAX_TOKENS: int = int(os.getenv("CLAUDE_MAX_TOKENS", "4096"))

#: Safety limit on tool-use round trips for a single query.
MAX_TOOL_ROUNDS: int = int(os.getenv("CLAUDE_MAX_TOOL_ROUNDS", "10"))

#: Server script extensions the STDIO transport knows how to launch.
SUPPORTED_SERVER_SUFFIXES: tuple[str, ...] = (".py", ".js", ".ts")
