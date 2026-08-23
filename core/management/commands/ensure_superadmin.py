import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or update the production Superadmin account."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("Superadmin")
        email = os.environ.get("sachwani25harsh@gmail.com")
        password = os.environ.get("Harsh@31")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_USERNAME/PASSWORD not configured. "
                    "Skipping Superadmin setup."
                )
            )
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email or "",
            },
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