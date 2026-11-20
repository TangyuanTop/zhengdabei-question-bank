"""Final pass: resolve answers by option-text sets, score chapters, emit bank."""

import collections
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from classify import CANON, RULES


def norm(s):
    return re.sub(r"[\W_]+", "", s, flags=re.UNICODE)


def load(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except FileNotFoundError:
        return []


SOURCES = [
    ("xlsx_std", load("work/xlsx_bank.json")),
    ("xlsx_random", load("work/xlsx_random.json")),
    ("ed15", load("work/ed15.json")),
    ("docx", load("work/parsed_v5.json")),
]

groups = collections.OrderedDict()
for kind, rows in SOURCES:
    for r in rows:
        k = norm(r["stem"])
        if k:
            groups.setdefault(k, []).append((kind, r))

out = []
for k, items in groups.items():
    # pick the record with the most options as structural base (then richest metadata)
    items.sort(key=lambda x: (-len(x[1]["options"]), {"xlsx_std": 0, "xlsx_random": 1, "ed15": 2, "docx": 3}[x[0]]))
    base = dict(items[0][1])
    base_opts = {norm(o[1]): o[0] for o in base["options"]}
    letters_of = {v: k for k, v in base_opts.items()}

    # collect answer sets expressed as canonical option text
    ballots = []
    for kind, r in items:
        texts = []
        for ch in r["answer"]:
            i = "ABCDE".index(ch)
            if i < len(r["options"]):
                texts.append(norm(r["options"][i][1]))
        mapped = frozenset(base_opts[t] for t in texts if t in base_opts)
        if mapped:
            ballots.append((kind, mapped))

    weight = {"xlsx_std": 3.0, "xlsx_random": 3.0, "ed15": 3.0, "docx": 1.0}
    score = collections.Counter()
    for kind, s in ballots:
        score[s] += weight[kind]
    if not score:
        continue
    best, best_score = score.most_common(1)[0]
    total = sum(score.values())
    base["answer"] = "".join(sorted(best, key=lambda c: "ABCDE".index(c)))
    base["multi"] = len(best) > 1
    base["confidence"] = "高" if best_score >= 3 and len(score) == 1 else ("中" if best_score >= 3 else "低")
    if len(score) > 1:
        base["confidence"] = "有争议"
        base["alt_answers"] = ["".join(sorted(s, key=lambda c: "ABCDE".index(c))) for s, _ in score.most_common()[1:3]]
    base["srcs"] = sorted({kind for kind, _ in items})
    base.pop("source", None)
    base.pop("sheet", None)
    base.pop("votes", None)
    base.pop("flag", None)

    # chapter scoring: keyword hits + label bonus
    text = base["stem"] + " " + " ".join(o[1] for o in base["options"])
    kw = {}
    for chapter, keywords in RULES:
        hits = sum(text.count(x) for x in keywords)
        if hits:
            kw[chapter] = hits
    label = CANON.get((base.get("chapter") or "").strip())
    if label:
        kw[label] = kw.get(label, 0) + 3.0
    if kw:
        base["chapter_final"] = max(kw.items(), key=lambda x: x[1])[0]
        base["chapter_margin"] = kw[base["chapter_final"]]
    else:
        base["chapter_final"] = "11 待归类"
        base["chapter_margin"] = 0
    for f in ("chapter_margin",):
        pass
    out.append(base)

out.sort(key=lambda r: (r["chapter_final"], {"单选": 0, "多选": 1, "判断": 2}.get(r.get("type") or "", 3), r["stem"]))
json.dump(out, open("work/bank_v6.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("total", len(out))
print("confidence", collections.Counter(r["confidence"] for r in out))
print("multi", sum(1 for r in out if r["multi"]))
print()
for c, n in sorted(collections.Counter(r["chapter_final"] for r in out).items()):
    print("  %-34s %4d" % (c, n))
