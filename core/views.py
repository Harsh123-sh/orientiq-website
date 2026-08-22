from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
import json

from django.db import transaction
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import RedirectView

from .data import (
    PRODUCTS,
    SERVICES,
    INDUSTRIES,
    TECHNOLOGIES,
)
from .models import (
    Booking,
    BookingItem,
    BookingStatus,
    BookingType,
    ContactInquiry,
    Profile,
)
from .forms import (
    CustomPasswordChangeForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    LoginForm,
    ProfileForm,
    RegisterForm,
    GuestForm,
    TravelerForm,
    build_booking_forms,
)
from .emails import booking_confirmation_email
from .services.booking import (
    calculate_price,
    compute_selection_key,
    create_booking as booking_service_create,
    DEMO_DISCLAIMER,
    expected_traveler_count,
    is_booking_rate_limited,
    resolve_inventory,
)


def home(request):
    """Render the ORENTIQ homepage."""
    return render(
        request,
        "pages/home.html",
        {
            "services": SERVICES[:4],
            "industries": INDUSTRIES[:6],
        },
    )


def about(request):
    """Render the About page."""
    return render(request, "pages/about.html")


def services(request):
    """Render the Services overview page."""
    ai_features = [
        "AI Business Consultant",
        "AI Chatbot",
        "RAG Chatbot",
        "AI Search",
        "AI Service Recommendation",
        "AI Requirement Analyzer",
        "AI Quote Assistant",
        "AI FAQ Assistant",
        "AI Knowledge Base",
        "Smart Contact Assistant",
    ]

    return render(request, "pages/services.html", {"services": SERVICES, "ai_features": ai_features})


def service_detail(request, slug):
    """Render a service detail page."""
    service = next((s for s in SERVICES if s["slug"] == slug), None)
    if service is None:
        return render(request, "pages/404.html", status=404)
    return render(
        request,
        "services/detail.html",
        {"service": service, "services": SERVICES},
    )


def industries(request):
    """Render the Industries overview page."""
    return render(request, "pages/industries.html", {"industries": INDUSTRIES})


def industry_detail(request, slug):
    """Render an industry detail page."""
    industry = next((i for i in INDUSTRIES if i["slug"] == slug), None)
    if industry is None:
        return render(request, "pages/404.html", status=404)
    return render(
        request,
        "industries/detail.html",
        {"industry": industry, "industries": INDUSTRIES},
    )


def portfolio(request):
    """Public portfolio page is intentionally unavailable."""
    return render(request, "pages/404.html", status=404)


def portfolio_detail(request, slug):
    """Public portfolio detail pages are intentionally unavailable."""
    return render(request, "pages/404.html", status=404)


def technologies(request):
    """Render the Technologies page."""
    return render(
        request,
        "pages/technologies.html",
        {"technologies": TECHNOLOGIES},
    )


def company(request):
    """Render the Company overview page."""
    return render(request, "pages/company.html")


def company_about(request):
    """Render the Company About page."""
    return render(request, "company/about.html")


def company_process(request):
    """Render the Company Process page."""
    return render(request, "company/process.html")


def company_careers(request):
    """Render the Company Careers page."""
    return render(request, "company/careers.html")


def company_contact(request):
    """Handle contact submissions and display the confirmation message."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not email or not message:
            messages.error(request, "Please complete your name, email, and message.")
            return render(request, "company/contact.html")

        record, created = ContactInquiry.objects.get_or_create(
            name=name,
            email=email,
            message=message,
        )

        if not created:
            record.name = name
            record.email = email
            record.message = message
            record.save(update_fields=["name", "email", "message", "updated_at"])

        messages.success(request, "Thank you for contacting us.\n\nWe'll get back to you soon.")
        return redirect("company_contact")

    return render(request, "company/contact.html")


def start_project(request):
    """Render the Start a Project page and save inquiries."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        if name and email:
            ContactInquiry.objects.create(
                name=name,
                email=email,
                phone=request.POST.get("phone", ""),
                company=request.POST.get("company", ""),
                service=request.POST.get("project_type", ""),
                budget=request.POST.get("budget", ""),
                message=request.POST.get("message", ""),
            )
            messages.success(
                request,
                "Thank you! Your project inquiry has been received. We'll get back to you within one business day.",
            )
            return redirect("start_project")
        messages.error(request, "Please provide your name and email.")
    return render(request, "pages/start-project.html")


