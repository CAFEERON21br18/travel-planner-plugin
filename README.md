# travel-planner

Claude plug-in that turns two short forms into a researched trip: an interactive trip page (map with real routes, day timelines, budget in three variants, to-dos) and a Trip Book PDF (PDF: phase 2, in progress).

## Kit (skills/travel-planner/kit)

Claude writes only `trip.json` (format in `SCHEMA.md`). The scripts do the rest:

```
python3 build.py samples/porto-douro          # places, routes, map data, page -> samples/porto-douro/out/
python3 check.py samples/porto-douro --shots  # rules + screenshots; must print ALL CHECKS PASSED
```

Publish `out/index.html` with `tiles-base.json`, `tiles-detail.json` and `glyphs.json` next to it.

| File | Does |
| --- | --- |
| `geo.py` | Coordinates from OpenStreetMap Nominatim (1 request/s, cached, limited to `trip.country`) |
| `routes.py` | Real routes: OSRM (car), routing.openstreetmap.de (foot); straight-line estimates as fallback |
| `basemap.py` | OpenFreeMap tiles picked around the stops, Natural Earth for the light map |
| `slim.py`, `layers.py` | Strip unused map layers and translated names from tiles (~60% smaller) |
| `links.py` | Google Maps links, split so phones show every stop |
| `build.py` | Runs everything and fills `templates/trip.html` |
| `check.py` | Plan rules (closed days, pace, driving, timing, budget) + page checks at 400/1440 px, light/dark |

Needs Python 3, `shapely` and `playwright` (for `check.py --shots`). Map data © OpenStreetMap contributors, OpenMapTiles, OpenFreeMap; Natural Earth (public domain).
