import feedparser
from typing import List, Dict


def fetch_rss_entries(feed_url: str, limit: int = 10) -> List[Dict]:
    parsed = feedparser.parse(feed_url)
    entries = []

    for entry in parsed.entries[:limit]:
        entries.append(
            {
                "title": getattr(entry, "title", ""),
                "link": getattr(entry, "link", ""),
                "published": getattr(entry, "published", ""),
                "summary": getattr(entry, "summary", ""),
            }
        )

    return entries