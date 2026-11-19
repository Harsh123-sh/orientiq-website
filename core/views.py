from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.conf import settings
from django.core.mail import BadHeaderError, send_mail
from django.core.exceptions import ValidationError
from django.core.cache import cache
import json
import logging
import smtplib
import uuid
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_GET, require_POST
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
    ChatbotConversation,
    ConsultationRequest,
    HumanSupportRequest,
    InquiryAttachment,
    ClientAccount,
    ClientDocument,
    ClientDeletionRequest,
    ActivityLog,
    ProjectUpdate,
    CandidateApplication,
    Profile,
    UserRole,
)
from .forms import (
    ChatbotInquiryForm,
    ConsultationRequestForm,
    HumanSupportRequestForm,
    validate_chatbot_attachment,
    CandidateApplicationForm,
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
from .permissions import is_admin


logger = logging.getLogger(__name__)


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


@require_GET
def robots_txt(request):
    """Serve the root robots.txt file."""
    robots_file = settings.BASE_DIR / "robots.txt"
    return HttpResponse(
        robots_file.read_text(encoding="utf-8"),
        content_type="text/plain; charset=utf-8",
    )


def about(request):
    """Render the About page."""
    return render(request, "pages/about.html")


def problem_solving(request):
    """Show ORENTIQ's problem-solving approach and illustrative solution paths."""
    return render(request, "pages/problem-solving.html")


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


def company_founder(request):
    """Render the Founder page."""
    return render(request, "company/founder.html")


def company_process(request):
    """Render the Company Process page."""
    return render(request, "company/process.html")


def company_careers(request):
    """Render Careers and accept consented profiles for future consideration."""
    if request.method == "POST":
        client_ip = request.META.get("REMOTE_ADDR", "unknown")
        rate_key = f"candidate-application:{client_ip}"
        attempts = cache.get(rate_key, 0)
        if attempts >= 3:
            form = CandidateApplicationForm(request.POST, request.FILES)
            form.add_error(None, "Please wait before submitting another profile.")
            return render(request, "company/careers.html", {"application_form": form, "open_application_modal": True}, status=429)

        form = CandidateApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data["email"]
            introduction = form.cleaned_data["introduction"].strip()
            recent_duplicate = CandidateApplication.objects.filter(
                email=email, introduction=introduction,
            ).order_by("-created_at").first()
            if recent_duplicate and (timezone.now() - recent_duplicate.created_at).total_seconds() < 300:
                form.add_error(None, "This profile was submitted recently. Please avoid duplicate submissions.")
            else:
                form.save()
                cache.set(rate_key, attempts + 1, 3600)
                return render(request, "company/careers.html", {"application_form": CandidateApplicationForm(), "application_success": True})
        return render(request, "company/careers.html", {"application_form": form, "open_application_modal": True}, status=400)

    return render(request, "company/careers.html", {"application_form": CandidateApplicationForm()})


@login_required
def candidate_resume_download(request, pk):
    """Serve applicant resumes only to authorized internal administrators."""
    from .permissions import require_admin
    require_admin(request.user)
    application = get_object_or_404(CandidateApplication, pk=pk)
    if not application.resume:
        raise Http404("No resume is attached to this application.")
    return FileResponse(application.resume.open("rb"), as_attachment=True, filename=application.resume.name.rsplit("/", 1)[-1])


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
                title=request.POST.get("project_type", "").strip(),
                budget=request.POST.get("budget", ""),
                timeline=request.POST.get("timeline", ""),
                message=request.POST.get("message", ""),
                source="start_project",
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
    """Redirect /favicon.ico to the official Orentiq icon."""

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
            ClientAccount.objects.get_or_create(
                user=user,
                defaults={
                    "company": form.cleaned_data.get("company", ""),
                    "phone": form.cleaned_data.get("phone", ""),
                    "status": "active",
                },
            )
            user.backend = "core.backends.EmailOrUsernameModelBackend"
            login(request, user)
            messages.success(request, "Welcome to ORENTIQ! Your account has been created.")
            return redirect("accounts_profile")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


class OrentiqLoginView(LoginView):
    """Login view styled for Orentiq."""

    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_staff or self.request.user.is_superuser or is_admin(self.request.user):
            return reverse("admin_dashboard")

        next_url = self.get_redirect_url()
        if next_url:
            return next_url

        return "/accounts/dashboard/"


def logout_view(request):
    """Log out the current user."""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


class OrentiqPasswordResetView(PasswordResetView):
    """Password reset request view."""

    template_name = "accounts/forgot_password.html"
    form_class = CustomPasswordResetForm
    email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("accounts_password_reset_done")


class OrentiqPasswordResetConfirmView(PasswordResetConfirmView):
    """Password reset confirmation view."""

    template_name = "accounts/reset_password.html"
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy("accounts_password_reset_complete")


@login_required
def profile(request):
    """View the current user's profile."""
    if is_admin(request.user):
        return redirect("admin_profile")
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "accounts/profile.html", {"profile": profile_obj})


