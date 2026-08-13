"""
Booking services for Phase 9: Booking + Reservation Workflow Foundation.

All money math happens here, server-side, using Python Decimal.
Client-submitted price/subtotal/total values are NEVER trusted.
"""

import hashlib
import random
import string
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth import get_user_model
from django.db import transaction

from ..models import Booking, BookingItem, BookingStatus, BookingType, Traveler

# Rate limiting for booking creation/confirmation (per IP, cache-backed).
BOOKING_RATE_MAX = 10
BOOKING_RATE_WINDOW_SECONDS = 60

DEMO_DISCLAIMER = (
    "DEMO RESERVATION — No real travel reservation or payment has been processed."
)

ZERO = Decimal("0.00")


def _dec(value):
    """Safely coerce a value to Decimal with 2 decimal places."""
    try:
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (TypeError, ValueError, ArithmeticError):
        return ZERO


def generate_booking_reference():
    """
    Generate a unique, non-sequential booking reference.
    Format: ORI-XXXXXXXX where X is alphanumeric (uppercase letters and numbers).
    """
    while True:
        reference = f"ORI-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        if not Booking.objects.filter(booking_reference=reference).exists():
            return reference


def get_client_ip(request):
    """Best-effort client IP extraction."""
    return (
        request.META.get("HTTP_X_FORWARDED_FOR", "")
        or request.META.get("REMOTE_ADDR")
        or "unknown"
    ).split(",")[0].strip()


def is_booking_rate_limited(request, cache):
    """Simple per-IP rate limit for booking creation/confirmation."""
    key = f"booking_rate_{get_client_ip(request)}"
    try:
        count = cache.get(key, 0) or 0
    except Exception:
        return False  # Fail open; never block legitimate demo use due to cache errors.
    if count >= BOOKING_RATE_MAX:
        return True
    try:
        cache.set(key, count + 1, BOOKING_RATE_WINDOW_SECONDS)
    except Exception:
        pass
    return False


