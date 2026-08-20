#!/usr/bin/env python3
"""Call a single MCP tool directly, without running the whole bot.

Run from the project root. No API key needed.

    python call_tool.py --list
    python call_tool.py list_pdfs
    python call_tool.py extract_pdf_text '{"filename": "sample_methods.pdf"}'

Use this to test a tool you just added: run --list to confirm the server
registered it, then call it with some arguments and look at the JSON.
"""
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from agent.mcp_client import MCPClient

SERVERS = ["mcp_servers.pdf_server", "mcp_servers.system_server"]


async def tools_of(module: str) -> list[str]:
    async with MCPClient(module) as client:
        listing = await client.session.list_tools()
        return [t.name for t in listing.tools]


async def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    if argv[0] == "--list":
        for module in SERVERS:
            print(f"{module}:")
            for name in await tools_of(module):
                print(f"  {name}")
        return 0

    name, raw_args = argv[0], argv[1] if len(argv) > 1 else "{}"
    try:
        arguments = json.loads(raw_args)
    except json.JSONDecodeError as exc:
        print(f"Arguments are not valid JSON: {exc}", file=sys.stderr)
        print("Remember the single quotes: '{\"filename\": \"a.pdf\"}'", file=sys.stderr)
        return 2

    for module in SERVERS:
        if name not in await tools_of(module):
            continue
        async with MCPClient(module) as client:
            print(json.dumps(await client.call_tool(name, arguments), indent=2))
        return 0

    print(f"No server exposes a tool called '{name}'.", file=sys.stderr)
    print("Run: python call_tool.py --list", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main(sys.argv[1:])))
