from __future__ import annotations

import re
import requests
import urllib3
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from clients.http_client import get_text
from sources.base import BaseSourceAdapter
from sources.fetch_with_cache import fetch_with_cache
from sources.source_models import SourcePayload

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


PHIVOLCS_BULLETIN_URL = "https://wovodat.phivolcs.dost.gov.ph/bulletin/list-of-bulletin"
PHIVOLCS_ALERT_LEVELS_URL = "https://www.phivolcs.dost.gov.ph/volcano-alert-levels/"


class PHIVOLCSAdapter(BaseSourceAdapter):
    CACHE_KEY = "phivolcs_volcano_status"

    def __init__(
        self,
        bulletin_url: str = PHIVOLCS_BULLETIN_URL,
        alert_levels_url: str = PHIVOLCS_ALERT_LEVELS_URL,
        timeout_sec: int = 20,
    ) -> None:
        self.bulletin_url = bulletin_url
        self.alert_levels_url = alert_levels_url
        self.timeout_sec = timeout_sec

    def fetch(self) -> SourcePayload:
        return fetch_with_cache(self.CACHE_KEY, self._build_payload)

    def _extract_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text("\n", strip=True)
        return re.sub(r"\s+", " ", text).strip()
    
    def _fetch_text_lenient_ssl(self, url: str) -> str:
        try:
            return get_text(url, timeout_sec=self.timeout_sec)
        except requests.exceptions.SSLError:
            response = requests.get(url, timeout=self.timeout_sec, verify=False)
            response.raise_for_status()
            return response.text

    def _extract_bulletin_items(self, html: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        candidates: list[str] = []

        for tag in soup.find_all(["a", "td", "li", "h1", "h2", "h3", "span", "div"]):
            text = re.sub(r"\s+", " ", tag.get_text(" ", strip=True)).strip()
            if not text:
                continue

            low = text.lower()
            if any(k in low for k in [
                "volcano bulletin",
                "volcano advisory",
                "eruption bulletin",
                "ashfall",
                "alert level",
                "taal",
                "mayon",
                "kanlaon",
                "bulusan",
                "pinatubo",
            ]):
                if 8 <= len(text) <= 220:
                    candidates.append(text)

        deduped: list[str] = []
        seen: set[str] = set()

        for item in candidates:
            key = item.lower()
            if key not in seen:
                seen.add(key)
                deduped.append(item)

            if len(deduped) >= 10:
                break

        return deduped

    def _infer_risk_terms(self, text: str) -> list[str]:
        low = text.lower()
        terms = []

        checks = {
            "Alert level language present": "alert level",
            "Ashfall language present": "ashfall",
            "Eruption language present": "eruption",
            "Lahar language present": "lahar",
            "Volcanic earthquake language present": "volcanic earthquake",
            "Sulfur dioxide / gas emission language present": "sulfur dioxide",
            "Evacuation / danger zone language present": "danger zone",
        }

        for label, needle in checks.items():
            if needle in low:
                terms.append(label)

        return terms

    def _build_payload(self) -> SourcePayload:
        now = datetime.now(timezone.utc)

        bulletin_html = self._fetch_text_lenient_ssl(self.bulletin_url)

        bulletin_text = self._extract_text(bulletin_html)
        bulletin_items = self._extract_bulletin_items(bulletin_html)
        risk_terms = self._infer_risk_terms(bulletin_text)

        latest_items = bulletin_items[:5]
        latest_text = (
            "\n".join(f"- {item}" for item in latest_items)
            if latest_items
            else "- No clean bulletin titles extracted."
        )

        if latest_items:
            assessment = (
                "PHIVOLCS volcano bulletin source was reachable at runtime. Latest extractable bulletin/advisory "
                "items should be reviewed for alert-level changes, ashfall, eruption, lahar, or aviation-impact language."
            )
            confidence = "Medium"
        else:
            assessment = (
                "PHIVOLCS source was reachable, but no clean bulletin titles were extracted. Treat this as monitor-only "
                "and manually verify the official PHIVOLCS bulletin page before movement if geological conditions matter."
            )
            confidence = "Low"

        risk_term_text = (
            "\n".join(f"- {x}" for x in risk_terms[:8])
            if risk_terms
            else "- No high-signal volcanic terms extracted from page text."
        )

        content = "\n".join([
            "Geological / Volcanic Activity",
            "",
            "Source:",
            f"- PHIVOLCS volcano bulletin list: {self.bulletin_url}",
            f"- PHIVOLCS alert-level reference: {self.alert_levels_url}",
            "",
            "Latest Extracted Bulletin / Advisory Items:",
            latest_text,
            "",
            "Runtime Assessment:",
            assessment,
            "",
            "Operational Significance:",
            "- Geological risk can affect aviation, road movement, port access, visibility, water quality, and local evacuation posture.",
            "- Ashfall, eruption columns, lahar risk, landslides, and earthquake damage should be treated as movement-disruption triggers.",
            "- Any alert-level increase or bulletin affecting Luzon, Manila airspace, major highways, or planned exfil routes requires reassessment.",
            "",
            "Trigger Language Detected:",
            risk_term_text,
            "",
            "Triggers to Watch:",
            "- PHIVOLCS volcano alert level increase",
            "- Ashfall advisory affecting Luzon, Manila, or flight corridors",
            "- Eruption bulletin, lahar warning, or danger-zone expansion",
            "- Earthquake damage causing road, airport, or port disruption",
            "",
            "Bottom Line:",
            "Geological activity is primarily a movement-disruption risk; escalate if PHIVOLCS reporting indicates ashfall, eruption, route closure, airport disruption, or evacuation orders.",
            "",
            f"Confidence: {confidence}",
        ])

        return SourcePayload(
            source_name="PHIVOLCS Volcano Status",
            section_name="Geological / Volcanic Activity",
            content=content,
            source_type="WEB",
            required=False,
            retrieved_at_utc=now,
            source_timestamp_utc=now,
            max_age_hours=24,
            notes="Official PHIVOLCS bulletin extraction for volcanic/geological movement-risk monitoring.",
            raw_metadata={
                "provider": "PHIVOLCS",
                "source_url": self.bulletin_url,
                "alert_levels_url": self.alert_levels_url,
                "live_mode": True,
                "extracted_items": latest_items,
                "risk_terms": risk_terms,
            },
        )    