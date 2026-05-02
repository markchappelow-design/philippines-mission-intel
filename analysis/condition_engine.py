def evaluate_condition(signals: list) -> str:
    high = [s for s in signals if getattr(s, "score", 0) >= 9]
    medium = [s for s in signals if getattr(s, "score", 0) >= 6]

    if any("airspace" in str(s).lower() for s in high):
        return "red"

    if len(high) > 0 or len(medium) >= 2:
        return "amber"

    return "green"