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


xl = load("work/xlsx_bank.json") + load("work/xlsx_random.json") + load("work/ed15.json")
dx = load("work/parsed_v5.json")

xlmap = {}
for r in xl:
    xlmap.setdefault(norm(r["stem"]), r)

dxmap = collections.defaultdict(list)
for r in dx:
    dxmap[norm(r["stem"])].append(r)

overlap = [k for k in dxmap if k in xlmap]
print("docx uniques", len(dxmap), "overlap with xlsx", len(overlap))

agree = disagree = 0
examples = []
for k in overlap:
    a = xlmap[k]
    a_text = {norm(o[1]) for o in a["options"] if o[0] in a["answer"]}
    for r in dxmap[k]:
        b_text = {norm(o[1]) for o in r["options"] if o[0] in r["answer"]}
        if a_text == b_text and a_text:
            agree += 1
        else:
            disagree += 1
            if len(examples) < 6:
                examples.append((a, r, a_text, b_text))

print("agree", agree, "disagree", disagree, "rate", round(agree / max(1, agree + disagree), 3))
for a, r, at, bt in examples:
    print("\nSTEM", a["stem"][:80])
    print("  xlsx ans", a["answer"], "->", [o[1][:25] for o in a["options"] if o[0] in a["answer"]])
    print("  docx ans", r["answer"], "->", [o[1][:25] for o in r["options"] if o[0] in r["answer"]])

# internal docx consistency: same stem across docx copies
same = diff = 0
for k, v in dxmap.items():
    if len(v) < 2:
        continue
    texts = {frozenset(norm(o[1]) for o in r["options"] if o[0] in r["answer"]) for r in v}
    if len(texts) == 1:
        same += 1
    else:
        diff += 1
print("\ndocx duplicated stems: consistent", same, "inconsistent", diff)
