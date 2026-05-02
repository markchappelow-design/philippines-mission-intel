from __future__ import annotations

import requests


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}


def get_text(url: str, timeout_sec: int) -> str:
    response = requests.get(url, timeout=timeout_sec, headers=DEFAULT_HEADERS)
    response.raise_for_status()
    return response.text


def get_json(url: str, timeout_sec: int) -> dict:
    response = requests.get(url, timeout=timeout_sec, headers=DEFAULT_HEADERS)
    response.raise_for_status()
    return response.json()