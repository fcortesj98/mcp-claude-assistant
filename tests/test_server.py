"""In-memory tests for every server primitive (no subprocess, no API key)."""

import asyncio
import json

import pytest
from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult

from mcp_client.features.resources import file_uri
from mcp_server import create_server
from mcp_server.core.paths import PathOutsideBaseDirError, get_path


def run(coro):
    return asyncio.run(coro)


async def _with_client(fn, **client_kwargs):
    async with Client(create_server(), **client_kwargs) as client:
        return await fn(client)


# --------------------------------------------------------------------- registry
def test_all_primitives_registered(workspace):
    async def check(c):
        tools = {t.name for t in await c.list_tools()}
        resources = {str(r.uri) for r in await c.list_resources()}
        templates = {t.uriTemplate for t in await c.list_resource_templates()}
        prompts = {p.name for p in await c.list_prompts()}
        return tools, resources, templates, prompts

    tools, resources, templates, prompts = run(_with_client(check))
    assert tools == {"write_file", "delete_file"}
    assert resources == {"dir://."}
    assert templates == {"file:///{file_name}"}
    assert prompts == {"code_review", "documentation_generator"}


# ------------------------------------------------------------------------ paths
def test_get_path_blocks_escape(workspace):
    assert get_path("pkg/mod.py") == workspace / "pkg" / "mod.py"
    for bad in ("../outside.txt", "/etc/passwd"):
        with pytest.raises(PathOutsideBaseDirError):
            get_path(bad)


# ------------------------------------------------------------------------ tools
def test_write_file_reports_progress(workspace):
    updates = []

    async def on_progress(progress, total, message):
        updates.append((progress, total))

    async def go(c):
        return await c.call_tool("write_file", {"file_path": "out/new.md", "content": "abc" * 20})

    result = run(_with_client(go, progress_handler=on_progress))
    assert "written successfully" in result.content[0].text
    assert (workspace / "out" / "new.md").read_text() == "abc" * 20
    assert updates and updates[-1] == (60, 60)


def test_write_file_outside_sandbox_fails(workspace):
    async def go(c):
        return await c.call_tool("write_file", {"file_path": "../x.txt", "content": "x"}, raise_on_error=False)

    assert run(_with_client(go)).is_error


def test_delete_file(workspace):
    async def go(c):
        ok = await c.call_tool("delete_file", {"file_path": "hello.py"})
        is_dir = await c.call_tool("delete_file", {"file_path": "pkg"})
        missing = await c.call_tool("delete_file", {"file_path": "nope.txt"})
        return ok.content[0].text, is_dir.content[0].text, missing.content[0].text

    ok, is_dir, missing = run(_with_client(go))
    assert ok.startswith("Successfully deleted") and not (workspace / "hello.py").exists()
    assert "is a directory" in is_dir and (workspace / "pkg").is_dir()
    assert missing.startswith("File not found")


# -------------------------------------------------------------------- resources
def test_read_file_resource_nested_path(workspace):
    async def go(c):
        return json.loads((await c.read_resource(file_uri("pkg/mod.py")))[0].text)

    assert run(_with_client(go)) == {"file_content": "x = 1\n"}


def test_read_file_resource_errors(workspace):
    async def go(c):
        missing = json.loads((await c.read_resource(file_uri("missing.py")))[0].text)
        escape = json.loads((await c.read_resource(file_uri("../secret")))[0].text)
        return missing, escape

    missing, escape = run(_with_client(go))
    assert "error" in missing and "error" in escape


def test_list_directory_resource(workspace):
    async def go(c):
        return json.loads((await c.read_resource("dir://."))[0].text)

    items = run(_with_client(go))["items"]
    assert [(i["name"], i["type"]) for i in items] == [("pkg", "directory"), ("hello.py", "file")]


# ---------------------------------------------------------------------- prompts
def test_code_review_prompt(workspace):
    async def go(c):
        return (await c.get_prompt("code_review", {"file_path": "hello.py"})).messages[0].content.text

    text = run(_with_client(go))
    assert "expert code editor" in text and "print('hello')" in text and ".py" in text


def test_documentation_prompt_uses_elicitation(workspace):
    async def answer(message, response_type, params, context):
        return response_type(file_path="hello.py", name="HELLO_DOCS")

    async def go(c):
        return (await c.get_prompt("documentation_generator")).messages[0].content.text

    text = run(_with_client(go, elicitation_handler=answer))
    assert "HELLO_DOCS" in text and "print('hello')" in text


def test_documentation_prompt_declined(workspace):
    async def decline(message, response_type, params, context):
        return ElicitResult(action="decline")

    async def go(c):
        return await c.get_prompt("documentation_generator")

    with pytest.raises(Exception):
        run(_with_client(go, elicitation_handler=decline))
