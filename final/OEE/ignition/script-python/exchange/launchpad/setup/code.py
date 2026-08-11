"""Build this gateway from nothing, from a button in the running session.

Everything a fresh gateway needs that is not the project itself: the database
connection, the tag provider, the historian, the simulator device and its programme,
the gateway scripting project, the tags, and then the seeding. All of it is reachable
from gateway scope, so none of it needs a Designer, an SSH session or a curl loop.

Two entry points:

    run(progress=None, force=False)   build everything that is missing
    check()                           report what is and is not in place, change nothing

Both are idempotent. `run` creates only what is absent unless `force` is set; `check`
writes nothing at all. The WebDev endpoint and the Setup button both call these, so
there is one implementation and not two that drift.

A note on the database. These projects ship SQLite at ${data}/Examples.db on purpose:
the schema is SQLite DDL, and a self-contained demo should not need a database server.
A SQLite connection needs no credentials, which is why setup can create it outright
rather than asking. If you want the demo on Postgres or MSSQL you need portable DDL
first -- pointing it at an existing connection is not enough, and the failure would be
a half-built schema rather than a clean error.
"""
import os
import traceback

LOG = system.util.getLogger("launchpad.setup")

RESOURCES = "data/config/resources"
CORE = "core/ignition"
HISTORIAN_MODULE = "core/com.inductiveautomation.historian"
OPCUA_MODULE = "core/com.inductiveautomation.opcua"

DATABASE = "Examples"
PROVIDER = "launchpad"
HISTORIAN = "launchpad"
DEVICE = "Launchpad"
SCRIPTING_PROJECT = "OEE"


def _isOee():
    """Which of the two projects this copy is running in.

    This file is byte-identical in OEE and in KPI on purpose -- two copies of a
    gateway builder drift, and the half that drifts is the half nobody runs. The
    project-specific parts are the seeding steps and the tag probe, and both are
    decided here rather than by maintaining two files.
    """
    return hasattr(exchange.launchpad, "oee")


def _lib():
    return exchange.launchpad.oee if _isOee() else exchange.launchpad.init


def _db():
    return _lib().db()


def _probeTag():
    """A tag that only exists once this project's tags are imported.

    Distinguishes "tags present" from "provider exists but empty", which look
    identical if you only browse the provider root.
    """
    if _isOee():
        return "[%s]OEE/Demo/Line 1/Enabled" % PROVIDER
    return "[%s]KPI/Lines/Line1/ProductionRate" % PROVIDER


# --------------------------------------------------------------- small helpers

def _emit(progress, message):
    LOG.info(message)
    if progress is not None:
        try:
            progress(message)
        except:
            pass  # a broken progress sink must never fail the install


def _abs(rel):
    from java.io import File
    return File(rel).getAbsolutePath()


def _write(path, content, binary=False):
    f = open(path, "wb" if binary else "w")
    try:
        f.write(content)
    finally:
        f.close()


def _read(path):
    f = open(path)
    try:
        return f.read()
    finally:
        f.close()


def _stamp():
    return system.date.format(system.date.now(), "yyyy-MM-dd'T'HH:mm:ss'Z'")


def _resourceJson(files, description):
    from java.util import UUID
    return system.util.jsonEncode({
        "scope": "A",
        "description": description,
        "version": 1,
        "restricted": False,
        "overridable": True,
        "files": files,
        "attributes": {
            "uuid": str(UUID.randomUUID()),
            "enabled": True,
            "lastModification": {"actor": "launchpad-setup", "timestamp": _stamp()},
        },
    })


