"""Company knowledge layer for the Orientiq AI assistant.

Sources (in priority order):
1. Published CMS/database content (Service, Industry, Product, Technology, Testimonial)
2. Approved static website data (core/data.py)
3. Safe static company information
"""

from core.data import (
    PRODUCTS,
    SERVICES,
    INDUSTRIES,
    PORTFOLIO_ITEMS,
    TECHNOLOGIES,
)
from core.models import (
    Product as ProductModel,
    Service as ServiceModel,
    Industry as IndustryModel,
    Technology as TechnologyModel,
    Testimonial as TestimonialModel,
)


def _published_cms_services():
    """Return published services from the CMS if present."""
    items = ServiceModel.objects.filter(status="published").order_by("display_order")
    return [
        {
            "title": s.title,
            "category": s.category,
            "short_description": s.short_description,
            "description": s.description,
        }
        for s in items
    ]


def _published_cms_industries():
    items = IndustryModel.objects.filter(status="published").order_by("display_order")
    return [
        {
            "name": i.name,
            "description": i.description,
        }
        for i in items
    ]


def _published_cms_products():
    items = ProductModel.objects.filter(status="published").order_by("display_order")
    return [
        {
            "name": p.name,
            "category": p.category,
            "status": p.product_status,
            "description": p.description,
        }
        for p in items
    ]


def _published_cms_technologies():
    items = TechnologyModel.objects.filter(active=True).order_by("display_order")
    return [
        {
            "name": t.name,
            "category": t.get_category_display(),
        }
        for t in items
    ]


def _published_cms_testimonials():
    items = TestimonialModel.objects.filter(status="published").order_by("display_order")
    return [
        {
            "client_name": t.client_name,
            "company": t.company,
            "testimonial": t.testimonial,
        }
        for t in items[:3]
    ]


def build_company_context():
    """Build the complete knowledge context for the AI assistant.

    Prefers published CMS content when available, then falls back to the
    approved static data in core/data.py.
    """
    services = _published_cms_services() or [
        {"title": s["name"], "category": s["tagline"], "short_description": s["short"], "description": ""}
        for s in SERVICES
    ]

    industries = _published_cms_industries() or [
        {"name": i["name"], "description": i["short"]}
        for i in INDUSTRIES
    ]

    products = _published_cms_products() or [
        {"name": p["name"], "category": p["category"], "status": p["status_label"], "description": p["description"]}
        for p in PRODUCTS
    ]

    technologies = _published_cms_technologies() or [
        {"name": t, "category": cat["category"]}
        for cat in TECHNOLOGIES
        for t in cat["items"]
    ]

    testimonials = _published_cms_testimonials()

    portfolio = [
        {
            "title": p["title"],
            "industry": p["industry"],
            "summary": p["summary"],
        }
        for p in PORTFOLIO_ITEMS[:5]
    ]

    return {
        "company": {
            "name": "Orientiq",
            "description": (
                "Orientiq is a premium technology and digital solutions company. "
                "We build AI-powered digital products, intelligent platforms, and "
                "scalable technology solutions for ambitious businesses worldwide."
            ),
            "mission": "To empower ambitious businesses with intelligent technology that delivers measurable results.",
            "vision": "To be the most trusted technology partner for global enterprises and startups alike.",
            "values": [
                "Excellence",
                "Transparency",
                "Innovation",
                "Partnership",
                "Impact",
                "Craft",
            ],
            "urls": {
                "about": "/about/",
                "process": "/company/process/",
                "careers": "/company/careers/",
                "contact": "/company/contact/",
                "start_project": "/start-project/",
                "services": "/services/",
                "industries": "/industries/",
                "portfolio": "/portfolio/",
                "products": "/products/",
                "technologies": "/technologies/",
            },
        },
        "services": services,
        "industries": industries,
        "products": products,
        "technologies": technologies,
        "testimonials": testimonials,
        "portfolio": portfolio,
        "start_project": {
            "description": (
                "Visitors can submit a project inquiry through the Start a Project "
                "form, which includes name, company, email, phone, project type, "
                "budget range, timeline, and message. Responses are typically "
                "provided within one business day."
            ),
            "url": "/start-project/",
        },
    }