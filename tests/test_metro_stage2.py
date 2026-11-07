"""Unit tests for Kolkata Metro Stage 2 (geocoding + nearest-station engine).

Geocoding uses mocked Nominatim payloads — no live network required.
"""

from __future__ import annotations

import io
import json
import math
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from modules.metro.distance_calculator import haversine_km, validate_coordinates
from modules.metro.geocoding_service import (
    GeocodeError,
    NominatimGeocoder,
    is_west_bengal,
)
from modules.metro.metro_service import (
    MetroService,
    classify_exclusion,
    operational_lines,
)

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "kolkata_metro_stations.json"


def _minimal_dataset(stations):
    return {
        "meta": {"version": "test"},
        "stations": stations,
    }


def _station(
    sid,
    name,
    lat,
    lon,
    lines,
    *,
    manual=False,
    confidence="high",
    match="matched",
    flags=None,
    sources=None,
):
    return {
        "id": sid,
        "name": name,
        "station_code": None,
        "lat": lat,
        "lon": lon,
        "lines": lines,
        "primary_status": "operational"
        if all(ln["status"] == "operational" for ln in lines)
        else "partially_operational"
        if any(ln["status"] == "operational" for ln in lines)
        else lines[0]["status"],
        "coordinate_confidence": confidence,
        "coordinate_source": "openstreetmap" if lat is not None else None,
        "sources": sources or [{"id": "test", "title": "test", "url": "https://example.test"}],
        "verification": {
            "osm_name_match": match,
            "needs_manual_verification": manual,
            "flags": flags or ([] if not manual else ["needs_manual_verification"]),
            "audit_coords_ok": False,
        },
    }


class TestHaversine(unittest.TestCase):
    def test_zero_distance(self):
        self.assertAlmostEqual(haversine_km(22.5, 88.3, 22.5, 88.3), 0.0, places=6)

    def test_known_short_distance(self):
        # ~1.11 km per 0.01 deg lat near equator; Kolkata ~1.11 km as well
        d = haversine_km(22.50, 88.35, 22.51, 88.35)
        self.assertGreater(d, 1.0)
        self.assertLess(d, 1.3)

    def test_symmetry(self):
        a = haversine_km(22.55, 88.35, 22.57, 88.37)
        b = haversine_km(22.57, 88.37, 22.55, 88.35)
        self.assertAlmostEqual(a, b, places=9)

    def test_invalid_coordinates_raise(self):
        with self.assertRaises(ValueError):
            haversine_km(None, 88.3, 22.5, 88.3)
        with self.assertRaises(ValueError):
            haversine_km(22.5, 88.3, 999.0, 88.3)
        with self.assertRaises(ValueError):
            haversine_km(22.5, 88.3, float("nan"), 88.3)


class TestValidateCoordinates(unittest.TestCase):
    def test_valid(self):
        ok, err = validate_coordinates(22.5, 88.3)
        self.assertTrue(ok)
        self.assertIsNone(err)

    def test_missing(self):
        ok, err = validate_coordinates(None, None)
        self.assertFalse(ok)
        self.assertEqual(err, "missing_coordinates")

    def test_non_numeric(self):
        ok, err = validate_coordinates("x", 88.3)
        self.assertFalse(ok)
        self.assertEqual(err, "non_numeric_coordinates")

    def test_out_of_range(self):
        ok, err = validate_coordinates(91.0, 88.3)
        self.assertFalse(ok)
        self.assertEqual(err, "coordinates_out_of_range")


class TestWestBengalFilter(unittest.TestCase):
    def test_west_bengal_state(self):
        hit = {
            "display_name": "Victoria Memorial, Kolkata, West Bengal, India",
            "address": {"state": "West Bengal", "city": "Kolkata", "country_code": "in"},
        }
        self.assertTrue(is_west_bengal(hit))

    def test_outside_state(self):
        hit = {
            "display_name": "Gateway of India, Mumbai, Maharashtra, India",
            "address": {"state": "Maharashtra", "city": "Mumbai", "country_code": "in"},
        }
        self.assertFalse(is_west_bengal(hit))