def products(request):
    """Render the Products showcase page."""
    return render(
        request,
        "pages/products.html",
        {"products": PRODUCTS},
    )


def product_detail(request, slug):
    """Render a product detail (coming-soon) page."""
    product = next((p for p in PRODUCTS if p["slug"] == slug), None)
    if product is None:
        return render(request, "pages/404.html", status=404)
    return render(
        request,
        "products/detail.html",
        {"product": product, "products": PRODUCTS},
    )


def design_system(request):
    """Render the Phase 1 design system showcase (dev-only)."""
    return render(request, "pages/design-system.html")


class FaviconRedirectView(RedirectView):
    """Redirect /favicon.ico to the official Orientiq icon."""

    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        return static("images/brand/Icon Luxry Light..png")


# ============================================================
# AUTHENTICATION VIEWS
# ============================================================

def register(request):
    """Register a new user account."""
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # With multiple auth backends, Django requires the backend attribute.
            user.backend = "core.backends.EmailOrUsernameModelBackend"
            login(request, user)
            messages.success(request, "Welcome to ORENTIQ! Your account has been created.")
            return redirect("accounts_profile")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


class OrientiqLoginView(LoginView):
    """Login view styled for Orientiq."""

    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.get_redirect_url():
            return self.get_redirect_url()
        # Redirect admins to the admin dashboard, others to their profile.
        if self.request.user.is_authenticated:
            from .permissions import is_admin
            if is_admin(self.request.user):
                return reverse_lazy("admin_dashboard")
        return reverse_lazy("accounts_profile")


def logout_view(request):
    """Log out the current user."""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


class OrientiqPasswordResetView(PasswordResetView):
    """Password reset request view."""

    template_name = "accounts/forgot_password.html"
    form_class = CustomPasswordResetForm
    email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("accounts_password_reset_done")


class OrientiqPasswordResetConfirmView(PasswordResetConfirmView):
    """Password reset confirmation view."""

    template_name = "accounts/reset_password.html"
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy("accounts_password_reset_complete")


@login_required
def profile(request):
    """View the current user's profile."""
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "accounts/profile.html", {"profile": profile_obj})


@login_required
def account_settings(request):
    """Edit profile and account settings."""
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts_settings")
    else:
        form = ProfileForm(instance=profile_obj, user=request.user)

    return render(
        request,
        "accounts/settings.html",
        {"form": form, "profile": profile_obj},
    )


class OrientiqPasswordChangeView(PasswordChangeView):
    """Change password view."""

    template_name = "accounts/change_password.html"
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy("accounts_settings")

    def form_valid(self, form):
        response = super().form_valid(form)
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, "Your password has been changed.")
        return response


# ============================================================
# LIVE INTELLIGENCE (PHASE 7)
# ============================================================

def live_intelligence_page(request):
    """Render the Phase 7 live intelligence foundation demo page."""
    return render(request, "pages/live-intelligence.html")


def api_location_search(request):
    """GET /api/location/search/?q=... — search locations."""
    from .services.location_service import search_locations

    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"success": False, "error": "Location query is required."}, status=400)

    result = search_locations(query)
    if not result["success"]:
        return JsonResponse({"success": False, "error": result["error"]}, status=400)

    results = result.get("results", [])
    if not results:
        return JsonResponse({"success": False, "error": "Location not found."}, status=404)

    return JsonResponse({"success": True, "results": results})


def api_weather(request):
    """GET /api/weather/?q=... — current weather for a location."""
    from .services.location_service import get_location_by_name
    from .services.weather_service import get_current_weather

    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"success": False, "error": "Location query is required."}, status=400)

    location = get_location_by_name(query)
    if not location:
        return JsonResponse({"success": False, "error": f"No location found for '{query}'."}, status=404)

    result = get_current_weather(location)
    if not result["success"]:
        return JsonResponse({"success": False, "error": result["error"]}, status=503)
    return JsonResponse({"success": True, "data": result["data"]})


def api_live_intelligence(request):
    """GET /api/live-intelligence/?q=... — combined live intelligence."""
    from .services.live_intelligence import get_destination_intelligence

    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"success": False, "error": "Destination is required."}, status=400)

    result = get_destination_intelligence(query)
    if not result["success"]:
        return JsonResponse({"success": False, "error": result["error"]}, status=404)
    return JsonResponse({"success": True, "data": result["data"]})


