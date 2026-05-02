from app.models import SourceItem


def get_generation_status(items: list[SourceItem]) -> str:
    critical_failures = [
        item for item in items
        if getattr(item, "fetch_status", "ok") != "ok" and item.source_name in {
            "US Embassy Manila",
            "US State Department Philippines Travel Advisory",
            "PAGASA",
            "PHIVOLCS",
        }
    ]
    return "degraded" if critical_failures else "complete"