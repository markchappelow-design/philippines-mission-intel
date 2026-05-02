import json
from pathlib import Path


def save_previous_source_log(source_log: list[dict], path: str = "output/previous_source_log.json") -> None:
    Path(path).write_text(json.dumps(source_log, indent=2), encoding="utf-8")


def load_previous_source_log(path: str = "output/previous_source_log.json") -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))