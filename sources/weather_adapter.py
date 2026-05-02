from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests

from sources.base import BaseSourceAdapter
from sources.fetch_with_cache import fetch_with_cache
from sources.source_models import SourcePayload


WEATHER_CODE_MAP = {
    0: "Clear",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    80: "Rain showers",
    81: "Moderate showers",
    82: "Violent showers",
    95: "Thunderstorm",
    96: "Thunderstorm w/ hail",
    99: "Severe thunderstorm w/ hail",
}


class WeatherAdapter(BaseSourceAdapter):
    CACHE_KEY = "weather"

    def __init__(self, api_url: str, timeout_sec: int = 15) -> None:
        super().__init__()
        self.api_url = api_url
        self.timeout_sec = timeout_sec

    def _fetch_weather(self) -> dict[str, Any]:
        params = {
            "latitude": 14.5995,
            "longitude": 120.9842,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,wind_speed_10m_max",
            "forecast_days": 5,
            "timezone": "Asia/Manila",
        }
        r = requests.get(self.api_url, params=params, timeout=self.timeout_sec)
        r.raise_for_status()
        return r.json()

    def _build_forecast_text(self, payload: dict[str, Any]) -> str:
        daily = payload.get("daily") or {}
        dates = daily.get("time") or []
        highs = daily.get("temperature_2m_max") or []
        lows = daily.get("temperature_2m_min") or []
        winds = daily.get("wind_speed_10m_max") or []
        codes = daily.get("weather_code") or []

        if not dates:
            raise ValueError("No daily forecast data returned by weather source")

        lines = ["Weather forecast"]
        for i in range(min(5, len(dates))):
            code = int(codes[i]) if i < len(codes) and codes[i] is not None else -1
            condition = WEATHER_CODE_MAP.get(code, f"Code {code}")
            lines.append(
                f"{dates[i]} | High {highs[i]}°C | Low {lows[i]}°C | Wind {winds[i]} km/h | {condition}"
            )

        lines.append("")
        lines.append("Heat / Sun Exposure Advisory")
        lines.append(
            "Heat injury remains a routine operational risk in the Philippines. Hydrate aggressively, use shade when available, "
            "limit prolonged midday sun exposure, and monitor for signs of heat exhaustion or heat stroke."
        )
        lines.append(
            "Use sunscreen, lightweight clothing, and electrolytes as needed. Overcast conditions do not eliminate heat risk."
        )
        return "\n".join(lines)

    def _build_payload(self) -> SourcePayload:
        now = datetime.now(timezone.utc)
        wx = self._fetch_weather()
        content = self._build_forecast_text(wx)

        return SourcePayload(
            source_name="Open-Meteo 5-Day Forecast",
            section_name="Weather forecast",
            content=content,
            source_type="LIVE_FEED",
            required=True,
            retrieved_at_utc=now,
            source_timestamp_utc=now,
            max_age_hours=12,
            notes="Five-day Manila/NAIA forecast with heat-exposure advisory.",
            raw_metadata={
                "provider": "open-meteo",
                "api_url": self.api_url,
                "timezone": "Asia/Manila",
                "forecast_days": 5,
            },
        )

    def fetch(self) -> SourcePayload:
        return fetch_with_cache(self.CACHE_KEY, self._build_payload)