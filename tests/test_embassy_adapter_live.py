from unittest.mock import patch

from sources.embassy_adapter import EmbassyManilaAdapter


@patch("sources.embassy_adapter.get_text")
def test_embassy_adapter_build_live_payload_parses_archive_style(mock_get_text):
    mock_get_text.return_value = """
    <html>
      <body>
        <p>Alerts. March 7, 2026. Security Alert – U.S. Embassy Manila – March 7, 2026 Read More</p>
        <p>Alerts. March 6, 2026. Demonstration Alert – Protest Activity in the Philippines Read More</p>
      </body>
    </html>
    """

    adapter = EmbassyManilaAdapter(api_url="https://example.com/embassy", timeout_sec=15)
    payload = adapter._build_live_payload()

    assert payload.source_name == "U.S. Embassy Manila Live"
    assert payload.section_name == "U.S. Embassy (Manila) travel advisories"
    assert payload.raw_metadata["live_mode"] is True
    assert "Security Alert" in payload.raw_metadata["latest_alert_title"]
    assert "March 7, 2026" in payload.raw_metadata["issued_date"]
    assert payload.source_type == "DOCUMENT"


@patch("sources.embassy_adapter.get_text")
def test_embassy_adapter_build_live_payload_raises_on_missing_alert(mock_get_text):
    mock_get_text.return_value = "<html><body><p>No alert data present</p></body></html>"

    adapter = EmbassyManilaAdapter(api_url="https://example.com/embassy", timeout_sec=15)

    try:
        adapter._build_live_payload()
        assert False, "Expected ValueError for missing latest alert"
    except ValueError as e:
        assert "missing expected field" in str(e).lower()