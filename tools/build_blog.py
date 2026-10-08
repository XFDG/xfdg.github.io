"""Markdown blog layered onto the existing portfolio; no network or account secrets.
Run after build_portfolio.py. --test exercises parsing/rendering without that module.
Only explicitly published files become pages, feeds, search entries, or exports.
"""
from __future__ import annotations
import argparse
from datetime import date, datetime, timezone
from email.utils import format_datetime
from hashlib import sha256
from html import escape
from pathlib import Path
import json
import re
import sys
import tempfile
import unittest
from urllib.parse import urljoin, urlsplit
import xml.etree.ElementTree as ET
import yaml
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://xfdg.github.io'
CMS = 'https://app.pagescms.org/'
SYNC = 'https://www.wechatsync.com/'
MARKER = '<!-- generated-blog-v1 -->'
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')

def e(value):
    return escape(str(value), quote=True)

def tr(zh, en, lang):
    return en if lang == 'en' else zh

def iso(value, field):
    if isinstance(value, (date, datetime)):
        return value.isoformat()[:10]
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError(f'{field}: use YYYY-MM-DD')
    date.fromisoformat(value)
    return value

def public_url(value, *, image=False):
    if not value:
        return ''
    value = str(value).strip()
    parsed = urlsplit(value)
    if parsed.scheme == 'https' and parsed.netloc and not parsed.username and not parsed.password:
        return value
    if value.startswith('/assets/blog/images/') and not any(x in value for x in ('..', '\\', '\n', '\r')):
        return BASE + value
    raise ValueError('Images and cross-post links must use an absolute HTTPS URL or /assets/blog/images/...')

def parse_post(path):
    text = path.read_text(encoding='utf-8-sig').replace('\r\n', '\n')
    if len(text) > 2_000_000:
        raise ValueError(f'{path.name}: article exceeds 2 MB')
    parts = re.split(r'^---\s*$', text, maxsplit=2, flags=re.M)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError(f'{path.name}: missing YAML frontmatter')
    meta = yaml.safe_load(parts[1])
    if not isinstance(meta, dict):
        raise ValueError(f'{path.name}: frontmatter must be an object')
    published = meta.get('published', False)
    if not isinstance(published, bool):
        raise ValueError(f'{path.name}: published must be true or false, not a string')
    if not published:
        return None
    title = str(meta.get('title', '')).strip()
    slug = str(meta.get('slug') or path.stem).strip()
    if not title or len(title) > 200 or len(slug) > 80 or not SLUG.fullmatch(slug):
        raise ValueError(f'{path.name}: title or URL slug is invalid')
    lang = meta.get('lang') or 'zh'
    if lang not in ('zh', 'en'):
        raise ValueError(f'{path.name}: language must be zh or en')
    created = iso(meta.get('date'), 'date')
    updated = iso(meta.get('updated') or created, 'updated')
    if updated < created:
        raise ValueError(f'{path.name}: updated date precedes publication date')
    body = parts[2].strip()
    if not body:
        raise ValueError(f'{path.name}: published article is empty')
    summary = str(meta.get('summary') or '').strip()
    if len(summary) > 400:
        raise ValueError(f'{path.name}: summary exceeds 400 characters')
    tags = meta.get('tags') or []
    if isinstance(tags, str):
        tags = [x.strip() for x in re.split('[,，]', tags) if x.strip()]
    if not isinstance(tags, list) or len(tags) > 12 or any(not isinstance(x, str) or len(x) > 40 for x in tags):
        raise ValueError(f'{path.name}: tags must be at most 12 short strings')
    links = {key: public_url(meta.get(key)) for key in ('csdn', 'zhihu', 'luogu') if meta.get(key)}
    translation = str(meta.get('translation') or '').strip()
    if translation and not SLUG.fullmatch(translation):
        raise ValueError(f'{path.name}: invalid translation slug')
    return dict(title=title, slug=slug, lang=lang, date=created, updated=updated,
                summary=summary, tags=list(dict.fromkeys(tags)), body=body,
                cover=public_url(meta.get('cover'), image=True), links=links,
                translation=translation, source=path.name, url=f'{BASE}/blog/{slug}/')

