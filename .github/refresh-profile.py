"""One-time, guarded migration for the public resume and merged-only OSS snapshot."""
from __future__ import annotations
import ast
import json
import os
import re
import base64
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT=Path.cwd()
TOKEN=os.environ['GH_TOKEN']
def api(path):
    request=Request('https://api.github.com/'+path,headers={'Authorization':'Bearer '+TOKEN,'Accept':'application/vnd.github+json','User-Agent':'portfolio-maintenance'})
    with urlopen(request,timeout=40) as response: return json.load(response)

blob=api('repos/XFDG/xfdg.github.io/git/blobs/00bcdf3b3e5b95cd42e73b965b6660ecdbe52724')
module=base64.b64decode(blob['content']).decode('utf-8')
module=re.sub(r",'1[3-9][0-9]{9}'",'',module)
module=re.sub(r",'[0-9]{9}'",'',module)
assert not re.search(r'(?<![0-9])1[3-9][0-9]{9}(?![0-9])',module)
(ROOT/'tools/build_anonymous_resume.py').write_text(module,encoding='utf-8')

status_path=ROOT/'content/portfolio_status.json'
status=json.loads(status_path.read_text(encoding='utf-8'))
new_groups=[
 {'name':'vLLM','repo':'vllm-project/vllm','category':'community','page':'opensource.html#vllm','prs':[
  {'number':58143,'state':'merged','zh':'修复 Cross-Encoder padding token_type_ids 的填充与区间压缩/重建语义，并补充回归验证。','en':'Preserve cross-encoder padding token types through padding, range compression and reconstruction, with regression coverage.'}]},
 {'name':'DeepSpeed','repo':'deepspeedai/DeepSpeed','category':'community','page':'opensource.html#deepspeed','prs':[
  {'number':8818,'state':'merged','zh':'修复 ZeRO-1/2 与 ZenFlow overlap 路径的 BF16 overflow-check opt-out，同时保留 FP32/FP16 非有限梯度保护。','en':'Honor BF16 overflow-check opt-out in ZeRO-1/2 and ZenFlow overlap while retaining FP32/FP16 nonfinite-gradient protection.'}]}
]
for group in new_groups:
    if not any(g['repo']==group['repo'] for g in status['groups']): status['groups'].append(group)
query='author:XFDG is:pr is:merged -user:XFDG'
items=[]
for page in range(1,11):
    data=api('search/issues?'+urlencode({'q':query,'per_page':100,'page':page}))
    assert not data.get('incomplete_results'), 'Incomplete GitHub search; abort rather than publish a partial count'
    items.extend(data['items'])
    if len(items)>=data['total_count']: break
else: raise RuntimeError('Too many pages')
for group in status['groups']:
    known={p['number']:p for p in group['prs']}
    selected=[i for i in items if i['repository_url'].endswith('/repos/'+group['repo'])]
    verified=[]
    for item in selected:
        pr=api('repos/'+group['repo']+'/pulls/'+str(item['number']))
        assert pr['merged'] is True and pr['merged_at'] and pr['user']['login']=='XFDG'
        old=known.get(pr['number'],{'zh':pr['title'],'en':pr['title']})
        verified.append({'number':pr['number'],'state':'merged','merged_at':pr['merged_at'],'merge_commit_sha':pr['merge_commit_sha'],'url':pr['html_url'],'zh':old['zh'],'en':old['en']})
    assert verified, 'Unexpected empty repository: '+group['repo']
    group['prs']=sorted(verified,key=lambda p:p['merged_at'],reverse=True)
status['verified_on']='2026-10-28'
status['scope']='Merged upstream PRs only, in selected AI infrastructure repositories; community and internship contributions are identified separately.'
status.pop('tracked_open',None)
status['verification']={'query':query,'author':'XFDG','method':'GitHub merged search plus individual PR merged/author verification'}
status_path.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Verified merged counts:',{g['name']:len(g['prs']) for g in status['groups']})

