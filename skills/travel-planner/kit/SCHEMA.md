# trip.json

Claude writes this file and nothing else. The kit adds coordinates, routes, map data and builds the page and the PDF. Never write `lonlat`, `route`, `km`, `minutes`, `legs` or `flags` by hand: `build.py` fills them (a `lonlat` you set yourself is kept, as an override when geocoding fails).

Dates are `YYYY-MM-DD`, times `HH:MM` (24 h), money in whole units of `budget.currency`. Text is in `trip.lang`.

```json
{
  "trip": {
    "title": "Porto & Douro",              // shown as the page name
    "type": "road | short | normal | long",
    "lang": "en | pt | fr",
    "from": "Lisbon",                       // where the trip starts
    "country": "pt",                        // ISO code(s) of the countries visited, e.g. "pt" or "fr,es": places are only searched there
    "start": "2026-11-13", "end": "2026-11-15",
    "purpose": ["cultural", "food"],
    "pace": "relaxed | balanced | packed",
    "max_drive_hours": 3,                   // per day, road trips
    "note": "optional line under the title"
  },
  "group": { "adults": 2, "children": [], "friends_trip": false, "names": [] },

  "days": [{
    "date": "2026-11-13",
    "city": "Porto",                        // the day's base; stops are checked against it
    "title": "Porto on foot",
    "mode": "foot | car | transit",         // how you move between stops
    "rain_plan": "optional",
    "tips": ["optional"],
    "stops": [{
      "id": "d1s1",                          // unique in the trip
      "name": "Livraria Lello",
      "query": "Livraria Lello, Porto",     // what geocoding searches for
      "kind": "sight | food | view | activity | transport | sleep | night",   // night: bars/clubs; a time like 00:30 counts as that evening, and nights out don't count towards the pace limit
      "time": "09:30", "minutes": 45,        // planned arrival and time spent
      "hours": "09:30-19:00",               // opening hours as published
      "closed": ["mon"],                     // weekdays it is closed: mon tue wed thu fri sat sun
      "price": "€10",
      "link": "https://…",
      "tip": "optional",
      "source": "https://…", "checked": "2026-10-30"
    }]
  }],

  "lodging": [{
    "city": "Porto", "nights": ["2026-11-13"],
    "picked": { "name": "", "area": "", "price_night": 0, "link": "" },
    "options": []
  }],

  "todos": [{
    "id": "t1", "text": "Book the Livraria Lello ticket", "due": "2026-11-06",
    "owner": "", "cost": "€10", "link": "https://…",
    "category": "book | documents | money | pack | other", "source": ""
  }],

  "budget": {
    "currency": "EUR",
    "lines": [{
      "category": "getting-there | sleep | getting-around | car | food | activities | insurance | buffer",
      "label": "Train Lisbon–Porto, return",
      "saver": 50, "standard": 70, "comfort": 120,
      "per": "group | person | person-day | day", // amount for the group, each person, each person each day, or the group each day
      "indicative": true,                      // fares that must be confirmed
      "source": "https://…", "checked": "2026-10-30"
    }]
  },

  "practical": { "emergency": "112", "currency": "Euro", "plugs": "Type F, 230 V", "notes": [] },
  "packing": ["Rain jacket"],
  "sources": [{ "title": "…", "url": "https://…" }]
}
```

Rules the check enforces:
- every stop geocodes and lies within 30 km of its day's `city` (car days: within 150 km);
- no stop is planned on a weekday listed in `closed`;
- a day's planned time (stops + travel + 30 min buffer per half-day) fits the pace: relaxed 6 h, balanced 8 h, packed 10 h;
- driving per day stays under `trip.max_drive_hours`;
- stop times are in order and do not overlap once travel time is added;
- `budget` amounts are `saver ≤ standard ≤ comfort`.
