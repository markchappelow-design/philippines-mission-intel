from app.parsers_common import clean_html_text, extract_page_title, keyword_slice


MARITIME_KEYWORDS = [
    "south china sea",
    "west philippine sea",
    "coast guard",
    "philippine navy",
    "water cannon",
    "harassment",
    "collision",
    "blockade",
    "shoal",
    "reef",
    "chinese vessel",
    "beijing",
    "scarborough",
    "second thomas",
]


def parse_maritime(html: str) -> dict:
    text = clean_html_text(html, max_chars=25000)
    focused = keyword_slice(text, MARITIME_KEYWORDS, window=2600)
    return {
        "title": extract_page_title(html),
        "summary_text": focused,
        "parser_name": "parse_maritime",
    }