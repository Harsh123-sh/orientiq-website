from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import CandidateApplication, ContactInquiry


@admin.register(CandidateApplication)
class CandidateApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "area_of_interest", "experience_level", "status", "created_at")
    list_filter = ("status", "area_of_interest", "experience_level", "created_at")
    search_fields = ("full_name", "email")
    readonly_fields = ("created_at", "updated_at", "consented_at", "resume_download")
    exclude = ("resume",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    @admin.display(description="Resume")
    def resume_download(self, obj):
        if not obj or not obj.resume:
            return "No resume uploaded"
        return format_html('<a href="{}">Download resume</a>', reverse("candidate_resume_download", args=[obj.pk]))


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company", "service", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "company", "message")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
