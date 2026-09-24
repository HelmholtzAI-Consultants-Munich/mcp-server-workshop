import json

from mcp.server.fastmcp import FastMCP

from mcp_servers import _pdf
from mcp_servers._paths import PAPERS_DIR, safe_pdf_path

mcp = FastMCP("pdf-server")


@mcp.tool()
def list_pdfs() -> str:
    """List PDF files in the papers directory."""
    root = PAPERS_DIR.resolve()
    if not root.is_dir():
        return json.dumps({"papers": [], "error": f"Directory not found: {root}"})
    entries = sorted(root.glob("*.pdf"), key=lambda p: p.name.lower())
    papers = []
    for path in entries:
        try:
            papers.append(_pdf.pdf_metadata(path))
        except Exception as exc:
            papers.append({"filename": path.name, "error": str(exc)})
    return json.dumps({"papers_dir": str(root), "papers": papers})


@mcp.tool()
def extract_pdf_text(
    filename: str,
    max_pages: int = 5,
    max_chars: int = 12000,
) -> str:
    """Extract text from a PDF (capped by pages and characters)."""
    return json.dumps(_pdf.extract_pdf_text(filename, max_pages, max_chars))


@mcp.tool()
def search_pdf_text(
    filename: str,
    query: str,
    max_pages: int = 10,
) -> str:
    """Return lines from a PDF that contain any query term (case-insensitive)."""
    return json.dumps(_pdf.search_pdf_text(filename, query, max_pages))


@mcp.tool()
def list_papers() -> str:
    """List papers from papers/manifest.json with curated metadata.

    Unlike list_pdfs, which scans the directory, this returns the curated
    catalogue in manifest.json and flags whether each entry's PDF is present.
    """
    root = PAPERS_DIR.resolve()
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        return json.dumps({"papers": [], "error": f"Manifest not found: {manifest_path}"})
    try:
        entries = json.loads(manifest_path.read_text()).get("papers", [])
    except json.JSONDecodeError as exc:
        return json.dumps({"papers": [], "error": f"Invalid manifest.json: {exc}"})
    papers = []
    for entry in entries:
        name = entry.get("filename", "")
        try:
            available = safe_pdf_path(name).is_file()
        except ValueError:
            available = False
        papers.append({**entry, "available": available})
    return json.dumps({"papers_dir": str(root), "papers": papers})


if __name__ == "__main__":
    mcp.run()
