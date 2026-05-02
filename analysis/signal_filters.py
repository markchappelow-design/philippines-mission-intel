from __future__ import annotations

from analysis.signal_engine import Signal


SECTION_MAP = {
    "regional_maritime": "Regional Maritime Security",
    "taiwan": "Priority Intelligence",
    "terrorism_internal_security": "Internal Security / Terrorism Assessment",
    "demonstration_civil_unrest": "U.S. Embassy (Manila) travel advisories",
    "aviation": "Aviation Operations Environment",
    "weather": "Weather forecast",
}


def filter_for_brief(signals: list[Signal], min_score: int = 5) -> list[Signal]:
    return [s for s in signals if s.score >= min_score]


def group_signals_by_section(signals: list[Signal]) -> dict[str, list[Signal]]:
    grouped: dict[str, list[Signal]] = {}
    for s in signals:
        section = SECTION_MAP.get(s.category, "Priority Intelligence")
        grouped.setdefault(section, []).append(s)
    return grouped


def crisis_indicators(signals: list[Signal]) -> list[Signal]:
    return [s for s in signals if s.score >= 9]