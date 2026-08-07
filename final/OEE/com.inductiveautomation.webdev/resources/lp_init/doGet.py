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
	out["hist"] = system.db.runQuery(
		"SELECT te.tagpath, COUNT(*) n, MIN(d.t_stamp) mn, MAX(d.t_stamp) mx "
		"FROM sqlth_te te JOIN sqlt_data_1_2026_08 d ON d.tagid = te.id "
		"WHERE te.tagpath IN ('kpi/dailyproduction','kpi/dailyproductionexpected','kpi/airpressure') "
		"GROUP BY te.tagpath", database=DB)
	out["hist"] = [[str(c) for c in r] for r in out["hist"]]
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

	Times are HHMM ints. The stock Exchange resource ships all three shifts
	disabled, which leaves CurrentShift = 0 and the whole ShiftOee branch
	degenerate (elapsed 0, target 0, so Performance divides by zero).
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