@login_required
def account_settings(request):
    """Edit profile and account settings."""
    if is_admin(request.user):
        return redirect("admin_profile")
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


class OrentiqPasswordChangeView(PasswordChangeView):
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
def client_dashboard(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("/admin/")

    profile = getattr(request.user, "profile", None)
    account = getattr(request.user, "client_account", None)

    if not profile or profile.role != UserRole.CLIENT or account is None:
        return redirect("/accounts/profile/")

    if account.status != "active" or not request.user.is_active:
        messages.error(request, "Your client account is not currently active.")
        return redirect("accounts_logout")

    projects = account.projects.prefetch_related("updates").all()
    documents = account.documents.select_related("project").all()

    return render(
        request,
        "accounts/client_dashboard.html",
        {
            "profile": profile,
            "account": account,
            "projects": projects,
            "documents": documents,
            "updates": ProjectUpdate.objects.filter(
                project__clients=account, visible_to_client=True
            ).select_related("project")[:8],
        },
    )


@login_required
def client_document_download(request, pk):
    """Serve a document only after checking the logged-in client's ownership."""
    account = getattr(request.user, "client_account", None)
    if not account or account.status != "active":
        raise Http404("Document not found.")
    document = get_object_or_404(ClientDocument, pk=pk, client=account)
    if not document.file:
        raise Http404("Document is unavailable.")
    return FileResponse(
        document.file.open("rb"),
        as_attachment=True,
        filename=document.file.name.rsplit("/", 1)[-1],
    )


@login_required
@require_POST
def client_deletion_request(request):
    account = getattr(request.user, "client_account", None)
    if not account or account.status in {"suspended", "deletion_requested"}:
        messages.error(request, "This account cannot submit another deletion request.")
        return redirect("accounts_settings")
    ClientDeletionRequest.objects.create(client=account)
    account.status = "deletion_requested"
    account.save(update_fields=["status", "updated_at"])
    ActivityLog.objects.create(
        user=request.user,
        action="deletion_request",
        object_type="ClientAccount",
        object_id=account.id,
        description=f"Client {account.client_id} requested account deletion.",
        ip_address=request.META.get("REMOTE_ADDR"),
    )
    messages.success(request, "Your deletion request has been submitted for review.")
    return redirect("accounts_settings")

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

    content_length = request.META.get("CONTENT_LENGTH")
    if content_length and content_length.isdigit() and int(content_length) > 24000:
        return JsonResponse(
            {"success": False, "message": "The chat request is too large.", "suggestions": []},
            status=413,
        )

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

    if not isinstance(payload, dict):
        return JsonResponse(
            {"success": False, "message": "Invalid request format.", "suggestions": []},
            status=400,
        )

    message = payload.get("message", "")
    history = payload.get("history", [])
    language = payload.get("language", "auto")
    if language not in {"auto", "en", "hi", "gu"}:
        return JsonResponse(
            {"success": False, "message": "Choose English, Hindi, or Gujarati.", "suggestions": []},
            status=400,
        )

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

    if not isinstance(history, list) or len(history) > 10:
        return JsonResponse(
            {"success": False, "message": "Conversation history is invalid.", "suggestions": []},
            status=400,
        )

    clean_history = []
    for item in history:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("user", ""), str)
            or not isinstance(item.get("assistant", ""), str)
            or len(item.get("user", "")) > 2000
            or len(item.get("assistant", "")) > 4000
        ):
            return JsonResponse(
                {"success": False, "message": "Conversation history is invalid.", "suggestions": []},
                status=400,
            )
        clean_history.append({
            "user": item.get("user", ""),
            "assistant": item.get("assistant", ""),
        })

    if payload.get("new_conversation") is True:
        request.session["chatbot_conversation_reference"] = str(uuid.uuid4())
    conversation_reference = request.session.get("chatbot_conversation_reference")
    if not conversation_reference:
        conversation_reference = str(uuid.uuid4())
        request.session["chatbot_conversation_reference"] = conversation_reference

    business_answer = _business_question_answer(message, language)
    if business_answer:
        _save_chatbot_turn(
            request, message, business_answer, language,
            consent=payload.get("conversation_consent") is True, history=clean_history,
        )
        return JsonResponse({
            "success": True,
            "message": business_answer,
            "suggestions": [],
            "conversation_reference": conversation_reference,
        })

    if _should_offer_inquiry_form(message):
        _save_chatbot_turn(
            request, message, "I'd be happy to help. I can guide you through a few questions, then show you a summary to review before anything is submitted.",
            language, consent=payload.get("conversation_consent") is True, history=clean_history,
        )
        return JsonResponse({
            "success": True,
            "message": "I'd be happy to help. I can guide you through a few questions, then show you a summary to review before anything is submitted.",
            "suggestions": [],
            "start_inquiry": True,
            "conversation_reference": conversation_reference,
        })

    result = generate_response(message, clean_history, language)

    if not result["success"]:
        return JsonResponse(result, status=503)

    _save_chatbot_turn(
        request, message, result["message"], language,
        consent=payload.get("conversation_consent") is True, history=clean_history,
    )
    result["conversation_reference"] = conversation_reference
    return JsonResponse(result)


