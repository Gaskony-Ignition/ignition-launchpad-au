# Launchpad KPI (AU)

An Australian port of the Inductive Automation **Launchpad KPI** Exchange resource.

A plant KPI overview, a configurable drag-and-drop dashboard, a trending screen and an
alarm view, over 61 simulated instrument tags across seven production lines. Everything
runs from a programmable simulator device; no PLC or field hardware is required.

Ignition **8.3.6** or later. Perspective, OPC-UA, SQL Historian and WebDev.

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
- **Dates DD/MM/YYYY and 24-hour time**, and the app bar hidden. Note that the built-in
  Time Series Chart and Power Chart draw their own axis labels and range footers in a
  fixed US format (`8-7-2026`, `3:03 AM`) which does not follow the session locale —
  that is the components' own rendering, not something the project sets.
- **Session `timeZoneId` ships as `UTC`.** Set it to your own zone
  (`Australia/Sydney`, and so on) on the target gateway; there is no single right value
  to ship, and leaving it at UTC will offset every displayed timestamp.
- **A flat tag layout.** `[Launchpad]KPI/…` rather than
  `[Launchpad]Exchange/Launchpad/…`, and the simulator's browse paths match, so the
  two stay in step.
- **Portable history paths.** The original's dashboard seed hard-coded a gateway name
  and project into every `histprov:` path, so the charts only resolved on the machine
  it was built on. They are now derived from the gateway's own system name at seed
  time.
- **An installer endpoint** so the one-time setup can be driven without opening a
  Designer (see *Custom Instructions*).

Conversions used: °F → °C as `(v − 32) × 5/9`, PSI → kPa as `v × 6.894757`. Ambient
air lands around 620–655 kPa and ambient temperature around 22 °C.

### One bug fixed along the way

**The history backfill wrote to the wrong table.** It composed the partition name as
`sqlt_data_1_<current month>`. Neither part is safe to assume: the `1` is a historian
driver id, and the historian allocates a new one whenever the gateway's system name
changes — so on any gateway that had ever been renamed, the seeded samples landed in a
retired partition the charts do not read, and every chart looked empty. The month was
equally fixed, so an install in any later month wrote to a table that need not exist.
It now resolves the current driver and looks the partition up in `sqlth_partitions`,
and reports anything that falls outside one rather than seeding a shorter window in
silence.

---

## Install

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

## Custom Instructions

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

### Notes

- The dashboard is editable from the running session: add, move and configure widgets
  from the ten in the catalogue, and dashboards persist to the `Examples` database.
- The `Placeholder` tag is deliberate — it is what a newly added widget points at
  until you choose a tag.

## Licence

MIT — see `LICENSE`. The original Launchpad resource is the property of Inductive
Automation; this is a derivative port published in the same spirit.
