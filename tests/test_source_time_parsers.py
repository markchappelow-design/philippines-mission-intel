from app.source_time_parsers import extract_time_from_meta


def test_extract_time_from_meta():
    html = """
    <html>
      <head>
        <meta property="article:published_time" content="2026-03-12T00:01:00+00:00">
      </head>
      <body></body>
    </html>
    """
    result = extract_time_from_meta(html)
    assert result == "2026-03-12T00:01:00+00:00"