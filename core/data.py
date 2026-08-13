"""Static content data for the Orientiq public website."""

SERVICES = [
    {
        "slug": "ai-automation",
        "name": "AI & Automation",
        "tagline": "Intelligent systems that work for you",
        "short": "Custom AI solutions and intelligent automation that transform business operations.",
        "icon": "ai",
        "features": [
            "Custom AI / ML models",
            "Intelligent document processing",
            "Workflow automation",
            "Predictive analytics",
            "Natural language processing",
        ],
        "problems": [
            "Manual processes limiting scale",
            "Data trapped in silos and documents",
            "Slow, error-prone decision making",
            "Customer service bottlenecks",
        ],
        "tech": ["Python", "TensorFlow", "PyTorch", "OpenAI", "LangChain", "PostgreSQL"],
        "benefits": [
            "Reduce operational costs by up to 40%",
            "Accelerate decision-making with real-time insights",
            "Scale operations without scaling headcount",
            "Improve accuracy and consistency",
        ],
        "use_cases": [
            "Automated document processing & extraction",
            "AI-powered customer support assistants",
            "Predictive maintenance for equipment",
            "Intelligent sales & demand forecasting",
        ],
        "faqs": [
            {
                "q": "How long does an AI project take?",
                "a": "Typical AI engagements range from 4–12 weeks for a focused solution to several months for enterprise-scale platforms.",
            },
            {
                "q": "Do we need existing data for AI?",
                "a": "We work with whatever data you have. Our team helps structure, clean, and prepare data as part of the process.",
            },
        ],
    },
    {
        "slug": "web-development",
        "name": "Web Development",
        "tagline": "Premium web platforms built to scale",
        "short": "High-performance web applications and platforms engineered for growth.",
        "icon": "web",
        "features": [
            "Custom web applications",
            "E-commerce platforms",
            "SaaS products",
            "Progressive web apps",
            "Headless CMS solutions",
        ],
        "problems": [
            "Outdated websites hurting conversions",
            "Slow page loads driving users away",
            "Systems that cannot scale with growth",
            "Poor mobile experience",
        ],
        "tech": ["Django", "Python", "PostgreSQL", "HTML5", "CSS3", "JavaScript"],
        "benefits": [
            "Lightning-fast page loads (< 2s)",
            "SEO-optimized, semantic architecture",
            "Mobile-first responsive experience",
            "Future-proof scalable codebase",
        ],
        "use_cases": [
            "Enterprise web platforms & portals",
            "High-conversion e-commerce stores",
            "SaaS dashboards & admin panels",
            "Marketing sites & brand experiences",
        ],
        "faqs": [
            {
                "q": "What technologies do you use?",
                "a": "We primarily build with Django and Python on the backend with clean HTML5, CSS3, and vanilla JavaScript on the frontend — keeping things fast and maintainable.",
            },
            {
                "q": "Can you redesign an existing site?",
                "a": "Yes. We regularly modernize legacy websites into fast, accessible, premium experiences without losing SEO equity.",
            },
        ],
    },
    {
        "slug": "mobile-development",
        "name": "Mobile Development",
        "tagline": "Native-quality mobile experiences",
        "short": "iOS and Android applications that feel effortless and perform beautifully.",
        "icon": "mobile",
        "features": [
            "iOS applications",
            "Android applications",
            "Cross-platform development",
            "Mobile UI/UX design",
            "App store submission",
        ],
        "problems": [
            "No mobile presence in a mobile-first world",
            "Clunky apps hurting brand perception",
            "Maintenance burden of separate codebases",
            "Poor app store discoverability",
        ],
        "tech": ["Flutter", "React Native", "Swift", "Kotlin", "Firebase", "REST APIs"],
        "benefits": [
            "Delightful, intuitive user experience",
            "Fast performance on all devices",
            "Single codebase for iOS & Android when appropriate",
            "Ongoing support & maintenance",
        ],
        "use_cases": [
            "Customer-facing mobile apps",
            "Field & staff productivity apps",
            "Mobile-first e-commerce",
            "IoT companion apps",
        ],
        "faqs": [
            {
                "q": "Do you build for both iOS and Android?",
                "a": "Yes. We normally recommend cross-platform for cost efficiency or native when performance demands it — based on your product needs.",
            },
            {
                "q": "How long does an app take?",
                "a": "A focused MVP typically ships in 8–16 weeks. Complex platforms can span 4–8 months depending on scope.",
            },
        ],
    },
    {
        "slug": "software-development",
        "name": "Software Development",
        "tagline": "Custom software for complex problems",
        "short": "Bespoke enterprise software engineered around your exact business needs.",
        "icon": "software",
        "features": [
            "Enterprise software",
            "Custom CRMs & ERPs",
            "Internal tools & dashboards",
            "API development & integration",
            "Legacy system modernization",
        ],
        "problems": [
            "Off-the-shelf tools not fitting your workflow",
            "Fragmented systems and manual data entry",
            "Scaling operational complexity",
            "Technical debt slowing innovation",
        ],
        "tech": ["Python", "Django", "PostgreSQL", "Docker", "Redis", "REST / GraphQL"],
        "benefits": [
            "Software built around your exact process",
            "Single source of truth for your data",
            "Seamless integration with existing tools",
            "Clean, documented, maintainable code",
        ],
        "use_cases": [
            "Custom ERP / CRM platforms",
            "Operations management systems",
            "Data management & reporting tools",
            "API & microservice backbones",
        ],
        "faqs": [
            {
                "q": "How do you scope custom software?",
                "a": "We run a collaborative discovery phase to map your process, identify priorities, and define a precise delivery plan before any code is written.",
            },
            {
                "q": "Can you work with our existing systems?",
                "a": "Absolutely. We regularly integrate with existing ERPs, CRMs, and internal tools via APIs and data pipelines.",
            },
        ],
    },
    {
        "slug": "ui-ux-design",
        "name": "UI/UX Design",
        "tagline": "Interfaces people love to use",
        "short": "Premium product design driven by research, clarity, and brand identity.",
        "icon": "design",
        "features": [
            "Product strategy & research",
            "UX architecture & wireframes",
            "High-fidelity UI design",
            "Design systems & tokens",
            "Usability testing",
        ],
        "problems": [
            "High drop-off in signup or checkout",
            "Users struggling to find features",
            "Inconsistent brand across touchpoints",
            "Design debt slowing product velocity",
        ],
        "tech": ["Figma", "Design Tokens", "Prototyping", "User Testing", "WCAG", "Atomic Design"],
        "benefits": [
            "Higher conversion and retention",
            "Consistent, premium brand experience",
            "Faster design-to-development handoff",
            "Accessible to the widest possible audience",
        ],
        "use_cases": [
            "SaaS & web app UX redesigns",
            "Mobile app design systems",
            "Landing page & funnel design",
            "Enterprise internal tool interfaces",
        ],
        "faqs": [
            {
                "q": "Do you design or build too?",
                "a": "Both. We are a full-studio — design and development work together so the final product matches the vision exactly.",
            },
            {
                "q": "How fast is a typical design engagement?",
                "a": "A design sprint can deliver clickable prototypes in 2–4 weeks. Full design systems typically complete in 6–10 weeks.",
            },
        ],
    },
    {
        "slug": "cloud-devops",
        "name": "Cloud & DevOps",
        "tagline": "Reliable infrastructure, delivered",
        "short": "Cloud architecture, CI/CD, and DevOps practices for resilient systems.",
        "icon": "cloud",
        "features": [
            "Cloud architecture (AWS / GCP / Azure)",
            "CI/CD pipelines",
            "Infrastructure as code",
            "Monitoring & observability",
            "Containerization & orchestration",
        ],
        "problems": [
            "Fragile infrastructure and downtime",
            "Manual deployment processes",
            "Rising cloud costs",
            "No visibility into system health",
        ],
        "tech": ["AWS", "GCP", "Docker", "Kubernetes", "Terraform", "GitHub Actions"],
        "benefits": [
            "99.9%+ uptime with automated recovery",
            "Push-button, zero-downtime deploys",
            "30–40% cloud cost reduction",
            "Full visibility with monitoring & alerts",
        ],
        "use_cases": [
            "Cloud migration & modernization",
            "Kubernetes / container platforms",
            "CI/CD automation for development teams",
            "Cost optimization & security hardening",
        ],
        "faqs": [
            {
                "q": "Which cloud provider do you use?",
                "a": "We are cloud-agnostic and typically recommend AWS, GCP, or Azure based on your workload, team, and budget.",
            },
        ],
    },
]

