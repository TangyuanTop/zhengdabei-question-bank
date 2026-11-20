"""Answer-anchored parser v4.

Chunk = text between two answer markers.  Chunks often begin with the tail of
the previous question's explanation, so we cut from the last question-start
line.  Explanation blocks are stripped before looking for options.
"""

import glob
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ANSWER = re.compile(
    r"(?:【答案】|\[答案\s*[：:]|正确答案\s*[：:]|答案\s*[：:])"
    r"\s*([A-Ea-eＡ-Ｅ](?:\s*[,，、]?\s*[A-Ea-eＡ-Ｅ]){0,4})"
)

Q_START = [
    re.compile(r"^\s*\d{1,3}\s*-\s*题目\s*[：:]"),
    re.compile(r"^\s*题目\s*[：:]"),
    re.compile(r"^\s*\d{1,3}\s*[.．、]\s*\S"),
    re.compile(r"^\s*[一二三四五六七八九十]{1,3}\s*[、.．]\s*\S"),
]

OPT_LETTER = [
    re.compile(r"^\s*[（(]\s*([A-Ea-eＡ-Ｅ])\s*[)）]\s*(.*)$"),
    re.compile(r"^\s*([A-Ea-eＡ-Ｅ])\s*[.．、]\s*(.*)$"),
    re.compile(r"^[○◯□]\s*([A-Ea-eＡ-Ｅ])[\s\t]+(.*)$"),
]

OPT_BARE = re.compile(r"^[○◯□]\s*(.+)$")

EXPL_START = re.compile(r"^\s*(【解析】|试题解析|答案解析|【解析】|解析)\s*[：:]?\s*")

NOISE = re.compile(
    r"(公众号|竞赛资料库|免费领取|大学生资源大全|全网独家|更多一手资料|一手答案|最新题库|"
    r"^\s*第[一二三四五六七八九十]+部份|^\s*※|^\s*[A-E]\s*$)"
)


def clean_stem(s):
    s = s.replace("\xa0", " ")
    s = re.sub(r"^\s*\d{1,3}\s*-\s*题目\s*[：:]\s*", "", s)
    s = re.sub(r"^\s*题目\s*[：:]\s*", "", s)
    s = re.sub(r"^\s*\d{1,3}\s*[.．、]\s*", "", s)
    s = re.sub(r"^\s*[一二三四五六七八九十]{1,3}\s*[、.．]\s*", "", s)
    s = re.sub(r"^\s*\*+\s*", "", s)
    s = re.sub(r"\[题型\s*[：:][^\]]*\]", " ", s)
    s = re.sub(r"\[答案\s*[：:][^\]]*\]", " ", s)
    s = re.sub(r"（\s*\d+(?:\.\d+)?\s*分\s*）", " ", s)
    s = re.sub(r"（\s*分\s*）", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def strip_explanations(lines):
    """Drop explanation paragraphs: EXPL marker until next question start."""
    out = []
    skipping = False
    for line in lines:
        if EXPL_START.match(line):
            skipping = True
            continue
        if skipping and any(p.match(line) for p in Q_START):
            skipping = False
        if not skipping:
            out.append(line)
    return out


def cut_to_last_question(lines):
    idx = -1
    for i, line in enumerate(lines):
        if any(p.match(line) for p in Q_START):
            idx = i
    if idx <= 0:
        return lines
    return lines[idx:]


def parse_chunk(chunk):
    lines = [l.strip() for l in chunk.replace("\r", "\n").split("\n")]
    lines = [l for l in lines if l and not NOISE.search(l)]
    lines = strip_explanations(lines)
    lines = cut_to_last_question(lines)

    stem_lines = []
    options = []
    mode = "stem"
    for line in lines:
        hit = None
        for p in OPT_LETTER:
            m = p.match(line)
            if m:
                hit = m
                break
        if hit:
            mode = "opt"
            options.append([hit.group(1).upper(), hit.group(2).strip()])
            continue
        bare = OPT_BARE.match(line)
        if bare:
            mode = "opt"
            options.append([None, bare.group(1).strip()])
            continue
        if mode == "opt" and options:
            options[-1][1] = (options[-1][1] + " " + line).strip()
        else:
            stem_lines.append(line)

    stem = clean_stem(" ".join(stem_lines))
    if not (2 <= len(options) <= 5):
        return None

    declared = [o[0] for o in options]
    if all(declared) and declared == list("ABCDE"[: len(options)]):
        pass  # already sequential
    else:
        for i, o in enumerate(options):
            o[0] = "ABCDE"[i]
    for o in options:
        o[1] = re.sub(r"\s+", " ", o[1]).strip()
    if any(not o[1] for o in options):
        return None
    return stem, options


def parse_file(path):
    text = open(path, encoding="utf-8").read().replace("\r", "\n")
    out = []
    prev = 0
    for m in ANSWER.finditer(text):
        chunk = text[prev : m.start()]
        prev = m.end()
        letters = re.sub(r"[^A-Ea-eＡ-Ｅ]", "", m.group(1)).upper()
        letters = letters.translate(str.maketrans("ＡＢＣＤＥ", "ABCDE"))
        if not letters or any(c not in "ABCDE" for c in letters):
            continue
        r = parse_chunk(chunk)
        if not r:
            continue
        stem, options = r
        if len(stem) < 8:
            continue
        if max("ABCDE".index(c) for c in letters) >= len(options):
            continue
        out.append(
            {
                "source": os.path.basename(path),
                "stem": stem,
                "options": options,
                "answer": letters,
                "multi": len(letters) > 1,
            }
        )
    return out


def main():
    rows = []
    report = []
    for path in sorted(glob.glob("work/text/*.txt"), key=lambda p: -os.path.getsize(p)):
        got = parse_file(path)
        rows.extend(got)
        report.append((os.path.basename(path), len(got)))
    for n, c in report:
        print("%-62s ok=%4d" % (n[:62], c))
    print("TOTAL", len(rows))
    json.dump(rows, open("work/parsed_v4.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