# ============================================================
# TRAVEL INVENTORY (PHASE 8)
# ============================================================

def travel_search_page(request):
    """Render the Phase 8 travel inventory demo page."""
    return render(request, "pages/travel-search.html")


def api_flights_search(request):
    """GET /api/flights/search/ — flight inventory search."""
    from .services.travel.flights import search_flights

    result = search_flights(request.GET)
    if not result["success"]:
        return JsonResponse({"success": False, "error": result["error"], "results": []}, status=400)
    return JsonResponse({"success": True, "results": result["results"], "demo": result["demo"]})


def api_hotels_search(request):
    """GET /api/hotels/search/ — hotel inventory search."""
    from .services.travel.hotels import search_hotels

    result = search_hotels(request.GET)
    if not result["success"]:
        return JsonResponse({"success": False, "error": result["error"], "results": []}, status=400)
    return JsonResponse({"success": True, "results": result["results"], "demo": result["demo"]})


def api_activities_search(request):
    """GET /api/activities/search/ — activity inventory search."""
    from .services.travel.activities import search_activities

    result = search_activities(request.GET)
    if not result["success"]:
        return JsonResponse({"success": False, "error": result["error"], "results": []}, status=400)
    return JsonResponse({"success": True, "results": result["results"], "demo": result["demo"]})


# ============================================================
# BOOKINGS (PHASE 9) — Booking + Reservation Workflow Foundation
# ============================================================

def _extract_selection_params(item_type, data):
    """Copy only the params the server needs to rebuild a trusted selection."""
    t = str(item_type)
    if t == "flight":
        keys = ("origin", "destination", "departure", "return", "trip_type",
                "adults", "children", "infants", "cabin_class", "flight_number", "sort")
    elif t == "hotel":
        keys = ("destination", "check_in", "check_out", "guests", "rooms",
                "hotel_name", "sort")
    else:
        keys = ("destination", "date", "guests", "category", "activity_name", "sort")
    return {k: data.get(k, "") for k in keys}


def _review_inventory(item_type, item, params):
    """Normalize a trusted inventory item for template display."""
    from .services.booking import _hotel_nights

    t = str(item_type)
    if t == "flight":
        return {
            "kind": "flight",
            "airline": item.get("airline"),
            "flight_number": item.get("flight_number"),
            "origin": item.get("origin"),
            "destination": item.get("destination"),
            "departure_date": params.get("departure", ""),
            "departure_time": item.get("departure_time"),
            "arrival_time": item.get("arrival_time"),
            "duration": item.get("duration"),
            "stops": item.get("stops"),
            "cabin_class": item.get("cabin_class"),
            "baggage": item.get("baggage"),
            "price": item.get("price"),
            "travelers": params.get("adults", 1),
        }
    if t == "hotel":
        return {
            "kind": "hotel",
            "hotel_name": item.get("hotel_name"),
            "location": item.get("location"),
            "rating": item.get("rating"),
            "room_type": item.get("room_type"),
            "amenities": item.get("amenities") or [],
            "cancellation_policy": item.get("cancellation_policy"),
            "price_per_night": item.get("price_per_night"),
            "nights": _hotel_nights(params),
            "check_in": params.get("check_in", ""),
            "check_out": params.get("check_out", ""),
            "guests": params.get("guests", 1),
            "rooms": params.get("rooms", 1),
        }
    return {
        "kind": "activity",
        "activity_name": item.get("activity_name"),
        "destination": item.get("destination"),
        "category": item.get("category"),
        "description": item.get("description"),
        "duration": item.get("duration"),
        "meeting_point": item.get("meeting_point"),
        "date": params.get("date", ""),
        "participants": params.get("guests", 1),
        "price": item.get("price"),
    }


