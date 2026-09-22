# Connect your tools to the agent

First inspect the MCP schemas with `python call_tool.py --list`.
See [the MCP walkthrough](MCP_WALKTHROUGH.md) for how these come from Python.

## Your two functions

Complete the two stubs in `agent/adapter.py`:

1. `mcp_tools_to_openai_schema(tools)` converts each MCP tool's name, description,
   and complete input schema into a Chat Completions function-tool definition.
2. Async `dispatch(tool_call, owners)` parses the model's JSON arguments and
   awaits the client that owns that tool. It returns the decoded result.

Read the docstrings and run the executable specification:

```bash
python -m pytest tests/test_adapter.py -q
```

These tests deliberately fail with `NotImplementedError` in the starter clone.
They require no model, API key, or server. Complete both functions and rerun.
Do not change the tests to hide failures.

One deviation from the original specification: `dispatch` returns the decoded
tool result rather than a string. Serializing it is the supplied loop's job,
so participants write no JSON handling on the way out, and the adapter tests
can compare real values instead of formatted text.

## Verify without a model

```bash
python run_bot.py --agent --dry-run
```

This starts discovered servers, checks your schema conversion, prints the
schemas, and exits without contacting a model. It does not exercise dispatch;
the adapter tests do. A failed schema conversion names `agent/adapter.py`.

## Run the supplied agent

Use the same `OPENAI_API_KEY`, `OPENAI_MODEL`, and optional `OPENAI_BASE_URL`
configuration as the existing bot. The endpoint and model must support
Chat Completions `tools` and `tool_calls`. Blablador supports them, which the
facilitator has verified against a live key, so there is no JSON fallback path
and none is needed.

```bash
python run_bot.py --agent --trace --max-iterations 5 "What methods are used?"
```

`agent/agent_loop.py` is supplied complete. It sends the available tools and
question to the model, executes requested tools, appends each result using its
`tool_call_id`, and asks the model again. Multiple calls in a response execute
sequentially. A text answer ends the loop. The cap counts model requests,
including the request that returns the final answer. Reaching it without an
answer reports a failure and exits; tool calls already executed are not undone.

The trace shows requests, tool names, arguments, and result status/length.
It does not request or expose private model reasoning. Undeclared arguments
are reported, since MCP may silently ignore them; the adapter receives the
original arguments. Tool errors become observations the model can respond to.
Duplicate tool names across servers must be renamed before agent mode runs.

The normal commands still run the four-step pipeline:

```bash
python run_bot.py --dry-run
python run_bot.py "What methods are used?"
```

## Test the supplied code

Before completing the adapter, run the infrastructure tests separately:

```bash
python -m pytest tests/ -m "not exercise" -q
```

Full `python -m pytest -q` includes the exercise tests, so a starter clone has
expected failures until you finish the adapter. The facilitator end-to-end
checks explicitly skip unless a local reference is selected. No tests call a
live model. The full pipeline integration check uses the real SDK with
simulated HTTP responses and real MCP servers.

Protocol reference: [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling).
