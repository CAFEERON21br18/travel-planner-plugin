---
name: travel-planner
description: Plans a trip from two short forms and delivers an interactive trip page (real map, day timelines, budget in three variants, shared to-dos) and a Trip Book PDF. Use when someone asks to plan, organise or build an itinerary for a trip, road trip, city break or holiday.
---

# Travel Planner

Two short forms → research → a round of choices → two deliverables built by the kit in `kit/`:

1. **Trip page** (artifact): map with real routes, a tab per day with a timeline, Budget (Saver / Standard / Comfort), To-dos with shared ticks.
2. **Trip Book PDF**: cover with QR code to the page, to-dos by deadline, one page per day with its map, budget, practical info.

## Rule zero: the kit decides the look, you only write `trip.json`

- Every output comes out of `kit/build.py` and `kit/pdf.py`. Never write or patch page or PDF HTML/CSS/JS by hand.
- You write **only** `trip.json` as described in `kit/SCHEMA.md`, with Python `json.dump`, never by hand-typed JSON.
- Never write coordinates, routes, km or minutes: the kit adds them from each stop's `query`.
- The forms always come from `kit/questions.py`, in its order and wording. Never reword, reorder or add questions.
- If something can't be done with the kit, say so in one line at the end. Don't work around it.

## Step 0: set up

```
cd <this skill's folder>/kit
pip install --break-system-packages -q shapely segno pypdf   # once per session; playwright + chromium are needed too
```
Work in a trip folder: `kit/trips/<short-slug>/` (its `trip.json` and `out/`).

## Step 1: Form 1 (always)

1. Before asking, take anything the person already said in their message (destination, dates, who) and don't ask for it again later; the form is still shown whole.
2. `python3 questions.py form1 --lang <en|pt|fr>` (language of the conversation).
3. Call the Visualizer `read_me` (module `elicitation`), then `show_widget` with **exactly** the printed HTML, title `trip_details`.
4. No Visualizer → send `python3 questions.py form1 --lang .. --text` verbatim and wait for numbered answers.
5. Skipped or unattended → `references/intake.md` defaults; say which were used.

A blank answer means "I don't know": you will propose options, never guess silently. **Leaving from** and **who is going** are needed for every price: if blank, ask once in one line.

## Step 2: Form 2 (only the follow-ups that apply)

Build `form2.json` from Form 1 (rules in `references/intake.md`), then `python3 questions.py form2 form2.json --lang ..` and show it the same way. Keys:

| Key | When | Value |
| --- | --- | --- |
| `destinations` | no destination given | 3 ideas from a quick web search matching purpose, budget, dates: `[{name, why, budget, months}]` |
| `road` | trip type = road trip | `{recommended_stops: n}`: one break per ~2 h of driving on the longest day + 1–2 scenic stops |
| `car` | road trip or own car | `true` |
| `flights` | plane chosen and no direct flight exists or another continent | `true` |
| `friends` | friends trip | `{count: n}` from "who is going" |
| `sport` | purpose includes sport | `true` |
| `rental` | rental car chosen | `true` |

Nothing applies → skip Form 2. Friends' emails and phone numbers stay in this conversation only: never put them in `trip.json`, the page, the PDF or memory.

## Step 3: research

Follow `references/research-checklist.md`. Cities or regions go to **subagents in parallel** (one per city, up to 4), each returning stops, food and lodging options with sources; transport, entry rules, holidays, climate and budget stay in the main thread.

- Open the page you take a fact from; a search snippet is not a source. Every price, opening hour and booking deadline keeps `source` and `checked` (today).
- No live fare feed exists: flight and train prices are typical ranges from web search, marked `"indicative": true`, with a pre-filled search link in the to-do.
- A fact you can't confirm becomes a to-do ("Check the opening hours"), never a guess.
- Plan each day with `references/planning-rules.md`. Bars and clubs are stops of kind `night` (00:30 counts as that evening; nights out don't count towards the pace).

## Step 4: the choices round (always)

Even when Form 1 was complete, offer 2–3 options for each basic decision before building: flight or train (times, stops, price range), area to stay + 2–3 places per city, rental car or public transport, road-trip stops, and anything left blank. Write `choices.json` (`[{id, question, options:[{title, lines, price}], recommended}]`), run `python3 questions.py choices choices.json --lang ..`, show it. Unanswered → take the recommended option and say so.

## Step 5: write trip.json and build

1. Write `trips/<slug>/trip.json` per `SCHEMA.md` with the picks: `trip.country` is required (ISO codes), budget lines with all three variants, to-dos with due dates **before** `trip.start`, a `rain_plan` on outdoor days, `sources`.
2. `python3 build.py trips/<slug>`
3. `python3 check.py trips/<slug> --shots` must print **ALL CHECKS PASSED**. A failure is fixed in `trip.json` (wrong place → better `query`; late arrival → move times; closed day → swap days), then rebuild. Look at `out/shots/` once (a day, budget, to-dos).

## Step 6: publish and make the PDF

1. Publish `out/index.html` with the Artifact tool, `files`: `tiles-base.json`, `tiles-detail.json`, `glyphs.json` from `out/`; `icon: "map"`; `capabilities: {db: {}}` (shared to-do ticks). Then one `ArtifactData` list of `ticks` (empty is fine).
2. `python3 pdf.py trips/<slug> --url <the published URL>` (puts the QR code on the cover).
3. `python3 check.py trips/<slug> --pdf` must pass. pdf.py already shrinks the map of a day that is too tall; a day that still spills over has too many stops → fold one into another stop's tip or split the day.
4. Send `out/trip-book.pdf` with SendUserFile.

## Step 7: friends trip

Prepare a ready-to-send message (message widget if available, else plain text) with the trip page link and a line to attach the PDF, addressed to the contacts from Form 2. Say once that the page is private until shared from its Share menu, and that Claude can't send it or share it. To-do ticks are shared once friends can open the page.

## Finish

A few lines: what was built (the card carries the page link), the PDF, the to-dos due first, anything marked indicative or left to check, and anything the kit couldn't do. No recap of the steps.
