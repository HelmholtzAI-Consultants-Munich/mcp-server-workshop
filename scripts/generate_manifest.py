#!/usr/bin/env python3
"""Rebuild data/manifest.json from whatever PDFs are in data/.

`list_papers` reads the manifest, not the folder, so a PDF you add yourself is
invisible to it until the manifest knows about it. Run this after adding
papers:

    python scripts/generate_manifest.py

Entries already in the manifest keep their curated title, authors, year and
tags. New PDFs get a title derived from the filename, because the /Title in a
publisher's PDF is usually a typesetting id such as "15341501303742 1..37"
rather than anything readable. Entries whose PDF has gone are dropped.
"""
import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MANIFEST = DATA / "manifest.json"

CURATED = ("title", "authors", "year", "tags")


def _looks_like_a_title(value: str | None) -> bool:
    """A real title, or the typesetter's id that most publishers leave behind."""
    if not value:
        return False
    value = value.strip()
    if len(value.split()) < 3:
        return False
    letters = sum(c.isalpha() for c in value)
    return letters >= len(value) / 2


def title_for(path: Path) -> str:
    try:
        embedded = (PdfReader(str(path)).metadata or {}).get("/Title")
    except Exception:
        embedded = None
    if _looks_like_a_title(str(embedded) if embedded else None):
        return str(embedded).strip()
    words = re.split(r"[-_\s]+", path.stem)
    return " ".join(words).strip().capitalize()


def build(existing: dict[str, dict]) -> list[dict]:
    papers = []
    for path in sorted(DATA.glob("*.pdf")):
        entry = existing.get(path.name)
        if entry and any(entry.get(field) for field in CURATED):
            papers.append(entry)          # curated by hand, leave it alone
            continue
        papers.append({
            "filename": path.name,
            "title": title_for(path),
            "authors": "",
            "year": None,
            "tags": [],
        })
    return papers


def main() -> None:
    existing: dict[str, dict] = {}
    if MANIFEST.is_file():
        try:
            entries = json.loads(MANIFEST.read_text()).get("papers", [])
            existing = {e["filename"]: e for e in entries if "filename" in e}
        except json.JSONDecodeError as exc:
            raise SystemExit(f"data/manifest.json is not valid JSON: {exc}")

    papers = build(existing)
    MANIFEST.write_text(json.dumps({"papers": papers}, indent=2) + "\n")

    kept = sum(1 for p in papers if p["filename"] in existing)
    print(f"{MANIFEST.relative_to(ROOT)}: {len(papers)} papers "
          f"({kept} kept, {len(papers) - kept} added)")
    for name in sorted(set(existing) - {p["filename"] for p in papers}):
        print(f"  dropped {name}: no such PDF")


if __name__ == "__main__":
    main()
