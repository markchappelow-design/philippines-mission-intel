from app.report_status import determine_report_status


def test_determine_report_status_complete():
    assert determine_report_status(True, "complete") == "complete"


def test_determine_report_status_degraded():
    assert determine_report_status(True, "degraded") == "degraded"


def test_determine_report_status_failed():
    assert determine_report_status(False, "complete") == "failed"