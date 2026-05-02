from app.parsers_embassy import parse_embassy


def test_parse_embassy_basic():
    html = """
    <html><head><title>Embassy Alert</title></head>
    <body><p>Security alert for U.S. citizens in Manila.</p></body></html>
    """
    result = parse_embassy(html)
    assert result["title"] == "Embassy Alert"
    assert "Security alert" in result["summary_text"]