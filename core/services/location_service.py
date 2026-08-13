"""Location service for the Orientiq live intelligence foundation.

Provides a provider-independent way to search and look up locations.
Supports arbitrary city/state/country/landmark searches via a real
geocoding provider (OpenStreetMap Nominatim) with a built-in fallback
set when the provider is unavailable.
"""

import os
import time
import urllib.parse
import urllib.request

from django.core.cache import cache


class LocationError(Exception):
    """Raised when a location cannot be resolved."""


# A small built-in fallback set of common destinations so the service
# remains functional and testable without any external API.
_FALLBACK_LOCATIONS = {
    "ahmedabad": {
        "name": "Ahmedabad",
        "display_name": "Ahmedabad, Gujarat, India",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "country": "India",
        "latitude": 23.0225,
        "longitude": 72.5714,
        "timezone": "Asia/Kolkata",
    },
    "bhopal": {
        "name": "Bhopal",
        "display_name": "Bhopal, Madhya Pradesh, India",
        "city": "Bhopal",
        "state": "Madhya Pradesh",
        "country": "India",
        "latitude": 23.2599,
        "longitude": 77.4126,
        "timezone": "Asia/Kolkata",
    },
    "gandhinagar": {
        "name": "Gandhinagar",
        "display_name": "Gandhinagar, Gujarat, India",
        "city": "Gandhinagar",
        "state": "Gujarat",
        "country": "India",
        "latitude": 23.2156,
        "longitude": 72.6369,
        "timezone": "Asia/Kolkata",
    },
    "jaipur": {
        "name": "Jaipur",
        "display_name": "Jaipur, Rajasthan, India",
        "city": "Jaipur",
        "state": "Rajasthan",
        "country": "India",
        "latitude": 26.9124,
        "longitude": 75.7873,
        "timezone": "Asia/Kolkata",
    },
    "udaipur": {
        "name": "Udaipur",
        "display_name": "Udaipur, Rajasthan, India",
        "city": "Udaipur",
        "state": "Rajasthan",
        "country": "India",
        "latitude": 24.5854,
        "longitude": 73.7125,
        "timezone": "Asia/Kolkata",
    },
    "goa": {
        "name": "Goa",
        "display_name": "Goa, India",
        "city": "",
        "state": "Goa",
        "country": "India",
        "latitude": 15.2993,
        "longitude": 74.1240,
        "timezone": "Asia/Kolkata",
    },
    "kerala": {
        "name": "Kerala",
        "display_name": "Kerala, India",
        "city": "",
        "state": "Kerala",
        "country": "India",
        "latitude": 10.8505,
        "longitude": 76.2711,
        "timezone": "Asia/Kolkata",
    },
    "madhya pradesh": {
        "name": "Madhya Pradesh",
        "display_name": "Madhya Pradesh, India",
        "city": "",
        "state": "Madhya Pradesh",
        "country": "India",
        "latitude": 22.9734,
        "longitude": 78.6569,
        "timezone": "Asia/Kolkata",
    },
    "gujarat": {
        "name": "Gujarat",
        "display_name": "Gujarat, India",
        "city": "",
        "state": "Gujarat",
        "country": "India",
        "latitude": 22.2587,
        "longitude": 71.1924,
        "timezone": "Asia/Kolkata",
    },
    "india": {
        "name": "India",
        "display_name": "India",
        "city": "",
        "state": "",
        "country": "India",
        "latitude": 20.5937,
        "longitude": 78.9629,
        "timezone": "Asia/Kolkata",
    },
    "dubai": {
        "name": "Dubai",
        "display_name": "Dubai, United Arab Emirates",
        "city": "Dubai",
        "state": "",
        "country": "United Arab Emirates",
        "latitude": 25.2048,
        "longitude": 55.2708,
        "timezone": "Asia/Dubai",
    },
    "london": {
        "name": "London",
        "display_name": "London, United Kingdom",
        "city": "London",
        "state": "",
        "country": "United Kingdom",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "timezone": "Europe/London",
    },
    "new york": {
        "name": "New York",
        "display_name": "New York, United States",
        "city": "New York",
        "state": "New York",
        "country": "United States",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York",
    },
    "paris": {
        "name": "Paris",
        "display_name": "Paris, France",
        "city": "Paris",
        "state": "",
        "country": "France",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "timezone": "Europe/Paris",
    },
    "tokyo": {
        "name": "Tokyo",
        "display_name": "Tokyo, Japan",
        "city": "Tokyo",
        "state": "",
        "country": "Japan",
        "latitude": 35.6762,
        "longitude": 139.6503,
        "timezone": "Asia/Tokyo",
    },
    "singapore": {
        "name": "Singapore",
        "display_name": "Singapore",
        "city": "Singapore",
        "state": "",
        "country": "Singapore",
        "latitude": 1.3521,
        "longitude": 103.8198,
        "timezone": "Asia/Singapore",
    },
    "mumbai": {
        "name": "Mumbai",
        "display_name": "Mumbai, Maharashtra, India",
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "timezone": "Asia/Kolkata",
    },
    "delhi": {
        "name": "Delhi",
        "display_name": "Delhi, India",
        "city": "Delhi",
        "state": "Delhi",
        "country": "India",
        "latitude": 28.7041,
        "longitude": 77.1025,
        "timezone": "Asia/Kolkata",
    },
    "bengaluru": {
        "name": "Bengaluru",
        "display_name": "Bengaluru, Karnataka, India",
        "city": "Bengaluru",
        "state": "Karnataka",
        "country": "India",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "timezone": "Asia/Kolkata",
    },
    "eiffel tower": {
        "name": "Eiffel Tower",
        "display_name": "Eiffel Tower, Paris, France",
        "city": "Paris",
        "state": "",
        "country": "France",
        "latitude": 48.8584,
        "longitude": 2.2945,
        "timezone": "Europe/Paris",
    },
    "taj mahal": {
        "name": "Taj Mahal",
        "display_name": "Taj Mahal, Agra, Uttar Pradesh, India",
        "city": "Agra",
        "state": "Uttar Pradesh",
        "country": "India",
        "latitude": 27.1751,
        "longitude": 78.0421,
        "timezone": "Asia/Kolkata",
    },
}


