(function () {
"use strict";
var container=document.querySelector("main");
if(!container)return;
var css=document.createElement("style");
css.textContent = [
"#factory-panel {margin-top:16px;padding:16px;background:#1b2f48;border:2px solid #55758e;color:#d8edf7;box-shadow:4px 4px 0 #0d182a}",
"#factory-panel button {cursor:pointer;font-family:inherit}",
"#factory-panel .fh {font-weight:900;color:#a4edce;letter-spacing:.05em;font-size:16px}",
"#factory-panel .sub {font-size:11px;color:#b3ccdc;line-height:1.7}",
"#factory-panel .as {display:grid;grid-template-columns:repeat(auto-fit,minmax(135px,1fr));gap:7px;margin:13px 0}",
"#factory-panel .agent {background:#263f59;border:1px solid #58728c;padding:9px;font-size:11px;line-height:1.5;min-height:75px}",
"#factory-panel .agent .nm {font-weight:900;color:#f1e1ba;display:block}",
"#factory-panel .agent .st {color:#a5dfd2;display:block;font-size:10px;margin-top:6px}",
"#factory-panel .job {border:1px solid #476a80;background:#263951;color:#f0f3f0;padding:9px;margin:5px 0;display:block;text-align:left;width:100%;font-size:11px;line-height:1.6}",
"#factory-panel .job.selected {border:2px solid #a5eccd;background:#24534f}",
"#factory-panel .detail {background:#152a42;border:1px solid #527790;padding:12px;margin-top:11px;font-size:11px;line-height:1.7}",
"#factory-panel .detail h3 {color:#f4dba7;font-size:14px;margin:0 0 7px}",
"#factory-panel .rowline {margin:5px 0;border-bottom:1px dashed #465e78;padding-bottom:6px}",
"#factory-panel .copy {border:0;border-bottom:3px solid #547b72;color:#1c3f35;background:#acebd3;padding:7px 12px;font-size:10px;font-weight:900}",
"#factory-panel .warn {color:#ffd79d;font-size:10px;line-height:1.6;margin-top:8px}",
"#factory-panel a {color:#9beed8}",
"#factory-panel .gridbody {display:grid;grid-template-columns:minmax(180px,1fr) minmax(230px,1.7fr);gap:12px}",
"@media(max-width:620px){#factory-panel .gridbody{grid-template-columns:1fr}}",
].join("\n");
document.head.append(css);
var panel=document.createElement("section");
panel.id="factory-panel";
panel.setAttribute("aria-label","AI Content Factory production desk");
container.append(panel);
function node(tag,cls,text){
 var element=document.createElement(tag);
 if(cls)element.className=cls;
 if(text!==undefined)element.textContent=String(text);
 return element;
}
var title=node("div","fh","▣ STUDIO PRODUKSI / AGENT 2–6");
var explanation=node("p","sub","Klik konsep untuk melihat kerja tiap agent. Semua skrip dan prompt saat ini disusun otomatis dengan template gratis; belum memakai generator AI video berbayar.");
var stats=node("p","sub","Memuat status pekerjaan...");
var agents=node("div","as");
var grid=node("div","gridbody");
var ideas=node("div");
var detail=node("div","detail");
grid.append(ideas,detail);
var caution=node("p","warn","PERHATIAN: Karakter bergerak adalah tampilan game. Munculnya prompt tidak berarti gambar/video sudah dirender atau konten sudah diposting.");
var refresh=node("button","copy","↻ PERBARUI STATUS");
refresh.type="button";
refresh.setAttribute("aria-label","Muat ulang data produksi dari GitHub Pages");
panel.append(title,explanation,refresh,stats,agents,grid,caution);
var data=null;
var selected="";
try{selected=localStorage.getItem("acf-pixel-office-selected-idea")||""}catch(e){}
function field(parent,label,value){
 var line=node("div","rowline");var strong=node("b","",label+": ");line.append(strong,document.createTextNode(String(value||"—")));parent.append(line);
}
function showDetail(job){
 detail.replaceChildren();
 if(!job){detail.append(node("p","sub","Belum ada draft. Nova perlu menghasilkan ide dahulu."));return;}
 detail.append(node("h3","",job.title));
 field(detail,"Asal ide",job.origin);
 field(detail,"Hook Kai",job.creative_director?.hook);
 field(detail,"Akhir cerita",job.creative_director?.big_idea);
 (job.creative_director?.storyboard||[]).forEach(function(shot){
  field(detail,"Adegan "+shot.shot+" ("+shot.seconds.join("–")+" detik)",shot.description);
 });
 var prompt=String(job.visual_creator?.image_prompt||"");
 field(detail,"Prompt Mira",prompt);
 if(prompt){var cp=node("button","copy","SALIN PROMPT VISUAL");cp.onclick=function(){
 if(navigator.clipboard?.writeText){navigator.clipboard.writeText(prompt).then(()=>{cp.textContent="✓ TERSALIN"}).catch(()=>{cp.textContent="SALIN SECARA MANUAL"})}
 };detail.append(cp);}
 field(detail,"Rencana Rio",job.video_producer?.editing_notes);
 field(detail,"Caption Sora",job.publisher?.caption_draft);
 field(detail,"Analisis Dex",job.analyst?.blocker);
 var link=job.source_url;
 if(/^https?:\/\//.test(link||"")){var a=node("a","","↗ LIHAT REFERENSI ASLI");a.href=link;a.target="_blank";a.rel="noopener noreferrer";detail.append(a);}
 detail.append(node("p","warn","Status saat ini: render belum dijalankan, posting belum dilakukan, views dan pendapatan belum tersedia."));
}
function draw(){
 agents.replaceChildren();ideas.replaceChildren();
 var mode=data?.mode||"no_ideas";
 stats.textContent="MODE: "+(mode==="public_research"?"REFERENSI PUBLIK":mode==="editorial_lab"?"EKSPERIMEN INTERNAL":"BELUM ADA IDE")+
  " • "+(data?.draft_count||0)+" paket draft • "+(data?.generated_at?new Date(data.generated_at).toLocaleString("id-ID"):"belum diperiksa");
 (data?.agents||[]).forEach(function(agent,i){
  var el=node("div","agent");
  el.append(node("span","nm",(i+1).toString().padStart(2,"0")+" · "+agent.name.toUpperCase()));
  el.append(node("span","",agent.role));
  el.append(node("span","st","● "+agent.status.replaceAll("_"," ").toUpperCase()));
  agents.append(el);
 });
 var queue=Array.isArray(data?.jobs)?data.jobs:[];
 if(!queue.length){ideas.append(node("p","sub","Belum ada ide yang bisa diproses."));showDetail(null);return;}
 if(!queue.some(x=>x.content_id===selected))selected=queue[0].content_id;
 queue.forEach(function(job){
  var btn=node("button","job"+(job.content_id===selected?" selected":""),job.title+" · "+job.origin);
  btn.onclick=function(){
   selected=job.content_id;
   try{localStorage.setItem("acf-pixel-office-selected-idea",selected)}catch(e){}
   draw();
  };
  ideas.append(btn);
 });
 showDetail(queue.find(x=>x.content_id===selected));
}
async function load(){
 refresh.disabled=true;
 refresh.textContent="MEMUAT...";
 try{
  var response=await fetch("./data/factory.json?ts="+Date.now(),{cache:"no-store"});
  if(!response.ok)throw new Error("HTTP "+response.status);
  var incoming=await response.json();
  if(incoming.schema_version!==1||!Array.isArray(incoming.jobs))throw new Error("Invalid contract");
  data=incoming;
  draw();
 }catch(e){
  stats.textContent="Rencana produksi belum tersedia. Akan muncul setelah proses GitHub berikutnya.";
  detail.textContent="Info: "+String(e.message||e);
 }finally{
  refresh.disabled=false;
  refresh.textContent="↻ PERBARUI STATUS";
 }
}
refresh.onclick=load;
load();
window.addEventListener("storage",function(e){if(e.key==="acf-pixel-office-selected-idea"){selected=e.newValue||"";if(data)draw()}});
})();
