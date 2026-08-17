"""Admin dashboard + CMS views for the Orientiq corporate website."""

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CustomPasswordChangeForm
from .models import (
    ActivityLog,
    Booking,
    BookingStatus,
    BookingType,
    ContactInquiry,
    Industry,
    MediaAsset,
    PortfolioProject,
    Product,
    Service,
    SiteSetting,
    Technology,
    Testimonial,
    UserRole,
)
from .permissions import is_admin, is_super_admin, require_admin, require_super_admin


def _log(user, action, obj_type="", obj_id=None, description="", request=None):
    """Create an activity log entry."""
    ActivityLog.objects.create(
        user=user,
        action=action,
        object_type=obj_type,
        object_id=obj_id,
        description=description,
        ip_address=request.META.get("REMOTE_ADDR") if request else None,
    )


def _paginate(request, queryset, per_page=20):
    paginator = Paginator(queryset, per_page)
    page = request.GET.get("page")
    return paginator.get_page(page)


# ============================================================
# AUTH
# ============================================================

@login_required
def admin_profile(request):
    """View admin profile."""
    require_admin(request.user)
    return render(request, "admin/profile.html")


@login_required
def admin_change_password(request):
    """Change admin password."""
    require_admin(request.user)
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            _log(request.user, "change_password", "User", user.id, "Changed own password", request)
            messages.success(request, "Your password has been changed.")
            return redirect("admin_profile")
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, "admin/change_password.html", {"form": form})


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def dashboard(request):
    """Admin dashboard with real database statistics."""
    require_admin(request.user)
    context = {
        "total_services": Service.objects.count(),
        "total_industries": Industry.objects.count(),
        "total_portfolio": PortfolioProject.objects.count(),
        "total_products": Product.objects.count(),
        "total_technologies": Technology.objects.count(),
        "total_testimonials": Testimonial.objects.count(),
        "new_inquiries": ContactInquiry.objects.filter(status="new").count(),
        "total_users": User.objects.count(),
        "recent_inquiries": ContactInquiry.objects.all()[:5],
        "recent_activity": ActivityLog.objects.all()[:10],
        "recent_services": Service.objects.all()[:5],
        "recent_products": Product.objects.all()[:5],
        "product_status_counts": Product.objects.values("product_status").annotate(count=Count("id")),
    }
    return render(request, "admin/dashboard.html", context)


# ============================================================
# SERVICES CMS
# ============================================================

@login_required
def service_list(request):
    require_admin(request.user)
    qs = Service.objects.all()
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(category__icontains=q))
    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)
    return render(request, "admin/services/list.html", {"items": _paginate(request, qs)})


@login_required
def service_create(request):
    require_admin(request.user)
    if request.method == "POST":
        title = request.POST.get("title")
        slug = request.POST.get("slug")
        if title and slug:
            obj = Service.objects.create(
                title=title,
                slug=slug,
                category=request.POST.get("category", ""),
                short_description=request.POST.get("short_description", ""),
                description=request.POST.get("description", ""),
                icon=request.POST.get("icon", ""),
                status=request.POST.get("status", "draft"),
                featured=request.POST.get("featured") == "on",
                display_order=int(request.POST.get("display_order", 0) or 0),
            )
            _log(request.user, "create", "Service", obj.id, f"Created service: {obj.title}", request)
            messages.success(request, "Service created.")
            return redirect("admin_service_edit", obj.id)
    return render(request, "admin/services/form.html", {"item": None})


@login_required
def service_edit(request, pk):
    require_admin(request.user)
    obj = get_object_or_404(Service, pk=pk)
    if request.method == "POST":
        obj.title = request.POST.get("title", obj.title)
        obj.slug = request.POST.get("slug", obj.slug)
        obj.category = request.POST.get("category", "")
        obj.short_description = request.POST.get("short_description", "")
        obj.description = request.POST.get("description", "")
        obj.icon = request.POST.get("icon", "")
        obj.status = request.POST.get("status", "draft")
        obj.featured = request.POST.get("featured") == "on"
        obj.display_order = int(request.POST.get("display_order", 0) or 0)
        obj.save()
        _log(request.user, "update", "Service", obj.id, f"Updated service: {obj.title}", request)
        messages.success(request, "Service updated.")
        return redirect("admin_service_edit", obj.id)
    return render(request, "admin/services/form.html", {"item": obj})


