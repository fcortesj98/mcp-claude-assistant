"""File-system tools: create and delete files inside ``BASE_DIR``."""

import asyncio

from fastmcp import Context

from mcp_server import config
from mcp_server.core.paths import get_path


async def write_file(file_path: str, content: str, ctx: Context) -> str:
    """Create (or overwrite) a file with the given content.

    Parent directories are created if needed. Content is written in UTF-8,
    in chunks, and progress is reported back to the client after each chunk.

    Args:
        file_path: Relative path where the file should be created.
        content: Text content to write to the file.
        ctx: MCP context used for logging and progress reporting.

    Returns:
        Success message with the file path.
    """
    try:
        path = get_path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        total = len(content)
        chunk_size = max(total // config.WRITE_PROGRESS_STEPS, 1)

        with open(path, "w", encoding="utf-8") as f:
            for i in range(0, total, chunk_size):
                f.write(content[i : i + chunk_size])
                written = min(i + chunk_size, total)
                await ctx.report_progress(
                    progress=written, total=total, message=f"Writing progress: {written}/{total}"
                )
                # Non-blocking pause so the progress bar is visible in the demo.
                await asyncio.sleep(config.WRITE_PROGRESS_DELAY)

        await ctx.report_progress(progress=total, total=total, message="Write complete")
        await ctx.info(f"File written successfully to: {file_path}")
        return f"File written successfully to: {file_path}"
    except Exception as e:
        await ctx.error(f"Error creating file: {e}")
        raise


async def delete_file(file_path: str, ctx: Context) -> str:
    """Delete a file from the project directory.

    Directories are never deleted; only regular files.

    Args:
        file_path: Relative path to the file to delete.
        ctx: MCP context used for logging.

    Returns:
        Success or error message describing the result.
    """
    try:
        path = get_path(file_path)
        if path.is_file():
            path.unlink()
            await ctx.info(f"Successfully deleted file {file_path}")
            return f"Successfully deleted file {file_path}"
        if path.is_dir():
            msg = f"Error: {file_path} is a directory, not a file"
        else:
            msg = f"File not found: {file_path}"
        await ctx.warning(msg)
        return msg
    except Exception as e:
        await ctx.error(f"Error deleting file: {e}")
        return f"Error deleting file: {e}"


#: Tools exported by this module (registered by ``mcp_server.tools``).
TOOLS = [write_file, delete_file]
