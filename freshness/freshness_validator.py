from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from sources.source_models import SourceRecord


class FreshnessValidationError(Exception):
    pass


def age_hours(now_utc: datetime, source_time_utc: datetime) -> float:
    delta = now_utc - source_time_utc
    return delta.total_seconds() / 3600.0


def evaluate_source_freshness(record: SourceRecord, now_utc: datetime | None = None) -> dict:
    now_utc = now_utc or datetime.now(timezone.utc)

    if record.source_type == "LIVE_FEED":
        reference_time = record.source_timestamp_utc
    else:
        reference_time = record.retrieved_at_utc

    age_h = age_hours(now_utc, reference_time)
    ok = age_h <= record.max_age_hours

    return {
        "source_name": record.source_name,
        "source_type": record.source_type,
        "required": record.required,
        "retrieved_at_utc": record.retrieved_at_utc.isoformat(),
        "source_timestamp_utc": record.source_timestamp_utc.isoformat(),
        "max_age_hours": record.max_age_hours,
        "age_hours": round(age_h, 2),
        "ok": ok,
        "notes": record.notes,
    }


def validate_all_sources(records: Iterable[SourceRecord], now_utc: datetime | None = None) -> dict:
    now_utc = now_utc or datetime.now(timezone.utc)
    results = [evaluate_source_freshness(r, now_utc) for r in records]

    failed_required = [r for r in results if (not r["ok"] and r["required"])]
    failed_optional = [r for r in results if (not r["ok"] and not r["required"])]

    if failed_required:
        names = ", ".join(r["source_name"] for r in failed_required)
        raise FreshnessValidationError(f"Required sources stale: {names}")

    return {
        "ok": True,
        "checked_at_utc": now_utc.isoformat(),
        "sources_checked": len(results),
        "failed_optional_count": len(failed_optional),
        "results": results,
    }