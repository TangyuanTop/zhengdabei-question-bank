import json
import random
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

rows = json.load(open("work/bank_release.json", encoding="utf-8"))
mode = sys.argv[1]

if mode == "disputed":
    sub = [r for r in rows if r["confidence"] == "有争议"]
    print("disputed", len(sub))
    for r in sub:
        print("=" * 64)
        print(r["chapter"], "|", r["type"], "| ans", r["answer"])
        print("Q:", r["stem"][:130])
        for o in r["options"]:
            mark = "*" if o[0] in r["answer"] else " "
            print("  ", mark, o[0], o[1][:60])
elif mode == "chapter":
    code = sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    sub = [r for r in rows if r["chapter_code"] == code]
    random.seed(5)
    for r in random.sample(sub, min(n, len(sub))):
        print("=" * 64)
        print(r["chapter"], "/", r["topic"], "|", r["type"], "|", r["confidence"], "| ans", r["answer"])
        print("Q:", r["stem"][:130])
        for o in r["options"]:
            print("   ", o[0], o[1][:60])
elif mode == "lowconf":
    sub = [r for r in rows if r["confidence"] == "低"]
    print("lowconf", len(sub))
    random.seed(2)
    for r in random.sample(sub, 8):
        print("=" * 64)
        print(r["chapter"], "|", r["type"], "| ans", r["answer"], "| srcs", r["n_sources"])
        print("Q:", r["stem"][:120])
        for o in r["options"]:
            print("   ", o[0], o[1][:55])
