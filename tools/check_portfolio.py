"""Offline checks for generated pages, links, language pairs and claim scope."""
from __future__ import annotations
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.refs=[]; self.lang=None; self.canonical=None; self.alternates={}; self.h1=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag=='html': self.lang=a.get('lang')
        if tag=='h1': self.h1+=1
        if tag=='link' and a.get('rel')=='canonical': self.canonical=a.get('href')
        if tag=='link' and a.get('rel')=='alternate': self.alternates[a.get('hreflang')]=a.get('href')
        for key in ['href','src']:
            if a.get(key): self.refs.append((tag,a[key]))


def main():
    pages={}; errors=[]; generated=[]
    for f in ROOT.rglob('*.html'):
        if '.git' in f.parts: continue
        p=Page(); text=f.read_text(encoding='utf-8'); p.feed(text)
        pages[f.resolve()]=p
        if 'class="portfolio-site"' in text: generated.append((f,p,text))
    for f,p,text in generated:
        rel=f.relative_to(ROOT).as_posix()
        if p.h1 != 1: errors.append(f'{rel}: {p.h1} h1 elements')
        if any(n>1 for n in Counter(p.ids).values()): errors.append(f'{rel}: duplicate IDs')
        en=rel.startswith('en/'); plain=rel[3:] if en else rel
        base='https://xfdg.github.io/'
        expected=base+('en/' if en else '')+('' if plain=='index.html' else plain)
        if p.canonical!=expected: errors.append(f'{rel}: wrong canonical')
        if p.lang!=('en' if en else 'zh-CN'): errors.append(f'{rel}: wrong language')
        if set(p.alternates)!={'zh-CN','en','x-default'}: errors.append(f'{rel}: missing alternate links')
        other=ROOT/('' if en else 'en')/plain
        if not other.exists(): errors.append(f'{rel}: missing language counterpart')
        for tag,url in p.refs:
            u=urlsplit(url)
            if u.scheme or u.netloc: continue
            path=unquote(u.path)
            target=(ROOT/path.lstrip('/') if path.startswith('/') else f.parent/path).resolve() if path else f.resolve()
            if target.is_dir(): target=target/'index.html'
            if not target.exists(): errors.append(f'{rel}: missing {url}'); continue
            if tag=='a' and u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:
                errors.append(f'{rel}: missing anchor {url}')
        if any(s in text for s in ['/volume/','zhaoye-gpu','2026.02 — 2026.05']):
            errors.append(f'{rel}: private or stale content')
        if re.search(r'(?<![0-9])1[3-9][0-9]{9}(?![0-9])', text): errors.append(f'{rel}: phone number in public page')
        if 'course' in text.lower() and 'drone' in text.lower() and plain=='projects.html': errors.append(f'{rel}: course label in project index')
    data=json.loads((ROOT/'content/portfolio_status.json').read_text())
    flat=[(g['repo'],pr['number']) for g in data['groups'] for pr in g['prs']]
    if len(flat)!=len(set(flat)): errors.append('Duplicate PR count')
    if ('kvcache-ai/Mooncake',3661) in flat: errors.append('Unmerged #3661 counted as merged')
    for language in ['', 'en/']:
        home=(ROOT/(language+'index.html')).read_text()
        if f'{len(flat)} PRs' not in home: errors.append(f'{language}: inconsistent homepage count')
        if '1,024' in home: errors.append(f'{language}: old KPI on homepage')
        resume=(ROOT/(language+'resume.html')).read_text()
        for token in ['IQuest-Q1','3.98','73.39','76.8','2026.01 — 2026.04']:
            if token not in resume: errors.append(f'{language}: resume missing {token}')
    if len(generated)<40: errors.append('Missing regenerated pages')
    print(json.dumps({'generated_pages':len(generated),'scoped_merged_prs':len(flat),'errors':errors},ensure_ascii=False,indent=2))
    if errors: sys.exit(1)

if __name__=='__main__': main()
