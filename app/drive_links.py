def build_drive_file_link(file_id: str) -> str:
    return f"https://drive.google.com/file/d/{file_id}/view"


def build_drive_doc_link(file_id: str) -> str:
    return f"https://docs.google.com/document/d/{file_id}/edit"


def extract_uploaded_file_links(uploaded_files: dict) -> dict:
    links = {}
    for key, payload in uploaded_files.items():
        file_id = payload.get("id")
        if not file_id:
            continue
        links[key] = build_drive_file_link(file_id)
    return links