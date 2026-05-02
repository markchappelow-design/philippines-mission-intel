from pathlib import Path


def write_markdown(report_text: str, output_path: str) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(report_text, encoding="utf-8")