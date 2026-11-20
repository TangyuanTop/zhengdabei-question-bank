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

by = collections.defaultdict(list)
for k, v in srcs.items():
    for r in v:
        by[norm(r["stem"])].append((k, r))

conf = 0
shown = 0
for key, items in by.items():
    kinds = {i[0] for i in items}
    answers = {(i[0], i[1]["answer"]) for i in items}
    xl = {a for k, a in answers if k.startswith("xlsx")}
    dx = {a for k, a in answers if k == "docx_v5"}
    if len(xl) > 1:
        conf += 1
        if shown < 6:
            print("XLSX-CONFLICT", xl, items[0][1]["stem"][:70])
            shown += 1
    elif xl and dx and not (dx & xl):
        conf += 1
        if shown < 12:
            print("XLSX-vs-DOCX", list(xl), list(dx), items[0][1]["stem"][:70])
            for k, r in items[:2]:
                print("    ", k, r["answer"], [o[1][:24] for o in r["options"]])
            shown += 1

print("conflicts flagged", conf)

print("\n--- per-source option counts ---")
for k, v in srcs.items():
    print(k, len(v), sorted(collections.Counter(len(r["options"]) for r in v).items()))

print("\n--- docx stems that look broken (contain multiple ？) ---")
bad = [r for r in srcs["docx_v5"] if r["stem"].count("（ ）") + r["stem"].count("()") > 1]
print(len(bad))
for r in bad[:5]:
    print("   ", r["stem"][:140])
