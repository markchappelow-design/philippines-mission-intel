from clients.http_client import get_text
import re

page_url = "https://newnaia.com.ph/about-us/news"
html = get_text(page_url, 15)

m = re.search(r'<script type="module" crossorigin src="([^"]+)"', html, re.I)
if not m:
    raise SystemExit("No JS bundle found")

bundle_url = "https://newnaia.com.ph" + m.group(1)
js = get_text(bundle_url, 15)

# Find the exact call site first
call_match = re.search(r'Z\(\{url:"news".{0,400}\}\)', js, re.I)
if call_match:
    pos = call_match.start()
    print("=== CALL SITE CONTEXT ===")
    print(js[max(0, pos - 1200):pos + 2500])
    print()

# Find function definition / assignment for Z
patterns = [
    r'function Z\((.*?)\)\{',
    r'const Z\s*=\s*\((.*?)\)\s*=>\{',
    r'let Z\s*=\s*\((.*?)\)\s*=>\{',
    r'var Z\s*=\s*\((.*?)\)\s*=>\{',
    r'Z\s*=\s*\((.*?)\)\s*=>\{',
]

found = False
for pat in patterns:
    m2 = re.search(pat, js, re.I | re.DOTALL)
    if m2:
        found = True
        pos = m2.start()
        print("=== Z DEFINITION CONTEXT ===")
        print(js[max(0, pos - 500):pos + 5000])
        print()
        break

if not found:
    # Fallback: search for queryKey and url usage around Z-like helpers
    for token in ['queryKey:[', 'queryFn:async', 'url:"news"', 'publish_date', 'fetch(`${', 'fetch("', "fetch('"]:
        for m3 in re.finditer(re.escape(token), js):
            pos = m3.start()
            print(f"=== TOKEN CONTEXT: {token} ===")
            print(js[max(0, pos - 1000):pos + 2500])
            print()
            break