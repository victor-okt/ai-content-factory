(function(){
'use strict';
var data=null;
var ideas=document.getElementById('ideas');
var status=document.getElementById('agent-status');
function setText(id,value){var x=document.getElementById(id);if(x)x.textContent=String(value);}
function isNova(){return (document.getElementById('agent-code')?.textContent||'').includes('01');}
function apply(){
 if(!isNova())return;
 var list=Array.isArray(data?.ideas)?data.ideas:[];
 status.textContent='● '+(data?.status==='stale'?'LAPORAN LAMA • SUMBER ERROR':String(data?.status||'MENUNGGU LAPORAN').toUpperCase());
 setText('agent-results',list.length+' ide • '+(data?.quality_control?.items_scanned ?? '?')+' sinyal dicek');
 setText('agent-data',data?.last_checked_at?new Date(data.last_checked_at).toLocaleString('id-ID'):'Belum diperiksa');
 setText('agent-next',data?.errors?.length?'Sebagian sumber bermasalah':list.length?'Baca laporan':'Menunggu hasil riset');
 setText('agent-help','Gerakan karakter hanya animasi. Hasil berasal dari Google Trends dan liputan publik, bukan statistik views TikTok.');
 var button=document.getElementById('open-results');if(button)button.textContent='▤ BUKA LAPORAN';
}
function render(){
 ideas.replaceChildren();
 var list=Array.isArray(data?.ideas)?data.ideas:[];
 var warning=document.querySelector('#results .warning');
 if(warning)warning.textContent='DIPERIKSA '+(data?.quality_control?.items_scanned??'?')+' SUMBER ITEM • '+(data?.disclaimer||'Bukan metrik viral TikTok.')+(data?.errors?.length?' Kendala: '+data.errors.join('; ').slice(0,160):'');
 if(!list.length){
  var blank=document.createElement('p');blank.className='warning';blank.textContent='Belum ada ide hasil riset. Jalankan workflow Trend Hunter di GitHub Actions untuk mengisi laporan.';ideas.append(blank);return;
 }
 list.slice(0,20).forEach(function(item){
  var card=document.createElement('article');card.className='idea';
  var score=document.createElement('div');score.className='score';score.textContent='★ '+String(item.score)+'/100 • KECOCOKAN IDE';
  var title=document.createElement('b');title.textContent=item.title||'Tanpa judul';
  var concept=document.createElement('p');concept.textContent=item.concept||'';
  var source=document.createElement('small');source.textContent=(item.signal_source||'Sumber publik')+' · '+(item.observed_at||'');
  var proof=document.createElement('small');proof.textContent=item.evidence_label||'Bukan data viral TikTok.';
  var link=document.createElement('a');var url=String(item.source_url||'');
  if(/^https?:\/\//i.test(url)){link.href=url;link.target='_blank';link.rel='noopener noreferrer';link.textContent='↗ LIHAT SUMBER';link.style.color='#a6efd5';}
  var choose=document.createElement('button');choose.className='pixel-btn secondary';choose.textContent='PILIH IDE';
  choose.onclick=function(){ideas.querySelectorAll('.idea').forEach(function(el){el.classList.remove('chosen')});card.classList.add('chosen');setText('feedback','Ide dipilih pada tampilan ini saja. Belum dikirim ke Agent 2 atau tersimpan di server.');};
  var why=document.createElement('small');why.textContent=Array.isArray(item.why_recommended)?'Alasan: '+item.why_recommended.slice(0,2).join(' · '):'Sumber publik, tidak menjamin viral.';
  card.append(score,title,concept,source,proof,why,link,choose);ideas.append(card);
 });
}
async function load(){
 try{
  var response=await fetch('./data/latest.json?nocache='+Date.now(),{cache:'no-store'});
  if(!response.ok)throw new Error('HTTP '+response.status);
  var parsed=await response.json();
  if(parsed.schema_version!==1||!Array.isArray(parsed.ideas))throw new Error('Format laporan tidak sesuai');
  data=parsed;
 }catch(error){data={schema_version:1,status:'error',ideas:[],errors:[String(error)]};}
 var chip=document.querySelector('.chip.demo');
 if(chip)chip.textContent='SUMBER PUBLIK • '+String(data.status).toUpperCase();
 render();apply();
}
ideas.replaceChildren();
var loading=document.createElement('p');loading.textContent='Memuat laporan riset publik...';ideas.append(loading);
var canvas=document.getElementById('office');
if(canvas)canvas.addEventListener('click',()=>requestAnimationFrame(apply));
load();
})();