def _business_question_answer(message, language):
    """Answer business-hours/location questions only from configured Google data."""
    normalized = message.casefold()
    intent_terms = (
        "open now", "currently open", "are you open", "working hours", "opening hours",
        "business hours", "holiday", "holidays", "sunday", "location", "address",
        "reach your office", "directions", "where are you",
        "હમણાં ખુલ્લું", "કામકાજના કલાક", "રવિવાર", "સરનામું", "ક્યાં",
        "अभी खुले", "काम के घंटे", "रविवार", "पता", "कहां",
    )
    if not any(term in normalized for term in intent_terms):
        return None

    locale = language
    if locale == "auto":
        locale = "gu" if any("\u0a80" <= char <= "\u0aff" for char in message) else (
            "hi" if any("\u0900" <= char <= "\u097f" for char in message) else "en"
        )
    from .services.google_business import get_business_info

    info = get_business_info()
    labels = {
        "en": {
            "unavailable": "I can't verify ORENTIQ's live business information from Google right now.",
            "open": "Current status: Open now.",
            "closed": "Current status: Closed now.",
            "status_unknown": "Current opening status is unavailable.",
            "hours": "Regular opening hours:",
            "hours_unknown": "Regular opening hours are unavailable.",
            "holiday_hours": "Verified special or holiday opening hours:",
            "holiday_unknown": "Verified special or holiday opening hours are unavailable.",
            "address": "Address:",
            "address_unknown": "Verified business address is unavailable.",
            "next": "Next change:",
            "time_zone": "Business timezone:",
        },
        "hi": {
            "unavailable": "मैं अभी Google से ORENTIQ की वर्तमान व्यावसायिक जानकारी सत्यापित नहीं कर सकता।",
            "open": "वर्तमान स्थिति: अभी खुला है।",
            "closed": "वर्तमान स्थिति: अभी बंद है।",
            "status_unknown": "अभी खुलने की स्थिति उपलब्ध नहीं है।",
            "hours": "नियमित कार्य समय:",
            "hours_unknown": "नियमित कार्य समय उपलब्ध नहीं है।",
            "holiday_hours": "सत्यापित विशेष या छुट्टी के कार्य समय:",
            "holiday_unknown": "सत्यापित विशेष या छुट्टी के समय उपलब्ध नहीं हैं।",
            "address": "पता:",
            "address_unknown": "सत्यापित व्यावसायिक पता उपलब्ध नहीं है।",
            "next": "अगला बदलाव:",
            "time_zone": "व्यावसायिक समय क्षेत्र:",
        },
        "gu": {
            "unavailable": "હું હાલમાં Google પરથી ORENTIQની વ્યવસાયિક માહિતી ચકાસી શકતો નથી.",
            "open": "હાલની સ્થિતિ: અત્યારે ખુલ્લું છે.",
            "closed": "હાલની સ્થિતિ: અત્યારે બંધ છે.",
            "status_unknown": "હાલનો ખુલવાનો દરજ્જો ઉપલબ્ધ નથી.",
            "hours": "નિયમિત કામકાજના કલાકો:",
            "hours_unknown": "નિયમિત કામકાજના કલાકો ઉપલબ્ધ નથી.",
            "holiday_hours": "ચકાસેલા ખાસ અથવા રજાના કામકાજના કલાકો:",
            "holiday_unknown": "ચકાસેલા ખાસ અથવા રજાના કલાકો ઉપલબ્ધ નથી.",
            "address": "સરનામું:",
            "address_unknown": "ચકાસેલું વ્યવસાયિક સરનામું ઉપલબ્ધ નથી.",
            "next": "આગળનો ફેરફાર:",
            "time_zone": "વ્યવસાયનો સમય ઝોન:",
        },
    }[locale]
    if not info["available"]:
        return labels["unavailable"]

    answers = []
    asks_location = any(term in normalized for term in (
        "location", "address", "reach your office", "directions", "where are you",
        "સરનામું", "ક્યાં", "पता", "कहां",
    ))
    asks_holiday = any(term in normalized for term in ("holiday", "holidays"))
    asks_hours = asks_holiday or any(term in normalized for term in (
        "working hours", "opening hours", "business hours", "sunday", "કામકાજના કલાક", "રવિવાર",
        "काम के घंटे", "रविवार",
    ))
    asks_status = any(term in normalized for term in ("open now", "currently open", "are you open", "હમણાં ખુલ્લું", "अभी खुले"))

    if asks_status or not (asks_location or asks_hours):
        answers.append(
            labels["open"] if info["status"] == "open" else
            labels["closed"] if info["status"] == "closed" else labels["status_unknown"]
        )
        if info.get("next_change"):
            answers.append(f"{labels['next']} {info['next_change']}")
    if asks_location:
        answers.append(f"{labels['address']} {info['address']}" if info.get("address") else labels["address_unknown"])
        if info.get("directions_url"):
            answers.append(info["directions_url"])
    if asks_hours:
        if info.get("time_zone"):
            answers.append(f"{labels['time_zone']} {info['time_zone']}")
        if asks_holiday:
            if info.get("special_hours"):
                answers.append(labels["holiday_hours"])
                answers.extend(info["special_hours"])
            else:
                answers.append(labels["holiday_unknown"])
        elif info.get("regular_hours"):
            descriptions = info["regular_hours"]
            if "sunday" in normalized or "રવિવાર" in normalized or "रविवार" in normalized:
                sunday_hours = [line for line in descriptions if line.casefold().startswith("sunday")]
                answers.extend(sunday_hours or [labels["hours_unknown"]])
            else:
                answers.append(labels["hours"])
                answers.extend(descriptions)
        else:
            answers.append(labels["hours_unknown"])
    return "\n".join(answers)


