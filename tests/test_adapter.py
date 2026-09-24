"""Executable student specification. These fail until the two stubs are solved.

Run: python -m pytest tests/test_adapter.py
No model, network, real MCP server, or API key is involved.
"""
import asyncio
import copy
import json
from types import SimpleNamespace as Obj
from unittest.mock import AsyncMock

import pytest


pytestmark = pytest.mark.exercise


def test_schema_preserves_names_descriptions_and_nested_parameters(adapter_impl):
    parameters = {"type": "object", "properties": {
        "filename": {"type": "string"},
        "options": {"type": "object", "properties": {
            "pages": {"type": "integer", "default": 5}}, "required": ["pages"]}},
        "required": ["filename"], "additionalProperties": False}
    tools = [Obj(name="read", description="Read a paper", inputSchema=parameters),
             Obj(name="clock", description=None, inputSchema={"type": "object", "properties": {}})]
    before = copy.deepcopy(tools)
    assert adapter_impl.mcp_tools_to_openai_schema(tools) == [
        {"type": "function", "function": {"name": "read", "description": "Read a paper",
                                            "parameters": parameters}},
        {"type": "function", "function": {"name": "clock", "description": "",
                                            "parameters": {"type": "object", "properties": {}}}}]
    assert tools == before


def test_empty_schema_list(adapter_impl):
    assert adapter_impl.mcp_tools_to_openai_schema([]) == []


@pytest.mark.parametrize("payload", [{"text": "Grüße", "count": 2}, {}])
def test_dispatch_awaits_only_the_owner_and_preserves_result(adapter_impl, payload):
    result = {"matches": ["paper p.1"], "count": 1}
    owner = Obj(call_tool=AsyncMock(return_value=result))
    other = Obj(call_tool=AsyncMock())
    owners = {"search": owner, "clock": other}
    call = Obj(id="call_1", function=Obj(name="search", arguments=json.dumps(payload)))
    before = copy.deepcopy(call)
    assert asyncio.run(adapter_impl.dispatch(call, owners)) is result
    owner.call_tool.assert_awaited_once_with("search", payload)
    other.call_tool.assert_not_called()
    assert call == before
    assert owners == {"search": owner, "clock": other}


@pytest.mark.parametrize("raw,error", [("{", json.JSONDecodeError), ("", json.JSONDecodeError),
                                        ("[]", ValueError), ("null", ValueError),
                                        ('"text"', ValueError), ("42", ValueError)])
def test_dispatch_rejects_invalid_arguments_before_calling_client(adapter_impl, raw, error):
    owner = Obj(call_tool=AsyncMock())
    call = Obj(function=Obj(name="search", arguments=raw))
    with pytest.raises(error):
        asyncio.run(adapter_impl.dispatch(call, {"search": owner}))
    owner.call_tool.assert_not_called()


def test_unknown_tool(adapter_impl):
    owner = Obj(call_tool=AsyncMock())
    call = Obj(function=Obj(name="absent", arguments="{}"))
    with pytest.raises(KeyError):
        asyncio.run(adapter_impl.dispatch(call, {"search": owner}))
    owner.call_tool.assert_not_called()


def test_client_failure_propagates(adapter_impl):
    owner = Obj(call_tool=AsyncMock(side_effect=RuntimeError("server disconnected")))
    call = Obj(function=Obj(name="search", arguments="{}"))
    with pytest.raises(RuntimeError, match="server disconnected"):
        asyncio.run(adapter_impl.dispatch(call, {"search": owner}))
