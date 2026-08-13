import unicodedata

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(UserCreationForm):
    """User registration form with profile fields."""

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@company.com"}),
    )
    phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+1 555 000 0000"}),
    )
    company = forms.CharField(
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Company name"}),
    )
    country = forms.CharField(
        max_length=80,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Country"}),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirm password"}
        )

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                phone=self.cleaned_data.get("phone", ""),
                company=self.cleaned_data.get("company", ""),
                country=self.cleaned_data.get("country", ""),
            )
        return user


class LoginForm(AuthenticationForm):
    """Login form styled with the Orientiq design system."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username or email"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
    )


class ProfileForm(forms.ModelForm):
    """Edit profile information."""

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@company.com"}),
    )

    class Meta:
        model = Profile
        fields = ["phone", "company", "country", "timezone", "profile_image"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+1 555 000 0000"}),
            "company": forms.TextInput(attrs={"class": "form-control", "placeholder": "Company name"}),
            "country": forms.TextInput(attrs={"class": "form-control", "placeholder": "Country"}),
            "timezone": forms.Select(attrs={"class": "form-control"}),
            "profile_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields["first_name"].initial = self.user.first_name
            self.fields["last_name"].initial = self.user.last_name
            self.fields["email"].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data["first_name"]
            self.user.last_name = self.cleaned_data["last_name"]
            self.user.email = self.cleaned_data["email"]
            if commit:
                self.user.save()
                profile.save()
        return profile


class CustomPasswordChangeForm(PasswordChangeForm):
    """Password change form styled for Orientiq."""

    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Current password"}),
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "New password"}),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm new password"}),
    )


class CustomPasswordResetForm(PasswordResetForm):
    """Password reset form styled for Orientiq."""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@company.com"}),
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Set new password form styled for Orientiq."""

    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "New password"}),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm new password"}),
    )


# ============================================================
# BOOKING FORMS (PHASE 9)
# ============================================================

def _normalize_name(value, field_label):
    """Normalize human names without changing their intended capitalization."""
    normalized = " ".join(unicodedata.normalize("NFKC", value or "").split())
    if not any(char.isalpha() for char in normalized):
        raise forms.ValidationError(f"{field_label} must contain letters.")
    return normalized


def _normalize_phone(value):
    """Accept common phone formatting, reject letters and implausible numbers."""
    raw = unicodedata.normalize("NFKC", value or "").strip()
    if not raw:
        return ""
    if any(not (char.isdigit() or char in "+-(). ") for char in raw):
        raise forms.ValidationError("Enter a valid phone number.")
    if raw.count("+") > 1 or ("+" in raw and not raw.startswith("+")):
        raise forms.ValidationError("Enter a valid phone number.")

    digits = "".join(char for char in raw if char.isdigit())
    if not 7 <= len(digits) <= 15:
        raise forms.ValidationError("Enter a valid phone number.")
    return f"+{digits}" if raw.startswith("+") else digits


class BookingPersonForm(forms.Form):
    """Shared server-side normalization for booking travelers and guests."""

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean_phone(self):
        return _normalize_phone(self.cleaned_data["phone"])


class TravelerForm(BookingPersonForm):
    """Flight traveler details form (validated strictly server-side)."""

    first_name = forms.CharField(
        max_length=120,
        required=True,
        label="First name",
        error_messages={"required": "First name is required."},
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First name", "autocomplete": "given-name"}
        ),
    )
    last_name = forms.CharField(
        max_length=120,
        required=True,
        label="Last name",
        error_messages={"required": "Last name is required."},
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last name", "autocomplete": "family-name"}
        ),
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        label="Email",
        error_messages={"required": "Email is required.", "invalid": "Enter a valid email address."},
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "you@example.com", "autocomplete": "email"}
        ),
    )
    phone = forms.CharField(
        max_length=30,
        required=False,
        label="Phone",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+91 98765 43210"}),
    )
    nationality = forms.CharField(
        max_length=80,
        required=False,
        label="Nationality",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "India"}),
    )

    def clean_first_name(self):
        return _normalize_name(self.cleaned_data["first_name"], "First name")

    def clean_last_name(self):
        return _normalize_name(self.cleaned_data["last_name"], "Last name")

    def clean_nationality(self):
        return " ".join(unicodedata.normalize("NFKC", self.cleaned_data["nationality"] or "").split())


class GuestForm(BookingPersonForm):
    """Hotel guest / activity participant details form."""

    name = forms.CharField(
        max_length=120,
        required=True,
        label="Name",
        error_messages={"required": "Name is required."},
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Full name"}),
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        label="Email",
        error_messages={"required": "Email is required.", "invalid": "Enter a valid email address."},
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "you@example.com", "autocomplete": "email"}
        ),
    )
    phone = forms.CharField(
        max_length=30,
        required=True,
        label="Phone",
        error_messages={"required": "Phone is required."},
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+91 98765 43210"}),
    )

    def clean_name(self):
        return _normalize_name(self.cleaned_data["name"], "Name")


def build_booking_forms(item_type, quantity, data=None):
    """Return a list of person detail forms for the booking type.

    FLIGHT   -> TravelerForm (first/last name, email, phone, nationality)
    HOTEL    -> GuestForm    (name, email, phone)
    ACTIVITY -> GuestForm    (name, email, phone)

    Forms are prefixed `person_<i>` so many travellers/guests/participants
    can be validated independently server-side.
    """
    form_class = GuestForm if str(item_type) in ("hotel", "activity") else TravelerForm
    try:
        quantity = max(int(quantity or 1), 1)
    except (TypeError, ValueError):
        quantity = 1
    return [form_class(data=data, prefix=f"person_{i}") for i in range(quantity)]
