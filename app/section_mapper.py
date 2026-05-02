from collections import defaultdict
from typing import Dict, List

from app.models import SourceItem


REQUIRED_HEADINGS = [
    "Strategic Situation",
    "Priority Intelligence",
    "U.S. Embassy (Manila) travel advisories",
    "U.S. State Department travel advisories for Americans",
    "Immunization recommendations",
    "Weather forecast",
    "NAIA publications and announcements",
    "Geothermal activity reported in the country",
    "Chinese hostility towards Philippine Navy or Coastguard in the China Sea or disputed territories",
    "The effect of global conflicts affecting flights in and out of the country",
    "PAGASA updates and announcements",
    "Operational Environment",
]


def map_items_to_sections(items: List[SourceItem]) -> Dict[str, List[SourceItem]]:
    grouped: Dict[str, List[SourceItem]] = defaultdict(list)

    for heading in REQUIRED_HEADINGS:
        grouped[heading] = []

    for item in items:
        grouped[item.section_target].append(item)

    return grouped