import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

rows = json.load(open("work/bank_release.json", encoding="utf-8"))
for term in sys.argv[1:]:
    hits = [r for r in rows if term in r["stem"]]
    print("==", term, len(hits))
    for r in hits[:8]:
        print("   ", r["chapter_code"], r["topic"], "|", r["stem"][:70])
