"""Client tests: agent loop with a fake Claude, features, menu, and STDIO e2e."""

import asyncio
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from mcp_client import ClaudeAgent, MCPClient
from mcp_client.cli.menu import MenuItem, run_menu
from mcp_client.features.conversation import converse
from mcp_client.features.prompts import run_prompt
from mcp_client.features.resources import read_dir, read_file
from mcp_client.handlers import make_elicitation_handler
from mcp_server import create_server

ROOT = Path(__file__).resolve().parents[1]


def run(coro):
    return asyncio.run(coro)


def feed(*answers):
    it = iter(answers)
    return lambda _prompt="": next(it)


# ------------------------------------------------------------- fake Anthropic
def _text(t):
    return SimpleNamespace(type="text", text=t)


def _tool_use(id_, name, args):
    return SimpleNamespace(type="tool_use", id=id_, name=name, input=args)


class FakeAnthropic:
    """Replays scripted responses and records the requests it received."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.requests = []
        self.messages = SimpleNamespace(create=self._create)

    async def _create(self, **kwargs):
        self.requests.append({**kwargs, "messages": list(kwargs["messages"])})
        return self._responses.pop(0)


def _resp(stop_reason, *blocks):
    return SimpleNamespace(stop_reason=stop_reason, content=list(blocks))


async def _connected(**kw) -> MCPClient:
    mcp = MCPClient(**kw)
    await mcp.connect(create_server())
    return mcp


# ------------------------------------------------------------------- agent
def test_agent_runs_tool_loop(workspace):
    fake = FakeAnthropic([
        _resp("tool_use", _text("Creating it"), _tool_use("t1", "write_file", {"file_path": "a.txt", "content": "hi"})),
        _resp("end_turn", _text("Done: a.txt created")),
    ])

    async def go():
        async with await _connected() as mcp:
            agent = ClaudeAgent(mcp, anthropic=fake)
            return await agent.process_query("make a.txt")

    assert run(go()) == "Done: a.txt created"
    assert (workspace / "a.txt").read_text() == "hi"
    second = fake.requests[1]
    assert {t["name"] for t in second["tools"]} == {"write_file", "delete_file"}
    tool_result = second["messages"][-1]["content"][0]
    assert tool_result["type"] == "tool_result" and "written successfully" in tool_result["content"]


def test_agent_reports_tool_errors_to_claude(workspace):
    fake = FakeAnthropic([
        _resp("tool_use", _tool_use("t1", "write_file", {"file_path": "../evil", "content": "x"})),
        _resp("end_turn", _text("Could not write")),
    ])

    async def go():
        async with await _connected() as mcp:
            return await ClaudeAgent(mcp, anthropic=fake).process_query("escape")

    assert run(go()) == "Could not write"
    assert fake.requests[1]["messages"][-1]["content"][0]["is_error"] is True


def test_agent_stops_after_max_rounds(workspace):
    loop = _resp("tool_use", _tool_use("t", "delete_file", {"file_path": "nope"}))
    fake = FakeAnthropic([loop, loop, loop])

    async def go():
        async with await _connected() as mcp:
            return await ClaudeAgent(mcp, anthropic=fake, max_tool_rounds=2).process_query("loop")

    assert "Stopped after 2 tool rounds" in run(go())


def test_conversation_keeps_history(workspace):
    fake = FakeAnthropic([_resp("end_turn", _text("one")), _resp("end_turn", _text("two"))])

    async def go():
        async with await _connected() as mcp:
            await converse(ClaudeAgent(mcp, anthropic=fake), input_fn=feed("first", "second", "q"))

    run(go())
    # Second request carries user, assistant, user.
    assert [m["role"] for m in fake.requests[1]["messages"]] == ["user", "assistant", "user"]


# ------------------------------------------------------------------ features
def test_read_file_and_dir_features(workspace, capsys):
    async def go():
        async with await _connected() as mcp:
            content = await read_file(mcp, input_fn=feed("pkg/mod.py"))
            missing = await read_file(mcp, input_fn=feed("missing.py"))
            items = await read_dir(mcp)
            return content, missing, items

    content, missing, items = run(go())
    assert content == "x = 1\n" and missing is None
    assert {i["name"] for i in items} == {"pkg", "hello.py"}
    assert "is not a valid file" in capsys.readouterr().out


def test_run_prompt_with_elicitation(workspace):
    fake = FakeAnthropic([_resp("end_turn", _text("docs written"))])
    handler = make_elicitation_handler(input_fn=feed("hello.py", "HELLO"))

    async def go():
        async with await _connected(elicitation_handler=handler) as mcp:
            return await run_prompt(mcp, ClaudeAgent(mcp, anthropic=fake), "documentation_generator")

    assert run(go()) == "docs written"
    assert "HELLO" in fake.requests[0]["messages"][0]["content"]


def test_run_prompt_with_arguments(workspace):
    fake = FakeAnthropic([_resp("end_turn", _text("looks good"))])

    async def go():
        async with await _connected() as mcp:
            agent = ClaudeAgent(mcp, anthropic=fake)
            return await run_prompt(mcp, agent, "code_review", input_fn=feed("hello.py"))

    assert run(go()) == "looks good"


def test_menu_dispatch_and_quit(capsys):
    calls = []

    async def action():
        calls.append("hit")

    run(run_menu([MenuItem("1", "Do it", action)], input_fn=feed("9", "1", "quit")))
    out = capsys.readouterr().out
    assert calls == ["hit"] and "Invalid choice" in out and "Exiting client" in out


def test_connect_rejects_bad_script():
    async def go():
        async with MCPClient() as mcp:
            await mcp.connect("server.txt")

    try:
        run(go())
        raise AssertionError("expected ValueError")
    except ValueError as e:
        assert ".py, .js, or .ts" in str(e)


# ----------------------------------------------------------- STDIO end-to-end
def test_stdio_end_to_end_menu():
    """Launch `python client.py server.py`, list the directory, quit."""
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    proc = subprocess.run(
        [sys.executable, "client.py", "server.py"],
        input="4\nq\n", capture_output=True, text=True, cwd=ROOT, env=env, timeout=60,
    )
    assert "MCP Client Started!" in proc.stdout
    assert "Directory Listing" in proc.stdout and "server.py" in proc.stdout
    assert "Exiting client" in proc.stdout
