/** Offline RIFF WAV PCM16/float32 amplitude -> mouth-open timing. */
const clamp=(v,lo,hi)=>Math.max(lo,Math.min(hi,v));
export function analyzeWav(input,{frameMs=20,threshold=0.035,minActiveMs=60,mergeGapMs=80}={}){
 if(!Number.isFinite(frameMs)||frameMs<5||frameMs>100)throw Error('frameMs must be 5..100');
 const buf=Buffer.isBuffer(input)?input:Buffer.from(input);
 if(buf.length<44||buf.toString('ascii',0,4)!=='RIFF'||buf.toString('ascii',8,12)!=='WAVE')throw Error('RIFF WAVE required');
 let fmt=null,data=null,at=12;
 while(at+8<=buf.length){const tag=buf.toString('ascii',at,at+4),size=buf.readUInt32LE(at+4),start=at+8;if(start+size>buf.length)throw Error('truncated WAV chunk');if(tag==='fmt '){if(size<16)throw Error('invalid fmt');fmt={format:buf.readUInt16LE(start),channels:buf.readUInt16LE(start+2),sampleRate:buf.readUInt32LE(start+4),blockAlign:buf.readUInt16LE(start+12),bits:buf.readUInt16LE(start+14)};}if(tag==='data')data={start,size};at=start+size+(size%2);}
 if(!fmt||!data)throw Error('missing fmt/data');
 const {format,channels,sampleRate,blockAlign,bits}=fmt;
 if(!(format===1&&bits===16||format===3&&bits===32)||channels<1||channels>8||sampleRate<8000||sampleRate>192000||blockAlign!==channels*bits/8)throw Error('unsupported WAV format');
 const sampleCount=Math.floor(data.size/blockAlign),windowSamples=Math.max(1,Math.round(sampleRate*frameMs/1000));const frames=[];
 for(let base=0;base<sampleCount;base+=windowSamples){const count=Math.min(windowSamples,sampleCount-base);let sum=0;for(let i=0;i<count;i++){let mixed=0;for(let c=0;c<channels;c++){const pos=data.start+(base+i)*blockAlign+c*bits/8;mixed+=(format===1?buf.readInt16LE(pos)/32768:buf.readFloatLE(pos))/channels;}sum+=mixed*mixed;}frames.push({start:base/sampleRate,end:(base+count)/sampleRate,rms:Math.sqrt(sum/count)});}
 const raw=[];let segment=null;for(const f of frames){if(f.rms>=threshold){if(!segment)segment={start:f.start,end:f.end,peak:f.rms};else{segment.end=f.end;segment.peak=Math.max(segment.peak,f.rms)}}else if(segment){raw.push(segment);segment=null}}if(segment)raw.push(segment);
 const merged=[];for(const s of raw){const last=merged.at(-1);if(last&&s.start-last.end<=mergeGapMs/1000){last.end=s.end;last.peak=Math.max(last.peak,s.peak)}else merged.push({...s});}
 const syllables=merged.filter(s=>s.end-s.start>=minActiveMs/1000).map(s=>({start:+s.start.toFixed(4),end:+s.end.toFixed(4),energy:+clamp(s.peak*3,0.1,1).toFixed(3)}));return {sampleRate,channels,duration:sampleCount/sampleRate,frames,syllables};
}
