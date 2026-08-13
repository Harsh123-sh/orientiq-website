"""Live Intelligence service for the Orientiq foundation.

Combines multiple live-data sources (location, weather, maps) into a
single normalized result. Designed so future modules (traffic, events,
travel alerts, local info) can be added without rewriting the architecture.
"""

from .location_service import get_location_by_name
from .maps_service import get_map
from .weather_service import get_current_weather


def get_destination_intelligence(destination):
    """Return combined live intelligence for a destination.

    Args:
        destination (str): Location name, e.g. "Dubai".

    Returns:
        {
            "success": bool,
            "data": {
                "location": {...},
                "weather": {...},
                "map": {...},
                "status": "success" | "partial" | "unavailable"
            },
            "error": str or None
        }
    """
    if not destination or not str(destination).strip():
        return {
            "success": False,
            "error": "Destination is required.",
            "data": None,
        }

    location = get_location_by_name(destination)
    if not location:
        return {
            "success": False,
            "error": f"No location found for '{destination}'.",
            "data": None,
        }

    weather_result = get_current_weather(location)
    map_result = get_map(location)

    weather = weather_result.get("data") if weather_result.get("success") else None
    map_data = map_result.get("data") if map_result.get("success") else None

    # Determine status.
    if weather and map_data:
        status = "success"
    elif weather or map_data:
        status = "partial"
    else:
        status = "unavailable"

    return {
        "success": True,
        "data": {
            "location": location,
            "weather": weather,
            "map": map_data,
            "status": status,
        },
        "error": None,
    }