def _normalize(query):
    """Normalize a location query for matching."""
    return " ".join(str(query or "").strip().lower().split())


class BaseLocationProvider:
    """Base class for location/geocoding providers."""

    def search(self, query, limit=5):
        raise NotImplementedError


class NominatimLocationProvider(BaseLocationProvider):
    """OpenStreetMap Nominatim geocoding provider.

    Uses the public Nominatim API. Respects the usage policy with a
    descriptive User-Agent. Returns normalized location results.
    """

    BASE_URL = "https://nominatim.openstreetmap.org/search"

    def search(self, query, limit=5):
        params = {
            "q": query,
            "format": "json",
            "limit": str(limit),
            "addressdetails": "1",
        }
        url = self.BASE_URL + "?" + urllib.parse.urlencode(params)

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "OrientiqWebsite/1.0 (contact: hello@orientiq.com)",
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                raw = resp.read().decode("utf-8")
        except Exception:
            raise LocationError("Geocoding provider unavailable")

        import json

        try:
            items = json.loads(raw)
        except (ValueError, TypeError):
            raise LocationError("Geocoding provider returned invalid data")

        results = []
        for item in items[:limit]:
            address = item.get("address", {}) or {}
            results.append(
                {
                    "name": item.get("name") or address.get("city")
                    or address.get("town") or address.get("state") or query,
                    "display_name": item.get("display_name", ""),
                    "city": address.get("city") or address.get("town") or address.get("village") or "",
                    "state": address.get("state", ""),
                    "country": address.get("country", ""),
                    "latitude": float(item.get("lat", 0)),
                    "longitude": float(item.get("lon", 0)),
                    "timezone": "UTC",
                }
            )
        return results


def get_location_provider():
    """Return the configured location provider, or Nominatim fallback."""
    provider_name = os.getenv("LOCATION_PROVIDER", "").strip().lower()
    api_key = os.getenv("LOCATION_API_KEY", "").strip()

    if provider_name and api_key:
        # Future: return a concrete provider (e.g., Google Geocoding).
        # For now, Nominatim is used even when a key is present.
        pass

    return NominatimLocationProvider()


def _fallback_search(query, limit=5):
    """Search the built-in fallback set."""
    q = _normalize(query)
    results = [
        loc
        for key, loc in _FALLBACK_LOCATIONS.items()
        if q in key or q in _normalize(loc["name"]) or q in _normalize(loc.get("display_name", ""))
    ]
    return results[:limit]


def search_locations(query, limit=5):
    """Search locations by arbitrary text (city, state, country, landmark).

    Returns:
        {
            "success": bool,
            "results": [location, ...],
            "error": str or None
        }
    """
    q = _normalize(query)
    if not q:
        return {"success": False, "error": "Location query is required.", "results": []}
    if len(q) > 200:
        return {"success": False, "error": "Location query is too long.", "results": []}

    # Cache key so repeated searches don't hammer external providers.
    # Use a quoted key to avoid memcached CacheKeyWarning on spaces/unicode.
    import hashlib
    cache_key = f"location_search_{hashlib.md5(q.encode('utf-8')).hexdigest()}"
    cached = cache.get(cache_key)
    if cached is not None:
        return {"success": True, "results": cached, "error": None}

    # Try the real geocoding provider first.
    provider = get_location_provider()
    try:
        results = provider.search(q, limit=limit)
    except LocationError:
        results = []

    # Fall back to the built-in set if the provider returned nothing.
    if not results:
        results = _fallback_search(q, limit=limit)

    # Cache for a short time (e.g., 10 minutes).
    cache.set(cache_key, results, 600)

    return {"success": True, "results": results, "error": None}


def get_location_by_name(query):
    """Look up a single location by name.

    Returns a normalized location dict, or None if not found.
    """
    q = _normalize(query)
    if not q:
        return None
    result = search_locations(q, limit=1)
    data = result.get("results", [])
    return data[0] if data else None


def get_location_by_coordinates(latitude, longitude):
    """Look up a location by coordinates (reverse geocode foundation).

    For the foundation, we validate the coordinates and return a normalized
    location placeholder. A provider-based reverse geocode can be added later.
    """
    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError):
        raise LocationError("Invalid coordinates")

    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise LocationError("Coordinates out of range")

    return {
        "name": "Selected location",
        "display_name": f"{round(lat, 6)}, {round(lon, 6)}",
        "city": "",
        "state": "",
        "country": "",
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "timezone": "UTC",
    }


def validate_coordinates(latitude, longitude):
    """Basic coordinate validation."""
    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError):
        return False
    return -90 <= lat <= 90 and -180 <= lon <= 180