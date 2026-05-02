from __future__ import annotations

from collections import Counter
from analysis.signal_engine import Signal


def signal_category_counts(signals: list[Signal]) -> dict[str, int]:
    return dict(Counter(s.category for s in signals))


def summarize_trends(current: dict[str, int], previous: dict[str, int]) -> str:
    lines: list[str] = []

    keys = sorted(set(current.keys()) | set(previous.keys()))
    for key in keys:
        c = current.get(key, 0)
        p = previous.get(key, 0)

        if c > p:
            lines.append(f"- {key}: increased from {p} to {c}")
        elif c < p:
            lines.append(f"- {key}: decreased from {p} to {c}")
        else:
            lines.append(f"- {key}: unchanged at {c}")

    return "\n".join(lines) if lines else "No meaningful signal trend change identified."