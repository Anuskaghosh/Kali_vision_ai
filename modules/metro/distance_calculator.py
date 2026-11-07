"""Straight-line (great-circle) distance helpers for Kolkata Metro Stage 2.

Distances are approximate kilometres via the Haversine formula.
They must NOT be labelled as walking distance or travel time.
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

EARTH_RADIUS_KM = 6371.0

# Broad sanity bounds for Greater Kolkata / West Bengal metro context
LAT_MIN, LAT_MAX = -90.0, 90.0
LON_MIN, LON_MAX = -180.0, 180.0


def validate_coordinates(lat: object, lon: object) -> Tuple[bool, Optional[str]]:
    """Return (ok, error_message). Accepts ints/floats; rejects None/NaN/out-of-range."""
    if lat is None or lon is None:
        return False, "missing_coordinates"
    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (TypeError, ValueError):
        return False, "non_numeric_coordinates"
    if not math.isfinite(lat_f) or not math.isfinite(lon_f):
        return False, "non_finite_coordinates"
    if not (LAT_MIN <= lat_f <= LAT_MAX and LON_MIN <= lon_f <= LON_MAX):
        return False, "coordinates_out_of_range"
    return True, None


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Approximate great-circle distance in kilometres between two WGS84 points."""
    ok1, err1 = validate_coordinates(lat1, lon1)
    ok2, err2 = validate_coordinates(lat2, lon2)
    if not ok1:
        raise ValueError(f"invalid origin coordinates: {err1}")
    if not ok2:
        raise ValueError(f"invalid destination coordinates: {err2}")

    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    d_phi = math.radians(float(lat2) - float(lat1))
    d_lambda = math.radians(float(lon2) - float(lon1))

    a = (
        math.sin(d_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_KM * c