def _save_chatbot_turn(request, question, answer, language, consent=False, history=None):
    """Persist only bounded visitor/assistant text for admin review and support."""
    if not consent:
        return None
    reference = request.session.get("chatbot_conversation_reference")
    if not reference:
        reference = str(uuid.uuid4())
        request.session["chatbot_conversation_reference"] = reference
    conversation, created = ChatbotConversation.objects.get_or_create(
        reference=reference,
        defaults={"language": language},
    )
    transcript = conversation.transcript if isinstance(conversation.transcript, list) else []
    if created:
        for turn in (history or [])[-10:]:
            if turn.get("user"):
                transcript.append({"role": "user", "text": turn["user"][:2000]})
            if turn.get("assistant"):
                transcript.append({"role": "assistant", "text": turn["assistant"][:4000]})
    transcript.extend([
        {"role": "user", "text": question[:2000]},
        {"role": "assistant", "text": answer[:4000]},
    ])
    conversation.transcript = transcript[-60:]
    conversation.language = language
    normalized_question = " ".join(question.split())[:2000]
    conversation.last_question = normalized_question
    conversation.unanswered = any(
        phrase in answer.lower()
        for phrase in ("don't have verified", "not available", "could not find verified")
    )
    conversation.save(update_fields=[
        "transcript", "language", "last_question", "unanswered", "updated_at",
    ])
    if conversation.unanswered and conversation.unanswered_notification_status == "not_applicable":
        repeats = ChatbotConversation.objects.filter(
            last_question__iexact=normalized_question,
            unanswered=True,
            updated_at__gte=timezone.now() - timedelta(hours=24),
        ).count()
        if repeats >= 3:
            conversation.unanswered_notification_status = _management_notification(
                "Repeated unanswered chatbot question",
                f"The same question was unanswered in {repeats} consented conversations in the past 24 hours:\n\n{normalized_question}",
                f"unanswered question {conversation.reference}",
            )
            conversation.save(update_fields=["unanswered_notification_status", "updated_at"])
    return conversation


