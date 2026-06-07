# HAICON26 Agentic RAG Hackathon

Hands-on mini hackathon for the [Helmholtz Agentic AI Workshop](https://github.com/Helmholtz-AI-Matter/agentic-ai-workshop) at HAICON26.

Build, plan, or stress-test a minimal **PDF research bot**: MCP tools + four steps (Discover → Select → Read → Answer) — a simple RAG pipeline over local files.

**Workshop repo (slides & overview):** [Helmholtz-AI-Matter/agentic-ai-workshop](https://github.com/Helmholtz-AI-Matter/agentic-ai-workshop)

Also at the hackathon: [Abstracts Explorer](https://github.com/thawn/abstracts-explorer) — choose one project for the session.

## Setup

```bash
git clone https://github.com/haider-khan-91/haicon26-agentic-rag-hackathon.git
cd haicon26-agentic-rag-hackathon
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

## Hackathon tracks (pick one)

See `PARTICIPANT_SHEET.md` and `TRACKS.md`.

| Track | Focus | File |
|-------|--------|------|
| **A** Feature sprint | Extend the bot (new MCP tool or pipeline step) | `FEATURE_BACKLOG_Track_A.md` |
| **B** Architecture planning | Plan agentic integration for your or another project — no code | `DESIGN_PROPOSAL_Track_B.md` |
| **C** Integration experiments | Run tests, compare tools vs bot, report failures | `INTEGRATION_Track_C.md` |

Fill in the **deliverable section** at the bottom of your track file before share-out.

## Layout

- `mcp_servers/` — PDF and system MCP tools
- `agent/` — MCP client and research bot
- `run_bot.py` — CLI entry point
