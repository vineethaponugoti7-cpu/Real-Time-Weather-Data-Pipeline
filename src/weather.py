"""
Weather fetching logic shared by both the local and AWS pipelines.

Calls the OpenWeatherMap API for a city, with retries, and returns a clean
dictionary of the fields we care about.
"""

import time
from datetime import datetime, timezone

import requests

import config


def build_owm_url(city: str) -> str:
    """Return the full OpenWeatherMap API URL for a city (metric units)."""
    return (
        f"{config.OWM_BASE_URL}"
        f"?q={city}&appid={config.OWM_API_KEY}&units=metric"
    )


def fetch_weather(city: str, retries: int = 3) -> dict | None:
    """
    Call the OWM API for one city and return a parsed record, or None if all
    attempts fail. Retries a few times with a short pause between tries.
    """
    for attempt in range(retries):
        try:
            resp = requests.get(build_owm_url(city), timeout=10)
            resp.raise_for_status()
            raw = resp.json()

            return {
                "city": raw["name"],
                "temp": raw["main"]["temp"],
                "humidity": raw["main"]["humidity"],
                "wind_speed": raw["wind"]["speed"],
                "weather": raw["weather"][0]["main"],
                "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            }

        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] {city} (attempt {attempt + 1}/{retries}): {exc}")
            time.sleep(2)

    return None
