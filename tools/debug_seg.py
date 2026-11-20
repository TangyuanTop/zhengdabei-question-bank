import sys

sys.path.insert(0, "tools")
from parse_bank2 import parse_segment, split_questions

path = sys.argv[1]
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 6
text = open(path, encoding="utf-8").read()
segs = split_questions(text)
shown = 0
for i, seg in enumerate(segs):
    r = parse_segment(seg)
    if r is None or len(r[0]) < 6 or len(r[1]) < 2:
        print("### BAD seg", i, "len", len(seg))
        for l in seg[:12]:
            print("   |", l[:140])
        print()
        shown += 1
        if shown >= limit:
            break
