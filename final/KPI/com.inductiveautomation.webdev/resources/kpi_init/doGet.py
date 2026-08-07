def doGet(request, session):
	"""Installer endpoint for the Launchpad KPI example.

	GET /system/webdev/KPI/kpi_init?action=initDashboard

	The dashboard tables live in the same database as the OEE ones, but the script
	that creates them (exchange.launchpad.init) belongs to THIS project -- project
	script packages are not visible across projects, so OEE's lp_init cannot call it.

	Actions: initDashboard | backfill | repairBackfill | status
	"""
	action = request["params"].get("action", "status")
	out = {"action": action}
	DB = "Examples"
	try:
		if action == "initDashboard":
			# idempotent: the seed script issues bare CREATE TABLE, so re-running it
			# against a populated database would fail half-way and leave it torn.
			existing = system.db.runScalarQuery(
				"SELECT COUNT(*) FROM sqlite_master WHERE type = \'table\' AND name = \'ex_lp_dashboards\'",
				database=DB)
			if existing:
				out["skipped"] = "dashboard tables already present"
			else:
				exchange.launchpad.init.initDashboard()
				out["created"] = True
			out["dashboards"] = system.db.runScalarQuery(
				"SELECT COUNT(*) FROM ex_lp_dashboards", database=DB)
			out["widgets"] = system.db.runScalarQuery(
				"SELECT COUNT(*) FROM ex_lp_dashboard_widgets", database=DB)
			out["ok"] = True
		elif action == "backfill":
			hours = int(request["params"].get("hours", 48))
			step = int(request["params"].get("step", 15))
			force = request["params"].get("force") in ("1", "true", "yes")
			out.update(_backfill(hours, step, force))
			out["ok"] = "error" not in out
		elif action == "repairBackfill":
			out["result"] = _repairBackfill()
			out["ok"] = True
		else:
			tables = system.db.runQuery(
				"SELECT name FROM sqlite_master WHERE type = \'table\' AND name LIKE \'ex_lp_%\' ORDER BY name",
				database=DB)
			out["tables"] = [r["name"] for r in tables]
			out["ok"] = True
	except:
		import traceback
		out["ok"] = False
		out["error"] = traceback.format_exc()
	return {"json": out}

def _driverIds():
	"""The sqlth_drv ids belonging to THIS gateway.

	The historian keys everything on the gateway's system name, and keeps the old
	rows when that name changes -- so a database can hold several generations. A
	renamed gateway (or one reusing an Examples database) ends up with two entries
	per tag path and two sets of partitions, and only the current generation is
	what the charts read. Everything below filters on these ids.
	"""
	DB = "Examples"
	sysName = system.tag.readBlocking(["[System]Gateway/SystemName"])[0].value
	rows = system.db.runPrepQuery(
		"SELECT id FROM sqlth_drv WHERE lower(name) = ?", [sysName.lower()], database=DB)
	return sysName, [r["id"] for r in rows]

def _partitions(drvIds):
	"""This gateway's data partitions, as [(name, startMs, endMs)].

	Partition names encode a driver id and a month (sqlt_data_<drvid>_<yyyy>_<mm>),
	neither of which is safe to assume: the driver id is not always 1, and the month
	is whatever month it happens to be. The historian creates these as it writes, so
	we look up what actually exists rather than composing a name.
	"""
	if not drvIds:
		return []
	rows = system.db.runQuery(
		"SELECT pname, drvid, start_time, end_time FROM sqlth_partitions",
		database="Examples")
	return [(r["pname"], r["start_time"], r["end_time"])
		for r in rows if r["drvid"] in drvIds]

def _partitionFor(tsMs, parts):
	for name, start, end in parts:
		if start <= tsMs < end:
			return name
	return None

def _liveTagIds(drvIds):
	"""(tagid, tagpath, datatype) for the kpi tags of the current gateway generation."""
	DB = "Examples"
	if not drvIds:
		return {}
	marks = ",".join(["?"] * len(drvIds))
	# concatenated, not %-formatted: the SQL contains a literal 'kpi/%' wildcard and
	# %-formatting reads that % as the start of a format spec
	rows = system.db.runPrepQuery(
		"SELECT te.id AS id, te.tagpath AS tagpath, te.datatype AS datatype "
		"FROM sqlth_te te JOIN sqlth_scinfo sc ON te.scid = sc.id "
		"WHERE te.tagpath LIKE 'kpi/%' AND te.retired IS NULL "
		"AND sc.drvid IN (" + marks + ")", list(drvIds), database=DB)
	return [(r["id"], r["tagpath"], r["datatype"]) for r in rows]

