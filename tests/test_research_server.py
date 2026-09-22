"""Spine step 1: the two tools you write in mcp_servers/research_server.py.

These fail in a fresh clone. That is the exercise. Implement the tools until
they pass; do not change the tests to hide a failure.

    python -m pytest tests/test_research_server.py -q
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mcp_servers import _paths

pytestmark = pytest.mark.exercise


@pytest.fixture
def output_dir(tmp_path, monkeypatch, research_server_impl):
    """Point output/ at a temporary folder so tests never touch the real one."""
    target = tmp_path / "output"
    target.mkdir()
    monkeypatch.setattr(_paths, "OUTPUT_DIR", target)
    monkeypatch.setattr(research_server_impl, "OUTPUT_DIR", target, raising=False)
    return target


def test_saves_the_extracted_text_next_to_a_matching_name(research_server_impl, output_dir):
    result = json.loads(research_server_impl.save_paper_text("sample_methods.pdf"))
    assert result["saved"] == "sample_methods.txt"
    assert result["source"] == "sample_methods.pdf"
    assert (output_dir / "sample_methods.txt").is_file()


def test_the_saved_file_holds_the_papers_text(research_server_impl, output_dir):
    research_server_impl.save_paper_text("sample_methods.pdf")
    saved = (output_dir / "sample_methods.txt").read_text(encoding="utf-8")
    assert "Methods" in saved
    assert len(saved) > 50


def test_the_report_counts_what_was_written(research_server_impl, output_dir):
    result = json.loads(research_server_impl.save_paper_text("sample_results.pdf"))
    written = (output_dir / "sample_results.txt").read_text(encoding="utf-8")
    assert result["characters"] == len(written)
    assert result["pages_read"] >= 1


def test_a_missing_paper_is_reported_and_writes_nothing(research_server_impl, output_dir):
    result = json.loads(research_server_impl.save_paper_text("nope.pdf"))
    assert "error" in result
    assert list(output_dir.iterdir()) == []


@pytest.mark.parametrize("hostile", ["../escape.pdf", "/etc/passwd", "../../secrets.pdf"])
def test_a_hostile_filename_never_writes_outside_output(research_server_impl, output_dir, hostile):
    with pytest.raises(ValueError):
        research_server_impl.save_paper_text(hostile)
    assert list(output_dir.iterdir()) == []


def test_list_saved_starts_empty(research_server_impl, output_dir):
    assert json.loads(research_server_impl.list_saved())["saved"] == []


def test_list_saved_reports_what_save_wrote(research_server_impl, output_dir):
    research_server_impl.save_paper_text("sample_methods.pdf")
    research_server_impl.save_paper_text("sample_results.pdf")
    saved = json.loads(research_server_impl.list_saved())["saved"]
    assert {entry["filename"] for entry in saved} == {
        "sample_methods.txt",
        "sample_results.txt",
    }
    assert all(entry["characters"] > 0 for entry in saved)
