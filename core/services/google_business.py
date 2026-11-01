"""Server-side Google Places business information integration."""

import json
import logging
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from core.models import SiteSetting

logger = logging.getLogger(__name__)

BUSINESS_CACHE_KEY = "google_business_place_details_v1"
BUSINESS_CACHE_SECONDS = 900


def _unavailable():
    return {
        "available": False,
        "status": "unavailable",
        "message": "Google business information is currently unavailable.",
        "address": "",
        "directions_url": "",
        "regular_hours": [],
        "special_hours": [],
        "special_days": [],
        "next_change": "",
        "time_zone": "",
        "time_zone_label": "",
    }


def _valid_time_zone():
    site_settings = SiteSetting.objects.filter(pk=1).values("google_business_time_zone").first()
    configured = (
        site_settings["google_business_time_zone"] if site_settings else ""
    ) or getattr(settings, "GOOGLE_BUSINESS_TIME_ZONE", "")
    configured = configured.strip()
    if not configured:
        return None
    try:
        return ZoneInfo(configured)
    except ZoneInfoNotFoundError:
        logger.error("GOOGLE_BUSINESS_TIME_ZONE is not a valid IANA timezone.")
        return None


def get_configured_business_time_zone():
    tz = _valid_time_zone()
    return str(tz) if tz else ""


def _format_next_change(opening_hours, current_status, tz):
    if not tz:
        return ""
    now = timezone.now().astimezone(tz)
    candidates = []
    next_key, next_label = (
        ("nextCloseTime", "Closes") if current_status is True
        else ("nextOpenTime", "Opens")
    )
    next_time = opening_hours.get(next_key)
    if isinstance(next_time, str):
        try:
            parsed_time = datetime.fromisoformat(next_time.replace("Z", "+00:00"))
            if parsed_time.tzinfo is None:
                parsed_time = parsed_time.replace(tzinfo=tz)
            parsed_time = parsed_time.astimezone(tz)
            if parsed_time > now:
                return f"{next_label} {parsed_time:%A}, {parsed_time.strftime('%I:%M %p').lstrip('0')}"
        except ValueError:
            pass
    elif isinstance(next_time, dict):
        parsed_date = _google_point_date(next_time)
        parsed_clock = _google_point_time(next_time)
        if parsed_date and parsed_clock:
            parsed_time = datetime.combine(parsed_date, parsed_clock, tzinfo=tz)
            if parsed_time > now:
                return f"{next_label} {parsed_time:%A}, {parsed_time.strftime('%I:%M %p').lstrip('0')}"

    for period in opening_hours.get("periods", []):
        if not isinstance(period, dict):
            continue
        for edge, label in (("open", "Opens"), ("close", "Closes")):
            data = period.get(edge, {})
            if not isinstance(data, dict):
                continue
            try:
                date_value = data.get("date", {})
                time_value = data.get("time", {})
                if isinstance(date_value, dict):
                    local_date = datetime(
                        date_value["year"], date_value["month"], date_value["day"]
                    ).date()
                else:
                    local_date = datetime.strptime(date_value, "%Y-%m-%d").date()
                if isinstance(time_value, dict):
                    local_time = datetime.min.replace(
                        hour=time_value.get("hour", time_value.get("hours")),
                        minute=time_value.get("minute", time_value.get("minutes", 0)),
                    ).time()
                else:
                    local_time = datetime.strptime(time_value, "%H%M").time()
                moment = datetime.combine(
                    local_date,
                    local_time,
                    tzinfo=tz,
                )
            except (TypeError, ValueError):
                continue
            if moment > now:
                candidates.append((moment, label))
    if not candidates:
        return ""
    moment, label = min(candidates, key=lambda candidate: candidate[0])
    formatted_time = moment.strftime("%I:%M %p").lstrip("0")
    return f"{label} {moment:%A}, {formatted_time}" if current_status is not None else ""


def _google_point_date(point):
    date_value = point.get("date", {}) if isinstance(point, dict) else {}
    if not isinstance(date_value, dict) or not all(
        key in date_value for key in ("year", "month", "day")
    ):
        return None
    try:
        return datetime(date_value["year"], date_value["month"], date_value["day"]).date()
    except (TypeError, ValueError):
        return None


