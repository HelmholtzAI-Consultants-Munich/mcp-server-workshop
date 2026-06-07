#!/usr/bin/env python3
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "papers"

SAMPLES = {
    "sample_methods.pdf": (
        "Methods\n\n"
        "We trained a convolutional neural network on 10,000 microscopy images. "
        "Augmentation included random rotations and intensity jitter. "
        "Optimization used Adam with learning rate 1e-4 for 50 epochs."
    ),
    "sample_results.pdf": (
        "Results\n\n"
        "The model achieved 92.3% accuracy on the held-out test set. "
        "Compared to the baseline U-Net, our approach improved F1 by 4.1 points. "
        "Failure cases were mostly dense cell clusters."
    ),
}


def write_pdf(path: Path, body: str) -> None:
    pdf = FPDF()
    pdf.set_margins(20, 20, 20)
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    w = pdf.epw
    for line in body.split("\n"):
        pdf.multi_cell(w, 8, line.strip() or "-")
    pdf.output(str(path))


def main() -> None:
    PAPERS.mkdir(parents=True, exist_ok=True)
    for name, text in SAMPLES.items():
        write_pdf(PAPERS / name, text)
        print(f"wrote {name}")


if __name__ == "__main__":
    main()
