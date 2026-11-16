"""Free-form chat with Claude, which can call the server's tools."""

from mcp_client.agent import ClaudeAgent

EXIT_WORDS = ("quit", "q")


async def converse(agent: ClaudeAgent, input_fn=input) -> None:
    """Multi-turn conversation; history is kept until the user exits."""
    print("\nEntering conversation mode. Type 'quit' or 'q' to exit.")
    history: list[dict] = []

    while True:
        query = input_fn("\nQuery: ").strip()
        if query.lower() in EXIT_WORDS:
            return
        if not query:
            print("Please enter a query")
            continue
        checkpoint = len(history)
        try:
            print("\n" + await agent.process_query(query, history=history))
        except Exception as e:
            del history[checkpoint:]  # Drop the failed turn so history stays valid
            print(f"Error processing query: {e}")