INDUSTRIES = [
    {
        "slug": "real-estate",
        "name": "Real Estate",
        "tagline": "Digital platforms for property and growth",
        "short": "PropTech platforms, CRM systems, and digital experiences for the modern real estate business.",
        "icon": "building",
        "challenges": [
            "Fragmented listing data across channels",
            "Manual lead follow-up slowing sales",
            "Outdated websites with poor mobile experience",
            "No visibility into pipeline performance",
        ],
        "solutions": [
            "Custom real estate portals & listing platforms",
            "Agent CRM and lead management systems",
            "Smart property search with filters & maps",
            "Marketing sites with virtual tour integration",
        ],
        "use_cases": [
            "Property listing & discovery platforms",
            "Brokerage CRM & pipeline tools",
            "Rental management systems",
            "Smart building & resident portals",
        ],
    },
    {
        "slug": "healthcare",
        "name": "Healthcare",
        "tagline": "Technology that cares",
        "short": "Secure, compliant digital health solutions for providers, clinics, and patients.",
        "icon": "health",
        "challenges": [
            "Strict compliance & data privacy requirements",
            "Outdated patient management workflows",
            "Limited patient engagement tools",
            "Fragmented clinical and admin data",
        ],
        "solutions": [
            "HIPAA-aware patient platforms",
            "Telehealth & appointment systems",
            "Clinical workflow automation",
            "Secure patient portals & communication",
        ],
        "use_cases": [
            "Patient scheduling & engagement portals",
            "Telemedicine platforms",
            "Electronic health record integrations",
            "Lab & clinic operations dashboards",
        ],
    },
    {
        "slug": "education",
        "name": "Education",
        "tagline": "Learning without limits",
        "short": "Digital learning platforms and student experiences for institutions and edtech.",
        "icon": "education",
        "challenges": [
            "Engaging remote & hybrid learners",
            "Managing admissions and enrollment manually",
            "Scaling course delivery across locations",
            "Student data scattered across systems",
        ],
        "solutions": [
            "Learning management platforms",
            "Student enrollment & admissions systems",
            "Virtual classroom experiences",
            "Institutional analytics dashboards",
        ],
        "use_cases": [
            "LMS & course platforms",
            "Student admission portals",
            "Assessment & certification tools",
            "Institutional data dashboards",
        ],
    },
    {
        "slug": "travel",
        "name": "Travel",
        "tagline": "Journeys deserve better technology",
        "short": "Travel booking platforms, experiences, and operations tools for modern travel brands.",
        "icon": "travel",
        "challenges": [
            "Complex booking & inventory management",
            "Fragmented distribution channels",
            "Delivering personalized experiences",
            "Operational cost pressure",
        ],
        "solutions": [
            "Custom booking & reservation platforms",
            "Travel agency management systems",
            "Dynamic packages & pricing engines",
            "Customer journey & loyalty tools",
        ],
        "use_cases": [
            "Hotel & resort booking platforms",
            "Tour operator management systems",
            "Travel marketplace development",
            "Loyalty & customer experience portals",
        ],
    },
    {
        "slug": "manufacturing",
        "name": "Manufacturing",
        "tagline": "Industry 4.0, operationalized",
        "short": "Smart manufacturing technology, IoT dashboards, and operational systems.",
        "icon": "manufacturing",
        "challenges": [
            "Limited visibility into production lines",
            "Manual quality control and reporting",
            "Predictive maintenance gaps",
            "Supply chain coordination complexity",
        ],
        "solutions": [
            "Production monitoring dashboards",
            "IoT & sensor data platforms",
            "Predictive maintenance systems",
            "Supply chain management tools",
        ],
        "use_cases": [
            "Factory floor analytics",
            "Equipment monitoring & alerts",
            "Quality management systems",
            "Inventory & supply chain platforms",
        ],
    },
    {
        "slug": "startups",
        "name": "Startups",
        "tagline": "From idea to launch, fast",
        "short": "End-to-end product development partners for ambitious startups.",
        "icon": "startup",
        "challenges": [
            "Moving from idea to MVP quickly",
            "Limited budgets and engineering resources",
            "Building product-market fit",
            "Scaling beyond the first launch",
        ],
        "solutions": [
            "MVP & prototype development",
            "Product strategy & technical architecture",
            "Full-stack product teams",
            "Post-launch scaling & optimization",
        ],
        "use_cases": [
            "SaaS product MVPs",
            "Marketplace platforms",
            "Consumer apps",
            "Founder & investor dashboards",
        ],
    },
    {
        "slug": "enterprise",
        "name": "Enterprise",
        "tagline": "Technology that transforms organizations",
        "short": "Large-scale digital transformation for established organizations.",
        "icon": "enterprise",
        "challenges": [
            "Complex legacy systems & data silos",
            "Security and governance requirements",
            "Cross-department process alignment",
            "Change management across teams",
        ],
        "solutions": [
            "Digital transformation roadmaps",
            "Custom enterprise platforms",
            "System integration & data unification",
            "Secure, governed architecture",
        ],
        "use_cases": [
            "Enterprise portals & intranets",
            "Unified data platforms",
            "Legacy modernization programs",
            "Cross-functional operations tools",
        ],
    },
]

