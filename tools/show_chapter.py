import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

code = sys.argv[1]
rows = json.load(open("work/bank_release.json", encoding="utf-8"))
sub = [r for r in rows if r["chapter_code"] == code]
print("count", len(sub))
for r in sub:
    print("-", r["stem"][:88], "|", [o[1][:12] for o in r["options"]][:4])