def _should_offer_inquiry_form(message):
    """Recognize clear project/contact intent without intercepting capability questions."""
    import re

    normalized = " ".join(message.lower().split())
    direct_intent = (
        r"\b(?:start|begin|discuss|submit)\s+(?:a\s+|my\s+|our\s+)?(?:project|project inquiry|inquiry)\b",
        r"\b(?:contact|reach out to)\s+(?:me|us|the team)\b",
        r"\b(?:talk|speak)\s+(?:to|with)\s+(?:someone|the team|a person)\b",
        r"\b(?:project inquiry|project enquiry)\b",
    )
    project_need = (
        r"\b(?:i|we)\s+(?:want|need|would like)\s+(?:to\s+)?"
        r"(?:(?:build|create|develop|launch)\s+)?"
        r"(?:a\s+|an\s+|my\s+|our\s+)?"
        r"(?:website|web site|mobile app|application|business dashboard|dashboard|"
        r"custom software|software|ai solution|automation|saas product|project)\b"
    )
    return any(re.search(pattern, normalized) for pattern in (*direct_intent, project_need))


@require_POST
def chatbot_inquiry_submit(request):
    """Validate and save a chatbot inquiry without changing the existing chat API contract."""
    from .ai.safety import is_inquiry_rate_limited

    content_length = request.META.get("CONTENT_LENGTH")
    if content_length and content_length.isdigit() and int(content_length) > 55 * 1024 * 1024:
        return JsonResponse(
            {"success": False, "message": "The inquiry form exceeds the 55 MB upload limit."},
            status=413,
        )

    if is_inquiry_rate_limited(request, cache):
        return JsonResponse(
            {"success": False, "message": "Too many inquiry submissions. Please wait and try again."},
            status=429,
        )

    form = ChatbotInquiryForm(request.POST)
    if not form.is_valid():
        return JsonResponse(
            {
                "success": False,
                "message": "Please check the highlighted fields and try again.",
                "errors": form.errors.get_json_data(),
            },
            status=400,
        )

    data = form.cleaned_data
    uploaded_files = request.FILES.getlist("attachments")
    if len(uploaded_files) > 5:
        return JsonResponse(
            {"success": False, "message": "Attach no more than five files."},
            status=400,
        )
    for uploaded in uploaded_files:
        try:
            validate_chatbot_attachment(uploaded)
        except ValidationError as exc:
            return JsonResponse(
                {"success": False, "message": "; ".join(exc.messages)},
                status=400,
            )
    submission_id = data["submission_id"]
    defaults = {
        "name": data["name"],
        "email": data["email"],
        "phone": data["phone"],
        "company": data["company"],
        "service": data["inquiry_type"],
        "inquiry_type": data["inquiry_type"],
        "title": data["title"],
        "budget": data["budget"],
        "timeline": data["timeline"],
        "contact_method": data["contact_method"],
        "message": data["description"],
        "source": "chatbot",
        "submission_id": submission_id,
        "conversation_reference": data["conversation_reference"],
        "conversation_transcript": data["conversation_transcript"],
        "consented_at": timezone.now(),
    }

    with transaction.atomic():
        inquiry, created = ContactInquiry.objects.get_or_create(
            submission_id=submission_id,
            defaults=defaults,
        )
        if created:
            if data["conversation_reference"] and data["conversation_transcript"]:
                ChatbotConversation.objects.get_or_create(
                    reference=data["conversation_reference"],
                    defaults={
                        "transcript": data["conversation_transcript"],
                        "language": request.POST.get("language", "auto")[:8],
                    },
                )
            for uploaded in uploaded_files:
                InquiryAttachment.objects.create(
                    inquiry=inquiry,
                    file=uploaded,
                    original_name=uploaded.name[:255],
                    content_type=uploaded.content_type or "application/octet-stream",
                    size=uploaded.size,
                )

    if not created and any(
        getattr(inquiry, field) != defaults[field]
        for field in (
            "name",
            "email",
            "phone",
            "company",
            "service",
            "inquiry_type",
            "title",
            "budget",
            "timeline",
            "contact_method",
            "message",
            "conversation_reference",
            "conversation_transcript",
        )
    ):
        return JsonResponse(
            {"success": False, "message": "This submission reference was already used. Refresh the form and try again."},
            status=409,
        )

    if created:
        inquiry.notification_status = _send_inquiry_notifications(inquiry)
        inquiry.save(update_fields=["notification_status", "updated_at"])

    return JsonResponse({
        "success": True,
        "message": "Thank you. Your inquiry has been received.",
        "reference": inquiry.reference,
    }, status=201 if created else 200)


