import json
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
root=Path(__file__).resolve().parent;dist=root/'dist'
projects=json.loads((root/'content/projects.json').read_text());news=json.loads((root/'content/news.json').read_text())
class Check(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.h1=0;self.lang=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='html':self.lang=a.get('lang')
  if tag=='h1':self.h1+=1
  if 'id' in a:self.ids.append(a['id'])
  if tag in ('a','img','script','link'):
   href=a.get('href') or a.get('src')
   if href:self.links.append(href)
projects=[p for p in projects if p.get('publication_status')=='published'];news=[n for n in news if n.get('publication_status')=='published']
assert len({p['id'] for p in projects})==len(projects)
errors=[];count=0
for f in dist.glob('*/**/index.html'):
 if f.relative_to(dist).parts[0]=='admin':continue
 p=Check();p.feed(f.read_text());count+=1
 if p.lang not in ('en','ko','ru') or p.h1!=1:errors.append(str(f)+': language/h1')
 if len(p.ids)!=len(set(p.ids)):errors.append(str(f)+': duplicate ids')
 for href in p.links:
  path=urlparse(href).path
  if urlparse(href).scheme or not path or path.startswith('#'):continue
  # The build supports a GitHub repository prefix, regardless of local preview base.
  if path.startswith('/kcap-site/'):path=path[len('/kcap-site'):]
  target=dist/unquote(path.lstrip('/'))
  if target.is_dir():target=target/'index.html'
  if not target.exists():errors.append(str(f)+': missing '+href)
 for n in ['Illustrative entry','Demonstration template','Предложенная редакция','Демонстрационная запись']:
  if n in f.read_text():errors.append(str(f)+': review placeholder '+n)
assert count==3*(9+len(projects)+len(news)),count
assert not errors,'\n'.join(errors[:30])
print(f'PASS: {count} language pages; {len(projects)} projects; {len(news)} news; unique IDs; internal links and assets.')
