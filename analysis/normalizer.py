# analysis/normalizer.py
from __future__ import annotations

import re

from analysis.event_model import Event


def normalize_text(text: str) -> str:
    text = text or ""
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def payload_to_event(payload) -> Event:
    return Event(
        section_name=payload.section_name,
        source_name=payload.source_name,
        raw_text=payload.content,
        normalized_text=normalize_text(payload.content).lower(),
        tags=[],
    )


def payloads_to_events(payloads) -> list[Event]:
    return [payload_to_event(p) for p in payloads]