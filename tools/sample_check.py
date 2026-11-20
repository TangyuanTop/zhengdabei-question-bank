import json
import random
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

rows = json.load(open("work/bank_final.json", encoding="utf-8"))
random.seed(11)
for r in random.sample(rows, 14):
    print("=" * 70)
    print(r["chapter_final"], "|", r.get("type"), "|", r.get("level"), "|", r["answer"], "|", r.get("srcs"))
    print("Q:", r["stem"])
    for o in r["options"]:
        print("   ", o[0], o[1])
