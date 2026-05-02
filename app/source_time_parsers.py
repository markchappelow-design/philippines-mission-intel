from bs4 import BeautifulSoup


TIME_META_KEYS = [
    "article:published_time",
    "og:published_time",
    "publish-date",
    "date",
    "dc.date",
]


def extract_time_from_meta(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    for tag in soup.find_all("meta"):
        prop = (tag.get("property") or tag.get("name") or "").strip().lower()
        content = (tag.get("content") or "").strip()
        if prop in TIME_META_KEYS and content:
            return content

    for time_tag in soup.find_all("time"):
        dt = (time_tag.get("datetime") or "").strip()
        if dt:
            return dt

    return "unknown"


def extract_time_by_source(source_name: str, html: str) -> str:
    return extract_time_from_meta(html)