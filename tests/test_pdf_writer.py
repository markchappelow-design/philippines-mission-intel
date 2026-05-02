from app.pdf_writer import write_pdf


def test_write_pdf(tmp_path):
    target = tmp_path / "report.pdf"
    write_pdf("sample report", str(target))
    assert target.exists()
    assert target.stat().st_size > 0