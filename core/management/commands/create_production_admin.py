import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Profile, UserRole


class Command(BaseCommand):
    help = "Create or repair the deployment super-admin account."

    def handle(self, *args, **options):
        user_model = get_user_model()
        username_field = user_model.USERNAME_FIELD
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip().lower()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if username_field == "username" and not username:
            raise CommandError("DJANGO_SUPERUSER_USERNAME is required for this user model.")
        if not password:
            raise CommandError("DJANGO_SUPERUSER_PASSWORD is required.")
        if username_field != "username" and not email:
            raise CommandError("DJANGO_SUPERUSER_EMAIL is required for this user model.")

        identifier = username or email
        user = user_model.objects.filter(**{username_field: identifier}).first()

        with transaction.atomic():
            if user is None:
                user_data = {username_field: identifier}
                if "email" in [field.name for field in user_model._meta.fields]:
                    user_data["email"] = email
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
            elif email and hasattr(user, "email"):
                user.email = email

            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            if profile.role != UserRole.SUPER_ADMIN:
                profile.role = UserRole.SUPER_ADMIN
                profile.save(update_fields=["role", "updated_at"])

        self.stdout.write(self.style.SUCCESS("Production admin ready."))
        self.stdout.write(f"Username/email: {user.email or getattr(user, username_field)}")
        self.stdout.write(f"is_active: {user.is_active}")
        self.stdout.write(f"is_staff: {user.is_staff}")
        self.stdout.write(f"is_superuser: {user.is_superuser}")
        self.stdout.write(f"Profile role: {profile.role.upper()}")