@login_required
def booking_review_page(request):
    """Booking Review — server rebuilds and prices the selected inventory.

    The selection params arrive via query-string; the server re-runs the
    Phase 8 demo search to obtain a trusted price. Client-submitted prices
    are never used.
    """
    from .forms import build_booking_forms
    from .models import BookingType
    from .services.booking import (
        calculate_price,
        DEMO_DISCLAIMER,
        expected_traveler_count,
        resolve_inventory,
    )

    item_type_raw = request.GET.get("item_type", "").strip()
    try:
        item_type = BookingType(item_type_raw)
    except ValueError:
        messages.error(request, "Please select a flight, hotel, or activity first.")
        return redirect("travel_search")

    params = _extract_selection_params(item_type, request.GET)
    item, error = resolve_inventory(item_type, params)
    if item is None:
        messages.error(request, error)
        return redirect("travel_search")

    subtotal, taxes, total, currency = calculate_price(item_type, item, params)
    person_forms = build_booking_forms(
        str(item_type), expected_traveler_count(item_type, params)
    )
    return render(
        request,
        "pages/booking-review.html",
        {
            "item_type": item_type,
            "item": _review_inventory(item_type, item, params),
            "booking_params": params,
            "subtotal": subtotal,
            "taxes": taxes,
            "total": total,
            "currency": currency,
            "quantity": expected_traveler_count(item_type, params),
            "person_forms": person_forms,
            "demo_disclaimer": DEMO_DISCLAIMER,
        },
    )


@login_required
@require_POST
def create_booking(request):
    """Confirm Demo Booking — POST only, CSRF protected.

    Validates the authenticated user, rebuilds inventory server-side,
    validates traveler data, recalculates the price with Decimal, creates the
    Booking + BookingItem + Traveler records atomically, and guards against
    duplicate confirmation via the selection_key check.
    """
    from django.db import transaction

    from .forms import build_booking_forms
    from .models import BookingItem, BookingStatus, BookingType
    from .services.booking import (
        calculate_price,
        compute_selection_key,
        create_booking as booking_service_create,
        DEMO_DISCLAIMER,
        expected_traveler_count,
        is_booking_rate_limited,
        resolve_inventory,
    )

    # Rate limiting (server-side, cache-backed).
    if is_booking_rate_limited(request, cache):
        return HttpResponse(
            "Too many booking attempts. Please wait a moment and try again.",
            status=429,
            content_type="text/plain",
        )

    item_type_raw = request.POST.get("item_type", "").strip()
    try:
        item_type = BookingType(item_type_raw)
    except ValueError:
        messages.error(request, "Invalid booking type.")
        return redirect("travel_search")

    params = _extract_selection_params(item_type, request.POST)
    # Validate the selected inventory before deriving the number of forms.
    # This keeps malformed client quantities from reaching form construction.
    item, error = resolve_inventory(item_type, params)
    if item is None:
        messages.error(request, error)
        return redirect("travel_search")

    quantity = expected_traveler_count(item_type, params)
    person_forms = build_booking_forms(str(item_type), quantity, data=request.POST)

    # ---- Server-side person/guest/participant validation -----
    if any(not form.is_valid() for form in person_forms):
        subtotal, taxes, total, currency = calculate_price(item_type, item, params)
        return render(
            request,
            "pages/booking-review.html",
            {
                "item_type": item_type,
                "item": _review_inventory(item_type, item, params),
                "booking_params": params,
                "subtotal": subtotal,
                "taxes": taxes,
                "total": total,
                "currency": currency,
                "quantity": quantity,
                "person_forms": person_forms,
                "demo_disclaimer": DEMO_DISCLAIMER,
            },
        )

    travelers_data = []
    is_guest_type = str(item_type) in ("hotel", "activity")
    for form in person_forms:
        cleaned = form.cleaned_data
        if is_guest_type:
            travelers_data.append(
                {
                    "first_name": cleaned.get("name", ""),
                    "last_name": "",
                    "email": cleaned.get("email", ""),
                    "phone": cleaned.get("phone", ""),
                    "nationality": "",
                }
            )
        else:
            travelers_data.append(
                {
                    "first_name": cleaned.get("first_name", ""),
                    "last_name": cleaned.get("last_name", ""),
                    "email": cleaned.get("email", ""),
                    "phone": cleaned.get("phone", ""),
                    "nationality": cleaned.get("nationality", ""),
                }
            )

    booking, state = booking_service_create(
        request.user, item_type, params, travelers_data
    )

    if state == "already_confirmed":
        # Find the already-confirmed booking for this exact selection.
        existing_item = BookingItem.objects.filter(
            booking__user=request.user,
            booking__status=BookingStatus.CONFIRMED,
            selection_key=compute_selection_key(item_type, params),
        ).select_related("booking").first()
        messages.info(request, "Booking has already been confirmed.")
        if existing_item:
            return redirect("booking_confirmation", reference=existing_item.booking.booking_reference)
        return redirect("user_booking_list")

    if state.startswith("error:"):
        messages.error(request, state[len("error:"):])
        return redirect("travel_search")

    # Email is sent after the transaction commits; a mail failure can never
    # corrupt the successfully committed booking.
    transaction.on_commit(
        lambda b=booking: _send_booking_confirmation_email(b)
    )
    messages.success(
        request, f"Your demo booking {booking.booking_reference} is confirmed."
    )
    return redirect("booking_confirmation", reference=booking.booking_reference)


