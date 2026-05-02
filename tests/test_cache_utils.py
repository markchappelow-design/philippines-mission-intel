from datetime import datetime, timezone

from sources.cache_utils import read_payload_cache, write_payload_cache
from sources.source_models import SourcePayload


def test_write_and_read_payload_cache_round_trip():
    now = datetime.now(timezone.utc)

    payload = SourcePayload(
        source_name="Test Source",
        section_name="Weather forecast",
        content="Test content",
        retrieved_at_utc=now,
        source_timestamp_utc=now,
        max_age_hours=12,
        required=True,
        notes="test",
        raw_metadata={"a": 1},
    )

    write_payload_cache("test_cache", payload)
    loaded = read_payload_cache("test_cache")

    assert loaded is not None
    assert loaded.source_name == payload.source_name
    assert loaded.section_name == payload.section_name
    assert loaded.content == payload.content
    assert loaded.max_age_hours == payload.max_age_hours