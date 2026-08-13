# Orientiq Travel Inventory Foundation — Phase 8

## Architecture

```
User
  ↓
Travel Search UI (/travel-search/)
  ↓
Django API (/api/flights/search/, /api/hotels/search/, /api/activities/search/)
  ↓
Travel Services (core/services/travel/)
  ↓
Provider Abstraction (BaseFlightProvider, BaseHotelProvider, BaseActivityProvider)
  ↓
Demo Provider (clearly labeled mock data)
```

The system is provider-independent. Real travel APIs can be connected later by implementing the base provider interfaces without changing the UI or services.

## Services

- `core/services/travel/flights.py` — Flight search with validation (origin, destination, dates, trip type, passengers, cabin class) + sorting (cheapest/fastest/recommended)
- `core/services/travel/hotels.py` — Hotel search with validation (destination, check-in/out, guests, rooms) + sorting (price/rating/recommended)
- `core/services/travel/activities.py` — Activity search with validation (destination, date, guests) + category filter + sorting (price/rating/recommended)

## Provider Abstraction

- `core/services/travel/providers/base.py` — Base interfaces
- `core/services/travel/providers/demo.py` — Demo/mock provider (clearly labeled `status: "demo"`)

## Normalized Result Formats

**Flight:**
```json
{
  "airline": "Demo Air",
  "flight_number": "DA101",
  "origin": "Ahmedabad",
  "destination": "Dubai",
  "departure_time": "08:00",
  "arrival_time": "10:30",
  "duration": "2h 30m",
  "stops": 0,
  "cabin_class": "economy",
  "price": 120,
  "currency": "USD",
  "baggage": "1 checked bag included",
  "status": "demo"
}
```

**Hotel:**
```json
{
  "hotel_name": "Demo Grand Hotel",
  "location": "Dubai",
  "rating": 4.5,
  "review_count": 1200,
  "room_type": "Deluxe King",
  "amenities": ["Free WiFi", "Pool", "Gym"],
  "price_per_night": 150,
  "total_price": 750,
  "currency": "USD",
  "availability": "demo",
  "cancellation_policy": "Free cancellation up to 48h"
}
```

**Activity:**
```json
{
  "activity_name": "Demo City Tour",
  "destination": "Dubai",
  "category": "Sightseeing",
  "description": "A demo guided city tour.",
  "duration": "4h",
  "rating": 4.8,
  "review_count": 500,
  "price": 45,
  "currency": "USD",
  "availability": "demo",
  "meeting_point": "City center"
}
```

## APIs

- `GET /api/flights/search/?origin=...&destination=...&departure=...&trip_type=...&return=...&adults=...&cabin_class=...&sort=...`
- `GET /api/hotels/search/?destination=...&check_in=...&check_out=...&guests=...&rooms=...&sort=...`
- `GET /api/activities/search/?destination=...&date=...&guests=...&sort=...`

All return `{"success": true, "results": [...], "demo": true}` or `{"success": false, "error": "..."}` with appropriate HTTP status codes.

## UI

`/travel-search/` — premium demo page with three tabs (Flights, Hotels, Activities), polished search forms (including trip type and return date for flights), result cards, loading/empty/error states, and clear "demo data" labeling. Uses the existing Phase 1 design system (light/dark theme, responsive).

## Mock/Demo Data

All results are clearly labeled `status: "demo"` / `availability: "demo"` and the UI shows "(Demo data — not real availability)". No real availability is implied.

## Future Real-Provider Integration

Implement the base provider interfaces (e.g., Amadeus, Sabre, Booking.com, Viator) and swap the provider in the service layer. No UI or service changes required.

## Security

- Server-side input validation (dates, passengers, guests, rooms, cabin class)
- Safe JSON errors (no stack traces, no API keys)
- No provider credentials exposed to frontend
- Caching with deterministic hashed keys
- No database persistence (search results are stateless)

## Caching

- Flight/hotel/activity searches cached for 10 minutes using Django's cache framework
- Deterministic hashed cache keys

## Testing

`core/tests.py` — `TravelInventoryTests` (20 tests):
- Flights: valid, missing origin, missing dates, invalid date, invalid passengers, same origin/destination, cheapest sort
- Hotels: valid, missing destination, invalid dates, rating sort
- Activities: valid, missing destination, price sort
- APIs: flights valid/invalid, hotels, activities, no API key exposure
- Demo page renders

## Phase 8 Boundaries

**NOT implemented:** booking, checkout, payment, orders, refunds, ticket issuance, hotel reservation, activity reservation, real payment gateway, complete AI itinerary, production travel API integration, customer travel dashboard, travel admin operations.