def _google_point_time(point):
    time_value = point.get("time", {}) if isinstance(point, dict) else {}
    try:
        if isinstance(time_value, dict):
            return datetime.min.replace(
                hour=time_value.get("hour", time_value.get("hours")),
                minute=time_value.get("minute", time_value.get("minutes", 0)),
            ).time()
        return datetime.strptime(time_value, "%H%M").time()
    except (KeyError, TypeError, ValueError):
        return None


def _special_hours(current):
    special_dates = set()
    for item in current.get("specialDays", []):
        if isinstance(item, dict):
            parsed_date = _google_point_date({"date": item.get("date", {})})
            if parsed_date:
                special_dates.add(parsed_date)
    if not special_dates:
        return []
    details = []
    for period in current.get("periods", []):
        if not isinstance(period, dict):
            continue
        open_point = period.get("open", {})
        open_date = _google_point_date(open_point)
        open_time = _google_point_time(open_point)
        if open_date not in special_dates or not open_time:
            continue
        close_point = period.get("close", {})
        close_date = _google_point_date(close_point)
        close_time = _google_point_time(close_point)
        date_label = open_date.strftime("%A, %b %d")
        open_label = datetime.combine(open_date, open_time).strftime("%I:%M %p").lstrip("0")
        if close_date and close_time:
            close_label = datetime.combine(close_date, close_time).strftime("%I:%M %p").lstrip("0")
            details.append(f"{date_label}: {open_label}–{close_label}")
        else:
            details.append(f"{date_label}: opens {open_label}; closing time unavailable")
    return details


def get_business_info(force_refresh=False):
    """Fetch configured Place details; API failures never produce a guessed status."""
    site_settings = SiteSetting.objects.filter(pk=1).values("google_place_id").first()
    place_id = (
        site_settings["google_place_id"] if site_settings else ""
    ) or getattr(settings, "GOOGLE_PLACE_ID", "")
    place_id = place_id.strip()
    api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", "").strip()
    if not place_id or not api_key:
        return _unavailable()

    tz = _valid_time_zone()
    cache_key = f"{BUSINESS_CACHE_KEY}:{place_id}:{tz or 'unset'}"
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    request = Request(
        f"https://places.googleapis.com/v1/places/{quote(place_id, safe='')}",
        headers={
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": (
                "id,formattedAddress,googleMapsUri,regularOpeningHours,"
                "currentOpeningHours"
            ),
        },
    )
    try:
        with urlopen(request, timeout=8) as response:
            if response.status != 200:
                logger.warning("Google Places returned HTTP %s.", response.status)
                return _unavailable()
            place = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, ValueError, UnicodeDecodeError) as exc:
        logger.warning("Google Places business lookup failed: %s", exc.__class__.__name__)
        return _unavailable()

    if not isinstance(place, dict) or place.get("id") != place_id:
        logger.error("Google Places returned a Place ID different from the configured ID.")
        return _unavailable()

    regular = place.get("regularOpeningHours") or {}
    current = place.get("currentOpeningHours") or {}
    status_value = current.get("openNow")
    status = "open" if status_value is True else "closed" if status_value is False else "unavailable"
    special_days = current.get("specialDays", [])
    result = {
        "available": True,
        "status": status,
        "message": (
            "Open now" if status == "open" else "Closed now" if status == "closed"
            else "Current opening status is unavailable."
        ),
        "address": place.get("formattedAddress", ""),
        "directions_url": place.get("googleMapsUri", ""),
        "regular_hours": regular.get("weekdayDescriptions", []),
        "special_hours": _special_hours(current),
        "special_days": [
            {
                "year": item["date"].get("year"),
                "month": item["date"].get("month"),
                "day": item["date"].get("day"),
            }
            for item in special_days
            if isinstance(item, dict) and isinstance(item.get("date"), dict)
        ],
        "next_change": _format_next_change(current, status_value, tz),
        "time_zone": str(tz) if tz else "",
        "time_zone_label": str(tz) if tz else "",
    }
    cache.set(cache_key, result, BUSINESS_CACHE_SECONDS)
    return result
