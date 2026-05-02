from app.parsers_common import clean_html_text, extract_page_title, keyword_slice


EMBASSY_KEYWORDS = [
    "alert",
    "security alert",
    "travel advisory",
    "message for u.s. citizens",
    "demonstration",
    "embassy",
    "consular",
    "advisory",
]


def parse_embassy(html: str) -> dict:
    text = clean_html_text(html, max_chars=25000)
    focused = keyword_slice(text, EMBASSY_KEYWORDS, window=2200)
    return {
        "title": extract_page_title(html),
        "summary_text": focused,
        "parser_name": "parse_embassy",
    }