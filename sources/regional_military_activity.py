from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List, Optional
from urllib.parse import urljoin
import re

import requests
from bs4 import BeautifulSoup

from sources.source_models import SourcePayload


SECTION_NAME = "Regional Military Activity / Movement"


SOURCES = [
    ("INDOPACOM", "https://www.pacom.mil/Media/News/"),
    ("DVIDS", "https://www.dvidshub.net/search?q=Philippines+South+China+Sea"),
    ("Reuters Asia Pacific", "https://www.reuters.com/world/asia-pacific/"),
    ("Reuters China", "https://www.reuters.com/world/china/"),
    ("USNI News", "https://news.usni.org/"),
    ("Naval News", "https://www.navalnews.com/"),
    ("Defense News", "https://www.defensenews.com/"),
    ("Philippine Navy", "https://navy.mil.ph/"),
    #("Philippine Coast Guard", "https://coastguard.gov.ph/"),
    ("GMA News", "https://www.gmanetwork.com/news/"),
    ("ABS-CBN News", "https://www.abs-cbn.com/news/"),
    ("Philstar", "https://www.philstar.com/"),
    ("Inquirer", "https://www.inquirer.net/"),
]


KEYWORD_SCORES = {
    # Critical / confrontation indicators
    "collision": 10,
    "water cannon": 10,
    "intercept": 9,
    "harassment": 9,
    "blockade": 9,
    "rammed": 9,
    "shadowing": 8,
    "combat readiness patrol": 8,
    "airspace closure": 8,
    "notam": 8,

    # Military movement / posture
    "missile": 7,
    "anti-ship": 7,
    "warship": 7,
    "destroyer": 7,
    "frigate": 6,
    "submarine": 7,
    "carrier": 7,
    "amphibious": 6,
    "live-fire": 6,
    "gunnery": 5,
    "joint exercise": 5,
    "military exercise": 5,
    "drill": 4,
    "maritime patrol": 5,
    "coast guard patrol": 5,
    "resupply mission": 6,

    # Geography / AO relevance
    "south china sea": 5,
    "west philippine sea": 5,
    "philippine sea": 5,
    "luzon strait": 5,
    "batanes": 5,
    "palawan": 4,
    "scarborough shoal": 6,
    "second thomas shoal": 6,
    "taiwan strait": 5,
    "edca": 4,
}


