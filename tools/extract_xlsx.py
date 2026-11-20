"""Extract structured question banks from the .xlsx files."""

import glob
import json
import os
import re
import sys

import openpyxl

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HEADER_HINTS = ("题干", "题型", "答案")


def norm_cell(v):
    if v is None:
        return ""
    s = str(v).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


def find_header(ws):
    for row_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=10, values_only=True), start=1):
        cells = [norm_cell(c) for c in row]
        squashed = [c.replace(" ", "") for c in cells]
        if all(any(h in c for c in squashed) for h in HEADER_HINTS):
            return row_idx, cells
    return None, None


def map_columns(header):
    idx = {}
    for i, name in enumerate(header):
        n = name.replace(" ", "")
        if not n:
            continue
        if "题干" in n or n == "题目":
            idx.setdefault("stem", i)
        elif "题型" in n:
            idx.setdefault("type", i)
        elif "答案" in n:
            idx.setdefault("answer", i)
        elif "章节" in n:
            idx.setdefault("chapter", i)
        elif "难度" in n:
            idx.setdefault("level", i)
        elif n in ("A", "B", "C", "D", "E", "F"):
            idx[n] = i
    return idx


def extract(path):
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    except Exception as e:  # noqa: BLE001
        print("SKIP", os.path.basename(path), type(e).__name__)
        return []
    out = []
    for ws in wb.worksheets:
        hdr_row, header = find_header(ws)
        if not hdr_row:
            continue
        idx = map_columns(header)
        if "stem" not in idx or "answer" not in idx:
            continue
        opt_cols = [k for k in ("A", "B", "C", "D", "E", "F") if k in idx]
        for row in ws.iter_rows(min_row=hdr_row + 1, values_only=True):
            stem = norm_cell(row[idx["stem"]]) if idx["stem"] < len(row) else ""
            ans = norm_cell(row[idx["answer"]]) if idx["answer"] < len(row) else ""
            if not stem or not ans:
                continue
            options = []
            for letter in opt_cols:
                i = idx[letter]
                txt = norm_cell(row[i]) if i < len(row) else ""
                if txt:
                    options.append([letter, txt])
            if len(options) < 2:
                continue
            ans_letters = re.sub(r"[^A-Fa-f]", "", ans).upper()
            if not ans_letters:
                continue
            if max("ABCDEF".index(c) for c in ans_letters) >= len(options):
                continue
            out.append(
                {
                    "source": os.path.basename(path) + "::" + ws.title,
                    "sheet": ws.title,
                    "type": norm_cell(row[idx["type"]]) if "type" in idx and idx["type"] < len(row) else "",
                    "chapter": norm_cell(row[idx["chapter"]]) if "chapter" in idx and idx["chapter"] < len(row) else "",
                    "level": norm_cell(row[idx["level"]]) if "level" in idx and idx["level"] < len(row) else "",
                    "stem": stem,
                    "options": options,
                    "answer": ans_letters,
                    "multi": len(ans_letters) > 1,
                }
            )
    wb.close()
    return out


def main():
    rows = []
    for path in sorted(glob.glob("*.xlsx") + glob.glob("*/*.xlsx")):
        got = extract(path)
        if got:
            print("%-60s ok=%4d" % (path[:60], len(got)))
        rows.extend(got)
    print("TOTAL", len(rows))
    json.dump(rows, open("work/xlsx_bank.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


main()
