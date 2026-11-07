#!/usr/bin/env python3
"""
Build verified Kolkata Metro station dataset (Stage 1).

Cross-checks:
  - Official / secondary operational corridor inventories (Metro Railway Kolkata
    corridor naming via mtp.indianrailways.gov.in; station inventory cross-checked
    against Wikipedia "List of Kolkata Metro stations" as of 22 Aug 2025 snapshot,
    KMRC Green Line station list, and corridor articles).
  - OpenStreetMap coordinates via Overpass API (cached raw dump).

Does not invent coordinates. Unmatched / uncertain records are flagged.
"""

from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW_OVERPASS = DATA / "_overpass_raw.json"
OUT = DATA / "kolkata_metro_stations.json"

SOURCE_WIKI_LIST = {
    "id": "wikipedia-list-of-kolkata-metro-stations",
    "title": "List of Kolkata Metro stations",
    "url": "https://en.wikipedia.org/wiki/List_of_Kolkata_Metro_stations",
    "retrieved": "2026-11-06",
    "note": "Used for English/Bengali names, station codes, opening dates, and status tables (operational / under construction / planned). Not used as sole authority for operational status.",
}
SOURCE_MTP = {
    "id": "metro-railway-kolkata-portal",
    "title": "Metro Railway, Kolkata (Indian Railways portal)",
    "url": "https://mtp.indianrailways.gov.in/",
    "retrieved": "2026-11-06",
    "note": "Official operator portal; confirms Blue/Green/Purple/Orange corridor naming and passenger timetable corridors.",
}
SOURCE_KMRC = {
    "id": "kmrc-stations",
    "title": "Kolkata Metro Rail Corporation Ltd. — Stations",
    "url": "https://www.kmrc.in/stations.php",
    "retrieved": "2026-11-06",
    "note": "Green Line (East–West) station-to-station inventory.",
}
SOURCE_ORANGE = {
    "id": "wikipedia-orange-line-kolkata-metro",
    "title": "Orange Line (Kolkata Metro)",
    "url": "https://en.wikipedia.org/wiki/Orange_Line_(Kolkata_Metro)",
    "retrieved": "2026-11-06",
}
SOURCE_YELLOW = {
    "id": "wikipedia-yellow-line-kolkata-metro",
    "title": "Yellow Line (Kolkata Metro)",
    "url": "https://en.wikipedia.org/wiki/Yellow_Line_(Kolkata_Metro)",
    "retrieved": "2026-11-06",
}
SOURCE_OSM = {
    "id": "openstreetmap-overpass",
    "title": "OpenStreetMap via Overpass API",
    "url": "https://overpass-api.de/api/interpreter",
    "retrieved": "2026-11-06",
    "query_bbox": [22.40, 88.20, 22.75, 88.55],
    "note": "Nodes/ways with station=subway or subway=yes; entrances excluded from primary match.",
}

# Curated station master list. Coordinates intentionally omitted here — filled from OSM only.
# status values: operational | under_construction | proposed | partially_operational (line-level)
# Wikipedia opening dates cited where available; operational claim requires corridor confirmation.


def S(
    name,
    name_bn,
    code,
    lines,
    aliases=None,
    opened=None,
    notes=None,
    flags=None,
    prefer_osm=None,
    reject_osm=False,
    audit_coords_ok=False,
):
    return {
        "name": name,
        "name_bn": name_bn,
        "station_code": code,
        "lines": lines,  # list of {line, status}
        "aliases": aliases or [],
        "opened": opened,
        "notes": notes,
        "seed_flags": flags or [],
        "prefer_osm_name": prefer_osm,
        # If True, discard any OSM name hit (e.g. railway-not-metro collision).
        "reject_osm": reject_osm,
        # If True, OSM coords were manually corridor-audited; clear wiki-suspect manual hold.
        "audit_coords_ok": audit_coords_ok,
    }


# Line-level status records
OP = "operational"
UC = "under_construction"
PR = "proposed"

