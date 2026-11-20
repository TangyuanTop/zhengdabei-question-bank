import sys

import docx

path = sys.argv[1]
d = docx.Document(path)
shown = 0
for i, p in enumerate(d.paragraphs):
    if not p.text.strip():
        continue
    parts = []
    for r in p.runs:
        color = r.font.color.rgb if r.font.color and r.font.color.rgb else None
        parts.append(f"[{r.text!r} c={color} b={r.bold} u={r.underline}]")
    print(i, p.style.name, " ".join(parts)[:300])
    shown += 1
    if shown > 40:
        break
