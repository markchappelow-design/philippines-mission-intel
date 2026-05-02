from clients.http_client import get_text
import re

page_url = "https://newnaia.com.ph/about-us/news"

print("STEP 1: fetch page")
html = get_text(page_url, 15)

m = re.search(r'<script type="module" crossorigin src="([^"]+)"', html, re.I)
if not m:
    raise SystemExit("No JS bundle found")

bundle_url = "https://newnaia.com.ph" + m.group(1)
print("BUNDLE_URL =", bundle_url)

print("STEP 2: fetch bundle")
js = get_text(bundle_url, 15)
print("JS_LEN =", len(js))

checks = [
    "baseURL",
    "axios.create",
    "fetch(",
    'url:"news"',
    "url:'news'",
    "publish_date",
    "/api/",
    "VITE_",
    "import.meta.env",
]

for token in checks:
    print(f"HAS {token} =", token in js)

print("\nSTEP 3: context around url:\"news\" or url:'news'\n")

patterns = [r'url:"news"', r"url:'news'"]
found = False

for pat in patterns:
    for match in re.finditer(pat, js):
        found = True
        pos = match.start()
        print("=" * 100)
        print(js[max(0, pos - 1200):pos + 2500])
        print("=" * 100)
        print()
        break
    if found:
        break

print("\nSTEP 4: possible base URL strings\n")

base_patterns = [
    r'baseURL:"([^"]+)"',
    r"baseURL:'([^']+)'",
    r'axios\.create\(\{[^}]*baseURL:\s*"([^"]+)"',
    r"axios\.create\(\{[^}]*baseURL:\s*'([^']+)'",
    r'fetch\("([^"]+/news[^"]*)"',
    r"fetch\('([^']+/news[^']*)'",
    r'"(/api/[^"]+)"',
    r"'(/api/[^']+)'",
]

seen = set()
for pat in base_patterns:
    for hit in re.findall(pat, js, re.I):
        if hit not in seen:
            seen.add(hit)
            print(hit)

print("\nSTEP 5: context around publish_date\n")

for match in re.finditer("publish_date", js):
    pos = match.start()
    print("=" * 100)
    print(js[max(0, pos - 1200):pos + 2500])
    print("=" * 100)
    print()
    break