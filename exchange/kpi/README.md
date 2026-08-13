# Launchpad KPI (AU)

An Australian port of the Inductive Automation **Launchpad KPI** Exchange resource.

## Why this exists

Inductive Automation's Launchpad KPI demo is a good showcase of a
configurable plant dashboard, but — like the companion OEE resource — it is
built around US units and formats. This is a straight port: metric converted
at the source (not just displayed), DD/MM/YYYY, 24-hour time, and history
paths that resolve on whatever gateway you install it on. Everything runs
from a programmable simulator device; no PLC or field hardware is required.

## What it looks like

![KPI overview across 61 simulated instrument tags](docs/images/kpi-overview.png)
*Overview — plant-wide production and instrument KPIs, realtime or historical.*

![KPI dashboard with editable widgets, gauges, sparklines and trend charts](docs/images/kpi-dashboard.png)
*Dashboard — ten widget types, add/move/configure from the running session.*

## What it does

- A plant KPI overview across **61 simulated instrument tags** on seven
  production lines.
- A **drag-and-drop dashboard** with ten widget types (gauges, sparklines,
  trend charts, KPI tiles and more), editable from the running session and
  persisted to the `Examples` database.
- A **Trending** screen and an **Alarming** view, both driven from the same
  tag set.
- Metric values converted **at the source** — the simulator generates °C and
  kPa, and the tags carry metric `engUnit` and engineering ranges, so values,
  axis labels, sparkline legends, history and gauges all agree.
- A **Setup button** on the Settings screen that builds the gateway this
  needs — database, tag provider, historian, simulator, tags, dashboard tables
  and 48 hours of history — plus Check, and re-seed/repair for afterwards.

## How to use it

### Install

1. **Import the project** — `Projects/KPI.zip`. On the gateway that is
   **Platform → Projects → Import Project**; the dialog asks for a name, and
   `KPI` is the one the rest of the package expects.
2. **Open Settings** in the running project and press **Set up this gateway**.

That is all of it. The button creates the `Examples` database, the `launchpad` tag
provider and historian, the programmable simulator device and its programme, the tags,
the dashboard tables and their seed data, and 48 hours of tag history. It narrates each
step as it goes, and creates only what is missing, so pressing it twice is safe.
**Check** beside it reports what is and is not in place and changes nothing.

The tags ship inside the project, so there is nothing to import separately. `Tags/` and
`Gateway/` are still in the package for anyone who would rather bring the tags in
through a Designer or drop the config resources in by hand, but the button needs
neither.

If you are installing both packages, the tag provider, database, historian and
simulator are the same resources in each; whichever you set up second finds them
already there and moves on.

### Driving it without the UI

Everything the button does is also a WebDev call, for anyone scripting an install:

    GET /system/webdev/KPI/kpi_init?action=setup     build whatever is missing
    GET /system/webdev/KPI/kpi_init?action=check     report state, change nothing

The other actions the endpoint carries are listed in `docs/` in the repo. It ships
requiring authentication; log in first, or set `require-auth: false` on the resource
while you use it and then set it back.

### If you would rather not ship an HTTP endpoint

Delete the `kpi_init` resource. The Setup button does not go through it — it calls
`exchange.launchpad.setup.run()` directly — so removing the endpoint costs you the
scripted install and nothing else. From a Designer script console the same functions
are `exchange.launchpad.setup.run()` and `.check()`, or the individual steps
`exchange.launchpad.init.initDashboard()`, `.backfill()` and `.repairBackfill()`.

---

## What "AU" changes

This is a port, not a rewrite. The screens and the widget catalogue are the original's.
What differs:

- **Metric throughout, converted at source.** Temperatures in °C, pressures in kPa.
  The simulator generates metric values and the tags carry metric `engUnit` and
  engineering ranges, so the numbers, the axis labels, the sparkline legends, the
  history and the gauges all agree. (A display-time conversion would not: anything
  reading the tag's own metadata — the sparkline legend does — would still say PSI,
  and the trend charts would plot the raw stored value in °F.)
- **Dates DD/MM/YYYY and 24-hour time**, and the app bar hidden — the charts included.
  The Time Series Chart and Power Chart range footers and x-trace boxes are all set
  explicitly rather than left at their US defaults. The Power Charts keep the `Auto`
  tick format, because the user drives their range picker to any span and no single
  fixed format survives that; their footers and info boxes carry the unambiguous date.
- **The session timezone follows the client.** `timeZoneId` is empty, which is the
  component's own default. Set it explicitly on the gateway only if you want to pin
  every session to one zone regardless of who opens it.
- **A flat tag layout.** `[Launchpad]KPI/…` rather than
  `[Launchpad]Exchange/Launchpad/…`, and the simulator's browse paths match, so the
  two stay in step.
- **Portable history paths.** Every `histprov:` path — in the dashboard seed and in the
  Trending page's own chart pens — is derived from the gateway's own system name rather
  than baked in: the seed at seed time, the Trending pens through a binding on
  `[System]Gateway/SystemName`. Install it anywhere and the charts resolve.
- **A Setup button**, so a working demo is an import and one click rather than a
  five-step gateway configuration. The same thing is reachable as a WebDev endpoint
  for anyone scripting it.

Conversions used: °F → °C as `(v − 32) × 5/9`, PSI → kPa as `v × 6.894757`. Ambient
air lands around 620–655 kPa and ambient temperature around 22 °C.

## Notes

- The dashboard is editable from the running session: add, move and configure widgets
  from the ten in the catalogue, and dashboards persist to the `Examples` database.
- The `Placeholder` tag is deliberate — it is what a newly added widget points at
  until you choose a tag.

## Licence and attribution

This is a **derivative work**. The Launchpad KPI project is published by
**Inductive Automation** on the Ignition Exchange, and the original views, scripts and
tag structures are theirs. This package holds them in modified form -- metricated,
re-dated to Australian conventions, with a gateway setup builder and a number of
repairs added.

The MIT licence in `LICENSE` covers that added and changed work. It does not grant
rights to Inductive Automation's underlying work, and the original resource is not
redistributed here -- download it from the Exchange if you want it.

Ignition, Perspective and Launchpad are trademarks of Inductive Automation. This
project is not affiliated with or endorsed by them.
