
"""
URL configuration for orentiq project.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import path, reverse

from core import admin_views, views


# ============================================================
# XML SITEMAP CONFIGURATION
# ============================================================

class StaticViewSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return [
            "home",
            "about",
            "problem_solving",
            "services",
            "industries",
            "technologies",
            "company",
            "company_about",
            "company_founder",
            "company_process",
            "company_careers",
            "company_contact",
            "start_project",
            "products",
        ]

    def location(self, item):
        return reverse(item)


sitemaps = {
    "static": StaticViewSitemap,
}


# ============================================================
# URL PATTERNS
# ============================================================

urlpatterns = [

    # ========================================================
    # GOOGLE SEARCH CONSOLE SITEMAP
    # ========================================================

    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),

    # ========================================================
    # DJANGO ADMIN
    # ========================================================

    path("django-admin/", admin.site.urls),

    # ========================================================
    # MAIN WEBSITE
    # ========================================================

    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("problem-solving/", views.problem_solving, name="problem_solving"),

    # ========================================================
    # SERVICES
    # ========================================================

    path("services/", views.services, name="services"),
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),

    # ========================================================
    # INDUSTRIES
    # ========================================================

    path("industries/", views.industries, name="industries"),
    path("industries/<slug:slug>/", views.industry_detail, name="industry_detail"),

    # ========================================================
    # TECHNOLOGIES
    # ========================================================

    path("technologies/", views.technologies, name="technologies"),

    # ========================================================
    # COMPANY
    # ========================================================

    path("company/", views.company, name="company"),
    path("company/about/", views.company_about, name="company_about"),
    path("company/founder/", views.company_founder, name="company_founder"),
    path("company/process/", views.company_process, name="company_process"),
    path("company/careers/", views.company_careers, name="company_careers"),

    path(
        "admin/candidate-applications/<int:pk>/resume/",
        views.candidate_resume_download,
        name="candidate_resume_download",
    ),

    path("company/contact/", views.company_contact, name="company_contact"),

    # ========================================================
    # START A PROJECT
    # ========================================================

    path("start-project/", views.start_project, name="start_project"),

    # ========================================================
    # PRODUCTS
    # ========================================================

    path("products/", views.products, name="products"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),

    # ========================================================
    # ACCOUNTS / AUTHENTICATION
    # ========================================================

    path("accounts/register/", views.register, name="accounts_register"),
    path("accounts/login/", views.OrentiqLoginView.as_view(), name="accounts_login"),
    path("accounts/logout/", views.logout_view, name="accounts_logout"),

    path(
        "accounts/forgot-password/",
        views.OrentiqPasswordResetView.as_view(),
        name="accounts_forgot_password",
    ),

    path(
        "accounts/reset-password/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="accounts_password_reset_done",
    ),

    path(
        "accounts/reset-password/<uidb64>/<token>/",
        views.OrentiqPasswordResetConfirmView.as_view(),
        name="accounts_password_reset_confirm",
    ),

    path(
        "accounts/reset-password/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="accounts_password_reset_complete",
    ),

    path("accounts/dashboard/", views.client_dashboard, name="client_dashboard"),
    path("accounts/profile/", views.profile, name="accounts_profile"),
    path("accounts/settings/", views.account_settings, name="accounts_settings"),

    path(
        "accounts/change-password/",
        views.OrentiqPasswordChangeView.as_view(),
        name="accounts_change_password",
    ),

    path(
        "accounts/documents/<int:pk>/download/",
        views.client_document_download,
        name="client_document_download",
    ),

    path(
        "accounts/deletion-request/",
        views.client_deletion_request,
        name="client_deletion_request",
    ),

    # ========================================================
    # ADMIN DASHBOARD / CMS
    # ========================================================

    path("admin/login/", views.OrentiqLoginView.as_view(), name="admin_login"),
    path("admin/logout/", views.logout_view, name="admin_logout"),
    path("admin/", admin_views.dashboard, name="admin_dashboard"),
    path("admin/profile/", admin_views.admin_profile, name="admin_profile"),
    path(
        "admin/change-password/",
        admin_views.admin_change_password,
        name="admin_change_password",
    ),

    # Services CMS
    path("admin/services/", admin_views.service_list, name="admin_service_list"),
    path("admin/services/create/", admin_views.service_create, name="admin_service_create"),
    path("admin/services/<int:pk>/edit/", admin_views.service_edit, name="admin_service_edit"),
    path("admin/services/<int:pk>/delete/", admin_views.service_delete, name="admin_service_delete"),

    # Industries CMS
    path("admin/industries/", admin_views.industry_list, name="admin_industry_list"),
    path("admin/industries/create/", admin_views.industry_create, name="admin_industry_create"),
    path("admin/industries/<int:pk>/edit/", admin_views.industry_edit, name="admin_industry_edit"),
    path("admin/industries/<int:pk>/delete/", admin_views.industry_delete, name="admin_industry_delete"),

    # Portfolio CMS
    path("admin/portfolio/", admin_views.portfolio_list, name="admin_portfolio_list"),
    path("admin/portfolio/create/", admin_views.portfolio_create, name="admin_portfolio_create"),
    path("admin/portfolio/<int:pk>/edit/", admin_views.portfolio_edit, name="admin_portfolio_edit"),
    path("admin/portfolio/<int:pk>/delete/", admin_views.portfolio_delete, name="admin_portfolio_delete"),

    # Products CMS
    path("admin/products/", admin_views.product_list, name="admin_product_list"),
    path("admin/products/create/", admin_views.product_create, name="admin_product_create"),
    path("admin/products/<int:pk>/edit/", admin_views.product_edit, name="admin_product_edit"),
    path("admin/products/<int:pk>/delete/", admin_views.product_delete, name="admin_product_delete"),

    # Technologies CMS
    path("admin/technologies/", admin_views.technology_list, name="admin_technology_list"),
    path("admin/technologies/create/", admin_views.technology_create, name="admin_technology_create"),
    path("admin/technologies/<int:pk>/edit/", admin_views.technology_edit, name="admin_technology_edit"),
    path("admin/technologies/<int:pk>/delete/", admin_views.technology_delete, name="admin_technology_delete"),

    # Testimonials CMS
    path("admin/testimonials/", admin_views.testimonial_list, name="admin_testimonial_list"),
    path("admin/testimonials/create/", admin_views.testimonial_create, name="admin_testimonial_create"),
    path("admin/testimonials/<int:pk>/edit/", admin_views.testimonial_edit, name="admin_testimonial_edit"),
    path("admin/testimonials/<int:pk>/delete/", admin_views.testimonial_delete, name="admin_testimonial_delete"),

    # Inquiries
    path("admin/inquiries/", admin_views.inquiry_list, name="admin_inquiry_list"),
    path("admin/inquiries/<int:pk>/", admin_views.inquiry_detail, name="admin_inquiry_detail"),
    path("admin/chatbot/", admin_views.chatbot_dashboard, name="admin_chatbot_dashboard"),

    path(
        "admin/chatbot/conversations/<uuid:reference>/",
        admin_views.chatbot_conversation_detail,
        name="admin_chatbot_conversation_detail",
    ),

    path("admin/chatbot/faqs/create/", admin_views.chatbot_faq_edit, name="admin_chatbot_faq_create"),
    path("admin/chatbot/faqs/<int:pk>/edit/", admin_views.chatbot_faq_edit, name="admin_chatbot_faq_edit"),

    # Users
    path("admin/users/", admin_views.user_list, name="admin_user_list"),
    path("admin/users/<int:pk>/edit/", admin_views.user_edit, name="admin_user_edit"),

    # Media
    path("admin/media/", admin_views.media_list, name="admin_media_list"),
    path("admin/media/upload/", admin_views.media_upload, name="admin_media_upload"),
    path("admin/media/<int:pk>/delete/", admin_views.media_delete, name="admin_media_delete"),

    # Settings
    path("admin/settings/", admin_views.settings_view, name="admin_settings"),

    # Activity
    path("admin/activity/", admin_views.activity_list, name="admin_activity"),
    path("admin/clients/", admin_views.client_list, name="admin_client_list"),
    path("admin/clients/create/", admin_views.client_create, name="admin_client_create"),
    path("admin/clients/<int:pk>/", admin_views.client_detail, name="admin_client_detail"),
    path("admin/projects/", admin_views.project_list, name="admin_project_list"),
    path("admin/projects/create/", admin_views.project_edit, name="admin_project_create"),
    path("admin/projects/<int:pk>/edit/", admin_views.project_edit, name="admin_project_edit"),
    path("admin/projects/<int:pk>/updates/create/", admin_views.project_update_create, name="admin_project_update_create"),
    path("admin/documents/", admin_views.document_list, name="admin_document_list"),
    path("admin/documents/upload/", admin_views.document_upload, name="admin_document_upload"),

    # ========================================================
    # LIVE INTELLIGENCE - PHASE 7
    # ========================================================

    path("live-intelligence/", views.live_intelligence_page, name="live_intelligence"),
    path("api/location/search/", views.api_location_search, name="api_location_search"),
    path("api/weather/", views.api_weather, name="api_weather"),
    path("api/live-intelligence/", views.api_live_intelligence, name="api_live_intelligence"),

    # ========================================================
    # TRAVEL INVENTORY - PHASE 8
    # ========================================================

    path("travel-search/", views.travel_search_page, name="travel_search"),
    path("api/flights/search/", views.api_flights_search, name="api_flights_search"),
    path("api/hotels/search/", views.api_hotels_search, name="api_hotels_search"),
    path("api/activities/search/", views.api_activities_search, name="api_activities_search"),

    # ========================================================
    # BOOKINGS - PHASE 9
    # ========================================================

    path("booking-review/", views.booking_review_page, name="booking_review"),
    path("bookings/create/", views.create_booking, name="create_booking"),
    path("bookings/<str:reference>/confirmation/", views.booking_confirmation, name="booking_confirmation"),

    path("accounts/bookings/", views.user_booking_list, name="user_booking_list"),
    path("accounts/bookings/<str:reference>/", views.user_booking_detail, name="user_booking_detail"),

    path("admin/bookings/", admin_views.booking_list, name="admin_booking_list"),
    path("admin/bookings/<str:reference>/", admin_views.booking_detail, name="admin_booking_detail"),

    path("api/bookings/", views.api_booking_list, name="api_booking_list"),
    path("api/bookings/create/", views.api_create_booking, name="api_create_booking"),
    path("api/bookings/<str:reference>/", views.api_booking_detail, name="api_booking_detail"),

    # ========================================================
    # AI ASSISTANT
    # ========================================================

    path("api/ai/chat/", views.ai_chat, name="ai_chat"),
    path("api/ai/inquiries/", views.chatbot_inquiry_submit, name="chatbot_inquiry_submit"),
    path("api/ai/business-info/", views.chatbot_business_info, name="chatbot_business_info"),

    path(
        "api/ai/consultations/availability/",
        views.chatbot_consultation_availability,
        name="chatbot_consultation_availability",
    ),

    path("api/ai/consultations/", views.chatbot_consultation_submit, name="chatbot_consultation_submit"),
    path("api/ai/support/", views.chatbot_support_submit, name="chatbot_support_submit"),
    path("api/ai/delete-data/", views.chatbot_delete_visitor_data, name="chatbot_delete_data"),

    path(
        "admin/chatbot/attachments/<int:pk>/download/",
        views.chatbot_attachment_download,
        name="chatbot_attachment_download",
    ),

    # ========================================================
    # DEVELOPMENT / DESIGN SYSTEM
    # ========================================================

    path("design-system/", views.design_system, name="design_system"),
    path("favicon.ico", views.FaviconRedirectView.as_view()),
]
