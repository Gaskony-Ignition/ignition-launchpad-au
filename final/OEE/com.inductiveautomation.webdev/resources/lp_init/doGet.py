def doGet(request, session):
	"""One-shot maintenance endpoint for the Launchpad OEE example.

	GET /system/webdev/OEE/lp_init?action=initDemoTags
	Actions: setupShifts | seedHistory | initDemoTags | resetDemoTags | initTables | diag | intervals | status
	Delete this resource before publishing the portable Exchange package.
	"""
	action = request["params"].get("action", "status")
	out = {"action": action}
	try:
		if action == "initDemoTags":
			exchange.launchpad.oee.initDemoTags()
			out["ok"] = True
		elif action == "resetDemoTags":
			exchange.launchpad.oee.resetDemoTags()
			out["ok"] = True
		elif action == "intervals":
			out["intervals"] = _allIntervals()
			out["ok"] = True
		elif action == "setupShifts":
			out["result"] = _setupShifts()
			out["ok"] = True
		elif action == "seedHistory":
			out["result"] = _seedHistory()
			out["ok"] = True
		elif action == "diag":
			out["diag"] = _diag()
			out["ok"] = True
		elif action == "initTables":
			# initTables issues bare CREATE UNIQUE INDEX and a seed INSERT, so a second
			# run throws half-way through and leaves the schema partly built.
			done = system.db.runScalarQuery(
				"SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' "
				"AND name = 'ex_launchpad_oee_shift'", database="Examples")
			if done:
				out["skipped"] = "OEE tables already present"
			else:
				exchange.launchpad.oee.initTables()
				out["created"] = True
			out["ok"] = True
		else:
			lines = exchange.launchpad.oee.getLineNames("[Launchpad]OEE/Demo")
			paths = []
			for ln in lines:
				for leaf in ["Display/OEE", "Display/Availability", "Plc/State", "ShiftOee/O", "Enabled"]:
					paths.append("[Launchpad]OEE/Demo/%s/%s" % (ln, leaf))
			vals = system.tag.readBlocking(paths)
			out["lines"] = lines
			out["tags"] = dict(zip(paths, ["%s (%s)" % (v.value, v.quality) for v in vals]))
			out["ok"] = True
	except:
		import traceback
		out["ok"] = False
		out["error"] = traceback.format_exc()
	return {"json": out}


def _diag():
	DB = "Examples"
	out = {}
	# what does the OEE engine currently hold for line 1?
	base = "[Launchpad]OEE/Demo/Line 1"
	leaves = ["ShiftOee/O","ShiftOee/A","ShiftOee/P","ShiftOee/Q","ShiftOee/U",
		"ShiftOee/RunSeconds","ShiftOee/SecondsElapsed","ShiftOee/ProductionCount",
		"ShiftOee/TargetProductionCount","ShiftOee/StartTime","ShiftOee/StartCounter",
		"ShiftOee/Duration","Plc/ProductionCounter","Plc/State",
		"Schedule/CurrentShift","Schedule/CurrentShiftStartTime","Config/TargetRate"]
	paths = ["%s/%s" % (base, l) for l in leaves]
	vals = system.tag.readBlocking(paths)
	out["line1"] = dict(zip(leaves, [str(v.value) for v in vals]))
	trh = system.tag.readBlocking(["%s/ShiftOee/TargetRateHistory" % base])[0].value
	if trh is not None:
		out["targetRateHistory"] = [[str(trh.getValueAt(r, c)) for c in range(trh.columnCount)]
			for r in range(trh.rowCount)]
		out["trhCols"] = list(trh.columnNames)
	# history coverage for the KPI chart tags
	out["hist"] = _histCoverage(DB)
	out["nowMs"] = str(system.date.toMillis(system.date.now()))
	# do the OEE named queries return anything?
	stop = system.date.now()
	start = system.date.addHours(stop, -24)
	try:
		r = system.db.runNamedQuery("OEE", "Exchange/Launchpad/Oee/HourlyStats",
			{"line_name": "Line 1", "tag_folder": "[Launchpad]OEE/Demo",
			 "start_time": start, "stop_time": stop})
		out["hourlyStatsRows"] = r.rowCount
	except:
		import traceback
		out["hourlyStatsError"] = traceback.format_exc()[-500:]
	return out


