"""Role-based permission helpers for the Orientiq admin dashboard."""

from django.core.exceptions import PermissionDenied

from .models import Profile, UserRole


def get_user_role(user):
    """Return the user's role string, or None if no profile exists."""
    if not user.is_authenticated:
        return None
    profile = getattr(user, "profile", None)
    if profile is None:
        profile, _ = Profile.objects.get_or_create(user=user)
    return profile.role


def is_super_admin(user):
    return get_user_role(user) == UserRole.SUPER_ADMIN


def is_admin(user):
    role = get_user_role(user)
    return role in (UserRole.SUPER_ADMIN, UserRole.ADMIN)


def is_client(user):
    return get_user_role(user) == UserRole.CLIENT


def require_admin(user):
    """Raise PermissionDenied unless the user is an admin or super admin."""
    if not user.is_authenticated or not is_admin(user):
        raise PermissionDenied("You do not have permission to access the admin dashboard.")
    return True


def require_super_admin(user):
    """Raise PermissionDenied unless the user is a super admin."""
    if not user.is_authenticated or not is_super_admin(user):
        raise PermissionDenied("Only super admins can perform this action.")
    return True