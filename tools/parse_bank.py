"""Parse the raw docx text dumps into a structured question bank."""

import glob
import json
import os
import re
import sys

TEXT_DIR = "work/text"

ANS_PATTERNS = [
    re.compile(r"【答案】\s*([A-Ea-eＡ-Ｅ]{1,5})"),
    re.compile(r"\[答案：\s*([A-Ea-e]{1,5})\s*\]"),
    re.compile(r"正确答案\s*[：:]\s*([A-Ea-e]{1,5})"),
]

OPT_LETTER = re.compile(r"^\s*([A-Ea-e])\s*[.．、]\s*(.+)$")
OPT_LETTER2 = re.compile(r"^\s*[（(]\s*([A-Ea-e])\s*[)）]\s*(.+)$")
QNUM = re.compile(r"^\s*(?:第)?\s*[0-9一二三四五六七八九十百]+\s*[-、.．]?\s*(?:题目|题)?\s*[：:]?\s*")


def norm(s):
    s = s.replace("\u3000", " ")
    s = re.sub(r"\s+", "", s)
    return s


def find_answer(line):
    for pat in ANS_PATTERNS:
        m = pat.search(line)
        if m:
            letters = m.group(1).upper()
            letters = letters.translate(str.maketrans("ＡＢＣＤＥ", "ABCDE"))
            return letters, (m.start(), m.end())
    return None, None


def parse_file(path):
    text = open(path, encoding="utf-8").read()
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [l.strip() for l in text.split("\n")]
    lines = [l for l in lines if l]

    blocks = []
    cur = []
    for line in lines:
        ans, span = find_answer(line)
        if ans:
            head = line[: span[0]].strip()
            if head:
                cur.append(head)
            blocks.append((cur, ans))
            cur = []
        else:
            cur.append(line)
    if cur:
        blocks.append((cur, None))
    return blocks


def extract(block_lines):
    """Return dict(stem, options[list of (letter,text)], or None)."""
    stem_parts = []
    options = []
    state = "stem"
    pending_bare = []
    for line in block_lines:
        m1 = OPT_LETTER.match(line)
        m2 = OPT_LETTER2.match(line)
        m = m1 or m2
        if m:
            state = "opt"
            options.append([m.group(1).upper(), m.group(2).strip()])
            continue
        if state == "stem":
            stem_parts.append(line)
        else:
            if options:
                # continuation of previous option
                options[-1][1] = (options[-1][1] + " " + line).strip()
            else:
                stem_parts.append(line)

    stem = " ".join(stem_parts)
    stem = re.sub(r"^\s*(?:第)?\s*[0-9一二三四五六七八九十百]+\s*[-、.．]?\s*(?:题目|题)?\s*[：:]\s*", "", stem)
    stem = re.sub(r"^\s*[0-9]+\s*[-、.．]\s*", "", stem)
    stem = re.sub(r"^\s*[0-9]+\s*[、.．]\s*", "", stem)
    stem = re.sub(r"\s*[（(]\s*[0-9.]+\s*分\s*[)）]\s*$", "", stem)
    stem = re.sub(r"\s*[（(]\s*分\s*[)）]\s*$", "", stem)
    stem = re.sub(r"\s*[（(]\s*[)）]\s*$", "", stem)
    stem = stem.strip()

    # normalise option letters sequentially
    if len(options) > 5:
        options = []
    for i, o in enumerate(options):
        o[0] = "ABCDE"[i]
    return stem, options


def main():
    rows = []
    stats = []
    for path in sorted(glob.glob(os.path.join(TEXT_DIR, "*.txt"))):
        name = os.path.basename(path)
        blocks = parse_file(path)
        got = 0
        skipped = 0
        for lines, ans in blocks:
            if not ans:
                skipped += 1
                continue
            stem, options = extract(lines)
            if len(stem) < 6 or len(options) < 2:
                skipped += 1
                continue
            rows.append(
                {
                    "source": name,
                    "stem": stem,
                    "options": options,
                    "answer": ans,
                    "multi": len(ans) > 1,
                }
            )
            got += 1
        stats.append((name, len(blocks), got, skipped))

    for s in stats:
        print("%-58s blocks=%4d ok=%4d skip=%4d" % (s[0][:58], s[1], s[2], s[3]))
    print("TOTAL", len(rows))
    print("MULTI", sum(1 for r in rows if r["multi"]))

    os.makedirs("work", exist_ok=True)
    with open("work/parsed_raw.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)

    import collections

    norm_stems = collections.Counter(norm(r["stem"]) for r in rows)
    print("UNIQUE_STEMS", len(norm_stems))
    print("DUP_TOP", norm_stems.most_common(3))


if __name__ == "__main__":
    main()
