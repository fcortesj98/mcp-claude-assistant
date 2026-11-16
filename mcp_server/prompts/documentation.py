"""Documentation prompt: inputs gathered through user elicitation."""

from fastmcp import Context

from mcp_server.core.paths import read_source_file
from mcp_server.core.schemas import DocumentGeneratorSchema

DOCUMENTATION_TEMPLATE = """You are an expert technical writer and documentation specialist. Create documentation for the following code file:

File: {file_path}
Language (file suffix): {language}

Current code:
'''
{code}
'''

Use MCP tools available to you to create the separate documentation file:
- **CRITICAL DETAIL: Name that separate document EXACTLY: {doc_name}**
- Add the .md suffix yourself if the name doesn't include it already"""


async def documentation_generator(ctx: Context) -> str:
    """Generate a prompt asking Claude to write a documentation file.

    The source file and the documentation file name are not arguments: they
    are requested from the user at runtime with ``ctx.elicit``.

    Args:
        ctx: MCP context used for elicitation and logging.

    Returns:
        The formatted documentation prompt.

    Raises:
        RuntimeError: If the user declines or cancels the elicitation.
        FileNotFoundError: If the elicited file does not exist.
    """
    try:
        result = await ctx.elicit(
            message="Please provide the subject file name and the documentation file name",
            response_type=DocumentGeneratorSchema,
        )
        if result.action != "accept":
            raise RuntimeError(f"User did not provide the inputs (action: {result.action})")

        source = read_source_file(result.data.file_path)
        prompt = DOCUMENTATION_TEMPLATE.format(
            file_path=source.relative_path,
            language=source.language or "unknown",
            code=source.content,
            doc_name=result.data.name,
        ).strip()
        await ctx.info("Successfully returned prompt")
        return prompt
    except FileNotFoundError as e:
        await ctx.warning(str(e))
        raise
    except Exception as e:
        await ctx.error(f"Error generating code documentation prompt: {e}")
        raise


#: Prompts exported by this module (registered by ``mcp_server.prompts``).
PROMPTS = [documentation_generator]
