# analysis/quality_control.py
from __future__ import annotations


def generate_quality_control_summary(
    sources_checked: int,
    failed_optional_count: int,
    used_cache_fallback: bool,
    significant_change_detected: bool,
    high_severity_signal_count: int,
) -> str:
    return "\n".join(
        [
            f"Sources checked: {sources_checked}",
            f"Failed optional sources: {failed_optional_count}",
            f"Cache fallback used: {'yes' if used_cache_fallback else 'no'}",
            f"Significant change detected: {'yes' if significant_change_detected else 'no'}",
            f"High-severity signals: {high_severity_signal_count}",
            f"Overall report confidence: {'Medium' if high_severity_signal_count == 0 else 'Medium-High'}",
        ]
    )