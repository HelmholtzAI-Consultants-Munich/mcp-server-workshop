# Feature sprint — Track A

## What this repo already is

A **minimal research bot** over PDFs in `papers/`:

1. **Discover** — list available PDFs  
2. **Select** — pick which files matter for the question  
3. **Read** — pull text from those PDFs  
4. **Answer** — produce a short report with citations  

That pipeline lives in **`agent/research_bot.py`**. You run it with **`run_bot.py`**.

Tools are **not** called directly from the bot’s code for file I/O. They go through **MCP servers** — small programs that expose named tools:

| Component | Path | Role |
|-----------|------|------|
| PDF tools | `mcp_servers/pdf_server.py` | `list_pdfs`, `extract_pdf_text`, `search_pdf_text` |
| System tools | `mcp_servers/system_server.py` | `get_current_time` |
| MCP client | `agent/mcp_client.py` | Starts servers, calls tools (usually leave as-is) |
| Prompts | `agent/prompts.py` | LLM prompts for Select / Answer steps |

This is a **simple RAG-shaped** setup: retrieve text from documents, then (optionally) generate an answer.

## What Track A asks you to do

**Do not rebuild the bot from scratch.** The baseline already runs:

```bash
conda activate hackathon-haicon
python run_bot.py --dry-run
```

Track A = **pick one improvement** from the backlog below and implement it by editing the repo — typically:

- a **new or better MCP tool** in `mcp_servers/`, and/or  
- a **change to one step** in `agent/research_bot.py` or `run_bot.py`  

Your feature should plug into the existing four steps (or add a step between them, e.g. ranking before Read).

## Where to look first

| If your task involves… | Start here |
|------------------------|------------|
| New PDF tool (A1, A2, A5) | `mcp_servers/pdf_server.py` |
| Bot logic / pipeline (A3, A4, A8) | `agent/research_bot.py`, `run_bot.py` |
| Tests (A7) | `mcp_servers/_paths.py`, new file under `tests/` |
| Sample data (A5) | `papers/manifest.json` (you create) |

Pick one task; get facilitator sign-off if unsure about scope.

| ID | Size | Task |
|----|------|------|
| A1 | S | `search_pdf_text(query)` — keyword scan over extracted text |
| A2 | S | `summarize_pdf(filename)` — single LLM call, capped input |
| A3 | M | Relevance ranking step before read (embeddings or LLM scores) |
| A4 | M | ReAct agent chooses tools instead of fixed 4-step script |
| A5 | M | `list_papers` from local `papers/manifest.json` |
| A6 | L | Chunk embeddings + k-means clusters in answer |
| A7 | S | Path safety tests for PDF MCP |
| A8 | M | Export answer as Markdown report with timestamp |

No API key needed for **A1, A5, A7, A8**.

---

## Your deliverable (fill in before 1:35)

**Task chosen (ID):**  
**Group members:**  

### Demo command

```bash
# command here
```

### What worked / what didn’t