STATIONS = [
    # ---------- BLUE (North–South) — operational ----------
    S("Kavi Subhash", "কবি সুভাষ", "KKSO",
      [{"line": "Blue", "status": OP}, {"line": "Orange", "status": OP}],
      aliases=["New Garia"], opened="2010-10-07",
      notes="Interchange Blue/Orange. Orange opened 2024-03-06 per corridor sources."),
    S("Shahid Khudiram", "শহীদ ক্ষুদিরাম", "KSKD",
      [{"line": "Blue", "status": OP}],
      aliases=["Briji", "Dhalai Bridge"], opened="2010-10-07"),
    S("Kavi Nazrul", "কবি নজরুল", "KKNZ",
      [{"line": "Blue", "status": OP}],
      aliases=["Garia Bazar"], opened="2009-08-22",
      flags=["wikipedia_list_coordinates_rejected"],
      audit_coords_ok=True,
      notes=(
          "Audit 2026-11-06: Wikipedia list WGS (≈22.778°N, 88.634°E) is ~44 km off corridor; "
          "rejected. OSM node 5421533465 (network=Kolkata Metro) sits between Shahid Khudiram and "
          "Gitanjali on Blue Line (~1.2 km neighbor spacing) and is retained."
      )),
    S("Gitanjali", "গীতাঞ্জলি", "KGTN",
      [{"line": "Blue", "status": OP}],
      aliases=["Naktala"], opened="2009-08-22",
      flags=["wikipedia_list_coordinates_rejected"],
      audit_coords_ok=True,
      notes=(
          "Audit 2026-11-06: Wikipedia list WGS (≈22.783°N, 88.617°E) is ~43 km off corridor; "
          "rejected. OSM way 535333554 (network=Kolkata Metro) sits between Kavi Nazrul and "
          "Masterda Surya Sen on Blue Line and is retained."
      )),
    S("Masterda Surya Sen", "মাস্টারদা সূর্য সেন", "KMSN",
      [{"line": "Blue", "status": OP}],
      aliases=["Bansdroni"], opened="2009-08-22"),
    S("Netaji", "নেতাজি", "KNTJ",
      [{"line": "Blue", "status": OP}],
      aliases=["Kudghat"], opened="2009-08-22"),
    S("Mahanayak Uttam Kumar", "মহানায়ক উত্তম কুমার", "KMUK",
      [{"line": "Blue", "status": OP}],
      aliases=["Tollygunge"], opened="1986-04-29"),
    S("Rabindra Sarobar", "রবীন্দ্র সরোবর", "KRSB",
      [{"line": "Blue", "status": OP}],
      aliases=["Charu Market", "Dhakuria"], opened="1986-04-29"),
    S("Kalighat", "কালীঘাট", "KKHG",
      [{"line": "Blue", "status": OP}],
      aliases=["Rashbehari"], opened="1986-04-29"),
    S("Jatin Das Park", "যতীন দাস পার্ক", "KJPK",
      [{"line": "Blue", "status": OP}],
      aliases=["Hazra"], opened="1986-04-29"),
    S("Netaji Bhavan", "নেতাজি ভবন", "KNBN",
      [{"line": "Blue", "status": OP}],
      aliases=["Bhawanipore"], opened="1984-10-24"),
    S("Rabindra Sadan", "রবীন্দ্র সদন", "KRSD",
      [{"line": "Blue", "status": OP}],
      aliases=["Exide"], opened="1984-10-24"),
    S("Maidan", "ময়দান", "KMDI",
      [{"line": "Blue", "status": OP}], opened="1984-10-24"),
    S("Park Street", "পার্ক স্ট্রীট", "KPSK",
      [{"line": "Blue", "status": OP},
       {"line": "Purple", "status": UC, "notes": "Purple Line northern extension; not an independent new station identity"}],
      aliases=["Mother Teresa"], opened="1984-10-24"),
    S("Esplanade", "এসপ্ল্যানেড", "KESP",
      [{"line": "Blue", "status": OP},
       {"line": "Green", "status": OP},
       {"line": "Purple", "status": UC, "notes": "Purple Line northern extension interchange"}],
      aliases=["Dharmatala"], opened="1984-10-24",
      prefer_osm="Esplanade (Line 1)"),
    S("Chandni Chowk", "চাঁদনি চক", "KCWC",
      [{"line": "Blue", "status": OP}], opened="1995-02-15"),
    S("Central", "সেন্ট্রাল", "KCEN",
      [{"line": "Blue", "status": OP}], opened="1995-02-15"),
    S("Mahatma Gandhi Road", "মহাত্মা গান্ধী রোড", "KMHR",
      [{"line": "Blue", "status": OP}],
      aliases=["Mahajati Sadan"], opened="1995-09-27"),
    S("Girish Park", "গিরীশ পার্ক", "KGPK",
      [{"line": "Blue", "status": OP}],
      aliases=["Jorasanko"], opened="1995-02-15"),
    S("Shobhabazar Sutanuti", "শোভাবাজার সুতানুটি", "KSHO",
      [{"line": "Blue", "status": OP}],
      aliases=["Hatkhola"], opened="1995-02-15"),
    S("Shyambazar", "শ্যামবাজার", "KSHY",
      [{"line": "Blue", "status": OP}], opened="1995-02-15"),
    S("Belgachhia", "বেলগাছিয়া", "KBEL",
      [{"line": "Blue", "status": OP}],
      aliases=["Belgachia"], opened="1984-11-12", prefer_osm="Belgachia"),
    S("Dum Dum", "দমদম", "KDMI",
      [{"line": "Blue", "status": OP}], opened="1984-11-12"),
    S("Noapara", "নোয়াপাড়া", "KNAP",
      [{"line": "Blue", "status": OP}, {"line": "Yellow", "status": OP}],
      aliases=["Maa Sarada"], opened="2013-07-10",
      notes="Yellow Line interchange opened 2025-08-22."),
    S("Baranagar", "বরাহনগর", "KBAR",
      [{"line": "Blue", "status": OP}], opened="2021-02-22"),
    S("Dakshineswar", "দক্ষিণেশ্বর", "KDSW",
      [{"line": "Blue", "status": OP}],
      aliases=["Dakshineshwar", "Sri Ramakrishna"], opened="2021-02-22",
      prefer_osm="Dakshineshwar"),

    # ---------- GREEN (East–West) — operational ----------
    S("Salt Lake Sector-V", "সল্টলেক সেক্টর V", "SVSA",
      [{"line": "Green", "status": OP}],
      aliases=["Salt Lake Sector V", "Sector V"], opened="2020-02-13",
      prefer_osm="Salt Lake Sector V"),
    S("Karunamoyee", "করুণাময়ী", "KESA",
      [{"line": "Green", "status": OP}], opened="2020-02-13"),
    S("Central Park", "সেন্ট্রাল পার্ক", "CPSA",
      [{"line": "Green", "status": OP}], opened="2020-02-13"),
    S("City Center", "সিটি সেন্টার", "CCSC",
      [{"line": "Green", "status": OP}],
      aliases=["City Centre"], opened="2020-02-13", prefer_osm="City Centre"),
    S("Bengal Chemical", "বেঙ্গল কেমিক্যাল", "BCSD",
      [{"line": "Green", "status": OP}],
      aliases=["Mani Square"], opened="2020-02-13"),
    S("Salt Lake Stadium", "সল্টলেক স্টেডিয়াম", "SSSA",
      [{"line": "Green", "status": OP}], opened="2020-02-13"),
    S("Phoolbagan", "ফুলবাগান", "PBGB",
      [{"line": "Green", "status": OP}], opened="2020-10-04"),
    S("Sealdah", "শিয়ালদহ", "SDHM",
      [{"line": "Green", "status": OP}], opened="2022-07-11"),
    S("Mahakaran", "মহাকরণ", "MKNA",
      [{"line": "Green", "status": OP}], opened="2024-03-06"),
    S("Howrah", "হাওড়া", "HWHM",
      [{"line": "Green", "status": OP}], opened="2024-03-06"),
    S("Howrah Maidan", "হাওড়া ময়দান", "HWMM",
      [{"line": "Green", "status": OP}], opened="2024-03-06"),

    # ---------- PURPLE — operational Majerhat–Joka ----------
    S("Joka", "জোকা", "KJKA",
      [{"line": "Purple", "status": OP}], opened="2022-12-30"),
    S("Thakurpukur", "ঠাকুরপুকুর", "KTKP",
      [{"line": "Purple", "status": OP}], opened="2022-12-30"),
    S("Behala Sakherbazar", "সখেরবাজার", "KSKB",
      [{"line": "Purple", "status": OP}],
      aliases=["Sakher Bazar", "Silpara", "Behala Sakher Bazar"], opened="2022-12-30",
      prefer_osm="Sakher Bazar"),
    S("Behala Chowrasta", "বেহালা চৌরাস্তা", "KBCR",
      [{"line": "Purple", "status": OP}], opened="2022-12-30"),
    S("Behala Bazar", "বেহালা বাজার", "KBBR",
      [{"line": "Purple", "status": OP}], opened="2022-12-30"),
    S("Taratala", "তারাতলা", "KTRT",
      [{"line": "Purple", "status": OP}],
      aliases=["Pathakpara"], opened="2022-12-30"),
    S("Majerhat", "মাঝেরহাট", "KMJH",
      [{"line": "Purple", "status": OP}],
      aliases=["Majherhat"], opened="2024-03-06"),

    # ---------- ORANGE — operational Kavi Subhash–Beleghata ----------
    S("Satyajit Ray", "সত্যজিৎ রায়", "KSJR",
      [{"line": "Orange", "status": OP}],
      aliases=["Chak Garia", "Ajoy Nagar"], opened="2024-03-06"),
    S("Jyotirindra Nandi", "জ্যোতিরিন্দ্র নন্দী", "KJNN",
      [{"line": "Orange", "status": OP}],
      aliases=["Singhbari"], opened="2024-03-06"),
    S("Kavi Sukanta", "কবি সুকান্ত", "KKSK",
      [{"line": "Orange", "status": OP}],
      aliases=["Avishikta More"], opened="2024-03-06"),
    S("Hemanta Mukhopadhyay", "হেমন্ত মুখোপাধ্যায়", "KHMD",
      [{"line": "Orange", "status": OP}],
      aliases=["Ruby"], opened="2024-03-06"),
    S("VIP Bazar", "ভিআইপি বাজার", "KVIB",
      [{"line": "Orange", "status": OP}], opened="2025-08-22"),
    S("Ritwik Ghatak", "ঋত্বিক ঘটক", "KRWG",
      [{"line": "Orange", "status": OP}],
      aliases=["Ritwick Ghatak", "Bantala Road"], opened="2025-08-22"),
    S("Barun Sengupta", "বরুণ সেনগুপ্ত", "KBST",
      [{"line": "Orange", "status": OP}],
      aliases=["Science City", "Dhapa", "Mathpukur", "Metropolitan"], opened="2025-08-22",
      flags=["wikipedia_list_coordinates_rejected"],
      audit_coords_ok=True,
      notes=(
          "Audit 2026-11-06: Wikipedia list longitude ≈88.339°E is ~6 km west of EM Bypass; "
          "rejected. OSM node 13088485701 (network=Kolkata Metro) lies between Ritwik Ghatak and "
          "Beleghata on Orange Line (~0.9–1.2 km neighbor spacing) and is retained."
      )),
    S("Beleghata", "বেলেঘাটা", "KBGA",
      [{"line": "Orange", "status": OP}],
      aliases=["Tangra"], opened="2025-08-22"),

    # ---------- YELLOW — operational Noapara–Jai Hind ----------
    S("Dum Dum Cantonment", "দমদম ক্যান্টনমেন্ট", "KDCM",
      [{"line": "Yellow", "status": OP}], opened="2025-08-22"),
    S("Jessore Road", "যশোহর রোড", "KJRO",
      [{"line": "Yellow", "status": OP}], opened="2025-08-22"),
    S("Jai Hind", "জয় হিন্দ", "KJHD",
      [{"line": "Yellow", "status": OP},
       {"line": "Orange", "status": UC, "notes": "Orange Line airport extension not yet operational"}],
      aliases=["Biman Bandar", "Airport"], opened="2025-08-22"),

    # ---------- PURPLE under construction / proposed (unique new stations) ----------
    S("Mominpur", "মোমিনপুর", None,
      [{"line": "Purple", "status": UC}],
      aliases=["Mominpore"],
      flags=["coords_unverified_pending_osm"],
      notes="Purple northern extension; listed under construction / works in progress in corridor summaries."),
    S("Khidirpur", "খিদিরপুর", None,
      [{"line": "Purple", "status": UC}],
      aliases=["Kidderpore"],
      flags=["coords_unverified_pending_osm"]),
    S("Victoria", "ভিক্টোরিয়া", None,
      [{"line": "Purple", "status": UC}],
      flags=["coords_unverified_pending_osm", "name_may_collide_with_landmark"]),
    S("Eden Gardens", "ইডেন গার্ডেনস", None,
      [{"line": "Purple", "status": PR}],
      aliases=["Babughat"],
      flags=["status_approved_or_proposed", "coords_unverified_pending_osm"],
      notes="Wikipedia list marks Approved; not claimed operational."),
    S("IIM Calcutta", "আই আই এম জোকা", None,
      [{"line": "Purple", "status": PR}],
      aliases=["IIM Joka"],
      flags=["tender_floated", "coords_unverified_pending_osm"],
      notes="Distinct from operational Joka; do not reuse Joka OSM coordinates."),
    S("Diamond Park", "ডায়মন্ড পার্ক", None,
      [{"line": "Purple", "status": PR}],
      flags=["land_acquisition", "coords_unverified_pending_osm"],
      notes="Purple branch; land acquisition reported ongoing."),

    # ---------- YELLOW under construction / proposed ----------
    S("Birati", "বিরাটি", None,
      [{"line": "Yellow", "status": UC}],
      flags=["coords_unverified_pending_osm"]),
    S("Michael Nagar", "মাইকেল নগর", None,
      [{"line": "Yellow", "status": UC}],
      flags=["coords_unverified_pending_osm"]),
    S("New Barrackpur", "নিউ ব্যারাকপুর", None,
      [{"line": "Yellow", "status": PR}],
      aliases=["New Barrackpore", "Bidhanpally", "Netaji Nagar"],
      flags=["coords_unverified_pending_osm", "yellow_alignment_name_may_change"],
      notes=(
          "Audit 2026-11-06: retained as proposed Yellow station name from corridor lists; "
          "newer Yellow alignment articles also cite Bidhanpally / possible Netaji Nagar rename "
          "near New Barrackpore — identity unresolved; coordinates kept null."
      )),
    S("Madhyamgram", "মধ্যমগ্রাম", None,
      [{"line": "Yellow", "status": PR}],
      flags=["coords_unverified_pending_osm"]),
    S("Hridaypur", "হৃদয়পুর", None,
      [{"line": "Yellow", "status": PR}],
      flags=["coords_unverified_pending_osm"]),
    S("Barasat", "বারাসাত", None,
      [{"line": "Yellow", "status": PR}],
      flags=["coords_unverified_pending_osm", "osm_hit_rejected_railway_not_metro"],
      reject_osm=True,
      notes=(
          "Audit 2026-11-06: OSM way 535333476 is named Barasat with station=subway but "
          "network is empty and location aligns with Barasat Junction railway precinct — "
          "NOT accepted as Yellow Line metro coordinates. Proposed Yellow terminus remains; "
          "lat/lon kept null."
      )),

    # ---------- ORANGE under construction (Beleghata → Airport) ----------
    S("Gour Kishore Ghosh", "গৌর কিশোর ঘোষ", "KGKG",
      [{"line": "Orange", "status": UC}],
      aliases=["Sukant Nagar", "Chingrighata"],
      flags=["coords_unverified_pending_osm"]),
    S("Nalban", "নলবন", "KNLN",
      [{"line": "Orange", "status": UC}],
      aliases=["Nicco Park", "Nalban Metro Station"],
      prefer_osm="Nalban Metro Station"),
    S("IT Centre", "আই টি সেন্টার", "KITC",
      [{"line": "Orange", "status": UC}],
      aliases=["IT Center", "Sector-V CM Block", "Salt Lake Sector-V Orange"],
      flags=["coords_unverified_pending_osm", "near_green_sector_v_interchange"],
      notes=(
          "Audit 2026-11-06: Orange Line UC station near Green Salt Lake Sector-V interchange. "
          "Distinct from Green City Center / Sector-V. Metro Railway reported Beleghata–IT Centre "
          "trial runs (Oct 2026) but station is NOT claimed operational. No exact OSM metro node; "
          "coordinates kept null (no fuzzy match)."
      )),
    S("Nabadiganta", "নবদিগন্ত", "KNBG",
      [{"line": "Orange", "status": UC}],
      aliases=["Technopolis"]),
    S("Nazrul Tirtha", "নজরুল তীর্থ", "KNLT",
      [{"line": "Orange", "status": UC}]),
    S("Swapnabhor", "স্বপ্নভোর", "KSPB",
      [{"line": "Orange", "status": UC}],
      aliases=["Axis Mall", "Swapno Bhor"],
      flags=["coords_unverified_pending_osm"]),
    S("Biswa Bangla Convention Centre", "বিশ্ব বাংলা কনভেনশন সেন্টার", "KBCC",
      [{"line": "Orange", "status": UC}]),
    S("Shiksha Tirtha", "শিক্ষা তীর্থ", "KSST",
      [{"line": "Orange", "status": UC}],
      aliases=["Siksha Tirtha", "Fintech Hub"],
      prefer_osm="Siksha Tirtha"),
    S("Mother's Wax Museum", "মাদার্স ওয়াক্স মিউজিয়াম", "KMWM",
      [{"line": "Orange", "status": UC}],
      aliases=["Mothers Wax Museum"]),
    S("Eco Park", "ইকো পার্ক", "KECP",
      [{"line": "Orange", "status": UC}]),
    S("Mangaldeep", "মঙ্গলদীপ", "KMDP",
      [{"line": "Orange", "status": UC}],
      flags=["coords_unverified_pending_osm"]),
    S("City Centre-2", "সিটি সেন্টার ২", "KCCT",
      [{"line": "Orange", "status": UC}],
      aliases=["City Centre 2", "City Center-2", "City Centre-II"],
      flags=["coords_unverified_pending_osm", "do_not_match_green_city_centre"],
      notes=(
          "Audit 2026-11-06: Orange New Town UC station. Must not reuse Green Line City Center "
          "OSM coordinates. No distinct OSM metro node found; lat/lon kept null."
      )),
    S("Chinar Park", "চিনার পার্ক", "KCNP",
      [{"line": "Orange", "status": UC}],
      flags=["coords_unverified_pending_osm"],
      notes=(
          "Audit 2026-11-06: Orange Line UC station on New Town–VIP Road approach. "
          "Name/status confirmed against Orange corridor lists; no OSM metro node; coords null."
      )),
    S("VIP Road", "ভি আই পি রোড", "KVIR",
      [{"line": "Orange", "status": UC}],
      aliases=["Haldirams Signal", "Haldiram"],
      flags=["coords_unverified_pending_osm", "name_ambiguous", "planned_green_teghoria_interchange"],
      notes=(
          "Audit 2026-11-06: Orange UC station near Haldiram/VIP Road; distinct from operational "
          "VIP Bazar. Planned interchange with Green Teghoria (separate station record). "
          "No OSM metro node; coordinates kept null."
      )),

    # ---------- GREEN proposed extensions (not claimed operational) ----------
    S("Krishnapur", "কৃষ্ণপুর", None,
      [{"line": "Green", "status": PR}],
      flags=["coords_unverified_pending_osm", "status_approved_or_proposed"],
      notes="Audit 2026-11-06: Green Sector-V→Teghoria approved extension; land notices reported; coords null."),
    S("Kestopur", "কেষ্টপুর", None,
      [{"line": "Green", "status": PR}],
      flags=["coords_unverified_pending_osm", "status_approved_or_proposed"],
      notes="Audit 2026-11-06: Green Sector-V→Teghoria approved extension; coords null."),
    S("Baguiati", "বাগুইআটি", None,
      [{"line": "Green", "status": PR}],
      flags=["coords_unverified_pending_osm", "status_approved_or_proposed"],
      notes="Audit 2026-11-06: Green Sector-V→Teghoria approved extension; coords null."),
    S("Raghunathpur", "রঘুনাথপুর", None,
      [{"line": "Green", "status": PR}],
      flags=["coords_unverified_pending_osm", "status_approved_or_proposed"],
      notes="Audit 2026-11-06: Green Sector-V→Teghoria approved extension; coords null."),
    S("Teghoria", "তেঘরিয়া", None,
      [{"line": "Green", "status": PR}],
      aliases=["Haldiram", "Haldirams"],
      flags=["coords_unverified_pending_osm", "status_approved_or_proposed", "planned_orange_vip_road_interchange"],
      notes=(
          "Audit 2026-11-06: Green approved eastern terminus (Sector-V→Teghoria). Planned "
          "interchange with Orange VIP Road (separate record). Land acquisition underway; "
          "not under construction for ops purposes; coords null."
      )),
]


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"\bmetro\b", "", s)
    s = re.sub(r"\bstation\b", "", s)
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def load_osm_stations():
    raw = json.loads(RAW_OVERPASS.read_text(encoding="utf-8"))
    out = []
    for el in raw.get("elements", []):
        if el.get("type") not in ("node", "way"):
            continue
        tags = el.get("tags") or {}
        name = tags.get("name:en") or tags.get("name")
        if not name:
            continue
        # Skip entrances / gates
        if tags.get("railway") == "subway_entrance":
            continue
        if re.search(r"\bgate\b", name, re.I):
            continue
        if tags.get("station") != "subway" and tags.get("subway") != "yes":
            # allow explicit Kolkata Metro network tags
            net = (tags.get("network") or "") + (tags.get("operator") or "")
            if "metro" not in net.lower() and "metro" not in name.lower():
                continue
        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        if lat is None or lon is None:
            continue
        out.append({
            "name": name,
            "lat": float(lat),
            "lon": float(lon),
            "osm_type": el["type"],
            "osm_id": el["id"],
            "network": tags.get("network"),
            "operator": tags.get("operator"),
        })
    return out


