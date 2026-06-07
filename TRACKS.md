# Hackathon tracks (2 h, on the spot)

No prep required. Start with `PARTICIPANT_SHEET.md`.

## Track A — Feature sprint

Open **`FEATURE_BACKLOG_Track_A.md`**. Pick a task, implement it, fill in the deliverable section at the bottom of the same file.

## Track B — Architecture planning

**No coding.** Open **`DESIGN_PROPOSAL_Track_B.md`**. Plan integration of this workshop’s MCP + phased pipeline into your project or another project you choose. Fill in the same file.

## Track C — Integration experiments

Open **`INTEGRATION_Track_C.md`**. Run `python scripts/integration_demo.py`, fill in the deliverable section at the bottom. **No API key required.**

## Setup (first 10 min)

1. `conda activate hackathon-haicon`
2. `cp .env.example .env` (optional — full bot / some Track A tasks)
3. `python scripts/generate_sample_pdfs.py`
4. `python run_bot.py --dry-run`

## One file per track

| Track | File |
|-------|------|
| A | `FEATURE_BACKLOG_Track_A.md` |
| B | `DESIGN_PROPOSAL_Track_B.md` |
| C | `INTEGRATION_Track_C.md` |
