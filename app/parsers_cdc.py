from app.parsers_common import clean_html_text, extract_page_title, keyword_slice


CDC_KEYWORDS = [
    "vaccines",
    "vaccinations",
    "immunizations",
    "travel health",
    "routine vaccines",
    "hep",
    "rabies",
    "malaria",
    "measles",
]


def parse_cdc(html: str) -> dict:
    text = clean_html_text(html, max_chars=22000)
    focused = keyword_slice(text, CDC_KEYWORDS, window=2400)
    return {
        "title": extract_page_title(html),
        "summary_text": focused,
        "parser_name": "parse_cdc",
    }