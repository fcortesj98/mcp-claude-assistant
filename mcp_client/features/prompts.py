"""Run a server prompt template and hand the result to Claude."""

from mcp_client.agent import ClaudeAgent
from mcp_client.cli.display import print_prompt_info
from mcp_client.connection import MCPClient


async def run_prompt(mcp: MCPClient, agent: ClaudeAgent, prompt_name: str, input_fn=input) -> str | None:
    """Collect a prompt's arguments, render it on the server, and run it.

    Arguments declared by the prompt are asked for here; inputs the server
    gathers via elicitation are handled by the elicitation handler instead.

    Returns:
        Claude's response, or ``None`` if the prompt could not be run.
    """
    try:
        prompts = await mcp.list_prompts()
        prompt_obj = next((p for p in prompts if p.name == prompt_name), None)
        if prompt_obj is None:
            print(f"Prompt '{prompt_name}' not found")
            return None

        print_prompt_info(prompt_obj)

        arguments: dict[str, str] = {}
        for arg in prompt_obj.arguments or []:
            label = "required" if arg.required else "optional"
            value = input_fn(f"{arg.name} ({label}): ").strip()
            if not value and arg.required:
                print(f"Error: {arg.name} is required")
                return None
            if value:
                arguments[arg.name] = value

        prompt_text = await mcp.get_prompt_text(prompt_name, arguments)
        response = await agent.process_query(prompt_text)
        print(response)
        return response
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}\n")
        return None
