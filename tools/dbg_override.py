import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def nz(s):
    return re.sub(r"[\W_]+", "", s or "", flags=re.UNICODE)


rows = json.load(open("work/bank_release.json", encoding="utf-8"))
for r in rows:
    if "居民区共有" in r["stem"]:
        print("STEM", repr(r["stem"][:40]))
        print("nz contains key?", "居民区共有" in nz(r["stem"]))
        for o in r["options"]:
            print("  ", o[0], repr(o[1]), "->", nz(o[1]), "| contains 902:", "902" in nz(o[1]))
        print("answer", r["answer"], r["confidence"], r["review_note"])
