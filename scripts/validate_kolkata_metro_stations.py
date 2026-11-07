#!/usr/bin/env python3
"""Validate data/kolkata_metro_stations.json (Stage 1) and print quality buckets."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "kolkata_metro_stations.json"
REPORT = ROOT / "data" / "kolkata_metro_data_quality_report.json"

ALLOWED_LINES = {"Blue", "Green", "Purple", "Orange", "Yellow"}
ALLOWED_STATUS = {"operational", "under_construction", "proposed", "partially_operational"}
ALLOWED_LINE_STATUS = {"operational", "under_construction", "proposed"}


def classify(st: dict) -> str:
    ver = st.get("verification") or {}
    flags = set(ver.get("flags") or [])
    lat = st.get("lat")
    if ver.get("needs_manual_verification"):
        if lat is None:
            return "missing_coordinates"
        if "osm_hit_rejected_railway_not_metro" in flags or "osm_hit_may_be_railway_not_metro" in flags:
            return "suspect_coordinates"
        return "unverified"
    if lat is not None and (
        "coords_corridor_audited" in flags
        or (ver.get("osm_name_match") == "matched" and st.get("coordinate_confidence") == "high")
    ):
        return "verified"
    if lat is None:
        return "missing_coordinates"
    return "unverified"


def main() -> int:
    if not DATA.exists():
        print(f"FAIL: missing {DATA}")
        return 1

    data = json.loads(DATA.read_text(encoding="utf-8"))
    stations = data.get("stations")
    if not isinstance(stations, list) or not stations:
        print("FAIL: stations must be a non-empty list")
        return 1

    errors = []
    warnings = []
    ids = []
    name_keys = []
    code_keys = []

    for i, st in enumerate(stations):
        prefix = f"stations[{i}]"
        sid = st.get("id")
        if not isinstance(sid, str) or not sid.startswith("km-"):
            errors.append(f"{prefix}: invalid id {sid!r}")
        else:
            ids.append(sid)

        name = st.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{prefix}: missing name")
        else:
            name_keys.append(name.strip().lower())

        code = st.get("station_code")
        if code is not None:
            if not isinstance(code, str) or not code.strip():
                errors.append(f"{prefix}: empty station_code should be null")
            else:
                code_keys.append(code.strip().upper())

        lines = st.get("lines")
        if not isinstance(lines, list) or not lines:
            errors.append(f"{prefix}: lines must be non-empty list")
        else:
            seen_lines = []
            for j, ln in enumerate(lines):
                if ln.get("line") not in ALLOWED_LINES:
                    errors.append(f"{prefix}.lines[{j}]: invalid line {ln.get('line')!r}")
                if ln.get("status") not in ALLOWED_LINE_STATUS:
                    errors.append(f"{prefix}.lines[{j}]: invalid status {ln.get('status')!r}")
                seen_lines.append(ln.get("line"))
            for ln, n in Counter(seen_lines).items():
                if n > 1:
                    errors.append(f"{prefix}: duplicate line assignment {ln!r}")

            statuses = {ln["status"] for ln in lines}
            ps = st.get("primary_status")
            if len(statuses) > 1 and ps != "partially_operational":
                errors.append(
                    f"{prefix} ({name}): multi-status lines require primary_status=partially_operational "
                    f"(got {ps!r}, statuses={sorted(statuses)})"
                )

        ps = st.get("primary_status")
        if ps not in ALLOWED_STATUS:
            errors.append(f"{prefix}: invalid primary_status {ps!r}")

        lat, lon = st.get("lat"), st.get("lon")
        if lat is None and lon is None:
            if not st.get("verification", {}).get("needs_manual_verification"):
                warnings.append(f"{prefix} ({name}): missing coords but not flagged for manual verification")
        else:
            if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
                errors.append(f"{prefix}: lat/lon must be numbers or both null")
            else:
                if not (22.2 <= float(lat) <= 23.0 and 88.0 <= float(lon) <= 88.7):
                    errors.append(f"{prefix} ({name}): coordinates outside Greater Kolkata bbox: {lat},{lon}")

        sources = st.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{prefix}: sources required")

        ver = st.get("verification") or {}
        if "needs_manual_verification" not in ver:
            errors.append(f"{prefix}: verification.needs_manual_verification required")
        if "flags" not in ver or not isinstance(ver["flags"], list):
            errors.append(f"{prefix}: verification.flags must be a list")

        # Reject known bad pattern: Barasat must not carry OSM railway coords
        if sid == "km-barasat" and lat is not None:
            errors.append(f"{prefix}: Barasat must not keep unverified OSM railway coordinates")

    id_counts = Counter(ids)
    for sid, n in id_counts.items():
        if n > 1:
            errors.append(f"duplicate id: {sid} ({n})")

    name_counts = Counter(name_keys)
    for nm, n in name_counts.items():
        if n > 1:
            errors.append(f"duplicate name: {nm} ({n})")

    code_counts = Counter(code_keys)
    for cd, n in code_counts.items():
        if n > 1:
            errors.append(f"duplicate station_code: {cd} ({n})")

    line_assign = defaultdict(Counter)
    primary = Counter()
    quality = Counter()
    manual = 0
    with_coords = 0
    for st in stations:
        primary[st["primary_status"]] += 1
        quality[classify(st)] += 1
        if st.get("lat") is not None:
            with_coords += 1
        if st.get("verification", {}).get("needs_manual_verification"):
            manual += 1
        for ln in st["lines"]:
            line_assign[ln["line"]][ln["status"]] += 1

    print("=== Kolkata Metro Stage 1 validation ===")
    print(f"File: {DATA}")
    print(f"Unique stations: {len(stations)}")
    print(f"With coordinates: {with_coords}")
    print(f"Needs manual verification: {manual}")
    print(f"Primary status: {dict(primary)}")
    print(f"Quality buckets: {dict(quality)}")
    print("Per-line assignments:")
    for line in sorted(ALLOWED_LINES):
        print(f"  {line}: {dict(line_assign[line])}")
    print(f"Full verification claimed: False (manual remaining={manual})")

    if REPORT.exists():
        print(f"Quality report present: {REPORT}")

    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            print("  WARN", w)

    if errors:
        print(f"\nFAIL ({len(errors)} errors):")
        for e in errors:
            print("  ERROR", e)
        return 1

    print("\nPASS: schema, IDs, names, codes, lines, coords bbox, duplicates, interchange status rules")
    return 0


if __name__ == "__main__":
    sys.exit(main())
