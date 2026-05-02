from __future__ import annotations

import hashlib
import json
import traceback
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Callable

from sources.source_models import SourcePayload

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _cache_path(cache_key: str) -> Path:
    """
    Returns a stable cache file path for a given cache key.
    """
    safe_key = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()[:24]
    return CACHE_DIR / f"{safe_key}.json"


def _ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def cache_age_hours(
    source_timestamp_utc: datetime | None,
    now_utc: datetime,
    retrieved_at_utc: datetime | None = None,
) -> float:
    effective_ts = source_timestamp_utc or retrieved_at_utc or now_utc
    age = (now_utc - effective_ts).total_seconds() / 3600.0
    return max(0.0, round(age, 2))


def _serialize_payload(payload: SourcePayload) -> dict:
    data = asdict(payload)
    data["retrieved_at_utc"] = payload.retrieved_at_utc.isoformat()
    data["source_timestamp_utc"] = payload.source_timestamp_utc.isoformat()
    return data


def _deserialize_payload(data: dict) -> SourcePayload:
    return SourcePayload(
        source_name=data["source_name"],
        section_name=data["section_name"],
        content=data["content"],
        retrieved_at_utc=datetime.fromisoformat(data["retrieved_at_utc"]),
        source_timestamp_utc=datetime.fromisoformat(data["source_timestamp_utc"]),
        max_age_hours=data["max_age_hours"],
        required=data["required"],
        notes=data["notes"],
        source_type=data["source_type"],
        raw_metadata=data.get("raw_metadata", {}),
    )


def _write_cache(cache_key: str, payload: SourcePayload) -> None:
    _ensure_cache_dir()
    path = _cache_path(cache_key)
    path.write_text(
        json.dumps(_serialize_payload(payload), indent=2),
        encoding="utf-8",
    )


def _read_cache(cache_key: str) -> SourcePayload | None:
    path = _cache_path(cache_key)
    if not path.exists():
        return None

    data = json.loads(path.read_text(encoding="utf-8"))
    return _deserialize_payload(data)


def _is_cache_fresh(payload: SourcePayload) -> bool:
    now = datetime.now(timezone.utc)
    effective_ts = payload.source_timestamp_utc or payload.retrieved_at_utc or now
    age_hours = max(0.0, (now - effective_ts).total_seconds() / 3600.0)
    return age_hours <= payload.max_age_hours

def fetch_with_cache(cache_key: str, builder: Callable[[], SourcePayload]) -> SourcePayload:
    fallback_reason = "unknown"
    fallback_stage = "unknown"
    fallback_reason_detail = ""

    try:
        payload = builder()

        metadata = payload.raw_metadata or {}
        metadata.update({
            "live_fetch_attempted": True,
            "live_fetch_ok": True,
            "cache_fallback": False,
            "fallback_reason": "",
            "fallback_stage": "",
            "fallback_reason_detail": "",
        })
        payload.raw_metadata = metadata

        _write_cache(cache_key, payload)
        return payload

    except TimeoutError as e:
        print(f"FETCH_WITH_CACHE ERROR [{cache_key}]: {type(e).__name__}: {e}")
        fallback_reason = "timeout"
        fallback_stage = "request"
        fallback_reason_detail = str(e)

    except Exception as e:
        print(f"FETCH_WITH_CACHE ERROR [{cache_key}]: {type(e).__name__}: {e}")
        fallback_reason = type(e).__name__.lower()
        fallback_stage = "unknown"
        fallback_reason_detail = str(e)

    cached = _read_cache(cache_key)

    if cached:
        metadata = cached.raw_metadata or {}
        metadata.update({
            "live_fetch_attempted": True,
            "live_fetch_ok": False,
            "cache_fallback": True,
            "fallback_reason": fallback_reason,
            "fallback_stage": fallback_stage,
            "fallback_reason_detail": fallback_reason_detail,
        })
        cached.raw_metadata = metadata
        return cached

    raise RuntimeError(
        f"Live fetch failed and no cache available for '{cache_key}'. "
        f"reason={fallback_reason} detail={fallback_reason_detail}"
    )