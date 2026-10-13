"""Dependency-free multilingual KCAP static site builder."""
import os,json,html,shutil,hashlib,re
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'dist'
LANGS=('en','ko','ru')
BASE=os.environ.get('BASE_PATH','').rstrip('/')
ORIGIN=os.environ.get('SITE_ORIGIN','').rstrip('/')
PUBLIC=os.environ.get('PUBLIC_RELEASE')=='1'
def load(name):return json.loads((ROOT/'content'/f'{name}.json').read_text())
COPY=load('pages');PROJECTS=load('projects');NEWS=load('news');SECTORS=load('sectors')['sectors']
PROJECTS=[p for p in PROJECTS if p.get('publication_status')=='published']
NEWS=[n for n in NEWS if n.get('publication_status')=='published']
CONFIG=load('release')
for sector in SECTORS:COPY[sector['key']]=sector['title']
if PUBLIC and not CONFIG.get('korean_review_approved'):raise SystemExit('Public release blocked: Korean copy requires Sergey review.')
def e(v):return html.escape(str(v),quote=True)
def t(k,l):return COPY.get(k,{}).get(l,{'en':'Translation pending','ko':'번역 준비 중','ru':'Перевод готовится'}[l])
def url(l,path=''):return BASE+'/'+l+'/'+path.strip('/')+('/' if path else '')
def img(name):
 asset=ROOT/'assets'/name
 version='?v='+hashlib.sha256(asset.read_bytes()).hexdigest()[:10] if asset.is_file() and name.endswith(('.css','.js')) else ''
 return BASE+'/assets/'+name+version
def a(label,href,cls=''):return f'<a class="{cls}" href="{e(href)}">{e(label)}</a>'
def link(k,l,path,cls='text-link'):return a(t(k,l),url(l,path),cls)
def section(content,cls='section'):return f'<section class="{cls}">{content}</section>'
def intro(k,l,copy=None,subtitle=None):return section(f'<div class="eyebrow">KCAP / {e(t(k,l))}</div><h1>{e(t(k,l))}</h1>'+ (f'<h2>{e(t(subtitle,l))}</h2>' if subtitle else '')+ (f'<p>{e(t(copy,l))}</p>' if copy else ''),'page-intro')
def note(k,l):return f'<p class="note">{e(t(k,l))}</p>'
def projectcard(p,l):
 path='projects/'+p['slug']
 search=' '.join([p['id'],*p['title'].values(),*p['description'].values(),*p['location'].values(),t(p['country'],l),t(p['sector'],l)])
 return f'<article class="project-row" data-country="{p["country"]}" data-sector="{p["sector"]}" data-stage="{p["stage"]}" data-search="{e(search)}"><div class="eyebrow">{e(t(p["sector"],l))}</div><a class="project-title" href="{url(l,path)}"><h3>{e(p["title"].get(l,t("pending",l)))}</h3><span aria-hidden="true">↗</span></a><p>{e(p["description"].get(l,t("pending",l)))}</p><div class="submeta"><span class="badge">{e(t(p["country"],l))}</span><span class="badge">{e(t(p["stage"],l))}</span></div></article>'
def newsdate(n,l):return n.get('event_date') or n['source_date']
def newscard(n,l):
 photo=f'<a class="news-media" href="{url(l,"news/"+n["id"])}" tabindex="-1" aria-hidden="true"><img class="news-photo" loading="lazy" width="960" height="1280" src="{img("uzbekistan-korea-forum-2026.jpg")}" alt="{e(n["caption"][l])}"></a>' if n.get('image_asset') else ''
 return f'<article class="news-item {"with-image" if photo else "without-image"}">{photo}<div class="news-content"><div class="news-metadata"><span class="eyebrow badge">{e(t(n["category"],l))}</span><time class="news-date badge" datetime="{newsdate(n,l)}">{newsdate(n,l)}</time></div><div class="news-copy"><h3>{a(n["title"][l],url(l,"news/"+n["id"]))}</h3><p>{e(n["summary"][l])}</p></div><span class="arrow" aria-hidden="true">↗</span></div></article>'
