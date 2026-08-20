from django.conf import settings
from django.db import models


class UserRole(models.TextChoices):
    """User role foundation."""

    SUPER_ADMIN = "super_admin", "Super Admin"
    ADMIN = "admin", "Admin"
    CLIENT = "client", "Client"


class Profile(models.Model):
    """Extended user profile linked to Django's built-in User model."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CLIENT,
    )
    phone = models.CharField(max_length=30, blank=True)
    company = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=80, blank=True)
    timezone = models.CharField(max_length=80, blank=True, default="UTC")
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    theme_preference = models.CharField(
        max_length=10,
        choices=[("dark", "Dark"), ("light", "Light")],
        default="dark",
    )
    email_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    @property
    def is_super_admin(self):
        return self.role == UserRole.SUPER_ADMIN

    @property
    def is_admin(self):
        return self.role in (UserRole.SUPER_ADMIN, UserRole.ADMIN)

    @property
    def is_client(self):
        return self.role == UserRole.CLIENT


# ============================================================
# CMS MODELS
# ============================================================

class BaseContent(models.Model):
    """Abstract base for CMS content models."""

    status = models.CharField(
        max_length=20,
        choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")],
        default="draft",
    )
    featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["display_order", "-updated_at"]


class Service(BaseContent):
    """CMS-managed service."""

    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=80, blank=True)
    short_description = models.TextField(blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=40, blank=True)
    hero_image = models.ImageField(upload_to="services/", blank=True, null=True)
    features = models.JSONField(default=list, blank=True)
    benefits = models.JSONField(default=list, blank=True)
    technologies = models.JSONField(default=list, blank=True)
    process = models.JSONField(default=list, blank=True)
    faq = models.JSONField(default=list, blank=True)
    seo_title = models.CharField(max_length=160, blank=True)
    seo_description = models.TextField(blank=True)

    class Meta(BaseContent.Meta):
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.title


class Industry(BaseContent):
    """CMS-managed industry."""

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=40, blank=True)
    hero_image = models.ImageField(upload_to="industries/", blank=True, null=True)
    features = models.JSONField(default=list, blank=True)
    seo_title = models.CharField(max_length=160, blank=True)
    seo_description = models.TextField(blank=True)

    class Meta(BaseContent.Meta):
        verbose_name = "Industry"
        verbose_name_plural = "Industries"

    def __str__(self):
        return self.name


class PortfolioProject(BaseContent):
    """CMS-managed portfolio project."""

    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    client_name = models.CharField(max_length=120, blank=True)
    category = models.CharField(max_length=80, blank=True)
    industry = models.CharField(max_length=80, blank=True)
    short_description = models.TextField(blank=True)
    description = models.TextField(blank=True)
    challenge = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    results = models.JSONField(default=list, blank=True)
    technologies = models.JSONField(default=list, blank=True)
    hero_image = models.ImageField(upload_to="portfolio/", blank=True, null=True)
    gallery = models.JSONField(default=list, blank=True)
    project_url = models.URLField(blank=True)
    seo_title = models.CharField(max_length=160, blank=True)
    seo_description = models.TextField(blank=True)

    class Meta(BaseContent.Meta):
        verbose_name = "Portfolio Project"
        verbose_name_plural = "Portfolio Projects"

    def __str__(self):
        return self.title


class Product(BaseContent):
    """CMS-managed product (preserves Phase 4 ProductStatus)."""

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=80, blank=True)
    icon = models.CharField(max_length=40, blank=True)
    description = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    capabilities = models.JSONField(default=list, blank=True)
    technology_tags = models.JSONField(default=list, blank=True)
    product_status = models.CharField(
        max_length=20,
        choices=[
            ("coming_soon", "Coming Soon"),
            ("in_development", "In Development"),
            ("beta", "Beta"),
            ("live", "Live"),
            ("archived", "Archived"),
        ],
        default="coming_soon",
    )
    website_url = models.URLField(blank=True)
    internal_url = models.CharField(max_length=200, blank=True)
    external_url = models.URLField(blank=True)
    seo_title = models.CharField(max_length=160, blank=True)
    seo_description = models.TextField(blank=True)

    class Meta(BaseContent.Meta):
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

    @property
    def status_label(self):
        return dict(self._meta.get_field("product_status").choices).get(self.product_status, "")

    @property
    def cta_label(self):
        return {
            "coming_soon": "Explore Product",
            "in_development": "View Progress",
            "beta": "Try Beta",
            "live": "Open Product",
            "archived": "Learn More",
        }.get(self.product_status, "Explore Product")


class Technology(BaseContent):
    """CMS-managed technology."""

    name = models.CharField(max_length=80)
    category = models.CharField(
        max_length=40,
        choices=[
            ("frontend", "Frontend"),
            ("backend", "Backend"),
            ("database", "Database"),
            ("ai", "AI"),
            ("cloud", "Cloud"),
            ("devops", "DevOps"),
            ("mobile", "Mobile"),
            ("other", "Other"),
        ],
        default="other",
    )
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=40, blank=True)
    website_url = models.URLField(blank=True)
    active = models.BooleanField(default=True)

    class Meta(BaseContent.Meta):
        verbose_name = "Technology"
        verbose_name_plural = "Technologies"

    def __str__(self):
        return self.name


class Testimonial(BaseContent):
    """CMS-managed testimonial."""

    client_name = models.CharField(max_length=120)
    company = models.CharField(max_length=120, blank=True)
    designation = models.CharField(max_length=120, blank=True)
    photo = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    testimonial = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)

    class Meta(BaseContent.Meta):
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return self.client_name


class ContactInquiry(models.Model):
    """Project/contact inquiry from the public website."""

    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("in_discussion", "In Discussion"),
        ("proposal_sent", "Proposal Sent"),
        ("won", "Won"),
        ("lost", "Lost"),
        ("archived", "Archived"),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    company = models.CharField(max_length=120, blank=True)
    service = models.CharField(max_length=120, blank=True)
    budget = models.CharField(max_length=80, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.email}"


class MediaAsset(models.Model):
    """Media library asset."""

    CATEGORY_CHOICES = [
        ("logos", "Logos"),
        ("services", "Services"),
        ("industries", "Industries"),
        ("portfolio", "Portfolio"),
        ("products", "Products"),
        ("testimonials", "Testimonials"),
        ("general", "General"),
    ]

    file = models.FileField(upload_to="media/")
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default="general")
    alt_text = models.CharField(max_length=200, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Media Asset"
        verbose_name_plural = "Media Assets"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


# ============================================================
# BOOKING MODELS (PHASE 9)
# ============================================================


class BookingStatus(models.TextChoices):
    """Booking status foundation."""

    DRAFT = "draft", "Draft"
    PENDING = "pending", "Pending Confirmation"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"
    FAILED = "failed", "Failed"
    EXPIRED = "expired", "Expired"


class BookingType(models.TextChoices):
    """Booking type foundation."""

    FLIGHT = "flight", "Flight"
    HOTEL = "hotel", "Hotel"
    ACTIVITY = "activity", "Activity"
    MULTI = "multi", "Multi-Item"


class Booking(models.Model):
    """Core booking record."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="bookings",
        null=True,
        blank=True,
    )
    booking_reference = models.CharField(max_length=20, unique=True, db_index=True)
    status = models.CharField(
        max_length=20, choices=BookingStatus.choices, default=BookingStatus.DRAFT
    )
    booking_type = models.CharField(
        max_length=20, choices=BookingType.choices, default=BookingType.FLIGHT
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    taxes = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default="USD")
    is_demo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"], name="booking_user_created_idx"),
            models.Index(fields=["status", "-created_at"], name="booking_status_created_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(subtotal__gte=0),
                name="booking_subtotal_nonnegative",
            ),
            models.CheckConstraint(
                check=models.Q(taxes__gte=0),
                name="booking_taxes_nonnegative",
            ),
            models.CheckConstraint(
                check=models.Q(total__gte=0),
                name="booking_total_nonnegative",
            ),
        ]

    def __str__(self):
        return f"{self.booking_reference} ({self.get_booking_type_display()}) - {self.get_status_display()}"


