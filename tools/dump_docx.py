import glob
import os

import docx

os.makedirs("work/text", exist_ok=True)

for path in sorted(glob.glob("*.docx")) + sorted(glob.glob("*/*.docx")):
    try:
        d = docx.Document(path)
    except Exception as e:  # noqa: BLE001
        print("ERR", path, e)
        continue
    lines = [p.text for p in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            cells = []
            for c in row.cells:
                cells.append(" ".join(c.text.split()))
            lines.append("\t".join(cells))
    name = os.path.basename(path).replace(".docx", "").strip()
    safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name)
    with open(f"work/text/docx_{safe}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(len(lines), path)
