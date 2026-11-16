"""A small, data-driven CLI menu.

Each entry is a ``MenuItem``; adding a feature to the menu is one line in
``mcp_client.app.build_menu``.
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

QUIT_KEYS = ("q", "quit")


@dataclass(frozen=True)
class MenuItem:
    key: str
    label: str
    action: Callable[[], Awaitable[Any]]


def render_menu(items: list[MenuItem]) -> str:
    lines = ["", "Select from the Menu"]
    lines += [f"{item.key}. {item.label}" for item in items]
    lines += ["q. Quit", "> "]
    return "\n".join(lines)


async def run_menu(items: list[MenuItem], input_fn=input) -> None:
    """Loop over the menu until the user quits."""
    actions = {item.key: item.action for item in items}
    print("\nMCP Client Started!")
    print("Select from the menu or 'quit'/'q' to exit.")

    while True:
        choice = input_fn(render_menu(items)).strip().lower()
        if choice in QUIT_KEYS:
            print("Exiting client...")
            return
        action = actions.get(choice)
        if action is None:
            print("Invalid choice. Please try again.")
            continue
        await action()
