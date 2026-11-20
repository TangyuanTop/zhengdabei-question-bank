"""Export the release bank to xlsx + CSV + JSON for the quiz page."""

import collections
import csv
import json
import os
import re
import sys

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = "成果/正大杯网考题库精编"
os.makedirs(OUT, exist_ok=True)

bank = json.load(open("work/bank_release.json", encoding="utf-8"))


def answer_text(r):
    return "；".join(o[1] for o in r["options"] if o[0] in r["answer"])


def option_line(r):
    return "\n".join("%s. %s" % (o[0], o[1]) for o in r["options"])


# ---------- CSV ----------
with open(os.path.join(OUT, "题库_全量.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["序号", "章节", "知识点", "题型", "难度", "题干", "选项", "答案", "答案内容", "答案可信度", "备注"])
    for r in bank:
        w.writerow(
            [
                r["id"],
                r["chapter"],
                r["topic"],
                r["type"],
                r["level"] or "",
                r["stem"],
                option_line(r).replace("\n", " / "),
                r["answer"],
                answer_text(r),
                r["confidence"],
                r.get("review_note", ""),
            ]
        )


# ---------- XLSX ----------
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "题库"

HEAD_FILL = PatternFill("solid", fgColor="1F4E79")
HEAD_FONT = Font(color="FFFFFF", bold=True, size=11)
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CONF_FILL = {
    "高": PatternFill("solid", fgColor="E2EFDA"),
    "已核对": PatternFill("solid", fgColor="C6E0B4"),
    "中": PatternFill("solid", fgColor="FFF2CC"),
    "单源": PatternFill("solid", fgColor="F2F2F2"),
    "有争议": PatternFill("solid", fgColor="FCE4D6"),
}

headers = ["序号", "章节", "知识点", "题型", "难度", "题干", "选项", "答案", "答案内容", "可信度", "备注"]
widths = [6, 18, 18, 7, 7, 62, 52, 7, 30, 9, 44]
ws.append(headers)
for i, wd in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = wd
for c in ws[1]:
    c.fill = HEAD_FILL
    c.font = HEAD_FONT
    c.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[1].height = 24

for r in bank:
    ws.append(
        [
            r["id"],
            r["chapter"],
            r["topic"],
            r["type"],
            r["level"] or "",
            r["stem"],
            option_line(r),
            r["answer"],
            answer_text(r),
            r["confidence"],
            r.get("review_note", ""),
        ]
    )
    row = ws.max_row
    for c in ws[row]:
        c.border = BORDER
        c.alignment = Alignment(vertical="top", wrap_text=True)
    ws.cell(row=row, column=1).alignment = Alignment(horizontal="center", vertical="top")
    ws.cell(row=row, column=8).alignment = Alignment(horizontal="center", vertical="top")
    conf = r["confidence"]
    if conf in CONF_FILL:
        ws.cell(row=row, column=10).fill = CONF_FILL[conf]

ws.freeze_panes = "A2"
ws.auto_filter.ref = "A1:K%d" % ws.max_row


# ---------- 章节统计 ----------
ws2 = wb.create_sheet("章节统计")
ws2.append(["章节", "单选题", "多选题", "判断题", "合计"])
for c in ws2[1]:
    c.fill = HEAD_FILL
    c.font = HEAD_FONT
    c.alignment = Alignment(horizontal="center")
order, seen = [], set()
for r in bank:
    if r["chapter"] not in seen:
        seen.add(r["chapter"])
        order.append(r["chapter"])
for ch in order:
    sub = [r for r in bank if r["chapter"] == ch]
    ws2.append(
        [
            ch,
            sum(1 for r in sub if r["type"] == "单选"),
            sum(1 for r in sub if r["type"] == "多选"),
            sum(1 for r in sub if r["type"] == "判断"),
            len(sub),
        ]
    )
ws2.append(
    [
        "合计",
        sum(1 for r in bank if r["type"] == "单选"),
        sum(1 for r in bank if r["type"] == "多选"),
        sum(1 for r in bank if r["type"] == "判断"),
        len(bank),
    ]
)
for i, wd in enumerate([24, 9, 9, 9, 9], 1):
    ws2.column_dimensions[get_column_letter(i)].width = wd

# ---------- 知识点统计 ----------
ws3 = wb.create_sheet("知识点清单")
ws3.append(["章节", "知识点", "题量"])
for c in ws3[1]:
    c.fill = HEAD_FILL
    c.font = HEAD_FONT
cnt = collections.Counter((r["chapter"], r["topic"] or "（综合）") for r in bank)
for (ch, tp), n in sorted(cnt.items(), key=lambda x: (order.index(x[0][0]), -x[1])):
    ws3.append([ch, tp, n])
for i, wd in enumerate([24, 26, 8], 1):
    ws3.column_dimensions[get_column_letter(i)].width = wd

path = os.path.join(OUT, "正大杯网考题库_精编版.xlsx")
wb.save(path)
print("saved", path, len(bank))

# ---------- quiz payload ----------
payload = [
    {
        "i": r["id"],
        "c": r["chapter"],
        "cc": r["chapter_code"],
        "t": r["topic"] or "",
        "y": r["type"],
        "s": r["stem"],
        "o": [o[1] for o in r["options"]],
        "a": [o[0] for o in r["options"] if o[0] in r["answer"]],
        "k": r["confidence"],
    }
    for r in bank
]
json.dump(payload, open("work/quiz_payload.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("payload", len(payload), os.path.getsize("work/quiz_payload.json"))