def sectors(l):return '<div class="sector-grid">'+''.join(f'<a class="sector-tile" href="{url(l,"projects")}?sector={s["key"]}"><span class="eyebrow">{i+1:02}</span><h3>{e(s["title"][l])}</h3><p>{e(s["description"][l])}</p><span class="sector-arrow" aria-hidden="true">↗</span></a>' for i,s in enumerate(SECTORS))+'</div>'
def process(l):
 return '<div class="section-heading"><h2>'+e(t('processHeading',l))+'</h2>'+link('talk',l,'contact')+'</div><div class="steps">'+''.join(f'<div class="step"><div class="marker">{i+1:02}</div><h3>{e(t(k,l))}</h3><p>{e(t(k+"Copy",l).replace(" Предложенная редакция.","").replace(" Proposed wording.","").replace(" 제안 문구입니다.",""))}</p></div>' for i,k in enumerate(('identify','review','connect','develop')))+'</div>'
def homepage(l):
 hero=section(f'<div><h1>KOREA <span class="hero-arrow" aria-hidden="true">↗</span><span class="teal">CENTRAL<br>ASIA</span></h1><p class="korean-line">한국 · 중앙아시아 비즈니스 게이트웨이</p></div><div class="hero-message"><h2>{e(t("slogan1",l))}<br><em>{e(t("slogan2",l))}</em></h2><p>{e(t("heroCopy",l))}</p><div class="hero-actions">{link("explore",l,"projects","action")}{link("talk",l,"contact")}</div></div>','hero')
 discover='<div class="discover"><div class="eyebrow">'+e(t('discover',l))+'</div>'+''.join(a(t(k,l)+' ↗',url(l,k)) for k in ('projects','cooperation','directions'))+'</div>'
 cities=[('SEOUL','Asia/Seoul','+9'),('TASHKENT','Asia/Tashkent','+5'),('ALMATY','Asia/Almaty','+5'),('BISHKEK','Asia/Bishkek','+6'),('DUSHANBE','Asia/Dushanbe','+5'),('ASHGABAT','Asia/Ashgabat','+5')]
 corridor=section('<div class="serif">'+e(t('corridor1',l))+'<br>'+e(t('corridor2',l))+'</div><div class="cities">'+''.join(f'<div class="city"><div class="eyebrow">{name}</div><div class="time"><span data-zone="{zone}">—</span><span class="zone">UTC{offset}</span></div></div>' for name,zone,offset in cities)+'</div>','corridor')
 featured=section('<div class="section-heading"><h2>'+e(t('projects',l))+'</h2>'+link('explore',l,'projects')+'</div><div class="project-list">'+''.join(projectcard(p,l) for p in PROJECTS if p['featured'])+'</div>'+note('sourceNote',l),'section home-projects')
 dirs=section('<div class="section-heading"><h2>'+e(t('directions',l))+'</h2>'+link('allDirections',l,'directions')+'</div>'+sectors(l),'section home-directions')
 news=section('<div class="section-heading"><h2>'+e(t('news',l))+'</h2>'+link('allNews',l,'news')+'</div><div class="news-list news-home">'+''.join(newscard(n,l) for n in NEWS)+'</div>','section home-news')
 return hero+discover+corridor+section(process(l),'section home-process')+dirs+featured+news

def catalogue(l):
 def select(key,options):return f'<label>{e(t(key,l))}<select id="filter-{key}" name="{key}">'+''.join(f'<option value="{v}">{e(text)}</option>' for v,text in options)+'</select></label>'
 filters=f'<label>{e(t("search",l))}<input id="filter-search" type="search" placeholder="{e(t("searchHint",l))}" autocomplete="off"></label>'
 filters+=select('country',[('all',t('allCountries',l))]+[(k,t(k,l)) for k in sorted({p['country'] for p in PROJECTS})])
 filters+=select('sector',[('all',t('allSectors',l))]+[(s['key'],s['title'][l]) for s in SECTORS if s['key'] in {p['sector'] for p in PROJECTS}])
 filters+=select('stage',[('all',t('allStages',l))]+[(k,t(k,l)) for k in sorted({p['stage'] for p in PROJECTS})])
 return intro('projects',l,'catalogueCopy')+section('<form class="filters" id="filters" role="search">'+filters+'</form><div class="results" id="results" aria-live="polite" data-label="'+e(t('entries',l))+'">'+e(t('entries',l))+': '+str(len(PROJECTS))+'</div><p class="no-results" id="empty" hidden>'+e(t('empty',l))+'</p><div class="project-list catalogue-list" id="catalogue">'+''.join(projectcard(p,l) for p in PROJECTS)+'</div>'+note('sourceNote',l))
