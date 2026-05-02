def determine_report_status(validation_ok: bool, generation_status: str) -> str:
    if not validation_ok:
        return "failed"
    if generation_status == "degraded":
        return "degraded"
    return "complete"