def _send_booking_confirmation_email(booking):
    """Thin on_commit-safe wrapper around core.emails."""
    from .emails import booking_confirmation_email

    try:
        booking_confirmation_email(booking)
    except Exception:
        # Must never break the booking flow.
        pass


@login_required
def booking_confirmation(request, reference):
    """Booking Confirmation — always ownership-scoped to the current user."""
    from .models import Booking

    booking = get_object_or_404(
        Booking.objects.select_related("user"),
        booking_reference=reference,
        user=request.user,
    )
    items = booking.items.select_related("booking").all()
    travelers = booking.travelers.all()
    return render(
        request,
        "pages/booking-confirmation.html",
        {
            "booking": booking,
            "items": items,
            "travelers": travelers,
            "demo_disclaimer": DEMO_DISCLAIMER,
        },
    )


@login_required
def user_booking_list(request):
    """My Bookings — list only the logged-in user's bookings."""
    from .models import Booking

    bookings = (
        Booking.objects.filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )
    return render(
        request,
        "accounts/bookings.html",
        {"bookings": bookings, "count": bookings.count()},
    )


@login_required
def user_booking_detail(request, reference):
    """Booking Detail — ownership is enforced via booking_reference + user."""
    from .models import Booking

    booking = get_object_or_404(
        Booking.objects.select_related("user").prefetch_related("items", "travelers"),
        booking_reference=reference,
        user=request.user,
    )
    items = booking.items.all()
    travelers = booking.travelers.all()
    return render(
        request,
        "accounts/booking-detail.html",
        {
            "booking": booking,
            "items": items,
            "travelers": travelers,
            "demo_disclaimer": DEMO_DISCLAIMER,
        },
    )


@login_required
def api_booking_list(request):
    """GET /api/bookings/ — list the authenticated user's bookings (JSON)."""
    from .models import Booking

    bookings = Booking.objects.filter(user=request.user).order_by("-created_at")
    return JsonResponse(
        {
            "success": True,
            "count": bookings.count(),
            "bookings": [
                {
                    "booking_reference": b.booking_reference,
                    "booking_type": b.get_booking_type_display(),
                    "status": b.get_status_display(),
                    "total": str(b.total),
                    "currency": b.currency,
                    "is_demo": b.is_demo,
                    "created_at": b.created_at.isoformat(),
                }
                for b in bookings
            ],
        }
    )


