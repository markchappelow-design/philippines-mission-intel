from datetime import datetime, timedelta, timezone

import pytest

from freshness.freshness_validator import validate_all_sources, FreshnessValidationError
from sources.source_models import SourceRecord


def test_validate_all_sources_passes_when_all_required_sources_fresh():
    now = datetime.now(timezone.utc)

    records = [
        SourceRecord(
            source_name="PAGASA Weather",
            retrieved_at_utc=now,
            source_timestamp_utc=now - timedelta(hours=1),
            max_age_hours=12,
            required=True,
        ),
        SourceRecord(
            source_name="Embassy Advisory",
            retrieved_at_utc=now,
            source_timestamp_utc=now - timedelta(hours=6),
            max_age_hours=24,
            required=True,
        ),
    ]

    result = validate_all_sources(records, now)
    assert result["ok"] is True
    assert result["sources_checked"] == 2


def test_validate_all_sources_fails_when_required_source_is_stale():
    now = datetime.now(timezone.utc)

    records = [
        SourceRecord(
            source_name="NAIA Operations",
            retrieved_at_utc=now,
            source_timestamp_utc=now - timedelta(hours=9),
            max_age_hours=6,
            required=True,
        )
    ]

    with pytest.raises(FreshnessValidationError) as exc:
        validate_all_sources(records, now)

    assert "Required sources stale" in str(exc.value)


def test_validate_all_sources_allows_optional_source_to_fail():
    now = datetime.now(timezone.utc)

    records = [
        SourceRecord(
            source_name="Optional Feed",
            retrieved_at_utc=now,
            source_timestamp_utc=now - timedelta(hours=50),
            max_age_hours=4,
            required=False,
        )
    ]

    result = validate_all_sources(records, now)
    assert result["ok"] is True
    assert result["failed_optional_count"] == 1