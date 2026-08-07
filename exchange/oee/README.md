# Launchpad OEE (AU)

An Australian port of the Inductive Automation **Launchpad OEE** Exchange resource.

## Why this exists

Inductive Automation's Launchpad OEE demo is a good showcase, but it ships in
US units and date conventions, and its shift roster leaves a twelve-hour hole
in the day — so it doesn't demonstrate OEE the way an Australian site actually
runs one. This is a straight port: metric at the source, DD/MM/YYYY, 24-hour
time, and a roster that covers all three shifts, plus a handful of bugs fixed
along the way. Everything runs from a self-contained simulator; no PLC or
field device is required.

## What it looks like

![OEE overview with all seven production lines, live Availability / Performance / Quality / Utilisation](docs/images/oee-overview.png)
*Overview — all seven lines at a glance, realtime or historical, by the hour.*

![OEE line view showing OEE trend and production against target for a single line](docs/images/oee-line-view.png)
*Line View — one line's OEE trend and production-vs-target over the selected window.*

![OEE production summary table across all seven lines for a chosen period](docs/images/oee-production.png)
*Production Summary — every line, any date range, runtime/downtime/idle included.*

## What it does

- Seven simulated production lines with live **Availability, Performance,
  Quality and Utilisation**, computed per hour, per shift and per day.
- A SQL history of shift and hourly statistics backing the Line View trend
  charts and the Production Summary table.
- A 3 × 8h shift roster (22:00–06:00, 06:00–14:00, 14:00–22:00) enabled on
  all seven lines out of the box.
- A WebDev installer endpoint that seeds tables, shifts and 30 days of demo
  history without opening a Designer.
- Metric units, DD/MM/YYYY dates and 24-hour time throughout the project's
  own screens — see *What "AU" changes* below.

## How to use it

### Install

1. **Gateway resources.** Create a tag provider named `launchpad`, a database
   connection named `Examples`, and a tag historian named `launchpad` pointing at it.
   `Gateway/` carries all three as 8.3 config resources if you would rather drop them
   in and run a **Config → Scan File System** than click through the pages.
   `Examples` is SQLite at `${data}/Examples.db` so the resource stays self-contained;
   point it at Postgres or MSSQL instead if you would rather.
2. **Project.** Import `Projects/OEE.zip`.
3. **Tags.** Import `Tags/launchpad-oee-udts.json` **first**, then
   `Tags/launchpad-oee-tags.json`, both into the `launchpad` provider. Order matters —
   an instance whose UDT type is missing loads broken and does not repair itself when
   the type arrives later.
4. **Gateway scripting project.** Set it to `OEE` under Config → System Properties.
   The UDT event scripts call `exchange.launchpad.oee.*` and resolve it from there;
   nothing computes until this is set.
5. **Seed the data** — see below.

### Seeding

The project carries a WebDev endpoint, `lp_init`, that performs the one-time setup.
**It ships requiring authentication**; either log in first or set
`require-auth: false` on the resource while you run these, then set it back.

    GET /system/webdev/OEE/lp_init?action=<action>

Run in this order:

| # | action | what it does |
|---|--------|--------------|
| 1 | `initTables` | creates the OEE shift/hour/rate tables |
| 2 | `setupShifts` | writes the 3 × 8h roster and enables it on every line |
| 3 | `seedHistory` | generates 30 days of shift and hourly history |
| 4 | `resetDemoTags` | zeroes the counters |
| 5 | *(wait ~45 s)* | the schedule expressions need a tick to publish the current shift start before step 6 reads it |
| 6 | `initDemoTags` | sets counters and run-times consistent with the current shift |

`status`, `diag` and `intervals` are read-only and report what the engine currently
holds — `intervals` gives O/A/P/Q/U for every line across all three windows, which is
the quickest way to confirm a healthy install.

Every action is idempotent. `initTables` in particular issues bare `CREATE UNIQUE
INDEX` statements, so re-running the underlying script directly would throw half-way
and leave the schema partly built; the endpoint checks first and skips.