class BookingItem(models.Model):
    """A single item within a booking (e.g., a flight, a hotel room, an activity)."""

    ITEM_TYPE_CHOICES = BookingType.choices # Reuse booking types for items

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="items"
    )
    item_type = models.CharField(
        max_length=20, choices=ITEM_TYPE_CHOICES, default=BookingType.FLIGHT
    )
    provider = models.CharField(max_length=80, blank=True)
    provider_reference = models.CharField(max_length=120, blank=True)
    title = models.CharField(max_length=255)
    route_or_destination = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Flight specific
    departure_time = models.CharField(max_length=10, blank=True)
    arrival_time = models.CharField(max_length=10, blank=True)
    duration = models.CharField(max_length=20, blank=True)
    stops = models.PositiveSmallIntegerField(null=True, blank=True)
    cabin_class = models.CharField(max_length=50, blank=True)

    # Hotel specific
    room_type = models.CharField(max_length=120, blank=True)
    amenities = models.JSONField(default=list, blank=True)
    cancellation_policy = models.CharField(max_length=255, blank=True)

    # Activity specific
    category = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    meeting_point = models.CharField(max_length=255, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    selection_key = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="Deterministic hash of the user's inventory selection, used to prevent duplicate confirmation.",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of the original normalized search result.",
    )

    class Meta:
        verbose_name = "Booking Item"
        verbose_name_plural = "Booking Items"
        indexes = [
            models.Index(fields=["booking", "item_type"], name="booking_item_type_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name="booking_item_price_nonnegative",
            ),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_item_type_display()}) for {self.booking.booking_reference}"


class Traveler(models.Model):
    """Traveler or guest information associated with a booking."""

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
        ("unspecified", "Prefer Not To Say"),
    ]

    TRAVELER_TYPE_CHOICES = [
        ("adult", "Adult"),
        ("child", "Child"),
        ("infant", "Infant"),
        ("guest", "Guest"), # For hotels and activities, general participant
    ]

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="travelers"
    )
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    nationality = models.CharField(max_length=80, blank=True)
    traveler_type = models.CharField(max_length=20, choices=TRAVELER_TYPE_CHOICES, default="adult")

    class Meta:
        verbose_name = "Traveler"
        verbose_name_plural = "Travelers"
        indexes = [
            models.Index(fields=["booking", "traveler_type"], name="traveler_booking_type_idx"),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_traveler_type_display()})"


class SiteSetting(models.Model):
    """Singleton website settings."""

    company_name = models.CharField(max_length=120, default="ORENTIQ")
    tagline = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    light_logo = models.ImageField(upload_to="brand/", blank=True, null=True)
    dark_logo = models.ImageField(upload_to="brand/", blank=True, null=True)
    favicon = models.ImageField(upload_to="brand/", blank=True, null=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    x = models.URLField(blank=True)
    site_title = models.CharField(max_length=160, blank=True)
    meta_description = models.TextField(blank=True)
    og_image = models.ImageField(upload_to="brand/", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_singleton(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ActivityLog(models.Model):
    """Audit log of admin actions."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=40)
    object_type = models.CharField(max_length=60, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action} — {self.object_type} ({self.timestamp:%Y-%m-%d %H:%M})"
