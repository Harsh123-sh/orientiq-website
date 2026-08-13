"""Activity search service for the Orientiq travel inventory foundation."""

import hashlib
from datetime import datetime

from django.core.cache import cache

from .providers.demo import DemoActivityProvider


def _validate_activity_params(params):
    """Validate activity search params. Returns (is_valid, error)."""
    destination = (params.get("destination") or "").strip()
    if not destination:
        return False, "Destination is required."

    date_str = params.get("date")
    if date_str:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            return False, "Invalid date. Use YYYY-MM-DD."

    try:
        guests = int(params.get("guests", 2) or 2)
    except (TypeError, ValueError):
        return False, "Invalid guests."
    if guests < 1 or guests > 20:
        return False, "Guests must be between 1 and 20."

    return True, ""


def search_activities(params):
    """Search activities using the configured provider.

    Returns:
        {
            "success": bool,
            "results": [activity, ...],
            "error": str or None,
            "demo": bool
        }
    """
    is_valid, error = _validate_activity_params(params)
    if not is_valid:
        return {"success": False, "error": error, "results": [], "demo": True}

    key_source = (
        f"{params.get('destination','')}|{params.get('date','')}|"
        f"{params.get('category','')}|{params.get('guests',2)}|"
        f"{params.get('sort','recommended')}"
    )
    cache_key = "activities_" + hashlib.md5(key_source.encode("utf-8")).hexdigest()
    cached = cache.get(cache_key)
    if cached is not None:
        return {"success": True, "results": cached, "error": None, "demo": True}

    provider = DemoActivityProvider()
    results = provider.search_activities(params)

    # Apply filtering by category.
    category = (params.get("category") or "").strip().lower()
    if category:
        results = [r for r in results if r.get("category", "").lower() == category]

    # Apply sorting.
    sort_by = params.get("sort", "recommended")
    if sort_by == "price":
        results = sorted(results, key=lambda r: r["price"])
    elif sort_by == "rating":
        results = sorted(results, key=lambda r: r["rating"], reverse=True)
    # "recommended" keeps provider order.

    cache.set(cache_key, results, 600)
    return {"success": True, "results": results, "error": None, "demo": True}