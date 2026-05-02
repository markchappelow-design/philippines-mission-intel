from pathlib import Path
from docx import Document


def write_docx(report_text: str, output_path: str) -> None:
    doc = Document()
    for block in report_text.split("\n\n"):
        doc.add_paragraph(block.strip())
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)