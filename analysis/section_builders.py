from __future__ import annotations

from analysis.signal_engine import Signal


def build_regional_maritime_section(signals: list[Signal]) -> str:
    maritime = [s for s in signals if s.category == "regional_maritime"]

    lines = ["Regional Maritime Security"]

    if not maritime:
        lines.append("No new high-signal regional maritime security indicator identified at runtime.")
        lines.append("Mission impact: Monitor.")
        return "\n".join(lines)

    lines.append(
        "Chinese maritime pressure in and around Philippine-claimed waters remains the most significant regional security concern affecting the operating environment."
    )
    for s in maritime[:2]:
        lines.append(f"- {s.summary}")

    lines.append(
        "Mission impact: Monitor South China Sea and Luzon-adjacent escalation for second-order effects on transport assumptions, crisis posture, and regional route confidence."
    )
    return "\n".join(lines)


def build_internal_security_section(signals: list[Signal]) -> str:
    internal = [
        s for s in signals
        if s.category in ("terrorism_internal_security", "demonstration_civil_unrest")
    ]

    lines = ["Internal Security / Terrorism Assessment"]

    if not internal:
        lines.append(
            "No current active internal-security indicators affecting Metro Manila or principal travel corridors were identified at runtime."
        )
        lines.append("Mission impact: No direct impact.")
        return "\n".join(lines)

    for s in internal[:3]:
        lines.append(f"- {s.summary}")

    lines.append(
        "Mission impact: Monitor demonstrations, unrest, or localized security deterioration for possible effects on access, timing, and traveler movement."
    )
    return "\n".join(lines)