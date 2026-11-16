"""Callbacks the server can trigger on the client through MCP Context.

* ``handle_elicitation`` -> server asks the user for structured input
* ``handle_progress``    -> server reports progress (``ctx.report_progress``)
* ``handle_message``     -> server notifications (list changed, etc.)
"""

from collections.abc import Callable
from typing import Any

from fastmcp.client.elicitation import ElicitResult

InputFn = Callable[[str], str]


def make_elicitation_handler(input_fn: InputFn = input):
    """Build an elicitation handler that asks for each field on the terminal.

    ``input_fn`` is injectable so the handler can be tested or wired to
    another UI without changing its logic.
    """

    async def handle_elicitation(message: str, response_type: type | None, params, context) -> Any:
        """Prompt the user for every field of ``response_type``.

        Returns:
            An instance of ``response_type`` with the user's answers, or
            ``ElicitResult(action="decline")`` if a field is left empty.
        """
        print(f"Server asks: {message}")
        if response_type is None:  # Server only wants a confirmation
            answer = input_fn("Accept? [y/N]: ").strip().lower()
            return ElicitResult(action="accept" if answer == "y" else "decline")

        user_data: dict[str, str] = {}
        for field_name, field_type in getattr(response_type, "__annotations__", {}).items():
            type_name = getattr(field_type, "__name__", str(field_type))
            user_input = input_fn(f"Enter value for '{field_name}' ({type_name}): ").strip()
            if not user_input:
                return ElicitResult(action="decline")
            user_data[field_name] = user_input

        return response_type(**user_data)

    return handle_elicitation


async def handle_progress(progress: float, total: float | None, message: str | None) -> None:
    """Print progress updates, as a percentage when ``total`` is known."""
    if total:
        print(f"Progress: {progress / total * 100:.1f}% - {message or ''}")
    else:
        print(f"Progress: {progress} - {message or ''}")


async def handle_message(message) -> None:
    """Print server notifications such as tool/resource list changes."""
    root = getattr(message, "root", None)
    method = getattr(root, "method", None)
    if not method:
        return
    print(f"Received: {method}")
    if method == "notifications/tools/list_changed":
        print("Tools have changed - might want to refresh tool cache")
    elif method == "notifications/resources/list_changed":
        print("Resources have changed")
