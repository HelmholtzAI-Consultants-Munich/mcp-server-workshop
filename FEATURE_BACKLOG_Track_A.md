# Feature sprint, Track A

Track A is a small, focused extension of the workshop project. Choose one
task, make the smallest useful change, and demonstrate it before share-out.
The repository already contains a working four-step research pipeline and an
optional tool-calling agent. Do not rebuild either one from scratch.

## Start here

The project has two kinds of code:

| Component | Path | Role |
|-----------|------|------|
| Student research server | `mcp_servers/research_server.py` | Your tools and later extensions. Not in this repository yet: it arrives with the workshop starter |
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
its Python signature and type hints.

## Student server and later extensions

The simple starter tools belong in `research_server.py`. Later research
features should extend that same server so students see one service grow from
a small example into a useful research capability.

That starter file and its tests are still being finalized with the facilitator
and are not in this repository yet. The tasks below describe what you add to
it once it arrives; everything else here works today.

When adding PDF features, import functions from `mcp_servers._pdf` instead of
duplicating `pypdf` setup or bypassing the `papers/` confinement. PDF readers
take filenames, not a configurable papers directory.

## Backlog

| ID | Size | LLM? | Task | How to test |
|----|------|------|------|-------------|
| A1 | S | no | Add `search_all_pdfs(query)` to your research server. Search every PDF and return useful matches grouped by filename. Reuse `_pdf.search_pdf_text` and keep the existing path rules. | `python call_tool.py search_all_pdfs '{"query": "accuracy"}'` |
| A2 | S | yes | Add `summarize_pdf(filename)` to your research server. Read a bounded excerpt through `_pdf.extract_pdf_text`, then make one model call and return the summary. | `python call_tool.py summarize_pdf '{"filename": "sample_methods.pdf"}'` |
| A3 | M | yes | Improve the agent-side selection logic so it ranks candidate papers before Read. This is reasoning in the agent or pipeline, not another MCP tool. | Run the relevant bot command and show which papers were ranked and selected. |
| A4 | M | yes | Extend the supplied agent behavior with a visible tool/action trace or another bounded ReAct improvement. Keep the termination condition and iteration cap. Do not expose private model chain-of-thought. | `python run_bot.py --agent --trace "What accuracy was reported?"` |
| A5 | S | no | Study and improve the shipped `list_papers` worked example. Keep curated manifest metadata separate from directory scanning and preserve the `available` flag. | `python call_tool.py list_papers` |
| A7 | S | no | Add or extend path-safety tests for `safe_pdf_path`: valid filename, `..` traversal, absolute path, and missing file. | `python -m pytest tests/ --ignore=tests/test_adapter.py -q` |
| A8 | S | no* | Add Markdown export as a tool on your research server. Include the finished answer and a timestamp from `get_current_time`; write only inside the project output area. | `python call_tool.py export_markdown '{"...": "..."}'` and inspect the generated report. |
| A9 | S | no | Add one standard MCP extension to your research server with `@mcp.resource()` or `@mcp.prompt()`. Describe what a client receives. | `python call_tool.py --list` and demonstrate the extension through the MCP client. |
| A10 | stretch | optional | Connect the server to a client such as Claude Desktop, Cursor, or Cline. Document the registration and one successful call. | Show the client configuration and a working tool call. |

\* A8 needs a finished answer, so the model steps must run first. Confirm the
export function's exact arguments from the starter specification before coding.

## Testing your change

Use `call_tool.py --list` first. It confirms automatic discovery, registration,
the description, and the schema. Then call the tool directly:

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

The adapter specification has no model or network dependency:

```bash
python -m pytest tests/test_adapter.py -q
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
