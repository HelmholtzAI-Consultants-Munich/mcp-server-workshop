#!/usr/bin/env python3
import argparse
import asyncio
import sys
from contextlib import AsyncExitStack
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from agent.mcp_client import connect_servers, owners_of
from agent.research_bot import ResearchBot


async def main(question: str, dry_run: bool) -> int:
    async with AsyncExitStack() as stack:
        connected, failures = await connect_servers(stack)
        for module, exc in failures.items():
            print(f"Warning: {module} failed to start ({exc}); skipping it.")
        owners = owners_of(connected)

        # The pipeline needs a server that can list PDFs and one that can tell
        # the time. Pick them by tool, not by filename, so adding your own
        # server never breaks this.
        pdf, system = owners.get("list_pdfs"), owners.get("get_current_time")
        if pdf is None or system is None:
            missing = [n for n in ("list_pdfs", "get_current_time") if n not in owners]
            print(f"No server provides: {', '.join(missing)}. Run: python call_tool.py --list")
            return 1

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