def load_posts(folder):
    posts = [p for f in sorted(folder.glob('*.md')) if (p := parse_post(f))]
    slugs = [p['slug'] for p in posts]
    if len(set(slugs)) != len(slugs):
        raise ValueError('Duplicate article URL: each slug must be unique')
    lookup = {p['slug']: p for p in posts}
    for p in posts:
        if p['translation']:
            other = lookup.get(p['translation'])
            if not other or other['lang'] == p['lang'] or other['translation'] != p['slug']:
                raise ValueError(f'{p["slug"]}: translation must link reciprocally to a published article in the other language')
    return sorted(posts, key=lambda p: (p['date'], p['slug']), reverse=True)

def code_highlight(code, language, _attrs):
    try:
        lexer = get_lexer_by_name(language or 'text')
    except ClassNotFound:
        lexer = get_lexer_by_name('text')
    return highlight(code, lexer, HtmlFormatter(nowrap=True))

# Small math rules keep TeX out of Markdown escaping. Code fences/inline code
# remain untouched; malformed/unclosed delimiters are rendered as ordinary text.
def inline_math(state, silent):
    pos = state.pos
    if state.src[pos:pos+1] != '$' or state.src[pos:pos+2] == '$$':
        return False
    end = pos + 1
    while True:
        end = state.src.find('$', end)
        if end < 0:
            return False
        if state.src[end-1] != '\\':
            break
        end += 1
    content = state.src[pos+1:end]
    if not content or '\n' in content or content[0].isspace() or content[-1].isspace():
        return False
    if not silent:
        token = state.push('math_inline', '', 0)
        token.content = content
    state.pos = end + 1
    return True

def block_math(state, start, end, silent):
    first = state.src[state.bMarks[start]+state.tShift[start]:state.eMarks[start]].strip()
    if not first.startswith('$$'):
        return False
    if first.endswith('$$') and len(first) > 4:
        latex, stop = first[2:-2].strip(), start
    elif first == '$$':
        stop = start + 1
        while stop < end and state.src[state.bMarks[stop]:state.eMarks[stop]].strip() != '$$':
            stop += 1
        if stop == end:
            return False
        latex = state.getLines(start+1, stop, 0, False).strip()
    else:
        return False
    if not silent:
        tok = state.push('math_block', '', 0)
        tok.content = latex
        tok.block = True
        tok.map = [start, stop+1]
    state.line = stop + 1
    return True

def render_markdown(body, url):
    md = MarkdownIt('commonmark', {'html': False, 'highlight': code_highlight}).enable(['table', 'strikethrough'])
    md.inline.ruler.before('escape', 'math_inline', inline_math)
    md.block.ruler.before('fence', 'math_block', block_math)
    md.add_render_rule('math_inline', lambda self,t,i,o,en: '<span class="math">'+e(t[i].content)+'</span>')
    md.add_render_rule('math_block', lambda self,t,i,o,en: '<div class="math math-display">'+e(t[i].content)+'</div>\n')
    tokens = md.parse(body)
    toc = []
    for idx, tok in enumerate(tokens):
        if tok.type in ('heading_open', 'heading_close'):
            tok.tag = 'h' + str(min(6, int(tok.tag[1]) + 1))
        if tok.type == 'heading_open':
            ident = f'section-{len(toc)+1}'
            tok.attrSet('id', ident)
            toc.append((ident, tokens[idx+1].content))
        for child in tok.children or []:
            if child.type == 'image':
                src = child.attrGet('src') or ''
                if src.startswith('/assets/blog/images/'):
                    src = public_url(src, image=True)
                else:
                    src = public_url(src, image=True)
                child.attrSet('src', src)
                child.attrSet('loading', 'lazy')
                child.attrSet('decoding', 'async')
            if child.type == 'link_open':
                href = child.attrGet('href') or ''
                if not href.startswith('#'):
                    child.attrSet('href', urljoin(url, href))
                child.attrSet('rel', 'noopener noreferrer')
    return md.renderer.render(tokens, md.options, {}), toc

