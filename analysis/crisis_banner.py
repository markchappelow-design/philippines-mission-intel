# analysis/crisis_banner.py
from __future__ import annotations


def build_crisis_banner(signals: list) -> str:
    if not any(s.score >= 9 for s in signals):
        return ""

    return "\n".join(
        [
            "CRISIS INDICATOR DETECTED",
            "One or more high-severity indicators were identified during this reporting cycle.",
            "Review movement assumptions, transport resilience, and security posture before execution.",
        ]
    )