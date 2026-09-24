"""Supplied loop checks use fixed fake adapter outputs, not student answers."""
import asyncio
import copy
import json
from types import SimpleNamespace as Obj
from unittest.mock import AsyncMock

import httpx
import pytest
from openai import APIConnectionError, BadRequestError
from openai.types.chat import ChatCompletion

from agent import agent_loop as loop
from agent.mcp_client import MCPClient, MCPToolError
from mcp.types import CallToolResult, TextContent

SCHEMA = {"type": "function", "function": {"name": "lookup", "description": "Find data",
          "parameters": {"type": "object", "properties": {"query": {"type": "string"}},
                         "required": ["query"]}}}


def response(calls=None, content=None, finish=None):
    return ChatCompletion.model_validate({
        "id": "test", "object": "chat.completion", "created": 0, "model": "fake",
        "choices": [{"index": 0, "finish_reason": finish or ("tool_calls" if calls else "stop"),
                     "message": {"role": "assistant", "content": content, "tool_calls": calls}}]})


def call(identifier="c1", name="lookup", arguments='{"query":"methods"}'):
    return {"id": identifier, "type": "function", "function": {"name": name, "arguments": arguments}}


class Model:
    def __init__(self, *responses):
        self.responses = iter(responses)
        self.requests = []
        self.chat = Obj(completions=Obj(create=self.create))

    async def create(self, **kwargs):
        self.requests.append(copy.deepcopy(kwargs))
        item = next(self.responses)
        if isinstance(item, Exception):
            raise item
        return item


@pytest.fixture
def setup():
    client = Obj(module="test_server")
    tool = Obj(name="lookup", description="Find data", inputSchema=copy.deepcopy(SCHEMA["function"]["parameters"]))
    adapter = Obj(mcp_tools_to_openai_schema=lambda tools: [copy.deepcopy(SCHEMA)],
                  dispatch=AsyncMock(return_value={"text": "evidence"}))
    connected = {"test_server": (client, [tool])}
    return connected, adapter


def run(model, setup, **kwargs):
    connected, adapter = setup
    schemas, owners, inputs = loop.prepare_tools(connected, adapter)
    return asyncio.run(loop.agent_loop("question", model, "fake", schemas, owners, inputs,
                                      adapter_module=adapter, **kwargs))


def test_multiple_rounds_and_multiple_calls_preserve_conversation(setup):
    model = Model(response([call(), call("c2")]), response([call("c3")]), response(content="Answer"))
    trace = []
    assert run(model, setup, trace=trace.append) == "Answer"
    assert setup[1].dispatch.await_count == 3
    messages = model.requests[-1]["messages"]
    assert [m["role"] for m in messages] == ["system", "user", "assistant", "tool", "tool", "assistant", "tool"]
    assert [m["tool_call_id"] for m in messages if m["role"] == "tool"] == ["c1", "c2", "c3"]
    assert json.loads(messages[-1]["content"]) == {"text": "evidence"}
    assert model.requests[0]["messages"][-1] == {"role": "user", "content": "question"}
    assert trace[-1] == "Finished: final answer received"


def test_direct_answer_never_dispatches(setup):
    assert run(Model(response(content="Hello")), setup) == "Hello"
    setup[1].dispatch.assert_not_called()


def test_iteration_cap_counts_requests(setup):
    model = Model(response([call()]), response([call("c2")]))
    with pytest.raises(loop.AgentError, match="Stopped after 2"):
        run(model, setup, max_iterations=2)
    assert len(model.requests) == 2
    assert setup[1].dispatch.await_count == 2


def test_final_answer_on_last_allowed_request(setup):
    assert run(Model(response([call()]), response(content="Done")), setup, max_iterations=2) == "Done"


@pytest.mark.parametrize("bad", [None, {}, [], [{"type": "function"}],
                                 [{"type": "function", "function": {"name": "wrong"}}]])
def test_bad_schema_is_local_adapter_error(setup, bad):
    connected, adapter = setup
    adapter.mcp_tools_to_openai_schema = lambda tools: bad
    with pytest.raises(loop.AgentError, match="agent/adapter.py"):
        loop.prepare_tools(connected, adapter)


def test_duplicate_tool_names_fail_before_adapter(setup):
    connected, adapter = setup
    connected["other"] = connected["test_server"]
    with pytest.raises(loop.AgentError, match="Duplicate tool name"):
        loop.prepare_tools(connected, adapter)


def test_no_tools_is_actionable(setup):
    with pytest.raises(loop.AgentError, match="No MCP tools"):
        loop.prepare_tools({}, setup[1])


@pytest.mark.parametrize("error", [KeyError("absent"), ValueError("not an object"), MCPToolError("invalid path")])
def test_tool_error_becomes_observation_and_model_can_recover(setup, error):
    setup[1].dispatch.side_effect = error
    model = Model(response([call()]), response(content="Could not read"))
    assert run(model, setup) == "Could not read"
    assert "error" in json.loads(model.requests[-1]["messages"][-1]["content"])


