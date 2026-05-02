import json
from pathlib import Path

from app.config import get_settings, validate_settings
from app.degraded_notifier import send_degraded_notification
from app.delta_compare import summarize_source_deltas
from app.docx_writer import write_docx
from app.drive_client import upload_file_to_folder, upsert_file_in_folder
from app.drive_layout import ensure_drive_layout
from app.drive_links import extract_uploaded_file_links
from app.email_notifier import send_email_notification
from app.failure_notifier import send_failure_notification
from app.fetchers import fetch_all_sources
from app.file_naming import build_output_names
from app.history_store import load_previous_source_log, save_previous_source_log
from app.llm_writer import generate_report
from app.logging_config import configure_logging
from app.markdown_writer import write_markdown
from app.pdf_writer import write_pdf
from app.report_manifest import build_manifest, write_manifest
from app.report_status import determine_report_status
from app.retry_runner import run_with_retries
from app.run_lock import acquire_run_lock, release_run_lock
from app.section_enricher import build_section_context
from app.source_registry import load_source_registry
from app.stale_guard import classify_stale_items, stale_summary
from app.status_banner import get_generation_status
from app.upload_cleanup import classify_upload_mode
from app.utils import ensure_dir, get_report_timestamp_utc
from app.validators import validate_report_text


def _notify_success(settings, subject: str, body: str) -> None:
    if not settings.email_notify_enabled or not settings.email_notify_to:
        return

    send_email_notification(
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_username=settings.smtp_username,
        smtp_password=settings.smtp_password,
        sender=settings.smtp_sender,
        recipient=settings.email_notify_to,
        subject=subject,
        body=body,
    )


def _notify_failure(settings, subject: str, body: str) -> None:
    if not settings.email_notify_enabled or not settings.email_notify_to:
        return

    send_failure_notification(
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_username=settings.smtp_username,
        smtp_password=settings.smtp_password,
        sender=settings.smtp_sender,
        recipient=settings.email_notify_to,
        subject=subject,
        body=body,
    )


def _notify_degraded(settings, subject: str, body: str) -> None:
    if not settings.email_notify_enabled or not settings.email_notify_to:
        return

    send_degraded_notification(
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_username=settings.smtp_username,
        smtp_password=settings.smtp_password,
        sender=settings.smtp_sender,
        recipient=settings.email_notify_to,
        subject=subject,
        body=body,
    )


