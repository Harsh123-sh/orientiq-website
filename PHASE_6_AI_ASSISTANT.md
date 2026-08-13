# Orientiq AI Assistant — Phase 6

## Architecture

```
Website (floating button + chat panel)
        ↓
Django API (POST /api/ai/chat/)
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
```

If `AI_PROVIDER` is empty or `AI_API_KEY` is missing, the assistant falls back to a **knowledge-based responder** that answers from the approved company context. This keeps the assistant functional without an API key.

## Environment Variables

| Variable | Purpose |
|---|---|
| `AI_PROVIDER` | Provider name (`openai` or empty) |
| `AI_API_KEY` | Server-side API key (never exposed) |
| `AI_MODEL` | Model name (e.g. `gpt-4o-mini`) |

## Knowledge Sources

Priority order:
1. **Published CMS content** — `Service`, `Industry`, `Product`, `Technology`, `Testimonial` models (status=published / active=True)
2. **Approved static data** — `core/data.py` (services, industries, products, technologies, portfolio)
3. **Safe static company info** — mission, vision, values, URLs

Private data is never included: admin notes, activity logs, inquiries, user profiles, passwords, API keys, internal settings.

## Security

- POST-only endpoint (`@require_POST`)
- Server-side message validation (empty / too long rejected)
- Simple per-IP rate limiting via Django cache (20 req/min)
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
{ "message": "What services does Orientiq provide?", "history": [] }

Response:
{
  "success": true,
  "message": "Orientiq provides...",
  "suggestions": [ { "label": "View Services", "url": "/services/" } ]
}
```

Error responses: `400` (invalid input), `429` (rate limited), `503` (provider unavailable).

## Frontend Behavior

- Floating sparkle button (bottom-right)
- Chat panel with header, messages, suggestions, input
- Enter to send, Shift+Enter for newline
- Typing indicator, error state, retry, clear conversation
- Suggested questions (6 pre-defined)
- CTA suggestions link to existing pages (`/services/`, `/start-project/`, etc.)
- Light/dark theme support via CSS variables
- Responsive (400px panel desktop, full-width mobile)
- `prefers-reduced-motion` respected
- ARIA labels, `aria-live` for new responses, keyboard focus management

## Testing

Run:

```bash
python manage.py check
python manage.py test core.tests.AIAssistantTests
```

Tests cover: POST-only enforcement, empty/long message rejection, valid request, Start Project suggestion, API key non-exposure, knowledge content, private data exclusion, and access for anonymous/CLIENT/ADMIN/SUPER_ADMIN.

## Error Handling

- Provider unavailable → user-friendly message ("I'm having trouble connecting right now...")
- Invalid API key → same friendly message (no details leaked)
- Timeout / network failure → friendly message + retry
- Rate limit → 429 with friendly message

## Future Extension Points

- `core/ai/service.py` — add new provider adapters (e.g., Anthropic, Gemini)
- `core/ai/knowledge.py` — extend knowledge sources
- Future product AIs (Travel, Society, Business) can reuse the same service pattern with their own knowledge layers