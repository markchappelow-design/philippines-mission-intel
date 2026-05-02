from app.confidence import compute_section_confidence
from app.models import SourceItem


def test_compute_section_confidence_high():
    items = [
        SourceItem(
            source_name="A",
            source_url="x",
            section_target="s",
            title="t1",
            published_time_original="unknown",
            published_time_utc="unknown",
            extracted_text="abc",
            reliability_tier=1,
        ),
        SourceItem(
            source_name="B",
            source_url="y",
            section_target="s",
            title="t2",
            published_time_original="unknown",
            published_time_utc="unknown",
            extracted_text="def",
            reliability_tier=1,
        ),
    ]
    assert compute_section_confidence(items) == "High"