from clients.http_client import get_text
import re

page_url = "https://newnaia.com.ph/about-us/news"

print("STEP 1: fetching page")
html = get_text(page_url, 15)
print("HTML_LEN =", len(html))

m = re.search(r'<script type="module" crossorigin src="([^"]+)"', html, re.I)
bundle = m.group(1) if m else None
print("BUNDLE =", bundle)

if not bundle:
    raise SystemExit("No JS bundle found in page HTML")

bundle_url = "https://newnaia.com.ph" + bundle if bundle.startswith("/") else bundle
print("BUNDLE_URL =", bundle_url)

print("STEP 2: fetching bundle")
js = get_text(bundle_url, 15)
print("JS_LEN =", len(js))

tokens = ["api", "news", "articles", "media", "fetch(", "/about-us/news", "axios", "graphql"]
for token in tokens:
    if token.lower() in js.lower():
        print("FOUND:", token)

print("\nSTEP 3: nearby 'news' hits")
hits = [x.start() for x in re.finditer("news", js.lower())][:20]
print("HITS =", len(hits))

for i, pos in enumerate(hits[:10], start=1):
    print(f"\n--- HIT {i} @ {pos} ---")
    print(js[max(0, pos - 200):pos + 400])