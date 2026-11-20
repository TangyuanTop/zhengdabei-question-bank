import glob
import os
import sys

import docx

out = []
for path in sorted(glob.glob("*.docx")) + sorted(glob.glob("*/*.docx")):
    try:
        d = docx.Document(path)
    except Exception as e:  # noqa: BLE001
        out.append(f"### {path}\nERROR {e}\n")
        continue
    ps = [p.text.strip() for p in d.paragraphs if p.text.strip()]
    out.append(f"### {path} | paras={len(ps)} tables={len(d.tables)}")
    for t in ps[:25]:
        out.append("  " + t[:120])
    out.append("")

with open("probe_out.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("done", len(out))
