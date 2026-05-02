from __future__ import annotations


def source_reliability(source_name: str) -> str:
    source_name = source_name.lower()

    if "state department" in source_name or "embassy" in source_name or "open-meteo" in source_name:
        return "A"
    if "taiwan mnd" in source_name:
        return "B"
    if "naia" in source_name:
        return "C"
    return "C"


def information_credibility(confidence: str) -> str:
    if confidence == "High":
        return "2"
    if confidence == "Medium":
        return "3"
    return "4"