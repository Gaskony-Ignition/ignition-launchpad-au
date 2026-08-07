#!/usr/bin/env python3
"""Convert the KPI example from imperial to metric at SOURCE.

The port previously converted at display time: four component views multiplied the
value and substituted the unit string, keyed off the tag name containing
"temperature" or "pressure". That left three things wrong:

  * the tags still carried engUnit 'PSI' / 'F', so the Sparkline legend -- which
    reads .engUnit directly -- labelled metric numbers as PSI;
  * the Trending page and every history chart plotted the raw stored value, i.e.
    Fahrenheit and PSI, while the tiles beside them read degC and kPa;
  * the rule was a substring match on the tag name, so it silently missed anything
    named differently and would double-convert a genuinely metric tag.

Converting the simulator output and the tag metadata instead makes the whole thing
metric end to end, and the display-time transforms are then removed (leaving them
would convert twice).

Dry-run by default; --apply to write.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__)) + "/.."
APPLY = "--apply" in sys.argv

F_TO_C = lambda v: (v - 32.0) * 5.0 / 9.0
PSI_TO_KPA = lambda v: v * 6.894757293168361

CSV = f"{ROOT}/live-config/device/Launchpad/instructions.csv"
TAGS = [f"{ROOT}/live-config/tag-definition/launchpad/KPI/tags.json"] + [
    f"{ROOT}/live-config/tag-definition/launchpad/KPI/Lines/Line{n}/tags.json" for n in range(1, 8)
]
VIEWS = f"{ROOT}/final/KPI/com.inductiveautomation.perspective/views"

# transforms to delete: the display-time value conversion and the unit-string swap
DEAD = ("6.894757293168361", "return u'°C'", 'return u"°C"', "return 'kPa'", 'return "kPa"')


def kind(name):
    n = name.lower()
    if "temperature" in n:
        return "temp"
    if "pressure" in n:
        return "press"
    return None


# ---------------------------------------------------------------- simulator
def do_csv():
    out, changed = [], 0
    for line in open(CSV).read().splitlines():
        m = re.match(r'^"(\d+)","([^"]+)","([^"]+)","([^"]+)"$', line)
        if not m:
            out.append(line)
            continue
        interval, path, expr, dtype = m.groups()
        k = kind(path.rsplit("/", 1)[-1])
        if k:
            fn = F_TO_C if k == "temp" else PSI_TO_KPA
            # random(min,max,bool) -> convert both; cosine(min,max,period,bool) -> the
            # third argument is a period in milliseconds and must be left alone
            fm = re.match(r"^(\w+)\((.*)\)$", expr)
            func, args = fm.group(1), [a.strip() for a in fm.group(2).split(",")]
            for i in (0, 1):
                args[i] = "%.2f" % fn(float(args[i]))
            expr = "%s(%s)" % (func, ", ".join(args))
            changed += 1
        out.append('"%s","%s","%s","%s"' % (interval, path, expr, dtype))
    if APPLY:
        open(CSV, "w").write("\n".join(out) + "\n")
    print(f"  simulator generators converted: {changed}")


# ---------------------------------------------------------------- tag metadata
def do_tags():
    changed = 0
    for f in TAGS:
        d = json.load(open(f))
        items = d if isinstance(d, list) else [d]
        for t in items:
            k = kind(t.get("name", ""))
            if not k:
                continue
            fn = F_TO_C if k == "temp" else PSI_TO_KPA
            t["engUnit"] = "°C" if k == "temp" else "kPa"
            for bound in ("engLow", "engHigh"):
                if bound in t and isinstance(t[bound], (int, float)):
                    t[bound] = round(fn(float(t[bound])), 1)
            changed += 1
        if APPLY:
            json.dump(items if isinstance(d, list) else items[0], open(f, "w"), indent=2)
    print(f"  tags re-scaled (engUnit + engLow/engHigh): {changed}")


# ---------------------------------------------------------------- views
def do_views():
    removed = 0
    for dirpath, _, files in os.walk(VIEWS):
        if "view.json" not in files:
            continue
        p = os.path.join(dirpath, "view.json")
        src = open(p).read()
        if not any(tok in src for tok in DEAD):
            continue
        d = json.loads(src)

        def walk(n):
            nonlocal removed
            if isinstance(n, dict):
                tr = n.get("transforms")
                if isinstance(tr, list):
                    keep = [t for t in tr
                            if not (isinstance(t, dict) and isinstance(t.get("code"), str)
                                    and any(tok in t["code"] for tok in DEAD))]
                    if len(keep) != len(tr):
                        removed += len(tr) - len(keep)
                        if keep:
                            n["transforms"] = keep
                        else:
                            del n["transforms"]
                for v in list(n.values()):
                    walk(v)
            elif isinstance(n, list):
                for v in n:
                    walk(v)

        walk(d)
        if APPLY:
            json.dump(d, open(p, "w"), indent=2)
        print("    %s" % os.path.relpath(p, VIEWS))
    print(f"  display-time conversion transforms removed: {removed}")


print("simulator:"); do_csv()
print("tags:");      do_tags()
print("views:");     do_views()
print("\n%s" % ("APPLIED" if APPLY else "DRY RUN - pass --apply to write"))
