from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"


def _confined(filename: str, base: Path) -> Path:
    """Resolve a bare filename inside base, rejecting anything that escapes it.

    The base is chosen by the code, never by a tool argument. That distinction
    is the whole point: a caller-supplied directory is how the PDF tools used
    to be talked out of the data folder.
    """
    base = base.resolve()
    name = Path(filename).name
    if not name or name != filename or ".." in Path(filename).parts:
        raise ValueError(f"Invalid filename: {filename}")
    path = (base / name).resolve()
    if base not in path.parents and path != base:
        raise ValueError(f"Path escapes {base.name} directory: {filename}")
    return path


def safe_pdf_path(filename: str) -> Path:
    """Resolve a filename inside data/, rejecting anything that escapes it."""
    return _confined(filename, DATA_DIR)


def safe_output_path(filename: str) -> Path:
    """Resolve a filename inside output/, rejecting anything that escapes it.

    The write-side counterpart of safe_pdf_path. Tools that create files use
    this so a filename coming from a model cannot place one anywhere else.
    """
    return _confined(filename, OUTPUT_DIR)