def _send_inquiry_notifications(inquiry):
    """Send optional confirmation and business notifications after inquiry persistence."""
    if not (
        settings.EMAIL_HOST
        and settings.EMAIL_HOST_USER
        and settings.EMAIL_HOST_PASSWORD
        and settings.DEFAULT_FROM_EMAIL
    ):
        logger.info("Inquiry notification not configured for %s.", inquiry.reference)
        return "not_configured"

    try:
        send_mail(
            f"ORENTIQ received your inquiry — {inquiry.reference}",
            (
                f"Hello {inquiry.name},\n\n"
                f"Thank you for contacting ORENTIQ about {inquiry.title}. "
                f"Your inquiry reference is {inquiry.reference}. Our team will review it and follow up.\n"
            ),
            settings.DEFAULT_FROM_EMAIL,
            [inquiry.email],
            fail_silently=False,
        )
    except (BadHeaderError, OSError, smtplib.SMTPException, ValidationError):
        logger.exception("Inquiry confirmation email failed for %s.", inquiry.reference)

    notification_email = getattr(settings, "INQUIRY_NOTIFICATION_EMAIL", "")
    if not notification_email:
        logger.info("Inquiry administrator email not configured for %s.", inquiry.reference)
        return "not_configured"
    try:
        send_mail(
            f"New chatbot inquiry — {inquiry.reference}",
            (
                f"Reference: {inquiry.reference}\nName: {inquiry.name}\n"
                f"Email: {inquiry.email}\nType: {inquiry.get_inquiry_type_display()}\n"
                f"Title: {inquiry.title}\n\n{inquiry.message}"
            ),
            settings.DEFAULT_FROM_EMAIL,
            [notification_email],
            fail_silently=False,
        )
    except (BadHeaderError, OSError, smtplib.SMTPException, ValidationError):
        logger.exception("Inquiry administrator notification failed for %s.", inquiry.reference)
        return "failed"
    return "sent"


@require_GET
def chatbot_business_info(request):
    """Return configured public Places information without exposing credentials."""
    from .services.google_business import get_business_info

    return JsonResponse(get_business_info())


def _management_notification(subject, body, reference):
    """Notify configured administrators and report delivery state for the admin UI."""
    recipient = getattr(settings, "INQUIRY_NOTIFICATION_EMAIL", "")
    if not (
        recipient
        and settings.EMAIL_HOST
        and settings.EMAIL_HOST_USER
        and settings.EMAIL_HOST_PASSWORD
        and settings.DEFAULT_FROM_EMAIL
    ):
        logger.info("Chatbot notification is not configured for %s.", reference)
        return "not_configured"
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)
    except (BadHeaderError, OSError, smtplib.SMTPException, ValidationError):
        logger.exception("Chatbot notification failed for %s.", reference)
        return "failed"
    return "sent"


