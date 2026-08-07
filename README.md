# Launchpad OEE + KPI — Australian port

Two Ignition 8.3 Perspective demonstration resources: **OEE** across seven simulated
production lines, and a plant **KPI** overview with a drag-and-drop dashboard.

## Why this exists

Both are ports of the Inductive Automation *Launchpad* Exchange resources, which ship
in US units, US date/time conventions, and a shift roster with a twelve-hour hole in
the day. This is a straight port to Australian conventions — metric converted at
source, DD/MM/YYYY, 24-hour time, a shift roster that covers the whole day, and a flat
tag layout — plus a handful of bugs fixed along the way. Everything runs from a
self-contained simulator. No PLC, no OPC server, no field device.

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
  history and gauges all agree. The original converted at display time only, which left
  the tags themselves reading `PSI` and `F`.
- **DD/MM/YYYY and 24-hour time** through the projects' own labels, tables, date
  pickers — and, now, the Time Series and Power Chart components too, whose date/time
  formats default to US forms and are explicitly set here. See *Presentation fixes*
  below.
- **A shift roster that covers the day.** The original ships three shifts *disabled*,
  spanning 09:00–21:30 with a twelve-hour hole. This runs a 3 × 8h roster —
  22:00–06:00, 06:00–14:00, 14:00–22:00 — enabled on all seven lines.
- **A flat tag layout**, `[Launchpad]OEE/…` and `[Launchpad]KPI/…`, rather than
  `[Launchpad]Exchange/Launchpad/…`.
- **Portable history paths**, derived from the gateway's own system name rather than
  baked in. The original hard-coded a gateway name into every `histprov:` path — in the
  dashboard seed *and* in the Trending page's chart pens.
- **Installer endpoints**, so the one-time setup can be driven without opening a Designer.

## Bugs fixed in the original resource

Found while getting these running; none were introduced by the Australian changes.

1. **Shifts crossing midnight were dated a day early.** `CurrentShiftStartTime`
   unconditionally did `addDays(now(), -1)` whenever `StartTime > StopTime` — correct
   after midnight, wrong before it. The original avoids the problem by shipping shifts
   that never cross midnight, which is also why they ship disabled.
2. **OEE could exceed 100%.** Nothing clamped `Performance`, so a just-rolled-over
   interval or a line running above target reported over 100%; a counter reset could
   produce figures in the thousands. A, P and U are now capped at 1.
3. **The Trending page only worked on the gateway it was built on.** Both Power Chart
   pen sources and the tag-browser path hard-coded a gateway system name, so anywhere
   else the pens read `Bad_NotFound` and the tag browser was empty. They now resolve
   from `[System]Gateway/SystemName`, the same way the project's popup views already
   did. This survived earlier testing because the development gateway still held a
   retired history generation under the old name, which made it look like it worked.
4. **The KPI history backfill wrote to the wrong table.** It composed the partition name
   as `sqlt_data_1_<this month>` — but the `1` is a historian driver id, not a constant,
   and the month is whatever month it is. On a gateway that had ever been renamed, or
   installed in any month other than the one it was written in, every seeded sample
   landed somewhere the charts do not read. It now resolves the driver and partition
   from the database.
5. **`##.0%` dropped the leading zero.** In an Ignition number-format pattern `#` is an
   optional digit, so anything under 1% rendered as `.0%`. The pattern lives on the OEE
   UDT, where every consumer reads it.
6. Smaller ones: the overview had no scroll at laptop height, so lines 5–7 were
   unreachable; the Production Summary column header read `Runime`; and the OEE
   project shipped `en-US` while KPI shipped `en-AU`.

## Presentation fixes

Small things, but the sort a demonstration resource is judged on:

- **The A / P / Q badges on each OEE bar no longer collide.** Each badge sits in a
  segment whose width is proportional to the *loss* for that component, so a line
  running at 100% got a zero-width segment — and its letter painted anyway, over its
  neighbours and off the card edge. The segments now clip to themselves, and a badge
  hides once its segment is too narrow to hold a glyph. The coloured segment still
  shows the loss either way; only the label goes.
- **Every chart renders DD/MM/YYYY and 24-hour time.** The Time Series and Power Chart
  do expose `dateFormat`, `timeFormat` and `timeAxis.tick.label.format` — the defaults
  are simply `M-D-YYYY`, `h:mm A` and an `Auto` tick format that is always 12-hour. All
  three are now set, along with the x-trace and annotation info boxes.
  The Line View's tick format is *bound to the selected interval* rather than fixed:
  `HH:mm` for Hour, `DD/MM HH:mm` for Shift, `DD/MM` for Day. A single fixed format
  cannot serve a chart whose range dropdown runs from Yesterday to Last 365 Days. The
  Power Charts keep `Auto` ticks for the same reason — the user drives their range to
  any span — while their footers and info boxes are fixed.
- **Session `timeZoneId` is no longer pinned.** It shipped as `UTC`, which was a value
  the development container had persisted, not a decision — and it offset every
  timestamp, including the shift boundaries, on any gateway that is not in UTC. It is
  now empty, the component's own default, so the session follows the client.

## One more bug this turned up

The Line View's chart transforms did `range(getRowCount() - 1)`, dropping the last row
**unconditionally**. That is right in Realtime, where the last row is the hour still in
progress and plotting a part-finished interval drags the line down for no reason. It is
wrong in Historical, where every row is a completed interval and the last one was being
silently discarded — a full day's chart quietly stopped an hour short. The transform
was branching on `view.custom.timeRange`, a property that does not exist on that view,
so the mode it thought it was checking was always `None`. It now reads the session's
display mode.

## Licence

MIT — see `exchange/LICENSE`. The original Launchpad resources are the property of
Inductive Automation; this is a derivative port published in the same spirit.
