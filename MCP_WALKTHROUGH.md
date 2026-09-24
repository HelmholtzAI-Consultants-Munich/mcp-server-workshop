# Understanding the MCP tools

An MCP server is a program that exposes capabilities to a client through the
Model Context Protocol. Here, the client starts each server as a Python
subprocess and communicates over standard input/output. The client can ask
which tools exist and call them by name with JSON arguments.

## Read a shipped tool

Open `mcp_servers/pdf_server.py` and find `extract_pdf_text`.

- `mcp = FastMCP("pdf-server")` creates the server.
- `@mcp.tool()` registers the function as a callable tool. An ordinary Python
  function without the decorator is not listed as a tool.
- `filename: str` becomes a required string property in the input schema.
- `max_pages: int = 5` becomes an optional integer property with default `5`.
- The function docstring becomes the tool description a model can read.

The server's functions return JSON strings. `MCPClient.call_tool()` decodes
these into Python values for the bot. Listing a tool does not execute it.

## Inspect what the model can see

From the repository root, with your environment activated:

```bash
python call_tool.py --list
python call_tool.py extract_pdf_text '{"filename": "sample_methods.pdf", "max_pages": 1}'
```

No API key is needed. The listing prints each server, its tool names,
descriptions, and input schemas. Compare the printed schema with the Python
signature. There is no `papers_dir` input: PDF tools read from the project's
`papers/` directory.

## How discovery works

`agent/mcp_client.py` scans `mcp_servers/` for Python files. A server placed
there is discovered automatically; no registration list needs updating.
Server files must be importable and start their MCP server when executed as
modules, using the existing `if __name__ == "__main__": mcp.run()` pattern.

Helpers begin with `_`, so `_paths.py`, `_pdf.py`, and `__init__.py` are ignored.
Actual server filenames do not begin with `_`.

If a server fails, `call_tool.py --list` identifies it while still showing
healthy servers. Read the diagnostic for syntax errors or missing imports.
If the server lists no tools, check the `@mcp.tool()` decorators. Run the
listing again after fixing the file.

## Reuse PDF reading in later tools

`mcp_servers/_pdf.py` contains ordinary functions, with no MCP registration:

- `extract_pdf_text(filename, max_pages=5, max_chars=12000)` returns a dictionary
  with `filename`, `pages_read`, `text`, and `truncated`.
- `search_pdf_text(filename, query, max_pages=10)` returns a dictionary with
  `filename`, `matches`, and `text`.
- `pdf_metadata(path)` reads metadata for a path obtained from the papers scan.

The filename-based readers use `_paths.safe_pdf_path()` to reject paths outside
`papers/`. They return an `error` dictionary for missing files; invalid paths
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
