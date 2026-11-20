"""Create a copy of the quiz page that self-tests its interactive logic."""

import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

src = "成果/正大杯网考题库精编/刷题自测.html"
html = io.open(src, encoding="utf-8").read()

TEST = """
<div id="testout" style="position:fixed;left:0;top:0;right:0;z-index:9999;background:#111;
 color:#eee;font:12px/1.5 Consolas,monospace;padding:10px;max-height:42vh;overflow:auto;white-space:pre-wrap"></div>
<script>
(function(){
  const log=[]; let pass=0, fail=0;
  const ok=(name,cond,extra)=>{ if(cond){pass++;log.push('PASS '+name);} else {fail++;log.push('FAIL '+name+(extra?' :: '+extra:''));} };

  function clickOpt(letter){
    const el=document.querySelector('.opt[data-l="'+letter+'"]');
    if(!el) return false; el.click(); return true;
  }
  function resultText(){ const r=document.querySelector('.res.show'); return r?r.innerText:''; }

  // 1. 初始渲染
  ok('初始有题目', list.length>0, 'len='+list.length);
  ok('初始有选项', document.querySelectorAll('.opt').length>=2);

  // 2. 选一个错误答案 -> 提交 -> 判错并给正确答案
  const q=list[0];
  const wrongLetter='ABCDEF'.split('').find(L=>!q.a.includes(L) && q.o['ABCDEF'.indexOf(L)]!==undefined);
  clickOpt(wrongLetter);
  const selAfter=document.querySelectorAll('.opt.sel').length;
  ok('点选后高亮', selAfter===1, 'sel='+selAfter);
  submit();
  ok('判分区出现', resultText().length>0, resultText());
  ok('错题提示正确答案', resultText().includes(q.a.join('')), resultText());
  ok('错题进入错题本', wrongSet.has(q.i));

  // 3. 下一题 + 正确答案判定
  document.getElementById('next').click();
  const q2=list[1];
  q2.a.forEach(L=>clickOpt(L));
  submit();
  ok('答对判定为正确', resultText().includes('回答正确'), resultText());
  ok('正确题不留在错题本', !wrongSet.has(q2.i));

  // 4. 标记
  document.getElementById('mark').click();
  ok('标记生效', markSet.has(q2.i));
  document.getElementById('mark').click();
  ok('取消标记', !markSet.has(q2.i));

  // 5. 章节筛选
  const target=CHAPS.find(c=>DATA.some(q=>q.c===c.name)).name;
  document.getElementById('ch').value=target;
  document.getElementById('start').click();
  ok('章节筛选全部命中', list.every(q=>q.c===target) && list.length>0, target+' n='+list.length);
  ok('章节筛选有题量', list.length>=5, 'n='+list.length);

  // 6. 题型筛选
  document.getElementById('ch').value='';
  document.getElementById('ty').value='判断';
  document.getElementById('start').click();
  ok('题型筛选', list.every(q=>q.y==='判断') && list.length>0, 'n='+list.length);

  // 7. 模拟卷
  document.getElementById('ty').value='';
  document.getElementById('mock').click();
  ok('模拟卷 85 题', list.length===85, 'len='+list.length);
  const c={}; list.forEach(q=>c[q.y]=(c[q.y]||0)+1);
  ok('模拟卷含三种题型', Object.keys(c).length===3, JSON.stringify(c));
  ok('模拟卷无重复', new Set(list.map(q=>q.i)).size===list.length);

  // 8. 数据完整性
  const badAns=DATA.filter(q=>!q.a.length||q.a.some(L=>'ABCDEF'.indexOf(L)>=q.o.length));
  ok('全部答案字母有效', badAns.length===0, badAns.length+' bad');
  const badOpt=DATA.filter(q=>q.o.length<2||q.o.some(t=>!t||!t.trim()));
  ok('全部选项非空', badOpt.length===0, badOpt.length+' bad');
  const dupStem=new Set(DATA.map(q=>q.s)); ok('题干无重复', dupStem.size===DATA.length, dupStem.size+'/'+DATA.length);
  const noChap=DATA.filter(q=>!q.c); ok('每题有章节', noChap.length===0, noChap.length+' bad');

  // 清除测试痕迹，避免污染真实错题本
  localStorage.removeItem('zdk_wrong_v1'); localStorage.removeItem('zdk_mark_v1');

  document.getElementById('testout').textContent =
    'PASS '+pass+' / FAIL '+fail+'  (共 '+(pass+fail)+' 项)\\n' + log.join('\\n');
  document.title = 'TEST pass='+pass+' fail='+fail;
})();
</script>
"""

html = html.replace("</body>", TEST + "</body>")
out = "work/quiz_test.html"
io.open(out, "w", encoding="utf-8").write(html)
print("wrote", out)
