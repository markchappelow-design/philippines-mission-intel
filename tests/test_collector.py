from unittest.mock import patch

from sources.collector import collect_all_sources
from sources.source_models import SourcePayload


@patch("sources.collector.WeatherAdapter.fetch")
def test_collect_all_sources_returns_expected_sections(mock_weather_fetch, monkeypatch):
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    mock_weather_fetch.return_value = SourcePayload(
        source_name="Weather Source",
        section_name="Weather forecast",
        content="Warm and humid with possible rain.",
        retrieved_at_utc=now,
        source_timestamp_utc=now,
        max_age_hours=12,
        required=True,
        notes="Mock weather payload",
        raw_metadata={},
    )

    monkeypatch.setenv("WEATHER_API_URL", "https://example.com/weather")

    payloads = collect_all_sources()
    sections = {p.section_name for p in payloads}

    assert "Strategic Situation" in sections
    assert "Priority Intelligence" in sections
    assert "U.S. Embassy (Manila) travel advisories" in sections
    assert "U.S. State Department travel advisories for Americans" in sections
    assert "Immunization recommendations" in sections
    assert "Weather forecast" in sections
    assert "NAIA" in sections