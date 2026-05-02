from bs4 import BeautifulSoup


def clean_html_text(html: str, max_chars: int = 20000) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())[:max_chars]


def extract_page_title(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    if soup.title and soup.title.text:
        return " ".join(soup.title.text.split())
    return "Untitled"


def keyword_slice(text: str, keywords: list[str], window: int = 1200) -> str:
    lowered = text.lower()
    for keyword in keywords:
        idx = lowered.find(keyword.lower())
        if idx >= 0:
            start = max(0, idx - 300)
            end = min(len(text), idx + window)
            return text[start:end]
    return text[:window]