# analysis/signal_engine.py
from __future__ import annotations

from dataclasses import dataclass, field

from analysis.event_model import Event


@dataclass
class Signal:
    category: str
    title: str
    summary: str
    source_name: str
    section_name: str
    confidence: str
    score: int
    mission_impact: str
    tags: list[str] = field(default_factory=list)


RULES = [
    {
        "category": "regional_maritime",
        "keywords": [
            "south china sea",
            "scarborough shoal",
            "second thomas shoal",
            "spratly",
            "water cannon",
            "ramming",
            "coast guard",
            "luzon strait",
            "exclusive economic zone",
        ],
        "base_score": 6,
        "confidence": "Medium",
        "mission_impact": "Monitor",
    },
    {
        "category": "taiwan",
        "keywords": [
            "taiwan",
            "taiwan strait",
            "adiz",
            "pla activities",
            "airspace around taiwan",
            "median line",
        ],
        "base_score": 5,
        "confidence": "Medium",
        "mission_impact": "Monitor",
    },
    {
        "category": "terrorism_internal_security",
        "keywords": [
            "abu sayyaf",
            "bangsamoro",
            "biff",
            "jemaah",
            "terror",
            "bomb",
            "insurgent",
            "mindanao",
            "extremist",
        ],
        "base_score": 7,
        "confidence": "Medium",
        "mission_impact": "Elevated risk",
    },
    {
        "category": "demonstration_civil_unrest",
        "keywords": [
            "demonstration",
            "protest",
            "rally",
            "civil unrest",
            "metro manila",
        ],
        "base_score": 4,
        "confidence": "Medium",
        "mission_impact": "Limited impact",
    },
    {
        "category": "aviation",
        "keywords": [
            "flight cancellation",
            "runway closure",
            "airport disruption",
            "naia",
            "airline delay",
            "airport operations",
        ],
        "base_score": 6,
        "confidence": "Medium",
        "mission_impact": "Limited impact",
    },
    {
        "category": "weather",
        "keywords": [
            "typhoon",
            "heavy rain",
            "flood",
            "thunderstorm",
            "heat stroke",
            "heat injury",
        ],
        "base_score": 6,
        "confidence": "High",
        "mission_impact": "Limited impact",
    },
]


ESCALATORS = {
    "collision": 3,
    "ramming": 3,
    "missile": 4,
    "warning": 2,
    "closure": 2,
    "suspended": 2,
    "cancelled": 2,
    "evacuation": 4,
    "armed": 3,
}


def detect_signals(events: list[Event]) -> list[Signal]:
    signals: list[Signal] = []

    for event in events:
        text = event.normalized_text

        for rule in RULES:
            hits = [kw for kw in rule["keywords"] if kw in text]
            if not hits:
                continue

            score = rule["base_score"]
            for term, delta in ESCALATORS.items():
                if term in text:
                    score += delta

            confidence = "High" if score >= 9 else rule["confidence"]

            summary = event.raw_text.replace("\n", " ").strip()
            if len(summary) > 240:
                summary = summary[:237].rsplit(" ", 1)[0] + "..."

            signals.append(
                Signal(
                    category=rule["category"],
                    title=f"{rule['category']} indicator",
                    summary=summary,
                    source_name=event.source_name,
                    section_name=event.section_name,
                    confidence=confidence,
                    score=score,
                    mission_impact=rule["mission_impact"],
                    tags=hits,
                )
            )

    return sorted(signals, key=lambda s: s.score, reverse=True)