def export_markdown(post):
    # CMS uploads already have absolute URLs. Also support hand-written root-
    # relative images, without changing code fences or inline code examples.
    lines, fence = [], None
    for line in post['body'].splitlines():
        match = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if match:
            delimiter = match[1]
            if fence is None:
                fence = delimiter
            elif delimiter[0] == fence[0] and len(delimiter) >= len(fence):
                fence = None
            lines.append(line)
            continue
        if not fence:
            pieces = re.split(r'(`+[^`]*`+)', line)
            for idx in range(0, len(pieces), 2):
                pieces[idx] = re.sub(r'(!?\[[^\]]*\]\()(/assets/blog/images/[^\s)]+)', lambda m:m[1]+BASE+m[2], pieces[idx])
                pieces[idx] = re.sub(r'^(\s{0,3}\[[^\]]+\]:\s*)(/assets/blog/images/\S+)', lambda m:m[1]+BASE+m[2], pieces[idx])
            line = ''.join(pieces)
        lines.append(line)
    origin = tr('原文', 'Original', post['lang'])
    return f'# {post["title"]}\n\n> {origin}：{post["url"]}\n\n'+'\n'.join(lines)+'\n'

KATEX = '''<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.css" integrity="sha384-u1zONI5gPXUx0UKI62c75/zww972y0v2rSK5ZYlVdS6xEuWDeZWUI66v6t1gvlXJ" crossorigin="anonymous"><script defer src="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.js" integrity="sha384-ykMNcWQhhTUb0YV9SPpPUFURHZ+tWmubkakGBP+OgNK/UXdO2gtzglWx0Rj9hnO3" crossorigin="anonymous"></script>'''

