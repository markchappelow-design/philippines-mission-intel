from __future__ import annotations

import re
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from clients.http_client import get_text
from config import REGIONAL_SECURITY_TIMEOUT_SEC, REGIONAL_SECURITY_URL
from sources.base import BaseSourceAdapter
from sources.fetch_with_cache import fetch_with_cache
from sources.quality import (
    analytic_section,
    assess_content_quality,
    extract_signal_lines,
    sanitize_text,
)
from sources.source_models import SourcePayload


class RegionalSecurityAdapter(BaseSourceAdapter):
    CACHE_KEY = "regional_security"

    def __init__(
        self,
        api_url: str = REGIONAL_SECURITY_URL,
        timeout_sec: int = REGIONAL_SECURITY_TIMEOUT_SEC,
    ) -> None:
        self.api_url = api_url
        self.timeout_sec = timeout_sec

    
    def _extract_relevant_activity(self, html: str) -> tuple[str, list[str]]:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text("\n", strip=True)
        text = sanitize_text(text)

        signal_lines = extract_signal_lines(text, limit=8)

        # Look for a likely date stamp in the page text, but do not overfit.
        date_hits = re.findall(r"\b20\d{2}[./-]\d{2}[./-]\d{2}\b", text)
        date_str = date_hits[0] if date_hits else "current reporting cycle"

        if signal_lines:
            summary = (
                f"Latest Taiwan Strait / PLA activity reporting identified for {date_str}. "
                f"Relevant indicators extracted from source page: "
                + " | ".join(signal_lines[:5])
            )
        else:
            summary = (
                "Regional-security source was reachable, but no clean operational activity indicators "
                "were extracted from the current page render."
            )

        return summary, signal_lines

    def _build_payload(self) -> SourcePayload:
        print(f"REGIONAL SECURITY REQUEST URL: {self.api_url}")
        print(f"REGIONAL SECURITY TIMEOUT: {self.timeout_sec}")

        now = datetime.now(timezone.utc)
        html = get_text(self.api_url, timeout_sec=self.timeout_sec)
        summary, signal_lines = self._extract_relevant_activity(html)

        if signal_lines:
            content = analytic_section(
                heading="Regional Security / Taiwan Strait",
                what_happened=(
                    summary
                ),
                why_it_matters=(
                    "Sustained PLA air and maritime activity near Taiwan is a standing indicator of elevated regional tension "
                    "in the Western Pacific. Even below conflict threshold, increased military signaling can affect crisis posture, "
                    "commercial confidence, and contingency planning assumptions."
                ),
                operational_effect=(
                    "No direct disruption to Philippine civil-aviation corridors is confirmed from this source alone at runtime. "
                    "Monitor for escalation indicators that could affect regional airspace posture, international carrier routing, "
                    "or traveler movement timelines."
                ),
                confidence="Medium",
            )
            notes = "Regional security page reachable; extracted operational signal lines without using full-page boilerplate dump."
        else:
            content = analytic_section(
                heading="Regional Security / Taiwan Strait",
                what_happened=(
                    "Source page was reachable, but extraction returned no reliable operational activity lines suitable for briefing."
                ),
                why_it_matters=(
                    "A reachable page without clean extractable indicators is insufficient for a senior-level intelligence summary."
                ),
                operational_effect=(
                    "Treat this source as monitor-only for this cycle; do not infer transport impact beyond general regional sensitivity."
                ),
                confidence="Low",
            )
            notes = "Reachable source but weak extractable signal; fail-closed summary used."

        quality_issues = assess_content_quality(content)
        if quality_issues:
            notes += f" Quality issues: {', '.join(quality_issues)}"

        return SourcePayload(
            source_name="Taiwan MND PLA Activities",
            section_name="Priority Intelligence",
            content=content,
            source_type="WEB",
            required=True,
            retrieved_at_utc=now,
            source_timestamp_utc=now,
            max_age_hours=24,
            notes=notes,
        )

    def fetch(self) -> SourcePayload:
        return fetch_with_cache(self.CACHE_KEY, self._build_payload)