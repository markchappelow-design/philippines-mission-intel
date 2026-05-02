def generate_delta_summary(diff_lines: int, alerts: list[str]) -> str:

    if diff_lines == 0:
        return "No significant operational changes detected since the previous report."

    items = []

    if "SIGNIFICANT_DELTA_DETECTED" in alerts:
        items.append("Material content changes detected in monitored sources.")

    if "CACHE_FALLBACK_USED" in alerts:
        items.append("Some sources temporarily unavailable; cached data used.")

    if not items:
        items.append("Minor informational changes detected.")

    return "\n".join(f"• {i}" for i in items)