# analysis/event_model.py
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Event:
    section_name: str
    source_name: str
    raw_text: str
    normalized_text: str
    tags: list[str] = field(default_factory=list)