def test_unfinished_dispatch_names_student_file(setup):
    setup[1].dispatch.side_effect = NotImplementedError()
    with pytest.raises(loop.AgentError, match="Implement dispatch in agent/adapter.py"):
        run(Model(response([call()])), setup)


def test_nonserializable_dispatch_result(setup):
    setup[1].dispatch.return_value = object()
    with pytest.raises(loop.AgentError, match="JSON-serializable"):
        run(Model(response([call()])), setup)


def test_extra_arguments_are_traced_and_not_filtered(setup):
    raw = '{"query":"test","papers_dir":"../.."}'
    trace = []
    assert run(Model(response([call(arguments=raw)]), response(content="Done")), setup, trace=trace.append) == "Done"
    assert any("undeclared arguments: papers_dir" in line for line in trace)
    assert setup[1].dispatch.call_args.args[0].function.arguments == raw


@pytest.mark.parametrize("reply", [response(), response(content="partial", finish="length"),
                                   response([call(), call()])])
def test_invalid_model_response_fails_clearly(setup, reply):
    with pytest.raises(loop.AgentError):
        run(Model(reply), setup)
    setup[1].dispatch.assert_not_called()


@pytest.mark.parametrize("error,match", [
    (APIConnectionError(request=httpx.Request("POST", "https://example.invalid")), "Cannot reach"),
    (BadRequestError("unsupported", response=httpx.Response(400, request=httpx.Request("POST", "https://example.invalid")), body=None), "HTTP 400")])
def test_api_failures_are_actionable(setup, error, match):
    with pytest.raises(loop.AgentError, match=match):
        run(Model(error), setup)


def test_mcp_error_flag_is_preserved():
    client = MCPClient("fake")
    client.session = Obj(call_tool=AsyncMock(return_value=CallToolResult(
        isError=True, content=[TextContent(type="text", text="Invalid filename")])) )
    with pytest.raises(MCPToolError, match="Invalid filename"):
        asyncio.run(client.call_tool("read", {}))


def test_mcp_success_stays_unchanged():
    client = MCPClient("fake")
    client.session = Obj(call_tool=AsyncMock(return_value=CallToolResult(
        content=[TextContent(type="text", text='{"papers": []}')])) )
    assert asyncio.run(client.call_tool("list")) == {"papers": []}


def test_unfinished_schema_function_is_actionable(setup):
    def unfinished(tools):
        raise NotImplementedError()
    setup[1].mcp_tools_to_openai_schema = unfinished
    with pytest.raises(loop.AgentError, match="mcp_tools_to_openai_schema failed"):
        loop.prepare_tools(setup[0], setup[1])


def test_server_cleanup_after_adapter_failure(monkeypatch, setup):
    closed = []
    async def connect(stack):
        async def close():
            closed.append(True)
        stack.push_async_callback(close)
        return setup[0], {}
    monkeypatch.setattr(loop, "connect_servers", connect)
    setup[1].mcp_tools_to_openai_schema = lambda tools: None
    with pytest.raises(loop.AgentError, match="Invalid"):
        asyncio.run(loop.run_agent("question", adapter_module=setup[1], dry_run=True))
    assert closed == [True]


def test_server_cleanup_after_model_failure(monkeypatch, setup):
    closed = []
    async def connect(stack):
        async def close():
            closed.append(True)
        stack.push_async_callback(close)
        return setup[0], {}
    monkeypatch.setattr(loop, "connect_servers", connect)
    with pytest.raises(loop.AgentError, match="Cannot reach"):
        asyncio.run(loop.run_agent("question", adapter_module=setup[1], client=Model(
            APIConnectionError(request=httpx.Request("POST", "https://example.invalid")))))
    assert closed == [True]


def test_invalid_iteration_cap_never_calls_model(setup):
    model = Model()
    with pytest.raises(loop.AgentError, match="at least 1"):
        run(model, setup, max_iterations=0)
    assert model.requests == []


def test_no_choices_is_actionable(setup):
    reply = response(content="unused")
    reply.choices = []
    with pytest.raises(loop.AgentError, match="no choices"):
        run(Model(reply), setup)


def test_trace_respects_open_argument_schema(setup):
    setup[0]["test_server"][1][0].inputSchema["additionalProperties"] = True
    schema = copy.deepcopy(SCHEMA)
    schema["function"]["parameters"]["additionalProperties"] = True
    setup[1].mcp_tools_to_openai_schema = lambda tools: [schema]
    trace = []
    run(Model(response([call(arguments='{"query":"x","extra":1}')]),
              response(content="Done")), setup, trace=trace.append)
    assert not any("undeclared" in line for line in trace)