### If you would rather not ship an HTTP endpoint

Delete the `lp_init` resource and call the same functions from a Designer script
console — `exchange.launchpad.oee.initTables()`, `.resetDemoTags()`,
`.initDemoTags()`, and `.makeHistory(lineName)` per line. `setupShifts` has no script
equivalent; write the shift times on the `Schedule` UDT members by hand, or on the
project's own Settings screen.

---

## What "AU" changes

This is a port, not a rewrite. The screens, the OEE engine and the UDT structure are
the original's. What differs:

- **Metric and local conventions.** Temperatures in °C, pressures in kPa, dates
  DD/MM/YYYY, 24-hour time, and the app bar hidden. (Most of the metrication lands in
  the companion *Launchpad KPI (AU)* resource, which is where the instrument tags live.)
  That includes the charts: the Time Series Chart's `dateFormat`, `timeFormat` and
  `timeAxis.tick.label.format` all default to US forms (`M-D-YYYY`, `h:mm A`, and an
  `Auto` tick format that is always 12-hour), and all three are set here. The Line
  View's tick format is *bound to the selected interval* — `HH:mm` for Hour,
  `DD/MM HH:mm` for Shift, `DD/MM` for Day — because one fixed format cannot serve a
  chart whose range runs from Yesterday to Last 365 Days.
- **The session timezone follows the client.** `timeZoneId` is empty, which is the
  component's own default. Set it explicitly on the gateway only if you want to pin
  every session to one zone regardless of who opens it.
- **A shift roster that actually covers the day.** The original ships three shifts
  **disabled**, spanning 09:00–21:30 with a 12-hour hole. This one runs a standard
  3 × 8h roster — **22:00–06:00, 06:00–14:00, 14:00–22:00** — enabled on all seven
  lines, and the seeded history matches those boundaries.
- **A flat tag layout.** `[Launchpad]OEE/…` rather than
  `[Launchpad]Exchange/Launchpad/Oee/…`. Shorter paths, and the folder is `OEE` in
  capitals throughout.
- **An installer endpoint** so the one-time setup can be driven without opening a
  Designer (see *Custom Instructions* above).

## Bugs fixed in the original resource

Both were in the original resource:

1. **Shifts crossing midnight were dated a day early.** `Schedule/CurrentShiftStartTime`
   unconditionally did `addDays(now(), -1)` for any shift where `StartTime > StopTime`.
   That is right *after* midnight and wrong *before* it, so for the whole pre-midnight
   half of a night shift the start time was a day out and the shift's elapsed and
   target figures disagreed. The original avoids the problem by shipping shifts that
   never cross midnight — which is also why they ship disabled. Now conditional on the
   current time of day.
2. **OEE could exceed 100%.** `Performance` is `ProductionCount / TargetProductionCount`
   with nothing clamping it, so an interval that had only just rolled over — or a line
   running above its target rate — reported over 100%; a counter reset could produce
   figures in the thousands. Availability, Performance and Utilisation are now capped
   at 1. The demo-history generator had the same flaw and is capped too.

Three smaller fixes: the overview's wide layout had no scroll, so on a laptop-height
window lines 5–7 were unreachable; the OEE UDT's `formatString` was `##.0%`, where
`##` makes the leading digit optional — so any figure under 1% rendered as `.0%` rather
than `0.0%`; and the Production Summary's run-time column header read `Runime`.

## Notes

- The demo lines are memory tags driven by two tag event scripts under
  `OEE/Demo/Sim`; there is no device to configure.
- Shortly after midnight the Line View's charts look nearly empty. That is honest —
  the default window is the current day, and the chart drops the still-running
  interval, so in the first hour or two there is little to draw.

## Licence

MIT — see `LICENSE`. The original Launchpad resource is the property of Inductive
Automation; this is a derivative port published in the same spirit.
