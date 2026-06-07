# Integration experiments — Track C

**You do not need IDE or MCP setup knowledge.**

## Run (terminal only)

```bash
conda activate hackathon-haicon
cd agentic-workshop-hackathon
python scripts/integration_demo.py
```

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

## Test queries (used by integration_demo.py)

1. What methods are used?
2. What accuracy was reported?
3. What optimization hyperparameters are mentioned?
4. What failure cases are described?

---

## Optional stretch

Wire MCP into VS Code, Cursor, or Claude Desktop — **not required**.

<details>
<summary>IDE MCP config</summary>

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

</details>

---

## Your deliverable (fill in before 1:35)

| Query | Pass/Fail | What happened |
|-------|-----------|---------------|
| | | |

### Top 3 problems

1.  
2.  
3.  

### One fix to suggest

### Optional: paste `integration_demo.py` output below
