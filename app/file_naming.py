from datetime import datetime, timezone


def build_report_stamp(report_timestamp: datetime) -> str:
    return report_timestamp.astimezone(timezone.utc).strftime("%Y-%m-%d_0001Z")


def build_output_names(report_timestamp: datetime) -> dict:
    stamp = build_report_stamp(report_timestamp)
    return {
        "docx_archive": f"Philippines_Mission_Intel_Status_Report_{stamp}.docx",
        "markdown_archive": f"Philippines_Mission_Intel_Status_Report_{stamp}.md",
        "pdf_archive": f"Philippines_Mission_Intel_Status_Report_{stamp}.pdf",
        "source_log": f"Philippines_Mission_Intel_Status_Report_{stamp}.source_log.json",
        "validation": f"Philippines_Mission_Intel_Status_Report_{stamp}.validation.json",
        "manifest": f"Philippines_Mission_Intel_Status_Report_{stamp}.manifest.json",
        "latest_docx": "LATEST - Philippines Mission Intel Status Report.docx",
        "latest_pdf": "LATEST - Philippines Mission Intel Status Report.pdf",
    }