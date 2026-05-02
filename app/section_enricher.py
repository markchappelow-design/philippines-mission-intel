from app.confidence import compute_section_confidence
from app.section_mapper import REQUIRED_HEADINGS, map_items_to_sections
from app.source_scoring import sort_items_by_score
from app.models import SourceItem


def build_section_context(items: list[SourceItem]) -> dict[str, dict]:
    grouped = map_items_to_sections(items)
    enriched = {}

    for heading in REQUIRED_HEADINGS:
        section_items = sort_items_by_score(grouped.get(heading, []))
        enriched[heading] = {
            "confidence": compute_section_confidence(section_items),
            "source_count": len(section_items),
            "items": section_items[:5],
        }

    return enriched