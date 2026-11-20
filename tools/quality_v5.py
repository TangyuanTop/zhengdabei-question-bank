import collections
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

rows = json.load(open("work/parsed_v5.json", encoding="utf-8"))


def norm(s):
    return re.sub(r"[\W_]+", "", s, flags=re.UNICODE)


seen = collections.OrderedDict()
dups = collections.Counter()
for r in rows:
    k = norm(r["stem"])
    dups[k] += 1
    seen.setdefault(k, []).append(r)

print("rows", len(rows), "unique", len(seen))
print("multi(unique)", sum(1 for v in seen.values() if v[0]["multi"]))
lens = sorted(len(v[0]["stem"]) for v in seen.values())
print("stem len p10/p50/p90/max", lens[len(lens) // 10], lens[len(lens) // 2], lens[9 * len(lens) // 10], lens[-1])
print("optcounts", sorted(collections.Counter(len(v[0]["options"]) for v in seen.values()).items()))

long_ = [v[0] for v in seen.values() if len(v[0]["stem"]) > 300]
print("over300", len(long_))
for r in long_[:6]:
    print("  LEN", len(r["stem"]), r["stem"][:160])

conf = []
for k, v in seen.items():
    ans = {x["answer"] for x in v}
    if len(ans) > 1:
        conf.append(v)
print("answer conflicts", len(conf))
for v in conf[:8]:
    print("  C", {x["answer"] for x in v}, v[0]["stem"][:70])
