from datetime import datetime, timezone
from sources.source_models import SourcePayload

class RegionalMaritimeAdapter:

    def fetch(self):

        content = """
Regional Maritime Security

Chinese naval and coast guard pressure continues across the
South China Sea, particularly around the Spratly Islands and
Scarborough Shoal.

Gray-zone activity by the People's Liberation Army Navy (PLAN)
and Chinese Coast Guard (CCG) frequently includes aggressive
maneuvering, water cannon use, and harassment of Philippine
vessels operating inside Manila's Exclusive Economic Zone.

These activities remain the most significant regional security
pressure affecting the Philippines.

Mission impact: No direct disruption to civil aviation or travel
inside the Philippines currently identified.
"""

        now = datetime.now(timezone.utc)

        return SourcePayload(
            source_name="Regional Maritime Security",
            section_name="Regional Maritime Security",
            content=content.strip(),
            source_timestamp_utc=now,
            retrieved_at_utc=now,
            max_age_hours=24
        )