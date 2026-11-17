"""Real routes between stops: OSRM for driving, routing.openstreetmap.de for walking.
Falls back to straight lines (x1.3) with an 'estimate' flag when a router can't be reached."""
import json, sys
from common import http, km, load, save

ROUTERS = {
    "car": "https://router.project-osrm.org/route/v1/driving/",
    "foot": "https://routing.openstreetmap.de/routed-foot/route/v1/driving/",
}
SPEED = {"car": 60, "foot": 4.5, "transit": 20}  # km/h for estimates


def estimate(pts, mode):
    legs = []
    for a, b in zip(pts, pts[1:]):
        d = km(a, b) * 1.3
        legs.append({"km": round(d, 1), "min": round(d / SPEED[mode] * 60) + (5 if mode == "transit" else 0), "estimate": True})
    return {"route": pts, "legs": legs}


def route(pts, mode):
    if mode == "transit" or mode not in ROUTERS:
        return estimate(pts, "transit" if mode == "transit" else "car")
    coords = ";".join(f"{x:.6f},{y:.6f}" for x, y in pts)
    try:
        r = json.loads(http(ROUTERS[mode] + coords + "?overview=full&geometries=geojson", min_gap=1.0))
        rt = r["routes"][0]
    except Exception as e:
        print(f"  routing failed ({mode}): {e}", file=sys.stderr)
        return estimate(pts, mode)
    return {
        "route": [[round(x, 5), round(y, 5)] for x, y in rt["geometry"]["coordinates"]],
        "legs": [{"km": round(l["distance"] / 1000, 1), "min": round(l["duration"] / 60)} for l in rt["legs"]],
    }


def resolve(trip):
    flags = []
    for d in trip["days"]:
        pts = [s["lonlat"] for s in d["stops"] if s.get("lonlat")]
        if len(pts) < 2:
            d.update(route=pts, legs=[], km=0, minutes=0); continue
        r = route(pts, d.get("mode", "car"))
        d.update(r)
        d["km"] = round(sum(l["km"] for l in r["legs"]), 1)
        d["minutes"] = sum(l["min"] for l in r["legs"])
        if d.get("mode") != "transit" and any(l.get("estimate") for l in r["legs"]):  # transit is always an estimate (shown on the page)
            flags.append(f"{d['date']}: travel times are estimates (no router answer for mode {d.get('mode')})")
    return flags


if __name__ == "__main__":
    t = load(sys.argv[1]); f = resolve(t); save(t, sys.argv[1]); print("\n".join(f) or "routes ok")
