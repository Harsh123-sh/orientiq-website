import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from core.models import Profile, UserRole


class Command(BaseCommand):
    help = "Create or repair the production Superadmin account."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip().lower()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "")

        if not username:
            raise CommandError("DJANGO_SUPERUSER_USERNAME is not configured.")

        if not email:
            raise CommandError("DJANGO_SUPERUSER_EMAIL is not configured.")

        if not password:
            raise CommandError("DJANGO_SUPERUSER_PASSWORD is not configured.")

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email},
        )

        user.email = email
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = UserRole.SUPER_ADMIN
        profile.save(update_fields=["role"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Superadmin '{user.username}' "
                f"{'created' if created else 'updated'} successfully."
            )
        )

        self.stdout.write(
            f"  is_active={user.is_active}"
        )
        self.stdout.write(
            f"  is_staff={user.is_staff}"
        )
        self.stdout.write(
            f"  is_superuser={user.is_superuser}"
        )
        self.stdout.write(
            f"  profile_role={profile.role}"
        )