'use strict';
function syncLanguageContext(){document.querySelectorAll('.languages a').forEach(link=>{link.href=link.href.split('?')[0]+location.search;});}
const filters=document.querySelector('#filters');
if(filters){
 const controls=['search','country','sector','stage'].map(k=>document.querySelector('#filter-'+k));
 const initial=new URLSearchParams(location.search);
 controls.forEach(c=>{const key=c.id.replace('filter-','');if(initial.has(key))c.value=initial.get(key);});
 function filter(update=true){
  const [search,country,sector,stage]=controls.map(c=>c.value);let count=0;
  document.querySelectorAll('#catalogue .project-row').forEach(row=>{
   row.hidden=!(row.dataset.search.toLocaleLowerCase().includes(search.trim().toLocaleLowerCase()) && (country==='all'||row.dataset.country===country) && (sector==='all'||row.dataset.sector===sector) && (stage==='all'||row.dataset.stage===stage));if(!row.hidden)count++;
  });
  const results=document.querySelector('#results');results.textContent=results.dataset.label+': '+count;document.querySelector('#empty').hidden=count!==0;
  if(update){const params=new URLSearchParams();controls.forEach(c=>{if(c.value&&c.value!=='all')params.set(c.id.replace('filter-',''),c.value);});history.replaceState(null,'',location.pathname+(params.size?'?'+params:''));syncLanguageContext();}
 }
 filters.addEventListener('submit',event=>event.preventDefault());controls.forEach(c=>c.addEventListener(c.type==='search'?'input':'change',()=>filter()));filter(false);
}
// Keep filter and enquiry context when switching languages; record paths already match.
syncLanguageContext();
const enquiry=document.querySelector('#enquiry');
if(enquiry){
 const parameters=new URLSearchParams(location.search);
 if(parameters.get('topic')==='project')enquiry.elements.topic.value='project';
 let project=parameters.get('project')||'';

 enquiry.elements.project_id.value=project;if(project){enquiry.elements.topic.value='project';enquiry.elements.message.value=project+' — ';}
 enquiry.addEventListener('submit',event=>{
  event.preventDefault();if(!enquiry.reportValidity())return;
  const data=new FormData(enquiry);const recipient=data.get('topic')==='project'?'project@koreacentralasia.com':'info@koreacentralasia.com';
  const subject='KCAP enquiry'+(project?' · '+project:'');
  const body=['Language: '+enquiry.dataset.language,'Project: '+(data.get('project_id')||'—'),'Name: '+data.get('name'),'Organisation: '+data.get('organisation'),'Email: '+data.get('email'),'',''+data.get('message')].join('\n');
  const mailto=document.createElement('a');mailto.href='mailto:'+recipient+'?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);mailto.click();
  document.querySelector('#form-status').textContent={en:'Email prepared. Complete sending in your email app.',ko:'이메일을 작성했습니다. 이메일 앱에서 전송을 완료해 주세요.',ru:'Письмо подготовлено. Завершите отправку в почтовой программе.'}[enquiry.dataset.language];
 });
}
function clocks(){document.querySelectorAll('[data-zone]').forEach(el=>{el.textContent=new Intl.DateTimeFormat('en-GB',{timeZone:el.dataset.zone,hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(new Date());});}clocks();if(document.querySelector('[data-zone]'))setInterval(clocks,30000);
