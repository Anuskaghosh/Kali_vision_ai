"""Kolkata Metro Stage 2 service: dataset load, eligibility, nearest stations.

Independent of Streamlit UI. Optional Streamlit cache for the JSON dataset only.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .distance_calculator import haversine_km, validate_coordinates
from .geocoding_service import ATTRIBUTION, GeocodeResult, NominatimGeocoder

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = ROOT / "data" / "kolkata_metro_stations.json"

OPERATIONAL = "operational"
EXCLUSION_PRIORITY = (
    "missing_coordinates",
    "invalid_coordinates",
    "manual_coordinate_verification",
    "coordinates_not_verified",
    "no_operational_line",
)


@dataclass
class LineInfo:
    line: str
    status: str
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"line": self.line, "status": self.status}
        if self.notes:
            d["notes"] = self.notes
        return d


@dataclass
class NearestStationResult:
    station_id: str
    name: str
    approximate_distance_km: float
    lat: float
    lon: float
    operational_lines: List[LineInfo]
    primary_status: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    station_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "station_id": self.station_id,
            "name": self.name,
            "station_code": self.station_code,
            "approximate_distance_km": round(self.approximate_distance_km, 3),
            "distance_note": (
                "Approximate straight-line distance in kilometres (Haversine). "
                "Not walking distance or travel time."
            ),
            "lat": self.lat,
            "lon": self.lon,
            "operational_status": OPERATIONAL,
            "lines": [ln.to_dict() for ln in self.operational_lines],
            # Convenience: primary metro line label(s)
            "metro_lines": [ln.line for ln in self.operational_lines],
            "primary_status": self.primary_status,
            "sources": self.sources,
        }


@dataclass
class SearchResponse:
    mode: str  # "default" | "nearest"
    query: Optional[str]
    geocode: Optional[Dict[str, Any]]
    nearest_stations: List[Dict[str, Any]]
    eligible_station_count: int
    excluded_station_count: int
    excluded_by_reason: Dict[str, int]
    verified_coordinate_stations: List[Dict[str, Any]]
    line_explorer_unverified: List[Dict[str, Any]]
    line_explorer_missing_coordinates: List[Dict[str, Any]]
    attribution: str = ATTRIBUTION
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_metro_dataset(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load the Stage 1 audited dataset. Optionally Streamlit-cached."""
    data_path = Path(path) if path else DEFAULT_DATASET
    return _load_json(data_path)


def load_metro_dataset_cached(path_str: str) -> Dict[str, Any]:
    """Load dataset; uses Streamlit cache_data only inside an active Streamlit script run."""
    # Avoid importing Streamlit during unit tests / CLI (prevents ScriptRunContext noise).
    import sys

    st_mod = sys.modules.get("streamlit")
    if st_mod is not None:
        try:
            from streamlit.runtime.scriptrunner import get_script_run_ctx

            if get_script_run_ctx() is not None:
                cached = getattr(st_mod, "cache_data", None)
                if cached is not None:

                    @cached(show_spinner=False)
                    def _cached(p: str) -> Dict[str, Any]:
                        return _load_json(Path(p))

                    return _cached(path_str)
        except Exception:
            pass
    return _load_json(Path(path_str))


