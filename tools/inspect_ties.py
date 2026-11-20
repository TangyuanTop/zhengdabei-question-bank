import json
import random
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

rows = json.load(open("work/bank_final.json", encoding="utf-8"))
ties = [r for r in rows if r.get("flag") == "tie"]
print("ties", len(ties), "multi among ties", sum(1 for r in ties if r["multi"]))
random.seed(3)
for r in random.sample(ties, 12):
    print("=" * 60)
    print(r.get("type"), "|", r["answer"], "|", r.get("srcs"), "|", r.get("votes"))
    print("Q:", r["stem"][:100])
    for o in r["options"]:
        print("   ", o[0], o[1][:50])
