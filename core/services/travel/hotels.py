"""Hotel search service for the Orientiq travel inventory foundation."""

import hashlib
from datetime import datetime, timedelta

from django.core.cache import cache

from .providers.demo import DemoHotelProvider


def _validate_hotel_params(params):
    """Validate hotel search params. Returns (is_valid, error)."""
    destination = (params.get("destination") or "").strip()
    if not destination:
        return False, "Destination is required."

    check_in = params.get("check_in")
    check_out = params.get("check_out")
    if not check_in:
        return False, "Check-in date is required."
    if not check_out:
        return False, "Check-out date is required."

    try:
        in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
        out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return False, "Invalid date. Use YYYY-MM-DD."

    if out_date <= in_date:
        return False, "Check-out must be after check-in."
    if (out_date - in_date).days > 30:
        return False, "Stay cannot exceed 30 nights."

    try:
        guests = int(params.get("guests", 2) or 2)
        rooms = int(params.get("rooms", 1) or 1)
    except (TypeError, ValueError):
        return False, "Invalid guests/rooms."
    if guests < 1 or guests > 20:
        return False, "Guests must be between 1 and 20."
    if rooms < 1 or rooms > 5:
        return False, "Rooms must be between 1 and 5."

    return True, ""


def search_hotels(params):
    """Search hotels using the configured provider.

    Returns:
        {
            "success": bool,
            "results": [hotel, ...],
            "error": str or None,
            "demo": bool
        }
    """
    is_valid, error = _validate_hotel_params(params)
    if not is_valid:
        return {"success": False, "error": error, "results": [], "demo": True}

    key_source = (
        f"{params.get('destination','')}|{params.get('check_in','')}|"
        f"{params.get('check_out','')}|{params.get('guests',2)}|{params.get('rooms',1)}|"
        f"{params.get('sort','recommended')}"
    )
    cache_key = "hotels_" + hashlib.md5(key_source.encode("utf-8")).hexdigest()
    cached = cache.get(cache_key)
    if cached is not None:
        return {"success": True, "results": cached, "error": None, "demo": True}

    provider = DemoHotelProvider()
    results = provider.search_hotels(params)

    # Apply sorting.
    sort_by = params.get("sort", "recommended")
    if sort_by == "price":
        results = sorted(results, key=lambda r: r["price_per_night"])
    elif sort_by == "rating":
        results = sorted(results, key=lambda r: r["rating"], reverse=True)
    # "recommended" keeps provider order.

    cache.set(cache_key, results, 600)
    return {"success": True, "results": results, "error": None, "demo": True}