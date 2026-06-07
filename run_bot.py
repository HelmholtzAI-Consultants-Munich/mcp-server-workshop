#!/usr/bin/env python3
import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from agent.mcp_client import MCPClient
from agent.research_bot import ResearchBot

PDF_SERVER = "mcp_servers.pdf_server"
SYSTEM_SERVER = "mcp_servers.system_server"


async def main(question: str, dry_run: bool) -> int:
    async with MCPClient(PDF_SERVER) as pdf, MCPClient(SYSTEM_SERVER) as system:
        bot = ResearchBot(pdf=pdf, system=system)
        print("Step 1 — Discover")
        papers = await bot.discover()
        for p in papers:
            print(f"  {p.get('filename')}: {p.get('page_count', '?')} pages")
        if dry_run:
            return 0
        print("Step 2 — Select")
        selected = await bot.select(question, papers)
        print(f"  {selected}")
        print("Step 3 — Read")
        excerpts = await bot.read(selected)
        print(f"  {len(excerpts)} chars")
        print("Step 4 — Answer")
        result = await bot.answer(question, excerpts)
        print("\n" + result)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mini research bot over local PDFs")
    parser.add_argument("question", nargs="?", default="What methods are used?")
    parser.add_argument("--dry-run", action="store_true", help="List PDFs only")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(main(args.question, args.dry_run)))
