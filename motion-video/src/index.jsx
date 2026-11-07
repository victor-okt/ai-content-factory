import React from 'react';
import {Composition, registerRoot, useCurrentFrame, useVideoConfig, interpolate, spring, AbsoluteFill} from 'remotion';

const scenes = [
  {start:0,end:180,caption:'Setiap malam, pintu itu mengetuk sendiri.',sub:'KETUKAN PERTAMA',light:'#1b2838'},
  {start:180,end:360,caption:'Padahal rumah itu sudah kosong 20 tahun.',sub:'RUMAH KOSONG',light:'#18202d'},
  {start:360,end:540,caption:'Aku memberanikan diri membuka pintunya.',sub:'JANGAN DIBUKA',light:'#273047'},
  {start:540,end:720,caption:'Di baliknya, ada seseorang yang mirip aku.',sub:'SIAPA DIA?',light:'#3b2534'},
  {start:720,end:900,caption:'Dia berbisik: jangan lihat ke belakang.',sub:'JANGAN MENENGOK',light:'#381e2a'},
];
const ease=(n,a,b)=>Math.max(0,Math.min(1,(n-a)/(b-a)));
function HorrorShort(){
 const frame=useCurrentFrame(); const {fps}=useVideoConfig();
 const idx=Math.min(4,Math.floor(frame/180)); const s=scenes[idx]; const local=frame-s.start;
 const pulse=Math.sin(frame*.16)*4; const zoom=interpolate(local,[0,180],[1,1.1]);
 const reveal=idx>=3; const doorOpen=idx>=2?interpolate(local,[0,100],[0,idx===2?64:70],{extrapolateRight:'clamp'}):0;
 const textOpacity=Math.min(1,ease(local,8,30),ease(s.end-frame,0,22));
 return <AbsoluteFill style={{backgroundColor:s.light,fontFamily:'Arial,sans-serif',color:'#fff',overflow:'hidden'}}>
  <AbsoluteFill style={{background:'radial-gradient(ellipse at 50% 42%, #53607755, transparent 65%)',transform:`scale(${zoom})`}}/>
  <div style={{position:'absolute',top:135,left:100,right:100,textAlign:'center',fontSize:38,letterSpacing:7,color:'#ffd769',fontWeight:800}}>CERITA TENGAH MALAM</div>
  <div style={{position:'absolute',top:350,left:125,width:830,height:1060,background:'#111824',border:'22px solid #495164',borderRadius:20,boxShadow:'0 0 120px #000'}}>
   <div style={{position:'absolute',inset:30,background:'#070b12'}}/>
   {reveal&&<div style={{position:'absolute',left:300,top:290,width:170,height:250,opacity:ease(local,5,55),transform:`translateY(${pulse}px)`}}>
     <div style={{width:130,height:130,borderRadius:'50%',background:'#b3a8a0',margin:'auto',boxShadow:'0 0 30px #f77'}}/>
     <div style={{height:160,background:'#111',borderRadius:'55% 55% 0 0'}}/>
     <div style={{position:'absolute',top:60,left:58,width:12,height:8,background:'#ff344b',boxShadow:'40px 0 #ff344b'}}/>
   </div>}
   <div style={{position:'absolute',inset:0,width:`${100-doorOpen}%`,background:'linear-gradient(90deg,#313948,#182130)',borderRight:'12px solid #68768a',boxShadow:'20px 0 40px #0009'}}>
    <div style={{position:'absolute',right:65,top:520,width:24,height:24,borderRadius:'50%',background:'#ffd769',boxShadow:'0 0 20px #ffdf88'}}/>
   </div>
  </div>
  <div style={{position:'absolute',left:170,top:1100,width:150,height:320,transform:`translateX(${Math.sin(frame*.055)*8}px)`}}>
   <div style={{position:'absolute',left:27,top:0,width:96,height:105,background:'#d8b9a4',borderRadius:'50% 50% 42% 42%'}}/>
   <div style={{position:'absolute',left:10,top:80,width:130,height:230,background:'#202a39',borderRadius:'50% 50% 10% 10%'}}/>
   <div style={{position:'absolute',left:55,top:46,width:10,height:7,background:'#111',boxShadow:'34px 0 #111'}}/>
  </div>
  <div style={{position:'absolute',left:75,right:75,bottom:255,textAlign:'center',opacity:textOpacity}}>
   <div style={{fontSize:35,color:'#ffd769',fontWeight:800,letterSpacing:5,marginBottom:22}}>{s.sub}</div>
   <div style={{fontSize:63,lineHeight:1.2,fontWeight:900,textShadow:'0 5px 14px #000, 0 0 30px #000',background:'#0008',padding:22,borderRadius:22}}>{s.caption}</div>
  </div>
  <div style={{position:'absolute',bottom:80,left:75,right:75,height:7,background:'#ffffff33',borderRadius:9}}>
   <div style={{height:'100%',width:`${frame/900*100}%`,background:'#ffd769',borderRadius:9}}/>
  </div>
 </AbsoluteFill>;
}
const Root=()=> <Composition id="HorrorShort" component={HorrorShort} durationInFrames={900} fps={30} width={1080} height={1920}/>;
registerRoot(Root);
