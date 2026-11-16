"""Enhanced MCP server package.

A modular File Operations MCP server exposing the three MCP primitives:

* **Tools**     -> active operations   (``mcp_server.tools``)
* **Resources** -> passive data access (``mcp_server.resources``)
* **Prompts**   -> reusable workflows  (``mcp_server.prompts``)

Original implementation: IBM Skills Network lab "Build an Enhanced MCP Server"
(IBM RAG and Agentic AI Professional Certificate), authored by Abdul Fatir,
Joshua Zhou and Joseph Santarcangelo. Upstream repository:
https://github.com/joshuazhou744/enhanced-mcp-server (Apache 2.0).
"""

from mcp_server.app import create_server

__all__ = ["create_server"]
