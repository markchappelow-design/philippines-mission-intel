from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import List, Tuple

from bs4 import BeautifulSoup

from clients.http_client import get_text
from config import EMBASSY_TIMEOUT_SEC, EMBASSY_URL
from sources.base import BaseSourceAdapter
from sources.fetch_with_cache import fetch_with_cache
from sources.source_models import SourcePayload


SECURITY_URL = "https://ph.usembassy.gov/category/security/"


class EmbassyManilaAdapter(BaseSourceAdapter):
    CACHE_KEY = "embassy_manila"

    def __init__(
        self,
        api_url: str = EMBASSY_URL,
        timeout_sec: int = EMBASSY_TIMEOUT_SEC,
    ) -> None:
        self.api_url = api_url
        self.timeout_sec = timeout_sec

    def _extract_titles(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        titles: list[str] = []

        for tag in soup.find_all(["h1", "h2", "h3", "a"]):
            text = re.sub(r"\s+", " ", tag.get_text(" ", strip=True)).strip()
            if not text:
                continue
            if len(text) > 8 and len(text) < 160:
                titles.append(text)

        deduped: list[str] = []
        seen = set()
        for t in titles:
            key = t.lower()
            if key not in seen:
                seen.add(key)
                deduped.append(t)
        return deduped

    def _pick_security_item(self, titles: list[str]) -> str:
        philippine_patterns = [
            r"mindanao",
            r"manila",
            r"cebu",
            r"davao",
            r"sulu",
            r"basilan",
            r"zamboanga",
            r"abu sayyaf",
            r"bangsamoro",
            r"jemaah",
        ]
        generic_patterns = [
            r"october 7",
            r"hamas",
            r"anniversary",
        ]

        for title in titles:
            low = title.lower()
            if any(re.search(p, low) for p in philippine_patterns):
                return title

        for title in titles:
            low = title.lower()
            if "security alert" in low and not any(re.search(p, low) for p in generic_patterns):
                return title

        return ""

    def _pick_alert_item(self, titles: List[str]) -> str:
        for title in titles:
            low = title.lower()
            if any(x in low for x in ["closure", "consular", "alert", "advisory"]):
                return title
        return ""

    def _build_payload(self) -> SourcePayload:
        print(f"EMBASSY REQUEST URL: {self.api_url}")
        print(f"EMBASSY TIMEOUT: {self.timeout_sec}")

        now = datetime.now(timezone.utc)

        alert_html = get_text(self.api_url, timeout_sec=self.timeout_sec)
        print("EMBASSY FETCH: live content received")
        security_html = get_text(SECURITY_URL, timeout_sec=self.timeout_sec)

        alert_titles = self._extract_titles(alert_html)
        security_titles = self._extract_titles(security_html)

        security_item = self._pick_security_item(security_titles)
        alert_item = self._pick_alert_item(alert_titles)

        lines = ["U.S. Embassy (Manila) travel advisories"]

        if security_item:
            lines.append(f"Security item identified: {security_item}")
            lines.append(
                "Operational note: Review Embassy security messaging closely for protest activity, terrorism risk, or location-specific movement restrictions."
            )
        else:
            lines.append("No current high-signal Embassy security item was cleanly extracted from the Embassy security archive at runtime.")

        if alert_item:
            lines.append(f"Administrative / consular item identified: {alert_item}")
            lines.append(
                "Operational note: Administrative Embassy notices can still affect traveler support, consular access, and appointment availability."
            )
        else:
            lines.append("No current administrative Embassy alert was cleanly extracted at runtime.")

        content = "\n".join(lines)

        return SourcePayload(
            source_name="U.S. Embassy Manila",
            section_name="U.S. Embassy (Manila) travel advisories",
            content=content,
            source_type="WEB",
            required=True,
            retrieved_at_utc=now,
            source_timestamp_utc=now,
            max_age_hours=24,
            notes="Embassy general alerts and security archive both checked.",
            raw_metadata={
                "provider": "ph.usembassy.gov",
                "alerts_url": self.api_url,
                "security_url": SECURITY_URL,
                "selected_security_item": security_item,
                "selected_alert_item": alert_item,
            },
        )

    def fetch(self) -> SourcePayload:
        return fetch_with_cache(self.CACHE_KEY, self._build_payload)