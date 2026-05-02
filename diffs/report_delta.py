from pathlib import Path
import difflib


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def diff_text(old_text: str, new_text: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            old_text.splitlines(),
            new_text.splitlines(),
            fromfile="previous",
            tofile="current",
            lineterm="",
        )
    )


def count_diff_lines(diff_text_value: str) -> int:
    if not diff_text_value:
        return 0
    return len(diff_text_value.splitlines())