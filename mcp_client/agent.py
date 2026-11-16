"""The Claude agent: an agentic tool-use loop over the MCP server's tools."""

import os
from typing import Any

from anthropic import AsyncAnthropic

from mcp_client import config
from mcp_client.connection import MCPClient


class ClaudeAgent:
    """Answers queries with Claude, letting it call MCP tools as needed."""

    def __init__(
        self,
        mcp: MCPClient,
        model: str = config.MODEL_ID,
        max_tokens: int = config.MAX_TOKENS,
        max_tool_rounds: int = config.MAX_TOOL_ROUNDS,
        anthropic: AsyncAnthropic | None = None,
    ):
        self.mcp = mcp
        self.model = model
        self.max_tokens = max_tokens
        self.max_tool_rounds = max_tool_rounds
        self._anthropic = anthropic

    @property
    def anthropic(self) -> AsyncAnthropic:
        # Created lazily so resource-only features work without an API key.
        if self._anthropic is None:
            if not os.getenv("ANTHROPIC_API_KEY"):
                raise RuntimeError(
                    "ANTHROPIC_API_KEY is not set. Add it to a .env file (see .env.example)."
                )
            self._anthropic = AsyncAnthropic()
        return self._anthropic

    async def _ask_claude(self, messages: list[dict], tools: list[dict]):
        return await self.anthropic.messages.create(
            model=self.model, max_tokens=self.max_tokens, messages=messages, tools=tools
        )

    async def _run_tool_calls(self, content_blocks) -> list[dict[str, Any]]:
        """Execute every ``tool_use`` block and return the ``tool_result`` blocks."""
        results = []
        for block in content_blocks:
            if block.type != "tool_use":
                continue
            try:
                text = await self.mcp.call_tool_text(block.name, block.input)
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": text})
            except Exception as e:
                print(f"Error calling tool {block.name}: {e}")
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Error: {e}",
                        "is_error": True,
                    }
                )
        return results

    async def process_query(self, query: str, history: list[dict] | None = None) -> str:
        """Run the agentic loop for one user query.

        Args:
            query: The user's message.
            history: Optional message list to continue a multi-turn
                conversation. It is updated in place with this turn.

        Returns:
            Claude's final text answer.
        """
        messages = history if history is not None else []
        messages.append({"role": "user", "content": query})
        tools = await self.mcp.list_tools_for_claude()

        response = await self._ask_claude(messages, tools)
        rounds = 0
        while response.stop_reason == "tool_use" and rounds < self.max_tool_rounds:
            rounds += 1
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": await self._run_tool_calls(response.content)})
            response = await self._ask_claude(messages, tools)

        text = "\n".join(b.text for b in response.content if getattr(b, "text", None))
        if response.stop_reason == "tool_use":
            # Don't store unanswered tool_use blocks: the next turn would be rejected.
            text += f"\n[Stopped after {self.max_tool_rounds} tool rounds]"
        else:
            messages.append({"role": "assistant", "content": response.content})
        return text
