"""Student exercise: connect MCP tools to Chat Completions tool calling."""
import json
from typing import Any

from mcp.types import Tool

from agent.mcp_client import MCPClient


def mcp_tools_to_openai_schema(tools: list[Tool]) -> list[dict]:
    """Return one Chat Completions function-tool definition per MCP tool.

    Preserve input order. Each entry has type="function" and a function dict
    with name, description (use "" if None), and parameters (the complete
    inputSchema, including required/default/nested fields). Do not mutate tools
    or add strict mode. An empty input returns []. See tests/test_adapter.py.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,
            },
        }
        for tool in tools
    ]


async def dispatch(tool_call: Any, owners: dict[str, MCPClient]) -> Any:
    """Call the owning MCP client and return its decoded result unchanged.

    tool_call has .function.name and .function.arguments (a JSON string).
    Parse arguments as a JSON object, find owners[name], then await that
    client's call_tool(name, arguments). Return the Python result, not a JSON
    string or a model message. Do not mutate owners or tool_call.

    Unknown names raise KeyError. Invalid JSON raises json.JSONDecodeError.
    Valid JSON that is not an object raises ValueError. Client exceptions
    propagate to the supplied loop. Never call a client for invalid arguments.
    """
    name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    if not isinstance(arguments, dict):
        raise ValueError(f"Tool arguments must be a JSON object, got {type(arguments).__name__}")
    return await owners[name].call_tool(name, arguments)
