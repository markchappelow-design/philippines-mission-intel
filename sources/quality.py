from __future__ import annotations

import html
import re
from typing import List


BOILERPLATE_PATTERNS = [
    r"Go To Main content",
    r"World Wide Web",
    r"News Channel",
    r"About the Minister",
    r"Organizational Hierarchy",
    r"Former Ministers",
    r"Passenger Guide",
    r"Dining",
    r"Shops",
    r"Wellness\s*&\s*Relaxation",
    r"Other Services\s*&\s*Amenities",
    r"Special Assistance",
    r"Page Not Found",
    r"Error 404",
    r"Privacy Statement",
    r"Learn More",
]


SIGNAL_PATTERNS = [
    r"\bPLA\b",
    r"\bTaiwan Strait\b",
    r"\bADIZ\b",
    r"\bmedian line\b",
    r"\baircraft\b",
    r"\bvessel\b",
    r"\bship\b",
    r"\bsortie\b",
    r"\bnaval\b",
    r"\bdrone\b",
    r"\bmissile\b",
    r"\bexercise\b",
    r"\bpatrol\b",
    r"\bincursion\b",
    r"\bmilitary\b",
]


def normalize_whitespace(text: str) -> str:
    text = html.unescape(text or "")
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def render_gold_section(
    title: str,
    narrative: str,
    key_points: list[str],
    operational_impact: list[str],
    triggers: list[str],
    time_horizon: dict[str, str],
    bottom_line: str,
    confidence: str,
) -> str:
    # Normalize inputs
    narrative = (narrative or "").strip()
    key_points = [k.strip() for k in (key_points or []) if k and k.strip()]
    operational_impact = [k.strip() for k in (operational_impact or []) if k and k.strip()]
    triggers = [k.strip() for k in (triggers or []) if k and k.strip()]
    bottom_line = (bottom_line or "").strip()
    confidence = (confidence or "").strip()

    th_immediate = time_horizon.get("Immediate", "").strip()
    th_near = time_horizon.get("Near-Term", "").strip()
    th_mid = time_horizon.get("Mid-Term", "").strip()

    parts = []

    # Narrative
    if narrative:
        parts.append("Narrative:")
        parts.append(narrative)

    # Key Points
    if key_points:
        parts.append("\nKey Points:")
        parts.extend([f"- {k}" for k in key_points])

    # Operational Impact
    if operational_impact:
        parts.append("\nOperational Impact:")
        parts.extend([f"- {k}" for k in operational_impact])

    # Triggers
    if triggers:
        parts.append("\nTriggers to Watch:")
        parts.extend([f"- {k}" for k in triggers])

    # Time Horizon
    parts.append("\nTime Horizon:")
    parts.append(f"Immediate (0–72 hours): {th_immediate}")
    parts.append(f"Near-Term (3–7 days): {th_near}")
    parts.append(f"Mid-Term (7–30 days): {th_mid}")

    # Bottom Line
    if bottom_line:
        parts.append("\nBottom Line:")
        parts.append(bottom_line)

    # Confidence
    parts.append(f"\nConfidence: {confidence}")

    return "\n".join(parts).strip()

def sanitize_text(text: str) -> str:
    text = normalize_whitespace(text)
    text = text.replace("\u25a0", "-")
    text = text.replace("\u25cf", "-")
    text = text.replace("\u2022", "-")
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def ensure_nonempty(text: str, fallback: str) -> str:
    value = (text or "").strip()
    return value if value else fallback.strip()


def validate_quality(text: str) -> list[str]:
    return assess_content_quality(text)

def assess_content_quality(text: str) -> List[str]:
    issues: List[str] = []
    t = text or ""

    if len(t.strip()) < 80:
        issues.append("content_too_short")

    for pattern in BOILERPLATE_PATTERNS:
        if re.search(pattern, t, re.IGNORECASE):
            issues.append(f"boilerplate_match:{pattern}")

    if t.count("http") > 3 and len(t.split()) < 200:
        issues.append("link_heavy_low_signal")

    return issues


def contains_boilerplate(text: str) -> bool:
    return any(re.search(p, text or "", re.IGNORECASE) for p in BOILERPLATE_PATTERNS)


def looks_like_404(text: str) -> bool:
    t = text or ""
    return (
        "Page Not Found" in t
        or "Error 404" in t
        or re.search(r"\b404\b", t) is not None
    )


def extract_signal_lines(text: str, limit: int = 8) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()

    for raw in (text or "").splitlines():
        line = normalize_whitespace(raw)
        if len(line) < 20:
            continue
        if contains_boilerplate(line):
            continue
        if not any(re.search(p, line, re.IGNORECASE) for p in SIGNAL_PATTERNS):
            continue

        key = line.lower()
        if key in seen:
            continue

        seen.add(key)
        lines.append(line)
        if len(lines) >= limit:
            break

    return lines


def intel_brief_section(narrative, key_points, assessment, confidence):
    return (
        f"{narrative.strip()}\n\n"
        "Key factors:\n"
        + "\n".join(f"- {k}" for k in key_points)
        + "\n\nAssessment:\n"
        + assessment.strip()
        + f"\n\nConfidence: {confidence}"
    )

def analytic_section(
    heading: str,
    what_happened: str,
    why_it_matters: str,
    operational_effect: str,
    confidence: str,
) -> str:
    return render_gold_section(
        title=heading,
        narrative=what_happened,
        key_points=[why_it_matters],
        operational_impact=[operational_effect],
        triggers=[
            "Embassy posture change",
            "Airport disruption expansion",
            "Flight cancellation clustering",
            "Regional military escalation",
        ],
        time_horizon={
            "Immediate": "Active monitoring required",
            "Near-Term": "Monitor aviation and weather variability",
            "Mid-Term": "Baseline regional tension persists",
        },
        bottom_line=operational_effect,
        confidence=confidence,
    )