def _configResource(module, kind, name, config, description, extra=None):
    """Write a gateway config resource. Returns the directory it landed in.

    `extra` is a list of (filename, content, binary) for resources that carry more
    than config.json -- the simulator device carries its programme alongside it, and
    a resource.json that does not list every file makes the gateway ignore the lot.
    """
    d = os.path.join(_abs(RESOURCES), module, kind, name)
    if not os.path.exists(d):
        os.makedirs(d)
    files = ["config.json"]
    _write(os.path.join(d, "config.json"), system.util.jsonEncode(config))
    for fname, content, binary in (extra or []):
        files.append(fname)
        _write(os.path.join(d, fname), content, binary)
    _write(os.path.join(d, "resource.json"), _resourceJson(files, description))
    return d


def _configScan():
    """Register config resources written above.

    This is NOT the project scan. The gateway has two identically labelled "Scan File
    System" buttons and running the wrong one does nothing at all, silently -- so this
    goes through the configuration manager, not system.project.requestScan().
    """
    from com.inductiveautomation.ignition.gateway import IgnitionGateway
    cm = IgnitionGateway.get().getConfigurationManager()
    before = str(cm.getScanInformation())
    cm.requestScan()
    # requestScan is ASYNCHRONOUS. Anything that depends on the scan having finished
    # -- restarting the tag provider, reading a tag that was just written -- acts on
    # the state from before the scan unless it waits for the reading to move. That is
    # the whole reason the second project's tags appeared to need a human to press
    # Scan File System: the scan was fine, the code just did not wait for it.
    # (scanSynchronous is not the synchronous form of this; it takes a Runnable to
    # run under the scan lock.)
    _waitFor(lambda: str(cm.getScanInformation()) != before, 90, 1)
    return True


def _waitFor(test, seconds=60, interval=2):
    """Poll until `test()` is true. Returns whether it became true.

    A fixed sleep is the usual way this is written and it is wrong in both directions:
    too short on a loaded gateway, and needlessly slow on a quick one.
    """
    from java.lang import Thread
    waited = 0
    while waited < seconds:
        try:
            if test():
                return True
        except:
            pass
        Thread.sleep(interval * 1000)
        waited += interval
    try:
        return bool(test())
    except:
        return False


# --------------------------------------------------------------- state probes

def databaseReady(name=None):
    """Whether the connection exists AND answers. Existing but faulted reads as no."""
    try:
        system.db.runScalarQuery("SELECT 1", database=(name or _db()))
        return True
    except:
        return False


def providerReady():
    """Whether the tag provider exists.

    Not a browse: system.tag.browse against a provider that does not exist returns an
    empty result rather than raising, so a browse-based probe reports every bare
    gateway as healthy. The config resource on disk is the thing that actually
    determines whether the provider is there.
    """
    return os.path.exists(os.path.join(
        _abs(RESOURCES), CORE, "tag-provider", PROVIDER))


def tagsPresent():
    try:
        return bool(system.tag.exists(_probeTag()))
    except:
        return False


def tagReading():
    """Whether the probe tag has a good value, not merely a definition.

    Imported tags exist immediately; they only carry values once the device is
    running and the scan class has ticked. The difference matters because a seeder
    that centres its generated band on the live value silently skips every tag that
    reads null -- reporting success while writing nothing.
    """
    try:
        paths = [_probeTag()]
        if _isOee():
            # Enabled being good says the tags installed; it says nothing about whether
            # the demo is actually running. A null production counter stops the
            # simulator script dead for every line while every other probe here stays
            # green -- so the counter is part of the probe, not just the definition.
            paths.append("[%s]OEE/Demo/Line 1/Plc/ProductionCounter" % PROVIDER)
        vals = system.tag.readBlocking(paths)
        qv = vals[0]
        out = {"quality": str(qv.quality), "value": str(qv.value),
               "ok": bool(qv.quality.isGood() and qv.value is not None)}
        if len(vals) > 1:
            cv = vals[1]
            out["productionCounter"] = str(cv.value)
            if cv.value is None:
                out["ok"] = False
                out["note"] = "the production counter has no value - the demo is not running"
        return out
    except:
        return {"ok": False}


def historianReady():
    return os.path.exists(os.path.join(
        _abs(RESOURCES), HISTORIAN_MODULE, "historian-provider", HISTORIAN))


