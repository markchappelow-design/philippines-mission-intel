from typing import List
import re

from config import LIVE_MILITARY_SOURCES
from clients.http_client import get_text
from sources.source_models import SourcePayload
from datetime import datetime, timezone


class LiveMilitaryAdapter:
    def __init__(self, timeout_sec: int = 15) -> None:
        self.timeout_sec = timeout_sec

    def _extract_relevant_lines(self, text: str, watch_terms: List[str]) -> List[str]:
        findings = []

        for line in text.splitlines():
            lower_line = line.lower()

            if any(term.lower() in lower_line for term in watch_terms):
                cleaned = re.sub(r"\s+", " ", line).strip()

                if len(cleaned) > 40:
                    findings.append(cleaned)

        return findings[:5]

    def fetch(self) -> SourcePayload:
        findings_all = []

        for source in LIVE_MILITARY_SOURCES:
            try:
                print(f"LIVE MIL REQUEST URL: {source['url']}")
                html = get_text(source["url"], timeout_sec=self.timeout_sec)

                findings = self._extract_relevant_lines(
                    html,
                    source.get("watch_terms", []),
                )

                for finding in findings[:2]:
                    findings_all.append(f"[{source['name']}] {finding}")

            except Exception as e:
                print(f"LIVE MIL SOURCE FAILED: {source['name']} -> {e}")

        content = "\n".join(findings_all).strip()

        if not content:
            content = (
                "No current PLA / regional military activity met freshness threshold. "
                "Continue monitoring Taiwan Strait, Luzon approaches, and WPS indicators."
            )

        return SourcePayload(
            source_name="live_military",
            section_name="Priority Intelligence",
            content=content,
            source_type="WEB",
            required=False,
            retrieved_at_utc=datetime.now(timezone.utc),
            source_timestamp_utc=datetime.now(timezone.utc),
            max_age_hours=24,
            notes="Live military / PLA regional activity watch",
            raw_metadata={
                "provider": "live_military_sources",
                "confidence": "medium",
            },
        )