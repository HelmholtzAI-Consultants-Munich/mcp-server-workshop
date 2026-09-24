# Core tasks: build an MCP server and connect it to an agent

Both core tasks are mandatory. Complete them in order: first build the MCP
tools, then connect those tools to the model.

## Core task 1: build your own MCP server

An MCP server is a program that exposes capabilities to a client through the
Model Context Protocol. Here, the client starts each server as a Python
subprocess and communicates over standard input/output. The client can ask
which tools exist and call them by name with JSON arguments.

### Read a shipped tool

Open `mcp_servers/pdf_server.py` and find `extract_pdf_text`.

- `mcp = FastMCP("pdf-server")` creates the server.
- `@mcp.tool()` registers the function as a callable tool. An ordinary Python
  function without the decorator is not listed as a tool.
- `filename: str` becomes a required string property in the input schema.
- `max_pages: int = 5` becomes an optional integer property with default `5`.
- The function docstring becomes the tool description a model can read.

The server's functions return JSON strings. `MCPClient.call_tool()` decodes
these into Python values for the bot. Listing a tool does not execute it.

### Inspect what the model can see

From the repository root, with your environment activated:

```bash
python call_tool.py --list
python call_tool.py extract_pdf_text '{"filename": "sample_methods.pdf", "max_pages": 1}'
```

No API key is needed. The listing prints each server, its tool names,
descriptions, and input schemas. Compare the printed schema with the Python
signature. There is no `data_dir` input: PDF tools read from the project's
`data/` directory.

### How discovery works

`agent/mcp_client.py` scans `mcp_servers/` for Python files. A server placed
there is discovered automatically; no registration list needs updating.
Server files must be importable and start their MCP server when executed as
modules, using the existing `if __name__ == "__main__": mcp.run()` pattern.

Helpers begin with `_`, so `_paths.py`, `_pdf.py`, and `__init__.py` are
ignored. Actual server filenames do not begin with `_`.

If a server fails, `call_tool.py --list` identifies it while still showing
healthy servers. Read the diagnostic for syntax errors or missing imports.
If the server lists no tools, check the `@mcp.tool()` decorators. Run the
listing again after fixing the file.

### Reuse PDF reading in later tools

`mcp_servers/_pdf.py` contains ordinary functions, with no MCP registration:

- `extract_pdf_text(filename, max_pages=5, max_chars=12000)` returns a dictionary
  with `filename`, `pages_read`, `text`, and `truncated`.
- `search_pdf_text(filename, query, max_pages=10)` returns a dictionary with
  `filename`, `matches`, and `text`.
- `pdf_metadata(path)` reads metadata for a path obtained from the data scan.

The filename-based readers use `_paths.safe_pdf_path()` to reject paths outside
`data/`. They return an `error` dictionary for missing files; invalid paths
raise `ValueError`. Server tools serialize these dictionaries with `json.dumps`.
Import these helpers into later research tools instead of duplicating the
low-level PDF parsing or calling another server's decorated Python functions.

The helper retains the existing extraction conventions: `pages_read` records
the selected page limit, even if the character budget stops extraction early;
blank pages add no text; the character budget counts page blocks before the
separators joining them. Search returns every match in `matches` and the first
80 in `text`. A query with no terms longer than two characters matches all lines.

The existing `run_bot.py` still follows Discover, Select, Read, Answer.
Use `call_tool.py` to exercise a new tool independently of that fixed pipeline.

## Core task 2: connect your tools to the agent

First inspect the MCP schemas with `python call_tool.py --list`.

### Your two functions

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

### Verify without a model

```bash
python run_bot.py --agent --dry-run
```

This starts discovered servers, checks your schema conversion, prints the
schemas, and exits without contacting a model. It does not exercise dispatch;
the adapter tests do. A failed schema conversion names `agent/adapter.py`.

### Run the supplied agent

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

### Test the supplied code

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
