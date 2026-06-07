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

See `PARTICIPANT_SHEET.md` and `TRACKS.md`. **One file per track:**

| Track | File |
|-------|------|
| A | `FEATURE_BACKLOG_Track_A.md` |
| B | `DESIGN_PROPOSAL_Track_B.md` |
| C | `INTEGRATION_Track_C.md` |

## Layout

- `mcp_servers/` — PDF and system MCP tools
- `agent/` — MCP client and research bot
- `run_bot.py` — CLI entry point
