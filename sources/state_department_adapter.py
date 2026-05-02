from __future__ import annotations

from datetime import datetime, timezone

from sources.base import BaseSourceAdapter
from sources.source_models import SourcePayload


class StateDepartmentAdapter(BaseSourceAdapter):
    CACHE_KEY = "state_department"

    def fetch(self) -> SourcePayload:
        now = datetime.now(timezone.utc)

        return SourcePayload(
            source_name="U.S. State Department Stub",
            section_name="U.S. State Department travel advisories for Americans",
                        content=(
                "U.S. State Department travel advisories for Americans\n\n"
                "The Philippines remains accessible for travel; however, U.S. government guidance identifies "
                "persistent security risks in specific regions that require deliberate risk assessment prior to movement.\n\n"
                "Key Threat Context:\n"
                "- Militant extremist groups, including the Abu Sayyaf Group (ASG), have historically conducted "
                "kidnappings, bombings, assassinations, and maritime attacks in the southern Philippines.\n"
                "- These groups are degraded but not eliminated, and retain the capability for localized violence "
                "and opportunistic targeting, including against foreign nationals.\n"
                "- Activity is concentrated in the Sulu Archipelago (Jolo, Basilan, Tawi-Tawi) and parts of western "
                "and central Mindanao, where governance, terrain, and security conditions allow such groups to operate.\n\n"
                "Operational Reality:\n"
                "- These threats are geographically limited, but high-impact where present.\n"
                "- Risk in major urban areas such as Manila is not driven by insurgent activity, but by crime, congestion, "
                "and infrastructure variability.\n"
                "- Movement into southern or remote regions without situational awareness introduces unnecessary exposure "
                "to kidnapping, armed group activity, and limited emergency response capability.\n\n"
                "Trigger Conditions Requiring Immediate Reassessment:\n"
                "- Reports of kidnapping-for-ransom activity, especially involving foreigners.\n"
                "- Any bombing, armed attack, or insurgent engagement in Mindanao or surrounding islands.\n"
                "- Changes in U.S. Embassy security posture or movement restrictions.\n"
                "- State Department advisory level increase or new region-specific warnings.\n"
                "- Indicators of militant activity expanding outside historically affected areas.\n\n"
                "Execution Guidance:\n"
                "- Do not treat advisory language as static; conditions can shift rapidly.\n"
                "- Avoid travel to Sulu Archipelago, Basilan, and high-risk Mindanao regions unless mission-essential "
                "and properly supported.\n"
                "- Maintain awareness of who you are interacting with, especially in unfamiliar or non-tourist environments.\n"
                "- Validate routes, lodging, and contacts against current conditions before movement.\n\n"
                "Bottom Line:\n"
                "- The Philippines is not uniformly high-risk, but specific regions contain real, documented threats involving "
                "terrorism, kidnapping, and armed groups.\n"
                "- Failure to recognize geographic risk boundaries is the primary pathway to exposure."
            ),
            retrieved_at_utc=now,
            source_timestamp_utc=now,
            max_age_hours=24,
        )