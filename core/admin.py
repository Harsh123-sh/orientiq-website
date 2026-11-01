from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    CandidateApplication,
    ChatbotConversation,
    ChatbotFAQ,
    ConsultationRequest,
    ContactInquiry,
    HumanSupportRequest,
    InquiryAttachment,
)


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


@admin.register(ChatbotConversation)
class ChatbotConversationAdmin(admin.ModelAdmin):
    list_display = ("reference", "language", "unanswered", "unanswered_notification_status", "updated_at")
    list_filter = ("language", "unanswered", "updated_at")
    search_fields = ("reference", "last_question")
    readonly_fields = ("reference", "transcript", "created_at", "updated_at")
    ordering = ("-updated_at",)


@admin.register(ChatbotFAQ)
class ChatbotFAQAdmin(admin.ModelAdmin):
    list_display = ("question", "active", "display_order", "updated_at")
    list_filter = ("active",)
    search_fields = ("question", "answer")
    ordering = ("display_order", "question")


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "preferred_date", "preferred_time", "business_time_zone", "status", "notification_status")
    list_filter = ("status", "preferred_date", "notification_status")
    search_fields = ("name", "email", "phone", "project_type", "description")
    readonly_fields = ("consented_at", "created_at", "calendar_event_id")
    ordering = ("-created_at",)


@admin.register(HumanSupportRequest)
class HumanSupportRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "status", "notification_status", "created_at")
    list_filter = ("status", "notification_status", "created_at")
    search_fields = ("name", "email", "phone", "conversation__reference")
    readonly_fields = ("consented_at", "created_at")
    ordering = ("-created_at",)


@admin.register(InquiryAttachment)
class InquiryAttachmentAdmin(admin.ModelAdmin):
    list_display = ("original_name", "inquiry", "content_type", "size", "created_at", "download_link")
    search_fields = ("original_name", "inquiry__reference", "inquiry__email")
    readonly_fields = ("original_name", "content_type", "size", "created_at")
    exclude = ("file",)
    ordering = ("-created_at",)

    @admin.display(description="Private download")
    def download_link(self, obj):
        return format_html(
            '<a href="{}">Download</a>',
            reverse("chatbot_attachment_download", args=[obj.pk]),
        )
