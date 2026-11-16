"""Run the server over STDIO: ``python -m mcp_server``."""

import sys

from mcp_server import config
from mcp_server.app import mcp


def main() -> None:
    # Log to stderr: with the STDIO transport, stdout carries JSON-RPC messages.
    print(f"Starting {mcp.name} (base dir: {config.BASE_DIR})...", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()
