"""Free OpenStreetMap routing via the public OSRM demo (FOSSGIS).

Supported profiles (only these are exposed to the UI):
  - foot     → Walking
  - bike     → Cycling
  - driving  → Driving

Usage policy (demo server): ≤1 req/s, identifying User-Agent, ODbL attribution.
Not for heavy/production load. See https://routing.openstreetmap.de/about.html
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
from typing import Any, Dict, List, Optional, Tuple

try:
    import certifi

    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:  # pragma: no cover
    _SSL_CTX = ssl.create_default_context()

OSRM_BASE = "https://router.project-osrm.org/route/v1"
DEFAULT_USER_AGENT = (
    "KALI-VISION-AI/1.0 (Kolkata Metro journey planner; educational; contact: local-dev)"
)
ATTRIBUTION = (
    "Routes © OSRM / FOSSGIS — OpenStreetMap data © ODbL contributors "
    "(https://www.openstreetmap.org/copyright)."
)

# UI label → OSRM profile path segment
TRAVEL_MODES: Dict[str, str] = {
    "Walking": "foot",
    "Cycling": "bike",
    "Driving": "driving",
}


@dataclass
class RouteStep:
    instruction: str
    distance_m: float
    duration_s: float
    name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RouteResult:
    ok: bool
    profile: str
    mode_label: str
    distance_m: Optional[float] = None
    duration_s: Optional[float] = None
    geometry: Optional[Dict[str, Any]] = None  # GeoJSON LineString
    steps: List[RouteStep] = field(default_factory=list)
    error: Optional[str] = None
    attribution: str = ATTRIBUTION

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    @property
    def distance_km(self) -> Optional[float]:
        if self.distance_m is None:
            return None
        return round(self.distance_m / 1000.0, 2)

    @property
    def duration_min(self) -> Optional[float]:
        if self.duration_s is None:
            return None
        return round(self.duration_s / 60.0, 1)


def _format_instruction(step: Dict[str, Any]) -> str:
    man = step.get("maneuver") or {}
    mtype = (man.get("type") or "").replace("_", " ")
    modifier = (man.get("modifier") or "").replace("_", " ")
    name = (step.get("name") or "").strip()
    bits = [p for p in (mtype.title(), modifier) if p]
    base = " ".join(bits).strip() or "Continue"
    if name:
        return f"{base} onto {name}"
    return base


class OsrmRouter:
    """Thin OSRM client with throttle + optional injectable opener (tests)."""

    def __init__(
        self,
        base_url: str = OSRM_BASE,
        user_agent: str = DEFAULT_USER_AGENT,
        min_interval_sec: float = 1.05,
        timeout_sec: float = 20.0,
        opener: Any = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.min_interval_sec = max(1.0, float(min_interval_sec))
        self.timeout_sec = timeout_sec
        self._opener = opener
        self._lock = threading.Lock()
        self._last_request_monotonic: float = 0.0

    def _throttle(self) -> None:
        with self._lock:
            now = time.monotonic()
            wait = self.min_interval_sec - (now - self._last_request_monotonic)
            if wait > 0:
                time.sleep(wait)
            self._last_request_monotonic = time.monotonic()

    def _http_get_json(self, url: str) -> Dict[str, Any]:
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
            raise RuntimeError(f"osrm_http_{e.code}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"osrm_connection_failed: {e.reason}") from e
        except TimeoutError as e:
            raise RuntimeError("osrm_timeout") from e
        except json.JSONDecodeError as e:
            raise RuntimeError("osrm_invalid_json") from e

        if not isinstance(data, dict):
            raise RuntimeError("osrm_unexpected_payload")
        return data

    def route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        *,
        mode_label: str = "Walking",
    ) -> RouteResult:
        """Compute a route. origin/destination are (lat, lon)."""
        label = mode_label if mode_label in TRAVEL_MODES else "Walking"
        profile = TRAVEL_MODES[label]
        olat, olon = float(origin[0]), float(origin[1])
        dlat, dlon = float(destination[0]), float(destination[1])

        coords = f"{olon},{olat};{dlon},{dlat}"
        qs = urllib.parse.urlencode(
            {
                "overview": "full",
                "geometries": "geojson",
                "steps": "true",
                "annotations": "false",
            }
        )
        url = f"{self.base_url}/{profile}/{coords}?{qs}"

        try:
            self._throttle()
            data = self._http_get_json(url)
        except RuntimeError as e:
            return RouteResult(
                ok=False, profile=profile, mode_label=label, error=str(e)
            )

        code = data.get("code")
        if code != "Ok":
            return RouteResult(
                ok=False,
                profile=profile,
                mode_label=label,
                error=f"osrm_{str(code or 'error').lower()}",
            )

        routes = data.get("routes") or []
        if not routes:
            return RouteResult(
                ok=False, profile=profile, mode_label=label, error="osrm_no_route"
            )

        best = routes[0]
        geometry = best.get("geometry")
        distance_m = best.get("distance")
        duration_s = best.get("duration")

        steps: List[RouteStep] = []
        for leg in best.get("legs") or []:
            for step in leg.get("steps") or []:
                steps.append(
                    RouteStep(
                        instruction=_format_instruction(step),
                        distance_m=float(step.get("distance") or 0),
                        duration_s=float(step.get("duration") or 0),
                        name=str(step.get("name") or ""),
                    )
                )

        return RouteResult(
            ok=True,
            profile=profile,
            mode_label=label,
            distance_m=float(distance_m) if distance_m is not None else None,
            duration_s=float(duration_s) if duration_s is not None else None,
            geometry=geometry if isinstance(geometry, dict) else None,
            steps=steps,
        )
