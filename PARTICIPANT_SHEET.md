# Agentic workshop hackathon — participant sheet

**2 hours · on the spot · no prep required**

## 1. Get the project

Clone or copy this folder to your laptop.

## 2. Setup (10 min — ask for help if stuck)

```bash
conda env create -f environment.yml
conda activate hackathon-haicon
python scripts/generate_sample_pdfs.py
python run_bot.py --dry-run
```

**No API key needed.** If install fails → join **Track B** (planning, no code).

## 3. Pick one track (your group chooses)

| Track | You do | Open this file |
|-------|--------|----------------|
| **A** Feature | Add one feature from backlog | `FEATURE_BACKLOG_Track_A.md` |
| **B** Architecture | Plan integration into **your project** or **another project** — design only | `DESIGN_PROPOSAL_Track_B.md` |
| **C** Integration | Run `python scripts/integration_demo.py`, write report | `INTEGRATION_Track_C.md` |

Overview: `TRACKS.md`

## 4. Deliverable (due before 1:35)

- **A:** `GROUP_OUTPUT_Track_A.md` + working demo command  
- **B:** completed `DESIGN_PROPOSAL_Track_B.md`  
- **C:** `INTEGRATION_REPORT_Track_C.md`  

## 5. The bot (four steps)

1. **Discover** — list PDFs in `papers/`  
2. **Select** — pick relevant files  
3. **Read** — extract / search text  
4. **Answer** — report with citations  

Code: `run_bot.py`, `agent/research_bot.py`, `mcp_servers/`
