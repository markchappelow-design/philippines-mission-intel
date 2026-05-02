from __future__ import annotations

from datetime import datetime, timezone

from sources.base import BaseSourceAdapter
from sources.fetch_with_cache import fetch_with_cache
from sources.quality import analytic_section, assess_content_quality
from sources.source_models import SourcePayload


class StrategicIntelAdapter(BaseSourceAdapter):
    CACHE_KEY = "strategic_intel"


    def __init__(self) -> None:
        super().__init__()

    def _build_payload(self) -> SourcePayload:
        now = datetime.now(timezone.utc)

        content = analytic_section(
            heading="Strategic Situation",
            what_happened=(
                "The operating environment for travel and transportation in the Philippines remains generally functional, "
                "but externally sensitive. The main near-term regional pressure remains sustained cross-strait military signaling "
                "between the People's Republic of China and Taiwan, while global conflict activity outside Southeast Asia may still "
                "create indirect pressure through fuel pricing, insurance posture, and airline network resilience."
            ),
            why_it_matters=(
                "Even without a direct crisis affecting the Philippines, transport systems can degrade quickly from second-order effects: "
                "airport congestion, weather disruption, airline schedule compression, administrative bottlenecks, or spillover from broader regional tension."
            ),
            operational_effect=(
                "For mission planning, conditions should be treated as stable but sensitive. Most likely disruption remains weather or airport throughput friction; "
                "most dangerous external escalator remains a regional security deterioration that alters airline routing, traveler confidence, or crisis response timelines."
            ),
            confidence="Medium",
        )

        quality_issues = assess_content_quality(content)
        notes = "Strategic synthesis generated from bounded analytic template."
        if quality_issues:
            notes += f" Quality issues: {', '.join(quality_issues)}"

        return SourcePayload(
            source_name="Strategic Intelligence Synthesis",
            section_name="Strategic Situation",
            content=content,
            source_type="ANALYTIC",
            required=True,
            retrieved_at_utc=now,
            source_timestamp_utc=now,
            max_age_hours=24,
            notes=notes,
            raw_metadata={
                "provider": "internal_synthesis",
                "live_mode": True,
                "quality_issues": quality_issues,
                "quality_ok": len(quality_issues) == 0,
            },
        )

    def fetch(self) -> SourcePayload:
        return fetch_with_cache(self.CACHE_KEY, self._build_payload)