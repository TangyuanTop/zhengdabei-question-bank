import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

rows = json.load(open("work/bank_v6.json", encoding="utf-8"))
left = [r for r in rows if r["chapter_final"] == "11 待归类"]
print(len(left))
for r in left:
    print("-", r["stem"][:90], "|", [o[1][:14] for o in r["options"]][:4])
