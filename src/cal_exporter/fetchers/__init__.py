"""Calendar fetchers for iCal and Google Calendar API."""

from .ical import ICalFetcher
from .local_ical import LocalICalFetcher

# Lazy import for GoogleAPIFetcher to avoid cryptography issues
def get_google_api_fetcher():
    """Get GoogleAPIFetcher class, raising ImportError if not available."""
    from .google_api import GoogleAPIFetcher
    return GoogleAPIFetcher

__all__ = ["ICalFetcher", "LocalICalFetcher", "get_google_api_fetcher"]
