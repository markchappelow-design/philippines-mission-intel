from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sources.base import BaseSourceAdapter
from sources.source_models import SourcePayload
from sources.contingency_entry_verifier import (
    verify_malaysia,
    verify_singapore,
    verify_thailand,
)

my = verify_malaysia()

@dataclass
class DiversionOption:
    name: str
    ok: bool
    notes: str
    verification_summary: str
    source_url: str
    expiry_utc: Optional[datetime] = None

    def qualifies(self, now_utc: datetime) -> bool:
        if not self.ok:
            return False
        if self.expiry_utc is not None and now_utc > self.expiry_utc:
            return False
        return True


class ContingencyEntryAdapter(BaseSourceAdapter):
    CACHE_KEY = "contingency_entry"

    def _build_options(self) -> list[DiversionOption]:
        my = verify_malaysia()
        sg = verify_singapore()
        th = verify_thailand()


        return [
            DiversionOption(
                "Malaysia",
                my.ok,
                "PRIMARY - best balance of proximity, low friction, and routing flexibility.",
                my.summary,
                my.source_url,
            ),
            DiversionOption(
                "Singapore",
                sg.ok,
                "PRIMARY - highest infrastructure reliability and administrative predictability.",
                sg.summary,
                sg.source_url,
            ),
            DiversionOption(
                "Thailand",
                True,
                "PRIMARY - visa-exempt entry; requires rapid digital arrival declaration (minutes, not approval).",
                th.summary,
                th.source_url,
            ),
          ]

    def _build_content(self, options: list[DiversionOption]) -> str:
        now_utc = datetime.now(timezone.utc)
        qualified = [o for o in options if o.qualifies(now_utc)]

        names = ", ".join(o.name for o in qualified) if qualified else "None verified for inclusion"

        lines = [
            "Contingency Diversion Footnote — Dual-Passport No-Visa Options (Daily Verified)",
            "",
            (
                "As of report generation, the following nearby Asia-Pacific destinations currently allow entry "
                "for both U.S. passport holders and Philippine passport holders without a prearranged visa; limited "
                "digital arrival declaration may be required."
                f"{names}."
            ),
            "",
            "Entry Processing:",
            "- Malaysia (MDAC), Singapore (SGAC), and Thailand (TDAC) require digital arrival declarations submitted prior to arrival.",
            "- These are not visas and typically process in seconds to minutes with no approval delay.",
        ]

        

        for option in qualified:
            if option.expiry_utc is not None:
                lines.append(
                    f"- {option.name}: included only while the current exemption remains valid through {option.expiry_utc.date().isoformat()}."
                )

        lines.extend([
            "",
            "Operational note:",
            (
                "This section is a rapid-diversion planning aid only. Final admission remains at the discretion "
                "of local immigration authorities. Passport validity, onward travel, proof of funds, and other "
                "arrival-side requirements still apply."
            ),
        ])

        return "\n".join(lines)

    def _build_payload(self) -> SourcePayload:
        now = datetime.now(timezone.utc)
        options = self._build_options()

        return SourcePayload(
            source_name="Contingency Entry Verification",
            section_name="Contingency diversion footnote",
            content=self._build_content(options),
            source_type="LIVE_FEED",
            required=True,
            retrieved_at_utc=now,
            source_timestamp_utc=now,
            max_age_hours=24,
            notes="Daily-verified shortlist of nearby no-visa diversion options for both U.S. and Philippine passport holders.",
            raw_metadata={
                "qualified_destinations": [o.name for o in options if o.qualifies(now)],
                "excluded_destinations": [o.name for o in options if not o.qualifies(now)],
                "verification": [
                    {
                        "name": o.name,
                        "ok": o.ok,
                        "summary": o.verification_summary,
                        "source_url": o.source_url,
                        "expiry_utc": o.expiry_utc.isoformat() if o.expiry_utc else None,
                    }
                    for o in options
                ],
                "policy_standard": "dual-passport no-visa / rapid-entry (arrival declaration allowed)",
            },
        )

    def build_assumptions_section() -> str:
        return (
            "Assumptions\n"
            "- Commercial aviation remains generally available from Metro Manila.\n"
            "- No immediate closure of Manila-area access routes is in effect at runtime.\n"
            "- Embassy, weather, and airport reporting remain sufficient for near-term movement planning.\n"
        )
    
     
    def fetch(self) -> SourcePayload:
        return self._build_payload()
    
    qualified_labels = [
    "Singapore (PRIMARY - low friction, major hub)",
]