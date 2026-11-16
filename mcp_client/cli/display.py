"""Formatting helpers for terminal output."""


def print_dir_listing(items: list[dict]) -> None:
    """Print a directory listing as a table (type, size, modified, name)."""
    print("\nDirectory Listing:\n")
    # Emojis render two columns wide, hence the wider "Type" header.
    print(f"{'Type':<13} {'Size':>10}  {'Modified':<26} {'Name'}")
    print("-" * 75)
    for item in items:
        icon = "📁" if item["type"] == "directory" else "📄"
        size = f"{item['size']} B"
        print(f"{icon:<2} {item['type']:<9} {size:>10}  {item['modified']:<26} {item['name']}")


def print_prompt_info(prompt) -> None:
    """Show a prompt's name, description and declared arguments."""
    print(f"\nPrompt: {prompt.name}")
    if prompt.description:
        print(f"  {prompt.description.strip().splitlines()[0]}")
    if prompt.arguments:
        names = ", ".join(a.name for a in prompt.arguments)
        print(f"  Arguments: {names}")
    else:
        print("  Arguments: none (the server may ask for inputs via elicitation)")
