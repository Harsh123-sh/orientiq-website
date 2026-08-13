"""Custom authentication backends for Orientiq."""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameModelBackend(ModelBackend):
    """Authenticate users by username OR email address.

    - If the identifier matches an existing email (case-insensitive),
      the corresponding User is resolved and the password is verified.
    - Otherwise the identifier is treated as a username.
    - Passwords are always verified via Django's hashing system.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return None

        identifier = username.strip()

        # Try matching by email first (case-insensitive), falling back to username.
        try:
            user = UserModel.objects.get(email__iexact=identifier)
        except UserModel.DoesNotExist:
            try:
                user = UserModel.objects.get(username=identifier)
            except UserModel.DoesNotExist:
                # Run the password hasher regardless to reduce timing differences
                # between "user exists" and "user does not exist" responses.
                UserModel().set_password(password)
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None