import collections
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

rows = json.load(open("work/parsed_v3.json", encoding="utf-8"))


def norm(s):
    return re.sub(r"[\W_]+", "", s, flags=re.UNICODE)


seen = collections.OrderedDict()
for r in rows:
    k = norm(r["stem"])
    seen.setdefault(k, []).append(r)

print("rows", len(rows), "unique", len(seen))
print("multi", sum(1 for r in rows if r["multi"]))
lens = sorted(len(r["stem"]) for r in rows)
print("stem len min/med/max", lens[0], lens[len(lens) // 2], lens[-1])
print(sorted(collections.Counter(len(r["options"]) for r in rows).items()))

conflicts = []
for k, v in seen.items():
    answers = {r["answer"] for r in v}
    if len(v) > 1 and len(answers) > 1:
        conflicts.append((v[0]["stem"][:70], answers, [r["source"] for r in v]))
print("CONFLICTS", len(conflicts))
for c in conflicts[:15]:
    print(" -", c[0], c[1])

print("\n--- sample 12 random uniques ---")
import random

random.seed(7)
for r in random.sample(list(seen.values()), 12):
    r = r[0]
    print("[%s]" % r["answer"], r["stem"][:110])
    for o in r["options"]:
        print("    ", o[0], o[1][:60])
