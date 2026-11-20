"""Render states of the quiz page for visual inspection."""

import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

html = io.open("成果/正大杯网考题库精编/刷题自测.html", encoding="utf-8").read()

STATES = {
    "answered": """
<script>
(function(){
  const q=list[0];
  const wrong='ABCDEF'.split('').find(L=>!q.a.includes(L)&&q.o['ABCDEF'.indexOf(L)]);
  document.querySelector('.opt[data-l="'+wrong+'"]').click();
  submit();
})();
</script>
""",
    "grid": """
<script>
(function(){
  document.getElementById('ch').value='08 双变量关联分析';
  document.getElementById('start').click();
  list.slice(0,18).forEach((q,i)=>{ answered.set(q.i,[q.a[0]]); });
  render(); renderGrid();
})();
</script>
""",
}

for name, script in STATES.items():
    io.open("work/state_%s.html" % name, "w", encoding="utf-8").write(html.replace("</body>", script + "</body>"))
    print("wrote", name)
