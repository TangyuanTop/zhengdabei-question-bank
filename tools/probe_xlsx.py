import glob
import sys

import openpyxl

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

for path in sorted(glob.glob("*.xlsx") + glob.glob("*/*.xlsx")):
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    except Exception as e:  # noqa: BLE001
        print("ERR", path, e)
        continue
    for ws in wb.worksheets:
        print("===", path, "|", ws.title, "|", ws.max_row, "x", ws.max_column)
        for row in ws.iter_rows(min_row=1, max_row=4, values_only=True):
            cells = [str(c)[:40] if c is not None else "" for c in row]
            print("   ", " | ".join(cells)[:220])
    wb.close()
