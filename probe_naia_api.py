from clients.http_client import get_text

candidates = [
    "https://newnaia.com.ph/api/news",
    "https://newnaia.com.ph/api/news/",
    "https://newnaia.com.ph/api/get/news",
    "https://newnaia.com.ph/api/v1/news",
    "https://newnaia.com.ph/news",
    "https://newnaia.com.ph/advisories",
]

for url in candidates:
    print(f"\n=== TESTING {url} ===")
    try:
        text = get_text(url, 15)
        print("LEN =", len(text))
        print(text[:800])
    except Exception as exc:
        print("ERROR =", type(exc).__name__, str(exc))