def build_once(settings):
    report_timestamp = get_report_timestamp_utc()
    names = build_output_names(report_timestamp)

    ensure_dir("output")
    registry = load_source_registry()
    items = fetch_all_sources(registry)

    stale_result = classify_stale_items(items, unknown_is_fresh=True)
    usable_items = [
        item for item in items
        if item.fetch_status == "ok" and item not in stale_result["stale"]
    ]

    previous_source_log = load_previous_source_log()
    current_source_log_payload = [item.__dict__ for item in usable_items]
    delta_lines = summarize_source_deltas(current_source_log_payload, previous_source_log)
    delta_lines.extend(stale_summary(stale_result["stale"]))
    section_context = build_section_context(usable_items)

    report_text = generate_report(
        openai_api_key=settings.openai_api_key,
        model=settings.openai_model,
        items=usable_items,
        section_context=section_context,
        delta_lines=delta_lines,
    )

    validation = validate_report_text(report_text, settings.report_title)
    generation_status = get_generation_status(items)
    report_status = determine_report_status(validation["ok"], generation_status)

    docx_archive_path = str(Path("output") / names["docx_archive"])
    latest_docx_path = str(Path("output") / names["latest_docx"])
    markdown_archive_path = str(Path("output") / names["markdown_archive"])
    pdf_archive_path = str(Path("output") / names["pdf_archive"])
    latest_pdf_path = str(Path("output") / names["latest_pdf"])
    source_log_path = Path("output") / names["source_log"]
    validation_path = Path("output") / names["validation"]
    manifest_path = Path("output") / names["manifest"]

    write_docx(report_text, docx_archive_path)
    write_docx(report_text, latest_docx_path)
    write_markdown(report_text, markdown_archive_path)

    if settings.pdf_output_enabled:
        write_pdf(report_text, pdf_archive_path)
        write_pdf(report_text, latest_pdf_path)

    source_log_path.write_text(json.dumps(current_source_log_payload, indent=2), encoding="utf-8")
    validation_path.write_text(
        json.dumps(
            {
                **validation,
                "generation_status": generation_status,
                "report_status": report_status,
                "delta_lines": delta_lines,
                "stale_exclusions": stale_summary(stale_result["stale"]),
                "section_context": {
                    k: {
                        "confidence": v["confidence"],
                        "source_count": v["source_count"],
                    }
                    for k, v in section_context.items()
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    upload_mode = classify_upload_mode(report_status=report_status, is_rerun=False)

    uploaded_files = {}
    if validation["ok"]:
        drive_layout = ensure_drive_layout(
            settings.google_service_account_json,
            settings.google_drive_target_folder_id,
        )

        if upload_mode["upload_archive"]:
            uploaded_files["archive_docx"] = upload_file_to_folder(
                settings.google_service_account_json,
                drive_layout["archive_folder_id"],
                docx_archive_path,
                names["docx_archive"],
            )
            if settings.pdf_output_enabled:
                uploaded_files["archive_pdf"] = upload_file_to_folder(
                    settings.google_service_account_json,
                    drive_layout["archive_folder_id"],
                    pdf_archive_path,
                    names["pdf_archive"],
                )
            uploaded_files["source_log"] = upload_file_to_folder(
                settings.google_service_account_json,
                drive_layout["source_logs_folder_id"],
                str(source_log_path),
                names["source_log"],
            )
            uploaded_files["validation"] = upload_file_to_folder(
                settings.google_service_account_json,
                drive_layout["source_logs_folder_id"],
                str(validation_path),
                names["validation"],
            )

        if upload_mode["upload_latest"]:
            uploaded_files["latest_docx"] = upsert_file_in_folder(
                settings.google_service_account_json,
                drive_layout["root_folder_id"],
                latest_docx_path,
                names["latest_docx"],
            )
            if settings.pdf_output_enabled:
                uploaded_files["latest_pdf"] = upsert_file_in_folder(
                    settings.google_service_account_json,
                    drive_layout["root_folder_id"],
                    latest_pdf_path,
                    names["latest_pdf"],
                )

    uploaded_links = extract_uploaded_file_links(uploaded_files)

    manifest = build_manifest(
        report_timestamp=report_timestamp.strftime("%Y-%m-%d %H:%M:%SZ"),
        generation_status=generation_status,
        validation=validation,
        names=names,
        uploaded_files=uploaded_files,
        report_status=report_status,
        stale_exclusions=stale_summary(stale_result["stale"]),
        uploaded_links=uploaded_links,
    )
    write_manifest(manifest, str(manifest_path))

    if validation["ok"]:
        save_previous_source_log(current_source_log_payload)

    return {
        "report_text": report_text,
        "validation": validation,
        "generation_status": generation_status,
        "report_status": report_status,
        "names": names,
        "manifest_path": str(manifest_path),
        "stale_exclusions": stale_summary(stale_result["stale"]),
        "uploaded_links": uploaded_links,
    }


def main() -> None:
    configure_logging()
    settings = get_settings()
    validate_settings(settings)

    acquire_run_lock()
    try:
        result = run_with_retries(
            lambda: build_once(settings),
            attempts=3,
            delays_seconds=[0, 600, 900],
        )

        if result["report_status"] == "failed":
            subject = f"FAILED - Philippines Mission Intel Status Report - {result['names']['docx_archive']}"
            body = (
                f"Report status: {result['report_status']}\n"
                f"Validation errors: {result['validation']['errors']}\n"
                f"Manifest: {result['manifest_path']}\n"
            )
            _notify_failure(settings, subject, body)
        elif result["report_status"] == "degraded":
            subject = f"DEGRADED - Philippines Mission Intel Status Report - {result['names']['docx_archive']}"
            body = (
                f"Generation status: {result['generation_status']}\n"
                f"Report status: {result['report_status']}\n"
                f"Report file: {result['names']['docx_archive']}\n"
                f"LATEST file: {result['names']['latest_docx']}\n"
                f"Links: {result['uploaded_links']}\n"
                f"Manifest: {result['manifest_path']}\n"
                f"Stale exclusions: {result['stale_exclusions']}\n"
            )
            _notify_degraded(settings, subject, body)
        else:
            subject = f"Philippines Mission Intel Status Report Ready - {result['names']['docx_archive']}"
            body = (
                f"Generation status: {result['generation_status']}\n"
                f"Report status: {result['report_status']}\n"
                f"Report file: {result['names']['docx_archive']}\n"
                f"LATEST file: {result['names']['latest_docx']}\n"
                f"Links: {result['uploaded_links']}\n"
                f"Manifest: {result['manifest_path']}\n"
                f"Stale exclusions: {result['stale_exclusions']}\n"
            )
            _notify_success(settings, subject, body)

        print(json.dumps(result["validation"], indent=2))
        print(f"Generation status: {result['generation_status']}")
        print(f"Report status: {result['report_status']}")
        print("Report build flow complete.")
    finally:
        release_run_lock()

print("Operator note: verify Drive archive, latest outputs, and manifest after first production run.")

if __name__ == "__main__":
    main()