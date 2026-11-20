"""Extract xlsx banks that lack a proper header row (headerless sheets)."""

import glob
import json
import os
import re
import sys

import openpyxl

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def norm_cell(v):
    if v is None:
        return ""
    return re.sub(r"\s+", " ", str(v).replace("\xa0", " ")).strip()


def guess_layout(ws):
    """Detect column roles from sampled rows: stem is the longest text col."""
    rows = list(ws.iter_rows(min_row=1, max_row=min(ws.max_row, 40), values_only=True))
    ncol = max(len(r) for r in rows) if rows else 0
    scores = []
    for c in range(ncol):
        vals = [norm_cell(r[c]) for r in rows if c < len(r)]
        vals = [v for v in vals if v]
        avg = sum(len(v) for v in vals) / max(1, len(vals))
        scores.append(avg)
    return scores


def extract(path, sheet=None, header_row=None, cols=None):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = []
    for ws in wb.worksheets:
        if sheet and ws.title != sheet:
            continue
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            continue
        start = header_row or 1
        for raw in rows[start - 1 :]:
            cells = [norm_cell(c) for c in raw]
            stem = cells[cols["stem"]] if cols["stem"] < len(cells) else ""
            ans = cells[cols["answer"]] if cols["answer"] < len(cells) else ""
            if not stem or len(stem) < 6:
                continue
            ans_letters = re.sub(r"[^A-Fa-f]", "", ans).upper()
            if not ans_letters or len(ans_letters) > 5:
                continue
            options = []
            for letter in "ABCDEF":
                if letter not in cols:
                    continue
                i = cols[letter]
                txt = cells[i] if i < len(cells) else ""
                if txt:
                    options.append([letter, txt])
            if len(options) < 2:
                continue
            if max("ABCDEF".index(c) for c in ans_letters) >= len(options):
                continue
            out.append(
                {
                    "source": os.path.basename(path) + "::" + ws.title,
                    "sheet": ws.title,
                    "type": cells[cols["type"]] if "type" in cols and cols["type"] < len(cells) else "",
                    "chapter": cells[cols["chapter"]] if "chapter" in cols and cols["chapter"] < len(cells) else "",
                    "level": cells[cols["level"]] if "level" in cols and cols["level"] < len(cells) else "",
                    "stem": stem,
                    "options": options,
                    "answer": ans_letters,
                    "multi": len(ans_letters) > 1,
                }
            )
    wb.close()
    return out


if __name__ == "__main__":
    COLS = {
        "stem": 2,
        "type": 1,
        "chapter": 3,
        "level": 4,
        "answer": 5,
        "A": 6,
        "B": 7,
        "C": 8,
        "D": 9,
        "E": 10,
    }
    rows = []
    for p in ["2. 市调大赛模拟试题/本科随机85道题.xlsx", "2. 市调大赛模拟试题/专科随机100道题.xlsx"]:
        got = extract(p, header_row=1, cols=COLS)
        print(p, len(got))
        rows.extend(got)
    json.dump(rows, open("work/xlsx_random.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("TOTAL", len(rows))
    import collections

    print(collections.Counter(r["chapter"] for r in rows).most_common())