def compute_selection_key(item_type, params):
    """
    Deterministic, non-sensitive hash identifying a specific inventory
    selection so the same selection cannot be confirmed twice.
    """
    parts = ["item_type", str(item_type)]

    if item_type == BookingType.FLIGHT:
        for key in ("origin", "destination", "departure", "flight_number"):
            parts.append(f"{key}={params.get(key, '')}")
    elif item_type == BookingType.HOTEL:
        for key in ("destination", "check_in", "check_out", "hotel_name"):
            parts.append(f"{key}={params.get(key, '')}")
    elif item_type == BookingType.ACTIVITY:
        for key in ("destination", "date", "activity_name"):
            parts.append(f"{key}={params.get(key, '')}")

    raw = "|".join(parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
def _hotel_nights(params):
    """Number of hotel nights derived from checked-in/out dates."""
    try:
        check_in = datetime.strptime(params.get("check_in", ""), "%Y-%m-%d").date()
        check_out = datetime.strptime(params.get("check_out", ""), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return 0
    nights = (check_out - check_in).days
    return max(nights, 0)


def resolve_inventory(item_type, params):
    """
    Reconstruct a TRUSTED inventory item server-side by re-running the
    Phase 8 demo search for the submitted selection parameters.

    Returns (item_dict, error) where item_dict is None on failure.
    Provider-sourced price and currency are used for all pricing.
    """
    try:
        if item_type == BookingType.FLIGHT:
            from .travel.flights import search_flights

            result = search_flights(params)
            if not result["success"]:
                return None, result.get("error", "Invalid flight selection.")
            flight_number = (params.get("flight_number") or "").strip()
            item = next(
                (r for r in result["results"] if r.get("flight_number") == flight_number),
                None,
            )
            if item is None:
                return None, "The selected flight could not be verified."
            return item, None

        if item_type == BookingType.HOTEL:
            from .travel.hotels import search_hotels

            result = search_hotels(params)
            if not result["success"]:
                return None, result.get("error", "Invalid hotel selection.")
            hotel_name = (params.get("hotel_name") or "").strip()
            item = next(
                (r for r in result["results"] if r.get("hotel_name") == hotel_name),
                None,
            )
            if item is None:
                return None, "The selected hotel could not be verified."
            return item, None

        if item_type == BookingType.ACTIVITY:
            from .travel.activities import search_activities

            result = search_activities(params)
            if not result["success"]:
                return None, result.get("error", "Invalid activity selection.")
            activity_name = (params.get("activity_name") or "").strip()
            item = next(
                (r for r in result["results"] if r.get("activity_name") == activity_name),
                None,
            )
            if item is None:
                return None, "The selected activity could not be verified."
            return item, None

        return None, "Unsupported booking type."
    except Exception:
        # Never leak internal detail to the client.
        return None, "The selected inventory could not be verified. Please try again."


def calculate_price(item_type, item, params):
    """
    Server-side Decimal price calculation.

    FLIGHT:   base = unit price x adults
    HOTEL:    base = price_per_night x nights
    ACTIVITY: base = unit price x participants (guests)

    Taxes/Fees are deliberately NOT invented in Phase 9 (the model has a
    taxes field but no tax engine exists).
    """
    currency = (str(item.get("currency") or "USD")).upper()
    subtotal = ZERO

    if item_type == BookingType.FLIGHT:
        unit = _dec(item.get("price"))
        quantity = max(int(params.get("adults", 1) or 1), 1)
        subtotal = (unit * Decimal(quantity)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    elif item_type == BookingType.HOTEL:
        unit = _dec(item.get("price_per_night"))
        quantity = _hotel_nights(params)
        subtotal = (unit * Decimal(quantity)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    elif item_type == BookingType.ACTIVITY:
        unit = _dec(item.get("price"))
        quantity = max(int(params.get("guests", 1) or 1), 1)
        subtotal = (unit * Decimal(quantity)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        return ZERO, ZERO, ZERO, currency

    taxes = ZERO  # Phase 9: no tax engine.
    total = subtotal
    return subtotal, taxes, total, currency


def expected_traveler_count(item_type, params):
    """How many traveler/guest/participant forms are required for a selection."""
    def valid_count(value):
        try:
            return max(int(value or 1), 1)
        except (TypeError, ValueError):
            return 1

    if item_type == BookingType.FLIGHT:
        return valid_count(params.get("adults", 1))
    if item_type == BookingType.HOTEL:
        return valid_count(params.get("guests", 1))
    if item_type == BookingType.ACTIVITY:
        return valid_count(params.get("guests", 1))
    return 1
def _traveler_type_for(item_type):
    if item_type == BookingType.FLIGHT:
        return "adult"
    return "guest"  # hotels and activities use a generic guest/participant record


def build_booking_item(booking, item_type, item, params):
    """Create a BookingItem from a trusted inventory item."""
    selection_key = compute_selection_key(item_type, params)

    if item_type == BookingType.FLIGHT:
        title = f"{item.get('airline', '')} {item.get('flight_number', '')}".strip()
        route = f"{item.get('origin', '')} → {item.get('destination', '')}"
        try:
            start_date = datetime.strptime(params.get("departure", ""), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            start_date = None
        end_date = None
        metadata = {
            "baggage": item.get("baggage", ""),
            "trip_type": params.get("trip_type", "one-way"),
            "return": params.get("return", ""),
        }
    elif item_type == BookingType.HOTEL:
        title = item.get("hotel_name", "")
        route = item.get("location", "")
        try:
            start_date = datetime.strptime(params.get("check_in", ""), "%Y-%m-%d").date()
            end_date = datetime.strptime(params.get("check_out", ""), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            start_date = None
            end_date = None
        metadata = {
            "rating": item.get("rating", ""),
            "review_count": item.get("review_count", ""),
            "guests": params.get("guests", 1),
            "rooms": params.get("rooms", 1),
            "nights": _hotel_nights(params),
            "price_per_night": str(item.get("price_per_night", "0")),
        }
    else:  # ACTIVITY
        title = item.get("activity_name", "")
        route = item.get("destination", "")
        try:
            start_date = datetime.strptime(params.get("date", ""), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            start_date = None
        end_date = None
        metadata = {
            "rating": item.get("rating", ""),
            "review_count": item.get("review_count", ""),
            "participants": params.get("guests", 1),
        }

    subtotal, _taxes, _total, currency = calculate_price(item_type, item, params)

    return BookingItem.objects.create(
        booking=booking,
        item_type=item_type,
        provider="Demo Provider",
        provider_reference=selection_key[:20],
        title=title,
        route_or_destination=route,
        start_date=start_date,
        end_date=end_date,
        departure_time=str(item.get("departure_time", "")),
        arrival_time=str(item.get("arrival_time", "")),
        duration=str(item.get("duration", "")),
        stops=item.get("stops"),
        cabin_class=str(item.get("cabin_class", "")),
        room_type=str(item.get("room_type", "")),
        amenities=item.get("amenities", []) or [],
        cancellation_policy=str(item.get("cancellation_policy", "")),
        category=str(item.get("category", "")),
        description=str(item.get("description", "")),
        meeting_point=str(item.get("meeting_point", "")),
        price=subtotal,
        currency=currency,
        selection_key=selection_key,
        metadata={
            **metadata,
            # Persist the complete server-verified normalized provider result.
            # This is a snapshot for the booking record, never client input.
            "inventory_snapshot": item,
            "demo": True,
            "source": "demo_provider",
        },
    )


def user_has_confirmed_selection(user, item_type, params):
    """True if this user already has a CONFIRMED item for the same selection."""
    selection_key = compute_selection_key(item_type, params)
    return BookingItem.objects.filter(
        booking__user=user,
        booking__status=BookingStatus.CONFIRMED,
        selection_key=selection_key,
    ).exists()


def confirm_booking(booking):
    """Finalize a fully assembled server-owned demo booking.

    Confirmation is deliberately restricted to draft/pending records.  The
    caller must create the booking, inventory snapshot, and traveler records
    in the same transaction before this transition is attempted.
    """
    if booking.status not in (BookingStatus.DRAFT, BookingStatus.PENDING):
        raise ValueError("Only a draft or pending booking can be confirmed.")
    if not booking.items.exists() or not booking.travelers.exists():
        raise ValueError("A booking needs inventory and traveler details before confirmation.")

    booking.status = BookingStatus.CONFIRMED
    booking.save(update_fields=["status", "updated_at"])
    return booking


def create_booking(user, item_type, params, travelers_data):
    """
    Atomically create and confirm a demo booking.

    Returns (booking, state) where state is one of:
        "created"           — new booking created
        "already_confirmed" — duplicate confirmation prevented

    Duplicate POST / double-click / browser-retry is handled by the
    selection_key check inside the same atomic block.
    """
    item, error = resolve_inventory(item_type, params)
    if item is None:
        return None, f"error:{error}"

    subtotal, taxes, total, currency = calculate_price(item_type, item, params)

    with transaction.atomic():
        # Serialise confirmations for this owner before checking the
        # selection. This closes the normal double-submit/race window while
        # preserving per-user (not global) duplicate protection.
        get_user_model().objects.select_for_update().get(pk=user.pk)
        if user_has_confirmed_selection(user, item_type, params):
            return None, "already_confirmed"

        booking = Booking.objects.create(
            user=user,
            booking_reference=generate_booking_reference(),
            # The booking only becomes CONFIRMED after its trusted inventory
            # snapshot and all validated traveler records have been saved.
            status=BookingStatus.DRAFT,
            booking_type=item_type,
            subtotal=subtotal,
            taxes=taxes,
            total=total,
            currency=currency,
            is_demo=True,
        )
        build_booking_item(booking, item_type, item, params)

        traveler_type = _traveler_type_for(item_type)
        for entry in travelers_data:
            Traveler.objects.create(
                booking=booking,
                first_name=(entry.get("first_name") or "").strip(),
                last_name=(entry.get("last_name") or "").strip(),
                email=(entry.get("email") or "").strip().lower(),
                phone=(entry.get("phone") or "").strip(),
                nationality=(entry.get("nationality") or "").strip(),
                traveler_type=traveler_type,
            )

        confirm_booking(booking)

    return booking, "created"
