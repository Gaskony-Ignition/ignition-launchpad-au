# Launchpad OEE + KPI — Australian port

Two Ignition 8.3 Perspective demonstration resources: **OEE** across seven simulated
production lines, and a plant **KPI** overview with a drag-and-drop dashboard.

## Why this exists

Both are ports of the Inductive Automation *Launchpad* Exchange resources, which are
built around US units and date conventions. This is a straight port to Australian
conventions — metric converted at source, DD/MM/YYYY, 24-hour time, a 3 × 8h shift
roster and a flat tag layout. Everything runs from a self-contained simulator. No PLC,
no OPC server, no field device.

## What it looks like

![OEE overview with all seven production lines](docs/images/oee-overview.png)
*OEE — seven lines, live Availability / Performance / Quality / Utilisation.*

![OEE line view](docs/images/oee-line-view.png)
*Line View — per-line OEE and production against target.*

![OEE production summary](docs/images/oee-production.png)
*Production Summary — every line, any period.*

![KPI overview](docs/images/kpi-overview.png)
*KPI — plant overview over 61 simulated instrument tags.*

![KPI dashboard](docs/images/kpi-dashboard.png)
*Dashboard — ten widget types, editable from the running session.*

![OEE Settings showing the Gateway setup card with Set up this gateway and Check buttons](docs/images/oee-setup.png)
*Settings — the whole install: import the project, press this.*

## What it does

- **OEE** across seven simulated production lines — Availability, Performance,
  Quality and Utilisation, computed per hour, per shift and per day, backed by a SQL
  history of shift and hourly statistics.
- **KPI** overview over 61 simulated instrument tags, with a drag-and-drop dashboard
  (ten widget types), a Trending screen and an Alarming view.
- Metric units converted at source, DD/MM/YYYY dates, 24-hour time and a 3 × 8h shift
  roster that covers the whole day — see *What "AU" changes* below.
- Self-contained: a programmable simulator device and a SQLite database ship with the
  packages, so nothing but Ignition itself is required.
- **A Setup button on each project's Settings screen** that builds the whole gateway —
  database, tag provider, historian, simulator, tags, tables, roster and demo history —
  and a Check button that reports what is in place.

## How to use it

Import the project and press a button.

1. **Import the project** — `Projects/OEE.zip` and/or `Projects/KPI.zip`. Either one
   installs on its own.
2. **Open its Settings screen** and press **Set up this gateway**.

That is the whole install. The button creates the `Examples` database, the `launchpad`
tag provider and historian, the simulator device *and its programme*, the tags and UDT
types, the tables, the shift roster and the demo history, and points the gateway
scripting project at OEE. It only creates what is missing, so pressing it twice is
safe, and **Check** beside it reports what is and is not in place without changing
anything.

Nothing needs to be imported separately — the tags ship inside the project. The
`Tags/` and `Gateway/` folders in each package are still there for anyone who would
rather bring the tags in through a Designer or drop the config resources in by hand,
but neither is needed for the route above.

Two things the button deliberately will not do, because they are not its call to make:
it will not touch a gateway scripting project that is already set to something else,
and it will not create a database connection other than its own SQLite `Examples` —
these projects are written against SQLite DDL, so pointing them at an existing Postgres
or MSSQL connection would half-build a schema rather than fail cleanly.

**Installing a fleet?** `tools/install.sh` does the same thing unattended over SSH for
a gateway you can reach the filesystem of. The button is the better route for one
gateway; the script is for many.

## What "AU" changes

This is a port, not a rewrite — the screens, the OEE engine and the UDT structure are
the original's.

- **Metric, converted at source.** The simulator generates °C and kPa and the tags carry
  metric `engUnit` and engineering ranges, so values, axis labels, sparkline legends,
  history and gauges all agree. A display-time conversion would not: anything reading
  the tag's own metadata still reports the stored unit.
- **DD/MM/YYYY and 24-hour time** through the projects' own labels, tables and date
  pickers, and through the Time Series and Power Chart components — whose `dateFormat`,
  `timeFormat` and tick formats are all set explicitly. The Line View's tick format is
  bound to the selected interval (`HH:mm` for Hour, `DD/MM HH:mm` for Shift, `DD/MM`
  for Day); the Power Charts keep `Auto` ticks, because the user drives their range
  anywhere from an hour to a year, with the unambiguous date in the footer and info box.
- **A 3 × 8h shift roster** — 22:00–06:00, 06:00–14:00, 14:00–22:00 — enabled on all
  seven lines, with the seeded history matching those boundaries.
- **A flat tag layout**, `[Launchpad]OEE/…` and `[Launchpad]KPI/…`, rather than
  `[Launchpad]Exchange/Launchpad/…`.
- **Portable history paths**, derived from the gateway's own system name rather than
  baked in — in the dashboard seed and in the Trending page's chart pens.
- **The session timezone follows the client.** `timeZoneId` is left empty, the
  component's own default. Set it on the gateway only if you want every session pinned
  to one zone regardless of who opens it.
- **A Setup button**, so a working demo is an import and one click rather than a
  five-step gateway configuration. The same thing is reachable as a WebDev endpoint for
  anyone scripting it.

## Licence

MIT — see `exchange/LICENSE`. The original Launchpad resources are the property of
Inductive Automation; this is a derivative port published in the same spirit.
