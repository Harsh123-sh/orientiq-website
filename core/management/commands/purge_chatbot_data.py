"""Delete expired chatbot conversations and private attachments."""

from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import ChatbotConversation, ContactInquiry, InquiryAttachment


class Command(BaseCommand):
    help = "Purge expired chatbot transcripts and private uploaded files."

    def handle(self, *args, **options):
        now = timezone.now()
        conversation_cutoff = now - timedelta(days=settings.CHATBOT_RETENTION_DAYS)
        file_cutoff = now - timedelta(days=settings.CHATBOT_FILE_RETENTION_DAYS)

        expired_attachments = InquiryAttachment.objects.filter(created_at__lt=file_cutoff)
        deleted_files = expired_attachments.count()
        expired_attachments.delete()

        deleted_conversations, _ = ChatbotConversation.objects.filter(
            updated_at__lt=conversation_cutoff,
        ).delete()
        redacted_inquiries = ContactInquiry.objects.filter(
            source="chatbot",
            created_at__lt=conversation_cutoff,
        ).update(conversation_transcript=[])

        self.stdout.write(self.style.SUCCESS(
            f"Deleted {deleted_conversations} expired conversation records and "
            f"{deleted_files} private files; redacted {redacted_inquiries} inquiry transcripts."
        ))
