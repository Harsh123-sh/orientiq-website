# Orentiq AI Assistant — Phase 6

## Architecture

```
Website (floating button + chat panel)
        ↓
Django APIs (POST /api/ai/chat/ and POST /api/ai/inquiries/)
        ↓
AI Service (core/ai/service.py)
        ↓
Provider Adapter (BaseProvider)
        ↓
LLM Provider (OpenAI) OR Knowledge Fallback
```

The AI service layer is designed so future product-specific AI systems can be added separately (e.g., Travel AI, Society AI, Business AI) without touching the company website assistant.

## AI Provider Configuration

The provider is configured through environment variables in `.env`:

```
AI_PROVIDER=          # e.g. "openai" (empty = knowledge fallback)
AI_API_KEY=           # server-side only, never in frontend code
AI_MODEL=             # e.g. "gpt-4o-mini"
INQUIRY_NOTIFICATION_EMAIL=  # optional business inquiry notification recipient
```

If `AI_PROVIDER` is empty or `AI_API_KEY` is missing, the assistant falls back to a **knowledge-based responder** that answers from the approved company context. The fallback is English-only; Hindi and Gujarati responses require a configured AI provider. The provider receives explicit language instructions and bounded conversation history.

## Environment Variables

| Variable | Purpose |
|---|---|
| `AI_PROVIDER` | Provider name (`openai` or empty) |
| `AI_API_KEY` | Server-side API key (never exposed) |
| `AI_MODEL` | Model name (e.g. `gpt-4o-mini`) |
| `INQUIRY_NOTIFICATION_EMAIL` | Optional recipient for saved chatbot inquiry notifications |
| `GOOGLE_MAPS_API_KEY` | Server-side key with Google Places API (New) enabled |
| `GOOGLE_PLACE_ID` | Optional verified Place ID fallback; the super-admin settings page can override it |
| `GOOGLE_BUSINESS_TIME_ZONE` | IANA timezone fallback; set the actual business timezone in admin settings |
| `CHATBOT_RETENTION_DAYS` | Consent-based transcript and inquiry-transcript retention period (default 180) |
| `CHATBOT_FILE_RETENTION_DAYS` | Private attachment retention period (default 180) |

## Knowledge Sources

Priority order:
1. **Published CMS content** — `Service`, `Industry`, `Product`, `PortfolioProject`, `Technology`, and `Testimonial` models (status=published / active=True)
2. **Approved static data** — `core/data.py` (services, industries, products, and technologies)
3. **Verified static company info** — ORENTIQ description, founder name, tagline, and public URLs

Private data is never included: admin notes, activity logs, inquiries, user profiles, passwords, API keys, internal settings.

## Security

- POST-only endpoint (`@require_POST`)
- Server-side message validation (empty / too long rejected)
- Simple per-IP rate limiting via Django cache (20 req/min)
- Chatbot inquiry endpoint has a separate per-IP submission limit and server-side form validation
- Inquiry form requires consent and uses a unique idempotency token and inquiry reference
- CSRF remains enabled for both public POST endpoints
- API key is server-side only — never in HTML, JS, or CSS
- AI output sanitized (markdown fences stripped, control chars removed)
- Frontend renders messages via `textContent` (XSS-safe)
- No stack traces or internal details exposed on errors
- No private CMS data returned

## API Endpoint

```
POST /api/ai/chat/
Content-Type: application/json

Request:
{ "message": "What services does Orentiq provide?", "history": [] }

Response:
{
  "success": true,
  "message": "Orentiq provides...",
  "suggestions": [ { "label": "View Services", "url": "/services/" } ]
}
```

Error responses: `400` (invalid input), `429` (rate limited), `503` (provider unavailable).

Clear project intent from chat returns `start_inquiry: true`; the browser then renders the consented, one-question-at-a-time form in the conversation.
The form submits via `POST /api/ai/inquiries/` and only displays a reference after the `ContactInquiry` record is saved.

Additional endpoints provide Google Place information, consultation availability/request submission, human support requests, and session-scoped data deletion. Consultation requests remain **requested**, not confirmed; Google Calendar event creation is not configured in this deployment.

## Frontend Behavior

- Floating local robot illustration launcher (bottom-right) with accessible tooltip
- Chat panel with header, messages, suggestions, input
- Enter to send, Shift+Enter for newline
- Typing indicator, error state, retry, clear conversation
- Suggested questions for ORENTIQ, its founder, services, industries, and starting a project
- Interactive project inquiry form, status/reference confirmation, and clear-state restoration
- Optional consent-based transcript retention, private reference-file uploads, and visitor data deletion
- English/Hindi/Gujarati AI language instructions; browser-native speech recognition and speech output are capability-gated
- Google business information card reports unavailable status until a verified Place and server-side key are configured
- Consultation requests are stored pending manual review; no appointment is confirmed by the chat
- CTA suggestions link to existing pages (`/services/`, `/start-project/`, etc.)
- Light/dark theme support via CSS variables
- Responsive (460px panel desktop, near-full-width mobile)
- `prefers-reduced-motion` respected
- ARIA labels, `aria-live` for new responses, keyboard focus management

## Testing

Run:

```bash
python manage.py check
python manage.py test core.tests.AIAssistantTests
python manage.py test core.tests.ChatbotInquiryTests core.tests.AdvancedChatbotTests
```

Tests cover chatbot validation, consent, knowledge grounding/follow-ups, inquiry idempotency, Google Place response parsing, pending consultation requests, support requests, admin permissions, private uploads, and visitor deletion.

## Error Handling

- Provider unavailable → user-friendly message ("I'm having trouble connecting right now...")
- Invalid API key → same friendly message (no details leaked)
- Timeout / network failure → friendly message + retry
- Rate limit → 429 with friendly message
- Invalid inquiry → field validation errors; no record is saved
- Inquiry notification mail is optional and cannot roll back a saved inquiry
- Configure and schedule `python manage.py purge_chatbot_data` to enforce the configured retention periods

## Google Business Setup

Enable the Google Places API (New), create a restricted server-side key, and enter the verified Place ID and actual IANA timezone in the super-admin Website Settings page. The public endpoint never returns credentials. Current status and special hours are shown only when Google returns the corresponding fields. Opening hours are cached for 15 minutes.

## External Setup Still Required

- Configure and test `AI_PROVIDER=openai`, `AI_API_KEY`, and `AI_MODEL` for live AI and full Hindi/Gujarati responses.
- Configure Google Places and verify the configured Place ID against the official ORENTIQ listing.
- Configure SMTP and `INQUIRY_NOTIFICATION_EMAIL` to deliver administrator notifications.
- Google Calendar integration is not implemented; consultation requests are availability-checked against active database requests and require manual confirmation.
- Schedule the retention management command in the deployment scheduler.

## Future Extension Points

- `core/ai/service.py` — add new provider adapters (e.g., Anthropic, Gemini)
- `core/ai/knowledge.py` — extend knowledge sources
- Future product AIs (Travel, Society, Business) can reuse the same service pattern with their own knowledge layers