def _setupShifts():
	"""Enable a standard 3 x 8h roster on every demo line.

	Times are HHMM ints. At least one shift must be enabled: with none
	enabled CurrentShift = 0 and the whole ShiftOee branch is degenerate
	(elapsed 0, target 0, so Performance divides by zero).
	This roster matches the shift boundaries the seeded history uses.
	"""
	SHIFTS = [(1, 2200, 600), (2, 600, 1400), (3, 1400, 2200)]
	lines = exchange.launchpad.oee.getLineNames("[Launchpad]OEE/Demo")
	paths, values = [], []
	for ln in lines:
		base = "[Launchpad]OEE/Demo/%s/Schedule" % ln
		for num, start, stop in SHIFTS:
			paths.append("%s/%d/StartTime" % (base, num)); values.append(start)
			paths.append("%s/%d/StopTime" % (base, num)); values.append(stop)
			paths.append("%s/%d/ShiftEnabled" % (base, num)); values.append(True)
	system.tag.writeBlocking(paths, values)
	return {"lines": lines, "tagsWritten": len(paths)}


def _seedHistory():
	"""Rebuild the OEE shift/hour tables using the example's own generator.

	Going through makeHistory (rather than inserting rows from outside) keeps the
	timestamp binding identical to what the named queries bind at read time --
	hand-written text timestamps do not compare equal against bound Dates.
	"""
	DB = "Examples"
	system.db.runUpdateQuery("DELETE FROM ex_launchpad_oee_shift", database=DB)
	system.db.runUpdateQuery("DELETE FROM ex_launchpad_oee_hour", database=DB)
	lines = exchange.launchpad.oee.getLineNames("[Launchpad]OEE/Demo")
	for ln in lines:
		exchange.launchpad.oee.makeHistory(ln)
	return {"lines": lines,
		"shiftRows": system.db.runScalarQuery("SELECT COUNT(*) FROM ex_launchpad_oee_shift", database=DB),
		"hourRows": system.db.runScalarQuery("SELECT COUNT(*) FROM ex_launchpad_oee_hour", database=DB)}


def _allIntervals():
	lines = exchange.launchpad.oee.getLineNames("[Launchpad]OEE/Demo")
	paths, keys = [], []
	for ln in lines:
		for iv in ("DayOee", "ShiftOee", "HourOee"):
			for leaf in ("O", "A", "P", "Q", "U"):
				paths.append("[Launchpad]OEE/Demo/%s/%s/%s" % (ln, iv, leaf))
				keys.append("%s|%s|%s" % (ln, iv, leaf))
	vals = system.tag.readBlocking(paths)
	out = {}
	for k, v in zip(keys, vals):
		ln, iv, leaf = k.split("|")
		out.setdefault(ln, {}).setdefault(iv, {})[leaf] = (
			round(v.value, 4) if isinstance(v.value, (int, float)) else str(v.value))
	return out

def _histCoverage(DB):
	"""Row counts for a few KPI history tags, from THIS gateway's current partition.

	The partition name encodes a historian driver id and a month
	(sqlt_data_<drvid>_<yyyy>_<mm>). Neither is safe to compose: the driver id is not
	always 1, and the historian allocates a new one whenever the gateway's system name
	changes. Look up what exists instead -- a composed name is either a missing table
	or, worse, a retired generation that reads as healthy while the charts show nothing.
	"""
	sysName = system.tag.readBlocking(["[System]Gateway/SystemName"])[0].value
	drv = system.db.runPrepQuery("SELECT id FROM sqlth_drv WHERE lower(name) = ?",
		[sysName.lower()], database=DB)
	drvIds = [r["id"] for r in drv]
	if not drvIds:
		return [["(no historian driver for %s)" % sysName, "0"]]
	nowMs = system.date.toMillis(system.date.now())
	part = None
	for r in system.db.runQuery(
			"SELECT pname, drvid, start_time, end_time FROM sqlth_partitions", database=DB):
		if r["drvid"] in drvIds and r["start_time"] <= nowMs < r["end_time"]:
			part = r["pname"]; break
	if part is None:
		return [["(no history partition covers now)", "0"]]
	rows = system.db.runQuery(
		"SELECT te.tagpath, COUNT(*) n, MIN(d.t_stamp) mn, MAX(d.t_stamp) mx "
		"FROM sqlth_te te JOIN %s d ON d.tagid = te.id "
		"WHERE te.tagpath IN ('kpi/dailyproduction','kpi/dailyproductionexpected',"
		"'kpi/airpressure') GROUP BY te.tagpath" % part, database=DB)
	return [[str(c) for c in r] for r in rows]
