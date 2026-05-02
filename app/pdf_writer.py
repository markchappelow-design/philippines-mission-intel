from app.pdf_writer_reportlab import write_pdf_reportlab


def write_pdf(report_text: str, output_path: str) -> None:
    write_pdf_reportlab(report_text, output_path)