import glob

import pdfplumber

lines = []
for path in sorted(glob.glob("*.pdf")) + sorted(glob.glob("*/*.pdf")):
    with pdfplumber.open(path) as pdf:
        first = pdf.pages[0].extract_text() or ""
    lines.append(f"### {path} pages={len(pdf.pages)}")
    lines.append(first[:800])
    lines.append("")

with open("pdf_probe.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("ok")
