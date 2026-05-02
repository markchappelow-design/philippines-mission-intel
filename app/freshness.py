from datetime import datetime, timedelta, timezone
from app.source_thresholds import get_source_max_age_hours


def is_recent_enough(
    published_time_utc: str,
    max_age_hours: int = 72,
    unknown_is_fresh: bool = True,
) -> bool:
    if published_time_utc == "unknown":
        return unknown_is_fresh

    try:
        dt = datetime.strptime(published_time_utc, "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - dt
        return age <= timedelta(hours=max_age_hours)
    except Exception:
        return unknown_is_fresh


def is_item_recent_enough(source_name: str, published_time_utc: str, unknown_is_fresh: bool = True) -> bool:
    max_age_hours = get_source_max_age_hours(source_name)
    return is_recent_enough(
        published_time_utc=published_time_utc,
        max_age_hours=max_age_hours,
        unknown_is_fresh=unknown_is_fresh,
    )