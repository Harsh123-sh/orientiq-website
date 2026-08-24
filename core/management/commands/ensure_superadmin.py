import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update the production Superadmin account."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip().lower()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "")

        if not username:
            self.stdout.write(
                self.style.ERROR(
                    "DJANGO_SUPERUSER_USERNAME is not configured."
                )
            )
            return

        if not password:
            self.stdout.write(
                self.style.ERROR(
                    "DJANGO_SUPERUSER_PASSWORD is not configured."
                )
            )
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email},
        )

        if email:
            user.email = email

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superadmin '{username}' created successfully."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superadmin '{username}' updated successfully."
                )
            )