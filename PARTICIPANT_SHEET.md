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

**`ModuleNotFoundError: No module named 'agent'`** → you are not in the project root. `cd` into the cloned folder first.

**No API key needed.** If install fails → **Track B** (no code).

## 3. Pick one track — one file each

| Track | Open this file |
|-------|----------------|
| **A** Feature sprint | `FEATURE_BACKLOG_Track_A.md` |
| **B** Architecture planning | `DESIGN_PROPOSAL_Track_B.md` |
| **C** Integration experiments | `INTEGRATION_Track_C.md` |

Overview: `TRACKS.md`

## 4. Deliverable

Fill in the **“Your deliverable”** section at the bottom of your track file before 1:35.

## 5. The bot (four steps)

1. **Discover** — list PDFs in `papers/`  
2. **Select** — pick relevant files  
3. **Read** — extract / search text  
4. **Answer** — report with citations  

Code: **`python run_bot.py`** from project root (or `python agent/research_bot.py`, or `python -m agent.research_bot`)
