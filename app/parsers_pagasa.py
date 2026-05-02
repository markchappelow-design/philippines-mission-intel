from app.parsers_common import clean_html_text, extract_page_title, keyword_slice


PAGASA_KEYWORDS = [
    "tropical cyclone",
    "weather advisory",
    "gale warning",
    "rainfall warning",
    "thunderstorm",
    "forecast",
    "severe weather",
    "bulletin",
]


def parse_pagasa(html: str) -> dict:
    text = clean_html_text(html, max_chars=25000)
    focused = keyword_slice(text, PAGASA_KEYWORDS, window=2500)
    return {
        "title": extract_page_title(html),
        "summary_text": focused,
        "parser_name": "parse_pagasa",
    }