@login_required
def service_delete(request, pk):
    require_admin(request.user)
    obj = get_object_or_404(Service, pk=pk)
    _log(request.user, "delete", "Service", obj.id, f"Deleted service: {obj.title}", request)
    obj.delete()
    messages.success(request, "Service deleted.")
    return redirect("admin_service_list")


# ============================================================
# INDUSTRIES CMS
# ============================================================

@login_required
def industry_list(request):
    require_admin(request.user)
    qs = Industry.objects.all()
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    return render(request, "admin/industries/list.html", {"items": _paginate(request, qs)})


@login_required
def industry_create(request):
    require_admin(request.user)
    if request.method == "POST":
        name = request.POST.get("name")
        slug = request.POST.get("slug")
        if name and slug:
            obj = Industry.objects.create(
                name=name,
                slug=slug,
                description=request.POST.get("description", ""),
                icon=request.POST.get("icon", ""),
                status=request.POST.get("status", "draft"),
                featured=request.POST.get("featured") == "on",
                display_order=int(request.POST.get("display_order", 0) or 0),
            )
            _log(request.user, "create", "Industry", obj.id, f"Created industry: {obj.name}", request)
            messages.success(request, "Industry created.")
            return redirect("admin_industry_edit", obj.id)
    return render(request, "admin/industries/form.html", {"item": None})


@login_required
def industry_edit(request, pk):
    require_admin(request.user)
    obj = get_object_or_404(Industry, pk=pk)
    if request.method == "POST":
        obj.name = request.POST.get("name", obj.name)
        obj.slug = request.POST.get("slug", obj.slug)
        obj.description = request.POST.get("description", "")
        obj.icon = request.POST.get("icon", "")
        obj.status = request.POST.get("status", "draft")
        obj.featured = request.POST.get("featured") == "on"
        obj.display_order = int(request.POST.get("display_order", 0) or 0)
        obj.save()
        _log(request.user, "update", "Industry", obj.id, f"Updated industry: {obj.name}", request)
        messages.success(request, "Industry updated.")
        return redirect("admin_industry_edit", obj.id)
    return render(request, "admin/industries/form.html", {"item": obj})


@login_required
def industry_delete(request, pk):
    require_admin(request.user)
    obj = get_object_or_404(Industry, pk=pk)
    _log(request.user, "delete", "Industry", obj.id, f"Deleted industry: {obj.name}", request)
    obj.delete()
    messages.success(request, "Industry deleted.")
    return redirect("admin_industry_list")


# ============================================================
# PORTFOLIO CMS
# ============================================================

@login_required
def portfolio_list(request):
    require_admin(request.user)
    qs = PortfolioProject.objects.all()
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(industry__icontains=q))
    return render(request, "admin/portfolio/list.html", {"items": _paginate(request, qs)})


@login_required
def portfolio_create(request):
    require_admin(request.user)
    if request.method == "POST":
        title = request.POST.get("title")
        slug = request.POST.get("slug")
        if title and slug:
            obj = PortfolioProject.objects.create(
                title=title,
                slug=slug,
                client_name=request.POST.get("client_name", ""),
                category=request.POST.get("category", ""),
                industry=request.POST.get("industry", ""),
                short_description=request.POST.get("short_description", ""),
                description=request.POST.get("description", ""),
                challenge=request.POST.get("challenge", ""),
                solution=request.POST.get("solution", ""),
                status=request.POST.get("status", "draft"),
                featured=request.POST.get("featured") == "on",
                display_order=int(request.POST.get("display_order", 0) or 0),
            )
            _log(request.user, "create", "Portfolio", obj.id, f"Created portfolio: {obj.title}", request)
            messages.success(request, "Portfolio project created.")
            return redirect("admin_portfolio_edit", obj.id)
    return render(request, "admin/portfolio/form.html", {"item": None})


