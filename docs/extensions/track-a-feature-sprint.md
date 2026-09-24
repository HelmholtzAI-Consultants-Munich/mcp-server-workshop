# Track A — Feature sprint

Track A is a small, focused extension of the workshop project. Choose one
task, make the smallest useful change, and demonstrate it before share-out.
The repository already contains a working four-step research pipeline and an
optional tool-calling agent. Do not rebuild either one from scratch.

For this track, extend existing modules only. Add your tests to the named
existing test file rather than creating a new module. Your deliverable includes
the feature, at least two focused tests you wrote, and a passing test command.

## Start here

The project has two kinds of code:

| Component | Path | Role |
|-----------|------|------|
| Student research server | `mcp_servers/research_server.py` | The two tools you write in step 1, and where your extension goes |
| Shipped PDF server | `mcp_servers/pdf_server.py` | Worked MCP examples and low-level PDF tools |
| Shared PDF helpers | `mcp_servers/_pdf.py` | Reusable reading functions; not an MCP server |
| System server | `mcp_servers/system_server.py` | `get_current_time` |
| MCP client | `agent/mcp_client.py` | Discovers servers and calls tools |
| Student adapter | `agent/adapter.py` | Converts schemas and dispatches calls |
| Supplied agent loop | `agent/agent_loop.py` | Runs the model/tool conversation |
| Legacy pipeline | `agent/research_bot.py` | Discover, Select, Read, Answer |
| Tool tester | `call_tool.py` | Lists and calls tools without a model |

Every Python file in `mcp_servers/` whose name does not begin with `_` is
discovered automatically. A helper such as `_pdf.py` is ignored. Use:

```bash
python call_tool.py --list
```

The listing shows each tool's description and the JSON schema generated from
its Python signature and type hints. It also lists static resources,
parameterized resource templates and reusable prompts when a server provides
them.

## Student server and later extensions

`research_server.py` starts with two tools you implement: `save_paper_text`,
which extracts a paper's text and saves it under `output/`, and `list_saved`.
Your extension goes on that same server, so one service grows from a small
example into something useful.

Writes are confined to `output/` by `safe_output_path`, the same way reads are
confined to `data/` by `safe_pdf_path`. Use it for anything that creates a
file: a filename chosen by a model is not a filename you can trust.

When adding PDF features, import functions from `mcp_servers._pdf` instead of
duplicating `pypdf` setup or bypassing the `data/` confinement. PDF readers
take filenames, not a configurable data directory.

## Backlog

| ID | Size | LLM? | Task | How to test |
|----|------|------|------|-------------|
| A1 | S | no | Add `search_all_pdfs(query)` to your research server. Search every PDF and return useful matches grouped by filename. Reuse `_pdf.search_pdf_text` and keep the existing path rules. | `python call_tool.py search_all_pdfs '{"query": "accuracy"}'` |
| A2 | S | yes | Add `summarize_pdf(filename)` to your research server. Read a bounded excerpt through `_pdf.extract_pdf_text`, then make one model call and return the summary. | `python call_tool.py summarize_pdf '{"filename": "sample_methods.pdf"}'` |
| A3 | M | yes | Improve the agent-side selection logic so it ranks candidate papers before Read. This is reasoning in the agent or pipeline, not another MCP tool. | Run the relevant bot command and show which papers were ranked and selected. |
| A4 | M | yes | Add `--trace-file` to the existing agent CLI. Extend `run_bot.py` and `agent/agent_loop.py` so a run writes a JSONL audit trail to `output/`: model request number, tool name, arguments, result status, and result length. Never write API keys, private model reasoning, or full PDF text. Add at least two focused tests to `tests/test_agent_loop.py`. Keep the existing iteration cap and final-answer behavior. | `python run_bot.py --agent --trace-file output/trace.jsonl "What accuracy was reported?"`, then inspect the JSONL file. |
| A5 | S | no | Add `validate_manifest()` to `research_server.py`. It must report duplicate filenames, manifest entries whose PDFs are missing, PDFs absent from the manifest, and malformed entries. It reports problems; it must not rewrite `manifest.json`. Add at least two focused tests to `tests/test_research_server.py`. | `python call_tool.py validate_manifest` |
| A6 | S | no | Write `scripts/generate_manifest.py` so `list_papers` also works for PDFs you brought yourself. Scan `data/`, build an entry per file, and write `manifest.json` in the existing shape. Take the title from the PDF's own metadata where there is one and fall back to the filename, since most PDFs carry no title. Do not discard curated entries that are already there. | `python scripts/generate_manifest.py`, then `python call_tool.py list_papers` lists your own PDFs with `"available": true` |
| A7 | S | no | Add upper bounds for `max_pages` and `max_chars` in the existing `mcp_servers/_pdf.py` helpers, with clear errors when a caller exceeds them. Preserve existing valid behavior, including `max_pages=0`. Update the MCP wrapper descriptions if needed, and add at least two boundary tests to `tests/test_pdf_helpers.py`. | `python call_tool.py extract_pdf_text '{"filename": "sample_methods.pdf", "max_pages": 999}'` reports a clear limit error. |
| A8 | S | no | Add Markdown export as a tool on your research server. Read what `save_paper_text` wrote to `output/`, add a timestamp through the ordinary `current_time_data` helper in `system_server.py`, and write the report back through `safe_output_path`. Do not call the decorated `get_current_time` MCP tool as a normal Python function. Add at least two focused tests to `tests/test_research_server.py`. | `python call_tool.py export_markdown '{"filename": "sample_methods.txt"}'` and inspect the generated report. |
| A9 | S | no | Add one standard MCP extension to your research server with `@mcp.resource()` or `@mcp.prompt()`. Describe what a client receives. | `python call_tool.py --list` shows the resource, template, or prompt; demonstrate one through an MCP client. |
| A10 | stretch | optional | Connect the server to a client such as Claude Desktop, Cursor, or Cline. Document the registration and one successful call. | Show the client configuration and a working tool call. |

## Testing your change

Use `call_tool.py --list` first. It confirms automatic discovery, tool
registration, descriptions, schemas, and any MCP resources or prompts. Then
call a tool directly:

```bash
python call_tool.py my_new_tool '{"arg": "value"}'
```

The legacy pipeline remains:

```bash
python run_bot.py --dry-run
python run_bot.py "What methods are used?"
```

The supplied agent uses the adapter and model endpoint:

```bash
python run_bot.py --agent --trace "What methods are used?"
```

The two exercises have no model or network dependency:

```bash
python -m pytest tests/test_research_server.py -q
python -m pytest tests/test_adapter.py -q
```

Everything that is not an exercise should pass from the start:

```bash
python -m pytest tests/ -m "not exercise" -q
```

No API key is needed for A1, A5, A7, A9, or the direct tool-listing checks.

## Deliverable

**Task chosen (ID):**
**Group members:**

### Demo command

```bash
# command here
```

### What worked / what did not