def deviceState():
    """The simulator's connection state, or None if the gateway has no such device.

    "Exists" is not the same as "connected": a device that is present but faulted
    leaves every OPC tag stale, which reads downstream as an empty historian rather
    than as a device problem.
    """
    try:
        devices = system.device.listDevices()
        for row in range(devices.getRowCount()):
            if devices.getValueAt(row, "Name") == DEVICE:
                return str(devices.getValueAt(row, "State"))
    except:
        pass
    return None


def deviceReady():
    # a simulator reports Running, a real driver reports Connected -- both are healthy,
    # and only Connected would report every working simulator as broken
    return deviceState() in ("Connected", "Running")


def scriptingProject():
    """The gateway's configured scripting project, or None if it cannot be read."""
    try:
        p = os.path.join(_abs(RESOURCES), CORE, "system-properties", "config.json")
        return system.util.jsonDecode(_read(p)).get("gatewayScriptingProject")
    except:
        return None


def tablesPresent():
    """Whether this project's own tables exist.

    tableExists goes through the gateway's metadata provider, so it answers for any
    connection type -- a "SELECT FROM sqlite_master" probe throws on Postgres and
    reports a healthy gateway as broken.
    """
    try:
        from com.inductiveautomation.ignition.gateway import IgnitionGateway
        from com.inductiveautomation.ignition.common.db.schema import TableType
        want = "ex_launchpad_oee_shift" if _isOee() else "ex_lp_dashboards"
        tables = IgnitionGateway.get().getDatasourceManager().getMetaProvider() \
            .getTables(_db(), TableType.Table)
        return want in tables
    except:
        return False


def historyRows(withinHours=24):
    """How many history rows land inside the last `withinHours`.

    Counting against a BOUND date rather than reading MAX() back and converting it:
    the timestamp columns come back from the driver as whatever it feels like (the
    OEE hour table declares utc_timestamp INTEGER and the generator writes Dates into
    it), so any probe that parses a returned timestamp reports a healthy gateway as
    empty. Binding a Date into the comparison is the same path the named queries use
    at read time, and it is the thing that actually has to work.
    """
    try:
        since = system.date.addHours(system.date.now(), -withinHours)
        if _isOee():
            return system.db.runScalarPrepQuery(
                "SELECT COUNT(*) FROM ex_launchpad_oee_hour WHERE hour_timestamp >= ?",
                [since], database=_db())
        drvIds = exchange.launchpad.init._driverIds()[1]
        total = 0
        # _partitions returns tuples of (name, startMs, endMs), not dicts
        for name, startMs, endMs in exchange.launchpad.init._partitions(drvIds):
            total += system.db.runScalarPrepQuery(
                "SELECT COUNT(*) FROM %s WHERE t_stamp >= ?" % name,
                [system.date.toMillis(since)], database=_db())
        return total
    except:
        return None


def shiftsEnabled():
    """A roster that covers the day is what stops Performance dividing by zero."""
    try:
        if not _isOee():
            return True  # the roster belongs to OEE; KPI has no shifts of its own
        lines = exchange.launchpad.oee.getLineNames("[%s]OEE/Demo" % PROVIDER)
        if not lines:
            return False
        # ShiftEnabled, not Enabled: the line itself has an Enabled tag, and reading
        # that one instead reports a roster that was never written as healthy
        paths = ["[%s]OEE/Demo/%s/Schedule/1/ShiftEnabled" % (PROVIDER, lines[0])]
        qv = system.tag.readBlocking(paths)[0]
        return bool(qv.quality.isGood() and qv.value)
    except:
        return False


# --------------------------------------------------------------- build steps

