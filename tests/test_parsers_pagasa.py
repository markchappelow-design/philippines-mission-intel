from app.parsers_pagasa import parse_pagasa


def test_parse_pagasa_basic():
    html = """
    <html><head><title>PAGASA Bulletin</title></head>
    <body><h1>Weather Advisory</h1><p>Tropical cyclone bulletin in effect.</p></body></html>
    """
    result = parse_pagasa(html)
    assert result["title"] == "PAGASA Bulletin"
    assert "Tropical cyclone bulletin" in result["summary_text"]