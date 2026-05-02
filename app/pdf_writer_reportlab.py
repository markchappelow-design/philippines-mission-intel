from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


def write_pdf_reportlab(report_text: str, output_path: str) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=LETTER)
    width, height = LETTER

    x = 50
    y = height - 50
    line_height = 14
    max_width_chars = 95

    def draw_line(line: str, current_y: int) -> int:
        c.drawString(x, current_y, line)
        return current_y - line_height

    for paragraph in report_text.split("\n"):
        text = paragraph.strip()
        if not text:
            y -= line_height
            if y < 50:
                c.showPage()
                y = height - 50
            continue

        while len(text) > max_width_chars:
            chunk = text[:max_width_chars]
            split_at = chunk.rfind(" ")
            if split_at <= 0:
                split_at = max_width_chars

            y = draw_line(text[:split_at], y)
            text = text[split_at:].strip()

            if y < 50:
                c.showPage()
                y = height - 50

        y = draw_line(text, y)

        if y < 50:
            c.showPage()
            y = height - 50

    c.save()