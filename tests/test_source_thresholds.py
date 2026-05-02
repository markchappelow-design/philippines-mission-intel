from app.source_thresholds import get_source_max_age_hours


def test_get_source_max_age_hours():
    assert get_source_max_age_hours("PAGASA") == 24
    assert get_source_max_age_hours("CDC Travelers Health Philippines") == 720
    assert get_source_max_age_hours("Unknown Source") == 72