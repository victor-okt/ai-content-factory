/** QA gates for actual acting shots and readable portrait subtitles. No rendering or TTS. */
export const SAFE={width:1080,height:1920,side:96,top:160,bottom:320,maxLines:2,maxChars:24};
const check=(ok,msg)=>{if(!ok)throw Error(msg)};
export function validateEpisode({shots}={}){
 check(Array.isArray(shots)&&shots.length>=3,'at least three shots required');
 let previous=0;
 for(const [i,shot] of shots.entries()){
  check(Number.isFinite(shot.start)&&Number.isFinite(shot.end)&&shot.end>shot.start,'invalid time '+i);
  check(Math.abs(shot.start-previous)<.001,'gap or overlap '+i);
  check(Array.isArray(shot.actions)&&shot.actions.some(a=>['walk','gesture','look','speak','blink','reach','turn','jump','fall','grab'].includes(a.type)),'character must act in shot '+i);
  check(!shot.cameraMotion||shot.cameraMotion==='locked','camera motion cannot replace acting '+i);
  check(!shot.bakedText,'subtitles must not be baked into illustrations '+i);
  previous=shot.end;
 }
 check(previous>=15&&previous<=60,'episode duration outside 15-60 seconds');
 return {duration:previous,shots:shots.length};
}
export function wrapSubtitle(text,maxChars=SAFE.maxChars){
 check(typeof text==='string'&&text.trim(),'subtitle required');
 const lines=[];let line='';
 for(const word of text.trim().split(/\s+/)){
  check(word.length<=maxChars,'word exceeds line width');
  if((line+' '+word).trim().length>maxChars){lines.push(line);line=word;}
  else line=(line+' '+word).trim();
 }
 if(line)lines.push(line);return lines;
}
export function timedSubtitles(words,{maxChars=SAFE.maxChars,maxLines=SAFE.maxLines}={}){
 check(Array.isArray(words)&&words.length>0,'timed words required');
 const cues=[];let group=[];
 const flush=()=>{if(!group.length)return;const lines=wrapSubtitle(group.map(x=>x.word).join(' '),maxChars);check(lines.length<=maxLines,'cue exceeds two lines');cues.push({start:group[0].start,end:group.at(-1).end,text:lines.join('\n')});group=[]};
 for(const word of words){
  check(typeof word.word==='string'&&Number.isFinite(word.start)&&Number.isFinite(word.end)&&word.end>word.start,'invalid word timestamp');
  check(!group.length||word.start>=group.at(-1).end,'overlapping words');
  const next=[...group,word];
  if(group.length&&(wrapSubtitle(next.map(x=>x.word).join(' '),maxChars).length>maxLines||word.end-group[0].start>3.2))flush();
  group.push(word);
 }
 flush();return cues;
}
export function subtitleSafeRect(width=SAFE.width,height=SAFE.height){
 check(width>0&&height>0,'invalid canvas');
 return {x:Math.round(SAFE.side*width/SAFE.width),y:Math.round((SAFE.height-SAFE.bottom)*height/SAFE.height),width:Math.round((SAFE.width-2*SAFE.side)*width/SAFE.width),height:Math.round(176*height/SAFE.height)};
}
