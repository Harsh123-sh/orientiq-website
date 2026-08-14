"""AI service layer for the Orientiq AI assistant.

Architecture:
    Website → Django API → AI Service → Provider Adapter → LLM Provider

If no AI provider is configured (AI_PROVIDER / AI_API_KEY), the service
falls back to a knowledge-based responder that answers from the approved
company context. This keeps the assistant functional without an API key.
"""

import os

from .knowledge import build_company_context
from .prompts import build_ai_prompt
from .safety import sanitize_output


class AIProviderError(Exception):
    """Raised when the AI provider fails."""


class BaseProvider:
    """Base class for AI providers."""

    def generate(self, prompt, max_tokens=300, temperature=0.3):
        raise NotImplementedError


class KnowledgeFallbackProvider(BaseProvider):
    """Answers from the approved company knowledge without an LLM.

    Used when no AI_PROVIDER / AI_API_KEY is configured. Provides a
    simple, safe, deterministic response based on keyword matching.
    """

    def generate(self, prompt, max_tokens=300, temperature=0.3):
        # The prompt contains the visitor message at the end.
        # Extract the last "User: ..." line.
        lines = prompt.strip().split("\n")
        user_line = ""
        for line in reversed(lines):
            if line.startswith("User:"):
                user_line = line[5:].strip()
                break

        context = build_company_context()
        return self._respond(user_line, context)

    def _respond(self, message, context):
        msg = message.lower()
        company = context["company"]
        services = context["services"]
        industries = context["industries"]
        products = context["products"]
        technologies = context["technologies"]

        # Services
        if any(k in msg for k in ["service", "offer", "provide", "do you do", "what do you"]):
            names = ", ".join(s["title"] for s in services[:6])
            return (
                f"Orientiq provides a range of services including {names}. "
                f"Each service is designed to help businesses build, scale, and transform "
                f"with technology. You can explore them at /services/."
            )

        # Industries
        if any(k in msg for k in ["industr", "sector", "field", "market"]):
            names = ", ".join(i["name"] for i in industries[:6])
            return (
                f"Orientiq serves a range of industries including {names}. "
                f"Each engagement is tailored to the specific challenges of the sector. "
                f"Learn more at /industries/."
            )

        # Technologies
        if any(k in msg for k in ["technolog", "stack", "tools", "tech"]):
            names = ", ".join(t["name"] for t in technologies[:8])
            return (
                f"Orientiq works with a modern technology ecosystem including {names}. "
                f"We choose the right tools for each challenge. See /technologies/ for details."
            )

        # Products
        if any(k in msg for k in ["product", "platform", "ai travel", "society", "business ai"]):
            names = ", ".join(p["name"] for p in products[:3])
            return (
                f"Orientiq is building a family of products including {names}. "
                f"These are showcased at /products/ and are currently in planning or early development."
            )

        # Start a project
        if any(k in msg for k in ["start", "project", "hire", "build", "quote", "estimate"]):
            return (
                "That sounds like a project Orientiq can help with. "
                "You can share your requirements through the Start a Project form at /start-project/. "
                "We typically respond within one business day."
            )

        # Company / about
        if any(k in msg for k in ["about", "who", "company", "mission", "vision", "values"]):
            return (
                f"{company['description']} "
                f"Mission: {company['mission']} "
                f"Vision: {company['vision']} "
                f"Learn more at /about/."
            )

        # Contact
        if any(k in msg for k in ["contact", "email", "reach", "phone"]):
            return (
                "You can reach Orientiq through the Contact page at /company/contact/ "
                "or submit a project inquiry at /start-project/."
            )

        # Careers
        if any(k in msg for k in ["career", "job", "join", "hiring"]):
            return (
                "Orientiq is always looking for exceptional engineers, designers, and strategists. "
                "See current opportunities at /company/careers/."
            )

        # Greeting
        if any(k in msg for k in ["hello", "hi ", "hey", "greetings"]):
            return (
                "Hello! I'm Orientiq AI, your guide to Orientiq. "
                "I can help you learn about our services, industries, technologies, products, "
                "and how to start a project. What would you like to know?"
            )

        # Default
        return (
            "I'm Orientiq AI, designed to help you understand Orientiq — our services, "
            "industries, technologies, products, and project process. "
            "If you have a question about those, I'd be happy to help. "
            "For project inquiries, you can also visit /start-project/."
        )


class OpenAIClientProvider(BaseProvider):
    """OpenAI-compatible provider adapter.

    Uses the OpenAI Python client if installed, otherwise raises AIProviderError.
    """

    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt, max_tokens=300, temperature=0.3):
        try:
            from openai import OpenAI
        except ImportError:
            raise AIProviderError("OpenAI client is not installed.")

        client = OpenAI(api_key=self.api_key)
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            raise AIProviderError(f"AI provider error: {exc}")


def get_provider():
    """Return the configured AI provider, or the knowledge fallback."""
    provider_name = os.getenv("AI_PROVIDER", "").strip().lower()
    api_key = os.getenv("AI_API_KEY", "").strip()
    model = os.getenv("AI_MODEL", "").strip()

    if provider_name == "openai" and api_key:
        return OpenAIClientProvider(api_key=api_key, model=model or "gpt-4o-mini")

    # No provider configured → knowledge fallback
    return KnowledgeFallbackProvider()


def generate_response(user_message, history=None):
    """Generate an AI response for a visitor message.

    Returns a dict with:
        - success: bool
        - message: str (sanitized)
        - suggestions: list of dicts {label, url}
    """
    history = history or []
    context = build_company_context()
    prompt = build_ai_prompt(context, history, user_message)

    provider = get_provider()
    try:
        raw = provider.generate(prompt)
    except AIProviderError:
        return {
            "success": False,
            "message": "I'm having trouble connecting right now. Please try again in a moment.",
            "suggestions": [],
        }

    text = sanitize_output(raw)
    if not text:
        return {
            "success": False,
            "message": "I'm having trouble connecting right now. Please try again in a moment.",
            "suggestions": [],
        }

    # Build relevant suggestions based on the message.
    suggestions = _suggestions_for(user_message, context)
    return {
        "success": True,
        "message": text,
        "suggestions": suggestions,
    }


def _suggestions_for(message, context):
    """Return relevant navigation suggestions for a message."""
    msg = message.lower()
    suggestions = []

    if any(k in msg for k in ["service", "offer", "provide"]):
        suggestions.append({"label": "View Services", "url": "/services/"})
    if any(k in msg for k in ["industr", "sector"]):
        suggestions.append({"label": "View Industries", "url": "/industries/"})
    if any(k in msg for k in ["product", "platform"]):
        suggestions.append({"label": "View Products", "url": "/products/"})
    if any(k in msg for k in ["technolog", "stack", "tools"]):
        suggestions.append({"label": "View Technologies", "url": "/technologies/"})
    if any(k in msg for k in ["about", "who", "company"]):
        suggestions.append({"label": "About Orientiq", "url": "/about/"})
    if any(k in msg for k in ["start", "project", "hire", "build", "quote", "estimate"]):
        suggestions.append({"label": "Start a Project", "url": "/start-project/"})

    # Always offer Start a Project as a conversion action when relevant.
    if not suggestions:
        suggestions.append({"label": "Start a Project", "url": "/start-project/"})

    return suggestions[:3]