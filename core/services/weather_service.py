"""Weather service for the Orientiq live intelligence foundation.

Provider-independent weather abstraction. Normalizes provider responses
into a consistent internal format so the rest of the application never
depends on a single provider's response shape.
"""

import os
import time
from datetime import datetime, timezone

from django.core.cache import cache

from .location_service import validate_coordinates


class WeatherError(Exception):
    """Raised when the weather provider fails."""


class BaseWeatherProvider:
    """Base class for weather providers."""

    def get_current_weather(self, location):
        raise NotImplementedError


class StaticWeatherProvider(BaseWeatherProvider):
    """Safe fallback provider that returns a normalized weather response.

    Used when no WEATHER_API_KEY is configured. Returns a deterministic
    placeholder so the foundation remains testable and functional.
    """

    def get_current_weather(self, location):
        lat = location.get("latitude")
        lon = location.get("longitude")
        if not validate_coordinates(lat, lon):
            raise WeatherError("Invalid coordinates for weather")

        return {
            "location": location.get("name", "Selected location"),
            "temperature": 24,
            "condition": "Clear",
            "humidity": 50,
            "wind_speed": 10,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "source": "static-fallback",
        }


def get_weather_provider():
    """Return the configured weather provider, or the static fallback."""
    provider_name = os.getenv("WEATHER_PROVIDER", "").strip().lower()
    api_key = os.getenv("WEATHER_API_KEY", "").strip()

    if provider_name and api_key:
        # Future: return a concrete provider (e.g., OpenWeatherMap).
        # For now, the static provider is used to avoid an unverified dependency.
        pass

    return StaticWeatherProvider()


def get_current_weather(location):
    """Return normalized current weather for a location.

    Returns:
        {
            "success": bool,
            "data": {...},
            "error": str or None
        }
    """
    if not location:
        return {"success": False, "error": "Location is required.", "data": None}

    lat = location.get("latitude")
    lon = location.get("longitude")
    if not validate_coordinates(lat, lon):
        return {"success": False, "error": "Invalid coordinates.", "data": None}

    cache_key = f"weather_{float(lat):.4f}_{float(lon):.4f}"
    cached = cache.get(cache_key)
    if cached is not None:
        return {"success": True, "data": cached, "error": None}

    provider = get_weather_provider()
    try:
        data = provider.get_current_weather(location)
    except WeatherError as exc:
        return {"success": False, "error": str(exc), "data": None}

    # Cache weather for a short duration (e.g., 10 minutes).
    cache.set(cache_key, data, 600)

    return {"success": True, "data": data, "error": None}