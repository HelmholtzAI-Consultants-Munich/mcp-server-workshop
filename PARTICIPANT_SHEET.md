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

## 3. Understand the MCP exercise

Open `MCP_WALKTHROUGH.md`, then inspect the available tools:

```bash
python call_tool.py --list
```

The command shows the names, descriptions, and JSON schemas that a model can
see. Servers under `mcp_servers/` are discovered automatically. Files whose
names begin with `_` are helpers and are ignored.

The supplied agent exercise is documented in `AGENT_EXERCISE.md`. You complete
the two functions in `agent/adapter.py`; the model loop in
`agent/agent_loop.py` is provided. The existing four-step pipeline remains
available through `python run_bot.py`.

## 4. Pick one track - one file each

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
