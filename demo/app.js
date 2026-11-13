"use strict";
const $=id=>document.getElementById(id);
const labels={all:"All groups",workforce:"General workforce",creatives:"Creative professionals",scientists:"Scientists",injected_decline:"Known decline at turn 7",flat:"Flat control",noisy_flat:"Noisy flat control"};
const methods={euclidean:"Largest absolute change",percentage:"Largest relative decline",curvature:"Change in slope",direction:"Change in direction"};
function fillGroups(){
  const dataset=$('dataset').value;
  const groups=Object.keys(window.EXAMPLE_DATA[dataset].cohorts).filter(k=>dataset==='public'||k!=='all');
  $('cohort').replaceChildren(...groups.map(k=>new Option(labels[k]||k,k)));
  if(dataset==='synthetic')$('cohort').value='injected_decline';
  render();
}
function draw(rows){
  const svg=$('chart');
  svg.replaceChildren();
  const width=Math.max(300,Math.min(900,svg.clientWidth||900));
  svg.setAttribute('viewBox',`0 0 ${width} 300`);
  const ns='http://www.w3.org/2000/svg';
  function node(tag,attrs,text){const e=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));if(text!==undefined)e.textContent=text;svg.append(e);return e;}
  node('title',{id:'chart-title'},'Average participant response length by turn');
  node('desc',{id:'chart-desc'},rows.length?rows.map(r=>`Turn ${r.turn}: ${r.mean_words.toFixed(1)} words from ${r.n} responses.`).join(' '):'No turns meet the minimum of 100 responses.');
  if(!rows.length){node('text',{x:width/2,y:150,'text-anchor':'middle',fill:'#596961','font-size':width<500?12:18},'No turns meet the 100-response minimum.');return;}
  const left=42,right=width-15,top=22,bottom=250,maxY=Math.max(10,...rows.map(r=>r.mean_words))*1.12;
  const minX=rows[0].turn,maxX=rows.at(-1).turn;
  const x=k=>left+(k-minX)/(maxX-minX||1)*(right-left),y=v=>bottom-v/maxY*(bottom-top);
  for(let i=0;i<=4;i++){const value=maxY*i/4;node('line',{x1:left,x2:right,y1:y(value),y2:y(value),stroke:'#e2e9e4'});node('text',{x:left-10,y:y(value)+4,'text-anchor':'end',fill:'#596961','font-size':13},String(Math.round(value)));}
  for(const [i,r] of rows.entries()){if(width<500&&rows.length>12&&i%2&&i!==rows.length-1)continue;node('text',{x:x(r.turn),y:bottom+23,'text-anchor':'middle',fill:'#596961','font-size':13},String(r.turn));}
  // A gap is not connected across a suppressed or missing turn.
  let path='';rows.forEach((r,i)=>{path+=`${i&&r.turn===rows[i-1].turn+1?'L':'M'}${x(r.turn)},${y(r.mean_words)} `;});
  node('path',{d:path,fill:'none',stroke:'#185444','stroke-width':3});
  rows.forEach(r=>node('circle',{cx:x(r.turn),cy:y(r.mean_words),r:4,fill:'#185444'}));
  node('text',{x:(left+right)/2,y:bottom+48,'text-anchor':'middle',fill:'#596961','font-size':14},'Participant response number');
}
function render(){
  const dataset=$('dataset').value,group=$('cohort').value,scenario=$('scenario').value;
  const study=window.EXAMPLE_DATA[dataset],value=study.cohorts[group][scenario];
  $('source-label').textContent=dataset==='public'?'Public research example':'Synthetic check';
  $('context').textContent=dataset==='public'?`Source release: 1,250 interviews; ${study.user_turns.toLocaleString()} parsed participant response slots, including three with zero words. Choose a group to see whether the same pattern shows up when you look at the groups separately.`:'These generated response counts use a fixed random seed. One example has a decline starting at turn 7. The flat and noisy-flat examples let you see what the methods flag when no decline was intended.';
  draw(value.rows);
  $('methods').replaceChildren(...Object.entries(methods).map(([key,label])=>{const div=document.createElement('div');div.className='method';const a=document.createElement('span'),b=document.createElement('strong');a.textContent=label;const result=value.detection.methods[key];b.textContent=result?`Turn ${result.turn}`:'No cue';div.append(a,b);return div;}));
  const candidates=[...new Set(Object.values(value.detection.methods).filter(Boolean).map(v=>v.turn))].sort((a,b)=>a-b);
  $('interpretation').textContent=group==='noisy_flat'?'This example has no intended downward trend, and the methods still flag a change. That\'s why I\'d read the surrounding conversation before interpreting a flagged turn as disengagement.':!value.rows.length?'This view doesn\'t have enough responses to run these checks. I\'d need to consider a different threshold as a separate analysis decision.':!candidates.length?'The methods didn\'t flag a downward change in the turns that meet the response-count threshold. That doesn\'t tell us whether everyone stayed engaged.':`Review cue${candidates.length>1?'s':''}: turn${candidates.length>1?'s':''} ${candidates.join(', ')}. Read the surrounding questions and responses before deciding what the pattern means.`;
  $('rows').replaceChildren(...value.rows.map(r=>{const tr=document.createElement('tr');[r.turn,r.n,r.mean_words.toFixed(1),r.median_words.toFixed(1)].forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.append(td);});return tr;}));
}
$('dataset').addEventListener('change',fillGroups);$('cohort').addEventListener('change',render);$('scenario').addEventListener('change',render);fillGroups();
