import json
from pathlib import Path


def load_source_registry() -> list[dict]:
    path = Path("app/source_registry.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    return [item for item in data if item.get("enabled", True)]