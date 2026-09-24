"""Shared PDF reading for MCP servers.

Helpers return ordinary dictionaries; each server serializes its tool results.
Filename-based helpers always resolve through safe_pdf_path inside papers/.
The leading underscore keeps this module out of server discovery.
"""
from pathlib import Path

from pypdf import PdfReader

from mcp_servers._paths import safe_pdf_path


def pdf_metadata(path: Path) -> dict:
    """Read metadata for a path obtained by scanning the papers directory."""
    reader = PdfReader(str(path))
    return {
        "filename": path.name,
        "size_bytes": path.stat().st_size,
        "page_count": len(reader.pages),
    }


def extract_pdf_text(
    filename: str,
    max_pages: int = 5,
    max_chars: int = 12000,
) -> dict:
    """Extract text from a PDF (capped by pages and characters)."""
    path = safe_pdf_path(filename)
    if not path.is_file():
        return {"error": f"File not found: {filename}"}
    reader = PdfReader(str(path))
    limit = min(max_pages, len(reader.pages))
    chunks = []
    total = 0
    for i in range(limit):
        text = (reader.pages[i].extract_text() or "").strip()
        if not text:
            continue
        block = f"[{path.name} p.{i + 1}]\n{text}"
        total += len(block)
        if total > max_chars:
            block = block[: max(0, max_chars - (total - len(block)))]
            chunks.append(block)
            break
        chunks.append(block)
    return {
        "filename": path.name,
        "pages_read": limit,
        "text": "\n\n".join(chunks),
        "truncated": total > max_chars,
    }


def search_pdf_text(
    filename: str,
    query: str,
    max_pages: int = 10,
) -> dict:
    """Return lines from a PDF that contain any query term (case-insensitive)."""
    path = safe_pdf_path(filename)
    if not path.is_file():
        return {"error": f"File not found: {filename}"}
    terms = {t.lower() for t in query.split() if len(t) > 2}
    reader = PdfReader(str(path))
    hits = []
    for i, page in enumerate(reader.pages[:max_pages]):
        for line in (page.extract_text() or "").splitlines():
            lower = line.lower()
            if terms and not any(t in lower for t in terms):
                continue
            hits.append(f"[{path.name} p.{i + 1}] {line.strip()}")
    return {"filename": path.name, "matches": hits, "text": "\n".join(hits[:80])}
