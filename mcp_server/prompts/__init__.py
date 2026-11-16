"""MCP **prompts**: user-controlled templates that kick off a workflow.

Prompts can get their inputs as function arguments (``code_review``) or ask
the user mid-call through elicitation (``documentation_generator``).

To add a prompt:
    1. Write an ``async def`` function returning a ``str`` in a module here.
    2. Append it to that module's ``PROMPTS`` list.
    3. If it is a new module, add the module to ``_MODULES`` below.
"""

from fastmcp import FastMCP

from mcp_server.prompts import code_review, documentation

_MODULES = [code_review, documentation]


def register_prompts(mcp: FastMCP) -> None:
    """Register every prompt exported by the modules in ``_MODULES``."""
    for module in _MODULES:
        for fn in module.PROMPTS:
            mcp.prompt(fn)