TECHNOLOGIES = [
    {
        "category": "Frontend",
        "items": ["HTML5", "CSS3", "JavaScript", "Django Templates"],
    },
    {
        "category": "Backend",
        "items": ["Python", "Django", "REST APIs", "GraphQL"],
    },
    {
        "category": "Mobile",
        "items": ["Flutter", "React Native", "Swift", "Kotlin"],
    },
    {
        "category": "AI & Machine Learning",
        "items": ["TensorFlow", "PyTorch", "OpenAI", "LangChain", "Pandas"],
    },
    {
        "category": "Database",
        "items": ["PostgreSQL", "MySQL", "MongoDB", "Redis"],
    },
    {
        "category": "Cloud",
        "items": ["AWS", "Google Cloud", "Azure", "Cloudflare"],
    },
    {
        "category": "DevOps",
        "items": ["Docker", "Kubernetes", "Terraform", "GitHub Actions"],
    },
    {
        "category": "Security",
        "items": ["OAuth 2.0", "HTTPS / TLS", "SSO / SAML", "AWS IAM"],
    },
    {
        "category": "Payments",
        "items": ["Stripe", "Razorpay", "PayPal", "Square"],
    },
    {
        "category": "Analytics",
        "items": ["Google Analytics", "Mixpanel", "Metabase", "Grafana"],
    },
]

