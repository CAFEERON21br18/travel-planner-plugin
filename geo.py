"""Coordinates for every stop and every day's base city (OpenStreetMap Nominatim, 1 request/s, cached)."""
import json, sys, urllib.parse
from common import http, km, load, save

NOMINATIM = "https://nominatim.openstreetmap.org/search?"


def geocode(q, country=None):
    p = {"q": q, "format": "json", "limit": 1}
    if country:
        p["countrycodes"] = country
    try:
        r = json.loads(http(NOMINATIM + urllib.parse.urlencode(p), min_gap=1.1))
    except Exception as e:  # blocked or offline: caller flags it
        print(f"  geocode failed for {q!r}: {e}", file=sys.stderr)
        return None
    return [round(float(r[0]["lon"]), 6), round(float(r[0]["lat"]), 6)] if r else None


def resolve(trip):
    """Fill stop.lonlat and day.center; add flags for places that can't be found or sit too far away."""
    flags = []
    cc = trip["trip"].get("country")
    if not cc:
        flags.append("trip.country is missing: add the ISO codes (e.g. \"pt\" or \"pt,es\") so places are searched in the right country")
    for d in trip["days"]:
        d["center"] = d.get("center") or geocode(d["city"], cc)
        limit = 150 if d.get("mode") == "car" else 30
        for s in d["stops"]:
            if not s.get("lonlat"):
                s["lonlat"] = geocode(s.get("query") or s["name"], cc)
            if not s["lonlat"]:
                flags.append(f"{d['date']} · {s['name']}: not found on the map (query {s.get('query')!r})")
            elif d["center"] and km(s["lonlat"], d["center"]) > limit:
                flags.append(f"{d['date']} · {s['name']}: {km(s['lonlat'], d['center']):.0f} km from {d['city']} (limit {limit} km), probably the wrong place")
    return flags


if __name__ == "__main__":
    t = load(sys.argv[1]); f = resolve(t); save(t, sys.argv[1]); print("\n".join(f) or "all places found")
