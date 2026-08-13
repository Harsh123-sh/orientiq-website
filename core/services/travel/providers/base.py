"""Base provider interfaces for travel inventory."""


class BaseFlightProvider:
    """Base interface for flight search providers."""

    def search_flights(self, params):
        raise NotImplementedError


class BaseHotelProvider:
    """Base interface for hotel search providers."""

    def search_hotels(self, params):
        raise NotImplementedError


class BaseActivityProvider:
    """Base interface for activity search providers."""

    def search_activities(self, params):
        raise NotImplementedError