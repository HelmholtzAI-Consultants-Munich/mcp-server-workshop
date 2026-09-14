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


async def main(question: str, dry_run: bool, *, agent_mode: bool = False,
               max_iterations: int = 5, trace: bool = False) -> int:
    if agent_mode:
        from agent.agent_loop import AgentError, run_agent
        def report(line):
            if trace or line.startswith("Warning:"):
                print(line)

        try:
            result = await run_agent(
                question, dry_run=dry_run, max_iterations=max_iterations,
                trace=report,
            )
        except AgentError as exc:
            print(f"Agent: {exc}", file=sys.stderr)
            return 1
        print(result)
        return 0
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
    parser.add_argument("--dry-run", action="store_true", help="No model call: list PDFs, or validate agent schemas with --agent")
    parser.add_argument("--agent", action="store_true", help="Use the tool-calling agent (complete agent/adapter.py first)")
    parser.add_argument("--max-iterations", type=int, default=5, help="Maximum model requests in agent mode, including the final answer")
    parser.add_argument("--trace", action="store_true", help="Show agent tool calls and result status")
    args = parser.parse_args()
    if args.max_iterations < 1:
        parser.error("--max-iterations must be at least 1")
    if not args.agent and (args.trace or args.max_iterations != 5):
        parser.error("--trace and --max-iterations require --agent")
    raise SystemExit(asyncio.run(main(args.question, args.dry_run, agent_mode=args.agent,
                                     max_iterations=args.max_iterations, trace=args.trace)))
