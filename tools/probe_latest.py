import sys

import docx

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

paths = [
    "【00重要】历届网考真题模拟题题库及答案/第十五届题库和答案/"
    "“正大杯”第十五届全国大学生市场调查与分析大赛网考参考题库(含答案)137620333586636386.1e8edbf1161a787.docx",
]

for p in paths:
    d = docx.Document(p)
    ps = [x.text.strip() for x in d.paragraphs if x.text.strip()]
    print("FILE", p.split("/")[-1][:60], "paras", len(ps), "tables", len(d.tables))
    for t in ps[:20]:
        print("  |", t[:150])
