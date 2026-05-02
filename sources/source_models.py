from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SourceRecord:
    source_name: str
    source_type: str
    required: bool
    retrieved_at_utc: datetime
    source_timestamp_utc: datetime
    max_age_hours: float
    notes: str = ""


@dataclass
class SourcePayload:
    source_name: str
    section_name: str
    content: str

    source_type: str = "DOCUMENT"
    required: bool = True

    retrieved_at_utc: datetime | None = None
    source_timestamp_utc: datetime | None = None
    max_age_hours: int = 24

    notes: str = ""
    raw_metadata: dict = field(default_factory=dict)

    def to_source_record(self) -> SourceRecord:
        """
        Convert payload into freshness validator record format.
        """
        return SourceRecord(
            source_name=self.source_name,
            source_type=self.source_type,
            required=self.required,
            retrieved_at_utc=self.retrieved_at_utc,
            source_timestamp_utc=self.source_timestamp_utc,
            max_age_hours=self.max_age_hours,
            notes=self.notes,
        )