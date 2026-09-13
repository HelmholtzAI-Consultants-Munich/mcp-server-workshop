#!/usr/bin/env python3
"""Call a single MCP tool directly, without running the whole bot.

Run from the project root. No API key needed.

    python call_tool.py --list
    python call_tool.py list_pdfs
    python call_tool.py extract_pdf_text '{"filename": "sample_methods.pdf"}'

Use this to test a tool you just added: run --list to confirm the server
registered it and to see the schema the model will read, then call it with
some arguments and look at the JSON.

Servers are found by scanning mcp_servers/, so a server you write yourself
shows up here as soon as the file exists. No registration step.
"""
import asyncio
import json
import sys
from contextlib import AsyncExitStack
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from agent.mcp_client import connect_servers, explain_failure, owners_of


def _print_listing(connected: dict, failures: dict) -> None:
    for module, (_, tools) in connected.items():
        print(f"{module}:")
        if not tools:
            print("  (no tools registered - did you forget @mcp.tool()?)")
        for tool in tools:
            print(f"  {tool.name}")
            if tool.description:
                print(f"      {tool.description.splitlines()[0]}")
            print(f"      schema: {json.dumps(tool.inputSchema)}")
    for module, exc in failures.items():
        print(f"{module}:")
        print(f"  FAILED to start ({exc})")
        print(f"      {explain_failure(module)}")


async def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    async with AsyncExitStack() as stack:
        connected, failures = await connect_servers(stack)

        if argv[0] == "--list":
            _print_listing(connected, failures)
            return 1 if failures else 0

        name, raw_args = argv[0], argv[1] if len(argv) > 1 else "{}"
        try:
            arguments = json.loads(raw_args)
        except json.JSONDecodeError as exc:
            print(f"Arguments are not valid JSON: {exc}", file=sys.stderr)
            print("Remember the single quotes: '{\"filename\": \"a.pdf\"}'", file=sys.stderr)
            return 2

        owners = owners_of(connected)
        client = owners.get(name)
        if client is None:
            print(f"No server exposes a tool called '{name}'.", file=sys.stderr)
            for module, exc in failures.items():
                print(f"Note: {module} failed to start ({exc}).", file=sys.stderr)
            print("Run: python call_tool.py --list", file=sys.stderr)
            return 1

        print(json.dumps(await client.call_tool(name, arguments), indent=2))
        return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main(sys.argv[1:])))
