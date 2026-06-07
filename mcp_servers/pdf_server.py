import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pypdf import PdfReader

from mcp_servers._paths import PAPERS_DIR, safe_pdf_path

mcp = FastMCP("pdf-server")


def _pdf_meta(path: Path) -> dict:
    reader = PdfReader(str(path))
    return {
        "filename": path.name,
        "size_bytes": path.stat().st_size,
        "page_count": len(reader.pages),
    }


@mcp.tool()
def list_pdfs(papers_dir: str = "papers") -> str:
    """List PDF files in the papers directory."""
    root = Path(papers_dir)
    if not root.is_absolute():
        root = PAPERS_DIR if papers_dir == "papers" else (PAPERS_DIR.parent / papers_dir)
    root = root.resolve()
    if not root.is_dir():
        return json.dumps({"papers": [], "error": f"Directory not found: {root}"})
    entries = sorted(root.glob("*.pdf"), key=lambda p: p.name.lower())
    papers = []
    for path in entries:
        try:
            papers.append(_pdf_meta(path))
        except Exception as exc:
            papers.append({"filename": path.name, "error": str(exc)})
    return json.dumps({"papers_dir": str(root), "papers": papers})


@mcp.tool()
def extract_pdf_text(
    filename: str,
    max_pages: int = 5,
    max_chars: int = 12000,
    papers_dir: str = "papers",
) -> str:
    """Extract text from a PDF (capped by pages and characters)."""
    root = PAPERS_DIR if papers_dir == "papers" else (PAPERS_DIR.parent / papers_dir).resolve()
    path = safe_pdf_path(filename, root)
    if not path.is_file():
        return json.dumps({"error": f"File not found: {filename}"})
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
    return json.dumps(
        {
            "filename": path.name,
            "pages_read": limit,
            "text": "\n\n".join(chunks),
            "truncated": total > max_chars,
        }
    )


@mcp.tool()
def search_pdf_text(
    filename: str,
    query: str,
    max_pages: int = 10,
    papers_dir: str = "papers",
) -> str:
    """Return lines from a PDF that contain any query term (case-insensitive)."""
    root = PAPERS_DIR if papers_dir == "papers" else (PAPERS_DIR.parent / papers_dir).resolve()
    path = safe_pdf_path(filename, root)
    if not path.is_file():
        return json.dumps({"error": f"File not found: {filename}"})
    terms = {t.lower() for t in query.split() if len(t) > 2}
    reader = PdfReader(str(path))
    hits = []
    for i, page in enumerate(reader.pages[:max_pages]):
        for line in (page.extract_text() or "").splitlines():
            lower = line.lower()
            if terms and not any(t in lower for t in terms):
                continue
            hits.append(f"[{path.name} p.{i + 1}] {line.strip()}")
    return json.dumps({"filename": path.name, "matches": hits, "text": "\n".join(hits[:80])})


if __name__ == "__main__":
    mcp.run()
