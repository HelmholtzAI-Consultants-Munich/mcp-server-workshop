SELECT_SYSTEM = """You pick PDF filenames relevant to a research question.
Return JSON only: {"filenames": ["a.pdf"], "rationale": "brief reason"}.
Pick at most 2 files from the provided list. Use exact filenames."""

ANSWER_SYSTEM = """You answer scientific questions using only the provided excerpts.
Cite sources as [filename p.N]. If evidence is insufficient, say so clearly."""


def select_user(question: str, papers: list[dict]) -> str:
    lines = [f"Question: {question}", "", "Available PDFs:"]
    lines.extend(
        f"- {p['filename']} ({p.get('page_count', '?')} pages)" for p in papers
    )
    return "\n".join(lines)


def answer_user(question: str, excerpts: str, timestamp: str) -> str:
    return (
        f"Question: {question}\n\n"
        f"Report generated at: {timestamp}\n\n"
        f"Excerpts:\n{excerpts}"
    )
