# analysis/brief_logic.py
from __future__ import annotations

from analysis.signal_engine import Signal


def top_signals(signals: list[Signal], limit: int = 5) -> list[Signal]:
    return sorted(signals, key=lambda s: s.score, reverse=True)[:limit]


def top_signal_by_category(signals: list[Signal], category: str) -> Signal | None:
    matches = [s for s in signals if s.category == category]
    if not matches:
        return None
    return sorted(matches, key=lambda s: s.score, reverse=True)[0]


def likely_disruption(signals: list[Signal]) -> str:
    for category, text in [
        ("weather", "Weather disruption"),
        ("aviation", "Airport or airline disruption"),
        ("demonstration_civil_unrest", "Demonstration or access disruption"),
    ]:
        if any(s.category == category for s in signals):
            return text
    return "Weather or airport throughput friction"


def dangerous_escalation(signals: list[Signal]) -> str:
    for category, text in [
        ("regional_maritime", "South China Sea maritime confrontation"),
        ("taiwan", "Taiwan Strait escalation affecting Luzon corridor assumptions"),
        ("terrorism_internal_security", "Internal security deterioration affecting travel corridors"),
    ]:
        if any(s.category == category for s in signals):
            return text
    return "Regional security deterioration affecting travel assumptions"