"""Merge every extracted source into one de-duplicated bank with chapters."""

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


srcs = {
    "xlsx_std": load("work/xlsx_bank.json"),
    "xlsx_random": load("work/xlsx_random.json"),
    "docx_v5": load("work/parsed_v5.json"),
    "ed15": load("work/ed15.json"),
}

for k, v in srcs.items():
    print(k, len(v))

allrows = []
for k, v in srcs.items():
    for r in v:
        r = dict(r)
        r["origin"] = k
        allrows.append(r)

# merge by normalised stem
merged = collections.OrderedDict()
for r in allrows:
    key = norm(r["stem"])
    if not key:
        continue
    if key not in merged:
        r["sources"] = [r.get("source", "")]
        merged[key] = r
    else:
        base = merged[key]
        src = r.get("source", "")
        if src and src not in base["sources"]:
            base["sources"].append(src)
        for field in ("chapter", "level", "type"):
            if not base.get(field) and r.get(field):
                base[field] = r[field]

rows = list(merged.values())
print("MERGED", len(rows))

no_chapter = sum(1 for r in rows if not r.get("chapter"))
print("no chapter", no_chapter)

print("\nchapter distribution:")
for c, n in collections.Counter(r.get("chapter") or "（无）" for r in rows).most_common():
    print("  %-22s %4d" % (c, n))

json.dump(rows, open("work/bank_merged.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("\nanswer conflicts after merge:", sum(1 for r in rows if len(r["answer"]) > 2))

# sanity samples per chapter
for c in ["市场调查概述", "抽样设计与推断", "问卷及量表设计"]:
    print("\n===", c)
    for r in [x for x in rows if x.get("chapter") == c][:3]:
        print("  [%s]" % r["answer"], r["stem"][:90])
        for o in r["options"]:
            print("      ", o[0], o[1][:50])
