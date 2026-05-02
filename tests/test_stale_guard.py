from app.models import SourceItem
from app.stale_guard import classify_stale_items


def test_classify_stale_items_unknown_allowed():
    items = [
        SourceItem(
            source_name="A",
            source_url="x",
            section_target="s",
            title="t",
            published_time_original="unknown",
            published_time_utc="unknown",
            extracted_text="abc",
            reliability_tier=1,
        )
    ]
    result = classify_stale_items(items, unknown_is_fresh=True)
    assert len(result["fresh"]) == 1
    assert len(result["stale"]) == 0