p=ROOT/'tools/build_portfolio.py'
s=p.read_text(encoding='utf-8')
def replace(old,new):
    global s
    if old not in s: raise RuntimeError('Missing patch anchor: '+old[:90])
    s=s.replace(old,new)
replace('覆盖 5 个 AI Infra 项目','覆盖 {len(GROUPS)} 个 AI Infra 项目')
replace('across five AI infrastructure projects','across {len(GROUPS)} AI infrastructure projects')
replace('本人 2026 年 9 月简历与工程记录摘要','本人最新简历与工程记录摘要')
replace('the author’s September 2026 resume','the author’s latest supplied resume')
for old,new in [
 ('48 层 Router 测量工作负载','代表 Router 测量工作负载'),
 ('measured 48-layer router workload','representative router workload'),
 ('48 层测试工作负载','代表 Router 测试工作负载'),
 ('48-layer test workload','representative router test workload'),
 ('48 层是此项优化的测量工作负载，并非对已发布 IQuest-Q1 层数的描述。',''),
 ('The 48 layers describe this measurement workload, not the released IQuest-Q1 architecture. ',''),
 ('128 GPUs · 300B-class · 200-step rollout','128 GPUs · 200-step rollout'),
 ('128 卡、300B 级模型的','128 卡研发配置的'),
 ('128-GPU, 300B-class','128-GPU'),
 ('300B 级模型','大规模研发模型'),
 ('300B-class development','large-scale development'),
 ('Prefix-cache hit 下整请求处理性能','async OE + prefix-cache hit 下整请求吞吐'),
 ('Full-request performance with prefix-cache hits','Full-request throughput with async OE and prefix-cache hits'),
 ('prefix-cache hit 下 TP1 / TP2 整请求处理性能','async OE + prefix-cache hit 下 TP1 / TP2 整请求吞吐'),
 ('Full-request performance with prefix-cache hits:','Full-request throughput with async OE and prefix-cache hits:'),
 ('维护上游贡献与回归测试；单独跟进尚未合入的 PR。','维护已合入的上游贡献与回归测试。'),
 ('Maintain upstream contributions and regression tests; track open PRs separately.','Maintain merged upstream contributions and regression tests.')
]: s=s.replace(old,new)
replace("    body=head(title,tx(('大模型系统与 GPU 性能工程'", "    contacts += '<div class=\"quick-links no-print\">'+link('/assets/resume/anonymous-zh.pdf',tx(('匿名简历 PDF · 中文','Anonymous PDF · Chinese'),lang),False)+link('/assets/resume/anonymous-en.pdf',tx(('匿名简历 PDF · English','Anonymous PDF · English'),lang),False)+'</div>'\n    body=head(title,tx(('大模型系统与 GPU 性能工程'")

