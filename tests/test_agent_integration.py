"""Full CLI path, real MCP processes, real SDK, simulated HTTP responses.

Use --adapter-reference PATH once a reference is available locally.
No API key, internet connection, or live model is used.
"""
import asyncio
import json
from pathlib import Path

import httpx
import pytest
from openai import AsyncOpenAI

from agent import adapter, agent_loop
import run_bot


@pytest.fixture
def completed_adapter(request, adapter_impl, monkeypatch):
    if not request.config.getoption("--adapter-reference"):
        pytest.skip("Facilitator end-to-end run requires --adapter-reference PATH")
    monkeypatch.setattr(adapter, "mcp_tools_to_openai_schema", adapter_impl.mcp_tools_to_openai_schema)
    monkeypatch.setattr(adapter, "dispatch", adapter_impl.dispatch)
    return adapter_impl


def completion(message):
    return {"id": "offline", "object": "chat.completion", "created": 0, "model": "offline",
            "choices": [{"index": 0, "finish_reason": "tool_calls" if message.get("tool_calls") else "stop",
                         "message": {"role": "assistant", **message}}]}


def tool_call(identifier, name, arguments):
    return {"id": identifier, "type": "function", "function": {"name": name, "arguments": json.dumps(arguments)}}


def test_cli_agent_reads_real_pdf_and_answers(completed_adapter, monkeypatch, capsys):
    requests = []
    clients = []
    def handler(request):
        payload = json.loads(request.content)
        requests.append(payload)
        assert request.url.path == "/v1/chat/completions"
        assert payload["model"] == "offline"
        if len(requests) == 1:
            names = {t["function"]["name"] for t in payload["tools"]}
            assert {"list_pdfs", "extract_pdf_text", "get_current_time"} <= names
            message = {"tool_calls": [tool_call("list", "list_pdfs", {})]}
        elif len(requests) == 2:
            papers = json.loads(payload["messages"][-1]["content"])["papers"]
            assert "sample_methods.pdf" in {p["filename"] for p in papers}
            message = {"tool_calls": [
                tool_call("read", "extract_pdf_text", {"filename": "sample_methods.pdf"}),
                tool_call("clock", "get_current_time", {})]}
        else:
            assert len(requests) == 3
            results = {m["tool_call_id"]: json.loads(m["content"]) for m in payload["messages"] if m["role"] == "tool"}
            assert "Adam" in results["read"]["text"]
            assert "iso" in results["clock"]
            message = {"content": "Training used Adam [sample_methods.pdf p.1]."}
        return httpx.Response(200, json=completion(message))
    def factory(**kwargs):
        kwargs["http_client"] = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        client = AsyncOpenAI(**kwargs)
        clients.append(client)
        return client
    monkeypatch.setattr(agent_loop, "AsyncOpenAI", factory)
    monkeypatch.setenv("OPENAI_API_KEY", "offline-test-only")
    monkeypatch.setenv("OPENAI_MODEL", "offline")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://offline.invalid/v1")
    assert asyncio.run(run_bot.main("What methods?", False, agent_mode=True, trace=True)) == 0
    out = capsys.readouterr().out
    assert "Training used Adam" in out
    assert "Model request 3/5" in out
    assert len(requests) == 3
    assert clients[0].is_closed()


def test_real_mcp_error_recovery_and_new_server_discovery(completed_adapter):
    from types import SimpleNamespace as Obj
    servers = Path(__file__).resolve().parent.parent / "mcp_servers"
    path = servers / "phase4_test_server.py"
    assert not path.exists()
    path.write_text('''from mcp.server.fastmcp import FastMCP
mcp = FastMCP("phase4")
@mcp.tool()
def phase4_echo(text: str) -> str:
    return text
if __name__ == "__main__":
    mcp.run()
''')
    requests = []
    async def create(**kwargs):
        from openai.types.chat import ChatCompletion
        requests.append(kwargs)
        if len(requests) == 1:
            assert any(t["function"]["name"] == "phase4_echo" for t in kwargs["tools"])
            message = {"tool_calls": [tool_call("bad", "extract_pdf_text", {"filename": "../outside.pdf"})]}
        elif len(requests) == 2:
            assert "error" in json.loads(kwargs["messages"][-1]["content"])
            message = {"tool_calls": [tool_call("echo", "phase4_echo", {"text": "recovered"})]}
        else:
            assert json.loads(kwargs["messages"][-1]["content"]) == {"text": "recovered"}
            message = {"content": "Recovered"}
        return ChatCompletion.model_validate(completion(message))
    try:
        client = Obj(chat=Obj(completions=Obj(create=create)))
        assert asyncio.run(agent_loop.run_agent("test", client=client)) == "Recovered"
    finally:
        path.unlink()
        for cached in (servers / "__pycache__").glob("phase4_test_server.*.pyc"):
            cached.unlink()


def test_agent_dry_run_needs_no_key(completed_adapter, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    schemas = json.loads(asyncio.run(agent_loop.run_agent("test", dry_run=True)))
    assert any(t["function"]["name"] == "list_pdfs" for t in schemas)


def test_missing_key_is_local_error(completed_adapter, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(agent_loop.AgentError, match="Set OPENAI_API_KEY"):
        asyncio.run(agent_loop.run_agent("test"))


def test_legacy_four_step_pipeline_with_real_mcp(monkeypatch, capsys):
    from openai import OpenAI
    from agent.research_bot import ResearchBot
    requests = []
    def handler(request):
        payload = json.loads(request.content)
        requests.append(payload)
        assert "tools" not in payload
        if len(requests) == 1:
            assert payload["response_format"] == {"type": "json_object"}
            content = json.dumps({"filenames": ["sample_methods.pdf"]})
        else:
            assert "Adam" in payload["messages"][-1]["content"]
            content = "Legacy answer [sample_methods.pdf p.1]."
        return httpx.Response(200, json=completion({"content": content}))
    with OpenAI(api_key="offline", http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
        monkeypatch.setattr(ResearchBot, "_client", lambda self: client)
        assert asyncio.run(run_bot.main("What methods?", False)) == 0
    out = capsys.readouterr().out
    for step in ("Step 1", "Step 2", "Step 3", "Step 4", "Legacy answer"):
        assert step in out
    assert len(requests) == 2
