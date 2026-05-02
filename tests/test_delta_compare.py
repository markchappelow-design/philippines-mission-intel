from app.delta_compare import summarize_source_deltas


def test_summarize_source_deltas():
    previous_items = [{"title": "Old Item"}]
    current_items = [{"title": "New Item"}]
    result = summarize_source_deltas(current_items, previous_items)
    joined = " ".join(result)
    assert "New Item" in joined
    assert "Old Item" in joined