@login_required
def portfolio_edit(request, pk):
    require_admin(request.user)
    obj = get_object_or_404(PortfolioProject, pk=pk)
    if request.method == "POST":
        obj.title = request.POST.get("title", obj.title)
        obj.slug = request.POST.get("slug", obj.slug)
        obj.client_name = request.POST.get("client_name", "")
        obj.category = request.POST.get("category", "")
        obj.industry = request.POST.get("industry", "")
        obj.short_description = request.POST.get("short_description", "")
        obj.description = request.POST.get("description", "")
        obj.challenge = request.POST.get("challenge", "")
        obj.solution = request.POST.get("solution", "")
        obj.status = request.POST.get("status", "draft")
        obj.featured = request.POST.get("featured") == "on"
        obj.display_order = int(request.POST.get("display_order", 0) or 0)
        obj.save()
        _log(request.user, "update", "Portfolio", obj.id, f"Updated portfolio: {obj.title}", request)
        messages.success(request, "Portfolio project updated.")
        return redirect("admin_portfolio_edit", obj.id)
    return render(request, "admin/portfolio/form.html", {"item": obj})


@login_required
def portfolio_delete(request, pk):
    require_admin(request.user)
    obj = get_object_or_404(PortfolioProject, pk=pk)
    _log(request.user, "delete", "Portfolio", obj.id, f"Deleted portfolio: {obj.title}", request)
    obj.delete()
    messages.success(request, "Portfolio project deleted.")
    return redirect("admin_portfolio_list")


# ============================================================
# PRODUCTS CMS
# ============================================================

@login_required
def product_list(request):
    require_admin(request.user)
    qs = Product.objects.all()
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(category__icontains=q))
    status = request.GET.get("status")
    if status:
        qs = qs.filter(product_status=status)
    return render(request, "admin/products/list.html", {"items": _paginate(request, qs)})


@login_required
def product_create(request):
    require_admin(request.user)
    if request.method == "POST":
        name = request.POST.get("name")
        slug = request.POST.get("slug")
        if name and slug:
            obj = Product.objects.create(
                name=name,
                slug=slug,
                category=request.POST.get("category", ""),
                icon=request.POST.get("icon", ""),
                description=request.POST.get("description", ""),
                vision=request.POST.get("vision", ""),
                product_status=request.POST.get("product_status", "coming_soon"),
                website_url=request.POST.get("website_url", ""),
                internal_url=request.POST.get("internal_url", ""),
                external_url=request.POST.get("external_url", ""),
                status=request.POST.get("status", "draft"),
                featured=request.POST.get("featured") == "on",
                display_order=int(request.POST.get("display_order", 0) or 0),
            )
            _log(request.user, "create", "Product", obj.id, f"Created product: {obj.name}", request)
            messages.success(request, "Product created.")
            return redirect("admin_product_edit", obj.id)
    return render(request, "admin/products/form.html", {"item": None})


@login_required
def product_edit(request, pk):
    require_admin(request.user)
    obj = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        obj.name = request.POST.get("name", obj.name)
        obj.slug = request.POST.get("slug", obj.slug)
        obj.category = request.POST.get("category", "")
        obj.icon = request.POST.get("icon", "")
        obj.description = request.POST.get("description", "")
        obj.vision = request.POST.get("vision", "")
        obj.product_status = request.POST.get("product_status", "coming_soon")
        obj.website_url = request.POST.get("website_url", "")
        obj.internal_url = request.POST.get("internal_url", "")
        obj.external_url = request.POST.get("external_url", "")
        obj.status = request.POST.get("status", "draft")
        obj.featured = request.POST.get("featured") == "on"
        obj.display_order = int(request.POST.get("display_order", 0) or 0)
        obj.save()
        _log(request.user, "update", "Product", obj.id, f"Updated product: {obj.name}", request)
        messages.success(request, "Product updated.")
        return redirect("admin_product_edit", obj.id)
    return render(request, "admin/products/form.html", {"item": obj})


