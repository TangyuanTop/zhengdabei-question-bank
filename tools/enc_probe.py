import glob
import os

for path in sorted(glob.glob("work/text/*.txt")):
    raw = open(path, "rb").read()
    guess = []
    for enc in ("utf-8", "utf-16", "gb18030"):
        try:
            text = raw.decode(enc)
        except UnicodeDecodeError:
            continue
        guess.append((enc, text.count("\ufffd"), len(text)))
    print(os.path.basename(path)[:60], guess[:3])
