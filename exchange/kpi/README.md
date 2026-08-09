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
- A WebDev installer endpoint that seeds the dashboard tables and 48 hours of
  tag history without opening a Designer.

## How to use it

### Install

1. **Gateway resources.** Create a tag provider named `launchpad`, a database
   connection named `Examples`, a tag historian named `launchpad` pointing at it, and
   a **Programmable Simulator** OPC device named `Launchpad`. `Gateway/` carries all
   four as 8.3 config resources if you would rather drop them in and run a
   **Config → Scan File System**. `Examples` is SQLite at `${data}/Examples.db` so the
   resource stays self-contained; point it at Postgres or MSSQL instead if you prefer.
2. **Simulator programme.** Load `Tags/launchpad-simulator.csv` into the `Launchpad`
   device. This is what gives every tag a value — without it the tags read stale.
3. **Project.** Import `Projects/KPI.zip`.
4. **Tags.** Import `Tags/launchpad-kpi-tags.json` into the `launchpad` provider.
5. **Seed the dashboard and history** — see below.

If you are installing this alongside *Launchpad OEE (AU)*, the tag provider, database
and historian are the same resources in both packages; whichever you install second is
a no-op for those three.

### Seeding

The project carries a WebDev endpoint, `kpi_init`. **It ships requiring
authentication**; either log in first or set `require-auth: false` on the resource
while you run these, then set it back.

    GET /system/webdev/KPI/kpi_init?action=<action>

| action | what it does |
|--------|--------------|
| `initDashboard` | creates the dashboard tables and seeds two example dashboards with 41 widgets |
| `backfill` | seeds 48 h of tag history so the charts and sparklines are not empty on day one |
| `repairBackfill` | moves mis-columned integer samples into `intvalue` |
| `status` | lists the dashboard tables — read-only |

Run `initDashboard`, then `backfill`. Both are idempotent; `initDashboard` issues bare
`CREATE TABLE` statements, so re-running the underlying script directly would throw
half-way, and the endpoint checks first and skips.

`backfill` takes `hours` (default 48), `step` in minutes (default 15) and `force=1`.
Use `force=1` to discard the existing samples and re-seed — worth doing if you rescale
a tag, so one series does not end up holding two different units.

Without the backfill nothing is broken; the charts simply fill in from live data over
the following hours.

### If you would rather not ship an HTTP endpoint

Delete the `kpi_init` resource and call `exchange.launchpad.init.initDashboard()` from
a Designer script console. There is no script equivalent for the history backfill —
let the charts populate from live data instead.

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
- **An installer endpoint** so the one-time setup can be driven without opening a
  Designer (see *Custom Instructions* above).

Conversions used: °F → °C as `(v − 32) × 5/9`, PSI → kPa as `v × 6.894757`. Ambient
air lands around 620–655 kPa and ambient temperature around 22 °C.

## Notes

- The dashboard is editable from the running session: add, move and configure widgets
  from the ten in the catalogue, and dashboards persist to the `Examples` database.
- The `Placeholder` tag is deliberate — it is what a newly added widget points at
  until you choose a tag.

## Licence

MIT — see `LICENSE`. The original Launchpad resource is the property of Inductive
Automation; this is a derivative port published in the same spirit.
