def classify_upload_mode(report_status: str, is_rerun: bool) -> dict:
    if report_status == "failed":
        return {
            "upload_archive": False,
            "upload_latest": False,
            "reason": "Failed reports should not overwrite user-facing latest output.",
        }

    if report_status == "degraded" and is_rerun:
        return {
            "upload_archive": True,
            "upload_latest": True,
            "reason": "Degraded rerun allowed; latest may still be updated if validation passed.",
        }

    return {
        "upload_archive": True,
        "upload_latest": True,
        "reason": "Standard upload path.",
    }