def _chatbot_rate_limited(request, action, limit=5, window=3600):
    ip_address = request.META.get("REMOTE_ADDR", "unknown")
    key = f"chatbot:{action}:{ip_address}"
    attempts = cache.get(key, 0)
    if attempts >= limit:
        return True
    cache.set(key, attempts + 1, window)
    return False


def _session_conversation(request, reference):
    if not reference:
        return None
    try:
        parsed_reference = uuid.UUID(reference)
    except (ValueError, TypeError, AttributeError):
        return None
    session_reference = request.session.get("chatbot_conversation_reference")
    if not session_reference:
        return None
    try:
        session_uuid = uuid.UUID(session_reference)
    except (ValueError, TypeError, AttributeError):
        return None
    if parsed_reference != session_uuid:
        return None
    return ChatbotConversation.objects.filter(reference=session_uuid).first()


@require_POST
def chatbot_consultation_availability(request):
    """Check whether the requested local date/time is already reserved."""
    if _chatbot_rate_limited(request, "consultation-availability", limit=20):
        return JsonResponse({"success": False, "message": "Please wait before checking another time."}, status=429)
    form = ConsultationRequestForm(request.POST)
    if not form.is_valid():
        timezone_error = any(
            "timezone" in str(error).lower()
            for error in form.errors.get("preferred_date", [])
        )
        return JsonResponse({
            "success": False,
            "message": (
                "Consultation scheduling is unavailable until the business timezone is configured."
                if timezone_error else "Please check your consultation details."
            ),
            "errors": form.errors.get_json_data(),
        }, status=400)
    data = form.cleaned_data
    busy = ConsultationRequest.objects.filter(
        preferred_date=data["preferred_date"],
        preferred_time=data["preferred_time"],
        status__in=["requested", "confirmed"],
    ).exists()
    return JsonResponse({
        "success": True,
        "available": not busy,
        "message": "This time is already requested." if busy else "No existing request conflicts with this time.",
    })


@require_POST
def chatbot_consultation_submit(request):
    """Save a consented, availability-checked consultation request as unconfirmed."""
    content_length = request.META.get("CONTENT_LENGTH", "")
    if content_length.isdigit() and int(content_length) > 16000:
        return JsonResponse({"success": False, "message": "The consultation request is too large."}, status=413)
    if _chatbot_rate_limited(request, "consultation", limit=3, window=3600):
        return JsonResponse({"success": False, "message": "Too many consultation requests. Please try again later."}, status=429)
    form = ConsultationRequestForm(request.POST)
    if not form.is_valid():
        return JsonResponse({
            "success": False,
            "message": "Please check your consultation details.",
            "errors": form.errors.get_json_data(),
        }, status=400)
    data = form.cleaned_data
    if ConsultationRequest.objects.filter(
        preferred_date=data["preferred_date"],
        preferred_time=data["preferred_time"],
        status__in=["requested", "confirmed"],
    ).exists():
        return JsonResponse({
            "success": False,
            "message": "That time already has a request. Please choose another time.",
        }, status=409)

    consultation = form.save(commit=False)
    consultation.consented_at = timezone.now()
    from .services.google_business import get_configured_business_time_zone

    consultation.business_time_zone = get_configured_business_time_zone()
    if not request.session.get("chatbot_conversation_reference") and data.get("conversation_reference"):
        request.session["chatbot_conversation_reference"] = str(data["conversation_reference"])
    consultation.conversation = _session_conversation(request, request.POST.get("conversation_reference", ""))
    consultation.conversation_reference = (
        consultation.conversation.reference
        if consultation.conversation
        else data.get("conversation_reference")
    )
    try:
        with transaction.atomic():
            consultation.save()
    except IntegrityError:
        return JsonResponse({
            "success": False,
            "message": "That time was just requested. Please choose another time.",
        }, status=409)

    consultation.notification_status = _management_notification(
        f"New consultation request — {consultation.pk}",
        (
            f"Name: {consultation.name}\nEmail: {consultation.email}\nPhone: {consultation.phone}\n"
            f"Preferred time: {consultation.preferred_date} {consultation.preferred_time} "
            f"{consultation.business_time_zone or '(timezone not configured)'}\n"
            f"Project type: {consultation.project_type}\n\n{consultation.description}"
        ),
        f"consultation {consultation.pk}",
    )
    consultation.save(update_fields=["notification_status"])
    return JsonResponse({
        "success": True,
        "status": consultation.status,
        "message": "Your request was saved. It is not a confirmed appointment; the team will verify the time and follow up.",
    }, status=201)


