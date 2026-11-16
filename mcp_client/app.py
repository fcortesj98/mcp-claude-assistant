"""Application wiring: connect, build the menu, run, clean up."""

import asyncio
import sys

from mcp_client.agent import ClaudeAgent
from mcp_client.cli.menu import MenuItem, run_menu
from mcp_client.connection import MCPClient
from mcp_client.features.conversation import converse
from mcp_client.features.prompts import run_prompt
from mcp_client.features.resources import read_dir, read_file


def build_menu(mcp: MCPClient, agent: ClaudeAgent) -> list[MenuItem]:
    """Menu entries, in display order. Add new features here."""
    return [
        MenuItem("1", "Generate Documentation", lambda: run_prompt(mcp, agent, "documentation_generator")),
        MenuItem("2", "Review Code", lambda: run_prompt(mcp, agent, "code_review")),
        MenuItem("3", "Read File", lambda: read_file(mcp)),
        MenuItem("4", "Read Current Directory", lambda: read_dir(mcp)),
        MenuItem("5", "Converse with Agent", lambda: converse(agent)),
    ]


async def run(server_path: str) -> None:
    async with MCPClient() as mcp:
        print(f"Connecting to server: {server_path}")
        await mcp.connect(server_path)
        agent = ClaudeAgent(mcp)
        await run_menu(build_menu(mcp, agent))


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("Usage: python client.py <server_path>")
        sys.exit(1)
    try:
        asyncio.run(run(argv[0]))
    except (KeyboardInterrupt, EOFError):
        print("\nExiting client...")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