# Reuse the live site's layout without editing its biographical content.
def page(path, title, summary, body, lang='zh', *, article=None, translations=None, noindex=False):
    from build_portfolio import shell
    text = shell(path, title, summary, body, lang, 'writing')
    text = text.replace('class="portfolio-site"', 'class="portfolio-site blog-site"')
    canonical = BASE + ('/en/' if lang == 'en' and article is None else '/') + path
    if canonical.endswith('/index.html'):
        canonical = canonical[:-10]
    text = re.sub(r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{e(canonical)}">', text)
    text = re.sub(r'<meta property="og:url"[^>]*>', f'<meta property="og:url" content="{e(canonical)}">', text)
    if article:
        text = re.sub(r'<link rel="alternate"[^>]*>', '', text)
        text = text.replace('content="website"', 'content="article"')
        translation = (translations or {}).get(article['translation'])
        if translation:
            paths = {article['lang']:article['url'], translation['lang']:translation['url']}
            switch = '<span class="language-switch" aria-label="Language">'+''.join(f'<a href="{e(u)}" lang="{l}"'+(' aria-current="page"' if l==lang else '')+'>'+('中' if l=='zh' else 'EN')+'</a>' for l,u in sorted(paths.items(),reverse=True))+'</span>'
            alternates = ''.join(f'<link rel="alternate" hreflang="{"zh-CN" if l=="zh" else "en"}" href="{e(u)}">' for l,u in paths.items())
            text = text.replace('</head>', alternates+'</head>')
        else:
            switch = '<span class="language-switch"><a href="/blog/">中文目录</a><span>/</span><a href="/en/blog/" lang="en">EN index</a></span>'
        text = re.sub(r'<span class="language-switch".*?</span></nav>', switch+'</nav>', text)
        schema = dict({'@context':'https://schema.org','@type':'BlogPosting'},headline=article['title'],datePublished=article['date'],dateModified=article['updated'],author={'@type':'Person','name':'Haoran Feng','url':BASE+'/'},mainEntityOfPage=canonical,inLanguage='zh-CN' if lang=='zh' else 'en')
        schema_text = json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')
        text = text.replace('</head>', f'<script type="application/ld+json">{schema_text}</script></head>')
    else:
        text = text.replace(BASE+'/blog/index.html',BASE+'/blog/').replace(BASE+'/en/blog/index.html',BASE+'/en/blog/')
    extra = '<link rel="stylesheet" href="/assets/blog/blog.css?v=1"><link rel="alternate" type="application/rss+xml" title="Haoran Feng — Blog" href="/blog/feed.xml">'
    if noindex:
        extra += '<meta name="robots" content="noindex,nofollow">'
    if article and 'class="math' in body:
        extra += KATEX
    extra += '<script defer src="/assets/blog/blog.js?v=1"></script>'
    return text.replace('</head>',extra+'</head>')

def post_rows(posts, lang):
    if not posts:
        return '<p class="blog-empty">'+tr('这里将记录技术文章、学习笔记与日常心得。','Technical articles, learning notes, and reflections will appear here.',lang)+'</p>'
    output = []
    for p in posts:
        query = ' '.join([p['title'], p['summary'], *p['tags']]).lower()
        output.append(f'<article class="blog-row" data-search="{e(query)}" data-tags="{e(json.dumps(p["tags"],ensure_ascii=False))}"><time datetime="{p["date"]}">{p["date"]}</time><div><h2><a href="/blog/{p["slug"]}/">{e(p["title"])}</a></h2><p>{e(p["summary"])}</p><span class="blog-meta">{e(" · ".join(p["tags"]))} · {"中文" if p["lang"]=="zh" else "English"}</span></div><a aria-label="{e(p["title"])}" href="/blog/{p["slug"]}/">↗</a></article>')
    return ''.join(output)

def article_body(p, posts):
    html, toc = render_markdown(p['body'], p['url'])
    origin = tr('原文', 'Original', p['lang'])
    export = export_markdown(p)
    share_html = html+f'<hr><p>{origin}：<a href="{e(p["url"])}">{e(p["url"])}</a></p>'
    payload = {k:p[k] for k in ('title','summary','url','lang','cover','updated')}
    payload.update(html=share_html, markdown=export)
    payload['digest'] = sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    intro = f'<header class="blog-article-head"><p class="eyebrow"><a href="{("/en" if p["lang"]=="en" else "")}/blog/">Blog</a> / {e(" · ".join(p["tags"]))}</p><h1>{e(p["title"])}</h1><p class="blog-meta">Haoran Feng · <time datetime="{p["date"]}">{p["date"]}</time>'
    if p['updated']!=p['date']:
        intro += ' · '+tr('更新于 ','Updated ',p['lang'])+p['updated']
    intro += '</p>'
    if p['summary']:
        intro += f'<p class="page-lead">{e(p["summary"])}</p>'
    intro += '</header>'
    labels = [('url','复制链接','Copy link'),('citation','复制引用（洛谷）','Copy Markdown link'),('markdown','复制 Markdown','Copy Markdown')]
    toolbar = '<div class="blog-actions">'+''.join(f'<button type="button" data-blog-copy="{kind}">{tr(zh,en,p["lang"])}</button>' for kind,zh,en in labels)
    toolbar += f'<a href="/blog/{p["slug"]}/article.md" download>{tr("下载 Markdown","Download Markdown",p["lang"])}</a><button type="button" id="open-sync">{tr("同步到 CSDN / 知乎","Sync to CSDN / Zhihu",p["lang"])}</button></div><p id="blog-status" class="blog-meta" role="status" aria-live="polite"></p>'
    cover = f'<figure><img src="{e(p["cover"])}" alt="" decoding="async"></figure>' if p['cover'] else ''
    contents = '<details class="blog-toc"><summary>'+tr('目录','Contents',p['lang'])+'</summary><nav>'+''.join(f'<a href="#{ident}">{e(title)}</a>' for ident,title in toc)+'</nav></details>' if toc else ''
    cross = '<p class="blog-meta">'+tr('其他平台：','Also on: ',p['lang'])+' · '.join(f'<a href="{e(url)}" rel="noopener noreferrer" target="_blank">{e(key)}</a>' for key,url in p['links'].items())+'</p>' if p['links'] else ''
    body = '<div class="shell blog-reading">'+intro+toolbar+cover+contents+f'<article class="blog-prose" id="article-body">{html}</article>'+cross+'</div>'
    body += '<div id="blog-payload" hidden data-url="/blog/'+p['slug']+'/article.json"></div>'+sync_dialog(p['lang'])
    return body, payload

def sync_dialog(lang):
    return f'''<dialog id="sync-dialog" class="sync-dialog" aria-labelledby="sync-title"><form method="dialog"><button class="dialog-close" aria-label="Close">×</button></form><h2 id="sync-title">{tr('分发文章','Distribute this article',lang)}</h2><p>{tr('将本文发送到所选账号的草稿箱，检查排版后再发布。','Send to selected accounts as drafts; review formatting before publishing.',lang)}</p><p class="blog-meta">{tr('需要同一浏览器安装 Wechatsync，并登录对应平台。','Install Wechatsync and sign in to the platforms in this browser.',lang)} <a href="{SYNC}" rel="noopener noreferrer" target="_blank">Wechatsync ↗</a></p><button type="button" id="detect-sync">{tr('检测已登录账号','Detect signed-in accounts',lang)}</button><fieldset id="sync-accounts"><legend>{tr('选择平台','Choose platforms',lang)}</legend><p>{tr('点击检测后显示账号。','Detect accounts to continue.',lang)}</p></fieldset><button type="button" id="start-sync" disabled>{tr('同步到所选草稿箱','Send to selected drafts',lang)}</button><p id="sync-status" role="status" aria-live="polite"></p><div id="sync-results"></div><p class="blog-meta">{tr('再次同步可能新建草稿，不会自动覆盖平台上已发布的文章。','Resending may create new drafts; published platform posts are not automatically overwritten.',lang)}</p></dialog>'''

def admin_body(lang):
    zh = lang == 'zh'
    title = '写作台' if zh else 'Writing desk'
    body = f'<section class="compact-page-head"><div class="shell"><span class="eyebrow">Write once · Share anywhere</span><h1>{title}</h1><p class="page-lead">'+tr('文章留在自己的站点，讨论发生在更远的地方。','Keep the original here. Take the conversation elsewhere.',lang)+f'</p><div class="blog-actions"><a class="blog-primary" href="{CMS}" target="_blank" rel="noopener noreferrer">'+tr('用 GitHub 登录写作后台 ↗','Open editor · Sign in with GitHub ↗',lang)+'</a><a href="/blog/">'+tr('查看博客','View blog',lang)+'</a></div></div></section>'
    steps = [('01 / 写作','01 / Write','首次打开 Pages CMS，用 GitHub 登录，仅授权 XFDG/xfdg.github.io。进入「博客文章」，填写标题、固定地址、日期和正文；编辑器支持 Markdown 源码与图片上传。','Sign into Pages CMS with GitHub and grant access only to XFDG/xfdg.github.io. Open Blog posts; enter the title, stable slug, date and body. Markdown source mode and image uploads are available.'),('02 / 发布','02 / Publish','打开「发布到网站」再保存。GitHub 自动构建文章、目录与 RSS；完成后访问 /blog/固定地址/。首次发布后不要随意修改固定地址。','Enable Publish to website and save. GitHub builds the article, index and RSS. Open /blog/your-slug/ when the build completes; keep the slug stable.'),('03 / 分发','03 / Distribute','在文章页复制链接或 Markdown 引用到洛谷；同步按钮调用浏览器中的 Wechatsync，把正文和图片发送到 CSDN / 知乎草稿箱，再到平台确认发布。','Copy a link or Markdown citation for Luogu. Use Wechatsync from the article page to send content and images to CSDN / Zhihu drafts, then confirm publication on those platforms.')]
    body += '<section class="dense-section section-line"><div class="shell admin-steps">'+''.join('<section><h2>'+tr(a,b,lang)+'</h2><p>'+tr(c,d,lang)+'</p></section>' for a,b,c,d in steps)+'</div></section>'
    body += '<section class="dense-section section-line"><div class="shell blog-reading"><h2>'+tr('开始之前','Before writing',lang)+'</h2><p>'+tr('当前仓库是公开的：后台保存的未发布文章仍能在 GitHub 源文件与历史记录中看到。未准备公开的内容，请先写在本地；发布开关仅控制网站是否展示。','This repository is public: unpublished CMS entries remain visible in GitHub source and history. Keep private drafts locally. The publish switch controls site visibility, not confidentiality.',lang)+'</p><p>'+tr('Wechatsync 是第三方浏览器扩展，安装前请检查它的账号与网站访问权限。本站不要求输入平台密码、Cookie 或 GitHub Token。公式和复杂排版在跨平台后仍建议检查；平台更新也可能导致同步失败。','Wechatsync is a third-party browser extension; review its account and site permissions before installation. This site does not ask for passwords, cookies or GitHub tokens. Check formulas and complex formatting in destination drafts; platform changes can break adapters.',lang)+'</p><div class="blog-actions"><a href="https://pagescms.org/docs/quick-start/" target="_blank" rel="noopener noreferrer">Pages CMS</a><a href="'+SYNC+'" target="_blank" rel="noopener noreferrer">Wechatsync</a><a href="https://github.com/XFDG/xfdg.github.io/actions" target="_blank" rel="noopener noreferrer">'+tr('构建状态','Build status',lang)+'</a><a href="/admin/post-template.md" download>'+tr('下载文章模板','Download post template',lang)+'</a></div></div></section>'
    body += '<section class="dense-section section-line"><div class="shell blog-reading"><h2>'+tr('本地草稿便笺','Local scratchpad',lang)+'</h2><p class="blog-meta">'+tr('仅保存在当前浏览器，不会上传。清理浏览器数据会丢失，请及时导出。正文准备好后可复制到后台的 Source 模式。','Stored only in this browser; never uploaded. Export a backup before clearing browser data. Paste the finished text into Source mode in the editor.',lang)+'</p><label for="scratch">Markdown</label><textarea id="scratch" spellcheck="false" rows="16" placeholder="# 标题\n\n从一个问题开始……"></textarea><div class="blog-actions"><button id="scratch-export" type="button">'+tr('导出 .md','Export .md',lang)+'</button><button id="scratch-copy" type="button">'+tr('复制正文','Copy text',lang)+'</button><button id="scratch-clear" type="button">'+tr('清空本地便笺','Clear local scratchpad',lang)+'</button></div><p id="scratch-status" role="status" class="blog-meta"></p></div></section>'
    return title, body

def write(path, content):
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding='utf-8')

