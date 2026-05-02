from app.models import SourceItem


def compute_section_confidence(items: list[SourceItem]) -> str:
    if not items:
        return "Low"

    ok_items = [i for i in items if i.fetch_status == "ok"]
    if not ok_items:
        return "Low"

    tier1_count = sum(1 for i in ok_items if i.reliability_tier == 1)
    tier2_count = sum(1 for i in ok_items if i.reliability_tier == 2)

    if tier1_count >= 2:
        return "High"
    if tier1_count >= 1 or tier2_count >= 2:
        return "Medium"
    return "Low"


def compute_overall_confidence(section_confidences: dict[str, str]) -> str:
    values = list(section_confidences.values())
    if not values:
        return "Low"

    if values.count("Low") >= 4:
        return "Low"
    if values.count("High") >= 4:
        return "High"
    return "Medium"