"""Nominatim geocoding for Kolkata Metro Stage 2 (explicit search only).

Respects public Nominatim usage policy:
- identifying User-Agent
- max one request per second
- cache successful and unsuccessful queries
- no autocomplete against the public endpoint
"""

from __future__ import annotations

import json
import ssl
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

try:
    import certifi

    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:  # pragma: no cover - certifi normally present via requirements
    _SSL_CTX = ssl.create_default_context()

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
DEFAULT_USER_AGENT = (
    "KALI-VISION-AI/1.0 (Kolkata Metro Stage 2; educational; contact: local-dev)"
)
ATTRIBUTION = (
    "Location search powered by OpenStreetMap / Nominatim "
    "(https://www.openstreetmap.org/copyright)."
)

# West Bengal tokens seen in Nominatim address / display_name
_WB_STATE_TOKENS = (
    "west bengal",
    "wb",
    "পশ্চিমবঙ্গ",
)


class GeocodeError(Exception):
    """Raised for transport / parse failures (not empty or out-of-state results)."""


@dataclass
class GeocodeResult:
    query: str
    ok: bool
    lat: Optional[float] = None
    lon: Optional[float] = None
    display_name: Optional[str] = None
    place_id: Optional[Any] = None
    address: Dict[str, Any] = field(default_factory=dict)
    in_west_bengal: bool = False
    error: Optional[str] = None
    cached: bool = False
    attribution: str = ATTRIBUTION
    raw: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


def _normalize_query(q: str) -> str:
    return " ".join((q or "").strip().lower().split())


def is_west_bengal(hit: Dict[str, Any]) -> bool:
    """Validate that a Nominatim hit belongs to West Bengal, India."""
    address = hit.get("address") or {}
    candidates: List[str] = []
    for key in ("state", "state_district", "ISO3166-2-lvl4", "county", "region"):
        val = address.get(key)
        if isinstance(val, str) and val.strip():
            candidates.append(val)
    display = hit.get("display_name")
    if isinstance(display, str):
        candidates.append(display)

    blob = " | ".join(candidates).lower()
    if not blob.strip():
        return False
    # Prefer explicit state match
    state = (address.get("state") or "").strip().lower()
    if state:
        return any(tok == state or tok in state for tok in ("west bengal", "পশ্চিমবঙ্গ")) or state == "wb"
    return any(tok in blob for tok in _WB_STATE_TOKENS)


class NominatimGeocoder:
    """Explicit-search Nominatim client with rate limit and response cache."""

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        min_interval_sec: float = 1.0,
        timeout_sec: float = 12.0,
        countrycodes: str = "in",
        limit: int = 5,
        opener: Any = None,
    ) -> None:
        self.user_agent = user_agent
        self.min_interval_sec = max(1.0, float(min_interval_sec))
        self.timeout_sec = timeout_sec
        self.countrycodes = countrycodes
        self.limit = limit
        self._opener = opener  # injectable for tests
        self._lock = threading.Lock()
        self._last_request_monotonic: float = 0.0
        # Cache maps normalized query -> GeocodeResult snapshot (without mutating later)
        self._cache: Dict[str, GeocodeResult] = {}

    @property
    def attribution(self) -> str:
        return ATTRIBUTION

    def clear_cache(self) -> None:
        with self._lock:
            self._cache.clear()

    def cache_size(self) -> int:
        with self._lock:
            return len(self._cache)

    def _throttle(self) -> None:
        with self._lock:
            now = time.monotonic()
            wait = self.min_interval_sec - (now - self._last_request_monotonic)
            if wait > 0:
                time.sleep(wait)
            self._last_request_monotonic = time.monotonic()

    def _http_get_json(self, url: str) -> List[Dict[str, Any]]:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "application/json",
            },
            method="GET",
        )
        try:
            if self._opener is not None:
                with self._opener.open(req, timeout=self.timeout_sec) as resp:
                    body = resp.read().decode("utf-8")
            else:
                with urllib.request.urlopen(
                    req, timeout=self.timeout_sec, context=_SSL_CTX
                ) as resp:
                    body = resp.read().decode("utf-8")
            data = json.loads(body)
        except urllib.error.HTTPError as e:
            raise GeocodeError(f"nominatim_http_{e.code}") from e
        except urllib.error.URLError as e:
            raise GeocodeError(f"nominatim_connection_failed: {e.reason}") from e
        except TimeoutError as e:
            raise GeocodeError("nominatim_timeout") from e
        except json.JSONDecodeError as e:
            raise GeocodeError("nominatim_invalid_json") from e

        if not isinstance(data, list):
            raise GeocodeError("nominatim_unexpected_payload")
        return data

    def search(self, query: str) -> GeocodeResult:
        """Geocode an explicit search string. Does not perform autocomplete."""
        raw_q = (query or "").strip()
        if not raw_q:
            return GeocodeResult(query=raw_q, ok=False, error="empty_query")

        key = _normalize_query(raw_q)
        with self._lock:
            cached = self._cache.get(key)
        if cached is not None:
            # Return a copy marked as cached
            return GeocodeResult(
                query=cached.query,
                ok=cached.ok,
                lat=cached.lat,
                lon=cached.lon,
                display_name=cached.display_name,
                place_id=cached.place_id,
                address=dict(cached.address or {}),
                in_west_bengal=cached.in_west_bengal,
                error=cached.error,
                cached=True,
                attribution=ATTRIBUTION,
                raw=cached.raw,
            )

        params = {
            "q": raw_q,
            "format": "jsonv2",
            "countrycodes": self.countrycodes,
            "addressdetails": "1",
            "limit": str(self.limit),
        }
        url = f"{NOMINATIM_SEARCH_URL}?{urllib.parse.urlencode(params)}"

        try:
            self._throttle()
            hits = self._http_get_json(url)
        except GeocodeError as e:
            result = GeocodeResult(query=raw_q, ok=False, error=str(e))
            with self._lock:
                self._cache[key] = result
            return GeocodeResult(**{**asdict(result), "cached": False})

        if not hits:
            result = GeocodeResult(query=raw_q, ok=False, error="no_results")
            with self._lock:
                self._cache[key] = result
            return result

        # Prefer first hit that is in West Bengal; else report out-of-state
        wb_hit = None
        for hit in hits:
            if is_west_bengal(hit):
                wb_hit = hit
                break

        if wb_hit is None:
            first = hits[0]
            result = GeocodeResult(
                query=raw_q,
                ok=False,
                lat=_safe_float(first.get("lat")),
                lon=_safe_float(first.get("lon")),
                display_name=first.get("display_name"),
                place_id=first.get("place_id"),
                address=dict(first.get("address") or {}),
                in_west_bengal=False,
                error="outside_west_bengal",
                raw=first,
            )
            with self._lock:
                self._cache[key] = result
            return result

        lat = _safe_float(wb_hit.get("lat"))
        lon = _safe_float(wb_hit.get("lon"))
        if lat is None or lon is None:
            result = GeocodeResult(
                query=raw_q,
                ok=False,
                error="invalid_geocode_coordinates",
                display_name=wb_hit.get("display_name"),
                raw=wb_hit,
            )
            with self._lock:
                self._cache[key] = result
            return result

        result = GeocodeResult(
            query=raw_q,
            ok=True,
            lat=lat,
            lon=lon,
            display_name=wb_hit.get("display_name"),
            place_id=wb_hit.get("place_id"),
            address=dict(wb_hit.get("address") or {}),
            in_west_bengal=True,
            raw=wb_hit,
        )
        with self._lock:
            self._cache[key] = result
        return result


def _safe_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None
