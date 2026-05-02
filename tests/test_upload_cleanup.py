from app.upload_cleanup import classify_upload_mode


def test_classify_upload_mode_failed():
    result = classify_upload_mode(report_status="failed", is_rerun=False)
    assert result["upload_archive"] is False
    assert result["upload_latest"] is False


def test_classify_upload_mode_complete():
    result = classify_upload_mode(report_status="complete", is_rerun=False)
    assert result["upload_archive"] is True
    assert result["upload_latest"] is True