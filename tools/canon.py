"""Canonical merge: resolve answer letters by option TEXT, not letter."""

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


srcs = [
    ("xlsx_std", load("work/xlsx_bank.json")),
    ("xlsx_random", load("work/xlsx_random.json")),
    ("ed15", load("work/ed15.json")),
    ("docx", load("work/parsed_v5.json")),
]

groups = collections.OrderedDict()
for kind, rows in srcs:
    for r in rows:
        k = norm(r["stem"])
        if not k:
            continue
        groups.setdefault(k, []).append((kind, r))

print("groups", len(groups))

merged = []
unsure = 0
for k, items in groups.items():
    # prefer xlsx (clean columns) then ed15 then docx
    rank = {"xlsx_std": 0, "xlsx_random": 1, "ed15": 2, "docx": 3}
    items.sort(key=lambda x: rank[x[0]])
    base_kind, base = items[0]
    base = dict(base)
    base_opts = {norm(o[1]): o[0] for o in base["options"]}

    votes = collections.Counter()
    for kind, r in items:
        answers = []
        for ch in r["answer"]:
            idx = "ABCDE".index(ch)
            if idx >= len(r["options"]):
                continue
            answers.append(norm(r["options"][idx][1]))
        for a in answers:
            if a in base_opts:
                votes[base_opts[a]] += 1

    if votes:
        top = votes.most_common()
        best = top[0][0]
        base["answer"] = best
        base["multi"] = False
        base["votes"] = dict(votes)
        if len(top) > 1 and top[1][1] == top[0][1]:
            unsure += 1
            base["flag"] = "tie"
    else:
        base["flag"] = "unresolved"
        unsure += 1

    # multi-select detection: any source says multi and its text maps to >1
    multi_sets = []
    for kind, r in items:
        if r.get("multi"):
            texts = set()
            for ch in r["answer"]:
                idx = "ABCDE".index(ch)
                if idx < len(r["options"]):
                    texts.add(norm(r["options"][idx][1]))
            mapped = sorted(base_opts[t] for t in texts if t in base_opts)
            if len(mapped) > 1:
                multi_sets.append("".join(mapped))
    if multi_sets:
        best = collections.Counter(multi_sets).most_common(1)[0][0]
        base["answer"] = best
        base["multi"] = True

    for kind, r in items:
        if not base.get("chapter") and r.get("chapter"):
            base["chapter"] = r["chapter"]
        if not base.get("type") and r.get("type"):
            base["type"] = r["type"]
        if not base.get("level") and r.get("level"):
            base["level"] = r["level"]
    base["srcs"] = sorted({kind for kind, _ in items})
    base.pop("source", None)
    base.pop("sheet", None)
    merged.append(base)

print("merged", len(merged), "unsure", unsure)
print("multi", sum(1 for r in merged if r["multi"]))
print("with chapter", sum(1 for r in merged if r.get("chapter")))
json.dump(merged, open("work/bank_canon.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("\nflag counts", collections.Counter(r.get("flag", "ok") for r in merged))
