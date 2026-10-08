"""Validate the blog build and, optionally, compare deployed bytes."""
from __future__ import annotations
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import time
from urllib.parse import unquote, urlsplit
from urllib.request import urlopen, Request
import xml.etree.ElementTree as ET
from build_blog import ROOT, BASE, load_posts, MARKER

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.refs=[]; self.h1=0; self.canonical=None; self.lang=None
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='html': self.lang=attrs.get('lang')
        if tag=='h1': self.h1+=1
        if 'id' in attrs: self.ids.append(attrs['id'])
        for key in ('href','src','data-url'):
            if attrs.get(key): self.refs.append((tag,attrs[key]))
        if tag=='link' and attrs.get('rel')=='canonical': self.canonical=attrs.get('href')

def check():
    posts=load_posts(ROOT/'content/posts')
    expected={p['slug'] for p in posts}
    assert len(json.loads((ROOT/'blog/index.json').read_text()))==len(posts)
    rss=ET.parse(ROOT/'blog/feed.xml')
    assert len(rss.findall('channel/item'))==len(posts)
    pages=[]
    for folder in ('blog','en/blog','admin','en/admin'):
        pages.extend((ROOT/folder).rglob('*.html'))
    for f in pages:
        text=f.read_text(); p=Page(); p.feed(text)
        assert p.h1==1, (f,'one h1 required')
        assert all(n==1 for n in Counter(p.ids).values()),(f,'duplicate IDs')
        assert p.canonical and p.canonical.startswith(BASE+'/'),(f,'canonical missing')
        for tag,url in p.refs:
            u=urlsplit(url)
            if u.netloc and u.netloc!=urlsplit(BASE).netloc: continue
            if u.scheme and u.scheme not in ('https','http'): continue
            path=unquote(u.path)
            target=ROOT/path.lstrip('/') if path.startswith('/') else f.parent/path
            target=target.resolve()
            assert target.is_relative_to(ROOT.resolve()),(f,'path traversal')
            if target.is_dir(): target=target/'index.html'
            assert target.exists(),(str(f),url)
    for f in (ROOT/'blog').glob('*/index.html'):
        if f.read_text().startswith(MARKER): assert f.parent.name in expected
    print(f'PASS: {len(pages)} blog/admin pages, {len(posts)} published posts, links, IDs, RSS, exports')

def live(timeout):
    paths=['blog/index.html','en/blog/index.html','admin/index.html','en/admin/index.html','blog/feed.xml','writing.html','assets/blog/blog.js','.pages.yml']
    # .pages.yml is configuration, not a publicly served page; verify it in Git.
    paths.remove('.pages.yml')
    pending=set(paths); deadline=time.monotonic()+timeout
    while pending and time.monotonic()<deadline:
        for path in list(pending):
            try:
                req=Request(BASE+'/'+path+'?blog-check='+str(time.time_ns()),headers={'Cache-Control':'no-cache','User-Agent':'PortfolioBlogCheck/1.0'})
                with urlopen(req,timeout=12) as response: content=response.read()
                if content==(ROOT/path).read_bytes(): pending.remove(path)
            except Exception: pass
        if pending: time.sleep(8)
    if pending: raise RuntimeError('Live content did not match: '+', '.join(sorted(pending)))
    print('PASS: all 7 public blog entry/resources match the repository build')

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--live',action='store_true'); parser.add_argument('--timeout',type=int,default=180)
    args=parser.parse_args(); check()
    if args.live: live(args.timeout)
