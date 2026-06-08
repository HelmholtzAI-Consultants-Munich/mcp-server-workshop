import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from openai import OpenAI

from agent.mcp_client import MCPClient
from agent.prompts import ANSWER_SYSTEM, SELECT_SYSTEM, answer_user, select_user

load_dotenv(ROOT / ".env", override=True)

PDF_SERVER = "mcp_servers.pdf_server"
SYSTEM_SERVER = "mcp_servers.system_server"


@dataclass
class ResearchBot:
    pdf: MCPClient
    system: MCPClient
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def _client(self) -> OpenAI:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not set")
        return OpenAI(api_key=key)

    async def discover(self) -> list[dict]:
        data = await self.pdf.call_tool("list_pdfs", {})
        return data.get("papers") or []

    async def select(self, question: str, papers: list[dict]) -> list[str]:
        valid = {p["filename"] for p in papers if "filename" in p}
        if not valid:
            return []
        client = self._client()
        resp = client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SELECT_SYSTEM},
                {"role": "user", "content": select_user(question, papers)},
            ],
        )
        payload = json.loads(resp.choices[0].message.content or "{}")
        chosen = [f for f in payload.get("filenames", []) if f in valid]
        return chosen or [next(iter(valid))]

    async def read(self, filenames: list[str]) -> str:
        parts = []
        for name in filenames:
            data = await self.pdf.call_tool(
                "extract_pdf_text", {"filename": name, "max_pages": 5}
            )
            text = data.get("text", "")
            if text:
                parts.append(text)
        return "\n\n".join(parts)

    async def answer(self, question: str, excerpts: str) -> str:
        ts = (await self.system.call_tool("get_current_time", {})).get("iso", "")
        client = self._client()
        resp = client.chat.completions.create(
            model=self.model,
            temperature=0.3,
            messages=[
                {"role": "system", "content": ANSWER_SYSTEM},
                {"role": "user", "content": answer_user(question, excerpts, ts)},
            ],
        )
        return resp.choices[0].message.content or ""

    async def run(self, question: str) -> dict:
        papers = await self.discover()
        if not papers:
            return {"error": "No PDFs in papers/. Add files and retry."}
        selected = await self.select(question, papers)
        excerpts = await self.read(selected)
        if not excerpts.strip():
            return {"error": "No text extracted from selected PDFs."}
        text = await self.answer(question, excerpts)
        return {
            "question": question,
            "selected": selected,
            "papers_found": len(papers),
            "answer": text,
        }


async def _cli(question: str, dry_run: bool) -> int:
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
        print("\n" + (await bot.answer(question, excerpts)))
    return 0


if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description="Mini research bot over local PDFs")
    parser.add_argument("question", nargs="?", default="What methods are used?")
    parser.add_argument("--dry-run", action="store_true", help="List PDFs only")
    args = parser.parse_args()
    os.chdir(ROOT)
    raise SystemExit(asyncio.run(_cli(args.question, args.dry_run)))
