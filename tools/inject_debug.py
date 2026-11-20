import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

html = io.open("成果/正大杯网考题库精编/刷题自测.html", encoding="utf-8").read()

DBG = """
<div id="dbg" style="position:fixed;left:0;top:0;right:0;background:#111;color:#0f0;
 font:12px monospace;padding:8px;white-space:pre-wrap;z-index:9999"></div>
<script>
(function(){
  const q=list[1];
  const lines=[];
  lines.push('q2 answer='+JSON.stringify(q.a)+' type='+q.y+' opts='+JSON.stringify(q.o));
  q.a.forEach(L=>{const el=document.querySelector('.opt[data-l="'+L+'"]'); if(el) el.click(); else lines.push('no opt '+L);});
  lines.push('picked='+JSON.stringify([...picked]));
  submit();
  lines.push('res='+(document.querySelector('.res.show')||{}).innerText);
  lines.push('answered='+JSON.stringify([...answered.entries()]));
  document.getElementById('dbg').textContent=lines.join('\\n');
})();
</script>
"""

io.open("work/quiz_debug.html", "w", encoding="utf-8").write(html.replace("</body>", DBG + "</body>"))
print("ok")
