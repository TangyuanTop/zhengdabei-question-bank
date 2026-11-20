import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

html = open("成果/正大杯网考题库精编/刷题自测.html", encoding="utf-8").read()
m = re.search(r"const CHAPS = (\[.*?\]);", html, re.S)
print("CHAPS found:", bool(m))
if m:
    print(m.group(1))
print("DATA length ok:", "const DATA = [" in html)
print("file size:", len(html))
