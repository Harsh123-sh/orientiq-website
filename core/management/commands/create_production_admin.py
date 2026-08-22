import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from core.models import Profile, UserRole


class Command(BaseCommand):
    help = "Create or repair the deployment super-admin account."

    def handle(self, *args, **options):
        user_model = get_user_model()
        username_field = user_model.USERNAME_FIELD
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip().lower()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not email:
            raise CommandError("DJANGO_SUPERUSER_EMAIL is required.")
        if username_field == "username" and not username:
            raise CommandError("DJANGO_SUPERUSER_USERNAME is required for this user model.")

        user = user_model.objects.filter(email__iexact=email).first()
        if user is None and username:
            user = user_model.objects.filter(**{username_field: username}).first()

        if user is not None:
            if username and getattr(user, username_field) != username:
                raise CommandError(
                    "The configured username does not match the existing admin account."
                )
            if user.email and user.email.casefold() != email.casefold():
                raise CommandError(
                    "The configured email does not match the existing admin account."
                )
        else:
            if not password:
                raise CommandError("DJANGO_SUPERUSER_PASSWORD is required to create the admin.")
            user_data = {username_field: username, "email": email}
            for field in user_model.REQUIRED_FIELDS:
                if field in user_data or field == "password":
                    continue
                value = os.getenv(f"DJANGO_SUPERUSER_{field.upper()}")
                if value is None:
                    raise CommandError(
                        f"DJANGO_SUPERUSER_{field.upper()} is required for this user model."
                    )
                user_data[field] = value
            user = user_model(**user_data)
            user.set_password(password)

        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        if os.getenv("DJANGO_SUPERUSER_UPDATE_PASSWORD", "").lower() in {
            "1",
            "true",
            "yes",
        }:
            if not password:
                raise CommandError(
                    "DJANGO_SUPERUSER_PASSWORD is required when password updates are enabled."
                )
            user.set_password(password)
        user.save()

        profile, _ = Profile.objects.get_or_create(user=user)
        if profile.role != UserRole.SUPER_ADMIN:
            profile.role = UserRole.SUPER_ADMIN
            profile.save(update_fields=["role", "updated_at"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Production admin ready: {user.email or getattr(user, username_field)}"
            )
        )