new_oss='''def opensource(lang: str) -> None:
    title=tx(('开源贡献','Open source'),lang)
    lead=tx((f'{TOTAL} 个已合入 PR，覆盖 {len(GROUPS)} 个 AI Infra 项目。',f'{TOTAL} merged PRs across {len(GROUPS)} AI infrastructure projects.'),lang)
    body=head(title,lead,lang,'Merged upstream contributions',f'<p class="section-note">{tx(("核验日期","Verified"),lang)}: {SNAPSHOT}</p>')
    body+=section(tx(('概览','Overview'),lang),oss_summary(lang))
    ids={'Mooncake':'mooncake','TensorFlow MUSA':'musa','Ray':'ray','FlashInfer':'flashinfer','Mirage':'mirage','vLLM':'vllm','DeepSpeed':'deepspeed'}
    for g in GROUPS:
        label=tx(('实习产出','Internship'),lang) if g['category']=='internship' else tx(('社区贡献','Community'),lang)
        body+=section(g['name'],pr_table(g,lang),f'<span>{label} · {len(g["prs"])} merged</span>',ids[g['name']])
    note=tx((f'{COMMUNITY} 个社区贡献与 {INTERNSHIP} 个实习产出；仅统计本人提交且上游已合入的 PR。',f'{COMMUNITY} community contributions and {INTERNSHIP} internship outputs; only authored, merged upstream PRs are counted.'),lang)
    body+=section(tx(('统计口径','Scope'),lang),para(note),reading=True)
    write_page('opensource.html',title,lead,body,lang,'opensource')
    g=next(g for g in GROUPS if g['name']=='Mooncake')
    body=head('Mooncake',tx(('分布式 KV Cache 的存储、RDMA 与正确性修复。','Storage, RDMA and correctness fixes for a distributed KV cache.'),lang),lang,'Open source',f'<p class="section-note">{len(g["prs"])} merged · {SNAPSHOT}</p>')
    body+=section(tx(('已合入上游','Merged upstream'),lang),pr_table(g,lang))
    write_page('projects/mooncake-contributions.html','Mooncake',tx(('Mooncake 上游贡献','Mooncake upstream contributions'),lang),body,lang)
    g=next(g for g in GROUPS if g['name']=='Mirage')
    body=head('Mirage',tx(('Qwen3 示例中的 padding / Argmax 正确性修复。','Padding / Argmax correctness in Qwen3 demos.'),lang),lang,'Open source')+section(tx(('已合入记录','Merged record'),lang),pr_table(g,lang))
    body+=section(tx(('修改范围','Scope'),lang),para(tx(('PR #755 调整 9 个示例脚本中的 lm_head padding 初始化，处理 padding 参与 Argmax 的异常 token 问题。','PR #755 changes lm_head padding initialization in nine demo scripts to address invalid tokens from padded Argmax candidates.'),lang)),reading=True)
    write_page('projects/mirage-contribution.html','Mirage',tx(('Mirage 上游贡献','Mirage upstream contribution'),lang),body,lang)
'''
new_pr_table='''def pr_table(g: dict, lang: str) -> str:
    rows=[]
    for pr in g['prs']:
        assert pr['state']=='merged' and pr.get('merged_at')
        rows.append([link(pr['url'], '#'+str(pr['number'])+' ↗'), esc(pr[lang]), esc(pr['merged_at'][:10])])
    return table([tx(('PR','PR'),lang),tx(('贡献','Contribution'),lang),tx(('合入日期（UTC）','Merged (UTC)'),lang)],rows,'oss-table')
'''
def replace_function(name,new):
    global s
    node=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name==name)
    lines=s.splitlines(keepends=True)
    s=''.join(lines[:node.lineno-1])+new+'\n'+''.join(lines[node.end_lineno:])
replace_function('opensource',new_oss)
replace_function('pr_table',new_pr_table)
replace('    sitemap()\n', '    from build_anonymous_resume import main as build_anonymous\n    build_anonymous()\n    sitemap()\n')
replace("or f.name=='404.html':", "or f.name in ('404.html','anonymous-resume.html'):")
compile(s,str(p),'exec'); p.write_text(s,encoding='utf-8')
req=ROOT/'tools/blog-requirements.txt'
text=req.read_text()
if 'reportlab==' not in text: req.write_text(text.rstrip()+'\nreportlab==4.4.9\n')
workflow=ROOT/'.github/workflows/build-bilingual-site.yml'
w=workflow.read_text(); w=w.replace('git add -- \'*.html\' en projects blog sitemap.xml','git add -- \'*.html\' en projects blog sitemap.xml assets/resume')
workflow.write_text(w)
check=ROOT/'tools/check_portfolio.py'
c=check.read_text()
c=c.replace("    if ('kvcache-ai/Mooncake',3661) in flat: errors.append('Unmerged #3661 counted as merged')", "    if any(p.get('state')!='merged' or not p.get('merged_at') for g in data['groups'] for p in g['prs']): errors.append('Unverified or unmerged PR in snapshot')")
check.write_text(c)
live=ROOT/'tools/check_live_site.py'
l=live.read_text().replace("'resume.html', 'en/resume.html', 'portfolio.css', 'script.js')", "'resume.html', 'en/resume.html', 'portfolio.css', 'script.js',\n         'assets/resume/anonymous-zh.pdf', 'assets/resume/anonymous-en.pdf')")
live.write_text(l)
print('Patched source generator, merged-only listing, anonymous downloads and release checks')
