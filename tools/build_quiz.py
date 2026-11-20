"""Build a single-file offline quiz page from work/quiz_payload.json."""

import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

data = json.load(open("work/quiz_payload.json", encoding="utf-8"))

chapters = []
seen = set()
for q in data:
    if q["c"] not in seen:
        seen.add(q["c"])
        chapters.append({"code": q["cc"], "name": q["c"], "n": sum(1 for x in data if x["c"] == q["c"])})

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>正大杯网考题库 · 刷题自测</title>
<style>
:root{
  --bg:#f5f7fa; --card:#fff; --text:#1d2b36; --muted:#6b7c8c;
  --line:#e3e9ef; --accent:#1f5fa9; --accent-soft:#eaf2fb;
  --ok:#1f8a54; --ok-soft:#e6f5ec; --bad:#c0392b; --bad-soft:#fdecea;
  --warn:#b8860b; --warn-soft:#fdf6e3;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
  font-family:-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;
  line-height:1.65;-webkit-font-smoothing:antialiased}
.wrap{max-width:920px;margin:0 auto;padding:18px 16px 64px}
header{background:linear-gradient(135deg,#1f5fa9,#2f8fd0);color:#fff;
  padding:22px 16px 18px;margin:0 -16px 18px;border-radius:0 0 18px 18px}
.wrap > header{margin-left:-16px;margin-right:-16px}
header h1{margin:0 0 4px;font-size:20px;letter-spacing:.3px}
header p{margin:0;font-size:13px;opacity:.9}
.card{background:var(--card);border-radius:14px;padding:16px 18px;
  box-shadow:0 1px 3px rgba(20,40,60,.06);margin-bottom:14px}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
label.f{font-size:13px;color:var(--muted);margin-right:2px}
select,button{font:inherit;font-size:13px;border-radius:9px;border:1px solid var(--line);
  background:#fff;color:var(--text);padding:7px 11px;cursor:pointer;transition:.15s}
select:focus,button:focus{outline:2px solid var(--accent-soft);outline-offset:1px}
button:hover{border-color:var(--accent);color:var(--accent)}
button.primary{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:600}
button.primary:hover{background:#1a508f;color:#fff}
button.ghost{background:transparent}
.hint{font-size:12.5px;color:var(--muted);margin-top:8px}
.bar{display:flex;justify-content:space-between;align-items:center;
  font-size:13px;color:var(--muted);margin-bottom:10px;gap:10px;flex-wrap:wrap}
.tag{display:inline-block;font-size:11.5px;padding:2px 8px;border-radius:20px;
  background:var(--accent-soft);color:var(--accent);margin-right:6px;white-space:nowrap}
.tag.gray{background:#f0f2f5;color:#65727f}
.tag.warn{background:var(--warn-soft);color:var(--warn)}
.stem{font-size:16.5px;font-weight:600;margin:6px 0 16px;line-height:1.7}
.opt{display:flex;gap:10px;align-items:flex-start;padding:11px 13px;margin-bottom:9px;
  border:1px solid var(--line);border-radius:11px;cursor:pointer;transition:.12s;background:#fff}
.opt:hover{border-color:#b9cfe6;background:#fafcff}
.opt .k{flex:0 0 22px;height:22px;border-radius:50%;border:1.5px solid #c3cfda;
  display:flex;align-items:center;justify-content:center;font-size:12.5px;
  font-weight:600;color:var(--muted);margin-top:2px}
.opt.sel{border-color:var(--accent);background:var(--accent-soft)}
.opt.sel .k{background:var(--accent);border-color:var(--accent);color:#fff}
.opt.ok{border-color:var(--ok);background:var(--ok-soft)}
.opt.ok .k{background:var(--ok);border-color:var(--ok);color:#fff}
.opt.bad{border-color:var(--bad);background:var(--bad-soft)}
.opt.bad .k{background:var(--bad);border-color:var(--bad);color:#fff}
.res{margin-top:12px;padding:12px 14px;border-radius:11px;font-size:14px;display:none}
.res.show{display:block}
.res.ok{background:var(--ok-soft);color:#14663d}
.res.bad{background:var(--bad-soft);color:#8e2b21}
.res b{font-weight:700}
.foot{display:flex;gap:10px;justify-content:space-between;margin-top:16px;flex-wrap:wrap}
.foot .mid{display:flex;gap:8px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(34px,1fr));gap:6px;margin-top:10px}
.grid button{padding:0;height:32px;font-size:12px;border-radius:7px}
.grid button.done{background:var(--ok-soft);border-color:#a8d5bb;color:#14663d}
.grid button.cur{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:700}
.score{font-size:13px;color:var(--muted)}
.empty{text-align:center;color:var(--muted);padding:40px 10px;font-size:14px}
.kbd{font-size:11.5px;color:#8fa0af}
@media(max-width:560px){.stem{font-size:15.5px}.wrap{padding-bottom:40px}}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>正大杯网考题库 · 刷题自测</h1>
  <p>__TOTAL__ 道去重精编题 · 按本科考纲分章 · 离线可用，记录只存在本机浏览器</p>
</header>

<div class="card">
  <div class="row">
    <label class="f" for="ch">章节</label>
    <select id="ch"><option value="">全部章节</option></select>
    <label class="f" for="ty">题型</label>
    <select id="ty">
      <option value="">全部</option><option value="单选">单选</option>
      <option value="多选">多选</option><option value="判断">判断</option>
    </select>
    <label class="f" for="md">模式</label>
    <select id="md">
      <option value="seq">顺序练习</option>
      <option value="rand">随机打乱</option>
      <option value="wrong">只刷错题</option>
      <option value="mark">只刷标记题</option>
      <option value="mock">模拟卷（85 题）</option>
    </select>
    <button class="primary" id="start">开始 / 重排</button>
    <button class="ghost" id="mock">模拟卷 85 题</button>
  </div>
  <div class="hint">键盘：A–E 选项 · Enter 提交 / 下一题 · ← → 翻页 · 空格看答案</div>
</div>

<div class="card" id="stage">
  <div class="bar">
    <div id="meta"></div>
    <div class="score" id="score"></div>
  </div>
  <div id="body"><div class="empty">选择条件后点“开始 / 重排”</div></div>
  <div class="foot">
    <button id="prev">← 上一题</button>
    <div class="mid">
      <button id="mark" title="标记这题，稍后回看">标记</button>
      <button id="reveal">看答案</button>
      <button class="primary" id="submit">提交并看解析</button>
    </div>
    <button id="next">下一题 →</button>
  </div>
  <div class="grid" id="grid"></div>
</div>
</div>

<script>
const DATA = __DATA__;
const CHAPS = __CHAPS__;
const LS = {
  wrong:'zdk_wrong_v1', mark:'zdk_mark_v1', pos:'zdk_pos_v1'
};
const load = (k,d)=>{try{return JSON.parse(localStorage.getItem(k))??d}catch(e){return d}};
const save = (k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}};

let wrongSet = new Set(load(LS.wrong,[]));
let markSet  = new Set(load(LS.mark,[]));
let list = [], idx = 0, picked = new Set(), answered = new Map(), mode='seq';

const $ = id=>document.getElementById(id);
const chSel=$('ch'), tySel=$('ty'), mdSel=$('md');
CHAPS.forEach(c=>{
  const o=document.createElement('option');
  o.value=c.name;
  o.textContent=(c.code&&c.code.length<=2?c.code+' ':'')+c.name+'（'+c.n+'）';
  chSel.appendChild(o);
});

function buildList(){
  mode = mdSel.value;
  let arr = DATA.slice();
  if(mode==='mock'){
    arr = mockPaper();
  }else{
    if(chSel.value) arr = arr.filter(q=>q.c===chSel.value);
    if(tySel.value) arr = arr.filter(q=>q.y===tySel.value);
    if(mode==='wrong') arr = arr.filter(q=>wrongSet.has(q.i));
    if(mode==='mark')  arr = arr.filter(q=>markSet.has(q.i));
    if(mode==='rand')  arr = shuffle(arr);
  }
  list = arr; idx = 0; picked = new Set(); answered = new Map();
  renderGrid(); render();
}

function shuffle(a){
  a = a.slice();
  for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}
  return a;
}

function mockPaper(){
  // 贴近真实卷面：60% 单选 + 30% 多选 + 10% 判断 的题量比例，共 85 题
  const singles = shuffle(DATA.filter(q=>q.y==='单选')).slice(0,51);
  const multis  = shuffle(DATA.filter(q=>q.y==='多选')).slice(0,25);
  const judges  = shuffle(DATA.filter(q=>q.y==='判断')).slice(0,9);
  const pickedSingles = singles.slice(0,51);
  return shuffle([...pickedSingles,...multis,...judges]);
}

function renderGrid(){
  const g=$('grid'); g.innerHTML='';
  if(!list.length) return;
  // 题量大时按当前题分页显示题号，避免整屏铺满
  const PAGE=60;
  let start=0;
  if(list.length>PAGE){
    start=Math.max(0, Math.min(Math.floor(idx/PAGE)*PAGE, list.length-PAGE));
  }
  const end=Math.min(list.length, start+PAGE);
  if(list.length>PAGE){
    const info=document.createElement('div');
    info.style.cssText='grid-column:1/-1;font-size:12px;color:#6b7c8c;margin-bottom:2px';
    info.textContent='题号 '+(start+1)+'–'+end+' / 共 '+list.length+' 题';
    g.appendChild(info);
  }
  for(let i=start;i<end;i++){
    const q=list[i];
    const b=document.createElement('button');
    b.textContent=i+1;
    if(answered.has(q.i)) b.classList.add('done');
    if(i===idx) b.classList.add('cur');
    b.onclick=()=>{idx=i;picked=new Set(answered.get(list[i].i)||[]);answerVisible=false;render();renderGrid()};
    g.appendChild(b);
  }
}

function render(){
  if(!list.length){
    $('body').innerHTML='<div class="empty">这个条件下没有题目</div>';
    $('meta').textContent=''; $('score').textContent=''; return;
  }
  const q=list[idx];
  const done=[...answered.keys()].length;
  const right=[...answered.entries()].filter(([id,sel])=>sameSet(sel, DATA.find(d=>d.i===id).a)).length;
  $('meta').innerHTML='<span class="tag">'+esc(q.c)+'</span>'+
    (q.t?'<span class="tag gray">'+esc(q.t)+'</span>':'')+
    '<span class="tag gray">'+q.y+'</span>'+
    '<span class="kbd">第 '+(idx+1)+' / '+list.length+' 题</span>';
  $('score').textContent = done? ('已答 '+done+' 题 · 正确 '+right) : '';
  $('mark').textContent = markSet.has(q.i)?'已标记':'标记';

  let h='<div class="stem">'+esc(q.s)+'</div>';
  const shown = answered.has(q.i) || answerVisible;
  q.o.forEach((txt,i)=>{
    const L='ABCDEF'[i];
    let cls='opt';
    if(shown){
      if(q.a.includes(L)) cls+=' ok';
      else if(picked.has(L)) cls+=' bad';
    }else if(picked.has(L)) cls+=' sel';
    h+='<div class="'+cls+'" data-l="'+L+'"><div class="k">'+L+'</div><div>'+esc(txt)+'</div></div>';
  });
  if(shown){
    const ok = sameSet([...picked],q.a);
    h+='<div class="res show '+(ok?'ok':'bad')+'">'+
       (ok?'✓ 回答正确':'✗ 正确答案：<b>'+q.a.join('')+'</b>')+
       ' &nbsp;<span style="opacity:.75">'+ (q.k==='已核对'?'（本题答案经核算修正）': (q.k==='有争议'?'（题库内部答案存在分歧，建议回教材确认）':'')) +'</span></div>';
  }
  $('body').innerHTML=h;
  $('body').querySelectorAll('.opt').forEach(el=>{
    el.onclick=()=>{
      if(answered.has(q.i)||answerVisible) return;
      const L=el.dataset.l;
      if(q.a.length===1){ picked=new Set([L]); }
      else { picked.has(L)?picked.delete(L):picked.add(L); }
      render();
    };
  });
}

let answerVisible=false;

function sameSet(a,b){
  if(a.length!==b.length) return false;
  const s=new Set(a); return b.every(x=>s.has(x));
}

function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}

function submit(){
  if(!list.length) return;
  const q=list[idx];
  if(!picked.size){return}
  const ok= sameSet([...picked], q.a);
  answered.set(q.i,[...picked]);
  if(!ok) wrongSet.add(q.i); else wrongSet.delete(q.i);
  save(LS.wrong,[...wrongSet]);
  render(); renderGrid();
}

$('start').onclick=()=>{answerVisible=false;buildList()};
$('mock').onclick=()=>{mdSel.value='mock';answerVisible=false;buildList()};
$('prev').onclick=()=>{if(idx>0){idx--;picked=new Set(answered.get(list[idx].i)||[]);answerVisible=false;render();renderGrid()}};
$('next').onclick=()=>{if(idx<list.length-1){idx++;picked=new Set(answered.get(list[idx].i)||[]);answerVisible=false;render();renderGrid()}};
$('submit').onclick=submit;
$('reveal').onclick=()=>{if(list.length){answerVisible=true;render()}};
$('mark').onclick=()=>{
  if(!list.length) return;
  const id=list[idx].i;
  markSet.has(id)?markSet.delete(id):markSet.add(id);
  save(LS.mark,[...markSet]); render(); renderGrid();
};

document.addEventListener('keydown',e=>{
  if(!list.length) return;
  const k=e.key.toUpperCase();
  if('ABCDEF'.includes(k)&&k.length===1){
    const q=list[idx];
    if(answered.has(q.i)||answerVisible) return;
    const i='ABCDEF'.indexOf(k);
    if(i>=q.o.length) return;
    if(q.a.length===1) picked=new Set([k]); else {picked.has(k)?picked.delete(k):picked.add(k)}
    render(); e.preventDefault();
  }
  else if(e.key==='Enter'){ if(answered.has(list[idx].i)) $('next').click(); else submit(); }
  else if(e.key==='ArrowRight') $('next').click();
  else if(e.key==='ArrowLeft') $('prev').click();
  else if(e.code==='Space'){ $('reveal').click(); e.preventDefault(); }
});

buildList();
</script>
</body>
</html>
"""

html = TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
html = html.replace("__CHAPS__", json.dumps(chapters, ensure_ascii=False))
html = html.replace("__TOTAL__", str(len(data)))

out = "成果/正大杯网考题库精编/刷题自测.html"
open(out, "w", encoding="utf-8").write(html)
print("saved", out, len(html), "bytes;", len(data), "questions")
