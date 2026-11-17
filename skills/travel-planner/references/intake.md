# Intake: reading the forms

## Form 1 answers → trip.json

| Answer | Goes to |
| --- | --- |
| Leaving from | `trip.from` (also the start of the first day / the flight search) |
| Trip type | `trip.type`. If the dates disagree (a "short trip" of 12 days), the dates win: say so in one line |
| Where | `trip.title`, `trip.country` (ISO codes of every country visited) |
| Cities + which | the bases; the number caps how many bases the plan uses |
| Who | `group.adults`, `group.children` (ages), `group.friends_trip` |
| Sleep | lodging options offered in the choices round |
| Getting there | transport options offered in the choices round |
| Purpose | `trip.purpose`; shapes the stops |
| Budget + basis + strict/flexible | compare the Standard total to it: strict → Standard must fit, flag if not; flexible → say how far over |
| Getting around | `days[].mode`: foot / car / transit |
| Dates + flexibility | `trip.start`, `trip.end`; flexible → propose cheaper dates in the choices round |
| Pace | `trip.pace` |
| Must-see | stops that must appear; things to avoid never appear |
| Extra | diet, mobility (less walking → fewer foot legs), pets (lodging), nationality (entry rules), language (`trip.lang`), bookings |
| Booked files | read them; booked items become fixed stops / lodging and are not offered again |

## Defaults when skipped or unattended

Leaving from: ask once (no default). Who: 2 adults. Type: from the dates. Sleep: hotel. Getting there: cheapest sensible. Purpose: discovery + cultural. Budget: none (show the three variants). Getting around: on foot + public transport (rental car on rural days). Dates: the next sensible window, 3 nights. Flexibility: exact. Pace: balanced. Language: the conversation's. Nationality: EU citizen.

## Form 2 rules

- `destinations`: only when "where" is blank. 3 places that fit purpose, budget and month, each with one line why, a rough per-person budget and the best months.
- `road.recommended_stops`: longest driving day in hours ÷ 2, rounded up, plus 1–2 scenic stops.
- `flights`: plane chosen and either no direct flight from the departure airport or another continent.
- `rental`: rental car chosen. Many firms set a minimum age (often 21) and charge drivers under 25 or with a recent licence extra: add a to-do to check the firm's conditions.
- `sport`: level shapes the spots (beginner → schools and gentle spots); flying with gear → a to-do to check the airline's sports-equipment fee.
