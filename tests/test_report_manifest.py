from app.report_manifest import build_manifest


def test_build_manifest():
    manifest = build_manifest(
        report_timestamp="2026-03-12 00:01:00Z",
        generation_status="complete",
        validation={"ok": True},
        names={"docx_archive": "x.docx"},
        uploaded_files={"latest_docx": {"id": "123"}},
        report_status="complete",
    )
    assert manifest["generation_status"] == "complete"
    assert manifest["report_status"] == "complete"
    assert manifest["uploaded_files"]["latest_docx"]["id"] == "123"