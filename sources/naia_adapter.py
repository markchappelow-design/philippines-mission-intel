from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests

from config import NAIA_API_URL, NAIA_TIMEOUT_SEC, NAIA_URL
from sources.base import BaseSourceAdapter
from sources.fetch_with_cache import fetch_with_cache
from sources.quality import (
    ensure_nonempty,
    validate_quality,
    sanitize_text,
    assess_content_quality,
)
from sources.source_models import SourcePayload

class NAIAAdapter(BaseSourceAdapter):
    CACHE_KEY = "naia_news"

    def __init__(
        self,
        site_url: str = NAIA_URL,
        api_url: str = NAIA_API_URL,
        timeout_sec: int = NAIA_TIMEOUT_SEC,
    ) -> None:
        self.site_url = site_url
        self.api_url = api_url
        self.timeout_sec = timeout_sec

    def _get_json(self) -> Any:
        print(f"NAIA REQUEST URL: {self.site_url}")
        print(f"NAIA TIMEOUT: {self.timeout_sec}")
        print(f"NAIA API URL: {self.api_url}")

        response = requests.get(self.api_url, timeout=self.timeout_sec)
        response.raise_for_status()
        return response.json()

    def _url_is_live(self, url: str) -> bool:
        try:
            r = requests.get(url, timeout=self.timeout_sec, allow_redirects=True)
            if r.status_code != 200:
                return False
            if looks_like_404(r.text):
                return False
            return True
        except Exception:
            return False

    def _extract_rows(self, data: Any) -> list[dict[str, Any]]:
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]

        if isinstance(data, dict):
            for key in ("data", "rows", "items", "results"):
                value = data.get(key)
                if isinstance(value, list):
                    return [x for x in value if isinstance(x, dict)]

        return []

    def _extract_items(self, data: Any) -> tuple[list[tuple[str, str]], int, int]:
        valid_items: list[tuple[str, str]] = []
        rejected = 0

        rows = self._extract_rows(data)
        total_rows = len(rows)

        for item in rows:
            title = sanitize_text(str(item.get("title") or "").strip())
            url = str(item.get("url") or item.get("link") or "").strip()

            if not title:
                continue

            # Fallback: build URL from slug if direct URL is absent
            if not url:
                slug = str(item.get("page_slug") or item.get("slug") or "").strip()
                if slug:
                    url = f"https://newnaia.com.ph/{slug}"

            if not url:
                rejected += 1
                continue

            if self._url_is_live(url):
                valid_items.append((title, url))
            else:
                rejected += 1

            if len(valid_items) >= 3:
                break

        return valid_items, rejected, total_rows

    def _build_payload(self) -> SourcePayload:
        now = datetime.now(timezone.utc)
        data = self._get_json()
        valid_items, rejected, total_rows = self._extract_items(data)

        if valid_items:
            item_text = " | ".join([f"{title} ({url})" for title, url in valid_items])

            content = (
                f"Validated current NAIA public items identified at runtime: {item_text}\n\n"
                "Key factors:\n"
                "- NAIA public news can provide limited insight into airport modernization, passenger-processing changes, or infrastructure announcements.\n"
                "- These items are useful only when the linked articles resolve live.\n\n"
                "Assessment:\n"
                "Use validated NAIA items as supplementary airport-context reporting only. They do not replace live airline, "
                "NOTAM, or airport-operations feeds for movement planning.\n\n"
                "Confidence: Medium"
            )
        else:
           content = (
                "No validated current NAIA public news items were confirmed from the website at runtime.\n\n"
                "Key factors:\n"
                "- The public NAIA news feed currently appears unreliable as a sole operational source.\n"
                "- The API structure may vary and entries may map to dead article URLs.\n\n"
                "Assessment:\n"
                "Do not treat NAIA public-site news alone as authoritative for current airport status. Use as supplemental context only.\n\n"
                "Confidence: Low"
            )

        notes_parts: list[str] = []

        quality_issues = assess_content_quality(content)
        if quality_issues:
            notes_parts.append(f"Quality issues: {', '.join(quality_issues)}")

        fallback_reason = None
        if not valid_items:
            fallback_reason = f"validated_items=0 rejected={rejected} rows_parsed={total_rows}"

        if fallback_reason:
            notes_parts.append(f"Fallback basis: {fallback_reason}")

        notes = " | ".join(notes_parts)

        return SourcePayload(
            source_name="NAIA Public News",
            section_name="NAIA / airport operational status",
            content=content,
            source_type="API",
            required=False,
            retrieved_at_utc=now,
            source_timestamp_utc=now,
            max_age_hours=24,
            notes=notes,
            raw_metadata={
                "provider": "newnaia.com.ph",
                "api_url": self.api_url,
                "site_url": self.site_url,
                "rows_parsed": total_rows,
                "validated_items": len(valid_items),
                "rejected_items": rejected,
                "live_mode": True,
                "quality_issues": quality_issues,
                "quality_ok": len(quality_issues) == 0,
                "fallback_reason": fallback_reason,
            }
        )

    def fetch(self) -> SourcePayload:
        return fetch_with_cache(self.CACHE_KEY, self._build_payload)
    
    