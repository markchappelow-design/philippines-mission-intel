import re


def normalize_text_for_compare(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return text


def dedupe_news_items(items: list[dict]) -> list[dict]:
    seen = set()
    deduped = []

    for item in items:
        key = normalize_text_for_compare(
            f"{item.get('title', '')} {item.get('summary', '')[:200]}"
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    return deduped