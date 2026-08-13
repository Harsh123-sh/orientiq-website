"""Maps service for the Orientiq live intelligence foundation.

Provider-independent maps abstraction. The rest of the application
communicates with this service layer rather than a concrete provider.
"""

import os

from django.core.cache import cache

from .location_service import validate_coordinates


class MapsError(Exception):
    """Raised when the maps provider fails."""


class BaseMapsProvider:
    """Base class for maps providers."""

    def get_map_data(self, location):
        raise NotImplementedError


class StaticMapsProvider(BaseMapsProvider):
    """Safe fallback provider that returns normalized map data.

    Used when no MAPS_API_KEY is configured. Returns coordinates and a
    static map URL (OpenStreetMap embed) without requiring an API key.
    """

    def get_map(self, location):
        lat = location.get("latitude")
        lon = location.get("longitude")
        if not validate_coordinates(lat, lon):
            raise MapsError("Invalid coordinates for map")

        return {
            "provider": "static",
            "latitude": round(float(lat), 6),
            "longitude": round(float(lon), 6),
            "embed_url": (
                f"https://www.openstreetmap.org/export/embed.html"
                f"?bbox={float(lon) - 0.01}%2C{float(lat) - 0.01}%2C"
                f"{float(lon) + 0.01}%2C{float(lat) + 0.01}"
                f"&layer=mapnik&marker={float(lat)}%2C{float(lon)}"
            ),
            "marker": {"latitude": round(float(lat), 6), "longitude": round(float(lon), 6)},
        }


def get_maps_provider():
    """Return the configured maps provider, or the static fallback."""
    provider_name = os.getenv("MAP_PROVIDER", "").strip().lower()
    api_key = os.getenv("MAPS_API_KEY", "").strip()

    if provider_name and api_key:
        # Future: return a concrete provider (e.g., Google Maps, Mapbox).
        # For now, the static provider is used even when a key is present,
        # to avoid introducing an unverified dependency.
        pass

    return StaticMapsProvider()


def get_map(location):
    """Return normalized map data for a location.

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

    cache_key = f"map_{float(lat):.4f}_{float(lon):.4f}"
    cached = cache.get(cache_key)
    if cached is not None:
        return {"success": True, "data": cached, "error": None}

    provider = get_maps_provider()
    try:
        data = provider.get_map(location)
    except MapsError as exc:
        return {"success": False, "error": str(exc), "data": None}

    # Cache map data for a moderate duration (e.g., 1 hour).
    cache.set(cache_key, data, 3600)

    return {"success": True, "data": data, "error": None}