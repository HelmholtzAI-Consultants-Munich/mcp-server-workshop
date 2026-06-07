# Hackathon tracks (2 h, on the spot)

No prep required. Your facilitator will distribute this folder in the room. Start with `PARTICIPANT_SHEET.md`.

## Track A — Feature sprint

Extend this repo using `FEATURE_BACKLOG.md`. Deliverable: working feature + demo command in `GROUP_OUTPUT.md`.

## Track B — Project planning

Fill in `templates/DESIGN_PROPOSAL.md` for an agentic tool in your domain. No coding required. **Best if API setup fails.**

## Track C — Integration experiments

Follow `INTEGRATION.md`: wire MCP servers (any IDE, extension, or terminal), run test queries, write `INTEGRATION_REPORT.md`. **Dry-run works without API key.**

## Setup (first 10 min of the block)

1. `conda activate hackathon-haicon`
2. `cp .env.example .env` and set API key (A and full bot only)
3. `python scripts/generate_sample_pdfs.py`
4. `python run_bot.py --dry-run`
5. Track A/C: `python run_bot.py "What methods are used?"` when key works

## Note on RAG

The baseline bot is a **simple RAG-shaped pipeline** (retrieve excerpts → generate). Tracks A/C improve or stress-test that; Track B designs what belongs beyond retrieval.
