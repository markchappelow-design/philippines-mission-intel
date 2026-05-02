from app.pdf_writer_reportlab import write_pdf_reportlab


def test_write_pdf_reportlab(tmp_path):
    target = tmp_path / "report.pdf"
    write_pdf_reportlab("Sample report text", str(target))
    assert target.exists()
    assert target.stat().st_size > 0