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

from .models import (
    CandidateApplication,
    ClientAccount,
    ClientDocument,
    ClientProject,
    Profile,
    ProjectUpdate,
)


class CandidateApplicationForm(forms.ModelForm):
    """Public future-opportunity form with conservative resume validation."""

    consent = forms.BooleanField(required=True, label="I agree to the privacy policy and future recruitment processing.", error_messages={"required": "Consent is required to submit your profile."})

    class Meta:
        model = CandidateApplication
        fields = ("full_name", "email", "phone", "location", "area_of_interest", "experience_level", "portfolio_url", "github_url", "resume", "introduction")
        widgets = {
            "full_name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel"}),
            "location": forms.TextInput(attrs={"autocomplete": "address-level2"}),
            "portfolio_url": forms.URLInput(attrs={"placeholder": "https://"}),
            "github_url": forms.URLInput(attrs={"placeholder": "https://github.com/"}),
            "resume": forms.ClearableFileInput(attrs={"accept": ".pdf,.doc,.docx"}),
            "introduction": forms.Textarea(attrs={"rows": 5, "maxlength": 1500}),
        }

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean_resume(self):
        resume = self.cleaned_data.get("resume")
        if not resume:
            return resume
        extension = resume.name.rsplit(".", 1)[-1].lower() if "." in resume.name else ""
        if extension not in {"pdf", "doc", "docx"}:
            raise forms.ValidationError("Upload a PDF, DOC, or DOCX resume.")
        allowed_types = {
            "application/pdf", "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        content_type = getattr(resume, "content_type", "")
        if content_type and content_type not in allowed_types:
            raise forms.ValidationError("The uploaded file type does not match a supported resume format.")
        if resume.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Your resume must be 5 MB or smaller.")
        return resume

    def save(self, commit=True):
        application = super().save(commit=False)
        from django.utils import timezone
        application.consented_at = timezone.now()
        if commit:
            application.save()
        return application


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
    """Login form styled with the Orentiq design system."""

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


class ClientAccountForm(forms.ModelForm):
    """Validated admin form for creating and editing a client account."""

    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField()

    class Meta:
        model = ClientAccount
        fields = ("first_name", "last_name", "email", "company", "phone", "business_address", "category", "internal_notes", "status")
        widgets = {
            "business_address": forms.Textarea(attrs={"rows": 3}),
            "internal_notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, user_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_instance = user_instance or (self.instance.user if self.instance.pk else None)
        if self.user_instance:
            self.fields["first_name"].initial = self.user_instance.first_name
            self.fields["last_name"].initial = self.user_instance.last_name
            self.fields["email"].initial = self.user_instance.email

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        query = User.objects.filter(email__iexact=email)
        if self.user_instance:
            query = query.exclude(pk=self.user_instance.pk)
        if query.exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class ClientProjectForm(forms.ModelForm):
    class Meta:
        model = ClientProject
        fields = ("name", "clients", "description", "category", "start_date", "expected_completion", "status", "progress", "admin_notes")
        widgets = {
            "clients": forms.SelectMultiple(attrs={"size": 5}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "admin_notes": forms.Textarea(attrs={"rows": 3}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "expected_completion": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_progress(self):
        progress = self.cleaned_data["progress"]
        if progress > 100:
            raise forms.ValidationError("Progress must be between 0 and 100.")
        return progress


class ClientDocumentForm(forms.ModelForm):
    class Meta:
        model = ClientDocument
        fields = ("title", "description", "category", "client", "project", "file", "version")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def clean_file(self):
        uploaded = self.cleaned_data["file"]
        extension = uploaded.name.rsplit(".", 1)[-1].lower() if "." in uploaded.name else ""
        if extension not in {"pdf", "doc", "docx", "xls", "xlsx", "png", "jpg", "jpeg"}:
            raise forms.ValidationError("Upload an approved document type.")
        if uploaded.size > 15 * 1024 * 1024:
            raise forms.ValidationError("Documents must be 15 MB or smaller.")
        if extension == "pdf":
            header = uploaded.read(5)
            uploaded.seek(0)
            if header != b"%PDF-":
                raise forms.ValidationError("The uploaded file is not a valid PDF.")
        return uploaded

    def clean(self):
        cleaned = super().clean()
        client = cleaned.get("client")
        project = cleaned.get("project")
        if client and project and not project.clients.filter(pk=client.pk).exists():
            self.add_error("project", "Select a project assigned to the selected client.")
        return cleaned


class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = ProjectUpdate
        fields = ("title", "body", "visible_to_client")
        widgets = {"body": forms.Textarea(attrs={"rows": 4})}


class CustomPasswordChangeForm(PasswordChangeForm):
    """Password change form styled for Orentiq."""

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
    """Password reset form styled for Orentiq."""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@company.com"}),
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Set new password form styled for Orentiq."""

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
