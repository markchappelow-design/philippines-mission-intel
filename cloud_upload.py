import os
from pathlib import Path
from datetime import datetime, timezone

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ["https://www.googleapis.com/auth/drive"]


def upload_file(service, local_path: Path, folder_id: str, drive_name: str):
    metadata = {
        "name": drive_name,
        "parents": [folder_id],
    }

    media = MediaFileUpload(
        str(local_path),
        mimetype="application/pdf",
        resumable=True,
    )

    return service.files().create(
        body=metadata,
        media_body=media,
        fields="id,name",
        supportsAllDrives=True,
    ).execute()


def delete_existing_named_file(service, folder_id: str, filename: str):
    query = (
        f"'{folder_id}' in parents and "
        f"name = '{filename}' and "
        "trashed = false"
    )

    results = service.files().list(
        q=query,
        fields="files(id,name)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()

    for item in results.get("files", []):
        service.files().delete(
            fileId=item["id"],
            supportsAllDrives=True,
        ).execute()


def main():
    service_account_json = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
    latest_folder_id = os.environ["GDRIVE_LATEST_FOLDER_ID"]
    archive_folder_id = os.environ["GDRIVE_ARCHIVE_FOLDER_ID"]
    output_pdf = Path(os.environ.get("OUTPUT_PDF", "outputs/latest/philippines_intel_report.pdf"))

    if not output_pdf.exists():
        raise FileNotFoundError(f"PDF not found: {output_pdf}")

    credentials_path = Path("service_account.json")
    credentials_path.write_text(service_account_json, encoding="utf-8")

    creds = service_account.Credentials.from_service_account_file(
        str(credentials_path),
        scopes=SCOPES,
    )

    service = build("drive", "v3", credentials=creds)

    latest_name = "philippines_intel_report_latest.pdf"
    date_stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    archive_name = f"philippines_intel_report_{date_stamp}.pdf"

    delete_existing_named_file(service, latest_folder_id, latest_name)

    upload_file(service, output_pdf, latest_folder_id, latest_name)
    upload_file(service, output_pdf, archive_folder_id, archive_name)

    print(f"Uploaded latest: {latest_name}")
    print(f"Uploaded archive: {archive_name}")


if __name__ == "__main__":
    main()