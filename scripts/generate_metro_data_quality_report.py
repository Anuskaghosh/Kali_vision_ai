#!/usr/bin/env python3
"""Generate data/kolkata_metro_data_quality_report.json from the Stage 1 dataset."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "kolkata_metro_stations.json"
OUT = ROOT / "data" / "kolkata_metro_data_quality_report.json"

SPECIAL_ATTENTION = {
    "km-kavi-nazrul",
    "km-gitanjali",
    "km-barun-sengupta",
    "km-barasat",
    "km-it-centre",
    "km-city-centre-2",
    "km-chinar-park",
    "km-vip-road",
    "km-krishnapur",
    "km-kestopur",
    "km-baguiati",
    "km-raghunathpur",
    "km-teghoria",
}


def classify(st: dict) -> str:
    ver = st.get("verification") or {}
    flags = set(ver.get("flags") or [])
    lat, lon = st.get("lat"), st.get("lon")
    if ver.get("needs_manual_verification"):
        if lat is None:
            return "missing_coordinates"
        if "osm_hit_rejected_railway_not_metro" in flags or "osm_hit_may_be_railway_not_metro" in flags:
            return "suspect_coordinates"
        if "wikipedia_list_coordinates_rejected" in flags and "coords_corridor_audited" not in flags:
            return "suspect_coordinates"
        return "unverified"
    if "coords_corridor_audited" in flags or (
        lat is not None and ver.get("osm_name_match") == "matched" and st.get("coordinate_confidence") == "high"
    ):
        return "verified"
    if lat is None:
        return "missing_coordinates"
    return "unverified"


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    stations = data["stations"]

    buckets = defaultdict(list)
    for st in stations:
        buckets[classify(st)].append(st["id"])

    interchanges = [
        {
            "id": st["id"],
            "name": st["name"],
            "primary_status": st["primary_status"],
            "lines": st["lines"],
        }
        for st in stations
        if len(st.get("lines") or []) > 1
    ]

    # Conflicting line / status heuristics: same id must be unique (already validated);
    # flag multi-line stations where primary_status disagrees with overall mix.
    conflicting_status = []
    for st in stations:
        statuses = {ln["status"] for ln in st["lines"]}
        ps = st["primary_status"]
        if len(statuses) == 1 and ps == next(iter(statuses)):
            continue
        if len(statuses) > 1 and ps != "partially_operational":
            conflicting_status.append({
                "id": st["id"],
                "name": st["name"],
                "primary_status": ps,
                "line_statuses": sorted(statuses),
                "issue": "multi-status lines should use primary_status=partially_operational",
            })
        if len(statuses) == 1 and ps == "partially_operational":
            conflicting_status.append({
                "id": st["id"],
                "name": st["name"],
                "primary_status": ps,
                "line_statuses": sorted(statuses),
                "issue": "partially_operational used with a single line status",
            })

    conflicting_lines = []
    # Detect duplicate line keys on one station
    for st in stations:
        lines = [ln["line"] for ln in st["lines"]]
        dup = [ln for ln, n in Counter(lines).items() if n > 1]
        if dup:
            conflicting_lines.append({
                "id": st["id"],
                "name": st["name"],
                "duplicate_lines": dup,
            })

    manual = [st for st in stations if st["verification"]["needs_manual_verification"]]
    special = []
    for st in stations:
        if st["id"] not in SPECIAL_ATTENTION:
            continue
        special.append({
            "id": st["id"],
            "name": st["name"],
            "primary_status": st["primary_status"],
            "lines": st["lines"],
            "lat": st.get("lat"),
            "lon": st.get("lon"),
            "coordinate_confidence": st.get("coordinate_confidence"),
            "osm": st.get("osm"),
            "verification": st.get("verification"),
            "notes": st.get("notes"),
            "quality_bucket": classify(st),
        })

    corrections = [
        {
            "id": "km-kavi-nazrul",
            "action": "accepted_osm_rejected_wikipedia_wgs",
            "detail": "Wikipedia ≈22.778,88.634 (~44 km off) rejected; OSM Kolkata Metro node retained after Blue corridor neighbor check.",
        },
        {
            "id": "km-gitanjali",
            "action": "accepted_osm_rejected_wikipedia_wgs",
            "detail": "Wikipedia ≈22.783,88.617 (~43 km off) rejected; OSM Kolkata Metro way retained after Blue corridor neighbor check.",
        },
        {
            "id": "km-barun-sengupta",
            "action": "accepted_osm_rejected_wikipedia_wgs",
            "detail": "Wikipedia lon ≈88.339 (~6 km west) rejected; OSM Kolkata Metro node retained between Ritwik Ghatak and Beleghata.",
        },
        {
            "id": "km-barasat",
            "action": "nulled_osm_railway_collision",
            "detail": "OSM Barasat subway-tagged way rejected (empty network; railway precinct). Coordinates set null; Yellow proposed status retained.",
        },
        {
            "id": "km-city-centre-2",
            "action": "blocked_green_city_centre_reuse",
            "detail": "No distinct Orange City Centre-2 OSM node; Green City Centre match forbidden; coords remain null.",
        },
        {
            "id": "km-it-centre",
            "action": "status_confirmed_uc_coords_null",
            "detail": "Orange UC near Green Sector-V; trials reported but not operational; coords null (no exact OSM metro node).",
        },
        {
            "id": "km-new-barrackpur",
            "action": "flagged_possible_rename",
            "detail": "Aliases Bidhanpally / Netaji Nagar added for Yellow realignment uncertainty; coords null.",
        },
        {
            "ids": [
                "km-gour-kishore-ghosh", "km-nalban", "km-it-centre", "km-nabadiganta",
                "km-nazrul-tirtha", "km-swapnabhor", "km-biswa-bangla-convention-centre",
                "km-shiksha-tirtha", "km-mother-s-wax-museum", "km-eco-park", "km-mangaldeep",
                "km-city-centre-2", "km-chinar-park", "km-vip-road",
            ],
            "action": "added_orange_station_codes_from_corridor_tables",
            "detail": "Station codes filled from Orange Line corridor tables where published (e.g. KITC, KCCT, KCNP, KVIR).",
        },
    ]

    report = {
        "title": "Kolkata Metro Stage 1 — data quality audit report",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dataset_file": str(DATA.relative_to(ROOT)),
        "dataset_version": data.get("meta", {}).get("version"),
        "full_verification_claimed": False,
        "summary": {
            "unique_stations": len(stations),
            "with_coordinates": sum(1 for s in stations if s.get("lat") is not None),
            "needs_manual_verification": len(manual),
            "quality_buckets": {k: len(v) for k, v in sorted(buckets.items())},
            "interchanges": len(interchanges),
            "conflicting_line_assignments": len(conflicting_lines),
            "conflicting_operational_statuses": len(conflicting_status),
        },
        "corrections_applied": corrections,
        "verified_records": buckets.get("verified", []),
        "unverified_records": buckets.get("unverified", []),
        "suspect_coordinates": buckets.get("suspect_coordinates", []),
        "missing_coordinates": buckets.get("missing_coordinates", []),
        "conflicting_line_assignments": conflicting_lines,
        "conflicting_operational_statuses": conflicting_status,
        "interchanges": interchanges,
        "special_attention_audit": special,
        "still_requires_manual_verification": [
            {
                "id": st["id"],
                "name": st["name"],
                "primary_status": st["primary_status"],
                "lines": [ln["line"] for ln in st["lines"]],
                "lat": st.get("lat"),
                "lon": st.get("lon"),
                "flags": st["verification"]["flags"],
                "quality_bucket": classify(st),
            }
            for st in manual
        ],
    }

    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Wrote", OUT)
    print("Buckets:", report["summary"]["quality_buckets"])
    print("Manual remaining:", report["summary"]["needs_manual_verification"])
    print("Full verification claimed:", report["full_verification_claimed"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
