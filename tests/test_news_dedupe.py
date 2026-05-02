from app.news_dedupe import dedupe_news_items


def test_dedupe_news_items():
    items = [
        {"title": "Flight disruption", "summary": "Airspace closure near conflict zone"},
        {"title": "Flight disruption", "summary": "Airspace closure near conflict zone"},
    ]
    result = dedupe_news_items(items)
    assert len(result) == 1