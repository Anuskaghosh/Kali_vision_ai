"""Unit tests for OSRM routing client (mocked HTTP)."""

from __future__ import annotations

import json
import unittest
from typing import Any

from modules.metro.routing_service import (
    TRAVEL_MODES,
    OsrmRouter,
    _format_instruction,
)


class FakeResp:
    def __init__(self, payload: Any) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "FakeResp":
        return self

    def __exit__(self, *args: Any) -> None:
        return None


class FakeOpener:
    def __init__(self, payload: Any) -> None:
        self.payload = payload
        self.last_url = None

    def open(self, req: Any, timeout: float | None = None) -> FakeResp:
        self.last_url = req.full_url
        return FakeResp(self.payload)


SAMPLE_OK = {
    "code": "Ok",
    "routes": [
        {
            "distance": 2500.0,
            "duration": 1200.0,
            "geometry": {
                "type": "LineString",
                "coordinates": [[88.35, 22.55], [88.36, 22.56]],
            },
            "legs": [
                {
                    "steps": [
                        {
                            "distance": 500,
                            "duration": 240,
                            "name": "AJC Bose Road",
                            "maneuver": {"type": "depart", "modifier": ""},
                        },
                        {
                            "distance": 2000,
                            "duration": 960,
                            "name": "Park Street",
                            "maneuver": {"type": "turn", "modifier": "right"},
                        },
                    ]
                }
            ],
        }
    ],
}


class RoutingTests(unittest.TestCase):
    def test_supported_modes(self) -> None:
        self.assertEqual(set(TRAVEL_MODES), {"Walking", "Cycling", "Driving"})
        self.assertEqual(TRAVEL_MODES["Walking"], "foot")

    def test_format_instruction(self) -> None:
        text = _format_instruction(
            {"maneuver": {"type": "turn", "modifier": "left"}, "name": "Park Street"}
        )
        self.assertIn("Park Street", text)
        self.assertIn("Turn", text)

    def test_route_ok(self) -> None:
        opener = FakeOpener(SAMPLE_OK)
        router = OsrmRouter(opener=opener, min_interval_sec=1.0)
        result = router.route((22.55, 88.35), (22.56, 88.36), mode_label="Walking")
        self.assertTrue(result.ok)
        self.assertEqual(result.distance_km, 2.5)
        self.assertEqual(result.duration_min, 20.0)
        self.assertEqual(result.profile, "foot")
        self.assertEqual(len(result.steps), 2)
        self.assertIn("/foot/", opener.last_url or "")

    def test_route_no_route(self) -> None:
        opener = FakeOpener({"code": "NoRoute", "routes": []})
        router = OsrmRouter(opener=opener, min_interval_sec=1.0)
        result = router.route((22.55, 88.35), (22.56, 88.36), mode_label="Driving")
        self.assertFalse(result.ok)
        self.assertIn("osrm_", result.error or "")
        self.assertEqual(result.profile, "driving")


if __name__ == "__main__":
    unittest.main()