class TestGeocoding(unittest.TestCase):
    def _geocoder_with_payload(self, payload):
        body = json.dumps(payload).encode("utf-8")
        resp = MagicMock()
        resp.read.return_value = body
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = False
        opener = MagicMock()
        opener.open.return_value = resp
        return NominatimGeocoder(opener=opener, min_interval_sec=1.0)

    def test_empty_query(self):
        g = NominatimGeocoder(opener=MagicMock())
        r = g.search("  ")
        self.assertFalse(r.ok)
        self.assertEqual(r.error, "empty_query")

    def test_empty_results(self):
        g = self._geocoder_with_payload([])
        with patch.object(g, "_throttle"):
            r = g.search("nowhere-xyz")
        self.assertFalse(r.ok)
        self.assertEqual(r.error, "no_results")

    def test_outside_west_bengal(self):
        g = self._geocoder_with_payload(
            [
                {
                    "lat": "19.0760",
                    "lon": "72.8777",
                    "display_name": "Mumbai, Maharashtra, India",
                    "place_id": 1,
                    "address": {"state": "Maharashtra", "country_code": "in"},
                }
            ]
        )
        with patch.object(g, "_throttle"):
            r = g.search("Gateway of India")
        self.assertFalse(r.ok)
        self.assertEqual(r.error, "outside_west_bengal")
        self.assertFalse(r.in_west_bengal)

    def test_successful_west_bengal(self):
        g = self._geocoder_with_payload(
            [
                {
                    "lat": "22.5448",
                    "lon": "88.3426",
                    "display_name": "Victoria Memorial, Kolkata, West Bengal, India",
                    "place_id": 42,
                    "address": {"state": "West Bengal", "city": "Kolkata", "country_code": "in"},
                }
            ]
        )
        with patch.object(g, "_throttle"):
            r = g.search("Victoria Memorial")
        self.assertTrue(r.ok)
        self.assertTrue(r.in_west_bengal)
        self.assertAlmostEqual(r.lat, 22.5448, places=4)
        self.assertAlmostEqual(r.lon, 88.3426, places=4)

    def test_cache_avoids_second_http(self):
        g = self._geocoder_with_payload(
            [
                {
                    "lat": "22.5448",
                    "lon": "88.3426",
                    "display_name": "Victoria Memorial, Kolkata, West Bengal, India",
                    "place_id": 42,
                    "address": {"state": "West Bengal", "country_code": "in"},
                }
            ]
        )
        with patch.object(g, "_throttle"):
            r1 = g.search("Victoria Memorial")
            r2 = g.search("victoria   memorial")
        self.assertTrue(r1.ok)
        self.assertTrue(r2.ok)
        self.assertTrue(r2.cached)
        self.assertEqual(g._opener.open.call_count, 1)

    def test_connection_failure_cached(self):
        opener = MagicMock()
        opener.open.side_effect = GeocodeError("boom")
        # Make opener raise URLError path via _http_get_json
        import urllib.error

        opener.open.side_effect = urllib.error.URLError("down")
        g = NominatimGeocoder(opener=opener, min_interval_sec=1.0)
        with patch.object(g, "_throttle"):
            r1 = g.search("Somewhere")
            r2 = g.search("Somewhere")
        self.assertFalse(r1.ok)
        self.assertIn("nominatim_connection_failed", r1.error or "")
        self.assertTrue(r2.cached)
        self.assertEqual(opener.open.call_count, 1)