ESCALATION_FLAGS = {
    "CONTACT / COLLISION": ["collision", "rammed", "hit", "crash"],
    "COERCIVE MARITIME ACTION": ["water cannon", "harassment", "blocked", "blockade"],
    "INTERCEPT / SHADOWING": ["intercept", "shadowing", "tailed"],
    "MISSILE / STRIKE SYSTEM": ["missile", "anti-ship", "himars", "nmesis"],
    "AIRSPACE / AVIATION RESTRICTION": ["notam", "airspace closure", "flight restriction"],
    "CHINA RESPONSE": ["china", "pla", "chinese coast guard", "ccg"],
    "EXERCISE-DRIVEN ACTIVITY": ["exercise", "drill", "live-fire", "gunnery"],
}


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def dedupe_key(title: str) -> str:
    title = title.lower()
    title = re.sub(r"[^a-z0-9 ]", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title[:140]


def score_text(text: str) -> tuple[int, list[str]]:
    t = text.lower()
    score = 0
    matched = []

    for keyword, value in KEYWORD_SCORES.items():
        if keyword in t:
            score += value
            matched.append(keyword)

    return score, matched


def escalation_flags(text: str) -> list[str]:
    t = text.lower()
    flags = []

    for label, terms in ESCALATION_FLAGS.items():
        if any(term in t for term in terms):
            flags.append(label)

    return flags


def classify_activity(score: int, flags: list[str]) -> str:
    critical_flags = {
        "CONTACT / COLLISION",
        "COERCIVE MARITIME ACTION",
        "AIRSPACE / AVIATION RESTRICTION",
    }

    if any(flag in critical_flags for flag in flags) or score >= 20:
        return "HIGH"

    if score >= 10:
        return "MODERATE"

    return "LOW"


def fetch_source(source_name: str, source_url: str) -> list[dict]:
    headers = {
        "User-Agent": "Mozilla/5.0 mission-intel-osint-monitor/1.0"
    }

    try:
        response = requests.get(source_url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(response.text, "lxml")
    hits = []

    for a in soup.find_all("a", href=True):
        title = normalize_text(a.get_text(" ", strip=True))
        if len(title) < 25:
            continue

        url = urljoin(source_url, a["href"])
        combined = f"{title} {url}"

        score, matched = score_text(combined)
        if score <= 0:
            continue

        flags = escalation_flags(combined)

        hits.append({
            "source": source_name,
            "title": title,
            "url": url,
            "score": score,
            "matched": matched,
            "flags": flags,
            "classification": classify_activity(score, flags),
        })

    return hits


def build_content(hits: list[dict]) -> str:
    if not hits:
        return ""

    high = sum(1 for h in hits if h["classification"] == "HIGH")
    moderate = sum(1 for h in hits if h["classification"] == "MODERATE")
    low = sum(1 for h in hits if h["classification"] == "LOW")

    lines = [
        SECTION_NAME,
        "",
        f"Collection Summary: {len(hits)} reportable item(s) detected.",
        f"Activity Classification: HIGH={high} / MODERATE={moderate} / LOW={low}",
        "",
        "Reportable Items:",
    ]

    for h in hits:
        flags = ", ".join(h["flags"]) if h["flags"] else "None"
        matched = ", ".join(h["matched"][:6])

        lines.extend([
            f"- [{h['classification']}] [{h['source']}] {h['title']}",
            f"  URL: {h['url']}",
            f"  Score: {h['score']}",
            f"  Escalation Flags: {flags}",
            f"  Matched Indicators: {matched}",
            "",
        ])

    lines.extend([
        "Assessment:",
        "- LOW indicates routine military/security reporting or general exercise activity.",
        "- MODERATE indicates meaningful regional posture, movement, or disputed-area relevance.",
        "- HIGH indicates confrontation, coercive maritime activity, missile/strike-system activity, or airspace/aviation restriction indicators.",
        "",
        "Operational Impact:",
        "- Monitor for embassy alert changes, airport disruption, NOTAMs, airspace restrictions, maritime confrontation, and protest activity near U.S.-linked sites.",
        "",
        "Confidence: Medium",
    ])

    return "\n".join(lines).strip()


def collect_regional_military_activity() -> SourcePayload:
    raw_hits = []

    for source_name, source_url in SOURCES:
        raw_hits.extend(fetch_source(source_name, source_url))

    seen = set()
    deduped = []

    for hit in raw_hits:
        key = dedupe_key(hit["title"])

        if key in seen:
            continue

        seen.add(key)
        deduped.append(hit)

    deduped.sort(
        key=lambda h: (
            {"HIGH": 3, "MODERATE": 2, "LOW": 1}[h["classification"]],
            h["score"],
        ),
        reverse=True,
    )

    deduped = deduped[:20]

    now_utc = datetime.now(timezone.utc)

    payload = SourcePayload(
        source_name="Regional Military Activity",
        section_name=SECTION_NAME,
        content=build_content(deduped),
        retrieved_at_utc=now_utc,
        source_timestamp_utc=now_utc,
        raw_metadata={
            "provider": "regional_military_activity",
            "live_mode": True,
            "hit_count": len(deduped),
            "high_count": sum(1 for h in deduped if h["classification"] == "HIGH"),
            "moderate_count": sum(1 for h in deduped if h["classification"] == "MODERATE"),
            "low_count": sum(1 for h in deduped if h["classification"] == "LOW"),
        },
    )

    setattr(payload, "category", "Priority Intelligence")

    return payload
