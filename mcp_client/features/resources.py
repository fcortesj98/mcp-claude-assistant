"""Read data from the server through its resources."""

from urllib.parse import quote

from mcp_client.cli.display import print_dir_listing
from mcp_client.connection import MCPClient


def file_uri(path: str) -> str:
    """Build a ``file:///`` URI, URL-encoding the path so ``/`` survives."""
    return f"file:///{quote(path, safe='')}"


async def read_file(mcp: MCPClient, input_fn=input) -> str | None:
    """Ask for a path and print the file via the ``file:///{file_name}`` template."""
    try:
        file_name = input_fn("Enter file path: ").strip()
        data = await mcp.read_resource_json(file_uri(file_name))
        if "error" in data:
            print(data["error"])
            return None
        print(f"File Content:\n {data['file_content']}")
        return data["file_content"]
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


async def read_dir(mcp: MCPClient) -> list[dict] | None:
    """Print the project directory via the static ``dir://.`` resource."""
    try:
        data = await mcp.read_resource_json("dir://.")
        if "error" in data:
            print(data["error"])
            return None
        print_dir_listing(data["items"])
        return data["items"]
    except Exception as e:
        print(f"Error reading directory: {e}")
        return None
