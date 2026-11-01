from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import InquiryAttachment


@receiver(pre_delete, sender=InquiryAttachment)
def remove_private_chatbot_attachment(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)
