"""URL patterns for the core app.

Note: the project's ROOT_URLCONF (orientiq/urls.py) wires all booking routes
directly. This module is kept in sync so `include('core.urls')` also works;
no user-facing routes are registered here that are not in the root config.
"""

from django.urls import path

from . import views

urlpatterns = [
    # Travel Search / Inventory (Phase 8)
    path("travel-search/", views.travel_search_page, name="travel_search"),
    path("api/flights/search/", views.api_flights_search, name="api_flights_search"),
    path("api/hotels/search/", views.api_hotels_search, name="api_hotels_search"),
    path("api/activities/search/", views.api_activities_search, name="api_activities_search"),
    # Booking workflow (Phase 9)
    path("booking-review/", views.booking_review_page, name="booking_review"),
    path("bookings/create/", views.create_booking, name="create_booking"),
    path(
        "bookings/<str:reference>/confirmation/",
        views.booking_confirmation,
        name="booking_confirmation",
    ),
    path("accounts/bookings/", views.user_booking_list, name="user_booking_list"),
    path(
        "accounts/bookings/<str:reference>/",
        views.user_booking_detail,
        name="user_booking_detail",
    ),
    # Booking JSON APIs (Phase 9)
    path("api/bookings/", views.api_booking_list, name="api_booking_list"),
    path("api/bookings/create/", views.api_create_booking, name="api_create_booking"),
    path(
        "api/bookings/<str:reference>/",
        views.api_booking_detail,
        name="api_booking_detail",
    ),
]