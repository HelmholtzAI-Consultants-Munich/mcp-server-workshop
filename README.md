# HAICON26 Agentic RAG Hackathon

A hands-on workshop: MCP servers + a four-step research bot over local PDFs.

## Setup

```bash
conda env create -f environment.yml
conda activate hackathon-haicon
cp .env.example .env   # optional: OPENAI_API_KEY for full LLM run
python scripts/generate_sample_pdfs.py
```

## Run

```bash
python run_bot.py --dry-run
python run_bot.py "What methods are used?"   # needs API key in .env
python scripts/integration_demo.py           # Track C, no API key
```

Add your own PDFs to `papers/`.

## Hackathon tracks

See `PARTICIPANT_SHEET.md` and `TRACKS.md`.

| Track | Focus | Key files |
|-------|--------|-----------|
| A | Feature sprint | `FEATURE_BACKLOG.md` |
| B | Project planning | `templates/DESIGN_PROPOSAL.md` |
| C | Integration test | `INTEGRATION.md`, `scripts/integration_demo.py` |

Deliverables: `GROUP_OUTPUT.md` (A), design proposal (B), `INTEGRATION_REPORT.md` (C).

## Layout

- `mcp_servers/` — PDF and system MCP tools
- `agent/` — MCP client and research bot
- `run_bot.py` — CLI entry point
