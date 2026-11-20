"""Structure-aware parser for the market-research exam banks.

Files come in several layouts:
  A) "1-题目：... [题型：单选题][答案：B]" then "1-选项：" then "（A）..."
  B) "1.题干（ ）。" then "A. xxx" ... then "【答案】A"
  C) "1、题干（ ）。（1.0分）" then "A. xxx" ... then "正确答案：A"
  D) "一、题干（ ）。（分）" then "A. xxx" ... then "正确答案：A"
"""

import glob
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

Q_START = [
    re.compile(r"^\d+\s*-\s*题目\s*[：:]"),
    re.compile(r"^题目\s*[：:]"),
    re.compile(r"^\d{1,3}\s*[.．、]\s*(?!\d)"),
    re.compile(r"^[一二三四五六七八九十]{1,3}\s*[、.．]\s*"),
]

ANSWER = re.compile(
    r"(?:【答案】|\[答案\s*[：:]|正确答案\s*[：:]|答案\s*[：:])\s*([A-Ea-eＡ-Ｅ](?:\s*[,，、]?\s*[A-Ea-eＡ-Ｅ]){0,4})"
)

OPT = [
    re.compile(r"^\s*[（(]\s*([A-Ea-eＡ-Ｅ])\s*[)）]\s*(.*)$"),
    re.compile(r"^\s*([A-Ea-eＡ-Ｅ])\s*[.．、]\s*(.*)$"),
]

TYPE_TAG = re.compile(r"\[题型\s*[：:]\s*([^\]]+)\]")


def split_questions(text):
    lines = [l.strip() for l in text.replace("\r", "\n").split("\n")]
    segs = []
    cur = []
    for line in lines:
        if not line:
            continue
        is_start = any(p.match(line) for p in Q_START)
        if is_start and cur:
            segs.append(cur)
            cur = [line]
        else:
            cur.append(line)
    if cur:
        segs.append(cur)
    return segs


def clean_stem(stem):
    s = stem
    s = re.sub(r"^\s*\d+\s*-\s*题目\s*[：:]\s*", "", s)
    s = re.sub(r"^\s*题目\s*[：:]\s*", "", s)
    s = re.sub(r"^\s*\d{1,3}\s*[.．、]\s*", "", s)
    s = re.sub(r"^\s*[一二三四五六七八九十]{1,3}\s*[、.．]\s*", "", s)
    s = re.sub(r"^\s*\*+\s*", "", s)
    s = TYPE_TAG.sub(" ", s)
    s = re.sub(r"（\s*\d+(?:\.\d+)?\s*分\s*）", " ", s)
    s = re.sub(r"（\s*分\s*）", " ", s)
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_segment(lines):
    body = "\n".join(lines)
    m = ANSWER.search(body)
    if not m:
        return None
    letters = re.sub(r"[^A-Ea-eＡ-Ｅ]", "", m.group(1)).upper()
    letters = letters.translate(str.maketrans("ＡＢＣＤＥ", "ABCDE"))
    if not letters:
        return None

    stem_lines = []
    options = []
    in_opts = False
    for line in lines:
        if re.match(r"^\s*\d*\s*-?\s*选项\s*[：:]?\s*$", line):
            in_opts = True
            continue
        if re.match(r"^\s*选项\s*[：:]?\s*$", line):
            in_opts = True
            continue
        matched = None
        for p in OPT:
            mm = p.match(line)
            if mm:
                matched = mm
                break
        if matched:
            in_opts = True
            options.append([matched.group(1).upper(), matched.group(2).strip()])
            continue
        if in_opts and options and not ANSWER.search(line):
            if not re.match(r"^\[?题型", line) and line not in ("试题解析：", "试题解析:"):
                options[-1][1] = (options[-1][1] + " " + line).strip()
        elif not in_opts:
            # strip trailing answer markers from the stem line
            s = ANSWER.split(line)[0]
            s = re.sub(r"\[答案\s*[：:][^\]]*\]", "", s)
            stem_lines.append(s)

    stem = clean_stem(" ".join(stem_lines))
    if len(options) > 5:
        return None
    for i, o in enumerate(options):
        o[0] = "ABCDE"[i]
    return stem, options, letters


def main():
    rows = []
    report = []
    for path in sorted(glob.glob("work/text/*.txt"), key=lambda p: -os.path.getsize(p)):
        name = os.path.basename(path)
        text = open(path, encoding="utf-8").read()
        segs = split_questions(text)
        ok = bad = 0
        for seg in segs:
            r = parse_segment(seg)
            if not r:
                bad += 1
                continue
            stem, options, letters = r
            if len(stem) < 6 or len(options) < 2:
                bad += 1
                continue
            if any(not o[1] for o in options):
                bad += 1
                continue
            rows.append(
                {
                    "source": name,
                    "stem": stem,
                    "options": options,
                    "answer": letters,
                    "multi": len(letters) > 1,
                }
            )
            ok += 1
        report.append((name, len(segs), ok, bad))

    for n, s, o, b in report:
        print("%-60s segs=%4d ok=%4d bad=%4d" % (n[:60], s, o, b))
    print("TOTAL", len(rows))
    json.dump(rows, open("work/parsed_raw2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
