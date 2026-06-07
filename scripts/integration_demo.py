#!/usr/bin/env python3
"""Track C demo — no IDE MCP config needed. Run from project root."""

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent.mcp_client import MCPClient

QUERIES = [
    ("What methods are used?", "sample_methods.pdf", "methods training"),
    ("What accuracy was reported?", "sample_results.pdf", "accuracy"),
    ("Hyperparameters?", "sample_methods.pdf", "Adam learning"),
    ("Failure cases?", "sample_results.pdf", "failure"),
]


async def main() -> int:
    print("=== Track C integration demo (terminal only) ===\n")
    async with MCPClient("mcp_servers.pdf_server") as pdf:
        listing = await pdf.call_tool("list_pdfs", {})
        papers = listing.get("papers") or []
        print("1. list_pdfs")
        for p in papers:
            print(f"   {p.get('filename')} ({p.get('page_count', '?')} pages)")
        print()

        for question, filename, search in QUERIES:
            print(f"Query: {question}")
            data = await pdf.call_tool(
                "search_pdf_text", {"filename": filename, "query": search}
            )
            hits = data.get("matches") or []
            status = "PASS" if hits else "FAIL"
            print(f"  search_pdf_text → {status} ({len(hits)} hits)")
            for line in hits[:3]:
                print(f"    {line[:100]}")
            print()

    print("Done. Fill in the deliverable section at the bottom of INTEGRATION_Track_C.md")
    print("Note any FAIL rows and why (wrong file, no matches, etc.).")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