def detail(p,l):
 facts=[('projectID',p['id']),('country',t(p['country'],l)),('location',p['location'][l]),('sector',t(p['sector'],l)),('stage',t(p['stage'],l))]
 if p.get('updated_at'):facts.append(('updated',p['updated_at']))
 facts.append(('reviewed',p['reviewed_at']))
 return section(link('backProjects',l,'projects')+'<div class="eyebrow">'+e(t(p['sector'],l))+' · '+e(t(p['country'],l))+'</div><h1>'+e(p['title'][l])+'</h1><p>'+e(p['description'][l])+'</p>','page-intro')+section('<div class="detail-grid"><article><h2>'+e(t('parameters',l))+'</h2><p>'+e(p['parameters'][l])+'</p><h2>'+e(t('cooperationFormat',l))+'</h2><p>'+e(p['participation'][l])+'</p>'+(f'<p>{e(p["stage_note"][l])}</p>' if p.get('stage_note') else '')+'</article><aside><dl class="facts">'+''.join(f'<div><dt>{e(t(k,l))}</dt><dd>{e(v)}</dd></div>' for k,v in facts)+'</dl>'+a(t('requestInfo',l),url(l,'contact')+'?project='+quote(p['id']),'action')+'</aside></div>'+note('infoCopy',l))

def article(n,l):
 photo=f'<figure id="article-photo"><img id="article-photo-img" width="960" height="1280" src="{img("uzbekistan-korea-forum-2026.jpg")}" alt="{e(n["caption"][l])}"><figcaption id="article-photo-caption">{e(n["caption"][l])}</figcaption></figure>' if n.get('image_asset') else ''
 return section(link('backNews',l,'news')+'<div class="eyebrow">'+e(t(n['category'],l))+'</div><h1>'+e(n['title'][l])+'</h1><p>'+e(t('eventDate' if n.get('date_kind')=='event' else 'sourceDate',l))+': <time datetime="'+newsdate(n,l)+'">'+newsdate(n,l)+'</time></p>','page-intro')+section('<article class="article-body">'+photo+''.join('<p>'+e(p)+'</p>' for p in n['body'][l])+a(n.get('public_source_label',{}).get(l,t('officialSource',l))+' ↗',n['source_url'],'text-link')+(note('externalNews',l) if not n.get('image_asset') else '')+'</article>')
def contact(l):
 labels={'en':('Prepare an email','This opens your email app. The message is sent only after you send it there.'),'ko':('이메일 작성','이메일 앱이 열립니다. 앱에서 전송을 완료해야 문의가 전달됩니다.'),'ru':('Подготовить письмо','Откроется ваша почтовая программа. Письмо отправляется только после отправки в ней.')}
 def field(k,typ='text'):return '<label><span>'+e(t(k,l))+'</span><input name="'+k+'" type="'+typ+'" required maxlength="200" autocomplete="'+({'name':'name','organisation':'organization','email':'email'}[k])+'"></label>'
 contact_intro=intro('contact',l,'contactCopy','contactSubtitle' if l in COPY.get('contactSubtitle',{}) else None)
 return contact_intro+section('<div class="contact-layout"><aside><div class="official-contacts"><div><label>'+e(t('general',l))+'</label><a href="mailto:info@koreacentralasia.com">info@koreacentralasia.com</a></div><div><label>'+e(t('projectInterest',l))+'</label><a href="mailto:project@koreacentralasia.com">project@koreacentralasia.com</a></div></div><p>'+e(t('contactAside',l))+'</p>'+note('noSensitive',l)+'</aside><form id="enquiry" data-language="'+l+'"><input name="project_id" type="hidden"><div class="form-grid">'+field('name')+field('organisation')+field('email','email')+'<label class="full">'+e(t('interest',l))+'<select name="topic"><option value="general">'+e(t('general',l))+'</option><option value="project">'+e(t('projectInterest',l))+'</option></select></label><label class="full">'+e(t('message',l))+'<textarea name="message" required maxlength="5000"></textarea></label></div><div class="form-footer"><button class="action" type="submit">'+e(labels[l][0])+' ↗</button></div><p class="note">'+e(labels[l][1])+'</p><div class="form-status" id="form-status" role="status"></div></form></div>')
