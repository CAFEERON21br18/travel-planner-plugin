"""Map data shipped with the trip page.

Street map: OpenFreeMap vector tiles (free, no key; offline use allowed up to 3,000 tiles / 50 MB per download),
picked from the trip itself: the whole region at zoom 5-9, each day's route corridor at 10-11, the streets around
each stop at 12-14. Layers the page never draws and translated names are stripped (slim.py).
Light map: Natural Earth (public domain) clipped to the trip.
"""
import base64, json, math, os, sys
from common import CACHE, http
from slim import slim

GLYPH_FONTS = ["Noto Sans Regular", "Noto Sans Bold"]
GLYPH_RANGES = ["0-255", "256-511", "8192-8447"]
MAX_TILES = 600


def tile(lon, lat, z):
    n = 2 ** z
    lat = max(min(lat, 85), -85)
    return int((lon + 180) / 360 * n), int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)


def tiles_in(bbox, z):
    w, s, e, n = bbox
    x0, y1 = tile(w, s, z); x1, y0 = tile(e, n, z)
    return [(z, x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]


def bbox_of(pts, pad=0.0):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    w, e, s, n = min(xs), max(xs), min(ys), max(ys)
    dx, dy = (e - w) * pad + 0.01, (n - s) * pad + 0.01
    return (w - dx, s - dy, e + dx, n + dy)


def plan(trip):
    """Which tiles to fetch, from the stops and routes."""
    want = set()
    allpts = [p for d in trip["days"] for p in (d.get("route") or [])] + [s["lonlat"] for d in trip["days"] for s in d["stops"] if s.get("lonlat")]
    region = bbox_of(allpts, 0.35)
    for z in range(5, 10):
        t = tiles_in(region, z)
        if z >= 8 and len(t) > 40:
            break
        want.update(t)
    for d in trip["days"]:
        pts = (d.get("route") or []) + [s["lonlat"] for s in d["stops"] if s.get("lonlat")]
        if not pts:
            continue
        corridor = bbox_of(pts, 0.1)
        for z in (10, 11):
            t = tiles_in(corridor, z)
            if len(t) <= 40:
                want.update(t)
        for s in d["stops"]:
            if not s.get("lonlat") or s.get("kind") == "transport" and s.get("minutes", 0) == 0 and d.get("mode") == "car":
                continue
            x, y = s["lonlat"]
            for z in (12, 13):
                want.update(tiles_in((x - 0.012, y - 0.009, x + 0.012, y + 0.009), z))
            r = 0.006 if d.get("mode") == "foot" else 0.004
            want.update(tiles_in((x - r, y - r * 0.75, x + r, y + r * 0.75), 14))
    want = sorted(want)
    if len(want) > MAX_TILES:  # keep the lowest zooms first
        want = sorted(want, key=lambda t: t[0])[:MAX_TILES]
    return want


def build(trip, out):
    tj = json.loads(http("https://tiles.openfreemap.org/planet", cache=False))
    tpl = tj["tiles"][0]
    base, detail, raw, small = {}, {}, 0, 0
    for z, x, y in plan(trip):
        b = http(tpl.format(z=z, x=x, y=y), binary=True)
        s = slim(b); raw += len(b); small += len(s)
        (base if z <= 11 else detail)[f"{z}/{x}/{y}"] = base64.b64encode(s).decode()
    json.dump(base, open(os.path.join(out, "tiles-base.json"), "w"))
    json.dump(detail, open(os.path.join(out, "tiles-detail.json"), "w"))
    glyphs = {}
    for f in GLYPH_FONTS:
        for r in GLYPH_RANGES:
            glyphs[f"{f}/{r}"] = base64.b64encode(http(f"https://tiles.openfreemap.org/fonts/{f.replace(' ', '%20')}/{r}.pbf", binary=True)).decode()
    json.dump(glyphs, open(os.path.join(out, "glyphs.json"), "w"))
    return {"tiles": len(base) + len(detail), "mb_raw": round(raw / 1e6, 1), "mb": round(small / 1e6, 1)}


NE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"


def light(trip):
    """Natural Earth layers clipped to the trip (for the light map)."""
    from shapely.geometry import shape, box, mapping
    allpts = [s["lonlat"] for d in trip["days"] for s in d["stops"] if s.get("lonlat")]
    w, s_, e, n = bbox_of(allpts, 0.6)
    w, s_, e, n = w - 0.5, s_ - 0.4, e + 0.5, n + 0.4
    B = box(w, s_, e, n)

    def rnd(c):
        return [rnd(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], 4), round(c[1], 4)]

    def clip(fn, props=(), keep=lambda p: True, tol=0.002):
        path = os.path.join(CACHE, "ne", fn + ".geojson")
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "wb").write(http(NE + fn + ".geojson", binary=True, cache=False))
        fs = []
        for f in json.load(open(path))["features"]:
            if not keep(f["properties"]):
                continue
            g = shape(f["geometry"])
            if not g.intersects(B):
                continue
            g = g.intersection(B).simplify(tol, preserve_topology=True)
            if g.is_empty:
                continue
            m = mapping(g)
            fs.append({"type": "Feature", "geometry": {"type": m["type"], "coordinates": rnd(m["coordinates"])}, "properties": {k: f["properties"].get(k) for k in props}})
        return {"type": "FeatureCollection", "features": fs}

    return {
        "land": clip("ne_10m_land"),
        "rivers": clip("ne_10m_rivers_lake_centerlines", ("name",)),
        "borders": clip("ne_10m_admin_0_boundary_lines_land"),
        "roads": clip("ne_10m_roads", ("type",), lambda p: p.get("type") in ("Major Highway", "Secondary Highway")),
        "towns": clip("ne_10m_populated_places_simple", ("name",), lambda p: (p.get("pop_max") or 0) > 15000),
        "bounds": [[w, s_], [e, n]],
    }


if __name__ == "__main__":
    t = json.load(open(sys.argv[1])); print(len(plan(t)), "tiles planned")
