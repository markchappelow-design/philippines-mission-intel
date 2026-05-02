from app.parsers_maritime import parse_maritime


def test_parse_maritime_basic():
    html = """
    <html><head><title>Maritime Incident</title></head>
    <body><p>South China Sea incident involving Philippine Coast Guard and Chinese vessel.</p></body></html>
    """
    result = parse_maritime(html)
    assert result["title"] == "Maritime Incident"
    assert "Philippine Coast Guard" in result["summary_text"]