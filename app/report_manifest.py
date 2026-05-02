import json
from pathlib import Path


def build_manifest(
    report_timestamp: str,
    generation_status: str,
    validation: dict,
    names: dict,
    uploaded_files: dict,
    report_status: str,
    stale_exclusions: list[str] | None = None,
    uploaded_links: dict | None = None,
) -> dict:
    return {
        "report_timestamp": report_timestamp,
        "generation_status": generation_status,
        "report_status": report_status,
        "validation": validation,
        "output_files": names,
        "uploaded_files": uploaded_files,
        "uploaded_links": uploaded_links or {},
        "stale_exclusions": stale_exclusions or [],
    }


def write_manifest(manifest: dict, output_path: str) -> None:
    Path(output_path).write_text(json.dumps(manifest, indent=2), encoding="utf-8")