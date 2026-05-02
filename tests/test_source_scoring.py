from app.models import SourceItem
from app.source_scoring import score_source_item


def test_score_source_item():
    item = SourceItem(
        source_name="A",
        source_url="x",
        section_target="s",
        title="t",
        published_time_original="unknown",
        published_time_utc="unknown",
        extracted_text="x" * 500,
        reliability_tier=1,
        critical=True,
    )
    assert score_source_item(item) >= 10