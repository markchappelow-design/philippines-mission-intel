from app.drive_client import ensure_subfolder


def ensure_drive_layout(service_account_json: str, root_folder_id: str) -> dict:
    archive_id = ensure_subfolder(service_account_json, root_folder_id, "Archive")
    source_logs_id = ensure_subfolder(service_account_json, root_folder_id, "Source_Logs")
    failures_id = ensure_subfolder(service_account_json, root_folder_id, "Failures")

    return {
        "root_folder_id": root_folder_id,
        "archive_folder_id": archive_id,
        "source_logs_folder_id": source_logs_id,
        "failures_folder_id": failures_id,
    }