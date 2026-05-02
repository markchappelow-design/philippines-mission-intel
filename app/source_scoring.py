from app.models import SourceItem


def score_source_item(item: SourceItem) -> int:
    score = 0

    if item.fetch_status == "ok":
        score += 2

    if item.reliability_tier == 1:
        score += 5
    elif item.reliability_tier == 2:
        score += 3
    else:
        score += 1

    if item.critical:
        score += 2

    if item.extracted_text and len(item.extracted_text) > 200:
        score += 1

    return score


def sort_items_by_score(items: list[SourceItem]) -> list[SourceItem]:
    return sorted(items, key=score_source_item, reverse=True)