# Agentic workshop hackathon — participant sheet

**2 hours · on the spot · no prep required**

## 1. Get the project

Copy `agentic-workshop-hackathon` from USB / AirDrop / shared link to your laptop.

## 2. Setup (10 min — ask for help if stuck)

```bash
cd agentic-workshop-hackathon
conda env create -f environment.yml
conda activate hackathon-haicon
python scripts/generate_sample_pdfs.py
python run_bot.py --dry-run
```

**No API key needed.** If install fails → join **Track B** (planning, no code).

## 3. Pick one track (your group chooses)

| Track | You do | File to open |
|-------|--------|--------------|
| **A** Feature | Add one feature from backlog | `FEATURE_BACKLOG.md` |
| **B** Plan | Design an agent for your science | `templates/DESIGN_PROPOSAL.md` |
| **C** Integration | Run `python scripts/integration_demo.py`, write `INTEGRATION_REPORT.md` | `INTEGRATION.md` |

Details: `TRACKS.md`

## 4. Deliverable (due before 1:35)

- **A:** `GROUP_OUTPUT.md` + working demo command  
- **B:** completed design proposal  
- **C:** `INTEGRATION_REPORT.md`  

## 5. The bot (four steps)

1. **Discover** — list PDFs in `papers/`  
2. **Select** — pick relevant files  
3. **Read** — extract / search text  
4. **Answer** — report with citations  

Code: `run_bot.py`, `agent/research_bot.py`, `mcp_servers/`
