from unittest.mock import patch

from sources.state_dept_adapter import StateDepartmentAdapter


@patch("sources.state_dept_adapter.get_text")
def test_state_dept_adapter_build_live_payload_parses_expected_fields(mock_get_text):
    mock_get_text.return_value = """
    <html>
      <body>
        <h1>Philippines - Level 2: Exercise Increased Caution</h1>
        <p>Travel Advisory May 8, 2025 Philippines - Level 2: Exercise Increased Caution</p>
        <p>Exercise increased caution in the Philippines due to crime, terrorism, civil unrest, and kidnapping.
        Read the entire Travel Advisory.</p>
      </body>
    </html>
    """

    adapter = StateDepartmentAdapter(api_url="https://example.com/state", timeout_sec=15)
    payload = adapter._build_live_payload()

    assert payload.source_name == "U.S. State Department Live"
    assert payload.section_name == "U.S. State Department travel advisories for Americans"
    assert payload.raw_metadata["live_mode"] is True
    assert payload.raw_metadata["advisory_level"] == "2"
    assert "Level 2" in payload.content


@patch("sources.state_dept_adapter.get_text")
def test_state_dept_adapter_build_live_payload_raises_on_missing_level(mock_get_text):
    mock_get_text.return_value = "<html><body><p>No advisory data</p></body></html>"

    adapter = StateDepartmentAdapter(api_url="https://example.com/state", timeout_sec=15)

    try:
        adapter._build_live_payload()
        assert False, "Expected ValueError for missing advisory level"
    except ValueError as e:
        assert "missing expected field" in str(e).lower()