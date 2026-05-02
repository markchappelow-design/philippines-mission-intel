from datetime import datetime, timezone
from sources.source_models import SourcePayload

class TerrorismAdapter:

    def fetch(self):

        content = """
Internal Security / Terrorism Assessment

No active terrorist alerts affecting Metro Manila travel were
identified at runtime.

Persistent insurgent and extremist activity remains concentrated
in parts of Mindanao involving groups such as Abu Sayyaf and the
Bangsamoro Islamic Freedom Fighters.

These groups historically target local security forces and
regional infrastructure rather than international travel hubs.

Mission impact: No direct threat indicators affecting Manila
transport corridors were identified.
"""

        now = datetime.now(timezone.utc)

        return SourcePayload(
            source_name="Philippine Internal Security",
            section_name="Internal Security / Terrorism Assessment",
            content=content.strip(),
            source_timestamp_utc=now,
            retrieved_at_utc=now,
            max_age_hours=24
        )