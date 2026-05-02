from app.drive_links import build_drive_file_link, extract_uploaded_file_links


def test_build_drive_file_link():
    link = build_drive_file_link("123abc")
    assert link == "https://drive.google.com/file/d/123abc/view"


def test_extract_uploaded_file_links():
    payload = {"latest_docx": {"id": "abc123"}}
    links = extract_uploaded_file_links(payload)
    assert links["latest_docx"] == "https://drive.google.com/file/d/abc123/view"