def _backfill(hours, stepMinutes, force=False):
	"""Seed KPI tag history so the example charts have something to draw."""
	import math, random
	random.seed(7)
	DB = "Examples"
	sysName, drvIds = _driverIds()
	tags = _liveTagIds(drvIds)
	parts = _partitions(drvIds)
	now = system.date.now()
	nowMs = system.date.toMillis(now)
	stepMs = stepMinutes * 60 * 1000
	count = hours * 60 / stepMinutes
	startMs = nowMs - count * stepMs

	# a sample can only be written where a partition already exists; group the
	# timestamps by partition and report any that fall outside one, rather than
	# quietly seeding a shorter window than was asked for
	buckets = {}
	unpartitioned = 0
	for i in range(count):
		ts = int(startMs + i * stepMs)
		p = _partitionFor(ts, parts)
		if p is None:
			unpartitioned += 1
		else:
			buckets.setdefault(p, []).append(ts)
	if not buckets:
		return {"rows": 0, "gateway": sysName, "tags": len(tags),
			"error": "no history partition covers the requested window - "
				 "let the historian record for a minute, then retry"}

	if force:
		# re-seeding after a units change: the old samples are on the previous scale,
		# so drop them rather than leaving two scales mixed in one series
		ids = [t[0] for t in tags]
		if ids:
			marks = ",".join(["?"] * len(ids))
			for p in buckets:
				system.db.runPrepUpdate(
					"DELETE FROM %s WHERE tagid IN (%s)" % (p, marks), ids, database=DB)

	total = 0
	skipped = 0
	for tagid, path, datatype in tags:
		# datatype 0 = integer, 1 = float. An int tag reads back from intvalue; writing
		# its samples into floatvalue leaves intvalue NULL, which the chart plots as 0.
		isInt = (datatype == 0)
		# take the live value as the centre of the generated band
		live = system.tag.readBlocking(["[Launchpad]" + path])[0]
		base = live.value
		if base is None or isinstance(base, basestring):
			skipped += 1
			continue
		base = float(base)
		if base == 0.0:
			base = 1.0
		amp = abs(base) * 0.12
		if not force:
			seen = 0
			for p in buckets:
				seen += system.db.runScalarQuery(
					"SELECT COUNT(*) FROM %s WHERE tagid = ? AND t_stamp < ?" % p,
					database=DB, args=[tagid, startMs + stepMs])
			if seen > 0:
				skipped += 1
				continue
		col = "intvalue" if isInt else "floatvalue"
		for p, stamps in buckets.items():
			vals = []
			for ts in stamps:
				phase = (ts / 3600000.0) * (math.pi / 12.0)
				v = base + amp * math.sin(phase) + random.uniform(-amp * 0.35, amp * 0.35)
				vals.append((tagid, v, ts))
			# insert in chunks so one statement never gets absurdly long
			chunk = 200
			for s in range(0, len(vals), chunk):
				part = vals[s:s + chunk]
				sql = ("INSERT INTO %s (tagid, %s, dataintegrity, t_stamp) VALUES " % (p, col)
					+ ",".join(["(?,?,192,?)"] * len(part)))
				args = []
				for tid, v, ts in part:
					args.extend([tid, int(round(v)) if isInt else v, ts])
				system.db.runPrepUpdate(sql, args, database=DB)
				total += len(part)
	out = {"rows": total, "gateway": sysName, "tags": len(tags),
	       "partitions": sorted(buckets.keys()), "tagsSkipped": skipped}
	if unpartitioned:
		out["samplesOutsideAnyPartition"] = unpartitioned
	return out

def _repairBackfill():
	"""Move mis-columned samples for integer tags into intvalue.

	Only affects rows this endpoint's backfill wrote -- the historian itself always
	writes an int tag to intvalue, so no genuinely-recorded sample has a floatvalue.
	"""
	DB = "Examples"
	sysName, drvIds = _driverIds()
	nowMs = system.date.toMillis(system.date.now())
	p = _partitionFor(nowMs, _partitions(drvIds))
	if p is None:
		return {"rowsRepaired": 0, "error": "no current history partition"}
	n = system.db.runUpdateQuery(
		"UPDATE %s SET intvalue = CAST(floatvalue AS INTEGER), floatvalue = NULL "
		"WHERE floatvalue IS NOT NULL "
		"AND tagid IN (SELECT id FROM sqlth_te WHERE datatype = 0)" % p, database=DB)
	return {"rowsRepaired": n, "partition": p}
