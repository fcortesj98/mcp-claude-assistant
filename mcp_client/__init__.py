"""Enhanced MCP client package.

* ``connection``  -> ``MCPClient``: STDIO connection + thin MCP API wrapper
* ``handlers``    -> elicitation / progress / notification callbacks
* ``agent``       -> ``ClaudeAgent``: the Claude tool-use (agentic) loop
* ``features``    -> one module per user-facing capability
* ``cli``         -> menu registry and terminal formatting

Original implementation: IBM Skills Network lab "Build an Enhanced MCP Server"
(IBM RAG and Agentic AI Professional Certificate), authored by Abdul Fatir,
Joshua Zhou and Joseph Santarcangelo. Upstream repository:
https://github.com/joshuazhou744/enhanced-mcp-server (Apache 2.0).
"""

from mcp_client.agent import ClaudeAgent
from mcp_client.connection import MCPClient

__all__ = ["ClaudeAgent", "MCPClient"]
