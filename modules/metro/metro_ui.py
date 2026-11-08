"""KALI VISION AI — Kolkata Metro page UI.

Full-viewport map + compact journey dock, station explorer, GPS origin,
marker/explorer/result destination selection, OSRM route overlay.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import quote

import folium
import streamlit as st
import streamlit.components.v1 as components

from .metro_service import MetroService, SearchResponse
from .routing_service import ATTRIBUTION as ROUTE_ATTRIBUTION
from .routing_service import TRAVEL_MODES, OsrmRouter

LINE_COLORS = {
    "Blue": "#2F6FED",
    "Green": "#1FA971",
    "Purple": "#9B4DCA",
    "Orange": "#E67E22",
    "Yellow": "#D4A017",
}
LINE_ORDER = ["Blue", "Green", "Purple", "Orange", "Yellow"]
ALL_LINES = "All"

STATUS_LABELS = {
    "operational": "Operational",
    "partially_operational": "Partially operational",
    "under_construction": "Under construction",
    "proposed": "Proposed",
}
STATUS_KEYS = list(STATUS_LABELS.keys())
COORDS_AWAITING = "coords_awaiting"

KOLKATA_CENTER = (22.555, 88.35)
DEFAULT_ZOOM = 12

ERROR_MESSAGES = {
    "empty_query": "Enter a place to search.",
    "no_results": "No matching place was found. Try a fuller name (e.g. add “Kolkata”).",
    "outside_west_bengal": "That location is outside West Bengal. Try a place in or near Kolkata.",
    "nominatim_timeout": "The location service timed out. Please try again in a moment.",
    "nominatim_connection_failed": "Could not reach the location service. Check your connection and retry.",
    "invalid_geocode_coordinates": "The location service returned unusable coordinates.",
    "geo_denied": (
        "Location permission was denied. Enable location for this site in your browser "
        "settings, then tap the location pin again."
    ),
    "geo_unavailable": "Location is unavailable on this device. Try again.",
    "geo_timeout": "Location timed out. Tap the location pin to try again.",
    "geo_insecure": "Browser geolocation needs HTTPS (or localhost).",
    "geo_failed": "Could not detect your location. Tap the location pin to try again.",
    "need_origin": "Tap the location pin first so we can draw your walk to the station.",
    "need_destination": "Type to find a station, then tap one in the list — or pick it on the map.",
    "osrm_no_route": "No route found between those points for this travel mode.",
    "osrm_timeout": "The routing service timed out. Please try again.",
}


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _normalize_line_filter(value: Optional[str]) -> str:
    if not value or value in ("All Lines", "All"):
        return ALL_LINES
    return value


def _sid(station: Dict[str, Any]) -> Optional[str]:
    return station.get("station_id") or station.get("id")


TO_PLACEHOLDER = "Choose a metro station…"


def _destination_option_label(station: Dict[str, Any]) -> str:
    name = station.get("name") or "Station"
    code = station.get("station_code") or "—"
    return f"{name} · {code}"


def _selectable_stations(stations: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for stn in stations:
        if stn.get("lat") is None or stn.get("lon") is None:
            continue
        if not _sid(stn):
            continue
        out.append(stn)
    out.sort(key=lambda s: str(s.get("name") or "").lower())
    return out


def _station_search_blob(station: Dict[str, Any]) -> str:
    parts = [
        str(station.get("name") or ""),
        str(station.get("station_code") or ""),
        str(station.get("name_bn") or ""),
    ]
    for alias in station.get("aliases") or []:
        parts.append(str(alias))
    for ln in _station_lines(station):
        parts.append(str(ln.get("line") or ""))
    lines = station.get("metro_lines") or []
    for ln in lines:
        parts.append(str(ln))
    return " ".join(parts).lower()


def _station_matches_query(station: Dict[str, Any], query: str) -> bool:
    """True when every whitespace token appears somewhere in the station blob."""
    q = (query or "").strip().lower()
    if not q:
        return True
    blob = _station_search_blob(station)
    tokens = [t for t in q.split() if t]
    return all(t in blob for t in tokens)


def _sync_to_selectbox(destination: Optional[Dict[str, Any]]) -> None:
    """Keep the TO selectbox label aligned with session destination (map/GPS/etc.)."""
    if destination and destination.get("name"):
        st.session_state.metro_to_station = _destination_option_label(destination)
    else:
        st.session_state.metro_to_station = TO_PLACEHOLDER


@st.cache_resource(show_spinner=False)
def get_metro_service() -> MetroService:
    return MetroService()


@st.cache_resource(show_spinner=False)
def get_router() -> OsrmRouter:
    return OsrmRouter()


def _init_state() -> None:
    defaults: Dict[str, Any] = {
        "metro_line_filter": ALL_LINES,
        "metro_search_response": None,
        "metro_search_error": None,
        "metro_focus_station_id": None,
        "metro_last_query": "",
        "metro_map_nonce": 0,
        # Journey planner
        "metro_destination": None,  # dict snapshot
        "metro_origin": None,  # {lat, lon, label, source, accuracy_m?} — never a station
        "metro_origin_error": None,
        "metro_request_geo": False,
        "metro_route": None,  # RouteResult.to_dict()
        "metro_route_error": None,
        "metro_show_route": False,
        "metro_travel_mode": "Walking",
        "metro_explorer_status": STATUS_KEYS + [COORDS_AWAITING],
        "metro_origin_framed": False,  # avoid re-zooming on every Streamlit rerun
        "metro_to_station": TO_PLACEHOLDER,
        "metro_station_filter": "",
        "metro_near_me_active": False,
        "metro_near_me_pending_focus": False,
        "metro_near_me_seeded": False,
        "metro_gps_nearest_list": [],
        "metro_cam_seq": 0,
        "metro_soft_land": False,
        "metro_preserve_map": False,
        "metro_map_html_cache": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    st.session_state.metro_line_filter = _normalize_line_filter(
        st.session_state.get("metro_line_filter")
    )
    pills_val = st.session_state.get("metro_line_pills")
    if pills_val is not None and pills_val not in ([ALL_LINES] + LINE_ORDER):
        st.session_state.metro_line_pills = st.session_state.metro_line_filter
    if st.session_state.get("metro_travel_mode") not in TRAVEL_MODES:
        st.session_state.metro_travel_mode = "Walking"


def _friendly_error(code: Optional[str]) -> str:
    if not code:
        return "Something went wrong."
    if code.startswith("nominatim_connection_failed"):
        return ERROR_MESSAGES["nominatim_connection_failed"]
    if code.startswith("nominatim_http"):
        return "The location service returned an error. Please try again shortly."
    if code.startswith("osrm_connection_failed") or code.startswith("osrm_http"):
        return "Could not reach the routing service. Please try again shortly."
    if code.startswith("osrm_") and code not in ERROR_MESSAGES:
        return "Routing failed. Try another travel mode or check your points."
    return ERROR_MESSAGES.get(code, f"Could not complete the request ({code}).")


def _station_lines(station: Dict[str, Any]) -> List[Dict[str, Any]]:
    return list(station.get("lines") or [])


def _station_has_line(station: Dict[str, Any], line: str) -> bool:
    line = _normalize_line_filter(line)
    if line == ALL_LINES:
        return True
    return any(ln.get("line") == line for ln in _station_lines(station))


def _has_operational_line(station: Dict[str, Any]) -> bool:
    return any(ln.get("status") == "operational" for ln in _station_lines(station))


def _coords_awaiting(station: Dict[str, Any]) -> bool:
    lat, lon = station.get("lat"), station.get("lon")
    if lat is None or lon is None:
        return True
    ver = station.get("verification") or {}
    return bool(ver.get("needs_manual_verification"))


def _primary_marker_color(station: Dict[str, Any]) -> str:
    lines = _station_lines(station)
    for preferred in LINE_ORDER:
        for ln in lines:
            if ln.get("line") == preferred and ln.get("status") == "operational":
                return LINE_COLORS[preferred]
    for preferred in LINE_ORDER:
        for ln in lines:
            if ln.get("line") == preferred:
                return LINE_COLORS[preferred]
    return "#E5BC70"


def _metro_station_map_icon(
    name: str,
    *,
    line_color: str = "#C62828",
    line_label: str = "Metro",
) -> folium.DivIcon:
    """Large labeled metro pin so the station reads clearly (not bare rail tracks)."""
    safe_name = _esc(name or "Metro station")
    safe_line = _esc(line_label or "Metro")
    safe_color = html.escape(line_color or "#C62828", quote=True)
    return folium.DivIcon(
        html=(
            f'<div class="metro-station-pin" style="width:160px;margin-left:-18px;margin-top:-36px;'
            f'font-family:Inter,system-ui,sans-serif;pointer-events:none;">'
            f'<div style="width:36px;height:36px;border-radius:50%;background:{safe_color};'
            f"border:3px solid #fff;box-shadow:0 4px 14px rgba(0,0,0,.4);"
            f'display:flex;align-items:center;justify-content:center;">'
            f'<span style="color:#fff;font-size:11px;font-weight:800;letter-spacing:.4px;">M</span>'
            f"</div>"
            f'<div style="margin-top:4px;display:inline-block;max-width:150px;'
            f"background:rgba(33,21,29,.94);color:#F6EBDD;border:1px solid rgba(216,180,119,.35);"
            f'border-radius:10px;padding:5px 8px;box-shadow:0 6px 16px rgba(0,0,0,.35);">'
            f'<div style="font-size:12px;font-weight:700;line-height:1.2;white-space:nowrap;'
            f'overflow:hidden;text-overflow:ellipsis;">{safe_name}</div>'
            f'<div style="font-size:10px;color:#E0B96A;margin-top:2px;font-weight:600;">'
            f"Metro station · {safe_line}</div>"
            f"</div></div>"
        ),
        icon_size=(160, 70),
        icon_anchor=(18, 36),
        class_name="metro-station-map-icon",
    )


def _destination_snapshot(station: Dict[str, Any]) -> Dict[str, Any]:
    lines = _station_lines(station)
    return {
        "station_id": _sid(station),
        "name": station.get("name"),
        "station_code": station.get("station_code"),
        "lat": station.get("lat"),
        "lon": station.get("lon"),
        "primary_status": station.get("primary_status"),
        "lines": list(lines),
        "metro_lines": [ln.get("line") for ln in lines if ln.get("line")],
    }


def _set_destination(
    station: Dict[str, Any],
    *,
    remount_map: bool = False,
) -> None:
    """Unified destination setter — map, explorer, selectbox, and nearest results.

    remount_map=False keeps the live Folium iframe (station taps).
    remount_map=True forces a fresh map (near-me / query bridge).
    """
    snap = _destination_snapshot(station)
    if snap.get("lat") is None or snap.get("lon") is None:
        st.session_state.metro_route_error = "need_destination"
        return
    st.session_state.metro_destination = snap
    st.session_state.metro_focus_station_id = snap.get("station_id")
    st.session_state.metro_route = None
    st.session_state.metro_route_error = None
    st.session_state.metro_show_route = False
    # Stop near-me autofocus from overriding a manual station tap
    st.session_state.metro_near_me_pending_focus = False
    st.session_state.metro_near_me_seeded = True
    st.session_state.metro_cam_seq = int(st.session_state.get("metro_cam_seq") or 0) + 1
    if remount_map:
        st.session_state.metro_soft_land = False
        st.session_state.metro_preserve_map = False
        st.session_state.metro_map_nonce = (
            int(st.session_state.get("metro_map_nonce") or 0) + 1
        )
    else:
        # Soft pick — reuse the pinned map iframe (no full reload flash)
        st.session_state.metro_soft_land = True
        st.session_state.metro_preserve_map = True
    _sync_to_selectbox(snap)


def _fmt_distance_away(km: Any) -> str:
    try:
        d = float(km)
    except (TypeError, ValueError):
        return "—"
    if d < 1:
        return f"{d * 1000:.0f} m away"
    return f"{d:.2f} km away"


def _auto_walk_route_if_ready() -> bool:
    """When origin + destination exist, draw the walking path automatically.

    Returns True if session state changed (caller should rebuild / rerun).
    """
    origin = st.session_state.get("metro_origin") or {}
    destination = st.session_state.get("metro_destination") or {}
    route = st.session_state.get("metro_route")
    if not st.session_state.get("metro_show_route"):
        return False
    if route and route.get("ok"):
        return False
    if st.session_state.get("metro_route_error"):
        return False
    if origin.get("lat") is None or origin.get("lon") is None:
        return False
    if destination.get("lat") is None or destination.get("lon") is None:
        return False
    try:
        result = get_router().route(
            (float(origin["lat"]), float(origin["lon"])),
            (float(destination["lat"]), float(destination["lon"])),
            mode_label="Walking",
        )
    except Exception:
        st.session_state.metro_route_error = "osrm_no_route"
        return True
    st.session_state.metro_route = result.to_dict()
    st.session_state.metro_route_error = (
        None if result.ok else (result.error or "osrm_no_route")
    )
    # Don't double-bump nonce when destination was just set in this same run —
    # one remount with dest+route together keeps the station zoom stable.
    if not st.session_state.get("metro_soft_land"):
        st.session_state.metro_map_nonce = (
            int(st.session_state.get("metro_map_nonce") or 0) + 1
        )
    return True


def _clear_destination_only() -> None:
    st.session_state.metro_destination = None
    st.session_state.metro_focus_station_id = None
    st.session_state.metro_route = None
    st.session_state.metro_route_error = None
    st.session_state.metro_show_route = False
    st.session_state.metro_map_nonce = int(st.session_state.get("metro_map_nonce") or 0) + 1
    _sync_to_selectbox(None)


def _clear_journey() -> None:
    st.session_state.metro_destination = None
    st.session_state.metro_origin = None
    st.session_state.metro_origin_error = None
    st.session_state.metro_route = None
    st.session_state.metro_route_error = None
    st.session_state.metro_show_route = False
    st.session_state.metro_focus_station_id = None
    st.session_state.metro_request_geo = False
    st.session_state.metro_origin_framed = False
    st.session_state.metro_near_me_active = False
    st.session_state.metro_near_me_pending_focus = False
    st.session_state.metro_near_me_seeded = False
    st.session_state.metro_gps_nearest_list = []
    st.session_state.metro_map_nonce = int(st.session_state.get("metro_map_nonce") or 0) + 1
    _sync_to_selectbox(None)


def _find_station(service: MetroService, station_id: str) -> Optional[Dict[str, Any]]:
    for stn in service.stations:
        if _sid(stn) == station_id:
            return stn
    # Also search verified summaries / nearest payloads
    return None


def _match_station_by_latlon(
    stations: Sequence[Dict[str, Any]], lat: float, lon: float, *, tol: float = 0.00035
) -> Optional[Dict[str, Any]]:
    best = None
    best_d = 1e9
    for stn in stations:
        slat, slon = stn.get("lat"), stn.get("lon")
        if slat is None or slon is None:
            continue
        d = abs(float(slat) - lat) + abs(float(slon) - lon)
        if d < best_d:
            best_d = d
            best = stn
    if best is not None and best_d <= tol:
        return best
    return None


def _consume_query_bridge(service: MetroService) -> None:
    """Read map-click / geolocation bridges from URL query params (session-only)."""
    qp = st.query_params
    if qp.get("metro_near_me") is not None:
        st.session_state.metro_near_me_active = True
        st.session_state.metro_near_me_pending_focus = True
        st.session_state.metro_station_q = ""
        st.session_state.metro_route = None
        st.session_state.metro_route_error = None
        try:
            del st.query_params["metro_near_me"]
        except Exception:
            pass
        print("[metro-geo] near_me armed via query bridge", dict(st.query_params))

    dest = qp.get("metro_dest")
    if dest:
        stn = _find_station(service, str(dest))
        plat, plon = qp.get("metro_plat"), qp.get("metro_plon")
        if stn is None and plat is not None and plon is not None:
            try:
                stn = _match_station_by_latlon(
                    service.stations, float(plat), float(plon)
                )
            except (TypeError, ValueError):
                stn = None
        if stn is not None:
            _set_destination(stn, remount_map=True)
            print(f"[metro-pick] query bridge set destination {_sid(stn)}")
            try:
                st.toast(f"Showing {stn.get('name') or 'station'} on map", icon="📍")
            except Exception:
                pass
        elif plat is not None and plon is not None:
            try:
                lat_f, lon_f = float(plat), float(plon)
                st.session_state.metro_destination = {
                    "station_id": str(dest),
                    "name": str(dest),
                    "lat": lat_f,
                    "lon": lon_f,
                    "lines": [],
                    "metro_lines": [],
                }
                st.session_state.metro_near_me_pending_focus = False
                st.session_state.metro_soft_land = False
                st.session_state.metro_preserve_map = False
                st.session_state.metro_cam_seq = (
                    int(st.session_state.get("metro_cam_seq") or 0) + 1
                )
                st.session_state.metro_map_nonce = (
                    int(st.session_state.get("metro_map_nonce") or 0) + 1
                )
                print(f"[metro-pick] query bridge coords-only {lat_f},{lon_f}")
            except (TypeError, ValueError):
                pass
        for key in ("metro_dest", "metro_plat", "metro_plon"):
            try:
                del st.query_params[key]
            except Exception:
                pass

    olat, olon = qp.get("metro_olat"), qp.get("metro_olon")
    if olat is not None and olon is not None:
        try:
            lat_f, lon_f = float(olat), float(olon)
            accuracy_m = None
            raw_acc = qp.get("metro_oacc")
            if raw_acc not in (None, ""):
                try:
                    accuracy_m = float(raw_acc)
                except (TypeError, ValueError):
                    accuracy_m = None
            _apply_geo_origin(lat_f, lon_f, accuracy_m=accuracy_m)
        except (TypeError, ValueError):
            _apply_geo_error("2")
        for key in ("metro_olat", "metro_olon", "metro_oacc", "metro_geo_err"):
            try:
                del st.query_params[key]
            except Exception:
                pass
        return

    geo_err = qp.get("metro_geo_err")
    if geo_err is not None:
        _apply_geo_error(str(geo_err))
        try:
            del st.query_params["metro_geo_err"]
        except Exception:
            pass

    if qp.get("metro_reset") is not None:
        _clear_journey()
        try:
            del st.query_params["metro_reset"]
        except Exception:
            pass


def _inject_metro_page_css() -> None:
    st.markdown(
        """
