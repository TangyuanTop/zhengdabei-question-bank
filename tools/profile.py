import collections
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def norm(s):
    return re.sub(r"[\W_]+", "", s, flags=re.UNICODE)


def load(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except FileNotFoundError:
        return []


xl = load("work/xlsx_bank.json")
rd = load("work/xlsx_random.json")
ed = load("work/ed15.json")

print("xlsx_std", len(xl), "random", len(rd), "ed15", len(ed))

uq = collections.OrderedDict()
for kind, rows in (("std", xl), ("random", rd), ("ed15", ed)):
    for r in rows:
        uq.setdefault(norm(r["stem"]), []).append((kind, r))
print("unique among xlsx+ed15", len(uq))

print("\ntypes:", collections.Counter(r["type"] for k, rows in (("a", xl), ("b", rd)) for r in rows))
print("\nlevels:", collections.Counter(r["level"] for r in xl))
print("\nchapters in xlsx_std:")
for c, n in sorted(collections.Counter(r["chapter"] for r in xl).items()):
    print("  %-24s %3d" % (c, n))
print("\nchapters in random:")
for c, n in sorted(collections.Counter(r["chapter"] for r in rd).items()):
    print("  %-24s %3d" % (c, n))

print("\n--- sheets in xlsx_std ---")
print(collections.Counter(r["source"] for r in xl))