class TestEligibilityAndNearest(unittest.TestCase):
    def setUp(self):
        self.stations = [
            _station(
                "km-a",
                "Alpha",
                22.55,
                88.35,
                [{"line": "Blue", "status": "operational"}],
            ),
            _station(
                "km-b",
                "Beta Interchange",
                22.56,
                88.36,
                [
                    {"line": "Blue", "status": "operational"},
                    {"line": "Purple", "status": "under_construction"},
                ],
            ),
            _station(
                "km-c",
                "Charlie UC",
                22.57,
                88.37,
                [{"line": "Orange", "status": "under_construction"}],
            ),
            _station(
                "km-d",
                "Delta Proposed",
                22.58,
                88.38,
                [{"line": "Green", "status": "proposed"}],
            ),
            _station(
                "km-e",
                "Echo Missing",
                None,
                None,
                [{"line": "Blue", "status": "operational"}],
                confidence="missing",
                match="unmatched",
            ),
            _station(
                "km-f",
                "Foxtrot Manual",
                22.54,
                88.34,
                [{"line": "Blue", "status": "operational"}],
                manual=True,
                flags=["needs_manual_verification", "osm_unmatched"],
            ),
        ]
        self.svc = MetroService(dataset=_minimal_dataset(self.stations), geocoder=NominatimGeocoder())

    def test_exclude_under_construction_only(self):
        self.assertEqual(classify_exclusion(self.stations[2]), "no_operational_line")

    def test_exclude_proposed(self):
        self.assertEqual(classify_exclusion(self.stations[3]), "no_operational_line")

    def test_exclude_missing_coordinates(self):
        self.assertEqual(classify_exclusion(self.stations[4]), "missing_coordinates")

    def test_exclude_manual_verification(self):
        self.assertEqual(classify_exclusion(self.stations[5]), "manual_coordinate_verification")

    def test_interchange_keeps_only_operational_lines(self):
        lines = operational_lines(self.stations[1])
        self.assertEqual([ln.line for ln in lines], ["Blue"])

    def test_nearest_sort_and_limit(self):
        # Origin near Foxtrot (manual, excluded) and Alpha
        results = self.svc.nearest_stations(22.550, 88.350, limit=5)
        ids = [r.station_id for r in results]
        self.assertEqual(ids[0], "km-a")
        self.assertIn("km-b", ids)
        self.assertNotIn("km-c", ids)
        self.assertNotIn("km-d", ids)
        self.assertNotIn("km-e", ids)
        self.assertNotIn("km-f", ids)
        # distances ascending
        dists = [r.approximate_distance_km for r in results]
        self.assertEqual(dists, sorted(dists))

    def test_duplicate_station_not_repeated(self):
        # Eligible set already unique by id; nearest list must not duplicate names/ids
        results = self.svc.nearest_stations(22.55, 88.35, limit=5)
        ids = [r.station_id for r in results]
        self.assertEqual(len(ids), len(set(ids)))
        beta = next(r for r in results if r.station_id == "km-b")
        self.assertEqual(len(beta.operational_lines), 1)
        self.assertEqual(beta.operational_lines[0].line, "Blue")

    def test_exclusion_report_counts(self):
        report = self.svc.exclusion_report()
        self.assertEqual(report["eligible_station_count"], 2)  # Alpha + Beta
        self.assertEqual(report["excluded_by_reason"]["no_operational_line"], 2)
        self.assertEqual(report["excluded_by_reason"]["missing_coordinates"], 1)
        self.assertEqual(report["excluded_by_reason"]["manual_coordinate_verification"], 1)

    def test_default_mode_partitions(self):
        resp = self.svc.default_inventory()
        self.assertEqual(resp.mode, "default")
        verified_ids = {s["station_id"] for s in resp.verified_coordinate_stations}
        self.assertIn("km-a", verified_ids)
        self.assertIn("km-b", verified_ids)
        # UC with coords still verified coords for explorer inventory
        self.assertIn("km-c", verified_ids)
        missing_ids = {s["station_id"] for s in resp.line_explorer_missing_coordinates}
        self.assertIn("km-e", missing_ids)
        unverified_ids = {s["station_id"] for s in resp.line_explorer_unverified}
        self.assertIn("km-f", unverified_ids)

    def test_search_with_mocked_geocode(self):
        payload = [
            {
                "lat": "22.550",
                "lon": "88.350",
                "display_name": "Test Place, Kolkata, West Bengal, India",
                "place_id": 9,
                "address": {"state": "West Bengal", "country_code": "in"},
            }
        ]
        body = json.dumps(payload).encode("utf-8")
        resp = MagicMock()
        resp.read.return_value = body
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = False
        opener = MagicMock()
        opener.open.return_value = resp
        geocoder = NominatimGeocoder(opener=opener, min_interval_sec=1.0)
        svc = MetroService(dataset=_minimal_dataset(self.stations), geocoder=geocoder)
        with patch.object(geocoder, "_throttle"):
            out = svc.search_location("Test Place", nearest_limit=3)
        self.assertEqual(out.mode, "nearest")
        self.assertIsNone(out.error)
        self.assertGreaterEqual(len(out.nearest_stations), 1)
        first = out.nearest_stations[0]
        self.assertIn("approximate_distance_km", first)
        self.assertIn("metro_lines", first)
        self.assertIn("sources", first)
        note = (first.get("distance_note") or "").lower()
        self.assertIn("not walking distance", note)
        self.assertIn("straight-line", note)


class TestRealDatasetEligibility(unittest.TestCase):
    """Smoke checks against the audited Stage 1 JSON (no network)."""

    @classmethod
    def setUpClass(cls):
        if not DATASET.exists():
            raise unittest.SkipTest("dataset missing")
        cls.svc = MetroService(dataset_path=DATASET, geocoder=NominatimGeocoder())

    def test_eligible_count_positive(self):
        report = self.svc.exclusion_report()
        self.assertGreater(report["eligible_station_count"], 40)
        self.assertEqual(
            report["eligible_station_count"] + report["excluded_station_count"],
            len(self.svc.stations),
        )

    def test_interchange_esplanade_operational_lines(self):
        esp = next(s for s in self.svc.stations if s["id"] == "km-esplanade")
        lines = [ln.line for ln in operational_lines(esp)]
        self.assertEqual(sorted(lines), ["Blue", "Green"])
        self.assertIsNone(classify_exclusion(esp))

    def test_uc_with_coords_excluded_from_nearest(self):
        nalban = next(s for s in self.svc.stations if s["id"] == "km-nalban")
        self.assertEqual(classify_exclusion(nalban), "no_operational_line")


if __name__ == "__main__":
    unittest.main()
