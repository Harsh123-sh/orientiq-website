"""Flight search service for the Orientiq travel inventory foundation."""

import hashlib
from datetime import date, datetime

from django.core.cache import cache

from .providers.demo import DemoFlightProvider

VALID_CABIN_CLASSES = {"economy", "premium_economy", "business", "first"}
VALID_TRIP_TYPES = {"one-way", "round-trip"}


def _validate_flight_params(params):
    """Validate flight search params. Returns (is_valid, error)."""
    origin = (params.get("origin") or "").strip()
    destination = (params.get("destination") or "").strip()

    if not origin:
        return False, "Origin is required."
    if not destination:
        return False, "Destination is required."
    if origin.lower() == destination.lower():
        return False, "Origin and destination must differ."

    departure = params.get("departure")
    if not departure:
        return False, "Departure date is required."
    try:
        datetime.strptime(departure, "%Y-%m-%d")
    except (ValueError, TypeError):
        return False, "Invalid departure date. Use YYYY-MM-DD."

    trip_type = params.get("trip_type", "one-way")
    if trip_type not in VALID_TRIP_TYPES:
        return False, "Invalid trip type."

    if trip_type == "round-trip":
        return_date = params.get("return")
        if not return_date:
            return False, "Return date is required for round-trip."
        try:
            return_dt = datetime.strptime(return_date, "%Y-%m-%d")
            departure_dt = datetime.strptime(departure, "%Y-%m-%d")
            if return_dt < departure_dt:
                return False, "Return date cannot be before departure date."
        except (ValueError, TypeError):
            return False, "Invalid return date. Use YYYY-MM-DD."

    cabin = params.get("cabin_class", "economy")
    if cabin not in VALID_CABIN_CLASSES:
        return False, "Invalid cabin class."

    adults = int(params.get("adults", 1) or 1)
    children = int(params.get("children", 0) or 0)
    infants = int(params.get("infants", 0) or 0)
    if adults < 1 or adults > 9:
        return False, "Adults must be between 1 and 9."
    if children < 0 or children > 8:
        return False, "Children must be between 0 and 8."
    if infants < 0 or infants > 4:
        return False, "Infants must be between 0 and 4."

    return True, ""


def search_flights(params):
    """Search flights using the configured provider.

    Returns:
        {
            "success": bool,
            "results": [flight, ...],
            "error": str or None,
            "demo": bool
        }
    """
    is_valid, error = _validate_flight_params(params)
    if not is_valid:
        return {"success": False, "error": error, "results": [], "demo": True}

    # Build a deterministic cache key.
    key_source = (
        f"{params.get('origin','')}|{params.get('destination','')}|"
        f"{params.get('departure','')}|{params.get('return','')}|"
        f"{params.get('trip_type','one-way')}|{params.get('adults',1)}|"
        f"{params.get('cabin_class','economy')}|{params.get('sort','recommended')}"
    )
    cache_key = "flights_" + hashlib.md5(key_source.encode("utf-8")).hexdigest()
    cached = cache.get(cache_key)
    if cached is not None:
        return {"success": True, "results": cached, "error": None, "demo": True}

    provider = DemoFlightProvider()
    results = provider.search_flights(params)

    # Apply sorting.
    sort_by = params.get("sort", "recommended")
    if sort_by == "cheapest":
        results = sorted(results, key=lambda r: r["price"])
    elif sort_by == "fastest":
        results = sorted(results, key=lambda r: r["duration"])
    # "recommended" keeps provider order.

    cache.set(cache_key, results, 600)
    return {"success": True, "results": results, "error": None, "demo": True}