@require_POST
def chatbot_support_submit(request):
    """Save a consented request for human follow-up without claiming live availability."""
    content_length = request.META.get("CONTENT_LENGTH", "")
    if content_length.isdigit() and int(content_length) > 12000:
        return JsonResponse({"success": False, "message": "The support request is too large."}, status=413)
    if _chatbot_rate_limited(request, "support", limit=3, window=3600):
        return JsonResponse({"success": False, "message": "Too many support requests. Please try again later."}, status=429)
    form = HumanSupportRequestForm(request.POST)
    if not form.is_valid():
        return JsonResponse({
            "success": False,
            "message": "Please check your contact details and consent.",
            "errors": form.errors.get_json_data(),
        }, status=400)

    support_request = form.save(commit=False)
    support_request.consented_at = timezone.now()
    if (
        not request.session.get("chatbot_conversation_reference")
        and form.cleaned_data.get("conversation_reference")
    ):
        request.session["chatbot_conversation_reference"] = str(
            form.cleaned_data["conversation_reference"]
        )
    support_request.conversation = _session_conversation(
        request, request.POST.get("conversation_reference", ""),
    )
    support_request.conversation_reference = (
        support_request.conversation.reference
        if support_request.conversation
        else form.cleaned_data.get("conversation_reference")
    )
    support_request.save()
    support_request.notification_status = _management_notification(
        f"New ORENTIQ support request — {support_request.pk}",
        (
            f"Name: {support_request.name}\nEmail: {support_request.email}\n"
            f"Phone: {support_request.phone or 'Not provided'}\n"
            f"Conversation: {support_request.conversation_reference or 'Not provided'}"
        ),
        f"support request {support_request.pk}",
    )
    support_request.save(update_fields=["notification_status"])
    return JsonResponse({
        "success": True,
        "message": "Your request has been sent to the team. No agent is represented as currently online.",
    }, status=201)


@require_POST
def chatbot_delete_visitor_data(request):
    """Delete the current session's chatbot transcript, inquiry, support, and files."""
    reference = request.session.get("chatbot_conversation_reference")
    if not reference:
        return JsonResponse({"success": True, "message": "No saved chatbot data was found."})
    try:
        parsed_reference = uuid.UUID(reference)
    except (ValueError, TypeError, AttributeError):
        request.session.pop("chatbot_conversation_reference", None)
        return JsonResponse({"success": False, "message": "Saved chatbot data could not be verified."}, status=400)
    if _chatbot_rate_limited(request, "delete-data", limit=3, window=3600):
        return JsonResponse({"success": False, "message": "Please wait before retrying data deletion."}, status=429)

    with transaction.atomic():
        ContactInquiry.objects.filter(
            source="chatbot",
            conversation_reference=parsed_reference,
        ).delete()
        ConsultationRequest.objects.filter(conversation_reference=parsed_reference).delete()
        HumanSupportRequest.objects.filter(conversation_reference=parsed_reference).delete()
        ChatbotConversation.objects.filter(reference=parsed_reference).delete()
    request.session.pop("chatbot_conversation_reference", None)
    return JsonResponse({
        "success": True,
        "message": "Saved chatbot conversation data and linked chatbot inquiries were deleted.",
    })


@login_required
def chatbot_attachment_download(request, pk):
    """Serve visitor-uploaded references only to authorized internal admins."""
    from .permissions import require_admin

    require_admin(request.user)
    attachment = get_object_or_404(InquiryAttachment, pk=pk)
    if not attachment.file:
        raise Http404("The attachment is unavailable.")
    response = FileResponse(
        attachment.file.open("rb"),
        as_attachment=True,
        filename=attachment.original_name,
        content_type="application/octet-stream",
    )
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response
