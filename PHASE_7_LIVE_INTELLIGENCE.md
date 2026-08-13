# Orientiq Live Intelligence Foundation — Phase 7

## 1. Objective

Create a reusable location, maps, weather, and live-data infrastructure that future Orientiq products (especially the AI Travel Platform) will use. This is a foundation only — no booking, flights, hotels, activities, payments, or full travel planning.

## 2. Architecture

```
User
  ↓
Live Intelligence Service (core/services/live_intelligence.py)
  ↓
Location Service → Maps Service → Weather Service
  ↓
Future AI / Travel Products
```

External APIs are never called directly from templates. All access goes through the service layer.

## 3. Location Service

`core/services/location_service.py`
- Search locations by name (case-insensitive)
- Look up a single location
- Coordinate lookup/validation
- Built-in fallback set of common destinations (Dubai, London, Paris, Tokyo, Singapore, Mumbai, Delhi, Bengaluru, Ahmedabad, New York)
- Cached (10 min)

## 4. Maps Service

`core/services/maps_service.py`
- Provider abstraction (`BaseMapsProvider`)
- Static fallback provider (OpenStreetMap embed, no API key needed)
- Normalized map data (coordinates, embed URL, marker)
- Cached (1 hour)

## 5. Weather Service

`core/services/weather_service.py`
- Provider abstraction (`BaseWeatherProvider`)
- Static fallback provider (deterministic normalized response)
- Normalized weather data (temperature, condition, humidity, wind)
- Cached (10 min)

## 6. Live Intelligence Service

`core/services/live_intelligence.py`
- Combines location + weather + map into one result
- Status: `success` / `partial` / `unavailable`
- Designed for future modules (traffic, events, travel alerts) to be added without rewriting

## 7. Providers

Configured via environment variables:
```
MAP_PROVIDER=
MAPS_API_KEY=
WEATHER_PROVIDER=
WEATHER_API_KEY=
```
When keys are missing, safe static fallbacks are used. The system continues to work without API keys.

## 8. Environment Variables

See `.env.example`. All keys are server-side only; never exposed to browser, templates, or public JSON.

## 9. Caching

- Location search: 10 min
- Weather: 10 min
- Map/geocode: 1 hour
- Uses Django's cache framework

## 10. Rate Limiting

Reuses the Phase 6 per-IP cache-based rate limiting approach for the AI endpoint. External API usage is server-side and protected by caching to avoid unnecessary repeated calls.

## 11. API Endpoints

- `GET /api/location/search/?q=...` — location search
- `GET /api/weather/?q=...` — current weather
- `GET /api/live-intelligence/?q=...` — combined live intelligence

All return normalized JSON: `{"success": true, "data": {...}}` or `{"success": false, "error": "..."}`.

## 12. Error Handling

Every service handles: invalid location, missing location, provider unavailable, timeout, malformed response, rate limit, auth failure. Returns safe normalized errors — never API keys, stack traces, or internal paths.

## 13. Security

- CSRF protection
- Server-side validation
- Environment-based secrets
- No secret exposure in responses
- Rate limiting
- No private admin information exposed

## 14. Testing

`core/tests.py` — `LiveIntelligenceTests` (15 tests):
- Location: valid, invalid, empty
- Weather: valid, invalid location
- Maps: valid, invalid coordinates
- Live intelligence: success, unknown, empty
- API endpoints: location, weather, live-intelligence, missing query
- Security: no API keys exposed
- Demo page renders

Run: `python manage.py test core.tests.LiveIntelligenceTests`

## 15. Future Extension Points

- Add concrete providers (Google Maps, Mapbox, OpenWeatherMap) behind the existing abstraction
- Add traffic, events, travel alerts, local info modules to live_intelligence
- Reuse the service layer for the AI Travel Platform

---

**Phase 8+ functionality has NOT been implemented.** No flights, no hotels, no activities, no booking, no payments, no orders, no complete travel itinerary, no complete AI travel planner.