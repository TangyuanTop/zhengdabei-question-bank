"""Extract the 15th-edition reference bank (clean layout)."""

import json
import re
import sys

import docx

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = (
    "【00重要】历届网考真题模拟题题库及答案/第十五届题库和答案/"
    "“正大杯”第十五届全国大学生市场调查与分析大赛网考参考题库(含答案)137620333586636386.1e8edbf1161a787.docx"
)

ANS = re.compile(r"^答案\s*[：:]\s*([A-Ea-e]{1,5})")
OPT = re.compile(r"^([A-Ea-e])\s*[、.．]\s*(.*)$")
SEC = re.compile(r"^[一二三四五六七八九十]+\s*[、.．]\s*(单选题|多选题|判断题|填空题|简答题)")
QNUM = re.compile(r"^\d{1,3}\s*[.．、]\s*")


def main():
    d = docx.Document(P)
    lines = [x.text.strip() for x in d.paragraphs if x.text.strip()]
    rows = []
    section = ""
    cur = None
    for line in lines:
        m = SEC.match(line)
        if m:
            section = m.group(1)
            continue
        if QNUM.match(line):
            if cur:
                rows.append(cur)
            cur = {"section": section, "stem_lines": [QNUM.sub("", line)], "options": [], "answer": ""}
            continue
        if cur is None:
            continue
        ma = ANS.match(line)
        if ma:
            cur["answer"] = ma.group(1).upper()
            continue
        mo = OPT.match(line)
        if mo:
            cur["options"].append([mo.group(1).upper(), mo.group(2).strip()])
            continue
        if cur["answer"]:
            # trailing junk / next section text
            continue
        if cur["options"]:
            cur["options"][-1][1] += " " + line
        else:
            cur["stem_lines"].append(line)
    if cur:
        rows.append(cur)

    out = []
    for r in rows:
        stem = re.sub(r"\s+", " ", " ".join(r["stem_lines"])).strip()
        opts = [[o[0], re.sub(r"\s+", " ", o[1]).strip()] for o in r["options"]]
        if not r["answer"] or len(opts) < 2:
            continue
        if max("ABCDE".index(c) for c in r["answer"]) >= len(opts):
            continue
        out.append(
            {
                "source": "第十五届网考参考题库",
                "section": r["section"],
                "stem": stem,
                "options": opts,
                "answer": r["answer"],
                "multi": len(r["answer"]) > 1,
            }
        )
    print("rows", len(out))
    import collections

    print(collections.Counter(r["section"] for r in out))
    print("multi", sum(1 for r in out if r["multi"]))
    json.dump(out, open("work/ed15.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in out[:3]:
        print(r["section"], r["answer"], r["stem"][:70], r["options"])


main()