@login_required
def product_delete(request, pk):
    require_admin(request.user)
    obj = get_object_or_404(Product, pk=pk)
    _log(request.user, "delete", "Product", obj.id, f"Deleted product: {obj.name}", request)
    obj.delete()
    messages.success(request, "Product deleted.")
    return redirect("admin_product_list")


# ============================================================
# TECHNOLOGIES CMS
# ============================================================

@login_required
def technology_list(request):
    require_admin(request.user)
    qs = Technology.objects.all()
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(category__icontains=q))
    return render(request, "admin/technologies/list.html", {"items": _paginate(request, qs)})


@login_required
def technology_create(request):
    require_admin(request.user)
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            obj = Technology.objects.create(
                name=name,
                category=request.POST.get("category", "other"),
                description=request.POST.get("description", ""),
                icon=request.POST.get("icon", ""),
                website_url=request.POST.get("website_url", ""),
                active=request.POST.get("active") == "on",
                display_order=int(request.POST.get("display_order", 0) or 0),
            )
            _log(request.user, "create", "Technology", obj.id, f"Created technology: {obj.name}", request)
            messages.success(request, "Technology created.")
            return redirect("admin_technology_edit", obj.id)
    return render(request, "admin/technologies/form.html", {"item": None})


@login_required
def technology_edit(request, pk):
    require_admin(request.user)
    obj = get_object_or_404(Technology, pk=pk)
    if request.method == "POST":
        obj.name = request.POST.get("name", obj.name)
        obj.category = request.POST.get("category", "other")
        obj.description = request.POST.get("description", "")
        obj.icon = request.POST.get("icon", "")
        obj.website_url = request.POST.get("website_url", "")
        obj.active = request.POST.get("active") == "on"
        obj.display_order = int(request.POST.get("display_order", 0) or 0)
        obj.save()
        _log(request.user, "update", "Technology", obj.id, f"Updated technology: {obj.name}", request)
        messages.success(request, "Technology updated.")
        return redirect("admin_technology_edit", obj.id)
    return render(request, "admin/technologies/form.html", {"item": obj})


@login_required
def technology_delete(request, pk):
    require_admin(request.user)
    obj = get_object_or_404(Technology, pk=pk)
    _log(request.user, "delete", "Technology", obj.id, f"Deleted technology: {obj.name}", request)
    obj.delete()
    messages.success(request, "Technology deleted.")
    return redirect("admin_technology_list")


# ============================================================
# TESTIMONIALS CMS
# ============================================================

@login_required
def testimonial_list(request):
    require_admin(request.user)
    qs = Testimonial.objects.all()
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(client_name__icontains=q) | Q(company__icontains=q))
    return render(request, "admin/testimonials/list.html", {"items": _paginate(request, qs)})


@login_required
def testimonial_create(request):
    require_admin(request.user)
    if request.method == "POST":
        client_name = request.POST.get("client_name")
        if client_name:
            obj = Testimonial.objects.create(
                client_name=client_name,
                company=request.POST.get("company", ""),
                designation=request.POST.get("designation", ""),
                testimonial=request.POST.get("testimonial", ""),
                rating=int(request.POST.get("rating", 5) or 5),
                status=request.POST.get("status", "draft"),
                featured=request.POST.get("featured") == "on",
                display_order=int(request.POST.get("display_order", 0) or 0),
            )
            _log(request.user, "create", "Testimonial", obj.id, f"Created testimonial: {obj.client_name}", request)
            messages.success(request, "Testimonial created.")
            return redirect("admin_testimonial_edit", obj.id)
    return render(request, "admin/testimonials/form.html", {"item": None})


