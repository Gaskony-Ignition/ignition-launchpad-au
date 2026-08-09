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
- One-command installer, and WebDev endpoints that seed both projects' demo data
  without opening a Designer.

## How to use it

Two ways, both documented in full in each package's own README.

**Automated**, if you can reach the target's container — about four minutes unattended,
and idempotent:

```bash
tools/install.sh --container your-ignition-container \
                 --url http://your-gateway:9088 \
                 --gateway <credentials-stanza> [--ssh your-ssh-host]
```

**By hand**, from the packages: create the `launchpad` tag provider, the `Examples`
database and the `launchpad` historian; import the project; import the tags (UDT types
first); set the gateway scripting project; then run the seeding endpoints. The `Gateway/`
folder in each package carries those config resources if you would rather drop them in
and run a **Config → Scan File System**.

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
- **Installer endpoints**, so the one-time setup can be driven without opening a Designer.

## Licence

MIT — see `exchange/LICENSE`. The original Launchpad resources are the property of
Inductive Automation; this is a derivative port published in the same spirit.