def ensureDatabase(force=False):
    """Create the SQLite connection the projects are written against.

    No credentials are involved, which is the whole reason this can be automated: a
    Postgres or MSSQL connection would need a password nobody can supply from here.
    """
    if databaseReady(DATABASE) and not force:
        return "already connected"
    _configResource(CORE, "database-connection", DATABASE, {
        "connectURL": "jdbc:sqlite:${data}/%s.db" % DATABASE,
        "connectionProps": "", "connectionResetParams": "",
        "defaultTransactionLevel": "DEFAULT", "driver": "SQLite",
        "evictionRate": -1, "evictionTests": 3, "evictionTime": 1800000,
        "failoverMode": "STANDARD", "failoverProfile": "",
        "includeSchemaInTableName": False,
        "poolInitSize": 0, "poolMaxActive": 8, "poolMaxIdle": 8, "poolMaxWait": 5000,
        "poolMinIdle": 0, "slowQueryLogThreshold": 60000,
        "testOnBorrow": True, "testOnReturn": False, "testWhileIdle": False,
        "translator": "SQLITE", "username": "",
        "validationQuery": "SELECT 1", "validationSleepTime": 10000,
    }, "SQLite database for the Launchpad OEE + KPI example resources")
    return "created"


def ensureTagProvider(force=False):
    if providerReady() and not force:
        return "already present"
    config = exchange.launchpad.payload.tagProvider()
    config["settings"]["defaultDatasourceName"] = DATABASE
    _configResource(CORE, "tag-provider", PROVIDER, config,
                    "Tag provider for the Launchpad OEE + KPI example resources")
    return "created"


def ensureHistorian(force=False):
    if historianReady() and not force:
        return "already present"
    config = exchange.launchpad.payload.historian()
    config["settings"]["database"] = DATABASE
    _configResource(HISTORIAN_MODULE, "historian-provider", HISTORIAN, config,
                    "Tag historian for the Launchpad OEE + KPI example resources")
    return "created"


def ensureDevice(force=False):
    """The programmable simulator, including its programme.

    Without the programme every KPI tag reads stale -- the device exists, the tags
    resolve, and nothing ever changes, which looks like a broken historian.
    """
    if deviceReady() and not force:
        return "already present"
    _configResource(OPCUA_MODULE, "device", DEVICE,
                    exchange.launchpad.payload.device(),
                    "Programmable simulator driving the Launchpad example tags",
                    extra=[("instructions.csv",
                            exchange.launchpad.payload.instructions(), True)])
    return "created"


def ensureScriptingProject(force=False):
    """Point the gateway's scripting project at OEE.

    The OEE UDT event scripts call exchange.launchpad.oee.* and resolve it from this
    setting. Until it is right nothing computes, every OEE figure sits at zero, and
    the gateway logs nothing to say why -- it is the single most confusing way for
    this resource to be broken.

    Two things it will not do. It will not point the gateway at OEE when OEE is not
    installed -- KPI has no tag-scope scripts and does not need this at all. And it
    will not take the setting off another project: this is a gateway-wide setting, so
    on a gateway that already uses it for something else, silently claiming it would
    break that other project's tag events. Both cases are reported, not performed.
    """
    if scriptingProject() == SCRIPTING_PROJECT and not force:
        return "already %s" % SCRIPTING_PROJECT
    if not os.path.exists(os.path.join(_abs("data/projects"), SCRIPTING_PROJECT)):
        return "not needed - the %s project is not installed" % SCRIPTING_PROJECT
    current = scriptingProject()
    if current and current != SCRIPTING_PROJECT and not force:
        return ("left alone - this gateway already uses '%s'; set it to %s by hand if "
                "the OEE demo is meant to own it" % (current, SCRIPTING_PROJECT))
    d = os.path.join(_abs(RESOURCES), CORE, "system-properties")
    cfgPath = os.path.join(d, "config.json")
    if not os.path.exists(cfgPath):
        return "system-properties resource missing - set it by hand"
    cfg = system.util.jsonDecode(_read(cfgPath))
    cfg["gatewayScriptingProject"] = SCRIPTING_PROJECT
    _write(cfgPath, system.util.jsonEncode(cfg))
    # rewrite the sibling resource.json in place: it carries attributes we did not
    # write and must not lose, and a stale signature makes the scan skip the file
    resPath = os.path.join(d, "resource.json")
    if os.path.exists(resPath):
        res = system.util.jsonDecode(_read(resPath))
        attrs = res.get("attributes", res)
        if "lastModificationSignature" in attrs:
            del attrs["lastModificationSignature"]
        attrs["lastModification"] = {"actor": "launchpad-setup", "timestamp": _stamp()}
        _write(resPath, system.util.jsonEncode(res))
    return "set to %s" % SCRIPTING_PROJECT


