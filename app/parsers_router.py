from app.parsers_cdc import parse_cdc
from app.parsers_embassy import parse_embassy
from app.parsers_naia import parse_naia
from app.parsers_pagasa import parse_pagasa
from app.parsers_phivolcs import parse_phivolcs
from app.parsers_state import parse_state_department
from app.parsers_common import clean_html_text, extract_page_title


def parse_by_source(source_name: str, html: str) -> dict:
    mapping = {
        "PAGASA": parse_pagasa,
        "PHIVOLCS": parse_phivolcs,
        "US Embassy Manila": parse_embassy,
        "US State Department Philippines Travel Advisory": parse_state_department,
        "CDC Travelers Health Philippines": parse_cdc,
        "NAIA": parse_naia,
    }

    parser = mapping.get(source_name)
    if parser:
        return parser(html)

    return {
        "title": extract_page_title(html),
        "summary_text": clean_html_text(html, max_chars=12000),
        "parser_name": "default_parser",
    }