def info(l,key):
 if key=='about':return intro('about',l,'aboutCopy')+section('<div class="audience-grid">'+''.join('<article><h2>'+e(t(k,l))+'</h2><p>'+e(t(k+'Copy',l))+'</p></article>' for k in ('businessPlatform','projectConsulting','advisory'))+'</div>')+section('<h2>'+e(t('regionalApproach',l))+'</h2><p class="spaced">'+e(t('geographyCopy',l))+'</p>')
 if key=='cooperation':
  audiences=section('<div class="audience-grid">'+''.join('<article><h2>'+e(t(k,l))+'</h2><p class="spaced">'+e(t(k+'Copy',l))+'</p>'+a(t(action,l),url(l,'contact')+'?topic='+('project' if k=='forSponsors' else 'general'),'action')+'</article>' for k,action in [('forKorea','companyInterest'),('forSponsors','submitProject')])+'</div>')
  interaction=''
  if l in COPY.get('cooperationSteps',{}):
   interaction=section('<h2>'+e(t('cooperationProcessHeading',l))+'</h2><ol class="cooperation-steps">'+''.join('<li>'+e(step)+'</li>' for step in COPY['cooperationSteps'][l])+'</ol><p>'+e(t('cooperationTerms',l))+'</p>')
  return intro(key,l,'cooperationIntro')+audiences+interaction+section(link('seeDirections',l,'directions'))
 if key=='directions':return intro(key,l,'directionsCopy')+section(sectors(l),'section directions-content')
 if key=='news':return intro(key,l,'newsCopy')+section('<div class="news-list news-index">'+''.join(newscard(n,l) for n in NEWS)+'</div>','section news-content-section')
 if key=='privacy':return intro(key,l)+section('<p>'+e(t('privacyPending',l))+'</p>')
 if key=='legal-notice':return intro('legalNotice',l)+section('<p>'+e({'en':'Operator registration details are being prepared. For enquiries: info@koreacentralasia.com.','ko':'운영자 등록 정보를 준비하고 있습니다. 문의: info@koreacentralasia.com.','ru':'Реквизиты оператора готовятся. Для обращений: info@koreacentralasia.com.'}[l])+'</p>')
 raise ValueError(key)
def render(l,path,body,title,description,kind=''):
 nav='<nav aria-label="'+e({'en':'Main navigation','ko':'주 메뉴','ru':'Основная навигация'}[l])+'">'+''.join(f'<a {"aria-current=page" if path==p or path.startswith(p+"/") and p else ""} href="{url(l,p)}">{e(t(k,l))}</a>' for k,p in [('home',''),('about','about'),('projects','projects'),('cooperation','cooperation'),('news','news'),('contact','contact')])+'</nav>'
 langs='<div class="languages">'+''.join(f'<a hreflang="{x}" lang="{x}" {"aria-current=page" if x==l else ""} href="{url(x,path)}">{label}</a>' for x,label in [('en','EN'),('ko','한국어'),('ru','RU')])+'</div>'
 header=f'<div class="demo-notice" role="note">{e(t("demoNotice",l))}</div><header><a class="brand" href="{url(l)}"><img src="{img("KCAP_horizontal_color.svg")}" alt="KCAP — Business Gateway Platform" width="210" height="45"></a>{nav}{langs}</header>'
 footer=f'<footer><a href="{url(l)}"><img src="{img("KCAP_horizontal_white.svg")}" alt="KCAP — Business Gateway Platform" width="150" height="32"></a><div class="footer-links">{link("privacy",l,"privacy","")}{link("legalNotice",l,"legal-notice","")}</div></footer>'
 band=section('<h2>'+e(t('start',l))+'</h2>'+a(t('talk',l),url(l,'contact')+('#enquiry' if path=='contact' else ''),'action'),'contact-band')
 labels=[t('platform',l),t('directions',l),t('projects',l),t('news',l),t('contact',l)]
 heading_index=0
 def label_heading(match):
  nonlocal heading_index
  if not path:
   index=heading_index
   label='KCAP' if index==0 else labels[min(index-1,len(labels)-1)]
  else:
   index=heading_index+1
   label=t('projects' if kind=='detail' else 'news' if kind=='article' else 'legalNotice' if path=='legal-notice' else path,l)
  heading_index+=1
  return match.group(0)+f'<span class="section-label" aria-hidden="true">{index:02} · {e(label)}</span>'
 body=re.sub(r'<h2(?:\s[^>]*)?>',label_heading,body)
 band=re.sub(r'<h2(?:\s[^>]*)?>',lambda m:m.group(0)+f'<span class="section-label" aria-hidden="true">{heading_index if not path else heading_index+1:02} · {e(t("contact",l))}</span>',band)
 seo=f'<meta name="robots" content="{"index,follow" if PUBLIC and path not in ("privacy","legal-notice") else "noindex,nofollow"}">'
 if ORIGIN:
  seo+=f'<link rel="canonical" href="{e(ORIGIN+url(l,path))}">'+''.join(f'<link rel="alternate" hreflang="{x}" href="{e(ORIGIN+url(x,path))}">' for x in LANGS)+f'<link rel="alternate" hreflang="x-default" href="{e(ORIGIN+url("en",path))}">'
 locale={'en':'en_US','ko':'ko_KR','ru':'ru_RU'}[l]
 social_image=ORIGIN+BASE+'/assets/kcap-social.png'
 seo+=f'<meta property="og:title" content="{e(title)} — KCAP"><meta property="og:description" content="{e(description[:180])}"><meta property="og:type" content="website"><meta property="og:url" content="{e(ORIGIN+url(l,path))}"><meta property="og:image" content="{e(social_image)}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="KCAP — Business Gateway Platform"><meta property="og:locale" content="{locale}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)} — KCAP"><meta name="twitter:description" content="{e(description[:180])}"><meta name="twitter:image" content="{e(social_image)}">'
 seo+=''.join(f'<meta property="og:locale:alternate" content="{v}">' for k,v in {'en':'en_US','ko':'ko_KR','ru':'ru_RU'}.items() if k!=l)
 htmlpage=f'<!doctype html><html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} — KCAP</title><meta name="description" content="{e(description[:180])}">{seo}<link rel="icon" href="{img("KCAP_symbol_color.svg")}" type="image/svg+xml"><link rel="stylesheet" href="{img("site.css")}"><script src="{img("app.js")}" defer></script></head><body><div id="kcap"><a class="skip" href="#main">{e({"en":"Skip to content","ko":"본문으로 이동","ru":"К содержанию"}[l])}</a><div class="viewport"><div class="site {"lang-ko" if l=="ko" else ""}" data-page="{kind or path or "home"}">{header}<main id="main">{body}</main>{band}{footer}</div></div></div></body></html>'
 file=OUT/l/path/'index.html';file.parent.mkdir(parents=True,exist_ok=True);file.write_text(htmlpage)
 return url(l,path)
