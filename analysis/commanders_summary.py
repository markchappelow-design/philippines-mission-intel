# analysis/commanders_summary.py
from __future__ import annotations

from analysis.brief_logic import dangerous_escalation, likely_disruption


def generate_commanders_summary(signals: list) -> str:
    environment = "Stable but sensitive"

    if any(s.score >= 9 for s in signals):
        environment = "Sensitive with elevated watch indicators"

    return "\n".join(
        [
            f"Environment: {environment}",
            f"Most likely disruption: {likely_disruption(signals)}.",
            f"Most dangerous escalation: {dangerous_escalation(signals)}.",
            "Bottom line: Travel remains feasible; monitor official alerts, weather, airport status, and regional security developments.",
        ]
    )