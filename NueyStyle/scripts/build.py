"""Validate the static website and stage only public files for deployment."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import re, json, shutil, subprocess, sys

root=Path(__file__).resolve().parent.parent
errors=[]
class Page(HTMLParser):
    def __init__(self,path):
        super().__init__(convert_charrefs=True)
        self.path=path;self.ids=set();self.refs=[];self.h1=0;self.images=0;self.controls=[]
        self.feed(path.read_text(encoding='utf-8'))
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids:errors.append(f'{self.path.name}: duplicate id {a["id"]}')
            self.ids.add(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='img':
            self.images+=1
            if 'alt' not in a:errors.append(f'{self.path.name}: image missing alt')
        for k in ('href','src','poster'):
            if a.get(k):self.refs.append(a[k])
        if a.get('srcset'):
            self.refs.extend(part.strip().split()[0] for part in a['srcset'].split(',') if part.strip())
        if a.get('aria-controls'):self.controls.extend(a['aria-controls'].split())
        if a.get('aria-labelledby'):self.controls.extend(a['aria-labelledby'].split())

pages={p.name:Page(p) for p in root.glob('*.html')}
references=0
for name,page in pages.items():
    if page.h1!=1:errors.append(f'{name}: expected one h1, got {page.h1}')
    for target in page.controls:
        if target not in page.ids:errors.append(f'{name}: missing labelled/control target {target}')
    for ref in page.refs:
        parsed=urlsplit(ref)
        if parsed.scheme or parsed.netloc:continue
        path=unquote(parsed.path)
        target=(root/path.lstrip('/')) if path else page.path
        if path=='/':target=root/'index.html'
        if not target.exists() and not target.suffix:target=target.with_suffix('.html')
        references+=1
        if not target.exists():errors.append(f'{name}: missing {ref}')
        elif parsed.fragment and target.suffix=='.html' and target.name in pages:
            if unquote(parsed.fragment) not in pages[target.name].ids:errors.append(f'{name}: missing anchor {ref}')
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>',page.path.read_text(encoding='utf-8'),re.S):
        try:json.loads(block)
        except ValueError as exc:errors.append(f'{name}: invalid structured metadata {exc}')
for css in (root/'css').glob('*.css'):
    for ref in re.findall(r'url\([\"\x27]?([^\)\"\x27]+)',css.read_text(encoding='utf-8')):
        if not urlsplit(ref).scheme and not ref.startswith('#') and not (css.parent/ref.split('?')[0]).exists():errors.append(f'{css.name}: missing asset {ref}')
for js in (root/'js').glob('*.js'):
    result=subprocess.run(['node','--check',str(js)],capture_output=True,text=True)
    if result.returncode:errors.append(result.stderr)
for name in ('index.html','capabilities.html'):
    source=(root/name).read_text(encoding='utf-8')
    grid=re.search(r'<div class="cobertura__grade".*?</div>',source,re.S)
    if not grid or len(re.findall(r'<i ',grid[0]))!=84:errors.append(f'{name}: original 84-square grid missing')
if errors:
    print('\n'.join(errors));sys.exit(1)
dist=root/'dist';dist.mkdir(exist_ok=True)
for name in ('css','js','fonts','img','brand','video'):shutil.copytree(root/name,dist/name,dirs_exist_ok=True)
for pattern in ('*.html','favicon.ico','robots.txt','sitemap.xml','site.webmanifest','_headers','_redirects'):
    for p in root.glob(pattern):shutil.copy2(p,dist/p.name)
print(f'PASS: {len(pages)} pages, {references} local references, all metadata and JavaScript. Original 84-square animation on both pages.')
print(f'Public build: {dist}')
