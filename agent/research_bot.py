import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI

from agent.mcp_client import MCPClient, ROOT
from agent.prompts import ANSWER_SYSTEM, SELECT_SYSTEM, answer_user, select_user

load_dotenv(ROOT / ".env")

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
