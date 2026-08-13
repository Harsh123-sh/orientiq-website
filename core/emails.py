"""
Email services for Orientiq.

Phase 9 booking confirmation email. Uses booking.user.email — never an
undefined `request` object. send_mail runs with fail_silently=True so an
email failure can never corrupt a successfully committed booking.
"""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string



EMAIL_DEMO_DISCLAIMER = (
    "DEMO BOOKING — No real provider reservation or payment has been processed."
)


def booking_confirmation_email(booking):
    """Send a demo booking confirmation email to the booking owner.

    Args:
        booking: core.models.Booking instance (must have .bookings owner link).

    Returns:
        int (number of emails sent) or None on failure.
    """
    if not booking or not booking.user or not booking.user.email:
        return None

    context = {
        "booking": booking,
        "items": booking.items.select_related("booking").all(),
        "travelers": booking.travelers.all(),
        "demo_disclaimer": EMAIL_DEMO_DISCLAIMER,
        "site_name": "Orientiq",
    }

    subject = f"Orientiq Booking Confirmed — {booking.booking_reference}"
    body = render_to_string("emails/booking_confirmation_email.txt", context)

    try:
        return send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=True,
        )
    except Exception:
        # Never raise: an email failure must not affect the booking flow.
        return None
