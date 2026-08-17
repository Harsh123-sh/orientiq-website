from django.contrib import admin

from .models import ContactInquiry


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company", "service", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "company", "message")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