def ensureTags(force=False):
    """Install the tags as gateway config resources, then scan them in.

    Deliberately NOT system.tag.configure. The runtime API looks tidier and cost a
    day: configuring a subtree at the provider root takes the provider's other
    subtrees with it, so installing KPI's tags silently removed OEE's -- on disk the
    definitions were still there, at runtime every path read Bad_NotFound. Writing
    the resource files and running a config scan is what the shell installer has
    always done, and it composes: each project installs only its own paths.

    UDT types come along in the same tree, under tag-type-definition rather than
    tag-definition, which is what puts them in the type namespace instead of leaving
    a tag folder literally called _types_ and every instance typeless.
    """
    if tagsPresent() and not force:
        return "already present"
    base = os.path.join(_abs(RESOURCES), CORE)
    written = 0
    for rel, text in exchange.launchpad.payload.tagFiles().items():
        dest = os.path.join(base, *rel.split("/"))
        parent = os.path.dirname(dest)
        if not os.path.exists(parent):
            os.makedirs(parent)
        _write(dest, text)
        written += 1
    # Scan, then wait, then scan again if needed. requestScan does pick these up --
    # verified with a throwaway nested tag folder -- but it is asynchronous and a
    # request made while the gateway is still working through the previous scan does
    # nothing at all. That is exactly the second project's situation: its setup runs
    # moments after the first one's, so a single fire-and-hope scan is the difference
    # between "tags imported" and "tags sitting on disk reading Bad_NotFound".
    for attempt in range(6):
        _configScan()
        if _waitFor(tagsPresent, 20, 2):
            return "installed %d resources" % written
    raise Exception("tags did not appear at %s after %d scans" % (_probeTag(), 6))
    return "installed %d resources" % written


def run(progress=None, force=False, history=True, tags=False):
    """Create everything that is missing and return a report of what changed."""
    report = {}

    def step(name, fn, message):
        _emit(progress, message)
        try:
            report[name] = fn()
        except:
            report[name] = "FAILED"
            report.setdefault("errors", []).append(
                "%s: %s" % (name, traceback.format_exc().strip().split("\n")[-1]))
            LOG.warn("setup step %s failed: %s" % (name, traceback.format_exc()))

    step("database", lambda: ensureDatabase(force), "creating the database connection")
    step("tagProvider", lambda: ensureTagProvider(force), "creating the tag provider")
    step("historian", lambda: ensureHistorian(force), "creating the tag historian")
    step("device", lambda: ensureDevice(force), "creating the simulator device")
    step("scriptingProject", lambda: ensureScriptingProject(force),
         "setting the gateway scripting project")

    _emit(progress, "registering gateway resources")
    _configScan()
    if not _waitFor(lambda: databaseReady(DATABASE) and providerReady(), 90):
        report.setdefault("errors", []).append(
            "gateway resources did not come up within 90s - press Set up again")
        report["ok"] = False
        return report

    # Tags are NOT reinstalled by a plain force. Installing the resources over
    # themselves leaves the previous definition's tag event script subscribed as
    # well as the new one, so the simulator's counter runs twice per tick, then
    # three times, and the demo produces at a multiple of its target rate until the
    # gateway restarts. Removing the files first was tried and measured: it does not
    # drop the old subscription, it adds another. So pressing Setup again is always
    # safe, and reinstalling tags has to be asked for by name (tags=1) -- after
    # which the gateway wants a restart.
    step("tags", lambda: ensureTags(force and tags), "importing the tags")
    if not tagsPresent():
        # every seeding step below reads tags. Carrying on produces a page of
        # confusing downstream failures instead of the one that matters.
        report.setdefault("errors", []).append(
            "tags are not present - seeding skipped")
        report["ok"] = False
        _emit(progress, "tags did not import - stopping")
        return report

    _seed(step, report, progress, history)

    report["ok"] = "errors" not in report
    _emit(progress, "done" if report["ok"] else "finished with errors")
    LOG.info("setup complete: %s" % report)
    return report


