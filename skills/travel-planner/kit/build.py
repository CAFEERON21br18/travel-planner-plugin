"""trip.json -> trip page (+ its map files). Usage: python3 build.py <trip-folder>

Reads <folder>/trip.json, writes <folder>/out/: index.html (publish this), tiles-base.json, tiles-detail.json,
glyphs.json (publish these next to it), preview.html (local testing only) and trip.resolved.json.
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geo, routes, links, basemap
from common import load, save


def render(trip, light):
    p = open(os.path.join(HERE, "templates", "trip.html"), encoding="utf-8").read()
    title = trip["trip"]["title"].replace("&", "&amp;").replace("<", "&lt;")
    p = p.replace("__TITLE__", title, 1)
    p = p.replace("/*__MAPLIBRE_CSS__*/", open(os.path.join(HERE, "templates", "maplibre.css")).read())
    p = p.replace("/*__LEAFLET_CSS__*/", open(os.path.join(HERE, "templates", "leaflet.css")).read())
    p = p.replace("/*__TRIP__*/null", json.dumps(trip, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
    p = p.replace("/*__LIGHT__*/null", json.dumps(light, separators=(",", ":")))
    p = p.replace("/*__I18N__*/", open(os.path.join(HERE, "templates", "i18n.js"), encoding="utf-8").read())
    return p


def main(folder, skip_tiles=False):
    t0 = time.time()
    trip = load(os.path.join(folder, "trip.json"))
    out = os.path.join(folder, "out"); os.makedirs(out, exist_ok=True)
    flags = []
    print("1/4 places"); flags += geo.resolve(trip)
    print("2/4 routes"); flags += routes.resolve(trip)
    links.resolve(trip)
    print("3/4 map data")
    if not skip_tiles:
        info = basemap.build(trip, out)
        print(f"    {info['tiles']} tiles, {info['mb_raw']} MB -> {info['mb']} MB after slimming")
    light = basemap.light(trip)
    trip["flags"] = flags
    save(trip, os.path.join(out, "trip.resolved.json"))
    print("4/4 page")
    page = render(trip, light)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page)
    open(os.path.join(out, "preview.html"), "w", encoding="utf-8").write(
        '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>' + page + "</body></html>")
    print(f"done in {time.time() - t0:.0f} s -> {out}")
    for f in flags:
        print("  FLAG", f)


if __name__ == "__main__":
    main(sys.argv[1], skip_tiles="--skip-tiles" in sys.argv)
