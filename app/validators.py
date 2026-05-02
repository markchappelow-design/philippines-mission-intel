from app.section_mapper import REQUIRED_HEADINGS


REQUIRED_CLOSING_LABELS = [
    "Assessment Confidence:",
    "Key Changes Since Prior Report:",
    "Watch Items for Next 24–72 Hours:",
    "Source Note:",
]


def validate_report_text(report_text: str, required_title: str) -> dict:
    errors = []

    title_ok = required_title in report_text
    if not title_ok:
        errors.append("Missing exact report title.")

    word_count = len(report_text.split())
    if word_count < 700:
        errors.append(f"Report below minimum word count: {word_count}")

    missing_headings = [h for h in REQUIRED_HEADINGS if h not in report_text]
    if missing_headings:
        errors.append(f"Missing headings: {missing_headings}")

    missing_closing_labels = [label for label in REQUIRED_CLOSING_LABELS if label not in report_text]
    if missing_closing_labels:
        errors.append(f"Missing closing labels: {missing_closing_labels}")

    return {
        "ok": len(errors) == 0,
        "status": "complete" if len(errors) == 0 else "failed",
        "errors": errors,
        "word_count": word_count,
        "missing_headings": missing_headings,
        "missing_closing_labels": missing_closing_labels,
        "title_ok": title_ok,
    }