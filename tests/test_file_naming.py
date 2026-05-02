from datetime import datetime, timezone
from app.file_naming import build_output_names


def test_build_output_names():
    dt = datetime(2026, 3, 12, 0, 1, tzinfo=timezone.utc)
    names = build_output_names(dt)
    assert names["docx_archive"] == "Philippines_Mission_Intel_Status_Report_2026-03-12_0001Z.docx"
    assert names["latest_docx"] == "LATEST - Philippines Mission Intel Status Report.docx"