@login_required
@require_POST
def api_create_booking(request):
    """POST /api/bookings/create/ — create a demo booking (JSON API).

    Body: {"item_type": "flight|hotel|activity", "params": {...},
           "travelers": [{first_name, last_name, email, phone}, ...]}
    """
    import json as _json

    from .models import BookingType

    # Apply the same cache-backed per-IP protection as the HTML confirmation
    # route. This endpoint can create bookings and must not be unbounded.
    if is_booking_rate_limited(request, cache):
        return JsonResponse(
            {"success": False, "error": "Too many booking attempts. Please wait and try again."},
            status=429,
        )

    try:
        payload = _json.loads(request.body.decode("utf-8") or "{}")
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request format."}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"success": False, "error": "Invalid request format."}, status=400)

    item_type_raw = str(payload.get("item_type", "")).strip()
    try:
        item_type = BookingType(item_type_raw)
    except ValueError:
        return JsonResponse({"success": False, "error": "Invalid booking type."}, status=400)

    raw_params = payload.get("params", {})
    if not isinstance(raw_params, dict):
        return JsonResponse({"success": False, "error": "Invalid selection data."}, status=400)
    params = _extract_selection_params(item_type, raw_params)
    travelers_data = payload.get("travelers", [])

    if not isinstance(travelers_data, list) or len(travelers_data) != expected_traveler_count(item_type, params):
        return JsonResponse({"success": False, "error": "Traveler count does not match the selection."}, status=400)

    normalized_travelers = []
    is_guest_type = item_type in (BookingType.HOTEL, BookingType.ACTIVITY)
    for entry in travelers_data:
        if not isinstance(entry, dict):
            return JsonResponse({"success": False, "error": "Invalid traveler details."}, status=400)

        if is_guest_type:
            form = GuestForm(
                {
                    "name": entry.get("name") or entry.get("first_name", ""),
                    "email": entry.get("email", ""),
                    "phone": entry.get("phone", ""),
                }
            )
        else:
            form = TravelerForm(entry)
        if not form.is_valid():
            return JsonResponse({"success": False, "error": "Invalid traveler details."}, status=400)

        cleaned = form.cleaned_data
        normalized_travelers.append(
            {
                "first_name": cleaned.get("name", cleaned.get("first_name", "")),
                "last_name": cleaned.get("last_name", ""),
                "email": cleaned["email"],
                "phone": cleaned.get("phone", ""),
                "nationality": cleaned.get("nationality", ""),
            }
        )

    booking, state = booking_service_create(
        request.user, item_type, params, normalized_travelers
    )

    if state == "already_confirmed":
        existing_item = BookingItem.objects.filter(
            booking__user=request.user,
            booking__status=BookingStatus.CONFIRMED,
            selection_key=compute_selection_key(item_type, params),
        ).select_related("booking").first()
        reference = existing_item.booking.booking_reference if existing_item else None
        return JsonResponse(
            {
                "success": True,
                "already_confirmed": True,
                "message": "Booking has already been confirmed.",
                "booking_reference": reference,
            }
        )

    if state.startswith("error:"):
        return JsonResponse({"success": False, "error": state[len("error:"):]}, status=400)

    transaction.on_commit(lambda b=booking: _send_booking_confirmation_email(b))
    return JsonResponse(
        {
            "success": True,
            "booking_reference": booking.booking_reference,
            "status": booking.get_status_display(),
            "total": str(booking.total),
            "currency": booking.currency,
            "is_demo": booking.is_demo,
        }
    )


@login_required
def api_booking_detail(request, reference):
    """GET /api/bookings/<reference>/ — ownership enforced (JSON)."""
    from .models import Booking, BookingItem

    booking_obj = get_object_or_404(
        Booking,
        booking_reference=reference,
        user=request.user,
    )
    items = BookingItem.objects.filter(booking=booking_obj)
    travelers = list(
        booking_obj.travelers.values("first_name", "last_name", "email", "phone", "traveler_type")
    )
    return JsonResponse(
        {
            "success": True,
            "booking": {
                "booking_reference": booking_obj.booking_reference,
                "booking_type": booking_obj.get_booking_type_display(),
                "status": booking_obj.get_status_display(),
                "subtotal": str(booking_obj.subtotal),
                "taxes": str(booking_obj.taxes),
                "total": str(booking_obj.total),
                "currency": booking_obj.currency,
                "is_demo": booking_obj.is_demo,
                "created_at": booking_obj.created_at.isoformat(),
                "items": [
                    {
                        "title": it.title,
                        "route_or_destination": it.route_or_destination,
                        "price": str(it.price),
                        "currency": it.currency,
                    }
                    for it in items
                ],
                "travelers": travelers,
            },
        }
    )



# ============================================================
# AI ASSISTANT
# ============================================================

@require_POST
def ai_chat(request):
    """POST /api/ai/chat/ — AI assistant chat endpoint.

    Accepts JSON: {"message": "...", "history": [...]}
    Returns JSON with the AI response and navigation suggestions.
    """
    from .ai.safety import is_rate_limited, validate_message
    from .ai.service import generate_response

    # Rate limiting (simple per-IP cache-based).
    if is_rate_limited(request, cache):
        return JsonResponse(
            {
                "success": False,
                "message": "You're sending too many messages. Please wait a moment and try again.",
                "suggestions": [],
            },
            status=429,
        )

    # Parse JSON body.
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request format.",
                "suggestions": [],
            },
            status=400,
        )

    message = payload.get("message", "")
    history = payload.get("history", [])

    # Validate message.
    is_valid, error = validate_message(message)
    if not is_valid:
        return JsonResponse(
            {
                "success": False,
                "message": error,
                "suggestions": [],
            },
            status=400,
        )

    # Validate history shape (list of dicts, keep small).
    if not isinstance(history, list):
        history = []
    history = history[:10]

    result = generate_response(message, history)

    if not result["success"]:
        return JsonResponse(result, status=503)

    return JsonResponse(result)
