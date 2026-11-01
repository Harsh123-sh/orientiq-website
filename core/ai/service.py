"""AI service layer for the ORENTIQ AI assistant.

Architecture:
    Website → Django API → AI Service → Provider Adapter → LLM Provider

If no AI provider is configured (AI_PROVIDER / AI_API_KEY), the service
falls back to a knowledge-based responder that answers from the approved
company context. This keeps the assistant functional without an API key.
"""

import logging
import os

from .knowledge import build_company_context
from .prompts import build_ai_prompt
from .safety import sanitize_output

logger = logging.getLogger(__name__)

class AIProviderError(Exception):
    """Raised when the AI provider fails."""


class BaseProvider:
    """Base class for AI providers."""

    def generate(self, prompt, max_tokens=300, temperature=0.3):
        raise NotImplementedError


class KnowledgeFallbackProvider(BaseProvider):
    """Answers from approved company knowledge when no LLM is configured.

    The API identifies this restricted mode for the chat interface.
    """

    def __init__(self, context=None):
        self.context = context or build_company_context()

    def generate(self, prompt, max_tokens=300, temperature=0.3):
        user_message = prompt[-1]["content"] if prompt else ""
        system_prompt = prompt[0]["content"] if prompt else ""
        if "Respond in Hindi." in system_prompt:
            return (
                "हिंदी में विस्तृत उत्तर अभी उपलब्ध नहीं है। यह चैट अभी केवल सत्यापित अंग्रेज़ी "
                "जानकारी मोड में चल रही है। कृपया अंग्रेज़ी में पूछें या सीधे ORENTIQ से संपर्क करें।"
            )
        if "Respond in Gujarati." in system_prompt:
            return (
                "ગુજરાતીમાં વિગતવાર જવાબ હાલમાં ઉપલબ્ધ નથી. આ ચેટ હાલમાં ફક્ત ચકાસેલી અંગ્રેજી "
                "માહિતી મોડમાં કાર્યરત છે. કૃપા કરીને અંગ્રેજીમાં પૂછો અથવા ORENTIQનો સીધો સંપર્ક કરો."
            )
        if any("\u0900" <= char <= "\u097f" for char in user_message):
            return (
                "हिंदी में विस्तृत उत्तर अभी उपलब्ध नहीं है। यह चैट अभी केवल सत्यापित अंग्रेज़ी "
                "जानकारी मोड में चल रही है। कृपया अंग्रेज़ी में पूछें या सीधे ORENTIQ से संपर्क करें।"
            )
        if any("\u0a80" <= char <= "\u0aff" for char in user_message):
            return (
                "ગુજરાતીમાં વિગતવાર જવાબ હાલમાં ઉપલબ્ધ નથી. આ ચેટ હાલમાં ફક્ત ચકાસેલી અંગ્રેજી "
                "માહિતી મોડમાં કાર્યરત છે. કૃપા કરીને અંગ્રેજીમાં પૂછો અથવા ORENTIQનો સીધો સંપર્ક કરો."
            )
        prior_messages = prompt[1:-1] if len(prompt) > 2 else []
        prior_user = next(
            (item["content"] for item in reversed(prior_messages) if item["role"] == "user"),
            "",
        )
        prior_assistant = next(
            (item["content"] for item in reversed(prior_messages) if item["role"] == "assistant"),
            "",
        )
        return self._respond(
            user_message,
            self.context,
            previous_user=prior_user,
            previous_assistant=prior_assistant,
        )

    def _respond(self, message, context, previous_user="", previous_assistant=""):
        msg = message.lower()
        company = context["company"]
        services = context["services"]
        industries = context["industries"]
        products = context["products"]
        technologies = context["technologies"]
        portfolio = context.get("portfolio", [])
        contact = context["contact"]

        if any(term in msg for term in ("tell me more", "more details", "more detail", "and that", "about it", "about this")):
            previous_context = f"{previous_user} {previous_assistant}".lower()
            related_services = [
                service for service in services
                if service["title"].lower() in previous_context
            ]
            if not related_services:
                related_services = self._matching_services(previous_user.lower(), services)
            if related_services:
                return "\n".join(
                    self._service_answer(service) for service in related_services[:3]
                )
            related_products = [
                product for product in products
                if product["name"].lower() in previous_context
            ]
            if related_products:
                return "\n".join(
                    f"{product['name']}: {product['description']} {product.get('url', company['urls']['products'])}"
                    for product in related_products[:3]
                )
            return "I can help with a follow-up, but I need to know which ORENTIQ service or product you mean."

        for faq in context.get("faqs", []):
            question_terms = {
                term for term in faq["question"].lower().split()
                if len(term) > 3
            }
            if question_terms and len(question_terms.intersection(msg.split())) >= max(1, len(question_terms) // 2):
                return faq["answer"]

        if any(k in msg for k in ["consultation", "consult", "nda", "non-disclosure", "obligation", "pressure"]):
            return (
                f"{contact['initial_consultation']}; {contact['engagement_terms']}. "
                f"{contact['nda']} Contact ORENTIQ at {contact['email']} to discuss."
            )

        if any(k in msg for k in ["pricing", "price", "how much", "cost", "rates"]):
            return (
                "I don't have verified pricing information to share. Project costs depend on "
                f"the scope and requirements. You can discuss them during a {contact['initial_consultation'].lower()}."
            )

        if any(k in msg for k in ["founder", "founded", "who started", "who created"]):
            founder = company["founder"]
            return (
                f"ORENTIQ Technologies was founded by {founder['name']}, "
                f"the {founder['role']}. Learn more: {founder['url']}."
            )

        if any(k in msg for k in ["logo", "monogram", "meaning of the mark"]):
            return f"{company['logo_meaning']} Learn more: {company['urls']['founder']}."

        if any(k in msg for k in ["response time", "how long", "when will", "when can i expect"]):
            return (
                f"ORENTIQ aims to respond {contact['response_time'].lower()}. "
                f"You can also contact us at {contact['email']}."
            )

        if any(k in msg for k in ["portfolio", "case study", "past project", "previous project"]):
            if portfolio:
                projects = "; ".join(
                    f"{item['title']}: {item['summary']}" for item in portfolio[:5]
                )
                return f"Published ORENTIQ projects include: {projects}."
            return (
                "I don't have published project details available to share right now. "
                f"You can ask the ORENTIQ team: {contact['email']}."
            )

        if any(k in msg for k in ["contact", "email", "reach", "phone", "whatsapp"]):
            return (
                f"Email: {contact['email']}\n"
                f"Phone: {contact['phone']} ({contact['phone_uri']})\n"
                f"WhatsApp: {contact['whatsapp_uri']}\n"
                f"Website: {contact['website']}\n"
                f"Or submit a project inquiry: {company['urls']['start_project']}."
            )

        if any(k in msg for k in ["service", "offer", "provide", "do you do", "what do you"]):
            matching_services = self._matching_services(msg, services)
            if matching_services:
                return "\n".join(self._service_answer(item) for item in matching_services)
            return "ORENTIQ's services include:\n" + "\n".join(
                f"- {item['title']}: {item.get('short_description') or item.get('description') or item.get('category', '')} {item['url']}"
                for item in services
            )

        if any(k in msg for k in ["industr", "sector", "field", "market"]):
            return "ORENTIQ's listed industries include:\n" + "\n".join(
                f"- {item['name']}: {item.get('description', '')} {item.get('url', '/industries/')}"
                for item in industries
            )

        if any(k in msg for k in ["technolog", "stack", "tools", "tech"]):
            groups = {}
            for item in technologies:
                groups.setdefault(item["category"], []).append(item["name"])
            return "The website lists these technologies by area:\n" + "\n".join(
                f"- {category}: {', '.join(names)}"
                for category, names in groups.items()
            ) + f"\nMore: {company['urls']['technologies']}."

        if any(k in msg for k in ["what does orentiq do", "what do orentiq do", "what do you do", "who are you"]):
            return f"{company['description']} Learn more: {company['urls']['about']}."

        if any(k in msg for k in ["process", "how do you work", "development stages", "workflow"]):
            return "ORENTIQ's delivery process is:\n" + "\n".join(
                f"- {step['name']}: {step['description']}" for step in context["process"]
            ) + f"\nMore: {company['urls']['process']}."

        if "mission" in msg or "company vision" in msg or "values" in msg:
            return (
                "I don't have a separate published company mission or values statement "
                f"in the verified information available. Learn about ORENTIQ: {company['urls']['about']}."
            )

        if "vision" in msg and any(word in msg for word in ["product", "platform"]):
            matching_products = [
                product for product in products
                if product.get("vision")
                and any(
                    word in msg
                    for word in product["name"].lower().split()
                    if word not in {"ai", "the", "of", "platform"}
                )
            ]
            if matching_products:
                return "\n".join(
                    f"{product['name']}: {product['vision']} {product['url']}"
                    for product in matching_products
                )

        if any(k in msg for k in ["website", "web site", "dashboard", "automation", "software", "mobile app"]):
            matching = self._matching_services(msg, services)
            if matching:
                return "\n".join(self._service_answer(item) for item in matching)

        if any(k in msg for k in ["product", "platform", "ai travel", "society", "business ai"]):
            if not products:
                return f"I don't have current product information available. See {company['urls']['products']}."
            return "ORENTIQ's listed products are:\n" + "\n".join(
                f"- {item['name']} ({item['status']}): {item['description']} {item.get('url', company['urls']['products'])}"
                for item in products
            )

        if any(k in msg for k in ["start", "project", "hire", "build", "quote", "estimate"]):
            return (
                "I can help you start a project inquiry here. "
                "If you would like, tell me you want to submit an inquiry, or visit "
                f"{company['urls']['start_project']}. ORENTIQ aims to respond "
                f"{contact['response_time'].lower()}."
            )

        if (
            "about orentiq" in msg
            or "about the company" in msg
            or msg.strip().rstrip("?!.") in {"what is orentiq", "what is the company orentiq"}
        ):
            return f"{company['description']} Learn more: {company['urls']['about']}."

        if any(k in msg for k in ["career", "job", "join", "hiring"]):
            return f"See ORENTIQ's careers page for current opportunities: {company['urls']['careers']}."

        if msg.strip() in {"hi", "hey", "hello", "greetings"} or any(
            k in msg for k in ["hello", "hi ", "hey", "greetings"]
        ):
            return (
                "Hello! I'm ORENTIQ's website assistant. "
                "I can help you learn about our services, industries, technologies, products, "
                "and how to start a project. What would you like to know?"
            )

        return (
            "I don't have verified information to answer that yet. "
            f"Please contact ORENTIQ at {contact['email']} or submit a project inquiry "
            f"at {company['urls']['start_project']}."
        )

    @staticmethod
    def _matching_services(message, services):
        aliases = {
            "web": ("web development", "website", "web site", "business website"),
            "software": ("software", "custom software", "business dashboard", "dashboard"),
            "mobile": ("mobile", "app development", "mobile app", "application"),
            "ai": ("ai", "automation", "artificial intelligence"),
            "design": ("ui/ux", "design", "user experience"),
            "cloud": ("cloud", "devops", "infrastructure"),
        }
        selected = set()
        for service in services:
            title = service["title"].lower()
            for group, terms in aliases.items():
                if group in title and any(term in message for term in terms):
                    selected.add(service["title"])
            if title in message:
                selected.add(service["title"])
        return [service for service in services if service["title"] in selected]

    @staticmethod
    def _service_answer(service):
        description = (
            service.get("short_description")
            or service.get("description")
            or service.get("category")
            or "See the service page for details."
        )
        return f"{service['title']}: {description} {service.get('url', '/services/')}"


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
        except ImportError as exc:
            raise AIProviderError("OpenAI client is not installed.") from exc

        try:
            client = OpenAI(api_key=self.api_key, timeout=20)
            response = client.chat.completions.create(
                model=self.model,
                messages=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            raise AIProviderError("The configured AI provider request failed.") from exc


def get_provider(context=None):
    """Return the configured AI provider, or the knowledge fallback."""
    provider_name = os.getenv("AI_PROVIDER", "").strip().lower()
    api_key = os.getenv("AI_API_KEY", "").strip()
    model = os.getenv("AI_MODEL", "").strip()

    if provider_name in {"", "knowledge"} and not api_key:
        return KnowledgeFallbackProvider(context or build_company_context())
    if provider_name == "openai" and api_key:
        return OpenAIClientProvider(api_key=api_key, model=model or "gpt-4o-mini")
    raise AIProviderError("AI provider configuration is incomplete or unsupported.")


def generate_response(user_message, history=None, language="auto"):
    """Generate an AI response for a visitor message.

    Returns a dict with:
        - success: bool
        - message: str (sanitized)
        - suggestions: list of dicts {label, url}
    """
    history = history or []
    context = build_company_context()
    prompt = build_ai_prompt(context, history, user_message, language)

    try:
        provider = get_provider(context)
        raw = provider.generate(prompt)
    except AIProviderError:
        logger.warning("The AI assistant could not use its configured response provider.")
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
        "mode": "knowledge" if isinstance(provider, KnowledgeFallbackProvider) else "ai",
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
        suggestions.append({"label": "About ORENTIQ", "url": "/about/"})
    if any(k in msg for k in ["start", "project", "hire", "build", "quote", "estimate"]):
        suggestions.append({"label": "Start a Project", "url": "/start-project/"})

    # Always offer Start a Project as a conversion action when relevant.
    if not suggestions:
        suggestions.append({"label": "Start a Project", "url": "/start-project/"})

    return suggestions[:3]