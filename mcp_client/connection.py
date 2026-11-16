"""MCP connection layer: owns the FastMCP ``Client`` and its lifecycle."""

import json
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

from fastmcp import Client

from mcp_client import config
from mcp_client.handlers import handle_message, handle_progress, make_elicitation_handler


class MCPClient:
    """Connects to an MCP server over STDIO and wraps the calls the app needs.

    Usage::

        async with MCPClient() as mcp:
            await mcp.connect("server.py")
            tools = await mcp.list_tools_for_claude()
    """

    def __init__(self, elicitation_handler=None, progress_handler=None, message_handler=None):
        self.exit_stack = AsyncExitStack()
        self.client: Client | None = None
        self._elicitation_handler = elicitation_handler or make_elicitation_handler()
        self._progress_handler = progress_handler or handle_progress
        self._message_handler = message_handler or handle_message

    # ------------------------------------------------------------------ lifecycle
    async def connect(self, server: Any) -> None:
        """Connect to a server.

        Args:
            server: Path to a ``.py``/``.js``/``.ts`` server script (launched as
                a subprocess over STDIO), or any other transport FastMCP's
                ``Client`` accepts (e.g. an in-memory ``FastMCP`` instance).

        Raises:
            ValueError: If a script path has an unsupported extension.
        """
        if isinstance(server, (str, Path)) and not str(server).endswith(
            config.SUPPORTED_SERVER_SUFFIXES
        ):
            raise ValueError("Server script must be a .py, .js, or .ts file")

        self.client = Client(
            server,
            elicitation_handler=self._elicitation_handler,
            progress_handler=self._progress_handler,
            message_handler=self._message_handler,
        )
        await self.exit_stack.enter_async_context(self.client)

    async def cleanup(self) -> None:
        """Close the connection and stop the server subprocess."""
        await self.exit_stack.aclose()

    async def __aenter__(self) -> "MCPClient":
        return self

    async def __aexit__(self, *exc) -> None:
        await self.cleanup()

    @property
    def session(self) -> Client:
        if self.client is None:
            raise RuntimeError("Not connected: call connect() first")
        return self.client

    # ---------------------------------------------------------------------- tools
    async def list_tools_for_claude(self) -> list[dict[str, Any]]:
        """Return the server's tools in the format the Claude API expects."""
        return [
            {
                "name": tool.name,
                "description": tool.description or "MCP Tool",
                "input_schema": tool.inputSchema,
            }
            for tool in await self.session.list_tools()
        ]

    async def call_tool_text(self, name: str, arguments: dict[str, Any]) -> str:
        """Call a tool and flatten its content blocks into plain text."""
        result = await self.session.call_tool(name, arguments)
        if isinstance(result.content, list):
            return "\n".join(getattr(c, "text", str(c)) for c in result.content)
        return str(result.content)

    # -------------------------------------------------------------------- prompts
    async def list_prompts(self):
        return await self.session.list_prompts()

    async def get_prompt_text(self, name: str, arguments: dict[str, str] | None = None) -> str:
        """Render a prompt template on the server and return its text."""
        result = await self.session.get_prompt(name, arguments=arguments or {})
        return result.messages[0].content.text

    # ------------------------------------------------------------------ resources
    async def list_resources(self):
        return await self.session.list_resources()

    async def list_resource_templates(self):
        return await self.session.list_resource_templates()

    async def read_resource_json(self, uri: str) -> dict[str, Any]:
        """Read a resource whose content is a JSON object and decode it."""
        contents = await self.session.read_resource(uri)
        return json.loads(contents[0].text)
