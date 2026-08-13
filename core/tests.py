import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse

from .models import (
    ActivityLog,
    Booking,
    BookingItem,
    BookingStatus,
    BookingType,
    ContactInquiry,
    Industry,
    PortfolioProject,
    Product,
    Profile,
    Service,
    Technology,
    Testimonial,
    Traveler,
    UserRole,
)


class OrientiqTestCase(TestCase):
    """Base test case with helper methods."""

    def setUp(self):
        self.client = Client(HTTP_HOST="127.0.0.1")

        self.superadmin_user = User.objects.create_superuser(
            username="superadmin", email="super@orientiq.com", password="AdminPass123!"
        )
        Profile.objects.create(user=self.superadmin_user, role=UserRole.SUPER_ADMIN)

        self.admin_user = User.objects.create_user(
            username="testadmin", email="admin@orientiq.com", password="AdminPass123!"
        )
        Profile.objects.create(user=self.admin_user, role=UserRole.ADMIN)

        self.client_user = User.objects.create_user(
            username="testclient", email="client@orientiq.com", password="ClientPass123!"
        )
        Profile.objects.create(user=self.client_user, role=UserRole.CLIENT)

    def login_as(self, username, password="AdminPass123!"):
        return self.client.login(username=username, password=password)

    def create_sample_data(self):
        service = Service.objects.create(title="Test Service", slug="test-service", status="published")
        industry = Industry.objects.create(name="Test Industry", slug="test-industry", status="published")
        portfolio = PortfolioProject.objects.create(title="Test Project", slug="test-project", status="published")
        product = Product.objects.create(name="Test Product", slug="test-product", product_status="coming_soon")
        tech = Technology.objects.create(name="Python", category="backend", active=True)
        testimonial = Testimonial.objects.create(client_name="Test Client", testimonial="Great work!")
        return service, industry, portfolio, product, tech, testimonial


