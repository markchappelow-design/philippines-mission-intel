import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from sources.source_models import SourcePayload


CACHE_DIR = Path("cache")


def ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def cache_path_for(source_key: str) -> Path:
    ensure_cache_dir()
    return CACHE_DIR / f"{source_key}.json"


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
        required=data.get("required", True),
        notes=data.get("notes", ""),
        raw_metadata=data.get("raw_metadata", {}),
    )


def write_payload_cache(source_key: str, payload: SourcePayload) -> None:
    path = cache_path_for(source_key)
    path.write_text(
        json.dumps(_serialize_payload(payload), indent=2),
        encoding="utf-8",
    )


def read_payload_cache(source_key: str) -> SourcePayload | None:
    path = cache_path_for(source_key)
    if not path.exists():
        return None

    data = json.loads(path.read_text(encoding="utf-8"))
    return _deserialize_payload(data)