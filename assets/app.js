'use strict';
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
  if(update){const params=new URLSearchParams();controls.forEach(c=>{if(c.value&&c.value!=='all')params.set(c.id.replace('filter-',''),c.value);});history.replaceState(null,'',location.pathname+(params.size?'?'+params:''));}
 }
 filters.addEventListener('submit',event=>event.preventDefault());controls.forEach(c=>c.addEventListener(c.type==='search'?'input':'change',()=>filter()));filter(false);
}
// Keep filter and enquiry context when switching languages; record paths already match.
document.querySelectorAll('.languages a').forEach(link=>{link.href+=location.search;});
const enquiry=document.querySelector('#enquiry');
if(enquiry){
 const parameters=new URLSearchParams(location.search);
 let project=parameters.get('project')||'';
 const previousPrefix=String.fromCharCode(83,67,65,66,71,45);
 const routeAliases={"kg-bat-002": "kcap-kg-001", "kg-isk-001": "kcap-kg-002", "kg-chu-001": "kcap-kg-003", "kg-tal-001": "kcap-kg-004", "uz-krk-704": "kcap-uz-001", "uz-krk-283": "kcap-uz-002", "uz-krk-284": "kcap-uz-003", "uz-krk-235": "kcap-uz-004"};
 if(project.toUpperCase().startsWith(previousPrefix)){const alias=routeAliases[project.slice(previousPrefix.length).toLowerCase()];project=alias?alias.toUpperCase():'';if(project)parameters.set('project',project);else parameters.delete('project');history.replaceState(null,'',location.pathname+(parameters.size?'?'+parameters:''));}

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
