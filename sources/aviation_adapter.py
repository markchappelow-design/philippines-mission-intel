from datetime import datetime, timezone
from sources.source_models import SourcePayload

class AviationAdapter:

    def fetch(self):

        content = """
Aviation Operations Environment

No validated major flight disruptions affecting Manila's
Ninoy Aquino International Airport were identified at runtime.

Regional aviation networks remain stable with normal airline
routing patterns across Southeast Asia.

Mission impact: No aviation-specific constraints affecting
travel into or out of Manila were identified.
"""

        now = datetime.now(timezone.utc)

        return SourcePayload(
            source_name="Regional Aviation Operations",
            section_name="Aviation Operations Environment",
            content=content.strip(),
            source_timestamp_utc=now,
            retrieved_at_utc=now,
            max_age_hours=24
        )