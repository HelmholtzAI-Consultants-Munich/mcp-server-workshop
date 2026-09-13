from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPERS_DIR = ROOT / "papers"


def safe_pdf_path(filename: str) -> Path:
    """Resolve a filename inside papers/, rejecting anything that escapes it."""
    base = PAPERS_DIR.resolve()
    name = Path(filename).name
    if not name or name != filename or ".." in Path(filename).parts:
        raise ValueError(f"Invalid filename: {filename}")
    path = (base / name).resolve()
    if base not in path.parents and path != base:
        raise ValueError(f"Path escapes papers directory: {filename}")
    return path
