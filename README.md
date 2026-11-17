# travel-planner

Claude plug-in that turns two short forms into a researched trip: an interactive trip page (map with real routes, day timelines, budget in three variants, to-dos) and a Trip Book PDF (cover with QR code, to-dos by deadline, one page per day with its map, budget variants, practical info).

## How it runs

`skills/travel-planner/SKILL.md` is the workflow Claude follows: Form 1 → Form 2 (only the follow-ups that apply) → research → a round of choices → build, check, publish, PDF. `references/` holds the intake defaults, the research checklist and the planning rules. The forms come from `kit/questions.py` (EN/PT/FR, fixed wording).

## Kit (skills/travel-planner/kit)

Claude writes only `trip.json` (format in `SCHEMA.md`). The scripts do the rest:

```
python3 build.py samples/porto-douro          # places, routes, map data, page -> samples/porto-douro/out/
python3 pdf.py samples/porto-douro --url <published page URL>   # Trip Book -> out/trip-book.pdf
python3 check.py samples/porto-douro --shots --pdf  # rules, screenshots, PDF; must print ALL CHECKS PASSED
```

Publish `out/index.html` with `tiles-base.json`, `tiles-detail.json` and `glyphs.json` next to it.

| File | Does |
| --- | --- |
| `geo.py` | Coordinates from OpenStreetMap Nominatim (1 request/s, cached, limited to `trip.country`) |
| `routes.py` | Real routes: OSRM (car), routing.openstreetmap.de (foot); straight-line estimates as fallback |
| `basemap.py` | OpenFreeMap tiles picked around the stops, Natural Earth for the light map |
| `slim.py`, `layers.py` | Strip unused map layers and translated names from tiles (~60% smaller) |
| `questions.py` | Form 1, Form 2 and the choices round, as form-widget HTML or numbered text |
| `links.py` | Google Maps links, split so phones show every stop |
| `build.py` | Runs everything and fills `templates/trip.html` |
| `pdf.py` | Trip Book PDF: map snapshots, `templates/book.html`, A4 with page numbers, QR to the trip page |
| `templates/i18n.js` | EN/PT/FR labels shared by the page and the PDF |
| `check.py` | Plan rules (closed days, pace, driving, timing, budget), page checks at 400/1440 px light/dark, PDF checks (a page and map per day, links, no day spilling onto a second page) |

Needs Python 3, `shapely`, `playwright`, `segno` (QR) and `pypdf` (PDF check). Map data © OpenStreetMap contributors, OpenMapTiles, OpenFreeMap; Natural Earth (public domain).
