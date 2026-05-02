import io
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_drive_service(service_account_json: str):
    info = json.loads(service_account_json)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def _make_media(local_path: str):
    with open(local_path, "rb") as f:
        return MediaIoBaseUpload(io.BytesIO(f.read()), resumable=True)


def find_file_in_folder(service_account_json: str, folder_id: str, filename: str):
    service = _get_drive_service(service_account_json)
    query = (
        f"'{folder_id}' in parents and "
        f"name = '{filename}' and trashed = false"
    )
    results = service.files().list(
        q=query,
        fields="files(id,name,parents,webViewLink)",
        pageSize=10,
    ).execute()
    files = results.get("files", [])
    return files[0] if files else None


def upload_file_to_folder(service_account_json: str, folder_id: str, local_path: str, remote_name: str):
    service = _get_drive_service(service_account_json)
    media = _make_media(local_path)

    metadata = {
        "name": remote_name,
        "parents": [folder_id],
    }

    return service.files().create(
        body=metadata,
        media_body=media,
        fields="id,name,parents,webViewLink",
    ).execute()


def upsert_file_in_folder(service_account_json: str, folder_id: str, local_path: str, remote_name: str):
    service = _get_drive_service(service_account_json)
    existing = find_file_in_folder(service_account_json, folder_id, remote_name)
    media = _make_media(local_path)

    if existing:
        return service.files().update(
            fileId=existing["id"],
            media_body=media,
            fields="id,name,parents,webViewLink",
        ).execute()

    metadata = {"name": remote_name, "parents": [folder_id]}
    return service.files().create(
        body=metadata,
        media_body=media,
        fields="id,name,parents,webViewLink",
    ).execute()


def ensure_subfolder(service_account_json: str, parent_folder_id: str, folder_name: str) -> str:
    service = _get_drive_service(service_account_json)
    query = (
        f"'{parent_folder_id}' in parents and "
        f"name = '{folder_name}' and "
        f"mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    results = service.files().list(
        q=query,
        fields="files(id,name)",
        pageSize=10,
    ).execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]

    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_folder_id],
    }
    created = service.files().create(body=metadata, fields="id,name").execute()
    return created["id"]