<style>
/* Map-paper chrome — avoids black divinity flash while the map iframe mounts */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.block-container {
  background:#dcd6cf !important;
  background-image:none !important;
}
.footer { display:none !important; }
[data-testid="stHeader"] { background:transparent !important; pointer-events:none !important; }
/* Hidden Streamlit form bridges — station / GPS sync without full page reload */
[data-testid="stForm"]:has(.metro-pick-bridge),
[data-testid="stForm"]:has(.metro-geo-bridge),
[data-testid="stForm"]:has(.metro-page-geo-bridge),
[data-testid="stForm"]:has(.metro-route-bridge) {
  position:fixed !important;
  left:-9999px !important;
  top:0 !important;
  width:1px !important;
  height:1px !important;
  opacity:0 !important;
  overflow:hidden !important;
  margin:0 !important;
  padding:0 !important;
  z-index:-1 !important;
}
.block-container {
  padding-top:0 !important;
  padding-bottom:0 !important;
  padding-left:0.4rem !important;
  padding-right:0.4rem !important;
  max-width:100% !important;
  transform:none !important;
}
[data-testid="stMainBlockContainer"],
[data-testid="stMain"] {
  transform:none !important;
  filter:none !important;
  perspective:none !important;
}
div[data-testid="stDecoration"] { display:none !important; }

:root {
  --metro-nav-band: 64px;
  --metro-dock-bottom: 16px;
  --metro-panel: #21151D;
  --metro-surface: #30232C;
  --metro-elevated: #382630;
  --metro-text: #F6EBDD;
  --metro-muted: #BDAEB6;
  --metro-gold: #D8B477;
  --metro-gold-action: #C7A05E;
  --metro-gold-ink: #21151D;
  --metro-blue: #53A8E8;
  --metro-border: rgba(216,180,119,.22);
}

/* Compact wide journey panel — centre bottom over the map.
   Use explicit top (not bottom+top:auto) — Streamlit flex blocks bottom anchoring. */
.metro-dock-panel {
  position:fixed !important;
  left:50% !important;
  right:auto !important;
  top:calc(100vh - var(--metro-dock-bottom) - min(42vh, 360px)) !important;
  bottom:auto !important;
  transform:translateX(-50%) !important;
  width:min(400px, calc(100vw - 40px)) !important;
  max-width:min(400px, calc(100vw - 40px)) !important;
  min-height:0 !important;
  max-height:min(42vh, 360px) !important;
  height:auto !important;
  overflow-x:hidden !important;
  overflow-y:auto !important;
  overscroll-behavior:contain;
  z-index:100 !important;
  margin:0 !important;
  padding:14px 22px 10px !important;
  background:rgba(33,21,29,.96) !important;
  border:1px solid var(--metro-border) !important;
  border-radius:24px !important;
  box-shadow:0 18px 44px rgba(0,0,0,.45), 0 0 0 1px rgba(216,180,119,.06) !important;
  backdrop-filter:none !important;
  -webkit-backdrop-filter:none !important;
  pointer-events:auto !important;
  color:var(--metro-text) !important;
  flex:0 0 auto !important;
  align-self:center !important;
}
.metro-dock-panel, .metro-dock-panel * { color:inherit; }
.metro-dock-panel [data-testid="stMarkdownContainer"] p,
.metro-dock-panel [data-testid="stCaption"],
.metro-dock-panel small {
  color:var(--metro-muted) !important;
}

.metro-header {
  display:flex; align-items:center; justify-content:space-between; gap:10px;
  margin:0 0 6px;
}
.metro-header-copy { min-width:0; }
.metro-kicker {
  font-family:'Inter',sans-serif; font-size:9px; letter-spacing:2.2px;
  color:var(--metro-gold); text-transform:uppercase; margin:0 0 2px; font-weight:600;
}
.metro-heading {
  font-family:'Cormorant Garamond',Georgia,serif; font-weight:600;
  font-size:1.15rem; color:var(--metro-text); margin:0; line-height:1.05;
}
.metro-subhead { display:none; }
.metro-mark {
  flex:0 0 auto; width:28px; height:28px; border-radius:8px;
  display:flex; align-items:center; justify-content:center;
  background:var(--metro-elevated); border:1px solid rgba(216,180,119,.35);
  color:var(--metro-gold); font-size:16px; line-height:1;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.04);
}

