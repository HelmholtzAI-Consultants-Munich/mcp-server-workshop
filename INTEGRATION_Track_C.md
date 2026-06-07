# Integration guide — Track C

**You do not need IDE or MCP setup knowledge.**

## Required (terminal only)

```bash
conda activate hackathon-haicon
cd agentic-workshop-hackathon
python scripts/integration_demo.py
```

Copy the output into `INTEGRATION_REPORT_Track_C.md`. For each query, note PASS/FAIL and why.

Add two questions of your own (change the script or run manually):

```bash
python -c "
import asyncio
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

## Deliverable

Fill in `INTEGRATION_REPORT_Track_C.md`:

| Query | Pass/Fail | What happened |
|-------|-----------|---------------|
| | | |

Plus: top 3 problems, one fix you’d suggest.

---

## Optional stretch (skip if confusing)

Wire MCP into VS Code, Cursor, or Claude Desktop — see paths below. **Not required for Track C.**

<details>
<summary>VS Code / Cursor / Claude Desktop MCP config</summary>

Project root as `cwd`, Python from `hackathon-haicon`:

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

Paste into your editor’s MCP settings. If it doesn’t work, stay on terminal path above.

</details>

## Test queries (used by integration_demo.py)

1. What methods are used?
2. What accuracy was reported?
3. What optimization hyperparameters are mentioned?
4. What failure cases are described?