def _name_compatible(osm_norm: str, station_norm: str) -> bool:
    """Exact match only for primary scoring — avoid City Centre ↔ City Centre-2."""
    if not osm_norm or not station_norm:
        return False
    return osm_norm == station_norm


def match_osm(station, osm_list):
    candidates = []
    prefer = station.get("prefer_osm_name")
    names = [station["name"]] + station.get("aliases", [])
    if prefer:
        names = [prefer] + names
    norms = [norm(n) for n in names if n]
    for o in osm_list:
        on = norm(o["name"])
        if any(_name_compatible(on, n) for n in norms):
            score = 100 if prefer and o["name"] == prefer else 80
            if on == norm(station["name"]):
                score = max(score, 90)
            candidates.append((score, o))
    # No fuzzy/substring matching: false positives (IT Centre→City Centre, IIM Joka→Joka)
    # are worse than leaving coordinates null for Stage 1.
    if not candidates:
        return None, "unmatched"
    candidates.sort(key=lambda x: (-x[0], x[1]["name"]))
    best_score, best = candidates[0]
    # Prefer Kolkata Metro network when available
    metroish = [c for c in candidates if c[1].get("network") and "metro" in (c[1].get("network") or "").lower()]
    if metroish:
        metroish.sort(key=lambda x: (-x[0], x[1]["name"]))
        best_score, best = metroish[0]
    kind = "matched" if best_score >= 80 else "fuzzy"
    return best, kind


