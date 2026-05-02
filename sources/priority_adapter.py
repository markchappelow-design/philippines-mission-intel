from __future__ import annotations

import re
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from clients.http_client import get_text
from config import REGIONAL_SECURITY_TIMEOUT_SEC, REGIONAL_SECURITY_URL
from sources.base import BaseSourceAdapter
from sources.fetch_with_cache import fetch_with_cache
from sources.source_models import SourcePayload


class PriorityIntelAdapter(BaseSourceAdapter):
    CACHE_KEY = "priority_intel"

    def __init__(
        self,
        api_url: str = REGIONAL_SECURITY_URL,
        timeout_sec: int = REGIONAL_SECURITY_TIMEOUT_SEC,
    ) -> None:
        self.api_url = api_url
        self.timeout_sec = timeout_sec

    def _extract_latest_title(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text("\n", strip=True)
        m = re.search(
            r"(20\d{2}\.\d{2}\.\d{2}\s+PLA activities in the waters and airspace around Taiwan)",
            text,
            re.IGNORECASE,
        )
        if m:
            return m.group(1)
        return "Latest PLA activity title not cleanly extracted."

    def _build_payload(self) -> SourcePayload:
        now = datetime.now(timezone.utc)
        html = get_text(self.api_url, timeout_sec=self.timeout_sec)
        latest_title = self._extract_latest_title(html)

        content = "\n".join(
            [
                "Priority Intelligence",
                f"Primary source: Taiwan Ministry of National Defense PLA Activities List ({self.api_url})",
                f"Latest item identified: {latest_title}",
                "Assessment: PLA military signaling around Taiwan remains active and should be treated as a standing regional-tension indicator.",
                "Operational significance: No direct disruption to Philippine civil aviation is confirmed from this source alone, but escalation could affect East Asia route confidence, crisis posture, and contingency planning assumptions.",
                "Bottom line: Monitor for meaningful changes in tempo, not just routine daily activity.",
            ]
        )

        return SourcePayload(
            source_name="Priority Intelligence - Taiwan MND",
            section_name="Priority Intelligence",
            content=content,
            source_type="WEB",
            required=True,
            retrieved_at_utc=now,
            source_timestamp_utc=now,
            max_age_hours=24,
            notes="Priority intelligence simplified and sourced directly to Taiwan MND.",
            raw_metadata={
                "provider": "mnd.gov.tw",
                "api_url": self.api_url,
                "latest_title": latest_title,
            },
        )

    def fetch(self) -> SourcePayload:
        return fetch_with_cache(self.CACHE_KEY, self._build_payload)