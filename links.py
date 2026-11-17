"""Links that need no API key: Google Maps directions, split so phones show every stop (max 3 waypoints)."""
import urllib.parse


def gmaps_day(day):
    pts = [s for s in day["stops"] if s.get("lonlat")]
    mode = {"foot": "walking", "car": "driving", "transit": "transit"}.get(day.get("mode"), "driving")
    out, i = [], 0
    while i < len(pts) - 1:
        part = pts[i:i + 5]
        ll = [f"{s['lonlat'][1]},{s['lonlat'][0]}" for s in part]
        q = {"api": "1", "origin": ll[0], "destination": ll[-1], "travelmode": mode}
        if len(ll) > 2:
            q["waypoints"] = "|".join(ll[1:-1])
        out.append({"url": "https://www.google.com/maps/dir/?" + urllib.parse.urlencode(q), "from": part[0]["name"], "to": part[-1]["name"]})
        i += 4
    return out


def gmaps_place(stop):
    return "https://www.google.com/maps/search/?" + urllib.parse.urlencode({"api": "1", "query": f"{stop['lonlat'][1]},{stop['lonlat'][0]}"})


def resolve(trip):
    for d in trip["days"]:
        d["gmaps"] = gmaps_day(d)
        for s in d["stops"]:
            if s.get("lonlat"):
                s["gmaps"] = gmaps_place(s)
    return []