class ProductStatus:
    """Product status constants for the showcase."""

    COMING_SOON = "coming_soon"
    IN_DEVELOPMENT = "in_development"
    BETA = "beta"
    LIVE = "live"
    ARCHIVED = "archived"

    LABELS = {
        COMING_SOON: "Coming Soon",
        IN_DEVELOPMENT: "In Development",
        BETA: "Beta",
        LIVE: "Live",
        ARCHIVED: "Archived",
    }

    # CTA label shown on product cards based on status.
    CTA_LABELS = {
        COMING_SOON: "Explore Product",
        IN_DEVELOPMENT: "View Progress",
        BETA: "Try Beta",
        LIVE: "Open Product",
        ARCHIVED: "Learn More",
    }


PRODUCTS = [
    {
        "slug": "ai-travel",
        "name": "AI Travel Platform",
        "short_name": "AI Travel",
        "tagline": "Intelligent technology for smarter travel",
        "description": "An intelligent travel platform designed to simplify trip discovery, planning, personalization, and travel management.",
        "long_description": (
            "AI Travel Platform is an upcoming intelligent travel product. "
            "It will help travelers discover destinations, plan personalised trips, "
            "and manage every stage of their journey — all in one place. "
            "The platform is being designed with AI at its core to make travel "
            "planning faster, smarter, and more enjoyable."
        ),
        "category": "Travel Technology",
        "icon": "travel",
        "status": ProductStatus.COMING_SOON,
        "status_label": ProductStatus.LABELS[ProductStatus.COMING_SOON],
        "featured": True,
        "order": 1,
        "website_url": "",
        "internal_url": "/products/ai-travel/",
        "external_url": "",
        "cta_label": ProductStatus.CTA_LABELS[ProductStatus.COMING_SOON],
        "technologies": ["Python", "Django", "AI/ML", "Cloud"],
        "key_features": [
            "Smart trip discovery",
            "Personalised planning",
            "Travel management",
            "AI-powered recommendations",
        ],
        "vision": (
            "To make travel planning effortless by using AI to understand "
            "preferences, suggest experiences, and handle the complexity of planning."
        ),
        "solves": (
            "Travelers currently juggle multiple apps, guides, and spreadsheets "
            "to plan a trip. AI Travel Platform will bring discovery, planning, "
            "and management into one intelligent experience."
        ),
        "status_note": (
            "This product is in early planning. All capabilities shown are "
            "planned or future capabilities — nothing is available yet."
        ),
    },
    {
        "slug": "society-management",
        "name": "Society Management Platform",
        "short_name": "Society Management",
        "tagline": "Simpler operations for residential communities",
        "description": "A future digital platform designed to simplify residential society operations, communication, security, and management.",
        "long_description": (
            "Society Management Platform is a planned product for residential "
            "communities. It will simplify daily operations — from security and "
            "visitor management to maintenance and resident communication — "
            "in one secure, well-designed platform."
        ),
        "category": "Property Technology",
        "icon": "building",
        "status": ProductStatus.COMING_SOON,
        "status_label": ProductStatus.LABELS[ProductStatus.COMING_SOON],
        "featured": True,
        "order": 2,
        "website_url": "",
        "internal_url": "/products/society-management/",
        "external_url": "",
        "cta_label": ProductStatus.CTA_LABELS[ProductStatus.COMING_SOON],
        "technologies": ["Python", "Django", "PostgreSQL", "Mobile"],
        "key_features": [
            "Resident communication",
            "Security & visitor management",
            "Maintenance management",
            "Society operations tools",
        ],
        "vision": (
            "To give residential societies a modern, unified platform that "
            "makes management transparent, secure, and effortless."
        ),
        "solves": (
            "Societies rely on scattered tools, paper records, and informal "
            "communication. This platform will centralise operations for "
            "residents, guards, and management committees."
        ),
        "status_note": (
            "This product is in early planning. All capabilities shown are "
            "planned or future capabilities — nothing is available yet."
        ),
    },
    {
        "slug": "business-ai",
        "name": "Business AI Platform",
        "short_name": "Business AI",
        "tagline": "Intelligence for better business decisions",
        "description": "An upcoming AI-powered business platform designed to help organizations automate workflows, understand information, and make better decisions.",
        "long_description": (
            "Business AI Platform is an upcoming product that will help "
            "organizations put AI to work. It will automate workflows, "
            "surface insights from business information, and support "
            "better, faster decisions — with enterprise-grade safety."
        ),
        "category": "Artificial Intelligence",
        "icon": "ai",
        "status": ProductStatus.COMING_SOON,
        "status_label": ProductStatus.LABELS[ProductStatus.COMING_SOON],
        "featured": True,
        "order": 3,
        "website_url": "",
        "internal_url": "/products/business-ai/",
        "external_url": "",
        "cta_label": ProductStatus.CTA_LABELS[ProductStatus.COMING_SOON],
        "technologies": ["Python", "AI/ML", "LLM", "Cloud"],
        "key_features": [
            "Workflow automation",
            "Information understanding",
            "Decision support",
            "Enterprise-grade safety",
        ],
        "vision": (
            "To make advanced AI practical and safe for everyday business use — "
            "helping teams focus on high-impact work."
        ),
        "solves": (
            "Businesses struggle to apply AI in a safe, practical way. "
            "This platform aims to make AI accessible, controllable, and useful "
            "for real organizational workflows."
        ),
        "status_note": (
            "This product is in early planning. All capabilities shown are "
            "planned or future capabilities — nothing is available yet."
        ),
    },
]

