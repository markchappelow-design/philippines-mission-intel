from __future__ import annotations

from analysis.signal_engine import Signal


def build_signal_bullets(signals: list[Signal], max_items: int = 3) -> str:
    if not signals:
        return "No significant new indicators identified at runtime."

    lines: list[str] = []
    for s in signals[:max_items]:
        lines.append(
            f"- {s.summary} | Confidence: {s.confidence} | Mission impact: {s.mission_impact}"
        )
    return "\n".join(lines)


def build_crisis_banner(signals: list[Signal]) -> str:
    if not signals:
        return ""

    return "\n".join(
        [
            "CRISIS INDICATOR DETECTED",
            "One or more high-severity indicators were identified during this reporting cycle.",
            "Review maritime, aviation, security, and movement assumptions before execution.",
        ]
    )