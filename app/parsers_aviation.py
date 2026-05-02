from app.parsers_common import clean_html_text, extract_page_title, keyword_slice


AVIATION_KEYWORDS = [
    "airspace",
    "flight disruption",
    "rerouting",
    "cancellation",
    "notam",
    "advisory",
    "airline",
    "airport",
    "conflict",
    "security",
    "missile",
    "closure",
    "diversion",
]


def parse_aviation(html: str) -> dict:
    text = clean_html_text(html, max_chars=25000)
    focused = keyword_slice(text, AVIATION_KEYWORDS, window=2600)
    return {
        "title": extract_page_title(html),
        "summary_text": focused,
        "parser_name": "parse_aviation",
    }