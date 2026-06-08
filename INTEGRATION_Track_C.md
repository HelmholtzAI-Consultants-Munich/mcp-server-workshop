# Integration experiments — Track C

**You do not need IDE or MCP setup knowledge.**  
Track C is about **finding where the system breaks**, not building a large feature. Follow the phases below (~60 min hands-on).

---

## How this relates to the project

| Layer | What Track C tests |
|-------|-------------------|
| `mcp_servers/pdf_server.py` | Do `list_pdfs` and `search_pdf_text` return useful results? |
| `agent/mcp_client.py` | Can tools be called reliably from Python? |
| `run_bot.py` / full bot | (Phase 3) Does the end-to-end path behave differently from calling tools directly? |

Track A **builds** features. Track B **plans** architecture elsewhere. Track C **stress-tests** what already exists.

---

## Phase 1 — Baseline run (~15 min)

```bash
conda activate hackathon-haicon
cd agentic-workshop-hackathon
python scripts/integration_demo.py
```

For each bundled query, note **PASS/FAIL** in your deliverable (bottom of this file). Paste the terminal output there.

Bundled queries:

1. What methods are used?
2. What accuracy was reported?
3. What optimization hyperparameters are mentioned?
4. What failure cases are described?

---

## Phase 2 — Your own queries (~15 min)

Add **at least 3 questions** — ideally one per group member’s domain. Try them against sample PDFs or PDFs you brought.

```bash
python -c "
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from agent.mcp_client import MCPClient
async def main():
    async with MCPClient('mcp_servers.pdf_server') as c:
        r = await c.call_tool('search_pdf_text', {
            'filename': 'sample_methods.pdf', 'query': 'YOUR TERMS'
        })
        print(r)
asyncio.run(main())
"
```

Run from the **project root** (same folder as `run_bot.py`). Or use `python scripts/integration_demo.py` instead.

Also try **`extract_pdf_text`** (full pages vs keyword search). Log which tool worked better per query.

---

## Phase 3 — Compare integration paths (~15 min)

Run the same question through **two paths** and compare:

| Path | Command |
|------|---------|
| Tools only | `integration_demo.py` or one-liner above |
| Full bot (dry) | `python run_bot.py --dry-run` |
| Full bot (optional) | `python run_bot.py "your question"` if you have an API key |

Fill in: *Where do paths agree? Where do they diverge? Which is easier to debug?*

---

## Phase 4 — Analysis (~10 min)

In the deliverable section:

- Top **3 problems** (not just “FAIL” — explain *why*)
- **One concrete fix** (tool change, pipeline change, or doc change)
- Would you trust this in real research? **Yes / not yet / no**

---

## Phase 5 — Stretch if you finish early (~15 min)

Pick **one**:

- Implement your suggested fix (small patch — overlaps with Track A)
- Add your 3 queries to `scripts/integration_demo.py` and re-run
- Try IDE MCP config (optional section below)
- Help another group interpret their failures

---

## Optional: IDE MCP config

Wire MCP into VS Code, Cursor, or Claude Desktop — **not required**.

<details>
<summary>IDE MCP config</summary>

```json
{
  "mcpServers": {
    "haicon-pdf": {
      "command": "/path/to/miniconda3/envs/hackathon-haicon/bin/python",
      "args": ["-m", "mcp_servers.pdf_server"],
      "cwd": "/path/to/agentic-workshop-hackathon"
    }
  }
}
```

</details>

---

## Your deliverable (fill in before 1:35)

### Phase 1 — Bundled queries

| Query | Pass/Fail | What happened |
|-------|-----------|---------------|
| | | |

### Phase 2 — Your queries (≥3)

| Query | Tool used | Pass/Fail | Notes |
|-------|-----------|-----------|-------|
| | | | |

### Phase 3 — Path comparison

**Question tested:**  

**Tools only vs bot:**  

### Top 3 problems

1.  
2.  
3.  

### One fix to suggest (or implement in Phase 5)

### Optional: paste terminal output below
