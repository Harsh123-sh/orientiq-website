"""
URL configuration for orientiq project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from core import admin_views, views

urlpatterns = [
    # Django built-in admin (emergency/internal use)
    path('django-admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # Services
    path('services/', views.services, name='services'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),

    # Industries
    path('industries/', views.industries, name='industries'),
    path('industries/<slug:slug>/', views.industry_detail, name='industry_detail'),

    # Technologies
    path('technologies/', views.technologies, name='technologies'),

    # Company
    path('company/', views.company, name='company'),
    path('company/about/', views.company_about, name='company_about'),
    path('company/process/', views.company_process, name='company_process'),
    path('company/careers/', views.company_careers, name='company_careers'),
    path('company/contact/', views.company_contact, name='company_contact'),

    # Start a Project
    path('start-project/', views.start_project, name='start_project'),

    # Products
    path('products/', views.products, name='products'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),

    # ============ ACCOUNTS / AUTHENTICATION ============
    path('accounts/register/', views.register, name='accounts_register'),
    path('accounts/login/', views.OrientiqLoginView.as_view(), name='accounts_login'),
    path('accounts/logout/', views.logout_view, name='accounts_logout'),
    path('accounts/forgot-password/', views.OrientiqPasswordResetView.as_view(), name='accounts_forgot_password'),
    path(
        'accounts/reset-password/',
        auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
        name='accounts_password_reset_done',
    ),
    path(
        'accounts/reset-password/<uidb64>/<token>/',
        views.OrientiqPasswordResetConfirmView.as_view(),
        name='accounts_password_reset_confirm',
    ),
    path(
        'accounts/reset-password/complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
        name='accounts_password_reset_complete',
    ),
    path('accounts/profile/', views.profile, name='accounts_profile'),
    path('accounts/settings/', views.account_settings, name='accounts_settings'),
    path('accounts/change-password/', views.OrientiqPasswordChangeView.as_view(), name='accounts_change_password'),

    # ============ ADMIN DASHBOARD / CMS ============
    path('admin/login/', views.OrientiqLoginView.as_view(), name='admin_login'),
    path('admin/logout/', views.logout_view, name='admin_logout'),
    path('admin/', admin_views.dashboard, name='admin_dashboard'),
    path('admin/profile/', admin_views.admin_profile, name='admin_profile'),
    path('admin/change-password/', admin_views.admin_change_password, name='admin_change_password'),

    # Services CMS
    path('admin/services/', admin_views.service_list, name='admin_service_list'),
    path('admin/services/create/', admin_views.service_create, name='admin_service_create'),
    path('admin/services/<int:pk>/edit/', admin_views.service_edit, name='admin_service_edit'),
    path('admin/services/<int:pk>/delete/', admin_views.service_delete, name='admin_service_delete'),

    # Industries CMS
    path('admin/industries/', admin_views.industry_list, name='admin_industry_list'),
    path('admin/industries/create/', admin_views.industry_create, name='admin_industry_create'),
    path('admin/industries/<int:pk>/edit/', admin_views.industry_edit, name='admin_industry_edit'),
    path('admin/industries/<int:pk>/delete/', admin_views.industry_delete, name='admin_industry_delete'),

    # Portfolio CMS
    path('admin/portfolio/', admin_views.portfolio_list, name='admin_portfolio_list'),
    path('admin/portfolio/create/', admin_views.portfolio_create, name='admin_portfolio_create'),
    path('admin/portfolio/<int:pk>/edit/', admin_views.portfolio_edit, name='admin_portfolio_edit'),
    path('admin/portfolio/<int:pk>/delete/', admin_views.portfolio_delete, name='admin_portfolio_delete'),

    # Products CMS
    path('admin/products/', admin_views.product_list, name='admin_product_list'),
    path('admin/products/create/', admin_views.product_create, name='admin_product_create'),
    path('admin/products/<int:pk>/edit/', admin_views.product_edit, name='admin_product_edit'),
    path('admin/products/<int:pk>/delete/', admin_views.product_delete, name='admin_product_delete'),

    # Technologies CMS
    path('admin/technologies/', admin_views.technology_list, name='admin_technology_list'),
    path('admin/technologies/create/', admin_views.technology_create, name='admin_technology_create'),
    path('admin/technologies/<int:pk>/edit/', admin_views.technology_edit, name='admin_technology_edit'),
    path('admin/technologies/<int:pk>/delete/', admin_views.technology_delete, name='admin_technology_delete'),

    # Testimonials CMS
    path('admin/testimonials/', admin_views.testimonial_list, name='admin_testimonial_list'),
    path('admin/testimonials/create/', admin_views.testimonial_create, name='admin_testimonial_create'),
    path('admin/testimonials/<int:pk>/edit/', admin_views.testimonial_edit, name='admin_testimonial_edit'),
    path('admin/testimonials/<int:pk>/delete/', admin_views.testimonial_delete, name='admin_testimonial_delete'),

    # Inquiries
    path('admin/inquiries/', admin_views.inquiry_list, name='admin_inquiry_list'),
    path('admin/inquiries/<int:pk>/', admin_views.inquiry_detail, name='admin_inquiry_detail'),

    # Users
    path('admin/users/', admin_views.user_list, name='admin_user_list'),
    path('admin/users/<int:pk>/edit/', admin_views.user_edit, name='admin_user_edit'),

    # Media
    path('admin/media/', admin_views.media_list, name='admin_media_list'),
    path('admin/media/upload/', admin_views.media_upload, name='admin_media_upload'),
    path('admin/media/<int:pk>/delete/', admin_views.media_delete, name='admin_media_delete'),

    # Settings
    path('admin/settings/', admin_views.settings_view, name='admin_settings'),

    # Activity
    path('admin/activity/', admin_views.activity_list, name='admin_activity'),

    # Live Intelligence (Phase 7)
    path('live-intelligence/', views.live_intelligence_page, name='live_intelligence'),
    path('api/location/search/', views.api_location_search, name='api_location_search'),
    path('api/weather/', views.api_weather, name='api_weather'),
    path('api/live-intelligence/', views.api_live_intelligence, name='api_live_intelligence'),

        # Travel Inventory (Phase 8)
    path('travel-search/', views.travel_search_page, name='travel_search'),
    path('api/flights/search/', views.api_flights_search, name='api_flights_search'),
    path('api/hotels/search/', views.api_hotels_search, name='api_hotels_search'),
    path('api/activities/search/', views.api_activities_search, name='api_activities_search'),
    
    # Bookings (Phase 9)
    path('booking-review/', views.booking_review_page, name='booking_review'),
    path('bookings/create/', views.create_booking, name='create_booking'),
    path('bookings/<str:reference>/confirmation/', views.booking_confirmation, name='booking_confirmation'),
    path('accounts/bookings/', views.user_booking_list, name='user_booking_list'),
    path('accounts/bookings/<str:reference>/', views.user_booking_detail, name='user_booking_detail'),
    path('admin/bookings/', admin_views.booking_list, name='admin_booking_list'),
    path('admin/bookings/<str:reference>/', admin_views.booking_detail, name='admin_booking_detail'),
    path('api/bookings/', views.api_booking_list, name='api_booking_list'),
    path('api/bookings/create/', views.api_create_booking, name='api_create_booking'),
    path('api/bookings/<str:reference>/', views.api_booking_detail, name='api_booking_detail'),


    # AI Assistant
    path('api/ai/chat/', views.ai_chat, name='ai_chat'),

    # Phase 1 (dev-only)
    path('design-system/', views.design_system, name='design_system'),
    path('favicon.ico', views.FaviconRedirectView.as_view()),
]
