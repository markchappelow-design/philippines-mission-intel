from app.parsers_common import clean_html_text, extract_page_title, keyword_slice


NAIA_KEYWORDS = [
    "advisory",
    "airport",
    "terminal",
    "passenger",
    "runway",
    "flight",
    "naia",
    "announcement",
    "operations",
]


def parse_naia(html: str) -> dict:
    text = clean_html_text(html, max_chars=25000)
    focused = keyword_slice(text, NAIA_KEYWORDS, window=2200)
    return {
        "title": extract_page_title(html),
        "summary_text": focused,
        "parser_name": "parse_naia",
    }