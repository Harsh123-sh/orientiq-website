"""Static content data for the Orientiq public website."""

SERVICES = [
    {
        "slug": "ai-automation",
        "name": "AI & Automation",
        "tagline": "Intelligent systems that work for you",
        "short": "Intelligent AI systems and automation designed around your business workflows.",
        "icon": "ai",
        "features": [
            "Custom AI solutions",
            "Intelligent workflow automation",
            "AI-powered document processing",
            "Predictive analytics",
            "Natural language solutions",
            "AI assistants and knowledge systems",
        ],
        "problems": [
            "Manual workflows consuming valuable time",
            "Data trapped across documents and systems",
            "Slow or inconsistent decision-making",
            "Customer support bottlenecks",
        ],
        "tech": ["Python", "OpenAI", "PyTorch", "TensorFlow", "LangChain", "PostgreSQL"],
        "benefits": [
            "Reduce repetitive operational work",
            "Accelerate decision-making with useful insights",
            "Improve consistency across workflows",
            "Scale processes more efficiently",
        ],
        "use_cases": [
            "Automated document processing & extraction",
            "AI-powered customer support assistants",
            "Predictive maintenance for equipment",
            "Intelligent sales & demand forecasting",
        ],
        "process": [
            {"number": "01", "title": "Discovery", "description": "Understand your workflows, data, goals, and opportunities for AI and automation."},
            {"number": "02", "title": "Strategy", "description": "Define the AI approach, architecture, integrations, and implementation roadmap."},
            {"number": "03", "title": "Design", "description": "Design the user experience, automation flows, and system interactions."},
            {"number": "04", "title": "Development", "description": "Build, integrate, test, and refine the solution in measurable increments."},
            {"number": "05", "title": "Launch", "description": "Deploy the solution and validate it in the real operating environment."},
            {"number": "06", "title": "Growth", "description": "Monitor performance, improve workflows, and expand capabilities over time."},
        ],
        "faqs": [
            {
                "q": "How long does an AI project take?",
                "a": "Timelines depend on the solution scope, data availability, and integration complexity. A focused proof-of-concept can typically move in 4–8 weeks, while production platforms often span 3–6 months.",
            },
            {
                "q": "Do we need existing data for AI?",
                "a": "We can work with whatever data you have available. Our team helps structure, clean, and prepare data as part of the discovery and strategy phases.",
            },
        ],
    },
    {
        "slug": "web-development",
        "name": "Web Development",
        "tagline": "Premium web platforms built to scale",
        "short": "High-performance web platforms built for usability, scalability, and long-term growth.",
        "icon": "web",
        "features": [
            "Custom web applications",
            "Business and enterprise platforms",
            "SaaS products",
            "E-commerce platforms",
            "Progressive web experiences",
            "API-driven web systems",
        ],
        "problems": [
            "Outdated websites limiting growth",
            "Slow experiences affecting engagement",
            "Platforms that cannot scale with demand",
            "Poor mobile usability",
        ],
        "tech": ["Django", "Python", "PostgreSQL", "HTML5", "CSS3", "JavaScript"],
        "benefits": [
            "Fast, responsive user experiences",
            "Search-friendly and accessible architecture",
            "Mobile-first experience",
            "Maintainable and scalable codebase",
        ],
        "use_cases": [
            "Enterprise web platforms & portals",
            "High-conversion e-commerce stores",
            "SaaS dashboards & admin panels",
            "Marketing sites & brand experiences",
        ],
        "process": [
            {"number": "01", "title": "Discovery", "description": "Understand your audience, business goals, competitive landscape, and technical requirements."},
            {"number": "02", "title": "Strategy", "description": "Define the platform architecture, roadmap, integrations, and measurable success criteria."},
            {"number": "03", "title": "Design", "description": "Create premium, user-centered interfaces and interactions optimized for your audience."},
            {"number": "04", "title": "Development", "description": "Build clean, performant code with responsive design and thorough testing."},
            {"number": "05", "title": "Launch", "description": "Deploy with SEO setup, analytics, and monitoring for ongoing visibility."},
            {"number": "06", "title": "Growth", "description": "Optimize performance, iterate based on user data, and scale as demand grows."},
        ],
        "faqs": [
            {
                "q": "What technologies do you use?",
                "a": "We build primarily with Django and Python on the backend, paired with clean HTML5, CSS3, and vanilla JavaScript on the frontend. This approach keeps applications fast, maintainable, and focused on user experience.",
            },
            {
                "q": "Can you redesign an existing site?",
                "a": "Yes. We regularly modernize legacy websites into fast, accessible, premium experiences while preserving SEO value and maintaining existing content.",
            },
        ],
    },
    {
        "slug": "mobile-development",
        "name": "Mobile Development",
        "tagline": "Native-quality mobile experiences",
        "short": "Mobile experiences designed for performance, usability, and seamless everyday use.",
        "icon": "mobile",
        "features": [
            "iOS applications",
            "Android applications",
            "Cross-platform applications",
            "Mobile UI/UX",
            "API and backend integration",
            "App deployment and maintenance",
        ],
        "problems": [
            "No effective mobile experience",
            "Poor app usability and performance",
            "Separate codebases increasing maintenance effort",
            "Difficulty turning mobile users into customers",
        ],
        "tech": ["Flutter", "React Native", "Swift", "Kotlin", "Firebase", "REST APIs"],
        "benefits": [
            "Intuitive mobile experiences",
            "Strong performance across supported devices",
            "Efficient cross-platform development when appropriate",
            "Maintainable applications with ongoing support",
        ],
        "use_cases": [
            "Customer-facing mobile apps",
            "Field & staff productivity apps",
            "Mobile-first e-commerce",
            "IoT companion apps",
        ],
        "process": [
            {"number": "01", "title": "Discovery", "description": "Understand your mobile strategy, target audience, platform priorities, and core functionality."},
            {"number": "02", "title": "Strategy", "description": "Define technical approach, native vs. cross-platform decision, integrations, and roadmap."},
            {"number": "03", "title": "Design", "description": "Design mobile-first interfaces optimized for touch, screens, and offline scenarios."},
            {"number": "04", "title": "Development", "description": "Build, test across devices, and implement backend integrations with performance focus."},
            {"number": "05", "title": "Launch", "description": "Deploy to app stores, configure analytics, and establish distribution and feedback channels."},
            {"number": "06", "title": "Growth", "description": "Monitor user feedback, optimize performance, add features, and maintain platform compatibility."},
        ],
        "faqs": [
            {
                "q": "Do you build for both iOS and Android?",
                "a": "Yes. We typically recommend cross-platform frameworks like Flutter for cost efficiency when appropriate, or native development when specific platform performance is critical. The choice depends on your product requirements.",
            },
            {
                "q": "How long does an app take?",
                "a": "Timelines depend on app complexity, feature scope, and testing requirements. An MVP can typically move faster, while full-featured production apps require more time for quality assurance and platform-specific optimization.",
            },
        ],
    },
    {
        "slug": "software-development",
        "name": "Software Development",
        "tagline": "Custom software for complex problems",
        "short": "Custom software engineered around your workflows, integrations, and operational needs.",
        "icon": "software",
        "features": [
            "Enterprise software",
            "Custom CRM and ERP systems",
            "Internal business tools",
            "Dashboards and operational systems",
            "API development and integrations",
            "Legacy system modernization",
        ],
        "problems": [
            "Off-the-shelf software not fitting the workflow",
            "Fragmented business systems",
            "Manual data entry and operational processes",
            "Legacy technology slowing growth",
        ],
        "tech": ["Python", "Django", "PostgreSQL", "Redis", "Docker", "REST / GraphQL"],
        "benefits": [
            "Software aligned with business processes",
            "Centralized and reliable business data",
            "Integration with existing systems",
            "Maintainable and documented architecture",
        ],
        "use_cases": [
            "Custom ERP / CRM platforms",
            "Operations management systems",
            "Data management & reporting tools",
            "API & microservice backbones",
        ],
        "process": [
            {"number": "01", "title": "Discovery", "description": "Understand your business processes, existing systems, pain points, and operational requirements."},
            {"number": "02", "title": "Strategy", "description": "Define the software architecture, integrations, data model, and implementation approach."},
            {"number": "03", "title": "Design", "description": "Design user workflows, dashboards, and system interfaces for your operational team."},
            {"number": "04", "title": "Development", "description": "Build, integrate with existing systems, and test across your operational workflows."},
            {"number": "05", "title": "Launch", "description": "Deploy with team training, data migration, and ongoing operational support."},
            {"number": "06", "title": "Growth", "description": "Monitor usage, optimize workflows, add requested capabilities, and scale as needed."},
        ],
        "faqs": [
            {
                "q": "How do you scope custom software?",
                "a": "We run a collaborative discovery phase to map your processes, identify priorities, and define a precise delivery plan before development begins. This ensures alignment on scope and realistic expectations.",
            },
            {
                "q": "Can you work with our existing systems?",
                "a": "Yes. We regularly integrate with existing ERPs, CRMs, and internal tools via APIs and data pipelines. Legacy system integration is a standard part of our approach.",
            },
        ],
    },
    {
        "slug": "ui-ux-design",
        "name": "UI/UX Design",
        "tagline": "Interfaces people love to use",
        "short": "Research-driven product experiences designed for clarity, usability, and conversion.",
        "icon": "design",
        "features": [
            "Product strategy and research",
            "UX architecture and wireframes",
            "High-fidelity interface design",
            "Design systems",
            "Interactive prototypes",
            "Usability testing",
        ],
        "problems": [
            "Users struggling to complete key tasks",
            "High drop-off during important journeys",
            "Inconsistent product experiences",
            "Design decisions made without user insight",
        ],
        "tech": ["Figma", "Design Systems", "Prototyping", "User Research", "Usability Testing", "WCAG"],
        "benefits": [
            "Clearer user journeys",
            "Stronger product usability",
            "Consistent visual language",
            "Better collaboration between design and development",
        ],
        "use_cases": [
            "SaaS & web app UX redesigns",
            "Mobile app design systems",
            "Landing page & funnel design",
            "Enterprise internal tool interfaces",
        ],
        "process": [
            {"number": "01", "title": "Discovery", "description": "Understand your users, business objectives, competitive landscape, and current pain points."},
            {"number": "02", "title": "Strategy", "description": "Define the design approach, user flows, information architecture, and success metrics."},
            {"number": "03", "title": "Design", "description": "Create wireframes, prototypes, and high-fidelity designs based on user research insights."},
            {"number": "04", "title": "Development", "description": "Collaborate with engineering to translate designs into coded, interactive experiences."},
            {"number": "05", "title": "Launch", "description": "Deploy the redesigned product with monitoring for user engagement and feedback."},
            {"number": "06", "title": "Growth", "description": "Gather user feedback, iterate on design, optimize conversions, and expand capabilities."},
        ],
        "faqs": [
            {
                "q": "Do you design or build too?",
                "a": "We are a full-service studio — design and development teams work together throughout the project. This ensures the final product precisely matches the design vision and performs seamlessly.",
            },
            {
                "q": "How fast is a typical design engagement?",
                "a": "A focused design sprint can deliver prototypes in 2–4 weeks. Comprehensive design systems and full redesigns typically span 6–12 weeks depending on scope and discovery depth.",
            },
        ],
    },
    {
        "slug": "cloud-devops",
        "name": "Cloud & DevOps",
        "tagline": "Reliable infrastructure, delivered",
        "short": "Reliable cloud infrastructure and deployment systems built for performance, visibility, and scale.",
        "icon": "cloud",
        "features": [
            "Cloud architecture",
            "CI/CD pipelines",
            "Infrastructure as code",
            "Monitoring and observability",
            "Containerization",
            "Deployment automation",
        ],
        "problems": [
            "Fragile infrastructure",
            "Manual deployments",
            "Poor system visibility",
            "Uncontrolled infrastructure complexity and cost",
        ],
        "tech": ["AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform", "GitHub Actions"],
        "benefits": [
            "Reliable infrastructure practices",
            "More efficient deployment workflows",
            "Better monitoring and system visibility",
            "Improved infrastructure management",
        ],
        "use_cases": [
            "Cloud migration & modernization",
            "Kubernetes / container platforms",
            "CI/CD automation for development teams",
            "Cost optimization & security hardening",
        ],
        "process": [
            {"number": "01", "title": "Discovery", "description": "Assess your current infrastructure, workloads, compliance requirements, and scaling goals."},
            {"number": "02", "title": "Strategy", "description": "Design cloud architecture, DevOps approach, cost model, and migration/implementation roadmap."},
            {"number": "03", "title": "Design", "description": "Create infrastructure blueprints, deployment pipelines, monitoring, and disaster recovery plans."},
            {"number": "04", "title": "Development", "description": "Build infrastructure as code, CI/CD pipelines, containerization, and automated testing."},
            {"number": "05", "title": "Launch", "description": "Deploy infrastructure, establish monitoring, run validation tests, and activate alerts."},
            {"number": "06", "title": "Growth", "description": "Monitor performance, optimize costs, scale infrastructure, and enhance security and resilience."},
        ],
        "faqs": [
            {
                "q": "Which cloud provider do you use?",
                "a": "We are cloud-agnostic and work with AWS, GCP, and Azure. We typically recommend based on your workload characteristics, team expertise, existing commitments, and budget requirements.",
            },
        ],
    },
]

