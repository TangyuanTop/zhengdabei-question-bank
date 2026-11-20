"""Hybrid parser: answer-anchored (layout B/C/D) + question-anchored (layout A)."""

import glob
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

INLINE_ANSWER = re.compile(r"\[答案\s*[：:]\s*([A-Ea-eＡ-Ｅ]{1,5})\s*\]")
INLINE_TYPE = re.compile(r"\[题型\s*[：:]\s*([^\]]+)\]")

Q_ANCHOR = re.compile(r"^\s*\d{1,3}\s*-\s*题目\s*[：:]")
Q_ANCHOR2 = re.compile(r"^\s*\d{1,3}\s*[：:]\s*\S")

OPT_LETTER = [
    re.compile(r"^\s*[（(]\s*([A-Ea-eＡ-Ｅ])\s*[)）]\s*(.*)$"),
    re.compile(r"^\s*([A-Ea-eＡ-Ｅ])\s*[.．、]\s*(.*)$"),
]


def parse_inline(path):
    """Layout A: '1-题目：stem [题型：..][答案：B]' then '1-选项：' then '（A）...'"""
    lines = [l.strip() for l in open(path, encoding="utf-8").read().replace("\r", "\n").split("\n")]
    lines = [l for l in lines if l]
    out = []
    i = 0
    while i < len(lines):
        if not (Q_ANCHOR.match(lines[i]) or Q_ANCHOR2.match(lines[i])):
            i += 1
            continue
        head = lines[i]
        m_ans = INLINE_ANSWER.search(head)
        stem = INLINE_ANSWER.sub(" ", head)
        stem = INLINE_TYPE.sub(" ", stem)
        stem = re.sub(r"^\s*\d{1,3}\s*-\s*题目\s*[：:]\s*", "", stem).strip()
        stem = re.sub(r"^\s*\d{1,3}\s*[：:]\s*", "", stem).strip()
        i += 1
        options = []
        while i < len(lines) and not (Q_ANCHOR.match(lines[i]) or Q_ANCHOR2.match(lines[i])):
            line = lines[i]
            if re.match(r"^\s*\d*\s*-?\s*选项\s*[：:]?\s*$", line):
                i += 1
                continue
            hit = None
            for p in OPT_LETTER:
                mm = p.match(line)
                if mm:
                    hit = mm
                    break
            if hit:
                options.append([hit.group(1).upper(), hit.group(2).strip()])
            elif options:
                options[-1][1] = (options[-1][1] + " " + line).strip()
            i += 1
        if m_ans and 2 <= len(options) <= 5:
            letters = re.sub(r"[^A-Ea-eＡ-Ｅ]", "", m_ans.group(1)).upper()
            letters = letters.translate(str.maketrans("ＡＢＣＤＥ", "ABCDE"))
            for j, o in enumerate(options):
                o[0] = "ABCDE"[j]
                o[1] = re.sub(r"\s+", " ", o[1]).strip()
            if all(o[1] for o in options) and all(c in "ABCDE"[: len(options)] for c in letters):
                out.append(
                    {
                        "source": os.path.basename(path),
                        "stem": re.sub(r"\s+", " ", stem).strip(),
                        "options": options,
                        "answer": letters,
                        "multi": len(letters) > 1,
                    }
                )
    return out


def main():
    import parse_bank4

    rows = []
    report = []
    for path in sorted(glob.glob("work/text/*.txt"), key=lambda p: -os.path.getsize(p)):
        a = parse_bank4.parse_file(path)
        b = parse_inline(path)
        best, kind = (a, "ans") if len(a) >= len(b) else (b, "inline")
        rows.extend(best)
        report.append((os.path.basename(path), len(a), len(b), kind))
    for n, ca, cb, k in report:
        print("%-58s ans=%4d inline=%4d -> %s" % (n[:58], ca, cb, k))
    print("TOTAL", len(rows))
    json.dump(rows, open("work/parsed_v5.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