def _seed(step, report, progress, history):
    """The part that differs between the two projects."""
    step("tables", _initTables, "creating the database tables")
    if not _isOee():
        if history:
            step("history", lambda: _freshHistory(progress), "seeding tag history")
        else:
            report["history"] = "skipped"
        return

    step("shifts", exchange.launchpad.oee.setupShifts, "writing the shift roster")
    if history:
        step("history", lambda: _freshHistory(progress), "generating demo history")
    else:
        report["history"] = "skipped"
    step("resetDemoTags", exchange.launchpad.oee.resetDemoTags, "zeroing the counters")

    # initDemoTags reads the current shift start, which the schedule expressions only
    # publish once they have ticked. Poll for it rather than sleeping a fixed 45s.
    _emit(progress, "waiting for the shift schedule to publish")
    _waitFor(_shiftStartPublished, 90)
    step("demoTags", exchange.launchpad.oee.initDemoTags, "seeding the demo counters")


def _backfillWhenReady(progress, attempts=10, waitSeconds=15, force=False):
    """Seed KPI history, once there is somewhere to put it.

    A sample can only be written where a history partition already exists, and the
    historian creates its first one when it first records. On a gateway built from
    nothing that is a minute away, so an immediate backfill reports "no partition
    covers the requested window" and seeds nothing -- a successful install with empty
    charts, which is the outcome this whole exercise exists to avoid.
    """
    from java.lang import Thread
    result = None
    for attempt in range(attempts):
        try:
            result = exchange.launchpad.init.backfill(force=force)
            if not result.get("error"):
                return result
            why = result["error"]
        except:
            # SQLite takes one writer at a time and the historian is recording while
            # this runs, so a bulk insert can lose the race. Retrying is right; failing
            # the install over a transient lock is not.
            why = traceback.format_exc().strip().split("\n")[-1]
            result = {"error": why}
        _emit(progress, "history not ready yet, retrying (%d/%d): %s"
              % (attempt + 1, attempts, why[:80]))
        Thread.sleep(waitSeconds * 1000)
    return result


def _freshHistory(progress, maxAgeHours=3):
    """Leave this gateway with history that runs up to now.

    Seeded history is a snapshot, not a subscription: it ends at the moment it was
    generated. A demo gateway that sat idle for a few days therefore has full, healthy,
    entirely historical tables -- and every chart and table whose window is "today"
    draws nothing. Since these projects are nearly always installed on a short-lived
    trial gateway that gets built, looked at, and thrown away, "seed it once at install
    and hope" is the wrong bargain: setup re-seeds whenever what is there has gone
    stale, and then verifies that it worked rather than assuming it.
    """
    existing = historyRows(maxAgeHours)
    if existing:
        return "already current (%d rows in the last %d hours)" % (existing, maxAgeHours)
    stale = historyRows(24 * 365)
    if stale:
        _emit(progress, "history stops short of now - regenerating it")
    if _isOee():
        result = exchange.launchpad.oee.seedHistory()
    else:
        # force: the existing samples stop where the last run left off and the window
        # has moved on since, so a non-forced pass leaves the recent end empty
        result = _backfillWhenReady(progress, force=bool(stale))
    if not historyRows(maxAgeHours):
        raise Exception("history still has no rows inside the last %d hours after "
                        "seeding" % maxAgeHours)
    return result


