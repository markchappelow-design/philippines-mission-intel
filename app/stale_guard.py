from app.models import SourceItem
from app.freshness import is_item_recent_enough


def classify_stale_items(
    items: list[SourceItem],
    unknown_is_fresh: bool = True,
) -> dict:
    fresh = []
    stale = []

    for item in items:
        if item.fetch_status != "ok":
            continue

        if is_item_recent_enough(
            source_name=item.source_name,
            published_time_utc=item.published_time_utc,
            unknown_is_fresh=unknown_is_fresh,
        ):
            fresh.append(item)
        else:
            stale.append(item)

    return {
        "fresh": fresh,
        "stale": stale,
    }


def stale_summary(items: list[SourceItem]) -> list[str]:
    if not items:
        return ["No stale-source issues identified."]
    return [
        f"Stale source excluded: {item.source_name} | {item.title} | {item.published_time_utc}"
        for item in items[:10]
    ]