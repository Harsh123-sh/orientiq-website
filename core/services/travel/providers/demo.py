"""Demo/mock travel inventory provider.

Clearly labeled demo data — NOT real availability.
"""

from .base import BaseActivityProvider, BaseFlightProvider, BaseHotelProvider


class DemoFlightProvider(BaseFlightProvider):
    """Returns clearly-labeled demo flight results."""

    def search_flights(self, params):
        origin = params.get("origin", "Ahmedabad")
        destination = params.get("destination", "Dubai")
        cabin = params.get("cabin_class", "economy")
        return [
            {
                "airline": "Demo Air",
                "flight_number": "DA101",
                "origin": origin,
                "destination": destination,
                "departure_time": "08:00",
                "arrival_time": "10:30",
                "duration": "2h 30m",
                "stops": 0,
                "cabin_class": cabin,
                "price": 120,
                "currency": "USD",
                "baggage": "1 checked bag included",
                "status": "demo",
            },
            {
                "airline": "Demo Express",
                "flight_number": "DE202",
                "origin": origin,
                "destination": destination,
                "departure_time": "14:00",
                "arrival_time": "17:00",
                "duration": "3h 00m",
                "stops": 1,
                "cabin_class": cabin,
                "price": 95,
                "currency": "USD",
                "baggage": "No checked bag",
                "status": "demo",
            },
        ]


class DemoHotelProvider(BaseHotelProvider):
    """Returns clearly-labeled demo hotel results."""

    def search_hotels(self, params):
        destination = params.get("destination", "Dubai")
        return [
            {
                "hotel_name": "Demo Grand Hotel",
                "location": destination,
                "rating": 4.5,
                "review_count": 1200,
                "room_type": "Deluxe King",
                "amenities": ["Free WiFi", "Pool", "Gym"],
                "price_per_night": 150,
                "total_price": 750,
                "currency": "USD",
                "availability": "demo",
                "image": "",
                "cancellation_policy": "Free cancellation up to 48h",
            },
            {
                "hotel_name": "Demo City Inn",
                "location": destination,
                "rating": 4.0,
                "review_count": 800,
                "room_type": "Standard Double",
                "amenities": ["Free WiFi", "Breakfast"],
                "price_per_night": 90,
                "total_price": 450,
                "currency": "USD",
                "availability": "demo",
                "image": "",
                "cancellation_policy": "Non-refundable",
            },
        ]


class DemoActivityProvider(BaseActivityProvider):
    """Returns clearly-labeled demo activity results."""

    def search_activities(self, params):
        destination = params.get("destination", "Dubai")
        return [
            {
                "activity_name": "Demo City Tour",
                "destination": destination,
                "category": "Sightseeing",
                "description": "A demo guided city tour.",
                "duration": "4h",
                "rating": 4.8,
                "review_count": 500,
                "price": 45,
                "currency": "USD",
                "availability": "demo",
                "meeting_point": "City center",
                "image": "",
            },
            {
                "activity_name": "Demo Desert Safari",
                "destination": destination,
                "category": "Adventure",
                "description": "A demo desert experience.",
                "duration": "6h",
                "rating": 4.9,
                "review_count": 900,
                "price": 80,
                "currency": "USD",
                "availability": "demo",
                "meeting_point": "Hotel pickup",
                "image": "",
            },
        ]