def _initTables():
    if tablesPresent():
        return "already present"
    if _isOee():
        exchange.launchpad.oee.initTables()
    else:
        exchange.launchpad.init.initDashboard()
    return "created"


def _shiftStartPublished():
    lines = exchange.launchpad.oee.getLineNames("[%s]OEE/Demo" % PROVIDER)
    if not lines:
        return False
    v = system.tag.readBlocking(
        ["[%s]OEE/Demo/%s/Schedule/CurrentShiftStartTime" % (PROVIDER, lines[0])])[0]
    return v.value is not None


def check():
    """Report what is and is not in place. Changes nothing."""
    report = {}

    def probe(name, fn):
        try:
            report[name] = fn()
        except:
            report[name] = "FAILED: %s" % traceback.format_exc().strip().split("\n")[-1]

    probe("database", lambda: {"name": DATABASE, "ok": databaseReady(DATABASE)})
    probe("tagProvider", lambda: {"name": PROVIDER, "ok": providerReady()})
    probe("historian", lambda: {"name": HISTORIAN, "ok": historianReady()})
    probe("device", lambda: {"name": DEVICE, "state": deviceState(),
                             "ok": deviceReady()})
    probe("scriptingProject", lambda: {
        "is": scriptingProject(),
        # only OEE needs it; on a KPI-only gateway the setting is irrelevant
        "ok": (scriptingProject() == SCRIPTING_PROJECT
               or not os.path.exists(os.path.join(_abs("data/projects"), SCRIPTING_PROJECT)))})
    probe("tags", lambda: {"probe": _probeTag(), "ok": tagsPresent()})
    probe("tagValues", tagReading)
    probe("tables", lambda: {"ok": tablesPresent()})
    probe("shifts", lambda: {"ok": shiftsEnabled()})
    probe("history", _historyProbe)
    probe("project", lambda: {"is": system.project.getProjectName(),
                              "oee": _isOee(), "ok": True})

    report["ok"] = all(isinstance(v, dict) and v.get("ok", True)
                       for k, v in report.items() if k != "ok")
    return report


def detail(report):
    """One line per item, for a status label with room for more than a verdict.

    The one-line summary answers "is it ready"; this answers "what is missing", which
    is the question anyone actually has when the answer to the first one is no.
    """
    lines = []
    for name in sorted(report.keys()):
        if name in ("ok", "errors"):
            continue
        value = report[name]
        if isinstance(value, dict):
            state = "ok" if value.get("ok", True) else "MISSING"
            note = value.get("state") or value.get("is") or value.get("name") or ""
            lines.append("%s: %s%s" % (name, state, (" (%s)" % note) if note else ""))
        else:
            lines.append("%s: %s" % (name, str(value)[:70]))
    for err in report.get("errors", []):
        lines.append("error - %s" % err[:120])
    return "\n".join(lines + ["", summary(report)])


def _historyProbe():
    """Fresh, stale or absent -- "the tables exist" is not the same as "the charts
    have anything to draw", and only the second one is what anyone is asking."""
    rows = historyRows(24)
    if rows is None:
        return {"ok": False, "state": "could not be read"}
    if rows == 0:
        return {"ok": False, "state": "nothing in the last 24 hours - press Set up "
                                      "to regenerate it"}
    return {"ok": True, "state": "%d rows in the last 24 hours" % rows}


def summary(report):
    """One line a human can read, from either run() or check()."""
    if report.get("ok"):
        return "everything is in place"
    missing = [k for k, v in report.items()
               if isinstance(v, dict) and not v.get("ok", True)]
    if missing:
        return "not ready: %s" % ", ".join(sorted(missing))
    return "; ".join(report.get("errors", ["failed"]))
