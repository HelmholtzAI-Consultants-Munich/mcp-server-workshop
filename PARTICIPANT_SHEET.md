# Agentic workshop hackathon — participant sheet

**2 hours · on the spot · no prep required**

## 1. Get the project

Clone or copy this folder to your laptop.

## 2. Setup (10 min — ask for help if stuck)

```bash
cd haicon26-agentic-rag-hackathon   # must be in project root
conda env create -f environment.yml
conda activate hackathon-haicon
python scripts/generate_sample_pdfs.py
python run_bot.py --dry-run
```

No conda? Replace the two conda lines with:

```bash
python3 --version              # must be 3.11 or newer
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

If `python3 --version` is older than 3.11, install a supported Python version
from [python.org](https://www.python.org/downloads/) and repeat the setup.

**`ModuleNotFoundError: No module named 'agent'`** → you are not in the project root. `cd` into the cloned folder first.

**No API key is needed for setup, tool discovery, or the no-LLM tasks.** If
install fails, ask for help or choose **Track B** (no code).

## 3. The three steps everyone does

Read `MCP_WALKTHROUGH.md` first. Then work through these in order.

**Step 1 - write your server.** Open `mcp_servers/research_server.py` and
implement its two tools. `save_paper_text` extracts a paper's text and saves it
under `output/`; `list_saved` says what is there. A tool is an ordinary Python
function with `@mcp.tool()` above it. `mcp_servers/pdf_server.py` is a working
reference to copy the shape from.

```bash
python -m pytest tests/test_research_server.py -q
```

**Step 2 - look at what you made.**

```bash
python call_tool.py --list
```

Find your two tools. Next to each is a JSON schema you never wrote: it was
generated from your type hints, and the description is your docstring. That
schema is exactly what a model is shown when it decides which tool to use.

Servers under `mcp_servers/` are discovered automatically, with no registration
step. Files whose names begin with `_` are helpers and are skipped.

**Step 3 - let the model choose.** Complete the two functions in
`agent/adapter.py`, following `AGENT_EXERCISE.md`. They translate between MCP's
description of a tool and what the model's API expects, then route the model's
chosen call to the server that owns it. The loop in `agent/agent_loop.py` is
provided.

```bash
python -m pytest tests/test_adapter.py -q
python run_bot.py --agent --trace "What methods are used?"
```

Both exercises ship with failing tests. That is the point: they pass when you
are done. Everything that is not an exercise should already pass:

```bash
python -m pytest tests/ -m "not exercise" -q
```

The original four-step pipeline stays available through `python run_bot.py`.

## 4. Then pick one extension - one file each

| Track | Open this file |
|-------|----------------|
| **A** Feature sprint | `FEATURE_BACKLOG_Track_A.md` |
| **B** Architecture planning | `DESIGN_PROPOSAL_Track_B.md` |
| **C** Integration experiments | `INTEGRATION_Track_C.md` |

Overview: `TRACKS.md`

## 5. Deliverable

Fill in the **“Your deliverable”** section at the bottom of your track file before 1:35.

## 6. The existing bot (four steps)

1. **Discover** — list PDFs in `papers/`  
2. **Select** — pick relevant files  
3. **Read** — extract / search text  
4. **Answer** — report with citations  

Code: **`python run_bot.py`** from project root (or `python agent/research_bot.py`, or `python -m agent.research_bot`)
