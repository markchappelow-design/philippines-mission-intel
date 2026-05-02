from unittest.mock import patch

from sources.weather_adapter import WeatherAdapter


@patch("sources.weather_adapter.get_json")
def test_weather_adapter_build_live_payload_parses_open_meteo_schema(mock_get_json):
    mock_get_json.return_value = {
        "latitude": 14.5995,
        "longitude": 120.9842,
        "current": {
            "time": "2026-03-13T12:00",
            "temperature_2m": 31.0,
            "apparent_temperature": 36.2,
            "wind_speed_10m": 11.4,
            "weather_code": 2,
        },
    }

    adapter = WeatherAdapter(api_url="https://example.com/weather", timeout_sec=15)
    payload = adapter._build_live_payload()

    assert payload.source_name == "Open-Meteo Weather Live"
    assert payload.section_name == "Weather forecast"
    assert payload.required is True
    assert payload.max_age_hours == 12
    assert payload.raw_metadata["live_mode"] is True
    assert "31.0C" in payload.content
    assert "36.2C" in payload.content
    assert "11.4 km/h" in payload.content


@patch("sources.weather_adapter.get_json")
def test_weather_adapter_build_live_payload_raises_on_missing_field(mock_get_json):
    mock_get_json.return_value = {
        "current": {
            "time": "2026-03-13T12:00",
            "temperature_2m": 31.0,
            "wind_speed_10m": 11.4,
            "weather_code": 2,
        }
    }

    adapter = WeatherAdapter(api_url="https://example.com/weather", timeout_sec=15)

    try:
        adapter._build_live_payload()
        assert False, "Expected ValueError for missing field"
    except ValueError as e:
        assert "Weather response missing expected field" in str(e)