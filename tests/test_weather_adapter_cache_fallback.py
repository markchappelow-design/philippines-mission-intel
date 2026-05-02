from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from sources.base import SourceFetchError
from sources.cache_utils import write_payload_cache
from sources.source_models import SourcePayload
from sources.weather_adapter import WeatherAdapter


def test_weather_adapter_fetch_uses_fresh_cache_when_live_fetch_fails():
    now = datetime.now(timezone.utc)

    cached_payload = SourcePayload(
        source_name="PAGASA Weather Live",
        section_name="Weather forecast",
        content="Cached weather content remains valid for fallback use.",
        retrieved_at_utc=now,
        source_timestamp_utc=now - timedelta(hours=1),
        max_age_hours=12,
        required=True,
        notes="cached weather payload",
        raw_metadata={"provider": "cache-test"},
    )

    write_payload_cache("weather", cached_payload)

    adapter = WeatherAdapter(api_url="https://example.com/weather", timeout_sec=15)

    with patch("sources.weather_adapter.USE_LIVE_WEATHER", True):
        with patch.object(adapter, "_build_live_payload", side_effect=RuntimeError("live fetch failed")):
            payload = adapter.fetch()

    assert payload.section_name == "Weather forecast"
    assert payload.content == "Cached weather content remains valid for fallback use."
    assert payload.raw_metadata["cache_fallback"] is True


def test_weather_adapter_fetch_fails_when_cache_is_stale():
    now = datetime.now(timezone.utc)

    stale_cached_payload = SourcePayload(
        source_name="PAGASA Weather Live",
        section_name="Weather forecast",
        content="Stale cached weather content.",
        retrieved_at_utc=now,
        source_timestamp_utc=now - timedelta(hours=20),
        max_age_hours=12,
        required=True,
        notes="stale cached weather payload",
        raw_metadata={"provider": "cache-test"},
    )

    write_payload_cache("weather", stale_cached_payload)

    adapter = WeatherAdapter(api_url="https://example.com/weather", timeout_sec=15)

    with patch("sources.weather_adapter.USE_LIVE_WEATHER", True):
        with patch.object(adapter, "_build_live_payload", side_effect=RuntimeError("live fetch failed")):
            try:
                adapter.fetch()
                assert False, "Expected fetch to fail when only stale cache is available"
            except SourceFetchError as e:
                assert "no valid cache available" in str(e)