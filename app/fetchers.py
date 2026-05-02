from typing import List
import requests

from app.models import SourceItem
from app.parsers_aviation import parse_aviation
from app.parsers_maritime import parse_maritime
from app.parsers_router import parse_by_source
from app.source_time_parsers import extract_time_by_source
from app.time_extractor import normalize_published_time


USER_AGENT = "Mozilla/5.0 (compatible; MissionIntelBot/1.0)"


def fetch_html(url: str, timeout: int = 25) -> str:
    response = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    return response.text


def _parse_entry(entry: dict, html: str) -> dict:
    if entry["section_target"] == "Chinese hostility towards Philippine Navy or Coastguard in the China Sea or disputed territories":
        return parse_maritime(html)

    if entry["section_target"] == "The effect of global conflicts affecting flights in and out of the country":
        return parse_aviation(html)

    return parse_by_source(entry["source_name"], html)


def fetch_all_sources(source_registry: list[dict]) -> List[SourceItem]:
    items: List[SourceItem] = []

    for entry in source_registry:
        try:
            html = fetch_html(entry["source_url"])
            parsed = _parse_entry(entry, html)

            published_time_original = extract_time_by_source(entry["source_name"], html)
            published_time_utc = normalize_published_time(published_time_original)

            items.append(
                SourceItem(
                    source_name=entry["source_name"],
                    source_url=entry["source_url"],
                    section_target=entry["section_target"],
                    title=parsed["title"],
                    published_time_original=published_time_original,
                    published_time_utc=published_time_utc,
                    extracted_text=parsed["summary_text"],
                    reliability_tier=entry["reliability_tier"],
                    fetch_status="ok",
                    error_text=None,
                    parser_name=parsed.get("parser_name"),
                    source_type=entry.get("source_type"),
                    critical=entry.get("critical", False),
                )
            )
        except Exception as exc:
            items.append(
                SourceItem(
                    source_name=entry["source_name"],
                    source_url=entry["source_url"],
                    section_target=entry["section_target"],
                    title=entry["source_name"],
                    published_time_original="unknown",
                    published_time_utc="unknown",
                    extracted_text="",
                    reliability_tier=entry["reliability_tier"],
                    fetch_status="error",
                    error_text=str(exc),
                    parser_name=None,
                    source_type=entry.get("source_type"),
                    critical=entry.get("critical", False),
                )
            )

    return items