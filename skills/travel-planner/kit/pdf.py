"""Trip Book PDF from a built trip. Usage: python3 pdf.py <trip-folder> [--url <published trip page URL>]

Needs build.py to have run first (uses out/preview.html and out/trip.resolved.json).
Writes out/trip-book.pdf (send this file) and out/maps/*.png (map snapshots, same map code as the trip page).
"""
import functools, http.server, json, os, sys, threading
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import load

SNAP_CSS = """
.wrap{max-width:none!important;padding:0!important}.eyebrow,h1,.lead,.bar,.panel,.credit{display:none!important}
.grid{display:block!important}.mapcol{position:static!important}
.mapbox{width:%dpx!important;height:%dpx!important;border:0!important;border-radius:0!important}
.maplibregl-ctrl-top-right,.maplibregl-ctrl-bottom-right,.maplibregl-ctrl-bottom-left{display:none!important}
"""


def map_mm(day):
    """Height of a day's map on the A4 page (180 mm wide): smaller on busy days so the day fits one page."""
    n = len(day["stops"])
    return 82 if n <= 5 else 56 if n <= 7 else 44


def serve(folder):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=folder))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


def qr_svg(url):
    import io, segno
    buf = io.BytesIO()
    segno.make(url, error="m").save(buf, kind="svg", scale=4, border=0, dark="#1b2426", xmldecl=False, svgns=True)
    return buf.getvalue().decode()


PAGE_MM, PX_PER_MM, MIN_MAP_MM = 297 - 16 - 18, 96 / 25.4, 30


def snapshot(b, base, out, view, mm, overview=False):
    w = 1240
    h = 760 if overview else round(w * mm / 180)
    pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2, color_scheme="light")
    pg.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent=%s;document.head.appendChild(s)})" % json.dumps(SNAP_CSS % (w, h)))
    pg.goto(base + "preview.html#" + view)
    try:
        pg.wait_for_function("document.body.dataset.map === 'ready'", timeout=20000)
    except Exception:
        print(f"  map for {view} did not finish drawing; using what is there", file=sys.stderr)
    pg.wait_for_timeout(1200)
    pg.locator(".mapbox").screenshot(path=os.path.join(out, "maps", view + ".png"))
    pg.close()
    return {"src": f"maps/{view}.png?h={h}", "mm": mm}


def book_page(trip, maps, url):
    page = open(os.path.join(HERE, "templates", "book.html"), encoding="utf-8").read()
    page = page.replace("__TITLE__", trip["trip"]["title"].replace("&", "&amp;").replace("<", "&lt;"), 1)
    page = page.replace("/*__TRIP__*/null", json.dumps(trip, ensure_ascii=False).replace("</", "<\\/"))
    page = page.replace("/*__MAPS__*/null", json.dumps(maps))
    page = page.replace("/*__QR__*/null", json.dumps(qr_svg(url) if url else None))
    page = page.replace("/*__URL__*/null", json.dumps(url))
    return page.replace("/*__I18N__*/", open(os.path.join(HERE, "templates", "i18n.js"), encoding="utf-8").read())


def main(folder, url=None):
    out = os.path.join(folder, "out")
    trip = load(os.path.join(out, "trip.resolved.json"))
    os.makedirs(os.path.join(out, "maps"), exist_ok=True)
    srv, base = serve(out)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
        maps = {"overview": snapshot(b, base, out, "overview", 0, overview=True)}
        for i, d in enumerate(trip["days"]):
            maps[f"day-{i + 1}"] = snapshot(b, base, out, f"day-{i + 1}", map_mm(d))
        # Lay the book out at A4 width; a day taller than one page gets a shorter map, up to 3 rounds.
        pg = b.new_page(viewport={"width": round(180 * PX_PER_MM), "height": 1100})
        pg.emulate_media(media="print")
        for _ in range(3):
            open(os.path.join(out, "book.html"), "w", encoding="utf-8").write(book_page(trip, maps, url))
            pg.goto(base + "book.html")
            pg.wait_for_function("window.BOOK_READY === true", timeout=20000)
            pg.wait_for_timeout(300)
            heights = pg.evaluate("[...document.querySelectorAll('section.day')].map(s => [s.dataset.day, s.getBoundingClientRect().height])")
            over = {int(k): h / PX_PER_MM - PAGE_MM for k, h in heights if h / PX_PER_MM > PAGE_MM - 2}
            fixable = {k: v for k, v in over.items() if maps[f"day-{k}"]["mm"] > MIN_MAP_MM}
            if not fixable:
                break
            for k, v in fixable.items():
                mm = max(MIN_MAP_MM, round(maps[f"day-{k}"]["mm"] - v - 4))
                print(f"  day {k} is {v:.0f} mm too tall: map {maps[f'day-{k}']['mm']} -> {mm} mm")
                maps[f"day-{k}"] = snapshot(b, base, out, f"day-{k}", mm)
        foot = f'<div style="width:100%;font:8px sans-serif;color:#56625f;padding:0 15mm;display:flex;justify-content:space-between"><span>{trip["trip"]["title"].replace("&", "&amp;").replace("<", "&lt;")}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'
        pdf = os.path.join(out, "trip-book.pdf")
        pg.pdf(path=pdf, format="A4", print_background=True, prefer_css_page_size=True, display_header_footer=True, header_template="<span></span>", footer_template=foot)
        b.close()
    srv.shutdown()
    print("PDF ->", pdf)
    return pdf


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[a.index("--url") + 1] if "--url" in a else None)