def overall_status(lines):
    statuses = {ln["status"] for ln in lines}
    if statuses == {OP}:
        return OP
    if OP in statuses and (UC in statuses or PR in statuses):
        return "partially_operational"
    if UC in statuses and PR not in statuses:
        return UC
    if UC in statuses and PR in statuses:
        return UC
    return PR


def build():
    if not RAW_OVERPASS.exists():
        raise SystemExit(f"Missing Overpass cache: {RAW_OVERPASS}")
    osm = load_osm_stations()
    records = []
    used_ids = set()

    for st in STATIONS:
        base = slugify(st["name"])
        sid = f"km-{base}"
        if sid in used_ids:
            raise SystemExit(f"Duplicate id seed: {sid}")
        used_ids.add(sid)

        osm_hit, match_kind = match_osm(st, osm)
        if st.get("reject_osm"):
            osm_hit, match_kind = None, "rejected"
        flags = list(st.get("seed_flags") or [])
        sources = [SOURCE_WIKI_LIST, SOURCE_MTP]
        if any(ln["line"] == "Green" for ln in st["lines"]):
            sources.append(SOURCE_KMRC)
        if any(ln["line"] == "Orange" for ln in st["lines"]):
            sources.append(SOURCE_ORANGE)
        if any(ln["line"] == "Yellow" for ln in st["lines"]):
            sources.append(SOURCE_YELLOW)

        lat = lon = None
        osm_ref = None
        coord_confidence = "missing"
        coord_source = None

        if osm_hit:
            sources.append(SOURCE_OSM)
            lat, lon = osm_hit["lat"], osm_hit["lon"]
            osm_ref = {
                "type": osm_hit["osm_type"],
                "id": osm_hit["osm_id"],
                "name": osm_hit["name"],
                "url": f"https://www.openstreetmap.org/{osm_hit['osm_type']}/{osm_hit['osm_id']}",
            }
            coord_source = "openstreetmap"
            if match_kind == "matched":
                coord_confidence = "high"
            else:
                coord_confidence = "medium"
                flags.append("fuzzy_osm_name_match")
            # Drop pending flag if we got coords
            flags = [f for f in flags if f != "coords_unverified_pending_osm"]
            if "osm_hit_may_be_railway_not_metro" in flags or "osm_hit_rejected_railway_not_metro" in flags:
                # Should not keep coords for railway collisions
                lat = lon = None
                osm_ref = None
                coord_source = None
                coord_confidence = "missing"
                match_kind = "rejected"
                sources = [s for s in sources if s.get("id") != SOURCE_OSM["id"]]
                flags.append("needs_manual_verification")
        else:
            if match_kind != "rejected":
                flags.append("osm_unmatched")
            flags.append("needs_manual_verification")

        # Wikipedia list bad WGS was rejected; OSM corridor-audited coords stay.
        if st.get("audit_coords_ok") and lat is not None and match_kind == "matched":
            flags = [f for f in flags if f not in {
                "needs_manual_verification",
                "wikipedia_coordinates_suspect",
            }]
            flags.append("coords_corridor_audited")
            coord_confidence = "high"

        # Deduplicate flags
        flags = sorted(set(flags))

        primary_status = overall_status(st["lines"])
        needs_manual = (
            "needs_manual_verification" in flags
            or coord_confidence in ("missing", "low")
            or match_kind not in ("matched", "rejected")
        )
        # rejected-with-null still needs manual for coords; keep needs_manual True
        if match_kind == "rejected" and lat is None:
            needs_manual = True
            if "needs_manual_verification" not in flags:
                flags.append("needs_manual_verification")
                flags = sorted(set(flags))
        if st.get("audit_coords_ok") and lat is not None and match_kind == "matched":
            needs_manual = False
            flags = sorted(set(f for f in flags if f != "needs_manual_verification"))

        records.append({
            "id": sid,
            "name": st["name"],
            "name_bn": st["name_bn"],
            "station_code": st["station_code"],
            "aliases": st["aliases"],
            "lines": st["lines"],
            "primary_status": primary_status,
            "opened": st.get("opened"),
            "lat": lat,
            "lon": lon,
            "coordinate_source": coord_source,
            "coordinate_confidence": coord_confidence,
            "osm": osm_ref,
            "notes": st.get("notes"),
            "sources": sources,
            "verification": {
                "osm_name_match": match_kind,
                "needs_manual_verification": needs_manual,
                "flags": flags,
                "audit_coords_ok": bool(st.get("audit_coords_ok")),
            },
        })

    dataset = {
        "meta": {
            "title": "Kolkata Metro stations — Stage 1 verified inventory",
            "version": "0.1.1-stage1-audit",
            "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "crs": "EPSG:4326",
            "scope": [
                "Blue", "Green", "Purple", "Orange", "Yellow",
            ],
            "status_vocabulary": [
                "operational",
                "partially_operational",
                "under_construction",
                "proposed",
            ],
            "methodology": [
                "Station names, codes, and corridor assignments seeded from Metro Railway Kolkata corridor naming and cross-checked against Wikipedia list, KMRC Green Line pages, and Yellow/Orange corridor articles.",
                "Operational status is NOT assumed for entire corridors; under-construction and proposed segments are listed separately.",
                "Coordinates taken only from OpenStreetMap Overpass exact name matches; no invented coordinates and no fuzzy forcing.",
                "Interchange stations are stored once with per-line status entries.",
                "2026-11-06 data-quality audit: Wikipedia WGS outliers rejected where OSM metro network nodes sit on corridor; railway-not-metro OSM hits nulled; unresolved UC/proposed coords remain null with flags.",
                "Records lacking a reliable OSM metro match or with conflicting evidence are flagged needs_manual_verification.",
            ],
            "completeness_statement": (
                "This Stage 1 dataset is audited but NOT fully verified. "
                "Unresolved under-construction and proposed stations still lack metro-grade coordinates; "
                "Yellow Line proposed names may change with realignment. Pink Line is out of scope."
            ),
            "sources": [
                SOURCE_MTP, SOURCE_KMRC, SOURCE_WIKI_LIST, SOURCE_ORANGE, SOURCE_YELLOW, SOURCE_OSM,
            ],
        },
        "stations": records,
    }
    DATA.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return dataset


def summarize(dataset):
    from collections import Counter, defaultdict
    line_counts = defaultdict(Counter)
    status_counts = Counter()
    manual = []
    for st in dataset["stations"]:
        status_counts[st["primary_status"]] += 1
        for ln in st["lines"]:
            line_counts[ln["line"]][ln["status"]] += 1
        if st["verification"]["needs_manual_verification"]:
            manual.append(st)
    print("Wrote", OUT)
    print("Total unique stations:", len(dataset["stations"]))
    print("Primary status breakdown:", dict(status_counts))
    print("Per-line line-assignment counts (status):")
    for line in ["Blue", "Green", "Purple", "Orange", "Yellow"]:
        print(f"  {line}: {dict(line_counts[line])} (total assignments {sum(line_counts[line].values())})")
    print("Needs manual verification:", len(manual))
    for st in manual:
        print(f"  - {st['id']}: {st['name']} | flags={st['verification']['flags']} | coords={st['lat']},{st['lon']}")


if __name__ == "__main__":
    summarize(build())
