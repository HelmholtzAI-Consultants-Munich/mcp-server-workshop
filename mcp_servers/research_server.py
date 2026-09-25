"""Reference answer for the starter server. Facilitator copy, not shipped."""
import json

from mcp.server.fastmcp import FastMCP

from mcp_servers._paths import OUTPUT_DIR, safe_output_path
from mcp_servers._pdf import extract_pdf_text

mcp = FastMCP("research-server")


@mcp.tool()
def save_paper_text(filename: str) -> str:
    """Extract the text of a paper in data/ and save it under output/."""
    extracted = extract_pdf_text(filename)
    if "error" in extracted:
        return json.dumps(extracted)
    target = safe_output_path(f"{filename.rsplit('.', 1)[0]}.txt")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(extracted["text"], encoding="utf-8")
    return json.dumps(
        {
            "saved": target.name,
            "source": extracted["filename"],
            "pages_read": extracted["pages_read"],
            "characters": len(extracted["text"]),
        }
    )


@mcp.tool()
def list_saved() -> str:
    """List the text files saved in output/ so far."""
    root = OUTPUT_DIR.resolve()
    if not root.is_dir():
        return json.dumps({"saved": []})
    files = sorted(p for p in root.glob("*.txt"))
    return json.dumps(
        {
            "output_dir": str(root),
            "saved": [
                {"filename": p.name, "characters": len(p.read_text(encoding="utf-8"))}
                for p in files
            ],
        }
    )


if __name__ == "__main__":
    mcp.run()