def _station_coords_verified(station: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Coordinates must be present, numeric, and not flagged for manual verification."""
    lat, lon = station.get("lat"), station.get("lon")
    ok, err = validate_coordinates(lat, lon)
    if not ok:
        return False, err or "missing_coordinates"

    ver = station.get("verification") or {}
    if ver.get("needs_manual_verification"):
        return False, "manual_coordinate_verification"

    # Require positive verification signal from Stage 1 audit
    flags = set(ver.get("flags") or [])
    confidence = station.get("coordinate_confidence")
    match = ver.get("osm_name_match")
    audited = "coords_corridor_audited" in flags or ver.get("audit_coords_ok") is True
    high_ok = confidence == "high" and match == "matched"
    if not (audited or high_ok):
        return False, "coordinates_not_verified"

    return True, None


def operational_lines(station: Dict[str, Any]) -> List[LineInfo]:
    out: List[LineInfo] = []
    for ln in station.get("lines") or []:
        if ln.get("status") == OPERATIONAL and ln.get("line"):
            out.append(
                LineInfo(
                    line=str(ln["line"]),
                    status=OPERATIONAL,
                    notes=ln.get("notes"),
                )
            )
    return out


def classify_exclusion(station: Dict[str, Any]) -> Optional[str]:
    """Return exclusive exclusion reason, or None if eligible for nearest-station calc."""
    lat, lon = station.get("lat"), station.get("lon")
    ok, err = validate_coordinates(lat, lon)
    if not ok:
        if err in ("missing_coordinates", None):
            return "missing_coordinates"
        return "invalid_coordinates"

    ver = station.get("verification") or {}
    if ver.get("needs_manual_verification"):
        return "manual_coordinate_verification"

    flags = set(ver.get("flags") or [])
    confidence = station.get("coordinate_confidence")
    match = ver.get("osm_name_match")
    audited = "coords_corridor_audited" in flags or ver.get("audit_coords_ok") is True
    high_ok = confidence == "high" and match == "matched"
    if not (audited or high_ok):
        return "coordinates_not_verified"

    if not operational_lines(station):
        return "no_operational_line"

    return None


def station_summary(station: Dict[str, Any], *, include_all_lines: bool = True) -> Dict[str, Any]:
    lines = station.get("lines") or []
    return {
        "station_id": station.get("id"),
        "name": station.get("name"),
        "station_code": station.get("station_code"),
        "lat": station.get("lat"),
        "lon": station.get("lon"),
        "primary_status": station.get("primary_status"),
        "lines": list(lines) if include_all_lines else [ln.to_dict() for ln in operational_lines(station)],
        "coordinate_confidence": station.get("coordinate_confidence"),
        "verification": station.get("verification"),
        "sources": station.get("sources") or [],
    }


class MetroService:
    """Nearest-station and default inventory engine over the Stage 1 dataset."""

    def __init__(
        self,
        dataset: Optional[Dict[str, Any]] = None,
        dataset_path: Optional[Path] = None,
        geocoder: Optional[NominatimGeocoder] = None,
    ) -> None:
        if dataset is not None:
            self.dataset = dataset
        else:
            path = Path(dataset_path) if dataset_path else DEFAULT_DATASET
            self.dataset = load_metro_dataset_cached(str(path))

        self.stations: List[Dict[str, Any]] = list(self.dataset.get("stations") or [])
        self.geocoder = geocoder or NominatimGeocoder()

    def exclusion_report(self) -> Dict[str, Any]:
        by_reason: Dict[str, int] = {k: 0 for k in EXCLUSION_PRIORITY}
        excluded_ids: Dict[str, List[str]] = {k: [] for k in EXCLUSION_PRIORITY}
        eligible: List[str] = []
        for st in self.stations:
            reason = classify_exclusion(st)
            if reason is None:
                eligible.append(st["id"])
            else:
                by_reason[reason] = by_reason.get(reason, 0) + 1
                excluded_ids.setdefault(reason, []).append(st["id"])
        return {
            "eligible_station_count": len(eligible),
            "eligible_station_ids": eligible,
            "excluded_station_count": sum(by_reason.values()),
            "excluded_by_reason": {k: v for k, v in by_reason.items() if v},
            "excluded_ids_by_reason": {k: v for k, v in excluded_ids.items() if v},
        }

    def eligible_stations(self) -> List[Dict[str, Any]]:
        return [st for st in self.stations if classify_exclusion(st) is None]

    def verified_coordinate_stations(self) -> List[Dict[str, Any]]:
        """All stations with verified coordinates (any line status) for default mode."""
        out = []
        for st in self.stations:
            ok, _ = _station_coords_verified(st)
            if ok:
                out.append(station_summary(st))
        return out

    def line_explorer_partitions(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Unverified (incl. manual) and missing-coordinate stations for future Line Explorer."""
        unverified: List[Dict[str, Any]] = []
        missing: List[Dict[str, Any]] = []
        for st in self.stations:
            lat, lon = st.get("lat"), st.get("lon")
            ok_coords, err = validate_coordinates(lat, lon)
            if not ok_coords:
                missing.append(station_summary(st))
                continue
            ver = st.get("verification") or {}
            if ver.get("needs_manual_verification"):
                unverified.append(station_summary(st))
                continue
            # Present coords but not meeting verified bar
            ok_ver, reason = _station_coords_verified(st)
            if not ok_ver and reason != "missing_coordinates":
                unverified.append(station_summary(st))
        return unverified, missing

    def nearest_stations(
        self,
        lat: float,
        lon: float,
        limit: int = 5,
    ) -> List[NearestStationResult]:
        ok, err = validate_coordinates(lat, lon)
        if not ok:
            raise ValueError(f"invalid search coordinates: {err}")

        ranked: List[NearestStationResult] = []
        for st in self.eligible_stations():
            op_lines = operational_lines(st)
            if not op_lines:
                continue
            dist = haversine_km(lat, lon, float(st["lat"]), float(st["lon"]))
            ranked.append(
                NearestStationResult(
                    station_id=st["id"],
                    name=st["name"],
                    approximate_distance_km=dist,
                    lat=float(st["lat"]),
                    lon=float(st["lon"]),
                    operational_lines=op_lines,
                    primary_status=st.get("primary_status") or OPERATIONAL,
                    sources=list(st.get("sources") or []),
                    station_code=st.get("station_code"),
                )
            )

        ranked.sort(key=lambda r: (r.approximate_distance_km, r.name))
        # Deduplicate by station id (interchanges already one record with multi-line info)
        seen = set()
        unique: List[NearestStationResult] = []
        for item in ranked:
            if item.station_id in seen:
                continue
            seen.add(item.station_id)
            unique.append(item)
            if len(unique) >= limit:
                break
        return unique

    def default_inventory(self) -> SearchResponse:
        report = self.exclusion_report()
        unverified, missing = self.line_explorer_partitions()
        verified = self.verified_coordinate_stations()
        return SearchResponse(
            mode="default",
            query=None,
            geocode=None,
            nearest_stations=[],
            eligible_station_count=report["eligible_station_count"],
            excluded_station_count=report["excluded_station_count"],
            excluded_by_reason=report["excluded_by_reason"],
            verified_coordinate_stations=verified,
            line_explorer_unverified=unverified,
            line_explorer_missing_coordinates=missing,
            attribution=self.geocoder.attribution,
        )

    def search_location(
        self,
        query: str,
        nearest_limit: int = 5,
    ) -> SearchResponse:
        """Geocode an explicit query and return the nearest eligible stations."""
        report = self.exclusion_report()
        unverified, missing = self.line_explorer_partitions()
        verified = self.verified_coordinate_stations()

        geo = self.geocoder.search(query)
        if not geo.ok:
            return SearchResponse(
                mode="nearest",
                query=query,
                geocode=geo.to_dict(),
                nearest_stations=[],
                eligible_station_count=report["eligible_station_count"],
                excluded_station_count=report["excluded_station_count"],
                excluded_by_reason=report["excluded_by_reason"],
                verified_coordinate_stations=verified,
                line_explorer_unverified=unverified,
                line_explorer_missing_coordinates=missing,
                attribution=self.geocoder.attribution,
                error=geo.error,
            )

        assert geo.lat is not None and geo.lon is not None
        nearest = self.nearest_stations(geo.lat, geo.lon, limit=nearest_limit)
        return SearchResponse(
            mode="nearest",
            query=query,
            geocode=geo.to_dict(),
            nearest_stations=[n.to_dict() for n in nearest],
            eligible_station_count=report["eligible_station_count"],
            excluded_station_count=report["excluded_station_count"],
            excluded_by_reason=report["excluded_by_reason"],
            verified_coordinate_stations=verified,
            line_explorer_unverified=unverified,
            line_explorer_missing_coordinates=missing,
            attribution=self.geocoder.attribution,
        )


def build_default_service(
    dataset_path: Optional[Path] = None,
    geocoder: Optional[NominatimGeocoder] = None,
) -> MetroService:
    return MetroService(dataset_path=dataset_path, geocoder=geocoder)