@login_required
def testimonial_edit(request, pk):
    require_admin(request.user)
    obj = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        obj.client_name = request.POST.get("client_name", obj.client_name)
        obj.company = request.POST.get("company", "")
        obj.designation = request.POST.get("designation", "")
        obj.testimonial = request.POST.get("testimonial", "")
        obj.rating = int(request.POST.get("rating", 5) or 5)
        obj.status = request.POST.get("status", "draft")
        obj.featured = request.POST.get("featured") == "on"
        obj.display_order = int(request.POST.get("display_order", 0) or 0)
        obj.save()
        _log(request.user, "update", "Testimonial", obj.id, f"Updated testimonial: {obj.client_name}", request)
        messages.success(request, "Testimonial updated.")
        return redirect("admin_testimonial_edit", obj.id)
    return render(request, "admin/testimonials/form.html", {"item": obj})


@login_required
def testimonial_delete(request, pk):
    require_admin(request.user)
    obj = get_object_or_404(Testimonial, pk=pk)
    _log(request.user, "delete", "Testimonial", obj.id, f"Deleted testimonial: {obj.client_name}", request)
    obj.delete()
    messages.success(request, "Testimonial deleted.")
    return redirect("admin_testimonial_list")


# ============================================================
# INQUIRIES
# ============================================================

@login_required
def inquiry_list(request):
    require_admin(request.user)
    all_qs = ContactInquiry.objects.all()
    qs = all_qs
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(email__icontains=q) | Q(company__icontains=q))
    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)

    status_summary = [
        {
            "value": value,
            "label": label,
            "count": all_qs.filter(status=value).count(),
        }
        for value, label in ContactInquiry.STATUS_CHOICES
    ]

    return render(
        request,
        "admin/inquiries/list.html",
        {
            "items": _paginate(request, qs),
            "status_choices": ContactInquiry.STATUS_CHOICES,
            "status_summary": status_summary,
            "status_total": all_qs.count(),
            "active_status": status or "all",
            "search_query": q or "",
        },
    )


@login_required
def inquiry_detail(request, pk):
    require_admin(request.user)
    obj = get_object_or_404(ContactInquiry, pk=pk)
    if request.method == "POST":
        obj.status = request.POST.get("status", obj.status)
        obj.admin_notes = request.POST.get("admin_notes", "")
        obj.save()
        _log(request.user, "update", "Inquiry", obj.id, f"Updated inquiry from {obj.name}", request)
        messages.success(request, "Inquiry updated.")
        return redirect("admin_inquiry_detail", obj.id)
    return render(request, "admin/inquiries/detail.html", {"item": obj})


# ============================================================
# USER MANAGEMENT
# ============================================================

@login_required
def user_list(request):
    require_admin(request.user)
    qs = User.objects.select_related("profile").order_by("-date_joined")
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(email__icontains=q) | Q(first_name__icontains=q))
    return render(request, "admin/users/list.html", {"items": _paginate(request, qs)})


@login_required
def user_edit(request, pk):
    require_admin(request.user)
    user = get_object_or_404(User, pk=pk)
    profile = getattr(user, "profile", None)
    if profile is None:
        from .models import Profile
        profile = Profile.objects.create(user=user)

    # Only super admin can change roles; admins cannot modify super admins.
    if profile.is_super_admin and not is_super_admin(request.user):
        messages.error(request, "You cannot modify a super admin.")
        return redirect("admin_user_list")

    if request.method == "POST":
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.is_active = request.POST.get("is_active") == "on"
        user.save()

        if is_super_admin(request.user):
            new_role = request.POST.get("role", profile.role)
            if user != request.user or new_role == UserRole.SUPER_ADMIN:
                profile.role = new_role
                profile.save()

        _log(request.user, "update", "User", user.id, f"Updated user: {user.username}", request)
        messages.success(request, "User updated.")
        return redirect("admin_user_list")

    return render(request, "admin/users/form.html", {"item": user, "profile": profile})