INDUSTRIES = [
    {
        "slug": "real-estate",
        "name": "Real Estate",
        "tagline": "Digital platforms for property and growth",
        "short": "Custom technology platforms that centralize listings, streamline operations, and create seamless buyer and agent experiences.",
        "icon": "building",
        "challenges": [
            "Listing data fragmented across multiple channels and formats",
            "Manual lead follow-up and pipeline tracking",
            "Slow, outdated websites that lose buyers before inquiry",
            "Limited visibility into transaction pipeline and performance",
        ],
        "solutions": [
            "Unified property portals with smart search and filtering",
            "CRM and lead management systems built for real estate workflows",
            "High-performance websites optimized for buyer engagement",
            "Operational dashboards for agents, teams, and brokerages",
        ],
        "benefits": [
            "Centralized listing data across all channels",
            "Faster inquiry response and lead qualification",
            "Improved buyer experience and conversion rates",
            "Better transparency into pipeline and performance metrics",
        ],
        "relevant_services": ["Web Development", "Software Development", "UI/UX Design", "Cloud & DevOps"],
        "use_cases": [
            "Property listing & discovery platforms",
            "Brokerage CRM & pipeline management",
            "Rental management and tenant portals",
            "Smart building & resident communication systems",
        ],
        "faqs": [
            {
                "q": "How do you handle real estate data integration?",
                "a": "We build systems that pull listing data from multiple sources (MLS, internal databases, APIs) and consolidate into a unified database. This ensures accurate, current information across all buyer-facing and internal channels.",
            },
            {
                "q": "Can you integrate with existing real estate tools?",
                "a": "Yes. We regularly integrate with CRMs, accounting systems, document management, and third-party services via APIs and data pipelines.",
            },
        ],
    },
    {
        "slug": "healthcare",
        "name": "Healthcare",
        "tagline": "Technology that cares",
        "short": "Secure, HIPAA-compliant digital health platforms that improve patient engagement, streamline clinical workflows, and enable better care coordination.",
        "icon": "health",
        "challenges": [
            "Strict compliance requirements (HIPAA, regulations) slowing innovation",
            "Outdated, fragmented patient management systems",
            "Limited tools for patient engagement and communication",
            "Clinical and administrative data trapped in separate systems",
        ],
        "solutions": [
            "HIPAA-compliant patient portals and engagement platforms",
            "Clinical workflow automation and task management",
            "Telehealth and secure appointment systems",
            "Secure data integration between clinical and administrative systems",
        ],
        "benefits": [
            "Regulatory compliance built into the platform foundation",
            "Reduced administrative burden on clinical staff",
            "Improved patient engagement and satisfaction",
            "Better care coordination through unified data",
        ],
        "relevant_services": ["Software Development", "AI & Automation", "Cloud & DevOps", "UI/UX Design"],
        "use_cases": [
            "Patient scheduling & engagement portals",
            "Telemedicine platforms for remote consultations",
            "Electronic health record integrations and data sharing",
            "Clinical operations dashboards and reporting",
        ],
        "faqs": [
            {
                "q": "How do you ensure HIPAA compliance?",
                "a": "HIPAA compliance is built into our architecture from the start — encryption at rest and in transit, access controls, audit logs, and data retention policies. We work with your compliance team to ensure all requirements are met.",
            },
            {
                "q": "Can you integrate with existing EHR systems?",
                "a": "Yes. We build integrations with major EHR platforms (Epic, Cerner, athenahealth, etc.) via their APIs and HL7 standards for seamless data flow.",
            },
        ],
    },
    {
        "slug": "education",
        "name": "Education",
        "tagline": "Learning without limits",
        "short": "Comprehensive educational platforms that unify admissions, course delivery, assessments, and student communication in one experience.",
        "icon": "education",
        "challenges": [
            "Manual enrollment and admissions processes creating bottlenecks",
            "Difficulty engaging remote and hybrid learners",
            "Course delivery, scheduling, and coordination across multiple locations",
            "Student data scattered across spreadsheets and disconnected systems",
        ],
        "solutions": [
            "Unified learning management and student information systems",
            "Enrollment and admissions automation with workflow tools",
            "Interactive course delivery with assessments and progress tracking",
            "Student and faculty communication and collaboration platforms",
        ],
        "benefits": [
            "Streamlined enrollment without manual data entry",
            "Consistent, engaging learning experiences for all students",
            "Real-time visibility into student progress and outcomes",
            "Improved coordination between academic and administrative teams",
        ],
        "relevant_services": ["Web Development", "Software Development", "Mobile Development", "AI & Automation"],
        "use_cases": [
            "Learning management platforms (LMS) for institutions",
            "Student admission and enrollment systems",
            "Assessment, certification, and grade management tools",
            "Institutional dashboards for enrollment and outcomes analytics",
        ],
        "faqs": [
            {
                "q": "Do you support blended and remote learning?",
                "a": "Yes. Our platforms support traditional, blended, and fully remote learning with video integration, discussion forums, assignment submission, and progress tracking.",
            },
            {
                "q": "Can you integrate with student information systems?",
                "a": "Absolutely. We build integrations with existing SIS platforms and can migrate legacy data while maintaining historical records.",
            },
        ],
    },
    {
        "slug": "travel",
        "name": "Travel",
        "tagline": "Journeys deserve better technology",
        "short": "Booking platforms, operations tools, and customer experience systems built for travel companies, agencies, and tour operators.",
        "icon": "travel",
        "challenges": [
            "Complex inventory management across flights, hotels, activities, and packages",
            "Fragmented booking channels leading to double-bookings and errors",
            "Difficulty delivering personalized experiences at scale",
            "Thin margins demanding operational efficiency and cost control",
        ],
        "solutions": [
            "Custom booking and reservation platforms with real-time inventory",
            "Travel operations management systems for itinerary planning and fulfillment",
            "Dynamic pricing engines responsive to demand and market conditions",
            "Customer loyalty and engagement platforms with personalization",
        ],
        "benefits": [
            "Centralized inventory reduces double-bookings and errors",
            "Personalized recommendations increase conversion and customer lifetime value",
            "Operational automation reduces manual work and costs",
            "Real-time insights enable better pricing and promotions",
        ],
        "relevant_services": ["Web Development", "Software Development", "AI & Automation", "Mobile Development"],
        "use_cases": [
            "Hotel and resort booking platforms",
            "Tour operator management and itinerary systems",
            "Travel marketplace platforms connecting buyers and suppliers",
            "Customer loyalty and experience portals",
        ],
        "faqs": [
            {
                "q": "How do you handle real-time booking and inventory?",
                "a": "Our systems use real-time databases and caching to ensure inventory accuracy across channels. We integrate with supplier systems via APIs to keep data current.",
            },
            {
                "q": "Can you support multi-currency and multi-language booking?",
                "a": "Yes. Our platforms support global operations with multi-currency pricing, localized content, and payment methods appropriate to each market.",
            },
        ],
    },
    {
        "slug": "manufacturing",
        "name": "Manufacturing",
        "tagline": "Industry 4.0, operationalized",
        "short": "Smart manufacturing platforms combining IoT monitoring, predictive analytics, and operational dashboards for modern factories.",
        "icon": "manufacturing",
        "challenges": [
            "Limited real-time visibility into production line performance and quality",
            "Manual quality control and reporting creating delays and errors",
            "Reactive maintenance causing unplanned downtime and production losses",
            "Complex supply chain coordination across multiple suppliers and locations",
        ],
        "solutions": [
            "Production monitoring dashboards with real-time KPI tracking",
            "IoT sensor integration for equipment health and performance monitoring",
            "AI-powered predictive maintenance systems that forecast failures",
            "Supply chain management and vendor coordination systems",
        ],
        "benefits": [
            "Increased production uptime and reduced unplanned downtime",
            "Better quality control with real-time issue detection",
            "Improved supply chain efficiency and cost management",
            "Data-driven decision-making with production analytics",
        ],
        "relevant_services": ["Software Development", "AI & Automation", "Cloud & DevOps", "Web Development"],
        "use_cases": [
            "Factory floor real-time analytics and KPI dashboards",
            "Equipment monitoring and predictive maintenance systems",
            "Quality management and inspection workflow automation",
            "Supply chain visibility and vendor management platforms",
        ],
        "faqs": [
            {
                "q": "What IoT sensors and devices do you support?",
                "a": "We integrate with industrial IoT platforms and can support sensors from major manufacturers. Our systems are sensor-agnostic and flexible for your existing hardware.",
            },
            {
                "q": "How does predictive maintenance work?",
                "a": "We analyze historical sensor data and equipment logs to identify failure patterns, then build models that predict failures with enough lead time for planned maintenance.",
            },
        ],
    },
    {
        "slug": "startups",
        "name": "Startups",
        "tagline": "From idea to launch, fast",
        "short": "End-to-end product development partners that help startups move from concept to market quickly and efficiently.",
        "icon": "startup",
        "challenges": [
            "Time pressure to build and launch MVP faster than competitors",
            "Limited budgets and engineering resources",
            "Uncertainty about product-market fit requiring rapid iteration",
            "Technical debt and scaling challenges after initial launch",
        ],
        "solutions": [
            "Rapid MVP development with focused scope and fast iteration cycles",
            "Product strategy and technical architecture guidance",
            "Full-stack development teams handling frontend, backend, and infrastructure",
            "Scalable architecture that grows with demand without major rewrites",
        ],
        "benefits": [
            "Faster time-to-market for MVP and subsequent releases",
            "Clear technical foundation that scales as the business grows",
            "Product strategy informed by market and user feedback",
            "Reduced technical debt and maintenance burden",
        ],
        "relevant_services": ["Web Development", "Mobile Development", "Software Development", "Cloud & DevOps"],
        "use_cases": [
            "SaaS product MVPs and founder-validated concepts",
            "Marketplace platforms connecting buyers and sellers",
            "Mobile-first consumer apps",
            "Founder dashboards and investor reporting tools",
        ],
        "faqs": [
            {
                "q": "How fast can you build an MVP?",
                "a": "Timelines depend on scope and complexity. A focused, well-defined MVP can typically launch in 8–12 weeks. More complex platforms may require longer timelines.",
            },
            {
                "q": "How do you handle scaling after launch?",
                "a": "We build with scalability in mind from the start — cloud infrastructure, database design, and code architecture all account for growth. As demand increases, the system can scale without major rewrites.",
            },
        ],
    },
]

