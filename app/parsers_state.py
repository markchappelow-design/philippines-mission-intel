from app.parsers_common import clean_html_text, extract_page_title, keyword_slice


STATE_KEYWORDS = [
    "travel advisory",
    "exercise increased caution",
    "do not travel",
    "reconsider travel",
    "country summary",
    "advisory",
]


def parse_state_department(html: str) -> dict:
    text = clean_html_text(html, max_chars=20000)
    focused = keyword_slice(text, STATE_KEYWORDS, window=2200)
    return {
        "title": extract_page_title(html),
        "summary_text": focused,
        "parser_name": "parse_state_department",
    }