# ============================================================
# MEDIA MANAGEMENT
# ============================================================

@login_required
def media_list(request):
    require_admin(request.user)
    qs = MediaAsset.objects.all()
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(category__icontains=q))
    return render(request, "admin/media/list.html", {"items": _paginate(request, qs)})


@login_required
def media_upload(request):
    require_admin(request.user)
    if request.method == "POST":
        file = request.FILES.get("file")
        name = request.POST.get("name", "")
        category = request.POST.get("category", "general")
        alt_text = request.POST.get("alt_text", "")
        if file:
            obj = MediaAsset.objects.create(
                file=file,
                name=name or file.name,
                category=category,
                alt_text=alt_text,
                uploaded_by=request.user,
            )
            _log(request.user, "upload", "Media", obj.id, f"Uploaded media: {obj.name}", request)
            messages.success(request, "Media uploaded.")
            return redirect("admin_media_list")
    return render(request, "admin/media/upload.html")


@login_required
def media_delete(request, pk):
    require_admin(request.user)
    obj = get_object_or_404(MediaAsset, pk=pk)
    _log(request.user, "delete", "Media", obj.id, f"Deleted media: {obj.name}", request)
    obj.file.delete(save=False)
    obj.delete()
    messages.success(request, "Media deleted.")
    return redirect("admin_media_list")


# ============================================================
# WEBSITE SETTINGS
# ============================================================

@login_required
def settings_view(request):
    require_super_admin(request.user)
    settings = SiteSetting.get_singleton()
    if request.method == "POST":
        settings.company_name = request.POST.get("company_name", settings.company_name)
        settings.tagline = request.POST.get("tagline", "")
        settings.email = request.POST.get("email", "")
        settings.phone = request.POST.get("phone", "")
        settings.address = request.POST.get("address", "")
        settings.linkedin = request.POST.get("linkedin", "")
        settings.instagram = request.POST.get("instagram", "")
        settings.youtube = request.POST.get("youtube", "")
        settings.x = request.POST.get("x", "")
        settings.site_title = request.POST.get("site_title", "")
        settings.meta_description = request.POST.get("meta_description", "")
        settings.save()
        _log(request.user, "update", "Settings", 1, "Updated website settings", request)
        messages.success(request, "Settings updated.")
        return redirect("admin_settings")
    return render(request, "admin/settings/form.html", {"settings": settings})


# ============================================================
# ACTIVITY LOG
# ============================================================

@login_required
def activity_list(request):
    require_super_admin(request.user)
    qs = ActivityLog.objects.select_related("user").all()
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(description__icontains=q) | Q(action__icontains=q) | Q(object_type__icontains=q))
    return render(request, "admin/activity/list.html", {"items": _paginate(request, qs)})


# ============================================================
# BOOKINGS ADMIN
# ============================================================

@login_required
def booking_list(request):
    """Admin booking management — search, filter, paginate."""
    require_admin(request.user)
    qs = Booking.objects.select_related("user").prefetch_related("items").all()

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(booking_reference__icontains=q)

    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)

    booking_type = request.GET.get("booking_type")
    if booking_type:
        qs = qs.filter(booking_type=booking_type)

    items = _paginate(request, qs)
    return render(
        request,
        "admin/bookings/list.html",
        {
            "items": items,
            "status_choices": BookingStatus.choices,
            "booking_type_choices": BookingType.choices,
        },
    )


@login_required
def booking_detail(request, reference):
    """Admin booking detail — full but non-sensitive booking view."""
    require_admin(request.user)
    booking = get_object_or_404(
        Booking.objects.select_related("user").prefetch_related("items", "travelers"),
        booking_reference=reference,
    )
    items = booking.items.all()
    travelers = booking.travelers.all()
    return render(
        request,
        "admin/bookings/detail.html",
        {"booking": booking, "items": items, "travelers": travelers},
    )