def build():
    source = ROOT/'content/posts'
    source.mkdir(parents=True, exist_ok=True)
    posts = load_posts(source)
    lookup = {p['slug']:p for p in posts}
    expected = set()
    for p in posts:
        body, payload = article_body(p, posts)
        prefix = f'blog/{p["slug"]}'
        path = prefix+'/index.html'
        write(path, MARKER+page(path, p['title'],p['summary'],body,p['lang'],article=p,translations=lookup))
        write(prefix+'/article.json',json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
        write(prefix+'/article.md',payload['markdown'])
        expected.add(p['slug'])
    # Remove only our previously generated article files, never arbitrary folders.
    for f in (ROOT/'blog').glob('*/index.html'):
        if f.parent.name not in expected and f.read_text(encoding='utf-8').startswith(MARKER):
            for name in ('index.html','article.json','article.md'):
                (f.parent/name).unlink(missing_ok=True)
            if not any(f.parent.iterdir()):
                f.parent.rmdir()
    for lang in ('zh','en'):
        prefix = 'en/' if lang=='en' else ''
        title = tr('博客与心得','Blog & notes',lang)
        body = '<section class="compact-page-head"><div class="shell"><span class="eyebrow">Notes / Essays / Experiments</span><h1>'+title+'</h1><p class="page-lead">'+tr('记录做过的事，想清楚的问题，以及还没想明白的部分。','Work in progress, lessons learned, and questions worth keeping.',lang)+'</p><div class="blog-actions"><a href="/'+prefix+'admin/">'+tr('写文章','Write a post',lang)+'</a><a href="/blog/feed.xml">RSS</a><a href="/'+prefix+'writing.html">'+tr('技术资料','Technical writing',lang)+'</a></div></div></section>'
        filters = '<div class="blog-search"><label for="blog-search">'+tr('搜索文章','Search posts',lang)+'</label><input id="blog-search" type="search" placeholder="'+tr('标题、摘要、标签','Title, summary, tags',lang)+'"><label for="blog-tag">'+tr('标签','Tag',lang)+'</label><select id="blog-tag"><option value="">'+tr('全部','All',lang)+'</option>'+''.join(f'<option>{e(t)}</option>' for t in sorted({t for p in posts for t in p['tags']}))+'</select></div>'
        body += '<section class="dense-section section-line"><div class="shell">'+filters+post_rows(posts,lang)+'<p id="blog-no-results" hidden>'+tr('没有匹配的文章。','No matching posts.',lang)+'</p></div></section>'
        write(prefix+'blog/index.html',page('blog/index.html',title,title,body,lang))
        admin_title,admin = admin_body(lang)
        write(prefix+'admin/index.html',page('admin/index.html',admin_title,admin_title,admin,lang,noindex=True))
        f = ROOT/(prefix+'writing.html')
        if f.exists():
            text = f.read_text(encoding='utf-8')
            text = re.sub(r'<!-- blog-latest:start -->.*?<!-- blog-latest:end -->','',text,flags=re.S)
            block = '<!-- blog-latest:start --><section class="dense-section section-line"><div class="shell"><div class="dense-heading"><h2>'+tr('博客与心得','Blog & notes',lang)+'</h2><div class="blog-actions"><a href="/'+prefix+'blog/">'+tr('全部文章 →','All posts →',lang)+'</a><a href="/'+prefix+'admin/">'+tr('写文章','Write',lang)+'</a></div></div>'+post_rows(posts[:4],lang)+'</div></section><!-- blog-latest:end -->'
            if '</section>' not in text:
                raise ValueError('Writing page does not have the expected section layout')
            text = text.replace('</section>','</section>'+block,1)
            if '/assets/blog/blog.css' not in text:
                text = text.replace('</head>','<link rel="stylesheet" href="/assets/blog/blog.css?v=1"></head>')
            f.write_text(text,encoding='utf-8')
    rss = ET.Element('rss',version='2.0')
    channel = ET.SubElement(rss,'channel')
    for key,val in [('title','Haoran Feng — Blog'),('link',BASE+'/blog/'),('description','Technical notes and reflections by Haoran Feng')]:
        ET.SubElement(channel,key).text=val
    for p in posts:
        item = ET.SubElement(channel,'item')
        values = [('title',p['title']),('link',p['url']),('guid',p['url']),('description',p['summary']),('pubDate',format_datetime(datetime.combine(date.fromisoformat(p['date']),datetime.min.time(),tzinfo=timezone.utc)))]
        for key,val in values:
            ET.SubElement(item,key).text=val
    write('blog/feed.xml',ET.tostring(rss,encoding='unicode',xml_declaration=True))
    write('blog/index.json',json.dumps([{k:p[k] for k in ('title','url','date','updated','lang','tags','summary')} for p in posts],ensure_ascii=False,indent=2)+'\n')
    # Merge blog URLs into the existing portfolio sitemap (idempotent).
    sitemap=ROOT/'sitemap.xml'
    ns='http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('',ns)
    xml=ET.parse(sitemap).getroot() if sitemap.exists() else ET.Element('{'+ns+'}urlset')
    for entry in list(xml):
        loc=entry.find('{'+ns+'}loc')
        if loc is not None and (loc.text or '').startswith((BASE+'/blog/',BASE+'/en/blog/',BASE+'/admin/',BASE+'/en/admin/')):
            xml.remove(entry)
    for url in [BASE+'/blog/',BASE+'/en/blog/']+[p['url'] for p in posts]:
        entry=ET.SubElement(xml,'{'+ns+'}url')
        ET.SubElement(entry,'{'+ns+'}loc').text=url
    write('sitemap.xml',ET.tostring(xml,encoding='unicode',xml_declaration=True))
    print(f'Blog: {len(posts)} published article(s); bilingual indexes and writing desk ready')

class BlogTests(unittest.TestCase):
    def make(self, folder, meta=None, body='## Hello\n\nText.'):
        data=dict(title='A title',slug='a-title',date='2026-10-08',published=True,lang='zh',tags=['CUDA'])
        data.update(meta or {})
        path=Path(folder)/'a-title.md'
        path.write_text('---\n'+yaml.safe_dump(data,allow_unicode=True)+'---\n'+body,encoding='utf-8')
        return path
    def test_published_requires_real_boolean(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(parse_post(self.make(d,{'published':False})))
            with self.assertRaises(ValueError): parse_post(self.make(d,{'published':'false'}))
    def test_metadata_and_url(self):
        with tempfile.TemporaryDirectory() as d:
            p=parse_post(self.make(d))
            self.assertEqual(p['url'],BASE+'/blog/a-title/')
            for meta in [{'slug':'../secret'},{'date':'bad'},{'cover':'javascript:alert(1)'},{'updated':'2020-01-01'},{'lang':'xx'}]:
                with self.assertRaises(ValueError): parse_post(self.make(d,meta))
    def test_duplicate_and_translation(self):
        with tempfile.TemporaryDirectory() as d:
            p=self.make(d)
            (Path(d)/'duplicate.md').write_text(p.read_text())
            with self.assertRaises(ValueError): load_posts(Path(d))
            (Path(d)/'duplicate.md').unlink()
            self.make(d,{'translation':'nonexistent'})
            with self.assertRaises(ValueError): load_posts(Path(d))
    def test_raw_html_and_unsafe_links(self):
        html,_=render_markdown('<script>alert(1)</script>\n\n[x](javascript:alert(1))\n\n# Heading',BASE+'/blog/a/')
        self.assertNotIn('<script>',html)
        self.assertNotIn('href="javascript:',html)
        self.assertIn('<h2 id="section-1">Heading</h2>',html)
    def test_math_code_and_table(self):
        html,toc=render_markdown('## 算法\n\n$a^2$\n\n$$\n\\sum_i x_i\n$$\n\n```cpp\nint x = 1; // $a$\n```\n\n| A | B |\n| --- | --- |\n| 1 | 2 |',BASE+'/blog/a/')
        self.assertIn('class="math"',html)
        self.assertIn('math-display',html)
        self.assertIn('<table>',html)
        self.assertEqual(len(toc),1)
    def test_exports_and_relative_images(self):
        with tempfile.TemporaryDirectory() as d:
            p=parse_post(self.make(d,body='![img](/assets/blog/images/a.png)\n\n```md\n![example](/assets/blog/images/a.png)\n```'))
            md=export_markdown(p)
            self.assertIn('('+BASE+'/assets/blog/images/a.png)',md)
            self.assertIn('![example](/assets/blog/images/a.png)',md)
            html,_=render_markdown(p['body'],p['url'])
            self.assertIn('src="'+BASE+'/assets/blog/images/a.png"',html)
    def test_no_private_drafts(self):
        with tempfile.TemporaryDirectory() as d:
            self.make(d,{'published':False},body='DO-NOT-PUBLISH')
            self.assertEqual(load_posts(Path(d)),[])
    def test_no_fake_translations(self):
        with tempfile.TemporaryDirectory() as d:
            a=self.make(d,{'translation':'a-title-en'})
            data=a.read_text().replace('slug: a-title\n','slug: a-title-en\n').replace('lang: zh','lang: en').replace('translation: a-title-en','translation: a-title')
            (Path(d)/'a-title-en.md').write_text(data)
            self.assertEqual(len(load_posts(Path(d))),2)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--test',action='store_true')
    args=parser.parse_args()
    if args.test:
        unittest.main(argv=[sys.argv[0]],verbosity=2)
    else:
        build()
