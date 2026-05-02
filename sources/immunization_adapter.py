from __future__ import annotations

import re
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from clients.http_client import get_text
from config import IMMUNIZATION_TIMEOUT_SEC, IMMUNIZATION_URL
from sources.base import BaseSourceAdapter
from sources.fetch_with_cache import fetch_with_cache
from sources.source_models import SourcePayload


class ImmunizationAdapter(BaseSourceAdapter):
    CACHE_KEY = "health_advisory"

    def __init__(
        self,
        api_url: str = IMMUNIZATION_URL,
        timeout_sec: int = IMMUNIZATION_TIMEOUT_SEC,
    ) -> None:
        self.api_url = api_url
        self.timeout_sec = timeout_sec

    def _extract_country_page_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text("\n", strip=True)
        return re.sub(r"\s+", " ", text)

    def _build_payload(self) -> SourcePayload:
        print(f"IMMUNIZATION REQUEST URL: {self.api_url}")
        print(f"IMMUNIZATION TIMEOUT: {self.timeout_sec}")

        now = datetime.now(timezone.utc)
        html = get_text(self.api_url, timeout_sec=self.timeout_sec)
        text = self._extract_country_page_text(html).lower()

        cdc_lines: list[str] = []

        if "level 1 practice usual precautions" in text:
            cdc_lines.append("CDC traveler page currently lists the Philippines at Level 1: Practice Usual Precautions.")

        if "measles" in text:
            cdc_lines.append("CDC notes measles remains a concern for international travelers; ensure MMR vaccination is current.")

        # Keep these concise, even if derived from the country page / standing travel guidance.
        cdc_lines.append("Mosquito-borne illness risk remains relevant; prevent bites and use repellent.")
        cdc_lines.append("Animal-bite exposure remains a practical risk; avoid contact with stray animals and seek care after bites.")
        cdc_lines.append("Food- and water-borne illness remains a routine travel risk; use safe food and bottled or treated water.")

        if len(cdc_lines) == 0:
            cdc_lines = [
                "No current health advisories issued by the Centers for Disease Control affecting travel to the Philippines or the surrounding region at this time."
            ]

        content = "\n".join(
            [
                "Routine / Recommended Vaccines",
                "Routine vaccines current (MMR, Tdap, influenza).",
                "Recommended travel vaccines commonly include Hepatitis A, Hepatitis B, and Typhoid.",
                "",
                "Higher-Risk Disease Considerations",
                "Rabies risk is relevant due to stray animal exposure.",
                "Mosquito-borne disease risk includes Dengue and Chikungunya; Japanese Encephalitis may matter in certain rural/agricultural exposure patterns.",
                "Use food and water discipline to reduce gastrointestinal disease risk.",
                "",
                "CDC Advisory Notes",
                *[f"- {line}" for line in cdc_lines[:5]],
            ]
        )

        return SourcePayload(
            source_name="CDC Traveler Health - Philippines",
            section_name="Immunization recommendations",
            content=content,
            source_type="WEB",
            required=True,
            retrieved_at_utc=now,
            source_timestamp_utc=now,
            max_age_hours=168,
            notes="Health advisory merged with immunization guidance.",
            raw_metadata={
                "provider": "cdc.gov",
                "api_url": self.api_url,
                "live_mode": True,
            },
        )

    def fetch(self) -> SourcePayload:
        return fetch_with_cache(self.CACHE_KEY, self._build_payload)