from app.parsers_aviation import parse_aviation


def test_parse_aviation_basic():
    html = """
    <html><head><title>Aviation Update</title></head>
    <body><p>Airspace closure causes rerouting and flight disruption.</p></body></html>
    """
    result = parse_aviation(html)
    assert result["title"] == "Aviation Update"
    assert "Airspace closure" in result["summary_text"]