def build():
 if OUT.exists():shutil.rmtree(OUT)
 OUT.mkdir(exist_ok=True);shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
 shutil.copytree(ROOT/'admin',OUT/'admin',dirs_exist_ok=True)
 (OUT/'content').mkdir(exist_ok=True)
 for name,values in [('projects',PROJECTS),('news',NEWS),('pages',COPY),('sectors',{'sectors':SECTORS})]:(OUT/'content'/f'{name}.json').write_text(json.dumps(values,ensure_ascii=False))
 routes=[]
 for l in LANGS:
  routes.append(render(l,'',homepage(l),'Korea Central Asia Platform',t('heroCopy',l)))
  for key in ('about','cooperation','directions','news','privacy','legal-notice'):routes.append(render(l,key,info(l,key),t('legalNotice' if key=='legal-notice' else key,l),t('heroCopy',l)))
  routes.append(render(l,'projects',catalogue(l),t('projects',l),t('catalogueCopy',l)))
  routes.append(render(l,'contact',contact(l),t('contact',l),t('contactCopy',l)))
  for p in PROJECTS:routes.append(render(l,'projects/'+p['slug'],detail(p,l),p['title'][l],p['description'][l],'detail'))
  for n in NEWS:routes.append(render(l,'news/'+n['id'],article(n,l),n['title'][l],n['summary'][l],'article'))
 (OUT/'index.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta http-equiv="refresh" content="0;url={url("en")}"><title>KCAP — Korea Central Asia Platform</title></head><body><a href="{url("en")}">KCAP · English</a></body></html>')
 (OUT/'.nojekyll').touch();(OUT/'404.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Page not found — KCAP</title><h1>404 · Page not found</h1>'+a('KCAP',BASE+'/')+'</html>')
 (OUT/'robots.txt').write_text('User-agent: *\n'+('Allow: /\nSitemap: '+ORIGIN+BASE+'/sitemap.xml\n' if PUBLIC else 'Disallow: /\n'))
 if ORIGIN:(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+e(ORIGIN+r)+'</loc></url>' for r in routes)+'</urlset>')
 print(json.dumps({'routes':len(routes),'projects':len(PROJECTS),'news':len(NEWS),'languages':list(LANGS),'public_release':PUBLIC,'output':str(OUT)},ensure_ascii=False))
if __name__=='__main__':build()
