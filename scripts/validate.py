import pathlib,json,hashlib,datetime,xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
R=pathlib.Path(__file__).resolve().parents[1]
if R.name!='hf-incident-wiki':R=R/'outputs'/'hf-incident-wiki'
class Page(HTMLParser):
 def __init__(self,text):super().__init__();self.ids=[];self.links=[];self.feed(text)
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if a.get('id'):self.ids.append(a['id'])
  for k in (['href'] if t in ['a','link'] else ['src'] if t in ['script','img'] else []):
   if a.get(k):self.links.append(a[k])
def run():
 checks=[]
 def check(n,b):checks.append(dict(check=n,passed=bool(b)))
 pages={p.name:Page(p.read_text(encoding='utf-8')) for p in R.glob('*.html')}
 for name,p in pages.items():
  check(name+' unique IDs',len(set(p.ids))==len(p.ids))
  for link in p.links:
   u=urlsplit(link)
   if u.scheme or u.netloc:continue
   f=R/unquote(u.path) if u.path else R/name
   check(name+' local '+link,f.is_file())
   if f.suffix=='.html' and u.fragment:check(name+' fragment '+link,f.name in pages and u.fragment in pages[f.name].ids)
 W=json.loads((R/'assets/wiki-data.json').read_text(encoding='utf-8'));P=json.loads((R/'assets/slide-map.json').read_text(encoding='utf-8'));S=json.loads((R/'sources/manifest.json').read_text(encoding='utf-8'))
 wids={w['id'] for w in W}
 check('19 slides; 13 Wiki entries',len(P)==19 and len(W)==13)
 check('slide Wiki links',all(set(p['wiki'])<=wids for p in P))
 check('titles concise',all(len(p['title'])<=17 for p in P))
 check('single Markdown submission report', (R/'README.md').is_file() and not (R/'繳交描述.txt').exists() and not (R/'README.txt').exists())
 check('no active lab/report HTML',not (R/'lab.html').exists() and not (R/'report.html').exists())
 check('single clean stylesheet',len(list((R/'assets').glob('*.css')))==1)
 check('no experimental slides',not any(p['title'] in ['本機實驗','實際執行','製作流程'] for p in P))
 for s in S:check(s['id']+' original snapshot hash',hashlib.sha256((R/s['snapshot']).read_bytes()).hexdigest()==s['sha256'])
 for w in W:
  check(w['id']+' related concepts',set(w['related'])<=wids)
  for e in w['evidence']:
   lines=(R/'sources'/f"{e['source']}.txt").read_text(encoding='utf-8').splitlines()
   check(w['id']+' evidence '+e['source'],e['needle'].lower() in lines[e['line']-1].lower())
 ns={'s':'http://www.w3.org/2000/svg'}
 diagrams=list((R/'assets/diagrams').glob('*.svg'));check('14 standalone SVG diagrams',len(diagrams)==14)
 for p in diagrams:
  root=ET.parse(p).getroot();check(p.stem+' accessible title/description',root.find('s:title',ns) is not None and root.find('s:desc',ns) is not None)
  ids={e.get('id') for e in root.iter() if e.get('id')};check(p.stem+' arrowhead definitions',{'blue','orange','green'}<=ids)
  check(p.stem+' no scripts',root.find('.//s:script',ns) is None)
 result=dict(executed_at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),scope='structural links, provenance, SVG syntax/accessibility and content organization; not a semantic truth or visual overlap proof',passed=sum(c['passed'] for c in checks),total=len(checks),failures=[c for c in checks if not c['passed']],checks=checks)
 (R/'checks').mkdir(exist_ok=True);(R/'checks/validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(f"{result['passed']}/{result['total']} checks passed")
 for f in result['failures']:print(f)
 if result['failures']:raise SystemExit(1)
if __name__=='__main__':run()
