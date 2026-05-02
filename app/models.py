from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SourceItem:
    source_name: str
    source_url: str
    section_target: str
    title: str
    published_time_original: str
    published_time_utc: str
    extracted_text: str
    reliability_tier: int
    fetch_status: str = "ok"
    error_text: Optional[str] = None
    parser_name: Optional[str] = None
    source_type: Optional[str] = None
    critical: bool = False


@dataclass
class SectionContext:
    heading: str
    confidence: str
    source_count: int
    items: List[SourceItem] = field(default_factory=list)


@dataclass
class ReportBuildResult:
    report_text: str
    word_count: int
    sections_present: List[str] = field(default_factory=list)
    status: str = "complete"