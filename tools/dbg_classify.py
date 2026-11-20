import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, "tools")
from build_final import APPENDIX_B, CHAPTERS, classify

stems = sys.argv[1:]
for s in stems:
    ch, topic = classify(s, [])
    scores = []
    for code, name, kws, topics in CHAPTERS + [APPENDIX_B]:
        sc = sum(3 for k in kws if k in s)
        if sc:
            scores.append((sc, code, name, [k for k in kws if k in s]))
    scores.sort(reverse=True)
    print(s[:60])
    print("  ->", ch[0], ch[1], "|", topic)
    for sc, code, name, hits in scores[:4]:
        print("     %5.1f %s %s %s" % (sc, code, name, hits))
