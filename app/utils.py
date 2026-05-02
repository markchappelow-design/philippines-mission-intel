from datetime import datetime, timedelta, timezone
from pathlib import Path


def get_report_timestamp_utc() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=1, second=0, microsecond=0)


def get_reporting_window(timestamp_utc: datetime) -> tuple[str, str]:
    start = timestamp_utc - timedelta(days=1)
    return start.strftime("%Y-%m-%d %H%MZ"), timestamp_utc.strftime("%Y-%m-%d %H%MZ")


def build_output_names(timestamp_utc: datetime) -> dict:
    stamp = timestamp_utc.strftime("%Y-%m-%d_0001Z")
    return {
        "docx_archive": f"Philippines_Mission_Intel_Status_Report_{stamp}.docx",
        "markdown_archive": f"Philippines_Mission_Intel_Status_Report_{stamp}.md",
        "source_log": f"Philippines_Mission_Intel_Status_Report_{stamp}.source_log.json",
        "validation": f"Philippines_Mission_Intel_Status_Report_{stamp}.validation.json",
        "latest_docx": "LATEST - Philippines Mission Intel Status Report.docx",
    }


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)