.metro-section-label {
  font-family:'Inter',sans-serif; font-size:10px; letter-spacing:1.7px;
  text-transform:uppercase; color:var(--metro-muted); margin:8px 0 4px; font-weight:600;
}
.metro-journey-head {
  display:flex; align-items:center; justify-content:space-between; gap:10px;
  margin:0 0 6px;
}
.metro-journey-head .metro-section-label { margin:0; }
a.metro-reset-link {
  font-family:'Inter',sans-serif; font-size:12px; font-weight:500;
  color:var(--metro-gold) !important; text-decoration:none !important;
  white-space:nowrap;
}
a.metro-reset-link:hover { color:#E8C98A !important; text-decoration:underline !important; }

/* Station sheet — rendered in parent page (not iframe) so clicks navigate */
.metro-sheet { margin:0 0 4px; }
.metro-sheet-hint {
  display:flex; align-items:center; justify-content:space-between; gap:10px;
  font-family:'Inter',sans-serif; font-size:11.5px; color:#C9B8C0;
  margin:0 0 8px; line-height:1.35;
}
/* Hidden forms, camera target, and 0px iframes are still flex items, so the
   panel's 16px gap stacks empty rows above the hint. Pull them out of flow. */
.metro-dock-panel > [data-testid="stLayoutWrapper"]:has([data-testid="stForm"]),
.metro-dock-panel > [data-testid="stElementContainer"]:has(#metro-cam-target),
.metro-dock-panel > [data-testid="stElementContainer"]:has(.metro-dock-anchor),
.metro-dock-panel > [data-testid="stElementContainer"]:has(iframe[height="0"]) {
  position:absolute !important;
  left:0 !important;
  top:0 !important;
  width:0 !important;
  height:0 !important;
  min-height:0 !important;
  margin:0 !important;
  padding:0 !important;
  overflow:hidden !important;
}
/* Kill Streamlit's default top gap above the sheet hint */
.metro-dock-panel [data-testid="stElementContainer"]:has(.metro-dock-anchor) {
  display:none !important;
  height:0 !important;
  margin:0 !important;
  padding:0 !important;
}
.metro-dock-panel > div:first-child,
.metro-dock-panel [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:first-child,
.metro-dock-panel [data-testid="stElementContainer"]:has(.metro-sheet),
.metro-dock-panel [data-testid="stElementContainer"]:has(.metro-sheet-hint) {
  margin-top:0 !important;
  padding-top:0 !important;
}
.metro-dock-panel [data-testid="stElementContainer"]:has(.metro-sheet) [data-testid="stMarkdownContainer"],
.metro-dock-panel [data-testid="stElementContainer"]:has(.metro-sheet-hint) [data-testid="stMarkdownContainer"],
.metro-dock-panel [data-testid="stElementContainer"]:has(.metro-sheet) [data-testid="stMarkdownContainer"] p,
.metro-dock-panel [data-testid="stElementContainer"]:has(.metro-sheet-hint) [data-testid="stMarkdownContainer"] p {
  margin-top:0 !important;
  margin-bottom:0 !important;
  padding-top:0 !important;
}
.metro-dock-panel [data-testid="stVerticalBlock"] {
  gap:0.2rem !important;
  padding-top:0 !important;
  margin-top:0 !important;
}
.metro-sheet-hint a {
  color:var(--metro-gold) !important; text-decoration:none !important;
  font-size:12px; font-weight:500; white-space:nowrap;
}
.metro-sheet-hint a:hover { color:#E8C98A !important; text-decoration:underline !important; }
.metro-sheet-search-row {
  display:flex; align-items:stretch; gap:8px; margin:0 0 2px;
}
/* Magnifier at the end of the search field (column :has marker) */
[data-testid="stColumn"]:has(.metro-sheet-search) {
  position:relative !important;
}
[data-testid="stColumn"]:has(.metro-sheet-search)::after {
  content:"";
  position:absolute; right:16px; top:50%; transform:translateY(-50%);
  width:16px; height:16px; z-index:5; pointer-events:none;
  background-color:#BDAEB6;
  -webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Ccircle cx='11' cy='11' r='6.5' fill='none' stroke='%23000' stroke-width='2'/%3E%3Cpath d='M16.2 16.2L20 20' fill='none' stroke='%23000' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E") center / contain no-repeat;
  mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Ccircle cx='11' cy='11' r='6.5' fill='none' stroke='%23000' stroke-width='2'/%3E%3Cpath d='M16.2 16.2L20 20' fill='none' stroke='%23000' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E") center / contain no-repeat;
}
.metro-dock-panel [data-testid="stHorizontalBlock"]:has(.metro-sheet-search) {
  flex-wrap:nowrap !important;
  align-items:center !important;
}
.metro-dock-panel [data-testid="stColumn"]:has(.metro-sheet-search) {
  flex:1 1 auto !important;
  min-width:0 !important;
  width:auto !important;
}
.metro-dock-panel .metro-sheet-search [data-testid="stTextInput"] input,
.metro-dock-panel .metro-sheet-search input,
[data-testid="stColumn"]:has(.metro-sheet-search) input {
  background:#1A1016 !important; color:#F6EBDD !important;
  border:1px solid rgba(216,180,119,.16) !important;
  border-radius:999px !important; padding:10px 40px 10px 14px !important;
  font-size:13.5px !important;
}
/* Location pin — column marker + button are siblings; do not require .metro-dock-panel */
[data-testid="stColumn"]:has(.metro-near-me-btn) {
  flex:0 0 2.7rem !important;
  width:2.7rem !important;
  min-width:2.7rem !important;
}
[data-testid="stColumn"]:has(.metro-near-me-btn) .stButton,
[data-testid="stColumn"]:has(.metro-near-me-btn) [data-testid="stButton"] {
  width:2.55rem !important;
}
[data-testid="stColumn"]:has(.metro-near-me-btn) .stButton > button,
[data-testid="stColumn"]:has(.metro-near-me-btn) button[kind],
[data-testid="stColumn"]:has(.metro-near-me-btn) button {
  background:rgba(216,180,119,.12) !important;
  color:transparent !important;
  border:1px solid rgba(216,180,119,.42) !important;
  border-radius:999px !important;
  width:2.55rem !important;
  min-width:2.55rem !important;
  max-width:2.55rem !important;
  height:2.55rem !important;
  min-height:2.55rem !important;
  padding:0 !important;
  font-size:0 !important;
  line-height:0 !important;
  overflow:hidden !important;
  position:relative !important;
  text-indent:-9999px !important;
}
[data-testid="stColumn"]:has(.metro-near-me-btn) .stButton > button *,
[data-testid="stColumn"]:has(.metro-near-me-btn) button * {
  font-size:0 !important;
  line-height:0 !important;
  color:transparent !important;
  opacity:0 !important;
  visibility:hidden !important;
}
[data-testid="stColumn"]:has(.metro-near-me-btn) .stButton > button::before,
[data-testid="stColumn"]:has(.metro-near-me-btn) button::before {
  content:"" !important;
  position:absolute !important; left:50% !important; top:50% !important;
  width:18px !important; height:18px !important;
  transform:translate(-50%, -50%) !important;
  background-color:#D8B477 !important;
  opacity:1 !important;
  visibility:visible !important;
  text-indent:0 !important;
  -webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23000' d='M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z'/%3E%3C/svg%3E") center / contain no-repeat !important;
  mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23000' d='M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z'/%3E%3C/svg%3E") center / contain no-repeat !important;
}
[data-testid="stColumn"]:has(.metro-near-me-btn) .stButton > button:hover,
[data-testid="stColumn"]:has(.metro-near-me-btn) button:hover {
  background:rgba(216,180,119,.22) !important;
  border-color:rgba(216,180,119,.65) !important;
}
[data-testid="stColumn"]:has(.metro-near-me-btn.is-active) .stButton > button,
[data-testid="stColumn"]:has(.metro-near-me-btn.is-active) button {
  background:rgba(216,180,119,.28) !important;
  border-color:#D8B477 !important;
}
.metro-sheet-list {
  display:flex; flex-direction:column; gap:8px;
  max-height:210px; overflow:auto; margin:8px 0 4px; padding-right:2px;
}
.metro-sheet-row {
  display:flex; align-items:center; justify-content:space-between; gap:12px;
  background:#3A252E !important; border:1px solid rgba(216,180,119,.08);
  border-radius:14px; padding:11px 12px 11px 14px;
  text-decoration:none !important; color:inherit !important;
  cursor:pointer; transition:background .12s ease, border-color .12s ease;
}
.metro-sheet-row:hover {
  background:#452C37 !important; border-color:rgba(216,180,119,.2);
  text-decoration:none !important;
}
.metro-sheet-row.is-selected {
  background:#4A3038 !important;
  border:2px solid #F0CD85 !important;
  box-shadow:0 0 0 1px rgba(240,205,133,.35), inset 0 0 0 1px rgba(240,205,133,.2);
}
.metro-sheet-row .copy { min-width:0; flex:1; }
.metro-sheet-row .nm {
  font-size:14.5px; font-weight:650; color:#FFFFFF !important; line-height:1.2;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
.metro-sheet-row .meta {
  margin-top:4px; font-size:12px; font-weight:500; color:#E0B96A !important;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
.metro-sheet-row .map-ext {
  flex:0 0 auto;
  display:inline-flex; align-items:center; justify-content:center;
  width:36px; height:36px; border-radius:10px;
  background:#C62828; color:#fff !important;
  text-decoration:none !important;
  box-shadow:0 2px 8px rgba(198,40,40,.28);
  transition:background .12s ease, transform .12s ease;
}
.metro-sheet-row a.map-ext:hover {
  background:#B71C1C; transform:translateY(-1px);
}
.metro-sheet-row .map-ext svg {
  width:18px; height:18px; display:block; pointer-events:none;
}
.metro-sheet-empty, .metro-sheet-foot {
  font-family:'Inter',sans-serif; font-size:11.5px; color:#9A8792;
  margin:6px 0 2px;
}
.metro-sheet-empty {
  padding:16px 12px; text-align:center; background:#3A252E; border-radius:14px;
}
.metro-sheet-empty[hidden],
.metro-sheet-foot[hidden],
.metro-sheet-row[hidden] {
  display:none !important;
}

/* Connected FROM / TO */
.metro-od {
  position:relative;
  padding:2px 0 2px 20px;
  margin:0 0 6px;
}
.metro-od::before {
  content:"";
  position:absolute; left:6px; top:18px; bottom:18px; width:2px;
  background:linear-gradient(180deg, rgba(83,168,232,.7), rgba(216,180,119,.55));
  border-radius:2px;
}
.metro-od-from, .metro-od-to { position:relative; margin:0 0 6px; }
.metro-od-from::before, .metro-od-to::before {
  content:""; position:absolute; left:-20px; top:14px;
  width:11px; height:11px; border-radius:50%;
  box-sizing:border-box; z-index:1;
}
.metro-od-from::before {
  background:var(--metro-blue);
  box-shadow:0 0 0 3px rgba(83,168,232,.22);
}
.metro-od-to::before {
  background:var(--metro-gold);
  box-shadow:0 0 0 3px rgba(216,180,119,.18);
  border-radius:50% 50% 50% 0;
  transform:rotate(-45deg);
  width:10px; height:10px;
}

.metro-field {
  background:var(--metro-surface);
  border:1px solid rgba(216,180,119,.16);
  border-radius:12px;
  padding:8px 12px;
  color:var(--metro-text);
}
.metro-field .label {
  font-family:'Inter',sans-serif; font-size:10px; letter-spacing:1.4px;
  text-transform:uppercase; color:var(--metro-muted); margin:0 0 4px;
}
.metro-field .value {
  font-family:'Inter',sans-serif; font-size:13.5px; color:var(--metro-text);
  margin:0; line-height:1.35;
}
.metro-field.is-empty .value { color:var(--metro-muted); }
.metro-field.is-origin { border-color:rgba(83,168,232,.35); }

.metro-dock-panel .metro-geo-btn .stButton > button,
.metro-dock-panel [data-testid="stBaseButton-secondary"].metro-geo,
.metro-dock-panel .metro-geo-btn button {
  background:var(--metro-surface) !important;
  background-image:none !important;
  color:var(--metro-text) !important;
  border:1px solid rgba(216,180,119,.16) !important;
  border-radius:12px !important;
  box-shadow:none !important;
  min-height:2.55rem !important;
  justify-content:flex-start !important;
  padding-left:12px !important;
  font-weight:500 !important;
  text-align:left !important;
}
.metro-dock-panel .metro-geo-btn .stButton > button:hover {
  background:var(--metro-elevated) !important;
  border-color:rgba(83,168,232,.4) !important;
  color:var(--metro-text) !important;
}

/* Soft secondary controls */
.metro-dock-panel [data-testid="stBaseButton-secondary"],
.metro-dock-panel button[kind="secondary"],
.metro-dock-panel button[data-testid="baseButton-secondary"],
.metro-dock-panel .stButton > button {
  background:var(--metro-surface) !important;
  background-image:none !important;
  color:var(--metro-text) !important;
  border:1px solid rgba(216,180,119,.18) !important;
  border-radius:12px !important;
  box-shadow:none !important;
  font-weight:500 !important;
  min-height:2.2rem !important;
}
.metro-dock-panel .stButton > button:hover {
  background:var(--metro-elevated) !important;
  border-color:rgba(216,180,119,.34) !important;
  color:var(--metro-text) !important;
}

/* Primary gold CTA */
.metro-dock-panel [data-testid="stBaseButton-primary"],
.metro-dock-panel button[kind="primary"],
.metro-dock-panel button[data-testid="baseButton-primary"],
.metro-dock-panel [data-testid="stFormSubmitButton"] > button[kind="primary"],
.metro-dock-panel .stButton > button[kind="primary"],
.metro-dock-panel .metro-route-btn .stButton > button {
  background:var(--metro-gold-action) !important;
  background-image:none !important;
  color:var(--metro-gold-ink) !important;
  border:1px solid #B8924E !important;
  border-radius:12px !important;
  box-shadow:0 6px 16px rgba(0,0,0,.28) !important;
  font-weight:700 !important;
  letter-spacing:.2px !important;
  min-height:2.55rem !important;
}
.metro-dock-panel [data-testid="stBaseButton-primary"]:hover,
.metro-dock-panel button[kind="primary"]:hover,
.metro-dock-panel .stButton > button[kind="primary"]:hover,
.metro-dock-panel .metro-route-btn .stButton > button:hover {
  background:#D4AF6A !important;
  border-color:#C7A05E !important;
  color:#1A1016 !important;
}
.metro-dock-panel [data-testid="stBaseButton-primary"]:focus-visible,
.metro-dock-panel .metro-route-btn .stButton > button:focus-visible {
  outline:2px solid var(--metro-gold) !important;
  outline-offset:2px !important;
}
.metro-dock-panel [data-testid="stBaseButton-primary"]:disabled,
.metro-dock-panel .metro-route-btn .stButton > button:disabled {
  background:#5A4A3A !important;
  color:#C9B7A4 !important;
  border-color:#4A3B30 !important;
  box-shadow:none !important;
  opacity:1 !important;
}

.metro-dock-panel [data-testid="stTextInput"] input,
.metro-dock-panel input[type="text"],
.metro-dock-panel div[data-baseweb="input"] > div,
.metro-dock-panel div[data-baseweb="base-input"] {
  background:var(--metro-surface) !important;
  background-color:var(--metro-surface) !important;
  color:var(--metro-text) !important;
  border:1px solid rgba(216,180,119,.16) !important;
  border-radius:12px !important;
  box-shadow:none !important;
  caret-color:var(--metro-text) !important;
}
.metro-dock-panel [data-testid="stTextInput"] input::placeholder,
.metro-dock-panel input[type="text"]::placeholder {
  color:rgba(189,174,182,.85) !important;
}
.metro-dock-panel [data-testid="stTextInput"] > div,
.metro-dock-panel [data-testid="stTextInput"] div[data-baseweb="input"] {
  background:transparent !important;
  border:none !important;
  box-shadow:none !important;
}
.metro-dock-panel [data-testid="stSelectbox"] > div,
.metro-dock-panel [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
  background:var(--metro-surface) !important;
  border-color:rgba(216,180,119,.16) !important;
  border-radius:14px !important;
  color:var(--metro-text) !important;
  box-shadow:none !important;
  min-height:2.55rem !important;
}
.metro-dock-panel [data-testid="stExpander"] details {
  background:var(--metro-surface) !important;
  border:1px solid rgba(216,180,119,.14) !important;
  border-radius:12px !important;
}
.metro-dock-panel [data-testid="stExpander"] {
  border:none !important; background:transparent !important; margin-top:4px !important;
}
.metro-dock-panel [data-testid="stExpander"] summary {
  font-size:12.5px !important; color:var(--metro-text) !important; padding:8px 10px !important;
  font-weight:500 !important;
}
.metro-dock-panel div[data-testid="stForm"] {
  border:none !important; background:transparent !important; padding:0 !important;
}
.metro-dock-panel [data-testid="stHorizontalBlock"] { gap:0.3rem !important; }
/* Tighten Streamlit's default vertical rhythm inside the dock */
.metro-dock-panel [data-testid="stVerticalBlock"] {
  gap:0.28rem !important;
}
.metro-dock-panel [data-testid="stElementContainer"],
.metro-dock-panel .element-container {
  margin-bottom:0 !important;
}
.metro-dock-panel [data-testid="stCaptionContainer"],
.metro-dock-panel [data-testid="stCaption"] {
  margin-top:0 !important;
  margin-bottom:0 !important;
}
.metro-route-btn { margin-top:2px; }

/* Current location control with pin glyph */
.metro-dock-panel .metro-geo-btn .stButton > button {
  display:inline-flex !important;
  align-items:center !important;
  gap:8px !important;
}
.metro-dock-panel .metro-geo-btn .stButton > button::before {
  content:"";
  width:14px; height:14px; flex:0 0 14px;
  border-radius:50% 50% 50% 0;
  transform:rotate(-45deg);
  background:var(--metro-blue);
  box-shadow:0 0 0 3px rgba(83,168,232,.22);
}
.metro-from-status {
  display:flex; align-items:center; gap:8px;
  background:var(--metro-surface);
  border:1px solid rgba(83,168,232,.35);
  border-radius:12px;
  padding:8px 12px;
  margin:0 0 6px;
}
.metro-from-status .pin {
  width:12px; height:12px; flex:0 0 12px;
  border-radius:50% 50% 50% 0; transform:rotate(-45deg);
  background:var(--metro-blue);
  box-shadow:0 0 0 3px rgba(83,168,232,.22);
}
.metro-from-status .copy { min-width:0; }
.metro-from-status .title {
  font-family:'Inter',sans-serif; font-size:13px; color:var(--metro-text); margin:0; line-height:1.3;
}
.metro-from-status .sub {
  font-family:'Inter',sans-serif; font-size:11px; color:var(--metro-muted); margin:1px 0 0;
}
.metro-dest-chip {
  background:var(--metro-elevated);
  border:1px solid rgba(216,180,119,.28);
  border-radius:12px;
  padding:8px 12px;
  margin:0 0 6px;
}
.metro-dest-chip .label {
  font-size:10px; letter-spacing:1.4px; text-transform:uppercase;
  color:var(--metro-muted); margin:0 0 2px;
}
.metro-dest-chip .name {
  font-family:'Cormorant Garamond',Georgia,serif; font-size:1.1rem;
  color:var(--metro-text); margin:0; line-height:1.2;
}
.metro-station-pick-list {
  max-height:220px; overflow-y:auto; overflow-x:hidden;
  margin:4px 0 6px; padding-right:2px;
  -webkit-overflow-scrolling:touch;
  border:1px solid rgba(216,180,119,.12);
  border-radius:12px;
  background:rgba(48,35,44,.55);
}
.metro-station-pick {
  display:block;
  padding:9px 12px;
  border-bottom:1px solid rgba(216,180,119,.1);
  text-decoration:none !important;
  color:var(--metro-text) !important;
  transition:background .12s ease;
}
.metro-station-pick:last-child { border-bottom:none; }
.metro-station-pick:hover {
  background:rgba(216,180,119,.08);
}
.metro-station-pick.is-selected {
  background:rgba(199,160,94,.16);
  border-left:2px solid var(--metro-gold);
}
.metro-station-pick .nm {
  font-family:'Cormorant Garamond',Georgia,serif; font-size:1.02rem;
  color:var(--metro-text); line-height:1.2;
}
.metro-station-pick .meta {
  font-family:'Inter',sans-serif; font-size:10.5px; color:var(--metro-muted);
  margin-top:2px;
}

.metro-result-card, .metro-station-card {
  background:var(--metro-elevated);
  border:1px solid rgba(216,180,119,.12);
  border-radius:12px;
  padding:10px 12px;
  margin:0 0 8px;
}
.metro-result-card.is-nearest,
.metro-station-card.is-selected {
  background:#43303A;
  border-color:rgba(216,180,119,.4);
}
.metro-result-name, .metro-station-name {
  font-family:'Cormorant Garamond',Georgia,serif; font-size:1.08rem; color:var(--metro-text);
  margin:0; line-height:1.25; word-break:break-word;
}
.metro-result-meta, .metro-station-meta {
  font-family:'Inter',sans-serif; font-size:11px; color:var(--metro-muted); margin-top:3px;
  line-height:1.35;
}
.metro-chip {
  display:inline-flex; align-items:center; gap:4px;
  padding:2px 8px; border-radius:999px; font-size:10px;
  margin:5px 4px 0 0; border:1px solid rgba(216,180,119,.22);
  color:var(--metro-gold); background:rgba(216,180,119,.08);
}
.metro-chip .dot { width:6px; height:6px; border-radius:50%; flex:0 0 auto; }
.metro-badge {
  display:inline-block; padding:2px 7px; border-radius:999px; font-size:10px;
  margin:4px 4px 0 0; font-family:'Inter',sans-serif;
  color:var(--metro-muted); background:rgba(255,255,255,.04);
  border:1px solid rgba(216,180,119,.16);
}
.metro-badge.warn { color:var(--metro-gold); border-color:rgba(216,180,119,.4); }
.metro-route-summary {
  font-family:'Inter',sans-serif; font-size:12px; color:var(--metro-text);
  padding:8px 0 2px; border-top:1px solid rgba(216,180,119,.16); margin-top:6px;
}
.metro-steps {
  max-height:120px; overflow:auto; margin-top:4px;
  font-family:'Inter',sans-serif; font-size:11px; color:var(--metro-muted);
}
.metro-steps div { padding:3px 0; border-bottom:1px solid rgba(216,180,119,.1); }
.metro-explorer-list {
  max-height:240px; overflow-y:auto; overflow-x:hidden;
  margin-top:8px; padding-right:4px;
  -webkit-overflow-scrolling:touch;
}
.metro-pick-dest {
  display:inline-block; margin-top:6px; padding:5px 10px;
  border-radius:8px; background:rgba(199,160,94,.2); color:var(--metro-gold) !important;
  font-size:11px; text-decoration:none; font-family:Inter,sans-serif;
  border:1px solid rgba(216,180,119,.28);
}

/* Compact colour-coded line pills */
.metro-dock-panel [data-testid="stPills"] button,
.metro-dock-panel [data-testid="stButtonGroup"] button {
  font-size:11px !important; padding:5px 10px !important; min-height:0 !important;
  background:var(--metro-surface) !important; color:var(--metro-text) !important;
  border:1px solid rgba(216,180,119,.14) !important; border-radius:999px !important;
}
.metro-dock-panel [data-testid="stPills"] button::before,
.metro-dock-panel [data-testid="stButtonGroup"] button::before {
  content:""; display:inline-block; width:7px; height:7px; border-radius:50%;
  margin-right:6px; vertical-align:middle;
}
.metro-dock-panel [data-testid="stPills"] button:nth-child(1)::before,
.metro-dock-panel [data-testid="stButtonGroup"] button:nth-child(1)::before { background:var(--metro-gold); }
.metro-dock-panel [data-testid="stPills"] button:nth-child(2)::before,
.metro-dock-panel [data-testid="stButtonGroup"] button:nth-child(2)::before { background:#2F6FED; }
.metro-dock-panel [data-testid="stPills"] button:nth-child(3)::before,
.metro-dock-panel [data-testid="stButtonGroup"] button:nth-child(3)::before { background:#1FA971; }
.metro-dock-panel [data-testid="stPills"] button:nth-child(4)::before,
.metro-dock-panel [data-testid="stButtonGroup"] button:nth-child(4)::before { background:#9B4DCA; }
.metro-dock-panel [data-testid="stPills"] button:nth-child(5)::before,
.metro-dock-panel [data-testid="stButtonGroup"] button:nth-child(5)::before { background:#E67E22; }
.metro-dock-panel [data-testid="stPills"] button:nth-child(6)::before,
.metro-dock-panel [data-testid="stButtonGroup"] button:nth-child(6)::before { background:#D4A017; }

/* Hide music completely on Metro — map + journey only */
body:has(.metro-dock-anchor) .music-player,
body:has(.metro-dock-anchor) #kali-music-player {
  display:none !important;
  visibility:hidden !important;
  pointer-events:none !important;
  opacity:0 !important;
}
#metro-geo-status {
  position:fixed; left:50%; top:72px; transform:translateX(-50%);
  z-index:1000002; background:#30232C; color:#F6EBDD;
  border:1px solid rgba(216,180,119,.35); padding:8px 14px; border-radius:10px;
  font:12.5px/1.35 Inter,sans-serif; box-shadow:0 10px 28px rgba(0,0,0,.35);
  pointer-events:none;
}

@media (max-width:900px) {
  .metro-dock-panel {
    width:min(380px, calc(100vw - 28px)) !important;
    max-width:min(380px, calc(100vw - 28px)) !important;
    max-height:min(44vh, 360px) !important;
    top:calc(100vh - var(--metro-dock-bottom) - min(44vh, 360px)) !important;
  }
}
@media (max-width:720px) {
  :root { --metro-nav-band: 56px; --metro-dock-bottom: 10px; }
  .metro-dock-panel {
    left:50% !important;
    right:auto !important;
    width:min(400px, calc(100vw - 24px)) !important;
    max-width:min(400px, calc(100vw - 24px)) !important;
    top:calc(100vh - 10px - min(48vh, 380px)) !important;
    bottom:auto !important;
    transform:translateX(-50%) !important;
    max-height:min(48vh, 380px) !important;
    height:auto !important;
    padding:14px 22px 10px !important;
  }
  .metro-heading { font-size:1.05rem; }
  .metro-explorer-list { max-height:100px; }
}
</style>
        """,
        unsafe_allow_html=True,
    )
    components.html(
        """
<script>
(function () {
  function pinDock() {
    try {
      var doc = window.parent.document;
      if (!doc.querySelector(".metro-page-active")) return;
      var anchor = doc.querySelector(".metro-dock-anchor");
      if (!anchor) return;
      var node = anchor;
      var target = null;
      while (node) {
        if (node.getAttribute && node.getAttribute("data-testid") === "stVerticalBlock") {
          target = node;
          break;
        }
        node = node.parentElement;
      }
      if (target) {
        doc.querySelectorAll(".metro-dock-panel").forEach(function (el) {
          if (el !== target) el.classList.remove("metro-dock-panel");
        });
        target.classList.add("metro-dock-panel");
        target.setAttribute("data-metro-dock", "1");
        var vw = window.parent.innerWidth || 1200;
        var isNarrow = vw <= 720;
        var bottom = isNarrow ? 10 : 16;
        var vh = window.parent.innerHeight || 800;
        var maxH = isNarrow
          ? Math.min(vh * 0.48, 380)
          : Math.min(vh * 0.42, 360);
        var width = vw <= 500
          ? "calc(100vw - 24px)"
          : "min(400px, calc(100vw - 48px))";
        target.style.setProperty("position", "fixed", "important");
        target.style.setProperty("left", "50%", "important");
        target.style.setProperty("right", "auto", "important");
        target.style.setProperty("bottom", "auto", "important");
        target.style.setProperty("transform", "translateX(-50%)", "important");
        target.style.setProperty("width", width, "important");
        target.style.setProperty("max-width", width, "important");
        target.style.setProperty("min-height", "0", "important");
        target.style.setProperty("max-height", maxH + "px", "important");
        target.style.setProperty("height", "auto", "important");
        target.style.setProperty("overflow", "hidden", "important");
        target.style.setProperty("top", "0px", "important");
        // Prefer visible box height (ignores collapsed expander guts in scrollHeight)
        var natural = Math.ceil(target.getBoundingClientRect().height || 200);
        var panelH = Math.max(150, Math.min(natural, maxH));
        var top = Math.max(bottom, vh - bottom - panelH);
        target.style.setProperty("height", panelH + "px", "important");
        target.style.setProperty("top", top + "px", "important");
        target.style.setProperty("overflow-x", "hidden", "important");
        target.style.setProperty("overflow-y", "auto", "important");
        target.style.setProperty("z-index", "100", "important");
        target.style.setProperty("pointer-events", "auto", "important");
        target.style.setProperty("flex", "0 0 auto", "important");
        target.style.setProperty("background", "#21151D", "important");
        target.style.setProperty("backdrop-filter", "none", "important");
        target.style.setProperty("border", "1px solid rgba(216,180,119,.22)", "important");
        target.style.setProperty("box-shadow", "0 18px 44px rgba(0,0,0,.45)", "important");
        target.style.setProperty("border-radius", "24px", "important");
        target.style.setProperty("padding", "14px 22px 10px", "important");
      }
      // Pause + hide any lingering music player on Metro
      doc.querySelectorAll(".music-player, #kali-music-player").forEach(function (el) {
        el.style.setProperty("display", "none", "important");
        el.style.setProperty("visibility", "hidden", "important");
        el.style.setProperty("pointer-events", "none", "important");
        try {
          var audio = el.querySelector("audio");
          if (audio) audio.pause();
          if (el._kaliAudio) el._kaliAudio.pause();
        } catch (e2) {}
      });
    } catch (e) {}
  }
  pinDock();
  setTimeout(pinDock, 80);
  setTimeout(pinDock, 300);
  setTimeout(pinDock, 900);
  window.parent.addEventListener("resize", pinDock);
})();
</script>
        """,
        height=0,
        width=0,
    )


def _geo_preserve_dest_id() -> str:
    dest = st.session_state.get("metro_destination") or {}
    return str(dest.get("station_id") or "")


# Streamlit components.html runs in a sandboxed about:srcdoc frame — it cannot
# call parent.location.assign. Install a MutationObserver on the parent page and
# navigate by setting #metro-nav-beacon[data-url] from the iframe instead.
_METRO_NAV_BRIDGE_JS = r"""
    function ensureNavBridge() {
      if (win.__metroNavBridgeV3) return true;
      try {
        var s = doc.createElement("script");
        s.textContent = "(function(){if(window.__metroNavBridgeV4)return;window.__metroNavBridgeV4=1;function boot(){var el=document.getElementById('metro-nav-beacon');if(!el){el=document.createElement('div');el.id='metro-nav-beacon';el.setAttribute('aria-hidden','true');el.style.cssText='display:none!important';(document.body||document.documentElement).appendChild(el);}if(el.__metroObs)return;el.__metroObs=new MutationObserver(function(){var u=el.getAttribute('data-url');if(!u)return;el.removeAttribute('data-url');try{console.log('[metro-nav] beacon assign',u);}catch(e0){}try{window.location.assign(u);}catch(e){window.location.href=u;}});el.__metroObs.observe(el,{attributes:true,attributeFilter:['data-url']});}boot();window.__metroNavigateTo=function(u){boot();var el=document.getElementById('metro-nav-beacon');if(el)el.setAttribute('data-url',String(u||''));else{try{location.assign(u);}catch(e){location.href=u;}}};})();";
        (doc.documentElement || doc.body).appendChild(s);
        win.__metroNavBridgeV4 = 1;
        return true;
      } catch (e) {
        try { console.warn("[metro-nav] bridge install failed", e); } catch (e2) {}
        return false;
      }
    }
    function navigateTop(url) {
      ensureNavBridge();
      try { console.log("[metro-nav] navigateTop", String(url || "")); } catch (eLog) {}
      try {
        if (typeof win.__metroNavigateTo === "function") {
          win.__metroNavigateTo(String(url || ""));
          return true;
        }
      } catch (e) {}
      try {
        var el = doc.getElementById("metro-nav-beacon");
        if (el) {
          el.setAttribute("data-url", String(url || ""));
          return true;
        }
      } catch (e2) {}
      try {
        win.location.assign(url);
        return true;
      } catch (e3) {
        try { console.warn("[metro-nav] assign blocked", e3); } catch (e4) {}
        return false;
      }
    }
"""


def _inject_geolocation_click_hook() -> None:
    """Bind Use My Location to real geolocation on a user gesture.

    Asking for geolocation after a Streamlit rerun loses the transient user
    activation, so browsers ignore/deny the prompt. Capture the button click
    on the parent page and call navigator.geolocation in that same gesture.

    Sync via the hidden metro_geo_bridge form (no location.assign). Browser
    "Redirect Blocker" extensions abort same-tab assigns and were sending
    users back through a bare reload / welcome race.
    """
    preserve = _geo_preserve_dest_id()
    # Live config node so destination survives without re-binding the hook
    st.markdown(
        f'<div id="metro-geo-config" data-preserve-dest="{_esc(preserve)}" style="display:none"></div>',
        unsafe_allow_html=True,
    )
    components.html(
        """
<script>
(function () {
    function install() {
    var win = window.parent;
    try { if (win.top && win.top.document) win = win.top; } catch (e) {}
    var doc = win.document;
    var LOG = "[metro-geo]";
    function log() {
      try {
        var args = Array.prototype.slice.call(arguments);
        args.unshift(LOG);
        console.log.apply(console, args);
      } catch (e) {}
    }
    // Versioned so hot-reloads replace a broken prior hook
    if (doc.__metroGeoClickHooked === 18) return;
    doc.__metroGeoClickHooked = 18;
    log("click hook bound v18 (near-me toggle)");
    try {
      log("boot context", {
        href: String(win.location.href || ""),
        search: String(win.location.search || ""),
        kali_welcome_v1: (function () {
          try { return win.localStorage.getItem("kali_welcome_v1"); } catch (e) { return "ERR"; }
        })(),
        geoForm: !!doc.querySelector('[data-testid="stForm"]:has(.metro-page-geo-bridge)')
      });
    } catch (eBoot) {}

    function status(msg) {
      var banner = doc.getElementById("metro-geo-status");
      if (!banner) {
        banner = doc.createElement("div");
        banner.id = "metro-geo-status";
        doc.body.appendChild(banner);
      }
      banner.textContent = msg || "";
      banner.style.display = msg ? "block" : "none";
    }

    function setNativeInput(input, value) {
      var proto = win.HTMLInputElement.prototype;
      var desc = Object.getOwnPropertyDescriptor(proto, "value");
      var next = String(value);
      // React ignores the input event if the value tracker already matches
      // the new DOM value — Streamlit then submits the previous (empty) widget.
      if (input._valueTracker && input._valueTracker.setValue) {
        try { input._valueTracker.setValue(String(input.value || "")); } catch (e) {}
      }
      if (desc && desc.set) desc.set.call(input, next);
      else input.value = next;
      input.dispatchEvent(new Event("input", { bubbles: true }));
      input.dispatchEvent(new Event("change", { bubbles: true }));
    }

    function submitGeoForm(payload) {
      // Prefer the Metro sheet fragment form — site-wide form shares an old
      // class and does not rebuild the nearest-station sheet/map.
      var form = doc.querySelector('[data-testid="stForm"]:has(.metro-page-geo-bridge)');
      log("submitGeoForm form?", !!form, "payload=", payload);
      if (!form) return false;
      var input = form.querySelector("input");
      var btn = form.querySelector('button[type="submit"], button');
      log("submitGeoForm input/btn?", !!input, !!btn);
      if (!input || !btn) return false;
      try { input.focus(); } catch (e) {}
      setNativeInput(input, String(payload || ""));
      log("input value now:", input.value);
      try {
        if (typeof form.requestSubmit === "function") {
          form.requestSubmit(btn);
          log("requestSubmit ok");
          return true;
        }
      } catch (e) {
        log("requestSubmit failed", String(e));
      }
      try {
        btn.dispatchEvent(new MouseEvent("click", {
          bubbles: true,
          cancelable: true,
          view: win
        }));
        log("MouseEvent click dispatched");
        return true;
      } catch (e2) {
        log("MouseEvent failed", String(e2));
      }
      try {
        btn.click();
        log("btn.click ok");
        return true;
      } catch (e3) {
        log("btn.click failed", String(e3));
        return false;
      }
    }

    function softSync(payload) {
      // Soft form only — NEVER location.assign (Redirect Blocker / welcome race).
      try { win.localStorage.setItem("kali_welcome_v1", "1"); } catch (eLs) {}
      var ok = submitGeoForm(payload);
      log("soft form sync?", ok);
      if (!ok) {
        status("Could not sync location (form missing). Try again.");
        log("ABORT soft sync — metro page geo form not found");
      } else {
        status("Location found — updating nearest metro…");
        // Banner clears after Streamlit rerender; also drop it shortly.
        win.setTimeout(function () { status(""); }, 2500);
      }
      return ok;
    }

    function requestGeo() {
      status("Requesting location permission…");
      log("requestGeo start");
      if (!win.isSecureContext) {
        softSync("err|insecure");
        return;
      }
      if (!win.navigator || !win.navigator.geolocation) {
        softSync("err|2");
        return;
      }
      win.navigator.geolocation.getCurrentPosition(
        function (pos) {
          var lat = pos.coords.latitude;
          var lon = pos.coords.longitude;
          var acc = (pos.coords.accuracy != null) ? String(pos.coords.accuracy) : "";
          log("geo ok — soft-syncing for nearest station", lat, lon, acc);
          softSync("ok|" + lat + "|" + lon + "|" + acc);
        },
        function (err) {
          var code = (err && err.code) ? String(err.code) : "2";
          log("geo err", code, err && err.message);
          status("Location request failed — check browser permission.");
          softSync("err|" + code);
        },
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
      );
    }

    win.__metroRequestGeo = requestGeo;
    win.__metroSoftGeoSync = softSync;

    function isNearMeButton(btn) {
      if (!btn) return false;
      // Marker class lives in the same Streamlit column as the button
      var col = btn.closest('[data-testid="stColumn"], [data-testid="column"]');
      if (col && col.querySelector(".metro-near-me-btn")) return true;
      if (btn.closest && btn.closest(".metro-near-me-btn")) return true;
      var label = (btn.innerText || btn.textContent || "").replace(/\\s+/g, " ").trim();
      if (/^(loc|near me|search near me)$/i.test(label)) return true;
      if (/^(use my )?current location$/i.test(label)) return true;
      var aria = (btn.getAttribute("aria-label") || btn.getAttribute("title") || "").trim();
      if (/near me|current location|nearest metro|your location/i.test(aria)) return true;
      return false;
    }

    if (doc.__metroGeoClickHandler) {
      doc.removeEventListener("click", doc.__metroGeoClickHandler, true);
    }
    doc.__metroGeoClickHandler = function (ev) {
      var t = ev.target;
      if (!t || !t.closest) return;
      var btn = t.closest("button");
      if (!isNearMeButton(btn)) return;
      // Keep the user gesture — ask for permission immediately (no Streamlit rerun first)
      log("loc button clicked", {
        label: ((btn.innerText || btn.textContent || "") + "").replace(/\\s+/g, " ").trim(),
        href: String(win.location.href || ""),
        geoForm: !!doc.querySelector('[data-testid="stForm"]:has(.metro-page-geo-bridge)')
      });
      ev.preventDefault();
      ev.stopPropagation();
      if (ev.stopImmediatePropagation) ev.stopImmediatePropagation();
      var col = btn.closest('[data-testid="stColumn"], [data-testid="column"]');
      if (col && col.querySelector(".metro-near-me-btn.is-active")) {
        log("loc toggle off — restore full station list");
        status("");
        softSync("off");
        return;
      }
      requestGeo();
    };
    doc.addEventListener("click", doc.__metroGeoClickHandler, true);
  }
  try { install(); } catch (e) {
    try { console.error("[metro-geo] install failed", e); } catch (e2) {}
  }
})();
</script>
        """,
        height=0,
        width=0,
    )


def _inject_metro_station_pick_hook() -> None:
    """Pick a station without full page reload — fly the live map, then soft-sync.

    Station rows encode the pick in href="#metro-pick=id|lat|lon|name" because
    Streamlit's HTML sanitizer often strips data-* attributes.
    """
    components.html(
        """
<script>
(function () {
  function install() {
    var win = window.parent;
    try { if (win.top && win.top.document) win = win.top; } catch (e) {}
    var doc = win.document;
    var LOG = "[metro-pick]";

    function log() {
      try {
        var args = Array.prototype.slice.call(arguments);
        args.unshift(LOG);
        console.log.apply(console, args);
      } catch (e) {}
    }
"""
        + _METRO_NAV_BRIDGE_JS
        + """
    ensureNavBridge();

    function mapsInFrame(frame) {
      var out = [];
      try {
        var w = frame.contentWindow;
        if (!w) return out;
        Object.keys(w).forEach(function (k) {
          if (k.indexOf("map_") !== 0) return;
          var m = w[k];
          if (m && (typeof m.flyTo === "function" || typeof m.setView === "function")) {
            out.push({
              win: w,
              map: m,
              key: k,
              frame: frame,
              pinned: frame.getAttribute("data-metro-map-frame") === "1",
              area: (frame.offsetWidth || 0) * (frame.offsetHeight || 0)
            });
          }
        });
      } catch (e) {
        log("iframe access error", String(e));
      }
      return out;
    }

    function findMaps() {
      // Prefer the pinned fullscreen Folium iframe — other iframes are decoys
      var pinned = doc.querySelector("iframe[data-metro-map-frame='1']");
      var maps = [];
      if (pinned) {
        maps = mapsInFrame(pinned);
        log("pinned map frame maps:", maps.length);
      }
      if (!maps.length) {
        var frames = doc.querySelectorAll("iframe");
        log("fallback scan iframes:", frames.length);
        for (var i = 0; i < frames.length; i++) {
          maps = maps.concat(mapsInFrame(frames[i]));
        }
        maps.sort(function (a, b) {
          return (b.pinned - a.pinned) || (b.area - a.area);
        });
      }
      return maps;
    }

    function flyToStation(lat, lon, name) {
      var la = parseFloat(lat);
      var lo = parseFloat(lon);
      log("flyToStation", { lat: la, lon: lo, name: name });
      if (isNaN(la) || isNaN(lo)) {
        log("ABORT fly — lat/lon NaN");
        return false;
      }
      var maps = findMaps();
      log("maps found:", maps.length, maps.map(function (m) {
        return m.key + (m.pinned ? "(pinned)" : "") + " area=" + m.area;
      }));
      if (!maps.length) {
        log("ABORT fly — no Leaflet map in iframes");
        return false;
      }
      // Only fly the best (pinned / largest) map — flying ghosts looked like "no zoom"
      var item = maps[0];
      try {
        if (item.map.stop) try { item.map.stop(); } catch (e0) {}
        item.win.__metroLockedView = { lat: la, lon: lo, zoom: 15 };
        win.__metroRouteView = false;
        try {
          if (item.win.__metroRouteLine) {
            item.map.removeLayer(item.win.__metroRouteLine);
            item.win.__metroRouteLine = null;
          }
        } catch (eLine) {}
        // setView goes straight to zoom 15. flyTo arcs past the target,
        // so a station picked after a wide route looked zoomed in too far
        // until the arc settled.
        if (item.map.setView) {
          item.map.setView([la, lo], 15, { animate: true });
          log("called setView on", item.key, "pinned=", item.pinned);
        }
        win.setTimeout(function () {
          if (win.__metroRouteView) return;
          try {
            var z = item.map.getZoom ? item.map.getZoom() : 15;
            if (Math.abs(z - 15) > 0.4 && item.map.setView) {
              item.map.setView([la, lo], 15, { animate: false });
            }
            item.win.__metroLockedView = { lat: la, lon: lo, zoom: 15 };
            log("lock zoom held on", item.key);
          } catch (eHold) {}
        }, 700);
        try { item.map.closePopup(); } catch (e1) {}
        try {
          var L = item.win.L;
          if (L) {
            if (item.win.__metroTravelMarker) {
              item.map.removeLayer(item.win.__metroTravelMarker);
            }
            var label = String(name || "Station").replace(/</g, "");
            item.win.__metroTravelMarker = L.circleMarker([la, lo], {
              radius: 11,
              color: "#F0CD85",
              weight: 3,
              fillColor: "#C62828",
              fillOpacity: 0.95
            }).addTo(item.map);
            item.win.__metroTravelMarker.bindTooltip(label, { permanent: false });
          }
        } catch (e2) {
          log("marker error", String(e2));
        }
      } catch (e) {
        log("fly error", String(e));
        return false;
      }
      return true;
    }

    function setNativeInput(input, value) {
      var proto = win.HTMLInputElement.prototype;
      var desc = Object.getOwnPropertyDescriptor(proto, "value");
      if (desc && desc.set) desc.set.call(input, value);
      else input.value = value;
      if (input._valueTracker && input._valueTracker.setValue) {
        try { input._valueTracker.setValue(""); } catch (e) {}
        try { input._valueTracker.setValue(String(value)); } catch (e) {}
      }
      input.dispatchEvent(new Event("input", { bubbles: true }));
      input.dispatchEvent(new Event("change", { bubbles: true }));
    }

    function submitPick(payload) {
      var form = doc.querySelector('[data-testid="stForm"]:has(.metro-pick-bridge)');
      log("submitPick form?", !!form, "payload=", payload);
      if (!form) return false;
      var input = form.querySelector("input");
      var btn = form.querySelector('button[type="submit"], button');
      log("submitPick input/btn?", !!input, !!btn);
      if (!input || !btn) return false;
      try { input.focus(); } catch (e) {}
      setNativeInput(input, String(payload || ""));
      log("input value now:", input.value);
      try {
        if (typeof form.requestSubmit === "function") {
          form.requestSubmit(btn);
          log("requestSubmit ok");
          return true;
        }
      } catch (e) {
        log("requestSubmit failed", String(e));
      }
      try {
        btn.dispatchEvent(new MouseEvent("click", {
          bubbles: true,
          cancelable: true,
          view: win
        }));
        log("MouseEvent click dispatched");
        return true;
      } catch (e2) {
        log("MouseEvent failed", String(e2));
      }
      try {
        btn.click();
        log("btn.click ok");
        return true;
      } catch (e3) {
        log("btn.click failed", String(e3));
        return false;
      }
    }

    function navigatePick(id, lat, lon) {
      // LAST RESORT only — full URL sync remounts the map (glitchy).
      try {
        var u = new URL(win.location.href);
        u.searchParams.set("metro_dest", String(id));
        if (!isNaN(lat)) u.searchParams.set("metro_plat", String(lat));
        if (!isNaN(lon)) u.searchParams.set("metro_plon", String(lon));
        log("navigatePick LAST RESORT", u.search);
        return navigateTop(u.toString());
      } catch (e) {
        log("navigatePick failed", String(e));
        return false;
      }
    }

    function markRowSelected(rowOrId) {
      var rows = doc.querySelectorAll(".metro-sheet-row");
      var target = null;
      if (rowOrId && rowOrId.nodeType === 1) target = rowOrId;
      else if (rowOrId) {
        var want = String(rowOrId);
        rows.forEach(function (r) {
          if ((r.getAttribute("data-metro-dest") || "") === want) target = r;
        });
      }
      rows.forEach(function (r) {
        r.classList.remove("is-selected");
        r.setAttribute("data-selected", "0");
        r.style.border = "";
        r.style.outline = "";
        r.style.boxShadow = "";
        r.style.background = "";
      });
      if (!target) return;
      target.classList.add("is-selected");
      target.setAttribute("data-selected", "1");
      target.style.border = "2px solid #F0CD85";
      target.style.outline = "2px solid #F0CD85";
      target.style.outlineOffset = "0";
      target.style.boxShadow = "0 0 0 1px rgba(240,205,133,.45)";
      target.style.background = "#4A3038";
    }
    win.__metroMarkRowSelected = markRowSelected;

    function parsePickHref(href) {
      if (!href) return null;
      var idx = href.indexOf("#metro-pick=");
      if (idx < 0) return null;
      var raw = href.slice(idx + "#metro-pick=".length);
      try { raw = decodeURIComponent(raw); } catch (e) {}
      return raw;
    }

    function parsePayload(raw) {
      var parts = String(raw || "").split("|");
      return {
        id: parts[0] || "",
        lat: parts[1],
        lon: parts[2],
        name: parts.slice(3).join("|") || ""
      };
    }

    function readSavedOrigin() {
      var el = doc.getElementById("metro-user-origin");
      if (!el) return null;
      var lat = parseFloat(el.getAttribute("data-lat"));
      var lon = parseFloat(el.getAttribute("data-lon"));
      if (isNaN(lat) || isNaN(lon)) return null;
      return { lat: lat, lon: lon };
    }

    function hideFindRouteBox() {
      var box = doc.getElementById("metro-find-route");
      if (box) box.style.display = "none";
    }

    function drawWalkLine(latlngs) {
      var maps = findMaps();
      if (!maps.length || !latlngs || latlngs.length < 2) return false;
      var item = maps[0];
      var L = item.win.L;
      if (!L) return false;
      try {
        if (item.win.__metroRouteLine) item.map.removeLayer(item.win.__metroRouteLine);
        item.win.__metroRouteLine = L.polyline(latlngs, {
          color: "#761F35",
          weight: 5,
          opacity: 0.92
        }).addTo(item.map);
        win.__metroRouteView = true;
        item.win.__metroLockedView = null;
        if (item.map.stop) try { item.map.stop(); } catch (e0) {}
        item.map.fitBounds(item.win.__metroRouteLine.getBounds(), {
          paddingTopLeft: [48, 90],
          paddingBottomRight: [48, 280],
          maxZoom: 15,
          animate: true
        });
        return true;
      } catch (e) {
        log("draw route failed", String(e));
        return false;
      }
    }

    function submitRouteForm(olat, olon) {
      var form = doc.querySelector('[data-testid="stForm"]:has(.metro-route-bridge)');
      if (!form) return false;
      var input = form.querySelector("input");
      var btn = form.querySelector('button[type="submit"], button');
      if (!input || !btn) return false;
      var proto = win.HTMLInputElement.prototype;
      var desc = Object.getOwnPropertyDescriptor(proto, "value");
      var next = String(olat) + "|" + String(olon);
      if (input._valueTracker && input._valueTracker.setValue) {
        try { input._valueTracker.setValue(String(input.value || "")); } catch (e) {}
      }
      if (desc && desc.set) desc.set.call(input, next);
      else input.value = next;
      input.dispatchEvent(new Event("input", { bubbles: true }));
      input.dispatchEvent(new Event("change", { bubbles: true }));
      try {
        btn.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true, view: win }));
        return true;
      } catch (e2) {
        try { btn.click(); return true; } catch (e3) { return false; }
      }
    }

    function requestWalkRoute() {
      var box = doc.getElementById("metro-find-route");
      var stn = box && box.__station;
      if (!box || !stn) return;
      var sub = box.querySelector(".sub");
      var btn = box.querySelector("button.go");
      if (btn) btn.disabled = true;
      function finish(msg, ok) {
        if (sub) sub.textContent = msg || "";
        if (btn) btn.disabled = false;
        if (!ok) log("route", msg);
      }
      function straightKm(lat1, lon1, lat2, lon2) {
        var r = 6371;
        var p1 = lat1 * Math.PI / 180, p2 = lat2 * Math.PI / 180;
        var dp = (lat2 - lat1) * Math.PI / 180;
        var dl = (lon2 - lon1) * Math.PI / 180;
        var a = Math.sin(dp / 2) * Math.sin(dp / 2)
          + Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) * Math.sin(dl / 2);
        return 2 * r * Math.asin(Math.min(1, Math.sqrt(a)));
      }
      function walkText(distanceM) {
        var meters = Math.max(0, Number(distanceM) || 0);
        var dist = meters < 1000
          ? Math.round(meters) + " m"
          : (meters / 1000).toFixed(meters < 10000 ? 1 : 0) + " km";
        // Public OSRM "foot" returns driving speed (~40–80 km/h). Pace the
        // same path at 5 km/h so the minutes match a walk.
        var mins = Math.max(1, Math.round(meters / 5000 * 60));
        var timeTxt;
        if (mins >= 60) {
          var h = Math.floor(mins / 60);
          var m = mins % 60;
          timeTxt = h + " hr" + (m ? " " + m + " min" : "");
        } else {
          timeTxt = mins + " min";
        }
        return dist + " · " + timeTxt + " walk";
      }
      function go(olat, olon) {
        var originEl = doc.getElementById("metro-user-origin");
        if (originEl) {
          originEl.setAttribute("data-lat", String(olat));
          originEl.setAttribute("data-lon", String(olon));
        }
        var away = straightKm(olat, olon, stn.lat, stn.lon);
        if (sub) sub.textContent = "Finding route…";
        var url = "https://router.project-osrm.org/route/v1/foot/"
          + olon + "," + olat + ";" + stn.lon + "," + stn.lat
          + "?overview=full&geometries=geojson";
        fetch(url)
          .then(function (r) { return r.json(); })
          .then(function (data) {
            var route = data && data.routes && data.routes[0];
            var coords = route && route.geometry && route.geometry.coordinates;
            if (!route || !coords || !coords.length) {
              finish("No route found.", false);
              return;
            }
            var latlngs = coords.map(function (c) { return [c[1], c[0]]; });
            drawWalkLine(latlngs);
            finish(away > 25 ? (Math.round(away) + " km away") : walkText(route.distance), true);
            submitRouteForm(olat, olon);
          })
          .catch(function () {
            finish("Could not load a route. Try again.", false);
          });
      }
      var saved = readSavedOrigin();
      if (saved) {
        go(saved.lat, saved.lon);
        return;
      }
      if (!win.navigator || !win.navigator.geolocation) {
        finish("Turn on location to find a route.", false);
        return;
      }
      if (sub) sub.textContent = "Getting your location…";
      win.navigator.geolocation.getCurrentPosition(
        function (pos) { go(pos.coords.latitude, pos.coords.longitude); },
        function () { finish("Location is needed to find a route.", false); },
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 }
      );
    }

    function showFindRouteBox(id, lat, lon, name) {
      var box = doc.getElementById("metro-find-route");
      if (!box) {
        box = doc.createElement("div");
        box.id = "metro-find-route";
        box.setAttribute("role", "dialog");
        box.innerHTML = '<button type="button" class="x" aria-label="Close">×</button>'
          + '<div class="nm"></div>'
          + '<button type="button" class="go">Find route</button>'
          + '<div class="sub"></div>';
        box.style.cssText = [
          "position:fixed",
          "left:50%",
          "bottom:calc(min(42vh, 360px) + 22px)",
          "transform:translateX(-50%)",
          "z-index:140",
          "display:flex",
          "align-items:center",
          "gap:10px",
          "max-width:min(420px, calc(100vw - 28px))",
          "padding:8px 10px 8px 12px",
          "background:#21151D",
          "color:#F6EBDD",
          "border:1px solid rgba(216,180,119,.45)",
          "border-radius:14px",
          "box-shadow:0 12px 32px rgba(0,0,0,.4)",
          "font:13px/1.3 Inter,sans-serif"
        ].join(";");
        var nm = box.querySelector(".nm");
        nm.style.cssText = "font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:180px;";
        var go = box.querySelector("button.go");
        go.style.cssText = "border:0;border-radius:999px;padding:7px 12px;background:#761F35;color:#F8ECDD;font:600 12.5px/1 Inter,sans-serif;cursor:pointer;white-space:nowrap;";
        var sub = box.querySelector(".sub");
        sub.style.cssText = "color:#D8B477;font-size:11.5px;white-space:nowrap;";
        var x = box.querySelector("button.x");
        x.style.cssText = "border:0;background:transparent;color:#D8B477;font-size:16px;line-height:1;cursor:pointer;padding:0 2px;";
        go.addEventListener("click", function (ev) {
          ev.preventDefault();
          ev.stopPropagation();
          requestWalkRoute();
        });
        x.addEventListener("click", function (ev) {
          ev.preventDefault();
          ev.stopPropagation();
          hideFindRouteBox();
        });
        doc.body.appendChild(box);
      }
      box.__station = { id: id, lat: lat, lon: lon, name: name || "" };
      var title = box.querySelector(".nm");
      if (title) title.textContent = name || "Metro station";
      var note = box.querySelector(".sub");
      if (note) note.textContent = "";
      var goBtn = box.querySelector("button.go");
      if (goBtn) goBtn.disabled = false;
      box.style.display = "flex";
    }

    win.__metroFlyToStation = flyToStation;
    win.__metroPickStation = function (id, lat, lon, name, fromMap) {
      log("PickStation called", { id: id, lat: lat, lon: lon, name: name, fromMap: !!fromMap });
      if (!id) {
        log("ABORT — empty id");
        return;
      }
      markRowSelected(id);
      var la = parseFloat(lat);
      var lo = parseFloat(lon);
      var label = name || "";
      var flew = flyToStation(la, lo, label);
      log("fly result:", flew);
      // Short skip only — after soft form rerun, camWatch must be free to
      // re-fly the (possibly remounted) iframe to this station.
      doc.__metroSkipCamUntil = Date.now() + 700;
      var payload = [id, isNaN(la) ? "" : la, isNaN(lo) ? "" : lo, label].join("|");
      // Soft form sync — NO location.assign (full URL reload was the glitch).
      var formOk = submitPick(payload);
      log("soft form sync?", formOk);
      if (!isNaN(la) && !isNaN(lo)) showFindRouteBox(id, la, lo, label);
      else hideFindRouteBox();
      if (!formOk) {
        win.setTimeout(function () {
          log("form missing — last-resort navigate");
          navigatePick(id, la, lo);
        }, 200);
      }
    };

    function camWatch() {
      var el = doc.getElementById("metro-cam-target");
      if (!el) return;
      var seq = el.getAttribute("data-seq") || "";
      if (seq && seq === doc.__metroCamSeqSeen) return;
      var lat = parseFloat(el.getAttribute("data-lat"));
      var lon = parseFloat(el.getAttribute("data-lon"));
      var name = el.getAttribute("data-name") || "";
      if (isNaN(lat) || isNaN(lon)) return;
      doc.__metroCamSeqSeen = seq;
      if (doc.__metroSkipCamUntil && Date.now() < doc.__metroSkipCamUntil) return;
      log("camWatch fly", seq, lat, lon, name);
      flyToStation(lat, lon, name);
    }

    function onPickClick(ev) {
      var t = ev.target;
      if (!t || !t.closest) return;
      var reset = t.closest("a.metro-reset-js, #metro-reset-link");
      if (reset) {
        log("reset clicked");
        ev.preventDefault();
        ev.stopPropagation();
        hideFindRouteBox();
        submitPick("__RESET__");
        return;
      }
      if (t.closest && t.closest("#metro-find-route")) return;
      // Google Maps icon — let the browser open the external link
      var gmaps = t.closest("a.map-ext");
      if (gmaps) {
        log("google maps link", gmaps.getAttribute("href"));
        ev.stopPropagation();
        if (ev.stopImmediatePropagation) ev.stopImmediatePropagation();
        return;
      }
      var row = t.closest(".metro-sheet-row, a.metro-pick-dest");
      if (!row) return;
      log("row click target=", t.tagName, "rowClass=", row.className);

      var hrefPayload = parsePickHref(
        row.getAttribute("data-pick") || row.getAttribute("href") || ""
      );
      var parsed = hrefPayload ? parsePayload(hrefPayload) : null;
      var id = (parsed && parsed.id) || row.getAttribute("data-metro-dest") || "";
      var lat = (parsed && parsed.lat) || row.getAttribute("data-lat") || "";
      var lon = (parsed && parsed.lon) || row.getAttribute("data-lon") || "";
      var nameEl = row.querySelector(".nm");
      var name = (parsed && parsed.name)
        || (nameEl ? nameEl.textContent : "")
        || row.getAttribute("data-name")
        || "";

      log("parsed pick", { hrefPayload: hrefPayload, id: id, lat: lat, lon: lon, name: name });
      if (!id) {
        log("ABORT click — no station id on row");
        return;
      }
      ev.preventDefault();
      ev.stopPropagation();
      if (ev.stopImmediatePropagation) ev.stopImmediatePropagation();
      markRowSelected(row);
      win.__metroPickStation(id, lat, lon, name);
    }

    if (doc.__metroPickClickHandler) {
      doc.removeEventListener("click", doc.__metroPickClickHandler, true);
    }
    doc.__metroPickClickHandler = onPickClick;
    doc.addEventListener("click", onPickClick, true);
    log("click handler bound v13, rows=", doc.querySelectorAll(".metro-sheet-row").length);

    if (doc.__metroPickHooked !== 13) {
      doc.__metroPickHooked = 13;
      win.setInterval(camWatch, 500);
      log("camWatch interval started v13");
    }
  }
  try { install(); } catch (e) {
    try { console.error("[metro-pick] install failed", e); } catch (e2) {}
  }
})();
</script>
        """,
        height=0,
        width=0,
    )


def _publish_metro_cam_target(destination: Optional[Dict[str, Any]]) -> None:
    """Parent-page camera target so a preserved Leaflet iframe can flyTo."""
    if not destination or destination.get("lat") is None or destination.get("lon") is None:
        st.markdown(
            '<div id="metro-cam-target" data-seq="0" style="display:none"></div>',
            unsafe_allow_html=True,
        )
        return
    seq = int(st.session_state.get("metro_cam_seq") or 0)
    lat = float(destination["lat"])
    lon = float(destination["lon"])
    name = html.escape(str(destination.get("name") or ""), quote=True)
    sid = html.escape(str(destination.get("station_id") or ""), quote=True)
    st.markdown(
        f'<div id="metro-cam-target" data-seq="{seq}" data-lat="{lat}" '
        f'data-lon="{lon}" data-name="{name}" data-sid="{sid}" '
        f'style="display:none"></div>',
        unsafe_allow_html=True,
    )


def _inject_metro_sheet_live_search() -> None:
    """Filter station rows on every keystroke (no Enter required)."""
    components.html(
        """
<script>
(function () {
  function install() {
    var win = window.parent;
    try { if (win.top && win.top.document) win = win.top; } catch (e) {}
    var doc = win.document;
    if (doc.__metroSheetLiveSearch === 2) {
      try { doc.__metroSheetApplyFilter && doc.__metroSheetApplyFilter(); } catch (e) {}
      return;
    }
    doc.__metroSheetLiveSearch = 2;

    function searchInput() {
      var col = doc.querySelector('[data-testid="stColumn"]:has(.metro-sheet-search)');
      if (!col) return null;
      return col.querySelector("input");
    }

    function tokensOf(q) {
      return String(q || "").trim().toLowerCase().split(/\\s+/).filter(Boolean);
    }

    function apply() {
      var list = doc.getElementById("metro-sheet-list")
        || doc.querySelector(".metro-sheet-list");
      var empty = doc.getElementById("metro-sheet-empty")
        || doc.querySelector(".metro-sheet-empty");
      var foot = doc.getElementById("metro-sheet-foot")
        || doc.querySelector(".metro-sheet-foot");
      if (!list) return;
      var input = searchInput();
      var q = input ? String(input.value || "") : "";
      var tokens = tokensOf(q);
      var mode = list.getAttribute("data-mode") || "all";
      var rows = list.querySelectorAll(".metro-sheet-row");
      var shown = 0;
      rows.forEach(function (row) {
        var blob = (row.getAttribute("data-search") || "").toLowerCase();
        var isNear = row.getAttribute("data-near") === "1";
        var match;
        if (!tokens.length) {
          match = mode === "near" ? isNear : true;
        } else {
          match = tokens.every(function (t) { return blob.indexOf(t) !== -1; });
        }
        if (match) {
          row.removeAttribute("hidden");
          row.style.display = "";
          shown += 1;
        } else {
          row.setAttribute("hidden", "");
          row.style.display = "none";
        }
      });
      if (empty) {
        if (shown) {
          empty.setAttribute("hidden", "");
          empty.style.display = "none";
        } else {
          empty.removeAttribute("hidden");
          empty.style.display = "";
        }
      }
      if (foot) {
        if (shown) {
          foot.removeAttribute("hidden");
          foot.style.display = "";
          var base = (mode === "near" && !tokens.length)
            ? ("Nearest to you · " + shown + " station" + (shown === 1 ? "" : "s"))
            : (shown + " station" + (shown === 1 ? "" : "s"));
          // Keep any "Showing · Name ·" prefix from server render when present
          var cur = foot.textContent || "";
          var showing = cur.match(/^Showing · .+? · /);
          foot.textContent = showing ? (showing[0] + base) : base;
        } else {
          foot.setAttribute("hidden", "");
          foot.style.display = "none";
        }
      }
    }

    doc.__metroSheetApplyFilter = apply;

    function bind() {
      var input = searchInput();
      if (!input) return false;
      if (input.__metroLiveBound) {
        apply();
        return true;
      }
      input.__metroLiveBound = true;
      input.addEventListener("input", apply);
      input.addEventListener("keyup", apply);
      input.addEventListener("change", apply);
      apply();
      return true;
    }

    if (!bind()) {
      var tries = 0;
      var t = win.setInterval(function () {
        tries += 1;
        if (bind() || tries > 40) win.clearInterval(t);
      }, 100);
    }
    doc.addEventListener("input", function (ev) {
      var t = ev && ev.target;
      if (!t || t.tagName !== "INPUT") return;
      var col = t.closest && t.closest('[data-testid="stColumn"]');
      if (col && col.querySelector(".metro-sheet-search")) apply();
    }, true);
  }
  try { install(); } catch (e) {}
})();
</script>
        """,
        height=0,
        width=0,
    )


def _run_geolocation_bridge() -> None:
    """Fallback path if Streamlit still flags a geo request without the click hook.

    Shows an explicit Allow button so geolocation runs under a fresh user gesture.
    """
    if not st.session_state.get("metro_request_geo"):
        return
    st.session_state.metro_request_geo = False
    st.info("Browser needs one more tap to share your location.")
    components.html(
        """
<div style="font-family:Inter,sans-serif;padding:4px 0 8px;">
  <button id="metro-geo-allow"
    style="width:100%;min-height:44px;border-radius:12px;border:1px solid #B8924E;
    background:#C7A05E;color:#21151D;font-weight:700;font-size:14px;cursor:pointer;">
    Allow location access
  </button>
  <div id="metro-geo-fallback-msg" style="margin-top:6px;font-size:12px;color:#BDAEB6;"></div>
</div>
<script>
(function () {
  var btn = document.getElementById("metro-geo-allow");
  var msg = document.getElementById("metro-geo-fallback-msg");
  if (!btn) return;
  btn.addEventListener("click", function () {
    if (msg) msg.textContent = "Requesting location permission…";
    try {
      var parent = window.parent;
      if (parent && typeof parent.__metroRequestGeo === "function") {
        parent.__metroRequestGeo();
        return;
      }
    } catch (e) {}
    if (msg) msg.textContent = "Could not start location request — try the pin again.";
  });
})();
</script>
        """,
        height=72,
        width=None,
    )


def _build_folium_map(
    stations: Sequence[Dict[str, Any]],
    *,
    line_filter: str,
    geocode: Optional[Dict[str, Any]] = None,
    nearest: Optional[Sequence[Dict[str, Any]]] = None,
    destination: Optional[Dict[str, Any]] = None,
    origin: Optional[Dict[str, Any]] = None,
    route: Optional[Dict[str, Any]] = None,
) -> folium.Map:
    line_filter = _normalize_line_filter(line_filter)
    nearest = list(nearest or [])
    nearest_ids = {_sid(n) for n in nearest}
    dest_id = _sid(destination) if destination else None
    visible = [s for s in stations if _station_has_line(s, line_filter)]

    center = list(KOLKATA_CENTER)
    zoom = DEFAULT_ZOOM
    # Selected station ALWAYS owns the camera — even when a walk route exists.
    # Previously route.fit_bounds() zoomed back out after flyTo (the snap-back bug).
    held_dest = st.session_state.get("metro_destination") or destination
    focus_latlon = None
    if destination and destination.get("lat") is not None:
        focus_latlon = (float(destination["lat"]), float(destination["lon"]))
    elif held_dest and held_dest.get("lat") is not None:
        focus_latlon = (float(held_dest["lat"]), float(held_dest["lon"]))
    lock_on_destination = focus_latlon is not None
    focus_destination = lock_on_destination  # alias used by later branches
    route_ok = bool(route and route.get("ok") and route.get("geometry"))
    # Explicit "Find route" should frame the walk, not stay locked on the station dot.
    if (
        st.session_state.get("metro_show_route")
        and route_ok
        and origin
        and origin.get("lat") is not None
        and destination
        and destination.get("lat") is not None
    ):
        lock_on_destination = False
        frame_nearest = False
        focus_destination = False
    # After GPS / origin: zoom toward nearest station until a destination is picked
    frame_nearest = bool(
        origin
        and origin.get("lat") is not None
        and not route_ok
        and not lock_on_destination
    )
    frame_origin_dest = False  # keep camera on the tapped station, not the OD pair
    if lock_on_destination and focus_latlon is not None:
        center = [focus_latlon[0], focus_latlon[1]]
        # 15 keeps neighborhood context — zoom 17 sits on elevated rail and looks like "tracks only"
        zoom = 15
    elif frame_nearest and nearest:
        # Bias camera toward the closest metro station
        n0 = nearest[0]
        if n0.get("lat") is not None and n0.get("lon") is not None:
            center = [float(n0["lat"]), float(n0["lon"])]
            zoom = 15
        else:
            center = [float(origin["lat"]), float(origin["lon"])]
            zoom = 15
    elif frame_nearest:
        center = [float(origin["lat"]), float(origin["lon"])]
        zoom = 15
    elif origin and origin.get("lat") is not None:
        center = [float(origin["lat"]), float(origin["lon"])]
        zoom = 14
    elif geocode and geocode.get("ok") and geocode.get("lat") is not None:
        center = [float(geocode["lat"]), float(geocode["lon"])]
        zoom = 13

    fmap = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="OpenStreetMap",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        control_scale=True,
        prefer_canvas=False,
        zoom_control=True,
    )
    fmap.get_root().header.add_child(
        folium.Element(
            """
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="preconnect" href="https://tile.openstreetmap.org" crossorigin>
<style>
  html, body, .leaflet-container { width:100%; height:100%; margin:0; padding:0; }
  html, body { background:#dcd6cf !important; margin:0; padding:0; }
  .leaflet-container { background:#dcd6cf !important; }
  .leaflet-control-attribution {
    background:rgba(255,255,255,.86) !important; color:#444 !important; font-size:10px !important;
  }
  .metro-station-map-icon { background:transparent !important; border:none !important; }
</style>
"""
        )
    )

    all_bounds: List[List[float]] = []
    operational_bounds: List[List[float]] = []
    station_index: Dict[str, List[float]] = {}
    station_names: Dict[str, str] = {}

    for stn in visible:
        lat, lon = stn.get("lat"), stn.get("lon")
        if lat is None or lon is None:
            continue
        sid = _sid(stn)
        if not sid:
            continue
        color = _primary_marker_color(stn)
        is_near = sid in nearest_ids
        is_dest = bool(dest_id and sid == dest_id)
        radius = 11 if is_dest else (7 if is_near else 5)
        weight = 3 if is_dest else (2.5 if is_near else 1.5)
        outline = "#F0CD85" if is_dest else ("#B8860B" if is_near else color)
        folium.CircleMarker(
            location=[float(lat), float(lon)],
            radius=radius,
            color=outline,
            weight=weight,
            fill=True,
            fill_color=color,
            fill_opacity=0.95,
            tooltip=stn.get("name"),
        ).add_to(fmap)
        pt = [float(lat), float(lon)]
        all_bounds.append(pt)
        station_index[sid] = pt
        station_names[sid] = str(stn.get("name") or "")
        if _has_operational_line(stn):
            operational_bounds.append(pt)

    # User GPS — separate marker type (never a station, never auto-popup)
    if origin and origin.get("lat") is not None:
        olat, olon = float(origin["lat"]), float(origin["lon"])
        accuracy_m = origin.get("accuracy_m")
        try:
            acc_val = float(accuracy_m) if accuracy_m is not None else None
        except (TypeError, ValueError):
            acc_val = None
        if acc_val and 5 <= acc_val <= 2000:
            folium.Circle(
                location=[olat, olon],
                radius=acc_val,
                color="#53A8E8",
                weight=1,
                opacity=0.45,
                fill=True,
                fill_color="#53A8E8",
                fill_opacity=0.10,
                interactive=False,
            ).add_to(fmap)
        gps_icon = folium.DivIcon(
            html=(
                '<div class="metro-gps-marker" title="My current location" '
                'style="width:18px;height:18px;margin-left:-9px;margin-top:-9px;'
                "border-radius:50%;background:#53A8E8;border:2.5px solid #ffffff;"
                "box-shadow:0 0 0 3px rgba(83,168,232,.28),0 2px 8px rgba(0,0,0,.35);"
                'pointer-events:auto;"></div>'
            ),
            icon_size=(18, 18),
            icon_anchor=(9, 9),
            class_name="metro-gps-icon",
        )
        folium.Marker(
            location=[olat, olon],
            icon=gps_icon,
            # Hover-only tooltip — never a popup / info card
            tooltip=folium.Tooltip(
                "My current location",
                permanent=False,
                sticky=True,
            ),
        ).add_to(fmap)

    if destination and destination.get("lat") is not None:
        dest_color = _primary_marker_color(destination)
        dest_lines = destination.get("metro_lines") or [
            ln.get("line")
            for ln in (destination.get("lines") or [])
            if isinstance(ln, dict) and ln.get("line")
        ]
        dest_line_txt = " · ".join(str(x) for x in dest_lines if x) or "Metro"
        folium.Marker(
            location=[float(destination["lat"]), float(destination["lon"])],
            tooltip=folium.Tooltip(
                f"{destination.get('name') or 'Station'} · Kolkata Metro",
                permanent=False,
                sticky=True,
            ),
            icon=_metro_station_map_icon(
                str(destination.get("name") or "Metro station"),
                line_color=dest_color,
                line_label=dest_line_txt,
            ),
        ).add_to(fmap)

    if geocode and geocode.get("ok") and geocode.get("lat") is not None and not origin:
        glat, glon = float(geocode["lat"]), float(geocode["lon"])
        folium.Marker(
            location=[glat, glon],
            tooltip=geocode.get("display_name") or "Searched location",
            icon=folium.DivIcon(
                html=(
                    '<div style="width:14px;height:14px;margin-left:-7px;margin-top:-7px;'
                    "border-radius:50%;background:#2F6FED;border:2px solid #fff;"
                    'box-shadow:0 1px 4px rgba(0,0,0,.35);"></div>'
                ),
                icon_size=(14, 14),
                icon_anchor=(7, 7),
            ),
        ).add_to(fmap)

    # Route polyline — draw it, but NEVER fit_bounds over a locked station view
    if route_ok:
        geom = route["geometry"]
        coords = geom.get("coordinates") or []
        # GeoJSON is [lon, lat]
        latlngs = [[c[1], c[0]] for c in coords if isinstance(c, (list, tuple)) and len(c) >= 2]
        if latlngs:
            folium.PolyLine(
                latlngs,
                color="#761F35",
                weight=5,
                opacity=0.9,
                tooltip="Walk to station",
            ).add_to(fmap)
            if st.session_state.get("metro_show_route"):
                fmap.fit_bounds(latlngs, padding=(80, 80), max_zoom=15)

    if lock_on_destination and focus_latlon is not None:
        # Remount lands on the station. soft_land=True means the user already
        # watched flyTo on the previous iframe — just snap, don't re-animate.
        dlat, dlon = focus_latlon
        dname = json.dumps(
            (destination or held_dest or {}).get("name") or "Station"
        )
        nonce = int(st.session_state.get("metro_map_nonce") or 0)
        cam_seq = int(st.session_state.get("metro_cam_seq") or 0)
        soft = "true" if st.session_state.get("metro_soft_land") else "false"
        st.session_state.metro_soft_land = False
        fmap.get_root().html.add_child(
            folium.Element(
                f"""
<script>
(function () {{
  var TARGET = [{dlat}, {dlon}];
  var ZOOM = 15;
  var SOFT = {soft};
  var KEY = "metroLock:" + {nonce} + ":" + {cam_seq};
  window.__metroLockedView = {{ lat: TARGET[0], lon: TARGET[1], zoom: ZOOM }};
  function apply(animated) {{
    try {{
      Object.keys(window).forEach(function (k) {{
        if (k.indexOf("map_") !== 0) return;
        var m = window[k];
        if (!m) return;
        if (m.setView) {{
          m.setView(TARGET, ZOOM, {{ animate: !!(animated && !SOFT) }});
        }}
      }});
    }} catch (e) {{}}
  }}
  if (window[KEY]) {{ apply(false); return; }}
  window[KEY] = true;
  document.documentElement.setAttribute("data-metro-focus-name", {dname});
  apply(false);
  if (document.readyState === "complete") apply(!SOFT);
  else window.addEventListener("load", function () {{ apply(!SOFT); }});
  setTimeout(function () {{ apply(false); }}, 60);
  setTimeout(function () {{ apply(false); }}, 200);
  setTimeout(function () {{ apply(false); }}, 500);
}})();
</script>
"""
            )
        )
    elif frame_nearest:
        # Zoom to user + nearest metro station(s) until a destination is picked
        near_bounds: List[List[float]] = [
            [float(origin["lat"]), float(origin["lon"])]
        ]
        for n in nearest[:3]:
            if n.get("lat") is not None and n.get("lon") is not None:
                near_bounds.append([float(n["lat"]), float(n["lon"])])
        if len(near_bounds) >= 2:
            fmap.fit_bounds(near_bounds, padding=(72, 72))
        else:
            fmap.location = [float(origin["lat"]), float(origin["lon"])]
            fmap.options["zoom"] = 15
    elif geocode and geocode.get("ok") and geocode.get("lat") is not None:
        search_bounds = [[float(geocode["lat"]), float(geocode["lon"])]]
        for n in nearest[:5]:
            if n.get("lat") is not None:
                search_bounds.append([float(n["lat"]), float(n["lon"])])
        if len(search_bounds) >= 2:
            fmap.fit_bounds(search_bounds, padding=(48, 48))
    elif dest_id is None and origin is None and not lock_on_destination:
        use_bounds = operational_bounds if len(operational_bounds) >= 2 else all_bounds
        if len(use_bounds) >= 2:
            fmap.fit_bounds(use_bounds, padding=(40, 40))

    # Bridge: station CircleMarker click / popup CTA → metro_dest
    # GPS marker and accuracy Circle are intentionally excluded.
    index_json = json.dumps(station_index)
    names_json = json.dumps(station_names)
    origin_lat = float(origin["lat"]) if origin and origin.get("lat") is not None else None
    origin_lon = float(origin["lon"]) if origin and origin.get("lon") is not None else None
    fmap.get_root().html.add_child(
        folium.Element(
            f"""
<script>
(function () {{
  var INDEX = {index_json};
  var NAMES = {names_json};
  var GPS = {(json.dumps([origin_lat, origin_lon]) if origin_lat is not None else "null")};
  function selectDest(id, fromMap) {{
    if (!id) return;
    try {{
      var p = INDEX[id] || null;
      var parent = window.parent;
      if (parent && parent.__metroPickStation && p) {{
        parent.__metroPickStation(id, p[0], p[1], NAMES[id] || "", !!fromMap);
        return;
      }}
      var u = new URL(parent.location.href);
      u.searchParams.set("metro_dest", id);
      parent.location.href = u.toString();
    }} catch (e) {{}}
  }}
  function nearestId(lat, lng) {{
    // Never treat the user GPS point as a station selection
    if (GPS && Math.abs(GPS[0] - lat) + Math.abs(GPS[1] - lng) < 0.00025) return null;
    var best = null, bestD = 1e9;
    Object.keys(INDEX).forEach(function (id) {{
      var p = INDEX[id];
      var d = Math.abs(p[0] - lat) + Math.abs(p[1] - lng);
      if (d < bestD) {{ bestD = d; best = id; }}
    }});
    return (best && bestD < 0.0005) ? best : null;
  }}
  function bind() {{
    var map = null;
    Object.keys(window).forEach(function (k) {{
      if (k.indexOf("map_") === 0 && window[k] && window[k].eachLayer) map = window[k];
    }});
    if (!map) {{ setTimeout(bind, 120); return; }}
    // Close any popup that Folium/Leaflet may have opened on load
    try {{ map.closePopup(); }} catch (e) {{}}
    map.eachLayer(function (layer) {{
      if (!layer.getLatLng || !layer.on) return;
      // Station dots are CircleMarkers; skip L.Circle (accuracy ring) and pin Markers
      if (typeof layer.getRadius !== "function") return;
      if (window.L && layer instanceof L.Circle) return;
      var ll = layer.getLatLng();
      var id = nearestId(ll.lat, ll.lng);
      if (!id) return;
      try {{ layer.unbindPopup(); }} catch (ePop) {{}}
      layer.on("click", function (ev) {{
        if (ev && ev.originalEvent) {{
          try {{ if (window.L && window.L.DomEvent) window.L.DomEvent.stopPropagation(ev); }} catch (eStop) {{}}
        }}
        selectDest(id, true);
      }});
    }});
    document.addEventListener("click", function (ev) {{
      var t = ev.target;
      if (!t) return;
      // GPS marker must never trigger station selection
      if (t.closest && t.closest(".metro-gps-icon, .metro-gps-marker")) return;
      if (t.classList && t.classList.contains("metro-pick-dest")) {{
        ev.preventDefault();
        selectDest(t.getAttribute("data-metro-dest"));
      }}
    }});
  }}
  bind();
}})();
</script>
"""
        )
    )
    if frame_nearest or frame_origin_dest:
        st.session_state.metro_origin_framed = True
    return fmap


# Folium's default page pulls jQuery, Bootstrap, Font Awesome and
# Awesome Markers before Leaflet can draw. This map only uses circle
# markers and div icons, so those libraries just delay the first paint.
_UNUSED_MAP_CDN = (
    "jquery",
    "bootstrap",
    "fontawesome",
    "font-awesome",
    "awesome-markers",
    "awesome.rotate",
    "glyphicons",
)


def _lighten_map_html(html_doc: str) -> str:
    def keep(match: re.Match) -> str:
        tag = match.group(0)
        low = tag.lower()
        if any(token in low for token in _UNUSED_MAP_CDN):
            return ""
        return tag

    html_doc = re.sub(
        r"<script\b[^>]*\bsrc=[^>]*>\s*</script>",
        keep,
        html_doc,
        flags=re.I,
    )
    html_doc = re.sub(r"<link\b[^>]*>", keep, html_doc, flags=re.I)
    return html_doc


def _metro_map_signature(verified, line_filter, gps_nearest, destination, origin, route) -> str:
    """Digest of everything that feeds the Folium document. Identical inputs
    produce byte-identical HTML, so Streamlit keeps the live iframe mounted —
    same outcome as today, minus the rebuild."""
    nonce = int(st.session_state.get("metro_map_nonce") or 0)
    payload = json.dumps(
        {
            "nonce": nonce,
            "line": line_filter,
            "verified": verified,
            "nearest": gps_nearest,
            "destination": destination,
            "origin": origin,
            "route": route,
        },
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _render_map_fullscreen(fmap: folium.Map = None, *, html_doc: Optional[str] = None) -> None:
    if html_doc is None:
        html_doc = _build_map_html_doc(fmap)
    components.html(html_doc, height=1, scrolling=False)


def _build_map_html_doc(fmap: folium.Map) -> str:
    html_doc = _lighten_map_html(fmap.get_root().render())
    # Full-bleed map under the floating pill navbar (navbar z-index stays above).
    # Pin the map iframe only. Do NOT write transparent backgrounds onto the
    # parent .stApp / body — those inline styles survive navigation and break
    # every other page's chrome until a hard refresh.
    pin_script = """
<script>
(function () {
  function metroStillActive() {
    try {
      return !!window.parent.document.querySelector(".metro-page-active");
    } catch (e) {
      return false;
    }
  }
  function pinFrame() {
    if (!metroStillActive()) return false;
    var frame = window.frameElement;
    if (!frame) return;
    // Mark the LIVE fullscreen map iframe so pick/fly targets the right one
    try {
      window.parent.document
        .querySelectorAll("iframe[data-metro-map-frame='1']")
        .forEach(function (el) { el.removeAttribute("data-metro-map-frame"); });
    } catch (e) {}
    frame.setAttribute("data-metro-map-frame", "1");
    frame.style.cssText = [
      "position:fixed",
      "inset:0",
      "top:0",
      "left:0",
      "right:0",
      "bottom:0",
      "width:100vw",
      "height:100vh",
      "max-width:100vw",
      "max-height:100vh",
      "z-index:1",
      "border:0",
      "margin:0",
      "padding:0",
      "display:block",
      "border-radius:0",
      "pointer-events:auto",
      "background:#dcd6cf",
      "opacity:1",
      "transition:opacity .25s ease"
    ].join(";");
    if (frame.parentElement) {
      frame.parentElement.style.cssText =
        "margin:0;padding:0;height:0;overflow:visible;pointer-events:none;background:#dcd6cf;";
    }
    setTimeout(function () {
      try {
        Object.keys(window).forEach(function (k) {
          if (k.indexOf("map_") !== 0) return;
          var m = window[k];
          if (!m) return;
          if (m.invalidateSize) m.invalidateSize(false);
          // Re-assert station lock after layout — invalidateSize used to
          // leave the map on the city overview.
          var lock = window.__metroLockedView;
          if (lock && m.setView) {
            m.setView([lock.lat, lock.lon], lock.zoom || 15, { animate: false });
          }
        });
      } catch (e) {}
    }, 150);
    return true;
  }
  // Do not wait for window "load" — that fires only after every map tile
  // arrives, so the first visit stays blank. Pin as soon as the dock exists.
  var tries = 0;
  function tryPin() {
    if (pinFrame()) return;
    if (tries++ > 100) return;
    setTimeout(tryPin, 60);
  }
  tryPin();
  window.addEventListener("load", pinFrame);
  window.parent.addEventListener("resize", pinFrame);
})();
</script>
"""
    if "</body>" in html_doc:
        html_doc = html_doc.replace("</body>", pin_script + "</body>")
    else:
        html_doc = html_doc + pin_script
    # Nonce in HTML so Streamlit remounts when journey state changes (keep height stable — avoids jitter)
    nonce = int(st.session_state.get("metro_map_nonce") or 0)
    html_doc = f"<!-- metro-map-nonce:{nonce} -->\n" + html_doc
    return html_doc


def _line_chips_html(lines: Sequence[Any]) -> str:
    chips = []
    for ln in lines:
        if isinstance(ln, dict):
            name = ln.get("line")
            status = ln.get("status")
        else:
            name, status = ln, None
        if not name:
            continue
        color = LINE_COLORS.get(str(name), "#E5BC70")
        label = _esc(name)
        if status:
            label = f"{label} · {_esc(STATUS_LABELS.get(status, status))}"
        chips.append(
            f'<span class="metro-chip"><span class="dot" style="background:{color}"></span>{label}</span>'
        )
    return "".join(chips)


def _render_journey_panel(
    *,
    destination: Optional[Dict[str, Any]],
    origin: Optional[Dict[str, Any]],
    route: Optional[Dict[str, Any]],
    origin_error: Optional[str],
    route_error: Optional[str],
    stations: Sequence[Dict[str, Any]],
    line_filter: str = ALL_LINES,
) -> Dict[str, Any]:
    """Bottom-sheet list: search + station rows; tap name to show on map.

    Pin icon opens that station in Google Maps.
    """
    actions: Dict[str, Any] = {
        "request_geo": False,
        "near_me": False,
        "find_route": False,
        "reset_journey": False,
        "clear_destination": False,
        "set_origin_search": False,
        "pick_destination_id": None,
        "origin_query": "",
    }

    selectable = [
        s
        for s in _selectable_stations(stations)
        if _station_has_line(s, line_filter)
    ]
    dest_id = _sid(destination) if destination else None
    near_me_active = bool(st.session_state.get("metro_near_me_active"))

    search_col, near_col = st.columns([6.0, 0.5], gap="small")
    with search_col:
        st.markdown('<div class="metro-sheet-search" style="display:none" aria-hidden="true"></div>', unsafe_allow_html=True)
        query = st.text_input(
            "Search stations",
            placeholder="Search stations…",
            label_visibility="collapsed",
            key="metro_station_q",
        )
    with near_col:
        near_cls = "metro-near-me-btn is-active" if near_me_active else "metro-near-me-btn"
        # Marker for CSS :has() + geo click-hook (button is a sibling in this column)
        st.markdown(f'<div class="{near_cls}" style="display:none" aria-hidden="true"></div>', unsafe_allow_html=True)
        if st.button(
            "loc",
            use_container_width=True,
            key="metro_btn_near_me",
            help="Use your location — show nearest metro stations",
        ):
            actions["near_me"] = True
            actions["request_geo"] = True

    q = (query or "").strip().lower()
    nearby_list = list(st.session_state.get("metro_gps_nearest_list") or [])
    nearby_dist = {
        str(_sid(item) or ""): item.get("approximate_distance_km")
        for item in nearby_list
        if _sid(item)
    }
    nearby_ids = set(nearby_dist.keys())
    show_near_me = bool(
        near_me_active
        and not q
        and origin
        and origin.get("lat") is not None
        and nearby_list
    )
    waiting_geo = bool(
        near_me_active
        and not q
        and not (origin and origin.get("lat") is not None)
        and not origin_error
    )

    # Always keep the full station catalog in the DOM so typing can filter live
    # without waiting for a Streamlit Enter/blur rerun.
    hits: List[Dict[str, Any]] = []
    if not waiting_geo:
        for stn in selectable:
            sid = _sid(stn) or ""
            lines = [ln.get("line") for ln in _station_lines(stn) if ln.get("line")]
            blob = _station_search_blob(stn)
            is_near = sid in nearby_ids
            if show_near_me:
                initially_visible = is_near
            else:
                initially_visible = _station_matches_query(stn, q)
            hits.append(
                {
                    "stn": stn,
                    "sid": sid,
                    "lines": lines,
                    "blob": blob,
                    "is_near": is_near,
                    "distance_km": nearby_dist.get(sid),
                    "visible": initially_visible,
                }
            )
        if show_near_me:
            hits.sort(
                key=lambda item: (
                    0 if item["is_near"] else 1,
                    float(item["distance_km"])
                    if item.get("distance_km") is not None
                    else 9999.0,
                    str((item["stn"] or {}).get("name") or "").lower(),
                )
            )

    visible_count = sum(1 for item in hits if item.get("visible"))

    if waiting_geo:
        st.markdown(
            '<div class="metro-sheet-empty">Getting your location…</div>',
            unsafe_allow_html=True,
        )
    else:
        row_bits: List[str] = []
        for item in hits:
            stn = item["stn"]
            sid = item["sid"]
            lines = item["lines"]
            line_txt = " · ".join(str(x) for x in lines) if lines else "Metro"
            dist_km = item.get("distance_km")
            if dist_km is not None and (show_near_me or item.get("is_near")):
                meta = f"{_fmt_distance_away(dist_km)} · {line_txt}"
            else:
                meta = f"Metro: {line_txt}"
            selected = bool(dest_id and sid == dest_id)
            cls = "metro-sheet-row is-selected" if selected else "metro-sheet-row"
            near_attr = "1" if item.get("is_near") else "0"
            search_attr = html.escape(str(item.get("blob") or ""), quote=True)
            hide_attrs = (
                ""
                if item.get("visible")
                else ' hidden style="display:none"'
            )
            try:
                lat_attr = f'{float(stn.get("lat"))}'
                lon_attr = f'{float(stn.get("lon"))}'
            except (TypeError, ValueError):
                lat_attr, lon_attr = "", ""
            name_raw = str(stn.get("name") or "")
            name_attr = html.escape(name_raw, quote=True)
            sid_attr = html.escape(str(sid), quote=True)
            # Encode pick in data-pick — Streamlit often strips other data-* attrs
            pick_payload = html.escape(
                "#metro-pick="
                + quote(
                    f"{sid}|{lat_attr}|{lon_attr}|{name_raw}",
                    safe="|",
                ),
                quote=True,
            )
            if lat_attr and lon_attr:
                gmaps_q = quote(f"{lat_attr},{lon_attr}", safe=",")
                gmaps_href = html.escape(
                    f"https://www.google.com/maps/search/?api=1&query={gmaps_q}",
                    quote=True,
                )
                map_icon = (
                    f'<a class="map-ext" href="{gmaps_href}" target="_blank" '
                    f'rel="noopener noreferrer" title="Open in Google Maps" '
                    f'aria-label="Open {name_attr} in Google Maps">'
                    f'<svg viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                    f'<path fill="currentColor" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 '
                    f"7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5A2.5 2.5 0 1 1 "
                    f'12 6.5a2.5 2.5 0 0 1 0 5z"/>'
                    f"</svg></a>"
                )
            else:
                map_icon = (
                    '<span class="map-ext" aria-hidden="true" '
                    'style="opacity:.35;pointer-events:none">'
                    '<svg viewBox="0 0 24 24" fill="none">'
                    '<path fill="currentColor" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 '
                    "7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5A2.5 2.5 0 1 1 "
                    '12 6.5a2.5 2.5 0 0 1 0 5z"/>'
                    "</svg></span>"
                )
            row_bits.append(
                f'<div class="{cls}" role="button" tabindex="0"'
                f' data-pick="{pick_payload}"'
                f' data-metro-dest="{sid_attr}" data-lat="{lat_attr}" '
                f'data-lon="{lon_attr}" data-name="{name_attr}"'
                f' data-search="{search_attr}" data-near="{near_attr}"{hide_attrs}>'
                f'<div class="copy">'
                f'<div class="nm">{_esc(stn.get("name"))}</div>'
                f'<div class="meta">{_esc(meta)}</div>'
                f"</div>"
                f"{map_icon}"
                f"</div>"
            )
        mode = "near" if show_near_me else "all"
        empty_attrs = (
            ' hidden style="display:none"'
            if visible_count
            else ""
        )
        st.markdown(
            f'<div class="metro-sheet-list" data-mode="{mode}" '
            f'id="metro-sheet-list">{"".join(row_bits)}</div>'
            f'<div class="metro-sheet-empty" id="metro-sheet-empty"'
            f"{empty_attrs}>No results</div>",
            unsafe_allow_html=True,
        )
        selected_name = (destination or {}).get("name") or ""
        if show_near_me:
            foot = f"Nearest to you · {visible_count} station" + (
                "" if visible_count == 1 else "s"
            )
        else:
            foot = f"{visible_count} station" + ("" if visible_count == 1 else "s")
        if selected_name:
            foot = f"Showing · {_esc(selected_name)} · {foot}"
        if (
            destination
            and destination.get("name")
            and not (origin and origin.get("lat") is not None)
            and not (route and route.get("ok"))
        ):
            foot = f"{foot} · tap the location pin to draw your walk"
        foot_attrs = (
            ""
            if visible_count
            else ' hidden style="display:none"'
        )
        st.markdown(
            f'<div class="metro-sheet-foot" id="metro-sheet-foot"'
            f"{foot_attrs}>{foot}</div>",
            unsafe_allow_html=True,
        )
        _inject_metro_sheet_live_search()

    _inject_metro_station_pick_hook()

    if destination and destination.get("name"):
        if st.button("Clear station", use_container_width=True, key="metro_btn_clear_dest"):
            actions["clear_destination"] = True

    if origin_error:
        st.caption(_friendly_error(origin_error))
    if route_error:
        st.caption(_friendly_error(route_error))
    if route and route.get("ok"):
        dist = route.get("distance_m")
        dur = route.get("duration_s")
        dist_txt = f"{(dist / 1000):.2f} km" if dist is not None else "—"
        dur_txt = f" · ~{(dur / 60):.0f} min" if dur is not None else ""
        st.markdown(
            f'<div class="metro-route-summary"><b>Your walk</b>'
            f" · {_esc(dist_txt)}{_esc(dur_txt)}</div>",
            unsafe_allow_html=True,
        )
        steps = route.get("steps") or []
        if steps:
            with st.expander("Walking directions", expanded=False):
                step_bits = []
                for s in steps[:30]:
                    metres = f"{float(s.get('distance_m') or 0):.0f}"
                    step_bits.append(
                        f"<div>{_esc(s.get('instruction'))}"
                        f" <span style='opacity:.7'>({_esc(metres)} m)</span></div>"
                    )
                st.markdown(
                    f'<div class="metro-steps">{"".join(step_bits)}</div>',
                    unsafe_allow_html=True,
                )
                st.caption(ROUTE_ATTRIBUTION)

    return actions


def _render_dock(
    *,
    service: MetroService,
    line_filter: str,
    destination: Optional[Dict[str, Any]],
    origin: Optional[Dict[str, Any]],
    route: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    st.markdown('<div class="metro-dock-anchor" style="display:none"></div>', unsafe_allow_html=True)

    journey_actions = _render_journey_panel(
        destination=destination,
        origin=origin,
        route=route,
        origin_error=st.session_state.get("metro_origin_error"),
        route_error=st.session_state.get("metro_route_error"),
        stations=service.stations,
        line_filter=line_filter,
    )

    # Re-pin after dock widgets exist (early CSS inject often runs too soon)
    components.html(
        """
<script>
(function () {
  function pin() {
    try {
      var doc = window.parent.document;
      if (!doc.querySelector(".metro-page-active")) return;
      var anchor = doc.querySelector(".metro-dock-anchor");
      if (!anchor) return;
      var node = anchor, target = null;
      while (node) {
        if (node.getAttribute && node.getAttribute("data-testid") === "stVerticalBlock") {
          target = node; break;
        }
        node = node.parentElement;
      }
      if (!target) return;
      doc.querySelectorAll(".metro-dock-panel").forEach(function (el) {
        if (el !== target) el.classList.remove("metro-dock-panel");
      });
      target.classList.add("metro-dock-panel");
      target.setAttribute("data-metro-dock", "1");
      var vw = window.parent.innerWidth || 1200;
      var vh = window.parent.innerHeight || 800;
      var isNarrow = vw <= 720;
      var bottom = isNarrow ? 10 : 16;
      var maxH = isNarrow ? Math.min(vh * 0.48, 380) : Math.min(vh * 0.42, 360);
      var width = vw <= 500 ? "calc(100vw - 24px)" : "min(400px, calc(100vw - 48px))";
      target.style.setProperty("position", "fixed", "important");
      target.style.setProperty("left", "50%", "important");
      target.style.setProperty("right", "auto", "important");
      target.style.setProperty("bottom", "auto", "important");
      target.style.setProperty("transform", "translateX(-50%)", "important");
      target.style.setProperty("width", width, "important");
      target.style.setProperty("max-width", width, "important");
      target.style.setProperty("min-height", "0", "important");
      target.style.setProperty("max-height", maxH + "px", "important");
      target.style.setProperty("height", "auto", "important");
      target.style.setProperty("overflow", "hidden", "important");
      target.style.setProperty("top", "0px", "important");
      var natural = Math.ceil(target.getBoundingClientRect().height || 200);
      var panelH = Math.max(150, Math.min(natural, maxH));
      var top = Math.max(bottom, vh - bottom - panelH);
      target.style.setProperty("height", panelH + "px", "important");
      target.style.setProperty("top", top + "px", "important");
      target.style.setProperty("overflow-x", "hidden", "important");
      target.style.setProperty("overflow-y", "auto", "important");
      target.style.setProperty("z-index", "100", "important");
      target.style.setProperty("pointer-events", "auto", "important");
      target.style.setProperty("flex", "0 0 auto", "important");
      target.style.setProperty("background", "#21151D", "important");
      target.style.setProperty("border", "1px solid rgba(216,180,119,.22)", "important");
      target.style.setProperty("box-shadow", "0 18px 44px rgba(0,0,0,.45)", "important");
      target.style.setProperty("border-radius", "24px", "important");
      target.style.setProperty("padding", "14px 22px 10px", "important");
    } catch (e) {}
  }
  pin();
  setTimeout(pin, 50);
  setTimeout(pin, 250);
})();
</script>
        """,
        height=0,
        width=0,
    )

    return {
        **journey_actions,
        "new_filter": line_filter,
    }


def _apply_geo_origin(
    lat: float,
    lon: float,
    *,
    accuracy_m: Optional[float] = None,
    arm_near_me: bool = True,
    force: bool = False,
) -> bool:
    """Store GPS origin and optionally arm near-me autofocus.

    Returns True when session origin changed.
    """
    existing = st.session_state.get("metro_origin") or {}
    try:
        same = (
            not force
            and existing.get("source") == "geolocation"
            and existing.get("lat") is not None
            and abs(float(existing["lat"]) - float(lat)) < 1e-5
            and abs(float(existing["lon"]) - float(lon)) < 1e-5
        )
    except (TypeError, ValueError):
        same = False
    if same:
        if accuracy_m is not None:
            existing["accuracy_m"] = accuracy_m
            st.session_state.metro_origin = existing
        if arm_near_me:
            # Loc button / near-me must still zoom + route even when GPS
            # coords match a prior site-wide capture.
            st.session_state.metro_near_me_active = True
            st.session_state.metro_near_me_pending_focus = True
            st.session_state.metro_station_q = ""
            st.session_state.metro_route = None
            st.session_state.metro_route_error = None
        return False

    st.session_state.metro_origin = {
        "lat": lat,
        "lon": lon,
        "label": "My Current Location",
        "source": "geolocation",
        "accuracy_m": accuracy_m,
        "kind": "user_gps",  # never treated as a metro station
    }
    st.session_state.metro_origin_error = None
    st.session_state.metro_route = None
    st.session_state.metro_route_error = None
    st.session_state.metro_request_geo = False
    st.session_state.metro_origin_framed = False
    st.session_state.metro_soft_land = False
    st.session_state.metro_station_q = ""
    if arm_near_me:
        st.session_state.metro_near_me_active = True
        st.session_state.metro_near_me_pending_focus = True
        st.session_state.metro_near_me_seeded = True
    st.session_state.metro_map_nonce = int(st.session_state.get("metro_map_nonce") or 0) + 1
    st.session_state.metro_cam_seq = int(st.session_state.get("metro_cam_seq") or 0) + 1
    return True


def _apply_geo_error(code: str) -> None:
    code_map = {
        "1": "geo_denied",
        "2": "geo_unavailable",
        "3": "geo_timeout",
        "insecure": "geo_insecure",
    }
    st.session_state.metro_origin_error = code_map.get(str(code), "geo_failed")
    st.session_state.metro_request_geo = False


def apply_geo_payload(raw: str, *, arm_near_me: bool = True) -> bool:
    """Parse `ok|lat|lon|acc` / `err|code` payloads from the soft geo bridge."""
    text = (raw or "").strip()
    if not text:
        return False
    parts = text.split("|")
    kind = (parts[0] or "").strip().lower()
    if kind == "ok" and len(parts) >= 3:
        try:
            lat_f = float(parts[1])
            lon_f = float(parts[2])
            accuracy_m = None
            if len(parts) > 3 and parts[3] not in ("", None):
                try:
                    accuracy_m = float(parts[3])
                except (TypeError, ValueError):
                    accuracy_m = None
            return _apply_geo_origin(
                lat_f, lon_f, accuracy_m=accuracy_m, arm_near_me=arm_near_me
            )
        except (TypeError, ValueError):
            _apply_geo_error("2")
            return False
    if kind == "err":
        _apply_geo_error(parts[1] if len(parts) > 1 else "2")
    return False


def _consume_geo_form() -> bool:
    """Apply GPS from the soft geo bridge (lives in the sheet fragment).

    Returns True when the form was submitted so the caller can full-rerun
    and rebuild the map with nearest-station focus.
    """
    with st.form("metro_geo_bridge", border=False, clear_on_submit=True):
        st.markdown(
            # Unique marker — do NOT reuse site-wide .metro-geo-bridge or the
            # loc button submits the wrong (page-level) form and never updates.
            '<div class="metro-page-geo-bridge" style="display:none" aria-hidden="true"></div>',
            unsafe_allow_html=True,
        )
        payload = st.text_input(
            "metro_geo_payload",
            key="metro_form_geo_payload",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Apply geo")
    if not submitted:
        return False
    if str(payload or "").strip().lower() == "off":
        st.session_state.metro_near_me_active = False
        st.session_state.metro_near_me_pending_focus = False
        st.session_state.metro_station_q = ""
        print("[metro-geo] near-me toggled off")
        return True
    apply_geo_payload(payload or "", arm_near_me=True)
    # Widget keys keep prior typed search unless cleared again here (form run).
    st.session_state.metro_station_q = ""
    print(f"[metro-geo] soft form applied payload={payload!r}")
    return True


def _consume_route_form() -> None:
    """Store a walking route after the map 'Find route' box is used.

    The live line is drawn in the browser. This keeps it for the next map mount
    without forcing a remount (soft land).
    """
    with st.form("metro_route_bridge", border=False, clear_on_submit=True):
        st.markdown(
            '<div class="metro-route-bridge" style="display:none" aria-hidden="true"></div>',
            unsafe_allow_html=True,
        )
        payload = st.text_input(
            "metro_route_payload",
            key="metro_form_route_payload",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Apply route")
    if not submitted:
        return
    parts = str(payload or "").split("|")
    if len(parts) >= 2:
        try:
            lat_f, lon_f = float(parts[0]), float(parts[1])
            existing = st.session_state.get("metro_origin") or {}
            if existing.get("lat") is None:
                st.session_state.metro_origin = {
                    "lat": lat_f,
                    "lon": lon_f,
                    "label": "My Current Location",
                    "source": "geolocation",
                    "kind": "user_gps",
                }
        except (TypeError, ValueError):
            pass
    st.session_state.metro_show_route = True
    st.session_state.metro_route = None
    st.session_state.metro_route_error = None
    st.session_state.metro_soft_land = True
    _auto_walk_route_if_ready()


def _consume_station_pick_form(service: MetroService) -> None:
    """Apply sheet/map station picks BEFORE the Folium map is built.

    Payload formats:
      - `station_id`
      - `station_id|lat|lon|name` (preferred — works even if id lookup fails)
      - `__RESET__`
    """
    with st.form("metro_sheet_pick", border=False, clear_on_submit=True):
        st.markdown(
            '<div class="metro-pick-bridge" style="display:none" aria-hidden="true"></div>',
            unsafe_allow_html=True,
        )
        pick_sid = st.text_input(
            "metro_pick_sid",
            key="metro_form_dest_id",
            label_visibility="collapsed",
        )
        picked = st.form_submit_button("Apply station")
    if not picked:
        return
    raw = (pick_sid or "").strip()
    # Debug: visible confirmation that Python received the tap
    print(f"[metro-pick] form submitted raw={raw!r}")
    if raw == "__RESET__":
        _clear_journey()
        st.toast("Journey reset", icon="↺")
        return
    if not raw:
        print("[metro-pick] empty payload — ignored")
        return

    parts = raw.split("|")
    sid = (parts[0] or "").strip()
    lat_f = lon_f = None
    name_hint = ""
    if len(parts) >= 3:
        try:
            lat_f = float(parts[1])
            lon_f = float(parts[2])
        except (TypeError, ValueError):
            lat_f = lon_f = None
        if len(parts) >= 4:
            name_hint = "|".join(parts[3:]).strip()

    stn = _find_station(service, sid) if sid else None
    if stn is None and lat_f is not None and lon_f is not None:
        stn = _match_station_by_latlon(service.stations, lat_f, lon_f)
    if stn is not None:
        _set_destination(stn, remount_map=False)
        print(
            f"[metro-pick] destination set id={_sid(stn)} "
            f"name={stn.get('name')} lat={stn.get('lat')} lon={stn.get('lon')}"
        )
        st.toast(f"Showing {stn.get('name') or 'station'} on map", icon="📍")
        return
    # Last resort: zoom using the coordinates from the clicked row
    if lat_f is None or lon_f is None:
        print(f"[metro-pick] FAIL — no station match for sid={sid!r} and no coords")
        st.toast("Could not open that station — check console [metro-pick] logs", icon="⚠️")
        return
    st.session_state.metro_destination = {
        "station_id": sid or None,
        "name": name_hint or "Metro station",
        "station_code": None,
        "lat": lat_f,
        "lon": lon_f,
        "primary_status": None,
        "lines": [],
        "metro_lines": [],
    }
    st.session_state.metro_focus_station_id = sid or None
    st.session_state.metro_route = None
    st.session_state.metro_route_error = None
    st.session_state.metro_near_me_pending_focus = False
    st.session_state.metro_near_me_seeded = True
    st.session_state.metro_cam_seq = int(st.session_state.get("metro_cam_seq") or 0) + 1
    st.session_state.metro_soft_land = True
    st.session_state.metro_preserve_map = True
    print(f"[metro-pick] destination from coords sid={sid} lat={lat_f} lon={lon_f}")
    st.toast(f"Showing {name_hint or 'station'} on map", icon="📍")


def render_metro_page() -> None:
    _init_state()
    st.markdown(
        '<div class="metro-page-active" style="display:none" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    _inject_metro_page_css()
    _inject_geolocation_click_hook()
    _inject_metro_station_pick_hook()

    service = get_metro_service()
    _consume_query_bridge(service)
    # Soft GPS + station picks live in the sheet fragment (synthetic form clicks
    # reach Streamlit there). Full st.rerun() after geo rebuilds the map.
    _run_geolocation_bridge()

    inventory: SearchResponse = service.default_inventory()
    verified = inventory.verified_coordinate_stations

    line_filter = ALL_LINES
    st.session_state.metro_line_filter = ALL_LINES

    destination = st.session_state.get("metro_destination")
    origin = st.session_state.get("metro_origin")
    route = st.session_state.get("metro_route")

    # Nearest stations from GPS (list filter only while the location pin is on)
    gps_nearest: List[Dict[str, Any]] = []
    near_limit = 8 if st.session_state.get("metro_near_me_active") else 5
    if origin and origin.get("lat") is not None and origin.get("lon") is not None:
        try:
            gps_nearest = [
                n.to_dict()
                for n in service.nearest_stations(
                    float(origin["lat"]), float(origin["lon"]), limit=near_limit
                )
            ]
        except (TypeError, ValueError):
            gps_nearest = []

    # Near me → pick closest station, zoom to IT (not the GPS pin), draw walk route
    if (
        st.session_state.get("metro_near_me_pending_focus")
        and origin
        and origin.get("lat") is not None
        and gps_nearest
    ):
        nearest0 = gps_nearest[0]
        full = _find_station(service, str(nearest0.get("station_id") or ""))
        if full is not None:
            _set_destination(full, remount_map=True)
        else:
            st.session_state.metro_destination = {
                "station_id": nearest0.get("station_id"),
                "name": nearest0.get("name"),
                "station_code": nearest0.get("station_code"),
                "lat": nearest0.get("lat"),
                "lon": nearest0.get("lon"),
                "primary_status": nearest0.get("primary_status"),
                "lines": list(nearest0.get("lines") or []),
                "metro_lines": list(nearest0.get("metro_lines") or []),
            }
            st.session_state.metro_route = None
            st.session_state.metro_route_error = None
            st.session_state.metro_cam_seq = (
                int(st.session_state.get("metro_cam_seq") or 0) + 1
            )
            st.session_state.metro_preserve_map = False
            st.session_state.metro_map_nonce = (
                int(st.session_state.get("metro_map_nonce") or 0) + 1
            )
        st.session_state.metro_soft_land = False
        st.session_state.metro_preserve_map = False
        st.session_state.metro_near_me_pending_focus = False
        destination = st.session_state.get("metro_destination")
        route = st.session_state.get("metro_route")
        nearest_name = (destination or {}).get("name") or "nearest station"
        try:
            st.toast(f"Nearest metro: {nearest_name}", icon="📍")
        except Exception:
            pass

    st.session_state.metro_gps_nearest_hint = (
        gps_nearest[0] if gps_nearest else None
    )
    st.session_state.metro_gps_nearest_list = gps_nearest

    # Origin + destination → walk path on the map automatically
    if _auto_walk_route_if_ready():
        route = st.session_state.get("metro_route")
        destination = st.session_state.get("metro_destination")

    # Map is OUTSIDE the sheet fragment — station taps must not remount it.
    _origin_now = st.session_state.get("metro_origin") or {}
    _olat = _origin_now.get("lat")
    _olon = _origin_now.get("lon")
    st.markdown(
        (
            f'<div id="metro-user-origin" data-lat="{_olat if _olat is not None else ""}" '
            f'data-lon="{_olon if _olon is not None else ""}" style="display:none"></div>'
        ),
        unsafe_allow_html=True,
    )
    _publish_metro_cam_target(destination)
    st.session_state.metro_preserve_map = False
    _map_sig = _metro_map_signature(
        verified, line_filter, gps_nearest or None, destination, origin, route
    )
    _map_cache = st.session_state.get("metro_map_html_cache")
    if (
        isinstance(_map_cache, dict)
        and _map_cache.get("sig") == _map_sig
        and _map_cache.get("html")
    ):
        _render_map_fullscreen(html_doc=_map_cache["html"])
    else:
        fmap = _build_folium_map(
            verified,
            line_filter=line_filter,
            geocode=None,
            nearest=gps_nearest or None,
            destination=destination,
            origin=origin,
            route=route,
        )
        _map_html = _build_map_html_doc(fmap)
        st.session_state.metro_map_html_cache = {"sig": _map_sig, "html": _map_html}
        components.html(_map_html, height=1, scrolling=False)

    @st.fragment
    def _metro_sheet_fragment() -> None:
        # Form submit reruns ONLY this fragment — live map iframe stays put.
        # Loc soft-form must live here too (same path as station pick).
        if _consume_geo_form():
            st.rerun()
        _consume_route_form()
        _consume_station_pick_form(service)
        # Clear station search BEFORE its text_input widget is created.
        if st.session_state.pop("metro_clear_station_q_pending", False):
            st.session_state["metro_station_q"] = ""
        dest = st.session_state.get("metro_destination")
        org = st.session_state.get("metro_origin")
        rte = st.session_state.get("metro_route")
        if _auto_walk_route_if_ready():
            rte = st.session_state.get("metro_route")
            dest = st.session_state.get("metro_destination")
        _publish_metro_cam_target(dest)
        actions = _render_dock(
            service=service,
            line_filter=line_filter,
            destination=dest,
            origin=org,
            route=rte,
        )
        if actions.get("pick_destination_id"):
            stn = _find_station(service, str(actions["pick_destination_id"]))
            if stn is not None:
                _set_destination(stn, remount_map=False)
                st.rerun(scope="fragment")
        if actions.get("clear_destination"):
            _clear_destination_only()
            st.rerun()
        if actions.get("near_me") or actions.get("request_geo"):
            if actions.get("near_me"):
                st.session_state.metro_near_me_active = True
                st.session_state.metro_near_me_pending_focus = True
                st.session_state.metro_soft_land = False
                st.session_state.metro_preserve_map = False
                st.session_state.metro_clear_station_q_pending = True
                # st.session_state.metro_station_q = ""
            st.session_state.metro_request_geo = True
            st.session_state.metro_origin_error = None
            st.rerun()
        if actions.get("set_origin_search"):
            query = (st.session_state.get("metro_origin_q") or "").strip()
            if not query:
                st.session_state.metro_origin_error = "empty_query"
                st.rerun()
            with st.spinner("Locating origin…"):
                result = service.geocoder.search(query)
            if not result.ok:
                st.session_state.metro_origin_error = result.error or "no_results"
                st.rerun()
            if not result.in_west_bengal:
                st.session_state.metro_origin_error = "outside_west_bengal"
                st.rerun()
            st.session_state.metro_origin = {
                "lat": result.lat,
                "lon": result.lon,
                "label": (result.display_name or query).split(",")[0],
                "source": "manual",
                "kind": "manual_origin",
            }
            st.session_state.metro_origin_error = None
            st.session_state.metro_route = None
            st.session_state.metro_origin_framed = False
            st.session_state.metro_preserve_map = False
            st.session_state.metro_map_nonce += 1
            st.rerun()

    _metro_sheet_fragment()
