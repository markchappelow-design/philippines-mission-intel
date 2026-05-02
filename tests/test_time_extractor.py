from app.time_extractor import normalize_published_time


def test_normalize_rfc2822():
    value = "Wed, 12 Mar 2026 00:01:00 GMT"
    result = normalize_published_time(value)
    assert result == "2026-03-12 00:01:00Z"