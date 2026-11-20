import collections
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def nz(s):
    return re.sub(r"[\W_]+", "", s or "", flags=re.UNICODE)


def load(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except FileNotFoundError:
        return []


SOURCES = [
    ("xlsx", load("work/xlsx_bank.json")),
    ("random", load("work/xlsx_random.json")),
    ("ed15", load("work/ed15.json")),
    ("docx", load("work/parsed_v5.json")),
]

groups = collections.OrderedDict()
for kind, rows in SOURCES:
    for r in rows:
        k = nz(r["stem"])
        if k:
            groups.setdefault(k, []).append((kind, r))

release = json.load(open("work/bank_release.json", encoding="utf-8"))
target = {nz(r["stem"]) for r in release if r["confidence"] in ("有争议", "低")}

shown = 0
for k, items in groups.items():
    if k not in target:
        continue
    conf = [r for r in release if nz(r["stem"]) == k]
    if not conf:
        continue
    if conf[0]["confidence"] == "低" and shown > 40:
        continue
    print("=" * 70)
    print("REL", conf[0]["chapter_code"], conf[0]["answer"], conf[0]["confidence"])
    print("Q:", items[0][1]["stem"][:100])
    for kind, r in items:
        f = r.get("source", "")
        ans_txt = [r["options"]["ABCDE".index(c)][1][:14] for c in r["answer"] if "ABCDE".index(c) < len(r["options"])]
        print("   %-7s %-46s %s -> %s" % (kind, f[-46:], r["answer"], ans_txt))
    shown += 1
