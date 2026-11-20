"""Answer-anchored parser: split the raw text at every answer marker."""

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

OPT_LETTER = [
    re.compile(r"^\s*[（(]\s*([A-Ea-eＡ-Ｅ])\s*[)）]\s*(.*)$"),
    re.compile(r"^\s*([A-Ea-eＡ-Ｅ])\s*[.．、]\s*(.*)$"),
    re.compile(r"^[○◯□]\s*([A-Ea-eＡ-Ｅ])[\s\t]+(.*)$"),
]

OPT_BARE = re.compile(r"^[○◯□]\s*(.+)$")

NOISE = re.compile(
    r"^(试题解析|解析|答案解析|更多一手资料|请关注微信公众号|微信公众号|免费领取|大学生资源大全|全网独家|A\.\s*$)"
)


def clean_stem(s):
    s = s.replace("\xa0", " ")
    s = re.sub(r"^\s*\d+\s*-\s*题目\s*[：:]\s*", "", s)
    s = re.sub(r"^\s*题目\s*[：:]\s*", "", s)
    s = re.sub(r"^\s*\d{1,3}\s*[.．、]\s*", "", s)
    s = re.sub(r"^\s*[一二三四五六七八九十]{1,3}\s*[、.．]\s*", "", s)
    s = re.sub(r"^\s*\*+\s*", "", s)
    s = re.sub(r"\[题型\s*[：:][^\]]*\]", " ", s)
    s = re.sub(r"（\s*\d+(?:\.\d+)?\s*分\s*）", " ", s)
    s = re.sub(r"（\s*分\s*）", " ", s)
    s = re.sub(r"^\s*选项\s*[：:]?\s*$", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_chunk(chunk):
    lines = [l.strip() for l in chunk.replace("\r", "\n").split("\n")]
    lines = [l for l in lines if l]

    stem_lines = []
    options = []
    mode = "stem"
    for line in lines:
        if NOISE.match(line):
            continue
        if line.startswith("※") or line.startswith("第") and "部分" in line:
            continue
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
    if len(options) > 5 or len(options) < 2:
        return None
    letters = [o[0] for o in options]
    if any(letters) and all(letters):
        # keep declared letters, re-map to sequence so answer letters align
        order = {l: i for i, l in enumerate(letters)}
        if sorted(order.values()) != list(range(len(options))):
            # letters out of order / duplicated -> reassign sequentially
            for i, o in enumerate(options):
                o[0] = "ABCDE"[i]
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
        if not letters:
            continue
        r = parse_chunk(chunk)
        if not r:
            continue
        stem, options = r
        if len(stem) < 8:
            continue
        if any(ch not in "ABCDE" for ch in letters):
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
    json.dump(rows, open("work/parsed_v3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
