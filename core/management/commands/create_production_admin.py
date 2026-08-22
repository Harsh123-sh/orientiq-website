import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Profile, UserRole


class Command(BaseCommand):
    help = "Create or repair the production Super Admin account."

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()

        # ---------------------------------------------------------
        # 1. Read production credentials from environment variables
        # ---------------------------------------------------------
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip().lower()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not username:
            raise CommandError(
                "DJANGO_SUPERUSER_USERNAME is required and must not be empty."
            )

        if not email:
            raise CommandError(
                "DJANGO_SUPERUSER_EMAIL is required and must not be empty."
            )

        if not password:
            raise CommandError(
                "DJANGO_SUPERUSER_PASSWORD is required and must not be empty."
            )

        # ---------------------------------------------------------
        # 2. Find existing user by username
        # ---------------------------------------------------------
        user = User.objects.filter(username=username).first()

        # ---------------------------------------------------------
        # 3. Create user if it does not exist
        # ---------------------------------------------------------
        if user is None:
            user = User(username=username)

            # Set email if the User model has an email field.
            if hasattr(user, "email"):
                user.email = email

        else:
            # Existing user: update email.
            if hasattr(user, "email"):
                user.email = email

        # ---------------------------------------------------------
        # 4. Make this user a fully active Django Super Admin
        # ---------------------------------------------------------
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True

        # Always reset the password to the configured production password.
        user.set_password(password)

        user.save()

        # ---------------------------------------------------------
        # 5. Create or repair Profile
        # ---------------------------------------------------------
        profile, _ = Profile.objects.get_or_create(user=user)

        # Make sure the profile is SUPER_ADMIN.
        profile.role = UserRole.SUPER_ADMIN
        profile.save()

        # ---------------------------------------------------------
        # 6. Success message
        # ---------------------------------------------------------
        self.stdout.write(
            self.style.SUCCESS(
                f"Production Super Admin '{user.username}' is ready."
            )
        )