PORTFOLIO_ITEMS = [
    {
        "slug": "enterprise-operations-platform",
        "title": "Enterprise Operations Platform",
        "industry": "Enterprise",
        "services": ["Software Development", "Cloud & DevOps"],
        "tech": ["Python", "Django", "PostgreSQL"],
        "summary": "A unified operations platform that replaced fragmented spreadsheets and manual workflows.",
        "challenge": "A global enterprise relied on disconnected spreadsheets and manual handoffs, causing delays and data inconsistency across departments.",
        "strategy": "We mapped their end-to-end operations, then designed a unified platform with role-based dashboards and automated approval flows.",
        "solution": "A custom Django-based operations platform with modular dashboards, automated workflows, and a single source of truth for operational data.",
        "results": [
            "Centralized data across 6 departments",
            "Automated monthly reporting cycles",
            "Role-based secure access controls",
        ],
        "note": "Demo case study — client details intentionally generic.",
    },
    {
        "slug": "ai-document-processing",
        "title": "AI Document Processing",
        "industry": "Financial Services",
        "services": ["AI & Automation", "Software Development"],
        "tech": ["Python", "OpenAI", "PostgreSQL"],
        "summary": "An AI pipeline that automatically extracts, validates, and routes data from thousands of documents.",
        "challenge": "Hundreds of hours per month were spent manually keying data from invoices and contracts into core systems.",
        "strategy": "We combined OCR, NLP models, and validation rules to build a document intelligence pipeline that handles edge cases gracefully.",
        "solution": "A secure AI pipeline that ingests documents, extracts structured data, flags anomalies, and routes approved records to their target systems.",
        "results": [
            "~85% reduction in manual data entry",
            "Sub-second document processing times",
            "Human-in-the-loop review for edge cases",
        ],
        "note": "Demo case study — client details intentionally generic.",
    },
    {
        "slug": "premium-ecommerce-experience",
        "title": "Premium E-Commerce Experience",
        "industry": "E-Commerce",
        "services": ["Web Development", "UI/UX Design"],
        "tech": ["Django", "PostgreSQL", "JavaScript"],
        "summary": "A high-converting e-commerce platform with a premium brand experience.",
        "challenge": "An established retailer's store was slow, dated, and converting poorly on mobile — most visitors left before checkout.",
        "strategy": "We rebuilt the experience around a mobile-first design system with fast product discovery and a frictionless checkout.",
        "solution": "A blazing-fast, mobile-first e-commerce platform with a premium design system and streamlined checkout flow.",
        "results": [
            "Mobile conversion rate doubled post-launch",
            "Page load time reduced from 6s to under 2s",
            "Seamless inventory & order integration",
        ],
        "note": "Demo case study — client details intentionally generic.",
    },
    {
        "slug": "real-estate-portal",
        "title": "Real Estate Listing Portal",
        "industry": "Real Estate",
        "services": ["Web Development", "Software Development"],
        "tech": ["Django", "PostgreSQL", "Cloudflare"],
        "summary": "A property discovery platform connecting buyers with listings across a multi-city portfolio.",
        "challenge": "Listings were scattered across print, portals, and social media with no unified search experience for buyers.",
        "strategy": "We centralized listing data into a structured model and built an intuitive filtered search experience.",
        "solution": "A property portal with smart search, saved searches, and agent dashboard for managing listings.",
        "results": [
            "3x increase in qualified enquiries",
            "Centralized listing management",
            "Real-time listing availability",
        ],
        "note": "Demo case study — client details intentionally generic.",
    },
    {
        "slug": "education-management-system",
        "title": "Education Management System",
        "industry": "Education",
        "services": ["Software Development", "UI/UX Design"],
        "tech": ["Django", "PostgreSQL", "Redis"],
        "summary": "A complete platform managing admissions, courses, assessments, and student communication.",
        "challenge": "An institution juggled enrollment, course delivery, and reporting across disconnected tools and paper records.",
        "strategy": "We designed a role-based platform around the real workflows of students, faculty, and administrators.",
        "solution": "A unified education management system covering admissions, course scheduling, assessments, and communications.",
        "results": [
            "90% faster enrollment processing",
            "Unified student records",
            "Automated reporting for administrators",
        ],
        "note": "Demo case study — client details intentionally generic.",
    },
    {
        "slug": "predictive-maintenance",
        "title": "Predictive Maintenance System",
        "industry": "Manufacturing",
        "services": ["AI & Automation", "Cloud & DevOps"],
        "tech": ["Python", "TensorFlow", "AWS"],
        "summary": "An AI-driven system predicting equipment failures before they disrupt production.",
        "challenge": "Unplanned equipment downtime caused significant production losses across multiple factory lines.",
        "strategy": "We analyzed sensor telemetry to identify failure patterns and built a real-time prediction pipeline.",
        "solution": "A predictive maintenance platform ingesting sensor data, scoring failure risk, and triggering automated maintenance alerts.",
        "results": [
            "~30% reduction in unplanned downtime",
            "Real-time line health dashboard",
            "Automated alerting & work orders",
        ],
        "note": "Demo case study — client details intentionally generic.",
    },
]