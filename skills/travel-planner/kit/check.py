"""Checks a built trip. Usage: python3 check.py <trip-folder> [--shots] [--pdf]
Prints ALL CHECKS PASSED or the list of problems. Fix trip.json and rebuild; never patch the page."""
import functools, http.server, json, os, sys, threading
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import load, minutes, weekday

PACE = {"relaxed": 6 * 60, "balanced": 8 * 60, "packed": 10 * 60}
KINDS = {"sight", "food", "view", "activity", "transport", "sleep", "night"}


def smin(s):
    """Stop time in minutes; a night stop after midnight (e.g. 00:30) belongs to the evening before."""
    m = minutes(s["time"])
    return m + 1440 if s.get("kind") == "night" and m < 720 else m
REQ = {"trip": ["title", "lang", "start", "end", "pace"], "group": ["adults"]}


def data_checks(t):
    bad = list(t.get("flags", []))
    for k, fields in REQ.items():
        for f in fields:
            if f not in t.get(k, {}):
                bad.append(f"missing {k}.{f}")
    ids = set()
    for d in t["days"]:
        prev_end, prev_i = None, None
        for i, s in enumerate(d["stops"]):
            if s.get("id") in ids: bad.append(f"duplicate stop id {s.get('id')}")
            ids.add(s.get("id"))
            if s.get("kind") not in KINDS: bad.append(f"{d['date']} · {s['name']}: kind {s.get('kind')!r} not in {sorted(KINDS)}")
            if weekday(d["date"]) in s.get("closed", []): bad.append(f"{d['date']} · {s['name']}: closed on {weekday(d['date'])}")
            if not s.get("time"): bad.append(f"{d['date']} · {s['name']}: no time"); continue
            a = smin(s)
            if prev_end is not None:
                travel = d["legs"][i - 1]["min"] if d.get("legs") and i - 1 < len(d["legs"]) else 0
                if a + 10 < prev_end + travel:
                    bad.append(f"{d['date']} · {s['name']} at {s['time']}: arrives {prev_end + travel - a} min late (previous stop + {travel} min travel)")
            prev_end = a + s.get("minutes", 0)
        st = [s for s in d["stops"] if s.get("time") and s.get("kind") != "night"]  # nights out don't count towards the day's length
        if st:
            span = smin(st[-1]) + st[-1].get("minutes", 0) - smin(st[0])
            limit = PACE.get(t["trip"]["pace"], 480) + 60  # + buffer allowance
            if span > limit: bad.append(f"{d['date']}: day lasts {span // 60} h {span % 60:02d}, more than the {t['trip']['pace']} pace allows")
        if d.get("mode") == "car" and t["trip"].get("max_drive_hours") and d.get("minutes", 0) > t["trip"]["max_drive_hours"] * 60:
            bad.append(f"{d['date']}: {d['minutes']} min of driving, more than {t['trip']['max_drive_hours']} h")
    for l in t.get("budget", {}).get("lines", []):
        if not l.get("saver", 0) <= l.get("standard", 0) <= l.get("comfort", 0):
            bad.append(f"budget {l['label']}: saver ≤ standard ≤ comfort is not true")
        if l.get("per", "group") not in ("group", "person", "person-day", "day"): bad.append(f"budget {l['label']}: per {l.get('per')!r}")
    for x in t.get("todos", []):
        if x.get("due") and x["due"] > t["trip"]["start"]: bad.append(f"to-do {x['text']!r} is due after the trip starts")
    return bad


def page_checks(out):
    from playwright.sync_api import sync_playwright
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    handler = functools.partial(Quiet, directory=out)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/preview.html"
    bad, shots = [], os.path.join(out, "shots"); os.makedirs(shots, exist_ok=True)
    n = len(load(os.path.join(out, "trip.resolved.json"))["days"])
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
        for w, h in [(400, 860), (1440, 900)]:
            for scheme in ["light", "dark"]:
                pg = b.new_page(viewport={"width": w, "height": h}, color_scheme=scheme)
                errs = []
                pg.on("pageerror", lambda e: errs.append(str(e)))
                pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                for view in ["overview"] + [f"day-{i + 1}" for i in range(n)] + ["budget", "todos"]:
                    pg.goto(url + "#" + view)
                    try:
                        if view == "overview" and not pg.evaluate("document.body.dataset.map"):
                            pg.wait_for_function("document.body.dataset.map === 'ready'", timeout=15000)
                    except Exception:
                        bad.append(f"{w}px {scheme}: street map never finished drawing")
                    pg.wait_for_timeout(900)
                    sw = pg.evaluate("document.documentElement.scrollWidth")
                    if sw > w: bad.append(f"{w}px {scheme} #{view}: page is {sw}px wide (horizontal scroll)")
                    if view in ("overview", "day-1", "budget", "todos"):
                        pg.screenshot(path=os.path.join(shots, f"{w}-{scheme}-{view}.png"), full_page=view in ("budget", "todos"))
                bad += [f"{w}px {scheme}: script error {e}" for e in set(errs)]
                pg.close()
        b.close()
    srv.shutdown()
    return bad


def pdf_checks(out, t):
    import pypdf
    path = os.path.join(out, "trip-book.pdf")
    if not os.path.exists(path):
        return ["trip-book.pdf missing: run pdf.py"]
    bad, r = [], pypdf.PdfReader(path)
    texts = [pg.extract_text() or "" for pg in r.pages]
    links = [sum(1 for a in (pg.get("/Annots") or []) if a.get_object().get("/A", {}).get("/URI")) for pg in r.pages]
    starts = {}
    for i, d in enumerate(t["days"]):
        hits = [k for k, tx in enumerate(texts) if k > 0 and d["title"] in tx[:160]]
        if not hits: bad.append(f"PDF: no page for day {i + 1} ({d['title']})"); continue
        starts[hits[0]] = i
        if not os.path.exists(os.path.join(out, "maps", f"day-{i + 1}.png")): bad.append(f"PDF: no map for day {i + 1}")
        if d.get("gmaps") and links[hits[0]] == 0: bad.append(f"PDF: day {i + 1} page has no working links")
    for k in sorted(starts):
        nxt = k + 1
        if nxt < len(texts) and nxt not in starts and not any(h in texts[nxt] for h in ("Budget", "Orçamento", "Practical", "Informações", "Infos pratiques")):
            bad.append(f"PDF: day {starts[k] + 1} runs onto a second page (shorten it or split the day)")
    return bad


if __name__ == "__main__":
    folder = sys.argv[1]
    out = os.path.join(folder, "out")
    t = load(os.path.join(out, "trip.resolved.json"))
    bad = data_checks(t)
    if "--shots" in sys.argv:
        bad += page_checks(out)
    if "--pdf" in sys.argv:
        bad += pdf_checks(out, t)
    print("ALL CHECKS PASSED" if not bad else "PROBLEMS:\n- " + "\n- ".join(bad))
    sys.exit(1 if bad else 0)
