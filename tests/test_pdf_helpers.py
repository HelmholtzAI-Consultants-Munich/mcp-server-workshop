"""Regression checks for shared reading, independent of the student exercises."""
import asyncio
import json
from contextlib import AsyncExitStack

import pytest
from fpdf import FPDF

from agent.mcp_client import connect_servers, discover_server_modules, owners_of
from mcp_servers import _paths, _pdf, pdf_server


@pytest.fixture
def paper(tmp_path, monkeypatch):
    monkeypatch.setattr(_paths, "PAPERS_DIR", tmp_path)
    monkeypatch.setattr(pdf_server, "PAPERS_DIR", tmp_path)
    path = tmp_path / "example.pdf"
    pdf = FPDF()
    for lines in (["Alpha methods", "Accuracy 92 percent"], [], ["Beta results"]):
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        for line in lines:
            pdf.cell(0, 10, line, new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(path))
    return path


def test_metadata_and_listing(paper):
    expected = {"filename": paper.name, "size_bytes": paper.stat().st_size,
                "page_count": 3}
    assert _pdf.pdf_metadata(paper) == expected
    assert json.loads(pdf_server.list_pdfs())["papers"] == [expected]


def test_extract_preserves_page_labels_and_skips_blank_pages(paper):
    result = _pdf.extract_pdf_text(paper.name)
    assert result == {
        "filename": paper.name, "pages_read": 3, "truncated": False,
        "text": "[example.pdf p.1]\nAlpha methods\nAccuracy 92 percent"
                "\n\n[example.pdf p.3]\nBeta results",
    }
    limited = _pdf.extract_pdf_text(paper.name, max_pages=1)
    assert limited["pages_read"] == 1
    assert "Beta" not in limited["text"]
    assert _pdf.extract_pdf_text(paper.name, max_pages=0)["text"] == ""


def test_character_limit_preserves_existing_truncation_behavior(paper):
    full = _pdf.extract_pdf_text(paper.name, max_pages=1)
    short = _pdf.extract_pdf_text(paper.name, max_chars=20)
    assert short["text"] == full["text"][:20]
    assert short["truncated"] is True
    exact = _pdf.extract_pdf_text(paper.name, max_pages=1,
                                  max_chars=len(full["text"]))
    assert exact == full


def test_search_terms_page_limits_and_no_matches(paper):
    result = _pdf.search_pdf_text(paper.name, "ALPHA beta")
    assert result["matches"] == ["[example.pdf p.1] Alpha methods",
                                  "[example.pdf p.3] Beta results"]
    assert result["text"] == "\n".join(result["matches"])
    assert _pdf.search_pdf_text(paper.name, "beta", max_pages=1)["matches"] == []
    assert _pdf.search_pdf_text(paper.name, "absent")["matches"] == []
    # Existing behavior: a query with no words longer than two characters
    # matches all lines. Keep this refactor behavior-neutral.
    assert len(_pdf.search_pdf_text(paper.name, "a of")["matches"]) == 3


@pytest.mark.parametrize("reader,args", [(_pdf.extract_pdf_text, ()),
                                         (_pdf.search_pdf_text, ("alpha",))])
def test_missing_file_returns_structured_error(paper, reader, args):
    assert reader("missing.pdf", *args) == {"error": "File not found: missing.pdf"}


@pytest.mark.parametrize("reader,args", [(_pdf.extract_pdf_text, ()),
                                         (_pdf.search_pdf_text, ("alpha",))])
def test_shared_readers_reject_escaping_symlink(paper, tmp_path, reader, args):
    link = paper.parent / "escape.pdf"
    link.symlink_to(tmp_path.parent / "outside.pdf")
    with pytest.raises(ValueError, match="Path escapes"):
        reader(link.name, *args)


def test_corrupt_pdf_is_reported_in_listing(paper):
    (paper.parent / "broken.pdf").write_bytes(b"not a PDF")
    papers = json.loads(pdf_server.list_pdfs())["papers"]
    by_name = {entry["filename"]: entry for entry in papers}
    assert "error" in by_name["broken.pdf"]
    assert by_name[paper.name]["page_count"] == 3


def test_four_tools_work_over_mcp_with_unchanged_schema():
    async def scenario():
        assert "mcp_servers._pdf" not in discover_server_modules()
        async with AsyncExitStack() as stack:
            connected, failures = await connect_servers(stack)
            assert not failures
            owners = owners_of(connected)
            tools = connected[owners["list_pdfs"].module][1]
            assert {tool.name for tool in tools} == {
                "list_pdfs", "extract_pdf_text", "search_pdf_text", "list_papers"}
            for tool in tools:
                assert "papers_dir" not in tool.inputSchema["properties"]
            listed = await owners["list_pdfs"].call_tool("list_pdfs")
            assert "sample_methods.pdf" in {p["filename"] for p in listed["papers"]}
            extracted = await owners["extract_pdf_text"].call_tool(
                "extract_pdf_text", {"filename": "sample_methods.pdf"})
            assert "[sample_methods.pdf p.1]" in extracted["text"]
            searched = await owners["search_pdf_text"].call_tool(
                "search_pdf_text", {"filename": "sample_methods.pdf", "query": "methods"})
            assert searched["matches"]
            curated = await owners["list_papers"].call_tool("list_papers")
            assert any(p["available"] for p in curated["papers"])
    asyncio.run(scenario())


# --- write-side confinement ---------------------------------------------------
# safe_output_path is ours, not an exercise: tools that create files depend on
# it, so it is checked here rather than in the student-facing tests.


def test_output_path_resolves_a_plain_filename(tmp_path, monkeypatch):
    monkeypatch.setattr(_paths, "OUTPUT_DIR", tmp_path)
    assert _paths.safe_output_path("notes.txt") == (tmp_path / "notes.txt").resolve()


@pytest.mark.parametrize(
    "hostile",
    ["../escape.txt", "../../etc/passwd", "/etc/passwd", "sub/dir.txt", "..", ""],
)
def test_output_path_rejects_anything_that_escapes(tmp_path, monkeypatch, hostile):
    monkeypatch.setattr(_paths, "OUTPUT_DIR", tmp_path)
    with pytest.raises(ValueError):
        _paths.safe_output_path(hostile)


def test_papers_and_output_stay_separate(tmp_path, monkeypatch):
    monkeypatch.setattr(_paths, "PAPERS_DIR", tmp_path / "papers")
    monkeypatch.setattr(_paths, "OUTPUT_DIR", tmp_path / "output")
    assert _paths.safe_pdf_path("a.pdf").parent.name == "papers"
    assert _paths.safe_output_path("a.txt").parent.name == "output"
