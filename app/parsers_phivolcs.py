from app.parsers_common import clean_html_text, extract_page_title, keyword_slice


PHIVOLCS_KEYWORDS = [
    "earthquake",
    "volcano",
    "volcanic",
    "seismic",
    "geothermal",
    "advisory",
    "bulletin",
    "taal",
    "mayon",
    "kanlaon",
]


def parse_phivolcs(html: str) -> dict:
    text = clean_html_text(html, max_chars=25000)
    focused = keyword_slice(text, PHIVOLCS_KEYWORDS, window=2500)
    return {
        "title": extract_page_title(html),
        "summary_text": focused,
        "parser_name": "parse_phivolcs",
    }