"""Your server. Two tools to write; mcp_servers/pdf_server.py is the reference.

A tool is an ordinary function with @mcp.tool() above it. The type hints become
the JSON schema a model reads, and this docstring becomes the tool description,
so run `python call_tool.py --list` after each change and look at what you made.

Read files only through mcp_servers._pdf, and write only through
safe_output_path, which confines writes to output/ the same way the PDF tools
are confined to data/.

Check your work: python -m pytest tests/test_research_server.py -q
"""
import json

from mcp.server.fastmcp import FastMCP

from mcp_servers._paths import OUTPUT_DIR, safe_output_path
from mcp_servers._pdf import extract_pdf_text

mcp = FastMCP("research-server")


@mcp.tool()
def save_paper_text(filename: str) -> str:
    """Extract the text of a PDF in data/ and save it under output/.

    Takes the PDF's filename only. Extract the text with extract_pdf_text,
    which returns a dict with "text", "filename" and "pages_read", or an
    "error" key when the file is missing. Pass that error straight back.

    Otherwise write the text to output/, named after the PDF with a .txt
    suffix, and return JSON reporting what you saved.
    """
    raise NotImplementedError("Implement save_paper_text in mcp_servers/research_server.py")


@mcp.tool()
def list_saved() -> str:
    """List the text files saved in output/ so far.

    Return JSON with one entry per .txt file in OUTPUT_DIR. No arguments: the
    directory is fixed, never something a caller can choose.
    """
    raise NotImplementedError("Implement list_saved in mcp_servers/research_server.py")


if __name__ == "__main__":
    mcp.run()
