"""Company knowledge layer for the ORENTIQ AI assistant.

Sources (in priority order):
1. Published CMS/database content (Service, Industry, Product, Technology, Testimonial)
2. Approved static website data (core/data.py)
3. Safe static company information
"""

from core.data import (
    PRODUCTS,
    SERVICES,
    INDUSTRIES,
    TECHNOLOGIES,
)
from core.models import (
    Product as ProductModel,
    Service as ServiceModel,
    Industry as IndustryModel,
    PortfolioProject as PortfolioProjectModel,
    Technology as TechnologyModel,
    Testimonial as TestimonialModel,
    ChatbotFAQ,
)


def _published_cms_services():
    """Return published services from the CMS if present."""
    items = ServiceModel.objects.filter(status="published").order_by("display_order")
    return [
        {
            "title": s.title,
            "slug": s.slug,
            "category": s.category,
            "short_description": s.short_description,
            "description": s.description,
            "technologies": s.technologies,
            "faq": s.faq,
            "url": f"/services/{s.slug}/",
        }
        for s in items
    ]


def _published_cms_industries():
    items = IndustryModel.objects.filter(status="published").order_by("display_order")
    return [
        {
            "name": i.name,
            "slug": i.slug,
            "description": i.description,
            "url": f"/industries/{i.slug}/",
        }
        for i in items
    ]


def _published_cms_products():
    items = ProductModel.objects.filter(status="published").order_by("display_order")
    return [
        {
            "name": p.name,
            "slug": p.slug,
            "category": p.category,
            "status": p.status_label,
            "description": p.description,
            "vision": p.vision,
            "capabilities": p.capabilities,
            "url": f"/products/{p.slug}/",
        }
        for p in items
    ]


def _published_cms_portfolio():
    items = PortfolioProjectModel.objects.filter(status="published").order_by("display_order")
    return [
        {
            "title": item.title,
            "slug": item.slug,
            "category": item.category,
            "industry": item.industry,
            "summary": item.short_description,
            "description": item.description,
        }
        for item in items
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
        {
            "title": s["name"],
            "slug": s["slug"],
            "category": s["tagline"],
            "short_description": s["short"],
            "description": "",
            "url": f"/services/{s['slug']}/",
        }
        for s in SERVICES
    ]

    industries = _published_cms_industries() or [
        {
            "name": i["name"],
            "slug": i["slug"],
            "description": i["short"],
            "url": f"/industries/{i['slug']}/",
        }
        for i in INDUSTRIES
    ]

    products = _published_cms_products() or [
        {
            "name": p["name"],
            "slug": p["slug"],
            "category": p["category"],
            "status": p["status_label"],
            "description": p["description"],
            "vision": p.get("vision", ""),
            "capabilities": p.get("capabilities", []),
            "url": f"/products/{p['slug']}/",
        }
        for p in PRODUCTS
    ]

    portfolio = _published_cms_portfolio()

    technologies = _published_cms_technologies() or [
        {"name": t, "category": cat["category"]}
        for cat in TECHNOLOGIES
        for t in cat["items"]
    ]

    testimonials = _published_cms_testimonials()
    faqs = list(
        ChatbotFAQ.objects.filter(active=True)
        .order_by("display_order", "question")
        .values("question", "answer")[:100]
    )

    return {
        "company": {
            "name": "ORENTIQ",
            "tagline": "Innovate. Integrate. Inspire.",
            "description": "ORENTIQ is a premium technology and digital solutions company building intelligent products for ambitious businesses.",
            "founder": {
                "name": "Harsh Sachwani",
                "role": "Founder & Technology Lead",
                "url": "/company/founder/",
            },
            "logo_meaning": (
                "The J is the first letter of Jhulelal, a meaningful personal inspiration "
                "behind the logo. The S represents the founder's surname and the person "
                "behind the original mark. ORENTIQ is the chosen technology-focused brand name."
            ),
            "urls": {
                "about": "/about/",
                "founder": "/company/founder/",
                "process": "/company/process/",
                "careers": "/company/careers/",
                "contact": "/company/contact/",
                "start_project": "/start-project/",
                "services": "/services/",
                "industries": "/industries/",
                "products": "/products/",
                "technologies": "/technologies/",
            },
        },
        "services": services,
        "industries": industries,
        "products": products,
        "portfolio": portfolio,
        "technologies": technologies,
        "testimonials": testimonials,
        "faqs": faqs,
        "process": [
            {"name": "Discovery", "description": "Understand goals, users, and constraints through collaboration."},
            {"name": "Strategy", "description": "Define architecture, roadmap, and success metrics."},
            {"name": "Design", "description": "Create user-centered experiences aligned with the brand."},
            {"name": "Development", "description": "Build in transparent, testable increments with regular demos."},
            {"name": "Launch", "description": "Deploy with testing, monitoring, documentation, and knowledge transfer."},
            {"name": "Growth", "description": "Iterate and scale based on real data."},
        ],
        "contact": {
            "email": "orentiq.js.official@gmail.com",
            "phone": "+91 93283 73770",
            "phone_uri": "tel:+919328373770",
            "whatsapp_uri": "https://wa.me/919328373770",
            "website": "https://orentiq.me/",
            "response_time": "Within one business day",
            "initial_consultation": "Free initial consultation",
            "engagement_terms": "No obligation, no pressure",
            "nda": "NDA available on request",
        },
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