"""Kolkata Metro — geocoding, nearest-station engine, and Stage 3 UI."""

from .distance_calculator import haversine_km, validate_coordinates
from .geocoding_service import GeocodeError, GeocodeResult, NominatimGeocoder
from .metro_service import MetroService, NearestStationResult, SearchResponse

__all__ = [
    "haversine_km",
    "validate_coordinates",
    "GeocodeError",
    "GeocodeResult",
    "NominatimGeocoder",
    "MetroService",
    "NearestStationResult",
    "SearchResponse",
    "render_metro_page",
]


def __getattr__(name: str):
    if name == "render_metro_page":
        from .metro_ui import render_metro_page

        return render_metro_page
    raise AttributeError(name)