class AuthenticationTests(OrientiqTestCase):
    def _register_user(self, username, email, password="StrongPass123!"):
        self.client.post(
            "/accounts/register/",
            {
                "first_name": "Test", "last_name": "User", "email": email,
                "username": username, "password1": password,
                "password2": password, "phone": "", "company": "", "country": "",
            },
        )

    def test_register(self):
        self._register_user("newuser", "new@test.com")
        self.assertTrue(User.objects.filter(username="newuser").exists())
        # Verify register redirects (logged in) to profile
        resp = self.client.get("/accounts/profile/")
        self.assertEqual(resp.status_code, 200)

    def test_login_with_username(self):
        """Login with a valid username should succeed."""
        self._register_user("logintest", "login@test.com", "StrongPass123!")
        self.client.logout()
        resp = self.client.post(
            "/accounts/login/",
            {"username": "logintest", "password": "StrongPass123!"},
        )
        self.assertEqual(resp.status_code, 302)

    def test_login_with_email(self):
        """Login with a valid email should succeed."""
        self._register_user("emailuser", "email@test.com", "StrongPass123!")
        self.client.logout()
        resp = self.client.post(
            "/accounts/login/",
            {"username": "email@test.com", "password": "StrongPass123!"},
        )
        self.assertEqual(resp.status_code, 302)

    def test_login_with_email_case_insensitive(self):
        """Login with email should be case-insensitive."""
        self._register_user("caseuser", "case@test.com", "StrongPass123!")
        self.client.logout()
        resp = self.client.post(
            "/accounts/login/",
            {"username": "CASE@TEST.COM", "password": "StrongPass123!"},
        )
        self.assertEqual(resp.status_code, 302)

    def test_login_with_incorrect_password(self):
        """Login with wrong password should fail with the same form error."""
        self._register_user("wrongpass", "wrong@test.com", "StrongPass123!")
        self.client.logout()
        resp = self.client.post(
            "/accounts/login/",
            {"username": "wrongpass", "password": "WrongPassword!"},
        )
        self.assertEqual(resp.status_code, 200)  # form shows error

    def test_login_with_nonexistent_username(self):
        """Login with a non-existent username should fail (not leak user existence)."""
        self.client.logout()
        resp = self.client.post(
            "/accounts/login/",
            {"username": "doesnotexist", "password": "WhateverPass1!"},
        )
        self.assertEqual(resp.status_code, 200)

    def test_login_with_nonexistent_email(self):
        """Login with a non-existent email should fail (not leak user existence)."""
        self.client.logout()
        resp = self.client.post(
            "/accounts/login/",
            {"username": "nobody@example.com", "password": "WhateverPass1!"},
        )
        self.assertEqual(resp.status_code, 200)

    def test_login_admin_with_email_allows_dashboard(self):
        """An ADMIN logging in via email should still reach the admin dashboard."""
        self.login_as("testadmin")  # verifies custom backend with username
        self.client.logout()
        resp = self.client.post(
            "/accounts/login/",
            {"username": "admin@orientiq.com", "password": "AdminPass123!"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/admin/", resp["Location"])

    def test_duplicate_registration(self):
        self.client.post(
            "/accounts/register/",
            {
                "first_name": "New", "last_name": "User", "email": "dup@test.com",
                "username": "dupuser", "password1": "StrongPass123!",
                "password2": "StrongPass123!", "phone": "", "company": "", "country": "",
            },
        )
# Registration logs the user in; log out so the duplicate attempt is
        # evaluated as an anonymous visitor (testing email uniqueness).
        self.client.logout()
        resp = self.client.post(
            "/accounts/register/",
            {
                "first_name": "New", "last_name": "User", "email": "dup@test.com",
                "username": "dupuser2", "password1": "StrongPass123!",
                "password2": "StrongPass123!", "phone": "", "company": "", "country": "",
            },
        )
        self.assertEqual(resp.status_code, 200)  # form error shown

    def test_valid_login(self):
        resp = self.client.post("/accounts/login/", {"username": "testadmin", "password": "AdminPass123!"})
        self.assertEqual(resp.status_code, 302)

    def test_invalid_login(self):
        resp = self.client.post("/accounts/login/", {"username": "testadmin", "password": "Wrong!"})
        self.assertEqual(resp.status_code, 200)  # form error shown

    def test_logout(self):
        self.login_as("testadmin")
        resp = self.client.get("/accounts/logout/")
        self.assertEqual(resp.status_code, 302)


class PermissionTests(OrientiqTestCase):
    def test_anonymous_redirected_to_admin_login(self):
        resp = self.client.get("/admin/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/admin/login/", resp["Location"])

    def test_client_forbidden_from_admin(self):
        self.login_as("testclient", "ClientPass123!")
        resp = self.client.get("/admin/")
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_access_dashboard(self):
        self.login_as("testadmin")
        resp = self.client.get("/admin/")
        self.assertEqual(resp.status_code, 200)

    def test_superadmin_can_access_all(self):
        self.login_as("superadmin")
        for route in ["/admin/", "/admin/settings/", "/admin/activity/"]:
            resp = self.client.get(route)
            self.assertEqual(resp.status_code, 200, f"Failed on {route}")

    def test_admin_cannot_access_settings(self):
        self.login_as("testadmin")
        resp = self.client.get("/admin/settings/")
        self.assertEqual(resp.status_code, 403)


class AdminCRUDTests(OrientiqTestCase):
    def setUp(self):
        super().setUp()
        self.login_as("testadmin")

    def test_service_create(self):
        resp = self.client.post(
            "/admin/services/create/",
            {"title": "AI Automation", "slug": "ai-automation", "status": "published"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Service.objects.filter(slug="ai-automation").exists())

    def test_service_edit(self):
        service = Service.objects.create(title="Test", slug="test-service")
        resp = self.client.post(
            f"/admin/services/{service.id}/edit/",
            {"title": "Updated", "slug": "test-service", "status": "published"},
        )
        self.assertEqual(resp.status_code, 302)
        service.refresh_from_db()
        self.assertEqual(service.title, "Updated")

    def test_service_delete(self):
        service = Service.objects.create(title="Delete Me", slug="delete-me")
        resp = self.client.get(f"/admin/services/{service.id}/delete/")
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Service.objects.filter(id=service.id).exists())

    def test_industry_crud(self):
        resp = self.client.post(
            "/admin/industries/create/",
            {"name": "Real Estate", "slug": "real-estate", "status": "published"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Industry.objects.filter(slug="real-estate").exists())

    def test_product_crud(self):
        resp = self.client.post(
            "/admin/products/create/",
            {"name": "AI Travel", "slug": "ai-travel", "product_status": "coming_soon", "status": "published"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Product.objects.filter(slug="ai-travel").exists())

    def test_technology_crud(self):
        resp = self.client.post(
            "/admin/technologies/create/",
            {"name": "Django", "category": "backend", "active": "on"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Technology.objects.filter(name="Django").exists())

    def test_testimonial_crud(self):
        resp = self.client.post(
            "/admin/testimonials/create/",
            {"client_name": "ACME", "testimonial": "Excellent!", "rating": "5", "status": "published"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Testimonial.objects.filter(client_name="ACME").exists())


class InquiryTests(OrientiqTestCase):
    def test_inquiry_creation_from_public_form(self):
        resp = self.client.post(
            "/start-project/",
            {
                "name": "John Doe", "email": "john@test.com", "phone": "123",
                "company": "ACME", "project_type": "Web Development",
                "budget": "$10k-$25k", "message": "Hello",
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(ContactInquiry.objects.filter(email="john@test.com").exists())

    def test_inquiry_requires_name_and_email(self):
        resp = self.client.post("/start-project/", {"name": "", "email": ""})
        self.assertEqual(resp.status_code, 200)  # error message shown
        self.assertEqual(ContactInquiry.objects.count(), 0)


class PublicRouteTests(OrientiqTestCase):
    def test_all_public_routes(self):
        routes = [
            "/", "/about/", "/services/", "/services/ai-automation/",
            "/industries/", "/industries/real-estate/", "/portfolio/",
            "/products/", "/products/ai-travel/", "/technologies/",
            "/company/", "/company/about/", "/start-project/",
            "/design-system/", "/accounts/login/", "/accounts/register/",
        ]
        for route in routes:
            resp = self.client.get(route)
            self.assertEqual(resp.status_code, 200, f"Failed on {route}")

    def test_404_for_invalid_product(self):
        resp = self.client.get("/products/invalid-slug/")
        self.assertEqual(resp.status_code, 404)


class PasswordResetTests(OrientiqTestCase):
    """Complete forgot-password → reset → login flow."""

    def test_forgot_password_flow(self):
        """Forgot password should generate a reset email without crashing."""
        resp = self.client.post(
            "/accounts/forgot-password/",
            {"email": "admin@orientiq.com"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/reset-password/", resp["Location"])

    def test_forgot_password_unknown_email(self):
        """Unknown email should not leak user existence (still redirects)."""
        resp = self.client.post(
            "/accounts/forgot-password/",
            {"email": "nobody@example.com"},
        )
        self.assertEqual(resp.status_code, 302)

    def test_reset_confirm_page(self):
        """The reset confirm page should render for a valid token."""
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        uid = urlsafe_base64_encode(force_bytes(self.admin_user.pk))
        token = default_token_generator.make_token(self.admin_user)

        # Django 5.0 validates the token and redirects to the set-password step.
        resp = self.client.get(f"/accounts/reset-password/{uid}/{token}/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/set-password/", resp["Location"])

        # Follow the redirect to the set-password form.
        resp = self.client.get(resp["Location"])
        self.assertEqual(resp.status_code, 200)

    def test_reset_password_and_login(self):
        """Complete flow: reset password via token, then login with new password."""
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        uid = urlsafe_base64_encode(force_bytes(self.admin_user.pk))
        token = default_token_generator.make_token(self.admin_user)

        # Step 1: GET the reset URL → redirects to set-password.
        resp = self.client.get(f"/accounts/reset-password/{uid}/{token}/")
        self.assertEqual(resp.status_code, 302)
        set_password_url = resp["Location"]

        # Step 2: GET the set-password form.
        resp = self.client.get(set_password_url)
        self.assertEqual(resp.status_code, 200)

        # Step 3: POST the new password.
        resp = self.client.post(
            set_password_url,
            {"new_password1": "NewPass456!", "new_password2": "NewPass456!"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/reset-password/complete/", resp["Location"])

        # Step 4: Login with the new password.
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.check_password("NewPass456!"))

        resp = self.client.post(
            "/accounts/login/",
            {"username": "admin@orientiq.com", "password": "NewPass456!"},
        )
        self.assertEqual(resp.status_code, 302)


class AIAssistantTests(OrientiqTestCase):
    """Tests for the AI assistant endpoint and knowledge layer."""

    def test_ai_endpoint_rejects_get(self):
        """GET to the AI endpoint should be rejected (POST-only)."""
        resp = self.client.get("/api/ai/chat/")
        self.assertEqual(resp.status_code, 405)

    def test_ai_endpoint_empty_message(self):
        """Empty message should be rejected with 400."""
        resp = self.client.post(
            "/api/ai/chat/",
            data='{"message": ""}',
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_ai_endpoint_very_long_message(self):
        """Very long message should be rejected with 400."""
        long_msg = "a" * 5000
        resp = self.client.post(
            "/api/ai/chat/",
            data='{"message": "%s"}' % long_msg,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_ai_endpoint_valid_request(self):
        """Valid request should return a knowledge-based response."""
        resp = self.client.post(
            "/api/ai/chat/",
            data='{"message": "What services do you provide?"}',
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["message"])
        self.assertIn("Orientiq", data["message"])

    def test_ai_endpoint_start_project_suggestion(self):
        """Project-related questions should include Start a Project suggestion."""
        resp = self.client.post(
            "/api/ai/chat/",
            data='{"message": "I want to build a platform."}',
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        urls = [s["url"] for s in data["suggestions"]]
        self.assertIn("/start-project/", urls)

    def test_ai_endpoint_no_api_key_exposed(self):
        """The API key must never be exposed in the response."""
        resp = self.client.post(
            "/api/ai/chat/",
            data='{"message": "What does Orientiq do?"}',
            content_type="application/json",
        )
        body = resp.content.decode("utf-8")
        self.assertNotIn("AI_API_KEY", body)
        self.assertNotIn("sk-", body)

    def test_knowledge_contains_published_services(self):
        """The knowledge layer should include company services."""
        from .ai.knowledge import build_company_context
        context = build_company_context()
        self.assertTrue(context["services"])
        self.assertTrue(context["company"]["name"] == "Orientiq")

    def test_knowledge_does_not_include_private_data(self):
        """Knowledge context must not include admin notes, passwords, or inquiries."""
        from .ai.knowledge import build_company_context
        context = build_company_context()
        text = str(context)
        self.assertNotIn("admin_notes", text)
        self.assertNotIn("password", text)
        self.assertNotIn("admin_notes", text)

    def test_assistant_available_to_anonymous(self):
        """Anonymous visitors can access the assistant endpoint."""
        resp = self.client.post(
            "/api/ai/chat/",
            data='{"message": "Hello"}',
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

    def test_assistant_available_to_authenticated(self):
        """Authenticated users (CLIENT, ADMIN, SUPER_ADMIN) can access the assistant."""
        self.login_as("testclient", "ClientPass123!")
        resp = self.client.post(
            "/api/ai/chat/",
            data='{"message": "Hello"}',
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

    def test_assistant_available_to_admin(self):
        self.login_as("testadmin")
        resp = self.client.post(
            "/api/ai/chat/",
            data='{"message": "Hello"}',
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

    def test_assistant_available_to_superadmin(self):
        self.login_as("superadmin")
        resp = self.client.post(
            "/api/ai/chat/",
            data='{"message": "Hello"}',
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)


class LiveIntelligenceTests(OrientiqTestCase):
    """Tests for the Phase 7 live intelligence foundation."""

    def setUp(self):
        super().setUp()
        # Mock the location provider so tests never make real network calls.
        # The mock raises LocationError, which forces the built-in fallback
        # set to be used — deterministic and fast.
        from unittest.mock import patch
        from .services.location_service import LocationError

        class MockProvider:
            def search(self, query, limit=5):
                raise LocationError("Geocoding provider unavailable")

        self._provider_patch = patch(
            "core.services.location_service.get_location_provider",
            return_value=MockProvider(),
        )
        self._provider_patch.start()

    def tearDown(self):
        self._provider_patch.stop()
        super().tearDown()

    def test_location_search_valid(self):
        """Valid location search should return results."""
        from .services.location_service import search_locations
        result = search_locations("dubai")
        self.assertTrue(result["success"])
        self.assertTrue(result["results"])
        self.assertEqual(result["results"][0]["name"], "Dubai")

    def test_location_search_arbitrary_city(self):
        """Bhopal should be searchable."""
        from .services.location_service import search_locations
        result = search_locations("Bhopal")
        self.assertTrue(result["success"])
        self.assertTrue(result["results"])

    def test_location_search_state(self):
        """Gujarat (state) should be searchable."""
        from .services.location_service import search_locations
        result = search_locations("Gujarat")
        self.assertTrue(result["success"])
        self.assertTrue(result["results"])

    def test_location_search_country(self):
        """India (country) should be searchable."""
        from .services.location_service import search_locations
        result = search_locations("India")
        self.assertTrue(result["success"])
        self.assertTrue(result["results"])

    def test_location_search_landmark(self):
        """Eiffel Tower (landmark) should be searchable."""
        from .services.location_service import search_locations
        result = search_locations("Eiffel Tower")
        self.assertTrue(result["success"])
        self.assertTrue(result["results"])

    def test_location_search_case_insensitive(self):
        """Search should be case-insensitive."""
        from .services.location_service import search_locations
        result = search_locations("BHO")
        self.assertTrue(result["success"])
        self.assertTrue(result["results"])

    def test_location_search_unknown(self):
        """Unknown location should return empty results (no matches)."""
        from .services.location_service import search_locations
        result = search_locations("atlantis")
        self.assertTrue(result["success"])
        self.assertEqual(result["results"], [])

    def test_location_search_ws_only(self):
        """Whitespace-only query should fail gracefully."""
        from .services.location_service import search_locations
        result = search_locations("   ")
        self.assertFalse(result["success"])

    def test_location_search_very_long(self):
        """Very long query should fail gracefully."""
        from .services.location_service import search_locations
        result = search_locations("x" * 500)
        self.assertFalse(result["success"])

    def test_location_search_empty(self):
        """Empty location query should fail gracefully."""
        from .services.location_service import search_locations
        result = search_locations("")
        self.assertFalse(result["success"])

    def test_weather_valid(self):
        """Valid location should return normalized weather."""
        from .services.location_service import get_location_by_name
        from .services.weather_service import get_current_weather
        loc = get_location_by_name("dubai")
        result = get_current_weather(loc)
        self.assertTrue(result["success"])
        self.assertIn("temperature", result["data"])
        self.assertIn("condition", result["data"])

    def test_weather_invalid_location(self):
        """Weather for an invalid location should fail gracefully."""
        from .services.weather_service import get_current_weather
        result = get_current_weather(None)
        self.assertFalse(result["success"])

    def test_maps_valid(self):
        """Valid coordinates should return map data."""
        from .services.location_service import get_location_by_name
        from .services.maps_service import get_map
        loc = get_location_by_name("london")
        result = get_map(loc)
        self.assertTrue(result["success"])
        self.assertIn("embed_url", result["data"])

    def test_maps_invalid_coordinates(self):
        """Invalid coordinates should fail gracefully."""
        from .services.maps_service import get_map
        result = get_map({"latitude": 999, "longitude": 999})
        self.assertFalse(result["success"])

    def test_live_intelligence_success(self):
        """Combined live intelligence should return location + weather + map."""
        from .services.live_intelligence import get_destination_intelligence
        result = get_destination_intelligence("dubai")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["status"], "success")
        self.assertIn("location", result["data"])
        self.assertIn("weather", result["data"])
        self.assertIn("map", result["data"])

    def test_live_intelligence_unknown_destination(self):
        """Unknown destination should fail gracefully."""
        from .services.live_intelligence import get_destination_intelligence
        result = get_destination_intelligence("atlantis")
        self.assertFalse(result["success"])

    def test_live_intelligence_empty(self):
        """Empty destination should fail gracefully."""
        from .services.live_intelligence import get_destination_intelligence
        result = get_destination_intelligence("")
        self.assertFalse(result["success"])

    def test_api_location_search(self):
        """GET /api/location/search/ should return JSON."""
        resp = self.client.get("/api/location/search/", {"q": "dubai"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["results"])

    def test_api_location_search_unknown(self):
        """Unknown location should return 404 with a friendly error."""
        resp = self.client.get("/api/location/search/", {"q": "atlantis"})
        self.assertEqual(resp.status_code, 404)
        data = resp.json()
        self.assertFalse(data["success"])
        self.assertIn("not found", data["error"].lower())

    def test_api_location_search_missing_query(self):
        """Missing query should return 400."""
        resp = self.client.get("/api/location/search/")
        self.assertEqual(resp.status_code, 400)

    def test_api_weather(self):
        """GET /api/weather/ should return normalized weather."""
        resp = self.client.get("/api/weather/", {"q": "dubai"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertIn("temperature", data["data"])

    def test_api_live_intelligence(self):
        """GET /api/live-intelligence/ should return combined data."""
        resp = self.client.get("/api/live-intelligence/", {"q": "dubai"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["status"], "success")

    def test_api_live_intelligence_missing_query(self):
        """Missing query should return 400."""
        resp = self.client.get("/api/live-intelligence/")
        self.assertEqual(resp.status_code, 400)

    def test_no_api_keys_exposed(self):
        """API responses must never expose API keys."""
        resp = self.client.get("/api/live-intelligence/", {"q": "dubai"})
        body = resp.content.decode("utf-8")
        self.assertNotIn("MAPS_API_KEY", body)
        self.assertNotIn("WEATHER_API_KEY", body)
        self.assertNotIn("sk-", body)

    def test_live_intelligence_page(self):
        """The /live-intelligence/ demo page should render."""
        resp = self.client.get("/live-intelligence/")
        self.assertEqual(resp.status_code, 200)


class TravelInventoryTests(OrientiqTestCase):
    """Tests for the Phase 8 travel inventory foundation."""

    def test_flights_valid_search(self):
        """Valid flight search should return demo results."""
        from .services.travel.flights import search_flights
        result = search_flights({
            "origin": "Ahmedabad", "destination": "Dubai",
            "departure": "2026-09-10", "adults": 1,
        })
        self.assertTrue(result["success"])
        self.assertTrue(result["results"])
        self.assertTrue(result["demo"])

    def test_flights_missing_origin(self):
        """Missing origin should fail gracefully."""
        from .services.travel.flights import search_flights
        result = search_flights({"destination": "Dubai", "departure": "2026-09-10"})
        self.assertFalse(result["success"])

    def test_flights_missing_dates(self):
        """Missing departure date should fail gracefully."""
        from .services.travel.flights import search_flights
        result = search_flights({"origin": "Ahmedabad", "destination": "Dubai"})
        self.assertFalse(result["success"])

    def test_flights_invalid_date(self):
        """Invalid date should fail gracefully."""
        from .services.travel.flights import search_flights
        result = search_flights({
            "origin": "Ahmedabad", "destination": "Dubai",
            "departure": "not-a-date",
        })
        self.assertFalse(result["success"])

    def test_flights_invalid_passenger_count(self):
        """Invalid passenger count should fail gracefully."""
        from .services.travel.flights import search_flights
        result = search_flights({
            "origin": "Ahmedabad", "destination": "Dubai",
            "departure": "2026-09-10", "adults": 99,
        })
        self.assertFalse(result["success"])

    def test_flights_invalid_return_date(self):
        """Return date before departure date should fail gracefully."""
        from .services.travel.flights import search_flights
        result = search_flights({
            "origin": "Ahmedabad", "destination": "Dubai",
            "departure": "2026-09-15", "return": "2026-09-10",
            "trip_type": "round-trip",
        })
        self.assertFalse(result["success"])
        self.assertIn("Return date cannot be before departure date.", result["error"])

    def test_flights_same_origin_destination(self):
        """Same origin/destination should fail gracefully."""
        from .services.travel.flights import search_flights
        result = search_flights({
            "origin": "Dubai", "destination": "Dubai",
            "departure": "2026-09-10",
        })
        self.assertFalse(result["success"])

    def test_flights_sort_cheapest(self):
        """Cheapest sort should order by price."""
        from .services.travel.flights import search_flights
        result = search_flights({
            "origin": "Ahmedabad", "destination": "Dubai",
            "departure": "2026-09-10", "sort": "cheapest",
        })
        prices = [r["price"] for r in result["results"]]
        self.assertEqual(prices, sorted(prices))

    def test_hotels_valid_search(self):
        """Valid hotel search should return demo results."""
        from .services.travel.hotels import search_hotels
        result = search_hotels({
            "destination": "Dubai", "check_in": "2026-09-10",
            "check_out": "2026-09-15", "guests": 2, "rooms": 1,
        })
        self.assertTrue(result["success"])
        self.assertTrue(result["results"])

    def test_hotels_missing_destination(self):
        """Missing destination should fail gracefully."""
        from .services.travel.hotels import search_hotels
        result = search_hotels({"check_in": "2026-09-10", "check_out": "2026-09-15"})
        self.assertFalse(result["success"])

    def test_hotels_invalid_dates(self):
        """Check-out before check-in should fail gracefully."""
        from .services.travel.hotels import search_hotels
        result = search_hotels({
            "destination": "Dubai", "check_in": "2026-09-15",
            "check_out": "2026-09-10",
        })
        self.assertFalse(result["success"])

    def test_hotels_sort_rating(self):
        """Rating sort should order by rating descending."""
        from .services.travel.hotels import search_hotels
        result = search_hotels({
            "destination": "Dubai", "check_in": "2026-09-10",
            "check_out": "2026-09-15", "sort": "rating",
        })
        ratings = [r["rating"] for r in result["results"]]
        self.assertEqual(ratings, sorted(ratings, reverse=True))

    def test_activities_valid_search(self):
        """Valid activity search should return demo results."""
        from .services.travel.activities import search_activities
        result = search_activities({"destination": "Dubai", "date": "2026-09-11"})
        self.assertTrue(result["success"])
        self.assertTrue(result["results"])

    def test_activities_missing_destination(self):
        """Missing destination should fail gracefully."""
        from .services.travel.activities import search_activities
        result = search_activities({"date": "2026-09-11"})
        self.assertFalse(result["success"])

    def test_activities_sort_price(self):
        """Sort by price should order by price."""
        from .services.travel.activities import search_activities
        result = search_activities({
            "destination": "Dubai", "date": "2026-09-11", "sort": "price",
        })
        prices = [r["price"] for r in result["results"]]
        self.assertEqual(prices, sorted(prices))

    def test_api_flights_search(self):
        """GET /api/flights/search/ should return JSON."""
        resp = self.client.get("/api/flights/search/", {
            "origin": "Ahmedabad", "destination": "Dubai", "departure": "2026-09-10",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["results"])

    def test_api_flights_search_invalid(self):
        """Invalid flight search should return 400."""
        resp = self.client.get("/api/flights/search/", {"destination": "Dubai"})
        self.assertEqual(resp.status_code, 400)

    def test_api_hotels_search(self):
        """GET /api/hotels/search/ should return JSON."""
        resp = self.client.get("/api/hotels/search/", {
            "destination": "Dubai", "check_in": "2026-09-10", "check_out": "2026-09-15",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["results"])

    def test_api_activities_search(self):
        """GET /api/activities/search/ should return JSON."""
        resp = self.client.get("/api/activities/search/", {"destination": "Dubai"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["results"])

    def test_api_no_keys_exposed(self):
        """Travel API responses must never expose API keys."""
        resp = self.client.get("/api/flights/search/", {
            "origin": "Ahmedabad", "destination": "Dubai", "departure": "2026-09-10",
        })
        body = resp.content.decode("utf-8")
        self.assertNotIn("API_KEY", body)
        self.assertNotIn("sk-", body)

    def test_travel_search_page(self):
        """The /travel-search/ demo page should render."""
        resp = self.client.get("/travel-search/")
        self.assertEqual(resp.status_code, 200)


class MediaUploadTests(OrientiqTestCase):
    def test_media_upload(self):
        self.login_as("testadmin")
        from django.core.files.uploadedfile import SimpleUploadedFile
        file = SimpleUploadedFile("test.txt", b"hello", content_type="text/plain")
        resp = self.client.post(
            "/admin/media/upload/",
            {"file": file, "name": "Test File", "category": "general", "alt_text": ""},
        )
        self.assertEqual(resp.status_code, 302)
class BookingTests(OrientiqTestCase):
    """Phase 9 — Booking + Reservation Workflow Foundation tests."""

    def setUp(self):
        super().setUp()
        cache.clear()

    def login_client(self):
        """Log in as the CLIENT test user with the correct password."""
        self.assertTrue(
            self.client.login(username="testclient", password="ClientPass123!")
        )

    # ============================================================
    # Helpers
    # ============================================================

    @staticmethod
    def _flight_params(**overrides):
        params = {
            "item_type": "flight",
            "origin": "Ahmedabad",
            "destination": "Dubai",
            "departure": "2026-09-10",
            "trip_type": "one-way",
            "adults": "1",
            "cabin_class": "economy",
            "flight_number": "DA101",
        }
        params.update(overrides)
        return params

    @staticmethod
    def _hotel_params(**overrides):
        params = {
            "item_type": "hotel",
            "destination": "Dubai",
            "check_in": "2026-09-10",
            "check_out": "2026-09-15",
            "guests": "2",
            "rooms": "1",
            "hotel_name": "Demo Grand Hotel",
        }
        params.update(overrides)
        return params

    @staticmethod
    def _activity_params(**overrides):
        params = {
            "item_type": "activity",
            "destination": "Dubai",
            "date": "2026-09-10",
            "guests": "2",
            "activity_name": "Demo City Tour",
        }
        params.update(overrides)
        return params

    def _flight_form_data(self, params=None):
        data = {"item_type": "flight"}
        data.update(params or self._flight_params())
        data["person_0-first_name"] = "Aarav"
        data["person_0-last_name"] = "Shah"
        data["person_0-email"] = "aarav@example.com"
        data["person_0-phone"] = "+91 90000 00000"
        data["person_0-nationality"] = "India"
        return data

    def _hotel_form_data(self, params=None):
        data = {"item_type": "hotel"}
        data.update(params or self._hotel_params())
        data["person_0-name"] = "Guest One"
        data["person_0-email"] = "guest1@example.com"
        data["person_0-phone"] = "1111111111"
        data["person_1-name"] = "Guest Two"
        data["person_1-email"] = "guest2@example.com"
        data["person_1-phone"] = "2222222222"
        return data

    def _activity_form_data(self, params=None):
        data = {"item_type": "activity"}
        data.update(params or self._activity_params())
        data["person_0-name"] = "P One"
        data["person_0-email"] = "p1@example.com"
        data["person_0-phone"] = "3333333333"
        data["person_1-name"] = "P Two"
        data["person_1-email"] = "p2@example.com"
        data["person_1-phone"] = "4444444444"
        return data

    def _booking_for(self, user, item_type="flight"):
        """Create a CONFIRMED demo booking through the service layer."""
        if item_type == "flight":
            params = self._flight_params()
            travelers = [{
                "first_name": "Aarav", "last_name": "Shah",
                "email": "aarav@example.com", "phone": "111", "nationality": "India",
            }]
        elif item_type == "hotel":
            params = self._hotel_params()
            travelers = [
                {"first_name": "Guest One", "last_name": "", "email": "guest1@example.com", "phone": "111", "nationality": ""},
                {"first_name": "Guest Two", "last_name": "", "email": "guest2@example.com", "phone": "222", "nationality": ""},
            ]
        else:
            params = self._activity_params()
            travelers = [
                {"first_name": "P One", "last_name": "", "email": "p1@example.com", "phone": "111", "nationality": ""},
                {"first_name": "P Two", "last_name": "", "email": "p2@example.com", "phone": "222", "nationality": ""},
            ]
        from .services.booking import create_booking

        booking, state = create_booking(user, BookingType(item_type), params, travelers)
        return booking
# ============================================================
    # A–C: Search → Select
    # ============================================================

    def test_travel_search_exposes_demo_booking_actions(self):
        """Every inventory category exposes a clear review-selection action."""
        response = self.client.get("/travel-search/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select / Book Demo Flight")
        self.assertContains(response, "Select / Book Demo Hotel")
        self.assertContains(response, "Select / Book Demo Activity")

    def test_search_select_flight(self):
        """Search flights and select a flight for booking review."""
        resp = self.client.get("/api/flights/search/", self._flight_params())
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode("utf-8")
        self.assertIn("DA101", body)
        self.assertIn("Demo Air", body)
        url = "/booking-review/?" + "&".join(
            f"{k}={v}" for k, v in self._flight_params().items()
        )
        self.login_client()
        review = self.client.get(url)
        self.assertEqual(review.status_code, 200)
        self.assertContains(review, "DA101")

    def test_search_select_hotel(self):
        """Search hotels and select a hotel for booking review."""
        resp = self.client.get("/api/hotels/search/", self._hotel_params())
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode("utf-8")
        self.assertIn("Demo Grand Hotel", body)
        self.login_client()
        review = self.client.get(
            "/booking-review/", self._hotel_params()
        )
        self.assertEqual(review.status_code, 200)
        self.assertContains(review, "Demo Grand Hotel")

    def test_search_select_activity(self):
        """Search activities and select an activity for booking review."""
        resp = self.client.get("/api/activities/search/", self._activity_params())
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode("utf-8")
        self.assertIn("Demo City Tour", body)
        self.login_client()
        review = self.client.get(
            "/booking-review/", self._activity_params()
        )
        self.assertEqual(review.status_code, 200)
        self.assertContains(review, "Demo City Tour")

    # ============================================================
    # D–G: Booking Review renders with correct data
    # ============================================================

    def test_booking_review_renders(self):
        """Booking Review page renders for a selected flight."""
        self.login_client()
        resp = self.client.get("/booking-review/", self._flight_params())
        self.assertEqual(resp.status_code, 200)
        self.assertContains(
            resp,
            "DEMO RESERVATION — No real travel reservation or payment has been processed.",
        )
        self.assertContains(resp, "Confirm Demo Booking")

    def test_booking_review_flight_data(self):
        """Correct flight data appears on the review page."""
        self.login_client()
        resp = self.client.get("/booking-review/", self._flight_params())
        self.assertContains(resp, "Demo Air")
        self.assertContains(resp, "DA101")
        self.assertContains(resp, "Ahmedabad")
        self.assertContains(resp, "Dubai")
        self.assertContains(resp, "2026-09-10")
        self.assertContains(resp, "08:00")
        self.assertContains(resp, "10:30")
        self.assertContains(resp, "2h 30m")
        self.assertContains(resp, "Stops")
        self.assertContains(resp, "Economy")
        self.assertContains(resp, "Price per traveler")
        self.assertContains(resp, "120.00")  # server price for 1 adult

    def test_booking_review_hotel_data(self):
        """Correct hotel data appears on the review page."""
        self.login_client()
        resp = self.client.get("/booking-review/", self._hotel_params())
        self.assertContains(resp, "Demo Grand Hotel")
        self.assertContains(resp, "Dubai")
        self.assertContains(resp, "2026-09-10")
        self.assertContains(resp, "2026-09-15")
        self.assertContains(resp, "Deluxe King")
        self.assertContains(resp, "Free WiFi")
        self.assertContains(resp, "Price per night")
        self.assertContains(resp, "Number of nights")
        self.assertContains(resp, "5")
        self.assertContains(resp, "750.00")  # 150 x 5 nights

    def test_booking_review_activity_data(self):
        """Correct activity data appears on the review page."""
        self.login_client()
        resp = self.client.get("/booking-review/", self._activity_params())
        self.assertContains(resp, "Demo City Tour")
        self.assertContains(resp, "Dubai")
        self.assertContains(resp, "2026-09-10")
        self.assertContains(resp, "4h")
        self.assertContains(resp, "Participants")
        self.assertContains(resp, "Price per participant")
        self.assertContains(resp, "90.00")  # 45 x 2 participants

    # ============================================================
    # H–J: Traveler / guest / participant validation
    # ============================================================

    def test_traveler_validation_pass(self):
        """Valid traveler data creates a booking."""
        self.login_client()
        resp = self.client.post("/bookings/create/", self._flight_form_data())
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Booking.objects.filter(user=self.client_user).exists())

    def test_invalid_email_rejected(self):
        """Invalid email is rejected server-side and no booking is created."""
        self.login_client()
        data = self._flight_form_data()
        data["person_0-email"] = "not-an-email"
        resp = self.client.post("/bookings/create/", data)
        self.assertEqual(resp.status_code, 200)  # re-renders with errors
        self.assertContains(resp, "valid email")
        self.assertFalse(Booking.objects.exists())

    def test_missing_required_fields_rejected(self):
        """Missing required traveler fields are rejected server-side."""
        self.login_client()
        data = self._flight_form_data()
        data["person_0-first_name"] = ""
        data["person_0-last_name"] = ""
        data["person_0-email"] = ""
        resp = self.client.post("/bookings/create/", data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "First name is required")
        self.assertContains(resp, "Last name is required")
        self.assertFalse(Booking.objects.exists())

    def test_guest_validation_missing_phone(self):
        """Hotel guests require name, email AND phone."""
        self.login_client()
        data = self._hotel_form_data()
        data["person_0-phone"] = ""
        resp = self.client.post("/bookings/create/", data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Phone is required")
        self.assertFalse(Booking.objects.exists())

    def test_invalid_phone_is_rejected_and_form_data_is_preserved(self):
        """A clearly invalid phone is rejected without losing the submitted form."""
        self.login_client()
        data = self._flight_form_data()
        data["person_0-phone"] = "not-a-phone"
        resp = self.client.post("/bookings/create/", data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Enter a valid phone number.")
        self.assertContains(resp, "aarav@example.com")
        self.assertFalse(Booking.objects.exists())

    def test_activity_participant_phone_is_validated(self):
        """Activity participants use the same required guest validation."""
        self.login_client()
        data = self._activity_form_data()
        data["person_1-phone"] = "12"
        resp = self.client.post("/bookings/create/", data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Enter a valid phone number.")
        self.assertFalse(Booking.objects.exists())

    def test_traveler_names_and_phone_are_normalized_before_persistence(self):
        """Accepted traveler values are normalized by the Django form."""
        self.login_client()
        data = self._flight_form_data()
        data["person_0-first_name"] = "  Aarav   "
        data["person_0-last_name"] = "  Shah  "
        data["person_0-phone"] = "+91 90000 00000"
        self.client.post("/bookings/create/", data)
        traveler = Traveler.objects.get()
        self.assertEqual(traveler.first_name, "Aarav")
        self.assertEqual(traveler.last_name, "Shah")
        self.assertEqual(traveler.phone, "+919000000000")
# ============================================================
    # K–M: Server-side price calculation & tampering rejection
    # ============================================================

    def test_server_side_price_calculation(self):
        """Prices are calculated server-side with Decimal."""
        from .models import Booking
        booking = self._booking_for(self.client_user, "flight")
        self.assertEqual(booking.subtotal, 120)
        self.assertEqual(booking.taxes, 0)
        self.assertEqual(booking.total, 120)
        self.assertEqual(booking.currency, "USD")

    def test_server_side_price_hotel(self):
        """Hotel price = price_per_night * nights (server-computed)."""
        booking = self._booking_for(self.client_user, "hotel")
        self.assertEqual(booking.total, 750)

    def test_client_price_tampering_rejected(self):
        """Client-submitted price is never trusted."""
        self.login_client()
        data = self._flight_form_data()
        data["price"] = "0.01"
        data["subtotal"] = "0.01"
        data["total"] = "0.01"
        self.client.post("/bookings/create/", data)
        booking = Booking.objects.get(user=self.client_user)
        self.assertEqual(booking.total, 120)  # server re-calculated

    def test_client_total_tampering_rejected(self):
        """Client-submitted total is never trusted even when huge."""
        self.login_client()
        data = self._flight_form_data()
        data["total"] = "999999"
        data["price"] = "999999"
        self.client.post("/bookings/create/", data)
        booking = Booking.objects.get(user=self.client_user)
        self.assertEqual(booking.total, 120)

    def test_client_cannot_set_booking_status_or_owner(self):
        """Booking status and ownership always come from the server."""
        self.login_client()
        data = self._flight_form_data()
        data["status"] = BookingStatus.CANCELLED
        data["user"] = str(self.admin_user.pk)
        self.client.post("/bookings/create/", data)
        booking = Booking.objects.get()
        self.assertEqual(booking.status, BookingStatus.CONFIRMED)
        self.assertEqual(booking.user, self.client_user)

    # ============================================================
    # N–R: Successful demo booking
    # ============================================================

    def test_successful_demo_booking(self):
        """Confirm Demo Booking succeeds and redirects to confirmation."""
        self.login_client()
        resp = self.client.post("/bookings/create/", self._flight_form_data())
        self.assertEqual(resp.status_code, 302)
        booking = Booking.objects.get(user=self.client_user)
        self.assertTrue(resp.url.endswith(f"/bookings/{booking.booking_reference}/confirmation/"))
        self.assertTrue(booking.is_demo)

    def test_booking_confirmation_action_is_post_only(self):
        """The state-changing confirmation endpoint rejects GET requests."""
        self.login_client()
        self.assertEqual(self.client.get("/bookings/create/").status_code, 405)

    def test_booking_reference_generated(self):
        """Booking reference is unique and follows ORI-XXXXXXXX."""
        b1 = self._booking_for(self.client_user, "flight")
        b2 = self._booking_for(self.admin_user, "hotel")
        self.assertRegex(b1.booking_reference, r"^ORI-[A-Z0-9]{8}$")
        self.assertNotEqual(b1.booking_reference, b2.booking_reference)

    def test_booking_status_confirmed(self):
        """Booking status becomes CONFIRMED after confirmation."""
        booking = self._booking_for(self.client_user)
        self.assertEqual(booking.status, BookingStatus.CONFIRMED)

    def test_only_draft_or_pending_bookings_can_be_confirmed(self):
        """The final status transition rejects terminal booking states."""
        from .services.booking import confirm_booking

        booking = self._booking_for(self.client_user)
        booking.status = BookingStatus.DRAFT
        booking.save(update_fields=["status"])
        confirm_booking(booking)
        self.assertEqual(booking.status, BookingStatus.CONFIRMED)

        booking.status = BookingStatus.CANCELLED
        booking.save(update_fields=["status"])
        with self.assertRaises(ValueError):
            confirm_booking(booking)
        booking.refresh_from_db()
        self.assertEqual(booking.status, BookingStatus.CANCELLED)

    def test_booking_item_created(self):
        """A BookingItem is created for the selected inventory."""
        booking = self._booking_for(self.client_user)
        items = BookingItem.objects.filter(booking=booking)
        self.assertEqual(items.count(), 1)
        self.assertIn("DA101", items.first().title)
        self.assertEqual(items.first().metadata["inventory_snapshot"]["flight_number"], "DA101")
        self.assertEqual(items.first().metadata["inventory_snapshot"]["price"], 120)

    def test_traveler_created(self):
        """Traveler records are created for the booking."""
        booking = self._booking_for(self.client_user)
        self.assertEqual(booking.travelers.count(), 1)
        self.assertEqual(booking.travelers.first().email, "aarav@example.com")

    def test_hotel_travelers_created(self):
        """Hotel booking creates the expected number of guests."""
        booking = self._booking_for(self.client_user, "hotel")
        self.assertEqual(booking.travelers.count(), 2)

    # ============================================================
    # S–T: Duplicate prevention & rollback
    # ============================================================

    def test_duplicate_confirmation_prevented(self):
        """Confirming the same selection twice creates only one booking."""
        self.login_client()
        first = self.client.post("/bookings/create/", self._flight_form_data())
        self.assertEqual(first.status_code, 302)
        self.assertEqual(Booking.objects.filter(user=self.client_user).count(), 1)

        second = self.client.post("/bookings/create/", self._flight_form_data())
        self.assertEqual(second.status_code, 302)
        self.assertEqual(Booking.objects.filter(user=self.client_user).count(), 1)
        # Redirects back to the already-confirmed booking (no duplicate created).
        booking = Booking.objects.get(user=self.client_user)
        self.assertTrue(
            second.url.endswith(f"/bookings/{booking.booking_reference}/confirmation/")
        )
        # The safe confirmation message is queued for display.
        messages = list(getattr(second.wsgi_request, "_messages", []))
        self.assertTrue(any("already been confirmed" in m.message for m in messages))

    def test_transaction_rollback(self):
        """A failure inside the atomic block rolls back the whole booking."""
        with patch("core.services.booking.build_booking_item", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                self._booking_for(self.client_user, "flight")
        self.assertEqual(Booking.objects.count(), 0)
        self.assertEqual(BookingItem.objects.count(), 0)
        self.assertEqual(Traveler.objects.count(), 0)
# ============================================================
    # U–W: Confirmation page, user history, user detail
    # ============================================================

    def test_confirmation_page(self):
        """Confirmation page renders the booking reference and demo notice."""
        booking = self._booking_for(self.client_user)
        self.login_client()
        resp = self.client.get(f"/bookings/{booking.booking_reference}/confirmation/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, booking.booking_reference)
        self.assertContains(resp, "Booking Confirmed")
        self.assertContains(resp, "DEMO RESERVATION")
        self.assertContains(resp, "No real travel reservation or payment has been processed.")
        self.assertContains(resp, booking.get_booking_type_display())
        self.assertContains(resp, booking.get_status_display())
        self.assertContains(resp, "Demo Air")
        self.assertContains(resp, "aarav@example.com")
        self.assertContains(resp, "120.00 USD")

    def test_invalid_confirmation_reference_returns_404(self):
        """A valid user cannot access a non-existent confirmation reference."""
        self.login_client()
        resp = self.client.get("/bookings/ORI-NOTFOUND/confirmation/")
        self.assertEqual(resp.status_code, 404)

    def test_anonymous_user_cannot_view_confirmation(self):
        """The confirmation page is protected by authentication."""
        booking = self._booking_for(self.client_user)
        self.client.logout()
        resp = self.client.get(f"/bookings/{booking.booking_reference}/confirmation/")
        self.assertEqual(resp.status_code, 302)

    def test_user_booking_history(self):
        """My Bookings lists only the logged-in user's bookings."""
        own_booking = self._booking_for(self.client_user)
        other_booking = self._booking_for(self.admin_user)
        self.login_client()
        resp = self.client.get("/accounts/bookings/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, own_booking.booking_reference)
        self.assertNotContains(resp, other_booking.booking_reference)

    def test_empty_booking_history(self):
        """Authenticated users receive a useful empty-state booking history."""
        self.login_client()
        resp = self.client.get("/accounts/bookings/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "0 bookings")
        self.assertContains(resp, "No bookings yet")

    def test_multiple_bookings_are_listed_for_the_owner(self):
        """A user's list includes each of their bookings and summary fields."""
        flight = self._booking_for(self.client_user, "flight")
        hotel = self._booking_for(self.client_user, "hotel")
        self.login_client()
        resp = self.client.get("/accounts/bookings/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, flight.booking_reference)
        self.assertContains(resp, hotel.booking_reference)
        self.assertContains(resp, "Flight")
        self.assertContains(resp, "Hotel")
        self.assertContains(resp, "Confirmed")
        self.assertContains(resp, "USD")
        self.assertContains(resp, "Demo")

    def test_user_booking_detail(self):
        """User booking detail shows the booking contents."""
        booking = self._booking_for(self.client_user)
        self.login_client()
        resp = self.client.get(f"/accounts/bookings/{booking.booking_reference}/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, booking.booking_reference)
        self.assertContains(resp, booking.get_booking_type_display())
        self.assertContains(resp, "Demo Air")
        self.assertContains(resp, "Aarav Shah")
        self.assertContains(resp, "Confirmed")
        self.assertContains(resp, "Subtotal")
        self.assertContains(resp, "120.00 USD")
        self.assertContains(resp, "DEMO RESERVATION")
        self.assertContains(resp, "No real travel reservation or payment has been processed.")

    # ============================================================
    # X–Z: Isolation & permissions
    # ============================================================

    def test_user_cannot_access_another_users_booking(self):
        """A user cannot view another user's booking (404)."""
        booking = self._booking_for(self.client_user)
        self.login_as("testadmin")  # different user
        resp = self.client.get(f"/accounts/bookings/{booking.booking_reference}/")
        self.assertEqual(resp.status_code, 404)
        resp_conf = self.client.get(f"/bookings/{booking.booking_reference}/confirmation/")
        self.assertEqual(resp_conf.status_code, 404)

    def test_api_user_cannot_access_another_users_booking(self):
        """API booking detail enforces ownership."""
        booking = self._booking_for(self.client_user)
        self.login_as("testadmin")
        resp = self.client.get(f"/api/bookings/{booking.booking_reference}/")
        self.assertEqual(resp.status_code, 404)

    def test_anonymous_redirected_to_login(self):
        """Anonymous users are redirected to login where appropriate."""
        self.client.logout()
        for path in (
            "/booking-review/",
            "/accounts/bookings/",
            "/accounts/bookings/ORI-NOPE1234/",
        ):
            self.assertEqual(self.client.get(path).status_code, 302)
        resp = self.client.post("/bookings/create/", self._flight_form_data())
        self.assertEqual(resp.status_code, 302)

    def test_client_cannot_access_admin_booking_management(self):
        """CLIENT users must be denied admin booking management (403)."""
        self.login_client()
        self.assertEqual(self.client.get("/admin/bookings/").status_code, 403)
        booking = self._booking_for(self.admin_user)
        self.assertEqual(
            self.client.get(f"/admin/bookings/{booking.booking_reference}/").status_code,
            403,
        )

    def test_admin_booking_access(self):
        """ADMIN can view the booking management pages."""
        self._booking_for(self.client_user)
        self.login_as("testadmin")
        self.assertEqual(self.client.get("/admin/bookings/").status_code, 200)
        booking = Booking.objects.first()
        self.assertEqual(
            self.client.get(f"/admin/bookings/{booking.booking_reference}/").status_code,
            200,
        )

    def test_admin_booking_detail_renders_booking_items_travelers_and_totals(self):
        """Admin booking detail uses the custom dashboard and exposes safe booking data."""
        booking = self._booking_for(self.client_user)
        self.login_as("testadmin")
        response = self.client.get(f"/admin/bookings/{booking.booking_reference}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, booking.booking_reference)
        self.assertContains(response, "Demo Air")
        self.assertContains(response, "Aarav Shah")
        self.assertContains(response, "120.00 USD")
        self.assertContains(response, "Confirmed")

    def test_super_admin_booking_access(self):
        """SUPER_ADMIN retains full booking management access."""
        self._booking_for(self.client_user)
        self.login_as("superadmin")
        self.assertEqual(self.client.get("/admin/bookings/").status_code, 200)
        booking = Booking.objects.first()
        self.assertEqual(
            self.client.get(f"/admin/bookings/{booking.booking_reference}/").status_code,
            200,
        )
        # Existing super-admin powers remain intact.
        self.assertEqual(self.client.get("/admin/users/").status_code, 200)
        self.assertEqual(self.client.get("/admin/settings/").status_code, 200)

    # ============================================================
    # AC–AE: Admin search & filters
    # ============================================================

    def test_admin_search_by_reference(self):
        """Admin can search bookings by reference."""
        self._booking_for(self.client_user, "flight")
        self._booking_for(self.admin_user, "hotel")
        self.login_as("testadmin")
        flight = Booking.objects.get(booking_type="flight")
        hotel = Booking.objects.get(booking_type="hotel")
        resp = self.client.get("/admin/bookings/", {"q": flight.booking_reference})
        self.assertContains(resp, flight.booking_reference)
        self.assertNotContains(resp, hotel.booking_reference)

    def test_admin_status_filter(self):
        """Admin can filter bookings by status."""
        self._booking_for(self.client_user)
        self.login_as("testadmin")
        resp = self.client.get("/admin/bookings/", {"status": BookingStatus.CONFIRMED})
        self.assertEqual(resp.status_code, 200)
        booking = Booking.objects.first()
        self.assertContains(resp, booking.booking_reference)

    def test_admin_type_filter(self):
        """Admin can filter bookings by booking type."""
        self._booking_for(self.client_user, "flight")
        self._booking_for(self.admin_user, "hotel")
        self.login_as("testadmin")
        flight = Booking.objects.get(booking_type="flight")
        hotel = Booking.objects.get(booking_type="hotel")
        resp = self.client.get("/admin/bookings/", {"booking_type": "flight"})
        self.assertContains(resp, flight.booking_reference)
        self.assertNotContains(resp, hotel.booking_reference)

    # ============================================================
    # AF–AI: Email, CSRF, rate limiting
    # ============================================================

    def test_email_confirmation(self):
        """booking_confirmation_email sends a demo confirmation email."""
        from .emails import booking_confirmation_email
        from django.core import mail

        booking = self._booking_for(self.client_user)
        result = booking_confirmation_email(booking)
        self.assertEqual(result, 1)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn(booking.user.email, email.to)
        self.assertIn(booking.booking_reference, email.subject)
        self.assertIn(booking.booking_reference, email.body)
        self.assertIn(booking.get_booking_type_display(), email.body)
        self.assertIn(booking.get_status_display(), email.body)
        self.assertIn("Demo Air", email.body)
        self.assertIn("Aarav Shah", email.body)
        self.assertIn("120.00 USD", email.body)
        self.assertIn(
            "DEMO BOOKING — No real provider reservation or payment has been processed.",
            email.body,
        )

    def test_confirmation_email_is_sent_only_after_commit(self):
        """The web confirmation path schedules delivery with on_commit."""
        from django.core import mail

        self.login_client()
        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            response = self.client.post("/bookings/create/", self._flight_form_data())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(callbacks), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Orientiq Booking Confirmed", mail.outbox[0].subject)

    def test_email_failure_handling(self):
        """An email failure must not raise or corrupt the booking flow."""
        from .emails import booking_confirmation_email

        booking = self._booking_for(self.client_user)
        with patch("core.emails.send_mail", side_effect=RuntimeError("smtp down")):
            result = booking_confirmation_email(booking)
        self.assertIsNone(result)
        # The booking still exists and remains committed.
        self.assertTrue(Booking.objects.filter(pk=booking.pk).exists())

    def test_csrf_protection(self):
        """POST to the booking confirm endpoint requires a CSRF token."""
        csrf_client = Client(enforce_csrf_checks=True)
        self.assertTrue(
            csrf_client.login(username="testclient", password="ClientPass123!")
        )
        resp = csrf_client.post("/bookings/create/", self._flight_form_data())
        self.assertEqual(resp.status_code, 403)
        self.assertFalse(Booking.objects.exists())

    def test_rate_limiting(self):
        """Booking creation is rate limited server-side (HTTP 429)."""
        from .services.booking import BOOKING_RATE_MAX, get_client_ip

        self.login_client()
        # Prime the cache counter for this client's IP.
        prime = self.client.post("/bookings/create/", self._flight_form_data())
        request = prime.wsgi_request
        cache.set(f"booking_rate_{get_client_ip(request)}", BOOKING_RATE_MAX, 60)
        # A fresh selection (different flight number) still hits the limiter.
        start = Booking.objects.count()
        resp = self.client.post(
            "/bookings/create/",
            self._flight_form_data({"flight_number": "DE202"}),
        )
        self.assertEqual(resp.status_code, 429)
        self.assertEqual(Booking.objects.count(), start)
        self.assertNotEqual(resp.content.decode("utf-8"), "")

    def test_api_booking_creation_is_rate_limited(self):
        """The JSON booking endpoint has the same bounded-attempt protection."""
        from .services.booking import BOOKING_RATE_MAX, get_client_ip

        self.login_client()
        request = self.client.get("/travel-search/").wsgi_request
        cache.set(f"booking_rate_{get_client_ip(request)}", BOOKING_RATE_MAX, 60)
        response = self.client.post(
            "/api/bookings/create/",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 429)
        self.assertEqual(Booking.objects.count(), 0)

    def test_api_booking_rejects_malformed_selection_without_internal_details(self):
        """Malformed JSON selection data is a safe 400, never a server error."""
        self.login_client()
        response = self.client.post(
            "/api/bookings/create/",
            data=json.dumps(
                {"item_type": "flight", "params": [], "travelers": []}
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid selection data.")
        self.assertNotIn("traceback", response.content.decode("utf-8").lower())
        self.assertEqual(Booking.objects.count(), 0)

    def test_api_booking_rejects_unverified_inventory_without_internal_details(self):
        """An unknown inventory identifier cannot create a booking or leak errors."""
        self.login_client()
        params = self._flight_params(flight_number="NOT-A-FLIGHT")
        response = self.client.post(
            "/api/bookings/create/",
            data=json.dumps(
                {
                    "item_type": "flight",
                    "params": params,
                    "travelers": [
                        {
                            "first_name": "Aarav",
                            "last_name": "Shah",
                            "email": "aarav@example.com",
                            "phone": "+919000000000",
                            "nationality": "India",
                        }
                    ],
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("traceback", response.content.decode("utf-8").lower())
        self.assertEqual(Booking.objects.count(), 0)

    def test_api_booking_creation_requires_csrf_for_session_authentication(self):
        """Session-authenticated JSON booking creation remains CSRF protected."""
        csrf_client = Client(enforce_csrf_checks=True)
        self.assertTrue(csrf_client.login(username="testclient", password="ClientPass123!"))
        response = csrf_client.post(
            "/api/bookings/create/",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_booking_money_constraints_reject_negative_values(self):
        """Database constraints protect persisted booking totals."""
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Booking.objects.create(
                    user=self.client_user,
                    booking_reference="ORI-NEGATIVE",
                    subtotal=-1,
                    taxes=0,
                    total=0,
                )

    def test_booking_item_money_constraint_rejects_negative_price(self):
        """Database constraints protect persisted inventory snapshot prices."""
        booking = self._booking_for(self.client_user)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BookingItem.objects.create(
                    booking=booking,
                    item_type=BookingType.FLIGHT,
                    title="Invalid snapshot",
                    route_or_destination="Ahmedabad to Dubai",
                    price=-1,
                    currency="USD",
                )
