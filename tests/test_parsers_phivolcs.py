from app.parsers_phivolcs import parse_phivolcs


def test_parse_phivolcs_basic():
    html = """
    <html><head><title>PHIVOLCS Advisory</title></head>
    <body><p>Earthquake information and volcanic activity update.</p></body></html>
    """
    result = parse_phivolcs(html)
    assert result["title"] == "PHIVOLCS Advisory"
    assert "Earthquake information" in result["summary_text"]