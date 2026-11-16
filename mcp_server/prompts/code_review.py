"""Code-review prompt: inputs supplied as regular prompt arguments."""

from fastmcp import Context

from mcp_server.core.paths import read_source_file

CODE_REVIEW_TEMPLATE = """You are an expert code editor. Review the following code quality.

File: {file_path}
Language (file suffix): {language}

Current code:
'''
{code}
'''

Provide a comprehensive evaluation of the code:
"""


async def code_review(file_path: str, ctx: Context) -> str:
    """Generate a prompt asking Claude for a code review of a file.

    Args:
        file_path: Relative path to the code file to review.
        ctx: MCP context used for logging.

    Returns:
        The formatted code-review prompt.

    Raises:
        FileNotFoundError: If ``file_path`` is not an existing file.
    """
    try:
        source = read_source_file(file_path)
        prompt = CODE_REVIEW_TEMPLATE.format(
            file_path=source.relative_path,
            language=source.language or "unknown",
            code=source.content,
        ).strip()
        await ctx.info("Successfully returned prompt")
        return prompt
    except FileNotFoundError as e:
        await ctx.warning(str(e))
        raise
    except Exception as e:
        await ctx.error(f"Error preparing code review prompt: {e}")
        raise


#: Prompts exported by this module (registered by ``mcp_server.prompts``).
PROMPTS = [code_review]
