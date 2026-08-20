# Feature sprint, Track A

## What this repo already is

A **minimal research bot** over PDFs in `papers/`:

1. **Discover**, list available PDFs
2. **Select**, pick which files matter for the question
3. **Read**, pull text from those PDFs
4. **Answer**, produce a short report with citations

That pipeline lives in **`agent/research_bot.py`**. You run it with **`run_bot.py`**.

Tools are **not** called directly from the bot's code for file I/O. They go through **MCP servers**, small programs that expose named tools:

| Component | Path | Role |
|-----------|------|------|
| PDF tools | `mcp_servers/pdf_server.py` | `list_pdfs`, `extract_pdf_text`, `search_pdf_text`, `list_papers` |
| System tools | `mcp_servers/system_server.py` | `get_current_time` |
| MCP client | `agent/mcp_client.py` | Starts servers, calls tools (usually leave as-is) |
| Prompts | `agent/prompts.py` | LLM prompts for Select / Answer steps |
| Tool tester | `call_tool.py` | Call one tool on its own, without running the bot |

This is a **simple RAG-shaped** setup: retrieve text from documents, then (optionally) generate an answer.

## What Track A asks you to do

**Do not rebuild the bot from scratch.** The baseline already runs:

```bash
python run_bot.py --dry-run
```

Track A = **pick one improvement** from the backlog below and implement it by editing the repo, typically:

- a **new or better MCP tool** in `mcp_servers/`, and/or
- a **change to one step** in `agent/research_bot.py` or `run_bot.py`

Your feature should plug into the existing four steps, or add a step between them, for example ranking before Read.

## Worked example: `list_papers`

Before you start, read **`list_papers`** in `mcp_servers/pdf_server.py`, together with `papers/manifest.json`. It is a complete, working example of exactly the kind of change Track A asks for: a new MCP tool, about 20 lines, reusing the existing `safe_pdf_path` helper. Run it with:

```bash
python call_tool.py list_papers
```

Most tasks below follow the same shape.

## Testing your change

`run_bot.py` only runs the fixed four-step pipeline, so it will not touch a new tool you have added. Use `call_tool.py` instead:

```bash
python call_tool.py --list                 # did my tool get registered?
python call_tool.py my_new_tool '{"arg": "value"}'
```

Arguments are a single JSON string in single quotes. No API key is needed for either command.

## Where to look first

| If your task involves... | Start here |
|------------------------|------------|
| New or changed PDF tool (A1, A2) | `mcp_servers/pdf_server.py` |
| Bot logic / pipeline (A3, A4, A8) | `agent/research_bot.py`, `run_bot.py` |
| Tests (A7) | `mcp_servers/_paths.py`, new file under `tests/` |

Pick one task; get facilitator sign-off if unsure about scope.

## The backlog

| ID | Size | LLM? | Task | How to test |
|----|------|------|------|-------------|
| A1 | S | no | `search_all_pdfs(query)`, search every PDF at once and return the best matches per file, rather than one file at a time like `search_pdf_text` | `python call_tool.py search_all_pdfs '{"query": "accuracy"}'` |
| A2 | S | yes | `summarize_pdf(filename)`, one LLM call over the extracted text. Cap the input at roughly 6000 characters so you do not blow up the context | `python call_tool.py summarize_pdf '{"filename": "sample_methods.pdf"}'` |
| A3 | M | yes | Relevance ranking step before Read. Ask the model to score each candidate paper, then read only the top ones. Use LLM scoring, not embeddings | `python run_bot.py "What accuracy was reported?"` and check the Select step |
| A4 | M | yes | ReAct agent that chooses tools itself instead of following the fixed four-step script. Cap it at about 3 tool-call iterations so it always terminates | `python run_bot.py "What accuracy was reported?"` and watch which tools it picks |
| A7 | S | no | Path safety tests for the PDF MCP. Cover four cases: a valid file, a traversal attempt with `..`, an absolute path, and a missing file | `pytest tests/` |
| A8 | S | no* | Export the answer as a Markdown report with a timestamp. `get_current_time` already exists, so this is mostly file writing | `python run_bot.py "..."` then open the generated `.md` file |

\* A8 needs a finished answer to export, so the LLM steps have to run first.

## Running without an API key

The LLM steps (Select and Answer) normally call OpenAI, which needs a key. If you do not have one, you can point the bot at a model running on your own machine instead. Install [Ollama](https://ollama.com), pull a model, then put this in `.env`:

```
OPENAI_API_KEY=ollama
OPENAI_MODEL=mistral-nemo:latest
OPENAI_BASE_URL=http://127.0.0.1:11434/v1
```

The whole four-step pipeline then runs locally, at no cost. Note the model download is several GB, so do this before the session rather than on the day.

A1 and A7 need no LLM at all, so they work regardless.

---

## Your deliverable (fill in before 1:35)

**Task chosen (ID):**
**Group members:**

### Demo command

```bash
# command here
```

### What worked / what didn't
