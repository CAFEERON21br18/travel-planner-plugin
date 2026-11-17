# Planning rules

`check.py` enforces the starred rules; follow the rest while writing.

- ★ No stop on a weekday listed in its `closed`, nor on a holiday closure.
- ★ Stop times in order: arrival ≥ previous arrival + time spent + travel (10 min slack).
- ★ Day span within the pace: relaxed 6 h, balanced 8 h, packed 10 h (+1 h allowance).
- ★ Driving per day within `trip.max_drive_hours` (default 3 h; from the form when given).
- ★ Every stop found on the map within 30 km of its day's `city` (150 km on car days).
- ★ Budget amounts `saver ≤ standard ≤ comfort`; to-dos due before the trip starts.
- One area per day; stops in route order, not list order.
- Arrival and departure days stay light and respect check-in / check-out times.
- Meals as `food` stops around 12:30–14:00 and 19:30–21:00 (adjust to the country).
- Outdoor days get a `rain_plan`.
- A day with more than 7 stops won't fit one PDF page: split it or drop the weakest stop.
- Road trips: a break about every 2 hours of driving.
- Busy, famous sights: first thing in the morning or a timed ticket, with a to-do.
- Budget variants: same itinerary, different choices (Saver: connections, hostels/campsites, public transport, groceries; Standard: direct, 3-star or flat, one restaurant meal a day; Comfort: best times, 4-star+, rental car, restaurants). `per`: `group`, `person`, `person-day` or `day`. The page and PDF add a 10% buffer.
