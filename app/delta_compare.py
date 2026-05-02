def summarize_source_deltas(current_items: list[dict], previous_items: list[dict]) -> list[str]:
    previous_titles = {item.get("title", "") for item in previous_items}
    current_titles = {item.get("title", "") for item in current_items}

    new_titles = sorted(t for t in current_titles if t and t not in previous_titles)
    dropped_titles = sorted(t for t in previous_titles if t and t not in current_titles)

    lines = []

    if new_titles:
        lines.append("New or newly captured items: " + "; ".join(new_titles[:5]))
    if dropped_titles:
        lines.append("Items no longer present in current capture: " + "; ".join(dropped_titles[:5]))

    if not lines:
        lines.append("No major source-capture delta identified against the previous run.")

    return lines