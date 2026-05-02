from clients.http_client import get_text
import json
from pprint import pprint

urls = [
    "https://newnaia.com.ph/api/v1/page/news",
    "https://newnaia.com.ph/api/v1/page/news/",
]

for url in urls:
    print(f"\n=== URL: {url} ===")
    raw = get_text(url, 15)
    print("RAW_LEN =", len(raw))
    print("RAW_HEAD =", raw[:500])

    try:
        data = json.loads(raw)
    except Exception as exc:
        print("JSON_ERROR =", type(exc).__name__, str(exc))
        continue

    print("TYPE =", type(data).__name__)

    if isinstance(data, dict):
        print("TOP_LEVEL_KEYS =", list(data.keys())[:50])

        for key in list(data.keys())[:20]:
            value = data[key]
            print(f"\nKEY = {key}")
            print("VALUE_TYPE =", type(value).__name__)
            if isinstance(value, dict):
                print("DICT_KEYS =", list(value.keys())[:30])
            elif isinstance(value, list):
                print("LIST_LEN =", len(value))
                if value:
                    print("FIRST_ITEM_TYPE =", type(value[0]).__name__)
                    if isinstance(value[0], dict):
                        print("FIRST_ITEM_KEYS =", list(value[0].keys())[:30])
                        pprint(value[0])
                    else:
                        pprint(value[0])
            else:
                pprint(value)

    elif isinstance(data, list):
        print("LIST_LEN =", len(data))
        if data:
            print("FIRST_ITEM_TYPE =", type(data[0]).__name__)
            if isinstance(data[0], dict):
                print("FIRST_ITEM_KEYS =", list(data[0].keys())[:30])
                pprint(data[0])
            else:
                pprint(data[0])