TECHNOLOGIES = [
    {
        "category": "Web & Application Development",
        "items": ["Python", "Django", "JavaScript", "HTML5", "CSS3", "REST APIs", "GraphQL"],
    },
    {
        "category": "AI & Machine Learning",
        "items": ["Python", "OpenAI", "PyTorch", "TensorFlow", "LangChain", "Pandas"],
    },
    {
        "category": "Mobile Development",
        "items": ["Flutter", "React Native", "Swift", "Kotlin", "Firebase"],
    },
    {
        "category": "Data & Databases",
        "items": ["PostgreSQL", "MySQL", "MongoDB", "Redis"],
    },
    {
        "category": "Cloud & Infrastructure",
        "items": ["AWS", "Google Cloud", "Microsoft Azure", "Cloudflare"],
    },
    {
        "category": "DevOps",
        "items": ["Docker", "Kubernetes", "Terraform", "GitHub Actions"],
    },
    {
        "category": "Product & Design",
        "items": ["Figma", "Design Systems", "Prototyping", "User Research", "Usability Testing", "WCAG"],
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
        "tagline": "Smarter planning for modern travel",
        "description": "A travel planning experience designed to reduce decision fatigue and keep every trip more organised.",
        "long_description": (
            "AI Travel Platform is a planned product for travelers who move between "
            "inspiration sources, booking tools, and trip logistics. It brings "
            "discovery, planning, and day-of-travel support into one experience, "
            "with AI helping surface better decisions at the right moment."
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
            "Trip discovery and inspiration",
            "Personalised itinerary planning",
            "Budget and travel coordination",
            "Smart recommendations and support",
        ],
        "vision": (
            "To help travelers move from inspiration to execution without losing the "
            "joy of discovery or the confidence of careful planning."
        ),
        "solves": (
            "Travelers often move between booking platforms, spreadsheets, and destination guides to plan a single trip. "
            "AI Travel Platform brings discovery, itinerary planning, and trip management into one more coherent experience."
        ),
        "status_note": (
            "This product is in planning and early development. Features shown are conceptual and may evolve as product requirements are refined."
        ),
    },
    {
        "slug": "society-management",
        "name": "Society Management Platform",
        "short_name": "Society Management",
        "tagline": "Clearer operations for residential communities",
        "description": "A resident-first operations platform for communities that need clearer communication and safer day-to-day processes.",
        "long_description": (
            "Society Management Platform is a planned system for residential communities "
            "that need smoother operations, stronger resident communication, and better "
            "visibility into day-to-day activity. It is designed to centralise resident "
            "requests, maintenance coordination, and security workflows in one place."
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
            "Resident communication and updates",
            "Visitor and security tracking",
            "Maintenance and service requests",
            "Community operations dashboards",
        ],
        "vision": (
            "To help communities operate more transparently, efficiently, and confidently with digital workflows built around residents and staff."
        ),
        "solves": (
            "Housing societies often rely on fragmented communication and manual follow-ups across resident communication, maintenance requests, and security processes. "
            "This platform consolidates those workflows into a single system."
        ),
        "status_note": (
            "This product is in planning and early development. Functional scope and rollout priorities will be shaped by real community needs."
        ),
    },
    {
        "slug": "business-ai",
        "name": "Business AI Platform",
        "short_name": "Business AI",
        "tagline": "Practical AI for smarter business operations",
        "description": "A business intelligence platform that helps teams turn information into action with safer, more practical AI workflows.",
        "long_description": (
            "Business AI Platform is a planned product for organizations that need AI to be useful, governed and easy to trust. "
            "It is designed to connect knowledge, workflows, and decisions in a more structured way, helping teams work faster without sacrificing clarity or control."
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
            "Workflow automation and task support",
            "Knowledge retrieval and insight generation",
            "Decision support and reporting",
            "Governance and operational controls",
        ],
        "vision": (
            "To give organizations a safer foundation for operational AI — one that supports better decisions, faster execution, and clearer accountability."
        ),
        "solves": (
            "Many teams want to use AI but struggle with fragmented tools, unclear governance, and inconsistent results. "
            "Business AI Platform aims to make AI more practical and easier to govern and easy to trust across everyday business workflows."
        ),
        "status_note": (
            "This product is in planning and early development. Final capabilities will depend on workflow needs, governance requirements, and deployment scope."
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