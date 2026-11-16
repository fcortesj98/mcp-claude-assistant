"""Server entry point (kept at the root so ``python client.py server.py`` works).

The implementation lives in the ``mcp_server`` package.
Based on the IBM Skills Network lab "Build an Enhanced MCP Server".
"""

from mcp_server.__main__ import main

if __name__ == "__main__":
    main()
