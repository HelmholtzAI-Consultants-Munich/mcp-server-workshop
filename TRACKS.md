# Hackathon tracks (2 h, on the spot)

No prep required. Start with `PARTICIPANT_SHEET.md`.

## Track A — Feature sprint

Extend this repo using `FEATURE_BACKLOG.md`. Deliverable: working feature + demo command in `GROUP_OUTPUT.md`.

## Track B — Architecture planning

**No coding.** Plan how to **design a new agentic tool** or **integrate this workshop’s architecture** (MCP tools + phased pipeline) into:

- **your own research project**, or  
- **another project** you know (lab tool, open-source repo, colleague’s system, etc.)

Use this repo as a **reference pattern**, not something you must fork. Deliverable: completed `templates/DESIGN_PROPOSAL.md`.

**Best if install fails or you prefer whiteboard/design work.**

## Track C — Integration experiments

Run `python scripts/integration_demo.py`, document results in `INTEGRATION_REPORT.md`. **No API key required.**

## Setup (first 10 min of the block)

1. `conda activate hackathon-haicon`
2. `cp .env.example .env` (optional — full bot / some Track A tasks only)
3. `python scripts/generate_sample_pdfs.py`
4. `python run_bot.py --dry-run`
5. Track A: `python run_bot.py "What methods are used?"` when you have an API key

## Note on RAG

The baseline bot is a **simple RAG-shaped pipeline** (retrieve excerpts → generate). Track B asks where that pattern belongs in real projects; Tracks A/C build or test it here.
