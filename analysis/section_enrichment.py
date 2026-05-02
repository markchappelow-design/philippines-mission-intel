from __future__ import annotations

from analysis.signal_engine import Signal


CATEGORY_TO_SECTION = {
    "taiwan": "Priority Intelligence",
    "regional_maritime": "Regional Maritime Security",
    "terrorism_internal_security": "Internal Security / Terrorism Assessment",
    "demonstration_civil_unrest": "U.S. Embassy (Manila) travel advisories",
    "aviation": "Aviation Operations Environment",
    "weather": "Weather forecast",
}


def top_signals_for_section(signals: list[Signal], section_name: str, limit: int = 2) -> list[Signal]:
    matched = [
        s for s in signals
        if CATEGORY_TO_SECTION.get(s.category) == section_name
    ]
    return sorted(matched, key=lambda s: s.score, reverse=True)[:limit]


def format_signal_bullets(signals: list[Signal]) -> str:
    if not signals:
        return "No additional high-signal indicators identified at runtime."

    lines: list[str] = []
    for s in signals:
        lines.append(
            f"- {s.summary} | Confidence: {s.confidence} | Mission impact: {s.mission_impact}"
        )
    return "\n".join(lines)


def enrich_section(base_text: str, signals: list[Signal], section_name: str) -> str:
    section_signals = top_signals_for_section(signals, section_name)

    if not section_signals:
        return base_text

    return "\n\n".join(
        [
            base_text.strip(),
            "Additional Signal Indicators",
            format_signal_bullets(section_signals),
        ]
    )