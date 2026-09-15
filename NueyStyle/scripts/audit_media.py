"""Audit editorial media placements, including resized and center-cropped duplicates.
Requires Pillow. Brand marks and video poster fallbacks in the same placement are excluded.
"""
from pathlib import Path
from html.parser import HTMLParser
from PIL import Image, ImageOps
import hashlib
root=Path(__file__).resolve().parent.parent
class Media(HTMLParser):
 def __init__(self):super().__init__();self.images=[];self.videos=[];self.video=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='img' and a.get('src','').startswith('img/'):self.images.append(a['src'])
  if tag=='video':self.video=[];self.videos.append(self.video)
  if tag=='source' and self.video is not None:self.video.append(a['src'])
 def handle_endtag(self,tag):
  if tag=='video':self.video=None

def signatures(path):
 im=Image.open(path).convert('L');result=[]
 for ratio in [None,1,4/3,16/9]:
  frame=im if ratio is None else ImageOps.fit(im,(round(160*ratio),160))
  values=list(frame.resize((17,16)).get_flattened_data())
  result.append(tuple(values[y*17+x]>values[y*17+x+1] for y in range(16) for x in range(16)))
 return result
rows=[];videos={};issues=[];placements=0
for page in root.glob('*.html'):
 media=Media();media.feed(page.read_text(encoding='utf8'))
 for src in media.images:rows.append((page.name,src,signatures(root/src)))
 for sources in media.videos:
  placements+=1
  for src in sources:
   digest=hashlib.sha256((root/src).read_bytes()).hexdigest()
   if digest in videos:issues.append(f'Repeated video: {videos[digest]} and {page.name}: {src}')
   videos[digest]=f'{page.name}: {src}'
for i,(page,src,sigs) in enumerate(rows):
 for other,path,hashes in rows[i+1:]:
  distance=min(sum(a!=b for a,b in zip(x,y)) for x in sigs for y in hashes)
  if distance<=12:issues.append(f'Repeated or near-identical image: {page}: {src} and {other}: {path} (distance {distance})')
if issues:raise SystemExit('\n'.join(issues))
print(f'PASS: {len(rows)} editorial image placements and {placements} video placements; no duplicate media detected.')
