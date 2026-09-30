"""Build the public bilingual portfolio from reviewed content; no network calls.

Engineering results below come from the owner's September 2026 resume. Model
specifications come from IQuestLab/IQuest-Q1 README. PR metadata is kept in a
separate, explicitly dated snapshot. Team results are not personal benchmarks.
Existing archival project pages and assets are preserved.
"""
from __future__ import annotations

import json
from html import escape as esc
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://xfdg.github.io'
EMAIL = '225010160@link.cuhk.edu.cn'
GITHUB = 'https://github.com/XFDG'
CSDN = 'https://blog.csdn.net/XFDG01'
ZHIHU = 'https://www.zhihu.com/people/xian-feng-dao-gu-73-49'
MODEL = 'https://github.com/IQuestLab/IQuest-Q1'
HF = 'https://huggingface.co/IQuestLab/IQuest-Q1'
LAB = 'https://iquestlab.github.io/'
PAPER = 'https://openreview.net/forum?id=6eDZdA6IGW'
PAPER_TITLE = 'From Structure to Preference: Token Weighting for Chain-of-Thought Distillation in Large Language Models'
STATUS = json.loads((ROOT / 'content/portfolio_status.json').read_text(encoding='utf-8'))
GROUPS = STATUS['groups']
SNAPSHOT = STATUS['verified_on']
TOTAL = sum(len(g['prs']) for g in GROUPS)
COMMUNITY = sum(len(g['prs']) for g in GROUPS if g['category'] == 'community')
INTERNSHIP = TOTAL - COMMUNITY
BUILT: list[str] = []


def tx(value: str | tuple[str, str], lang: str) -> str:
    return value if isinstance(value, str) else value[0 if lang == 'zh' else 1]


def local(path: str, lang: str) -> str:
    return ('/en/' if lang == 'en' else '/') + ('' if path == 'index.html' else path)


def link(url: str, label: str, external: bool = True) -> str:
    attrs = ' target="_blank" rel="noopener noreferrer"' if external else ''
    return f'<a href="{esc(url, quote=True)}"{attrs}>{label}</a>'


def ilink(path: str, label: str, lang: str) -> str:
    return link(local(path, lang), esc(label), False)


def para(text: str) -> str:
    return f'<p>{text}</p>'


def bullets(items: list[str]) -> str:
    return '<ul class="fact-list">' + ''.join(f'<li>{s}</li>' for s in items) + '</ul>'


def section(title: str, body: str, note: str = '', ident: str = '', reading: bool = False) -> str:
    sid = f' id="{esc(ident)}"' if ident else ''
    return f'<section class="dense-section section-line"{sid}><div class="shell{" reading" if reading else ""}"><div class="dense-heading"><h2>{esc(title)}</h2>{note}</div>{body}</div></section>'


def table(headers: list[str], rows: list[list[str]], cls: str = '') -> str:
    head = ''.join(f'<th scope="col">{esc(h)}</th>' for h in headers)
    body = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<div class="table-wrap"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def head(title: str, lead: str, lang: str, eyebrow: str = '', extra: str = '') -> str:
    return f'<section class="compact-page-head"><div class="shell"><span class="eyebrow">{esc(eyebrow)}</span><h1>{esc(title)}</h1><p class="page-lead">{lead}</p>{extra}</div></section>'


def shell(path: str, title: str, description: str, body: str, lang: str, key: str) -> str:
    zh, en = BASE + local(path, 'zh'), BASE + local(path, 'en')
    canonical = zh if lang == 'zh' else en
    items = [('home', 'index.html', ('首页', 'Home')), ('projects', 'projects.html', ('项目', 'Work')), ('experience', 'experience.html', ('经历', 'Experience')), ('writing', 'writing.html', ('文章', 'Writing')), ('contact', 'contact.html', ('联系', 'Contact')), ('resume', 'resume.html', ('简历', 'Résumé'))]
    nav = ''.join(f'<a data-nav="{k}" href="{local(p,lang)}"' + (' class="active" aria-current="page"' if k == key else '') + f'>{tx(t,lang)}</a>' for k,p,t in items)
    switch = '<span class="language-switch" aria-label="Language">' + link(local(path,'zh'), '中', False).replace('>中', (' class="is-active" aria-current="page"' if lang == 'zh' else ' lang="zh-CN"') + '>中') + '<span class="language-divider" aria-hidden="true">/</span>' + link(local(path,'en'), 'EN', False).replace('>EN', (' class="is-active" aria-current="page"' if lang == 'en' else ' lang="en"') + '>EN') + '</span>'
    return f'''<!doctype html>
<html lang="{'zh-CN' if lang == 'zh' else 'en'}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — Haoran Feng</title><meta name="description" content="{esc(description,quote=True)}">
<meta name="theme-color" content="#f4f2ed"><meta property="og:title" content="{esc(title,quote=True)} — Haoran Feng"><meta property="og:description" content="{esc(description,quote=True)}"><meta property="og:type" content="website"><meta property="og:url" content="{canonical}">
<link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="zh-CN" href="{zh}"><link rel="alternate" hreflang="en" href="{en}"><link rel="alternate" hreflang="x-default" href="{zh}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/portfolio.css?v=20260929"><script src="/script.js" defer></script>
</head>
<body class="portfolio-site" data-page="{key}">
<a class="skip-link" href="#main">{tx(('跳转正文','Skip to content'),lang)}</a>
<header class="site-header"><div class="shell header-inner"><a class="brand" href="{local('index.html',lang)}"><span class="brand-copy">Haoran Feng <small>AI Infrastructure</small></span></a><button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="{tx(('切换导航','Toggle navigation'),lang)}"><span></span></button><nav class="site-nav" id="site-nav" aria-label="{tx(('主导航','Primary navigation'),lang)}">{nav}{switch}</nav></div></header>
<main id="main"{' class="resume-content"' if key == 'resume' else ''}>{body}</main>
<footer class="site-footer"><div class="shell footer-inner"><span>© <span data-year>2026</span> Haoran Feng</span><div class="footer-links">{link('mailto:'+EMAIL,'Email',False)}{link(GITHUB,'GitHub')}{link(CSDN,'CSDN')}{link(ZHIHU,tx(('知乎','Zhihu'),lang))}{ilink('opensource.html',tx(('开源记录','Open source'),lang),lang)}{ilink('roadmap.html','Now',lang)}</div></div></footer>
</body></html>
'''


def write_page(path: str, title: str, lead: str, body: str, lang: str, key: str = 'projects') -> None:
    dest = ('en/' if lang == 'en' else '') + path
    f = ROOT / dest
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(shell(path,title,lead,body,lang,key), encoding='utf-8')
    BUILT.append(dest)


DETAILS = [
    dict(slug='fa3-deterministic-swa', cat='training', title=('FA3：确定性 SWA 反向调度','FA3: deterministic SWA backward scheduling'),
         summary=('缩短 dQ semaphore 依赖链，在原 fused kernel 内调整 ticket 与 reverse scheduler。','Shorten the dQ semaphore dependency chain inside the fused kernel.'), evidence=('完整 backward · 3.98×','Full backward · 3.98×'),
         problem=('长序列、确定性模式下的 SWA backward 出现性能回退。目标是在不破坏逐位确定性的前提下缩短反向传播耗时。','Long-sequence sliding-window attention regressed in deterministic backward mode. The goal was lower backward latency without losing bitwise determinism.'),
         work=('负责问题归因、调度实现和回归验证。使用 Nsys / NCU 定位 dQ semaphore 依赖链，在原 fused kernel 内实现 contributor-relative ticket，并与 reverse scheduler 对齐。','Owned diagnosis, scheduling changes and validation. Nsys / NCU isolated the dQ semaphore dependency chain; contributor-relative tickets were implemented in the existing fused kernel and aligned with the reverse scheduler.'),
         results=[('代表 packed shape 的完整 backward','Full backward, representative packed shape','6.755 ms → 1.699 ms · 3.98×'),('2K–12K 测试范围','Tested 2K–12K sequence range','1.59–5.37×'),('回归覆盖','Regression coverage','3,601'),('逐位确定性重复测试','Repeated bitwise-determinism checks','1,000')],
         delivery=('完成 wheel 交付。','Delivered as a wheel.'),
         boundary=('加速针对所列 SWA backward 工作负载，不等于整轮训练或 IQuest-Q1 最终模型的端到端加速。该工作作为实习工程产出展示，不计入上游 PR 合入统计。','Speedups describe the stated SWA backward workloads, not a full training step or the final IQuest-Q1 model end to end. This is internship engineering work, not a separately counted upstream PR.')),
    dict(slug='fc1-communication',cat='training',title=('FC1：计算与通信竞争优化','FC1: compute–communication contention'),
         summary=('在 4×H200 双 stream 代理上联合调整 NCCL CTA 与 DeepGEMM SM 预算。','Jointly tune NCCL CTA and DeepGEMM SM budgets in a dual-stream, four-H200 proxy.'),evidence=('代理联合耗时 −12.80%','Proxy joint latency −12.80%'),
         problem=('跨 stream 通信与 FC1 计算竞争 GPU 资源，导致原本较快的计算路径在并发时退化。','Communication on a separate stream competed with FC1 for GPU resources, degrading concurrent compute performance.'),
         work=('搭建 4×H200 双 stream 代理，联合控制 NCCL CTA 预算和 DeepGEMM SM budget。完成 121 组粗扫、89 组细扫及复验，并在相同通信配置下隔离控核收益。','Built a dual-stream proxy on four H200 GPUs and co-tuned NCCL CTA and DeepGEMM SM budgets. Ran 121 coarse configurations, 89 fine configurations and rechecks; held communication settings fixed to isolate the compute-budget contribution.'),
         results=[('AllGatherV 代理联合耗时','AllGatherV proxy joint latency','−12.80%'),('相同通信设置下的控核独立贡献','Compute-budget contribution at fixed communication settings','7.58%'),('配置扫描','Configuration sweeps','121 + 89')],
         delivery=('形成联合预算选择与复验方法。','Produced a joint-budget selection and revalidation procedure.'),
         boundary=('这里是双 stream 代理测试，而非完整模型训练吞吐结果；联合收益与控核独立贡献采用不同对照，不能直接相加。','These are dual-stream proxy results, not full-model training throughput. Joint gains and isolated compute-budget gains use different controls and must not be added.')),
    dict(slug='deterministic-router-gemm',cat='inference',title=('确定性 MoE Router GEMM','Deterministic MoE router GEMM'),
         summary=('为小 M decode 接入三级后端，兼顾选核、CUDA Graph 和逐位一致性。','Three backends for small-M decode with CUDA Graph preflight and bitwise checks.'),evidence=('Router 耗时 −73.39%','Router latency −73.39%'),
         problem=('小 M decode 中存在无效 GEMM 计算；同时，选核与 CUDA Graph 路径必须满足确定性约束。','Small-M decode wasted GEMM work while kernel selection and CUDA Graph execution had to satisfy determinism constraints.'),
         work=('在 vLLM 接入 DeepGEMM / Triton Full-K / persistent 三级后端，负责选核、Graph preflight、cache / fallback 与 workspace 管理，并开展 kernel 和模型场景回归。','Integrated DeepGEMM, Triton Full-K and persistent backends into vLLM. Implemented dispatch, Graph preflight, cache/fallback and workspace management, then validated kernel and model scenarios.'),
         results=[('48 层 Router 测量工作负载的中位耗时','Median latency in the measured 48-layer router workload','−73.39%'),('Kernel 逐位一致','Bitwise-matching kernel cases','135 / 135'),('模型场景逐位一致','Bitwise-matching model scenarios','20 / 20'),('Prefix-cache hit 下整请求处理性能','Full-request performance with prefix-cache hits','TP1 +3.81% · TP2 +4.36%')],
         delivery=('覆盖 Kernel dispatch 到推理 Runtime 的完整接入。','Delivered the integration from kernel dispatch to inference runtime.'),
         boundary=('48 层是此项优化的测量工作负载，并非对已发布 IQuest-Q1 层数的描述。Router 局部耗时降幅不等同于整请求收益；后者仅适用于已测 prefix-cache hit 配置。','The 48 layers describe this measurement workload, not the released IQuest-Q1 architecture. The router-only reduction is not an end-to-end gain; request-level results apply to the tested prefix-cache-hit configurations.')),
    dict(slug='oe-async',cat='inference',title=('OE：异步 GPU 状态算子','OE: asynchronous GPU state operators'),
         summary=('将历史 token 状态留在 GPU，以 Triton fused-hash 减少同步与回传。','Keep token history on the GPU and reduce synchronization with Triton fused hashing.'),evidence=('TP1 吞吐 +4.99%','TP1 throughput +4.99%'),
         problem=('历史 token 构造中的同步与 CPU 往返增加 decode 开销；异步化还需要保证请求恢复、slot 复用等跨 step 状态正确。','Token-history construction added synchronization and CPU round trips. Asynchronous execution also required correct state across recovery, slot reuse and decode steps.'),
         work=('在 GPU 侧保留状态，使用 Triton fused-hash 构造输入，并修复请求恢复、slot 复用等跨 step 状态问题。分别验证 TP1 融合路径和 TP2 / TP4 安全路径。','Kept history state on the GPU, built inputs with Triton fused hashing, and fixed cross-step recovery and slot-reuse behavior. Validated the TP1 fused path separately from TP2 / TP4 safe paths.'),
         results=[('TP1 验证与吞吐','TP1 validation and throughput','28 / 28 · +4.99%'),('TP2 安全路径','TP2 safe path','84 / 84 · 0 mismatch · +4.6%'),('TP4 安全路径','TP4 safe path','84 / 84 · 0 mismatch · +3.0%')],
         delivery=('形成分 TP 配置的正确性与性能验收。','Established correctness and performance acceptance by TP configuration.'),
         boundary=('TP1 与 TP2 / TP4 不是同一融合路径。多卡结果仅对应已验证的安全路径，不代表所有配置均可直接启用 fused-hash。','TP1 and TP2 / TP4 do not use the same fused path. Multi-GPU results describe the validated safe path, not universal fused-hash support.')),
    dict(slug='router-replay',cat='rl',title=('R3：MoE 训推路由一致性','R3: MoE training–rollout route consistency'),
         summary=('打通 vLLM 路由采集、传输与 Megatron 回放，扩展到 128 卡研发验证。','Connect vLLM route capture to Megatron replay, with development validation at 128 GPUs.'),evidence=('路由不一致率 → 0','Route mismatch → 0'),
         problem=('vLLM rollout 与 Megatron 训练侧的自然路由存在偏差，需要对齐路由数据、response mask 和概率漂移指标。','Natural routing differed between vLLM rollout and Megatron training. Route data, response masks and probability-drift metrics needed a shared contract.'),
         work=('完成 route 采集、传输与回放链路，建立 response-mask 对齐及 mismatch / fτ² / KL 监控；随后将 rollout 系统扩展到更大模型与多卡规模。','Implemented route capture, transport and replay, with response-mask alignment and mismatch / fτ² / KL monitoring. Extended the rollout system to larger development models and GPU counts.'),
         results=[('8×H200 · Qwen3-30B-A3B · 20-step 路由不一致率','8×H200 · Qwen3-30B-A3B · 20-step route mismatch','17–19% → 0'),('同一对照中的概率漂移指标','Probability-drift metrics in that control experiment','fτ² ↓36–145× · KL ↓4–7×'),('独立的大规模研发验证','Separate large-scale development validation','128 GPUs · 300B-class · 200-step rollout')],
         delivery=('打通 RL 训练与 rollout 的数据和验证闭环。','Connected RL training and rollout through a tested data contract.'),
         boundary=('20-step 小模型指标与 128 卡、300B 级模型的 200-step rollout 是两项不同验证。路由一致不等于最终 reward、收敛或模型质量提升。','The 20-step smaller-model comparison and the 128-GPU, 300B-class 200-step rollout are separate validations. Route consistency alone does not establish improved reward, convergence or model quality.')),
    dict(slug='flashinfer-ftz',cat='rl',title=('FlashInfer：CUDA Graph hang 排障','FlashInfer: diagnosing a CUDA Graph hang'),
         summary=('两卡最小复现定位 Lamport sentinel 的 FTZ 误判，回移上游修复。','A two-GPU reproducer isolated FTZ-sensitive sentinel handling; an upstream fix was backported.'),evidence=('模型级 Graph 回归','Model-level Graph regression'),
         problem=('H200、TP=2 的 rollout 在 CUDA Graph 路径卡死，外层表现为 hang 或 RPC timeout。','H200 TP=2 rollout hung in a CUDA Graph path, surfacing as a hang or RPC timeout.'),
         work=('构建两卡最小复现，通过 eager / Graph、fused / unfused 控制变量定位 Lamport sentinel 的 FTZ 误判。回移上游位级判断修复，并完成模型级 Graph replay 回归。','Built a two-GPU reproducer and compared eager/Graph and fused/unfused execution. Isolated FTZ-sensitive Lamport sentinel handling, backported the upstream bitwise fix and ran model-level Graph replay regression.'),
         results=[('修复后重复 Graph replay','Repeated Graph replay after the fix','No observed hang / timeout')],
         delivery=('完成根因隔离、补丁回移与回归验证。','Completed root-cause isolation, backporting and regression validation.'),
         boundary=('此项为实习期间的上游修复回移与验证，不宣称原创上游修复。另行合入的 FlashInfer #5171 是已安装包测试兼容性修复，两者分开记录。','This is an internship backport and validation, not authorship of the original upstream fix. The separately merged FlashInfer #5171 addresses installed-package tests and is recorded independently.')),
    dict(slug='quant-runtime',cat='runtime',title=('LLMQRT：量化推理 Runtime','LLMQRT: quantized inference runtime'),
         summary=('基于 PyTorch Extension，为 H200 双卡交付 32B 量化推理与 Tensor Parallel。','A PyTorch Extension runtime for two-H200, 32B quantized inference and tensor parallelism.'),evidence=('输出吞吐 +76.8%','Output throughput +76.8%'),
         problem=('面向 H200 双卡上的 32B 量化推理，需要打通量化后端、Attention、KV Cache 与多卡通信，并排除尾组越界。','Deploying a 32B quantized model on two H200 GPUs required integration across quantization backends, attention, KV cache and collectives, plus tail-group memory-safety fixes.'),
         work=('负责 W4A16 / W8A8 / FP8 后端适配，接入 FlashAttention-2/4、GQA、softcap 与 SDPA。使用 Compute Sanitizer 定位 gemv_kernel_g128 尾组越界并补充保护；实现 Qwen2 packed-AWQ TP=2 列 / 行切分及 NCCL all-reduce。','Adapted W4A16 / W8A8 / FP8 backends and integrated FlashAttention-2/4, GQA, softcap and SDPA. Used Compute Sanitizer to isolate gemv_kernel_g128 tail-group out-of-bounds accesses; added guards, packed-AWQ TP=2 column/row sharding and NCCL all-reduce.'),
         results=[('Qwen2.5-Coder-32B W4A16 checkpoint 体积','Qwen2.5-Coder-32B W4A16 checkpoint size','−70.5%'),('峰值显存','Peak GPU memory','−66.8%'),('端到端输出吞吐','End-to-end output throughput','+76.8%'),('代表 shape 的四类 Sanitizer 检查','Four sanitizer checks on representative shapes','0 error / 0 hazard')],
         delivery=('2025.12—至今。通过数值、跨 rank token 与交互验收，完成 H200 双卡部署验证。','December 2025–present. Passed numerical, cross-rank token and interactive acceptance checks for the two-H200 deployment.'),
         boundary=('百分比来自项目中 Qwen2.5-Coder-32B 的对照部署，基线、模型、量化和 batch 配置相关；不推广为所有模型或 FA4 后端的通用收益。','Percentages describe the project’s paired Qwen2.5-Coder-32B deployment comparison and depend on its baseline and configuration. They are not general gains for every model or attention backend.')),
    dict(slug='musa-extension',cat='framework',title=('TensorFlow MUSA Extension','TensorFlow MUSA Extension'),
         summary=('摩尔线程实习：算子与优化器适配、GELU 融合、性能分析和长跑稳定性。','Moore Threads internship: operators, optimizers, GELU fusion, profiling and long-run stability.'),evidence=('10 个 PR 已合入','10 merged PRs'),
         problem=('国产 GPU 后端需要同时对齐 TensorFlow 算子语义、HostMemory、资源变量及 Device Kernel 生命周期。','The GPU backend needed consistent TensorFlow operator semantics, HostMemory placement, resource variables and device-kernel lifetimes.'),
         work=('2026.01—2026.04，算子与编译器优化实习生。接入 muDNN 并修复 GELU 融合链路，优化 Logical_Or，补充 Adam / AdaMax / GradientDescent 实现或修复及测试。针对随机崩溃重构 HostMemory，修复资源变量更新和 Session 关闭问题。','January–April 2026, Operator and Compiler Optimization Intern. Integrated muDNN, repaired GELU fusion, optimized Logical_Or, and implemented or fixed Adam / AdaMax / GradientDescent paths and tests. Reworked HostMemory handling and fixed resource updates and session shutdown.'),
         results=[('整网 GELU 融合','GELU fusion coverage','11 / 11'),('真实 shape GELU 耗时','GELU latency on workload-shaped tests','−36.6%'),('Logical_Or 算子耗时','Logical_Or latency','21.2 μs → 10.7 μs'),('稳定性阶段验证','Staged stability validation','500 rounds ≈30% success → 1,000 rounds 100%'),('长跑轮数','Long-run validation rounds','40,000 / 400,000 / 800,000')],
         delivery=('公开 PR 作为实习产出的可核验记录，计入含实习贡献的总数，但不重复计算。','Public PRs provide verifiable internship outputs. They are included once in the internship-inclusive contribution total.'),
         boundary=('GELU 与 Logical_Or 数字是算子级结果，不等于整网吞吐提升。长跑结果反映所测环境和轮数，不表示无限期稳定。','GELU and Logical_Or numbers are operator-level results, not whole-model throughput gains. Long-run results describe the tested environment and duration, not indefinite stability.')),
]


def by_slug(slug: str) -> dict:
    return next(d for d in DETAILS if d['slug'] == slug)


def work_rows(details: list[dict], lang: str) -> str:
    result = []
    for n,d in enumerate(details,1):
        result.append(f'<a class="work-row" data-category="{d["cat"]}" href="{local("projects/"+d["slug"]+".html",lang)}"><span class="work-index">{n:02d}</span><span class="work-main"><strong>{esc(tx(d["title"],lang))}</strong><small>{esc(tx(d["summary"],lang))}</small></span><span class="work-evidence">{esc(tx(d["evidence"],lang))}</span><span class="work-arrow" aria-hidden="true">↗</span></a>')
    return '<div class="work-list">' + ''.join(result) + '</div>'


def pr_url(group: dict, item: dict) -> str:
    return f'https://github.com/{group["repo"]}/pull/{item["number"]}'


def pr_table(group: dict, lang: str) -> str:
    return table(['PR',tx(('已合入内容','Merged change'),lang),tx(('状态','Status'),lang)], [[link(pr_url(group,p),f'#{p["number"]} ↗'),esc(p[lang]),'Merged'] for p in group['prs']], 'oss-detail-table')


def oss_summary(lang: str) -> str:
    rows = []
    for g in GROUPS:
        category = tx(('实习期间','During internship'),lang) if g['category']=='internship' else tx(('社区贡献','Community'),lang)
        rows.append([ilink(g['page'],g['name'],lang),category,str(len(g['prs']))])
    return table([tx(('项目','Project'),lang),tx(('来源','Context'),lang),tx(('已合入','Merged'),lang)],rows,'oss-table') + f'<p class="section-note">{tx((f"{TOTAL} 个已合入 PR，覆盖 5 个 AI Infra 项目；含 {INTERNSHIP} 个摩尔线程实习 PR。状态核验：{SNAPSHOT}。",f"{TOTAL} merged PRs across five AI infrastructure projects, including {INTERNSHIP} from the Moore Threads internship. Verified {SNAPSHOT}."),lang)}</p>'


def education(lang: str) -> str:
    entries = [
        ('2025.09–2027.06',('香港中文大学（深圳）','The Chinese University of Hong Kong, Shenzhen'),('集成电路与系统 · 硕士在读，预计 2027.06 毕业','M.Sc. in Integrated Circuits and Systems · expected June 2027')),
        ('2021.09–2025.06',('山东大学','Shandong University'),('电子科学与技术 · 本科；计算机科学与技术 · 辅修','B.Eng. in Electronic Science and Technology · Minor in Computer Science and Technology'))]
    return '<div class="timeline-compact">' + ''.join(f'<div><time>{date}</time><strong>{esc(tx(name,lang))}</strong><span>{esc(tx(desc,lang))}</span></div>' for date,name,desc in entries) + '</div>'


def research_blurb(lang: str) -> str:
    return f'<div class="publication-state">{tx(("AAAI 2027 · 已投稿","AAAI 2027 · Submitted"),lang)}</div><div class="paper-title">{ilink("research.html",PAPER_TITLE,lang)}</div><p class="paper-meta">{tx(("共同作者；负责模型训练、超参调优与 vLLM TP=4 评测。","Co-author; model training, hyperparameter tuning and vLLM TP=4 evaluation."),lang)}</p>'


def home(lang: str) -> None:
    bio = tx(('港中深集成电路硕士在读，关注大模型系统与 GPU 性能工程。','M.Sc. candidate at CUHK-Shenzhen, focused on LLM systems and GPU performance.'),lang)
    hero = f'''<section class="editorial-hero"><div class="shell"><div class="editorial-hero-grid"><div class="hero-primary"><span class="eyebrow">AI Infrastructure</span><h1>Haoran Feng<span>冯浩然</span></h1></div><div class="hero-secondary"><p class="hero-statement">{bio}</p><dl class="hero-facts"><div><dt>Current</dt><dd>{tx(('至知创新研究院 · AI Infra 实习','IQuestLab · AI Infra Intern'),lang)}</dd></div><div><dt>Work</dt><dd>{ilink('projects/iquest-q1.html','IQuest-Q1 · '+tx(('训练、推理与 RL 基础设施','Training, inference & RL infrastructure'),lang),lang)}</dd></div></dl><div class="quick-links">{link('mailto:'+EMAIL,'Email',False)}{link(GITHUB,'GitHub ↗')}{ilink('resume.html',tx(('简历','Résumé'),lang),lang)}{ilink('research.html',tx(('研究','Research'),lang),lang)}</div></div></div><div class="context-line"><span><strong>IQuest-Q1</strong> · {tx(('参与已发布模型的基础设施开发','Infrastructure contributions to a released model'),lang)}</span><span><strong>{TOTAL} PRs</strong> · {tx(('含实习贡献','including internship work'),lang)}</span><span><strong>H200 / B200</strong> · {tx(('开发环境','development access'),lang)}</span></div></div></section>'''
    featured = dict(slug='iquest-q1',cat='model',title=('IQuest-Q1：训练、推理与 RL 基础设施','IQuest-Q1: training, inference and RL infrastructure'),summary=('参与 320B-A15B MoE 模型的算子优化、训推一致性与稳定性验证。','Contributed kernel optimization, training–rollout consistency and stability work to the 320B-A15B MoE model.'),evidence=('模型已发布 · 实习项目','Released model · internship'))
    content = hero + section(tx(('精选工作','Selected work'),lang),work_rows([featured,by_slug('fa3-deterministic-swa'),by_slug('deterministic-router-gemm'),by_slug('quant-runtime')],lang),ilink('projects.html',tx(('全部项目 →','All work →'),lang),lang))
    content += section(tx(('开源贡献','Open source'),lang),oss_summary(lang),ilink('opensource.html',tx(('PR 明细 →','PR record →'),lang),lang))
    content += '<section class="dense-section section-line"><div class="shell two-column-dense"><div><div class="dense-heading"><h2>' + tx(('教育','Education'),lang) + '</h2></div>'+education(lang)+'</div><div><div class="dense-heading"><h2>'+tx(('研究','Research'),lang)+'</h2></div>'+research_blurb(lang)+'</div></div></section>'
    content += section(tx(('技术分享','Writing'),lang),'<div class="profile-links">'+link(CSDN,'CSDN ↗')+link(ZHIHU,tx(('知乎 ↗','Zhihu ↗'),lang))+ilink('writing.html',tx(('技术文章索引 →','Technical notes →'),lang),lang)+'</div>')
    write_page('index.html','AI Infrastructure',bio,content,lang,'home')


def details(lang: str) -> None:
    for d in DETAILS:
        title, lead = tx(d['title'],lang),tx(d['summary'],lang)
        own = tx(('来源：本人 2026 年 9 月简历与工程记录摘要；以下为所述实验条件下的结果。','Source: the author’s September 2026 resume and engineering summary; results apply to the stated test conditions.'),lang)
        body = head(title,esc(lead),lang,d['cat']+' / Engineering', '<div class="quick-links">'+ilink('projects.html',tx(('项目索引','Project index'),lang),lang)+(ilink('projects/iquest-q1.html','IQuest-Q1',lang) if d['cat'] in ['training','inference','rl'] else '')+'</div>')
        body += section(tx(('问题与职责','Problem & contribution'),lang),para(esc(tx(d['problem'],lang)))+para(esc(tx(d['work'],lang))),reading=True)
        results = [[esc(zh if lang=='zh' else en),esc(value)] for zh,en,value in d['results']]
        body += section(tx(('验证结果','Validation'),lang),table([tx(('条件 / 指标','Condition / metric'),lang),tx(('结果','Result'),lang)],results)+para(esc(tx(d['delivery'],lang)))+f'<p class="source-note">{own}</p><p class="boundary-note">{esc(tx(d["boundary"],lang))}</p>',reading=True)
        if d['slug']=='musa-extension':
            body += section(tx(('实习期间的公开 PR','Public internship PRs'),lang),pr_table(GROUPS[1],lang),f'<span>{SNAPSHOT}</span>')
        if d['slug']=='flashinfer-ftz':
            body += section(tx(('另一个上游贡献','A separate upstream contribution'),lang),para(link('https://github.com/flashinfer-ai/flashinfer/pull/5171','#5171 ↗')+' · '+tx(('已安装包测试兼容性修复，已合入；不与本页的回移工作混为一项。','Installed-package test compatibility, merged; distinct from the backport on this page.'),lang)),reading=True)
        write_page('projects/'+d['slug']+'.html',title,lead,body,lang)


def iquest(lang: str) -> None:
    title = tx(('IQuest-Q1：模型基础设施','IQuest-Q1: model infrastructure'),lang)
    lead = tx(('参与 IQuest-Q1 的训练、推理与 RL rollout 基础设施开发，负责算子优化、训推一致性、稳定性排障与多卡验证。','Contributed to IQuest-Q1 training, inference and RL rollout infrastructure through kernel optimization, training–rollout consistency, stability debugging and multi-GPU validation.'),lang)
    links = '<div class="quick-links">'+link(MODEL,tx(('官方仓库 ↗','Official repository ↗'),lang))+link(HF,'Hugging Face ↗')+link(LAB,'IQuestLab ↗')+'</div>'
    body = head(title,esc(lead),lang,tx(('九坤投资—至知创新研究院 · 2026.04—至今','Ubiquant · IQuestLab · April 2026–present'),lang),links)
    spec = '<div class="summary-grid">' + ''.join(f'<div><strong>{a}</strong><span>{b}</span></div>' for a,b in [('320B / 15B',tx(('总参数 / 每 token 激活参数','Total / active parameters per token'),lang)),('88 layers',tx(('公开模型层数','Released model depth'),lang)),('512K',tx(('公开上下文长度','Released context length'),lang))]) + '</div>'
    source = tx(('官方将 IQuest-Q1 定位为面向 agentic coding、推理与多步工具使用的 MoE 模型，采用 3 SWA + 1 FA 的混合注意力。上面的模型规模属于团队发布成果。','The official release describes IQuest-Q1 as a MoE model for agentic coding, reasoning and multi-step tool use, with a 3 SWA + 1 FA attention pattern. These specifications describe the team’s released model.'),lang)
    body += section(tx(('团队发布','Team release'),lang),spec+para(esc(source))+f'<p class="source-note">{link(MODEL+"#model-specifications",tx(("公开规格来源：官方 README","Public specification source: official README"),lang))}</p>')
    columns=[(('训练算子','Training kernels'),('确定性 SWA backward；FC1 计算与通信竞争。','Deterministic SWA backward; FC1 compute–communication contention.')),(('推理 Runtime','Inference runtime'),('确定性 Router GEMM；异步 GPU token 状态。','Deterministic router GEMM; asynchronous GPU token state.')),(('RL 基础设施','RL infrastructure'),('Router Replay；多卡 rollout 与 CUDA Graph 稳定性。','Router Replay; multi-GPU rollout and CUDA Graph stability.'))]
    diagram='<div class="approach">'+''.join(f'<div><span class="mono">0{i}</span><h3>{tx(t,lang)}</h3><p>{tx(p,lang)}</p></div>' for i,(t,p) in enumerate(columns,1))+'</div>'
    body += section(tx(('我的工作范围','My contribution'),lang),diagram+work_rows(DETAILS[:6],lang))
    write_page('projects/iquest-q1.html',title,lead,body,lang)


def projects(lang: str) -> None:
    lead = tx(('模型基础设施、算子优化与推理 Runtime。先看负责的工作，再看实验条件。','Model infrastructure, GPU kernels and inference runtime. Contributions first, experimental context next.'),lang)
    body = head(tx(('工程项目','Engineering work'),lang),lead,lang,'Projects', '<div class="quick-links">'+ilink('projects/iquest-q1.html','IQuest-Q1',lang)+ilink('opensource.html',tx(('开源贡献','Open source'),lang),lang)+'</div>')
    body += section('IQuest-Q1 · '+tx(('实习工程','Internship engineering'),lang),para(ilink('projects/iquest-q1.html',tx(('模型已发布；查看个人参与范围 →','Released model; view my contribution →'),lang),lang))+work_rows(DETAILS[:6],lang))
    body += section(tx(('Runtime 与框架','Runtime & frameworks'),lang),work_rows(DETAILS[6:],lang))
    old=[('gemm-profiling','H200 Grouped GEMM',('工作量口径重建、shape replay 与调优。','Workload reconstruction, shape replay and tuning.')),('deepgemm-offline',tx(('DeepGEMM 离线交付','DeepGEMM offline delivery'),lang),('离线 cubin、完整性校验与部署。','Offline cubins, integrity checks and deployment.')),('drone-detection-pipeline',tx(('无人机检测实验流水线','Drone detection experiment pipeline'),lang),('数据工程、多 GPU 调度与训练恢复。','Data engineering, multi-GPU scheduling and training recovery.'))]
    rows=[[ilink('projects/'+slug+'.html',title,lang),esc(tx(desc,lang))] for slug,title,desc in old]
    body += section(tx(('其他工程记录','Other engineering records'),lang),table([tx(('项目','Project'),lang),tx(('内容','Focus'),lang)],rows))
    write_page('projects.html',tx(('项目','Work'),lang),lead,body,lang)


def experience_body(lang: str, resume: bool = False) -> str:
    title=tx(('实习经历','Experience'),lang)
    company=tx(('九坤投资—至知创新研究院','Ubiquant · IQuestLab'),lang)
    role=tx(('大模型与高性能计算实习生','LLM & High-Performance Computing Intern'),lang)
    text=tx(('参与已发布的 IQuest-Q1（320B-A15B）MoE 模型的训练、推理与 RL rollout 基础设施开发。','Contributed to training, inference and RL rollout infrastructure for the released IQuest-Q1 (320B-A15B) MoE model.'),lang)
    summaries=[
        ('fa3-deterministic-swa',('FA3 确定性 SWA backward','FA3 deterministic SWA backward'),('定位 dQ semaphore 依赖链，实现 contributor-relative ticket 并对齐 reverse scheduler；代表 packed shape 完整 backward 6.755 → 1.699 ms（3.98×），3,601 项回归与 1,000 次逐位确定性测试，交付 wheel。','Isolated dQ semaphore dependencies and aligned contributor-relative tickets with the reverse scheduler. Full backward on a representative packed shape: 6.755 → 1.699 ms (3.98×); 3,601 regressions and 1,000 bitwise checks; wheel delivered.')),
        ('fc1-communication',('FC1 计算与通信','FC1 compute–communication'),('4×H200 双 stream 代理，联合控制 NCCL CTA / DeepGEMM SM budget；121 组粗扫、89 组细扫与复验；AllGatherV 代理联合耗时 −12.80%，固定通信设置下控核贡献 7.58%。','Four-H200 dual-stream proxy with NCCL CTA / DeepGEMM SM budgeting; 121 coarse and 89 fine configurations plus rechecks. AllGatherV proxy joint latency −12.80%; isolated compute-budget contribution 7.58%.')),
        ('deterministic-router-gemm',('确定性 Router GEMM','Deterministic router GEMM'),('接入三级后端、Graph preflight、cache / fallback 与 workspace 管理；48 层测试工作负载中位耗时 −73.39%，135/135 kernel 与 20/20 模型场景逐位一致；prefix-cache hit 下 TP1 / TP2 整请求处理性能 +3.81% / +4.36%。','Three backends, Graph preflight, cache/fallback and workspace management. Median latency −73.39% in a 48-layer test workload; 135/135 kernel and 20/20 model cases bitwise-matching; full-request performance +3.81% / +4.36% at TP1 / TP2 with prefix-cache hits.')),
        ('oe-async',('OE 异步状态','OE asynchronous state'),('GPU token history 与 Triton fused-hash；TP1 28/28 case，吞吐 +4.99%；TP2 / TP4 安全路径各 84/84、0 mismatch，decode 吞吐 +4.6% / +3.0%。','GPU token history and Triton fused hashing. TP1: 28/28 cases, throughput +4.99%. TP2 / TP4 safe paths: 84/84 each, zero mismatch, decode throughput +4.6% / +3.0%.')),
        ('router-replay',('R3 Router Replay','R3 Router Replay'),('打通 vLLM / Megatron 路由采集、传输、回放与监控。8×H200、Qwen3-30B-A3B、20-step 对照：mismatch 17–19% → 0，fτ² / KL 降低 36–145× / 4–7×；另完成 128 卡、300B 级研发模型的 200-step rollout。','Connected vLLM / Megatron route capture, transport, replay and monitoring. Eight-H200, Qwen3-30B-A3B, 20-step control: mismatch 17–19% → 0, fτ² / KL lower by 36–145× / 4–7×. Separately completed a 200-step development rollout for a 300B-class model on 128 GPUs.')),
        ('flashinfer-ftz',('CUDA Graph 稳定性','CUDA Graph stability'),('两卡最小复现定位 Lamport sentinel 的 FTZ 误判，回移上游位级判断修复；模型级重复 Graph replay 未再观察到 hang / timeout。','A two-GPU reproducer isolated FTZ-sensitive Lamport sentinel handling. Backported the upstream bitwise fix; repeated model-level Graph replay showed no further hang or timeout.'))]
    items=[f'<strong>{ilink("projects/"+slug+".html",tx(t,lang),lang)}</strong> · {esc(tx(desc,lang))}' for slug,t,desc in summaries]
    body=f'<article class="exp-entry"><div class="exp-heading"><h3>{company}</h3><time>2026.04 — {tx(("至今","Present"),lang)}</time></div><p class="exp-role">{role}</p><p>{ilink("projects/iquest-q1.html","IQuest-Q1",lang)} · {esc(text)}</p>{bullets(items)}</article>'
    mt=tx(('摩尔线程','Moore Threads'),lang)
    mrole=tx(('算子与编译器优化实习生','Operator & Compiler Optimization Intern'),lang)
    musaitems=[tx(('接入 muDNN 与 GELU 图融合，整网 11/11 GELU 融合；真实 shape 算子耗时 −36.6%。Logical_Or 21.2 → 10.7 μs；补充 Adam / AdaMax / GradientDescent 实现或修复及测试。','Integrated muDNN and GELU fusion: 11/11 GELUs fused; operator latency −36.6% on workload-shaped tests. Logical_Or: 21.2 → 10.7 μs. Implemented or fixed Adam / AdaMax / GradientDescent and tests.'),lang),tx(('重构 HostMemory 并修复资源变量及 Session 生命周期；稳定性从 500 轮约 30% 成功率提升至 1,000 轮 100%，通过 4 万 / 40 万 / 80 万轮长跑验证。','Reworked HostMemory and resource/session lifetimes. Stability improved from approximately 30% success over 500-round runs to 100% over 1,000-round runs, followed by 40k / 400k / 800k-round validation.'),lang)]
    body+=f'<article class="exp-entry"><div class="exp-heading"><h3>{mt}</h3><time>2026.01 — 2026.04</time></div><p class="exp-role">{mrole}</p>{para(ilink("projects/musa-extension.html","TensorFlow MUSA Extension",lang))}{bullets(musaitems)}</article>'
    return section(title,body)


def experiences(lang: str) -> None:
    lead=tx(('从 GPU 后端到基础模型的训练与推理系统。','From GPU backends to training and inference systems for foundation models.'),lang)
    body=head(tx(('经历','Experience'),lang),lead,lang,'Education / Experience')
    body+=section(tx(('教育经历','Education'),lang),education(lang)+para(tx(('山东大学学业奖学金（前 20%）；特长奖学金（竞赛创新）。','Shandong University Academic Scholarship (top 20%) and Competition & Innovation Scholarship.'),lang)))
    body+=experience_body(lang)
    body+=section(tx(('研究','Research'),lang),research_blurb(lang))
    body+=section(tx(('公开工程记录','Public engineering record'),lang),oss_summary(lang),ilink('opensource.html',tx(('查看 PR →','View PRs →'),lang),lang))
    write_page('experience.html',tx(('经历','Experience'),lang),lead,body,lang,'experience')


def research(lang: str) -> str:
    authors='Shankui Han, Zhaoyu Li, Weiwen Yuan, Yuyuan Yang, <strong>Haoran Feng</strong>, Jinke Ren'
    personal=tx(('共同作者。负责模型训练、超参调优与 vLLM TP=4 评测，完成 LoRA / DPO 训练及对照评测。','Co-author. Responsible for model training, hyperparameter tuning and vLLM TP=4 evaluation, including LoRA / DPO training and controlled comparisons.'),lang)
    method=tx(('参与“结构恢复、关键 Token 加权监督、偏好优化”三阶段框架。通过逐 token 扰动教师推理后参考答案生成似然的下降量估计重要性，并将权重用于 SFT 与辅助损失。','Contributed to a three-stage framework of structure recovery, key-token-weighted supervision and preference optimization. Token importance is estimated by the drop in teacher likelihood of the reference answer after perturbing each rationale token, then used in weighted SFT and an auxiliary loss.'),lang)
    rows=[['Qwen2.5-7B-Instruct','94.01%','94.00%'],[tx(('较最强基线提升','Gain over strongest baseline'),lang),'+5.51 pp','+10.10 pp']]
    body=f'<div class="publication-state">AAAI 2027 · {tx(("已投稿","Submitted"),lang)}</div><h3>{esc(PAPER_TITLE)}</h3><p class="paper-authors">{authors}</p>'+para(personal)+para(method)+table(['Student / comparison','GSM8K','SVAMP'],rows)+f'<p class="source-note">{link(PAPER,"OpenReview ↗")} · {tx(("结果来自在投稿件；当前仅按已投稿展示，不表示已录用。","Results are reported in the submitted manuscript. Submission does not imply acceptance."),lang)}</p>'
    return body


def research_page(lang: str) -> None:
    lead=tx(('关键 Token 加权思维链蒸馏。','Token-weighted chain-of-thought distillation.'),lang)
    body=head(tx(('研究','Research'),lang),lead,lang,'CoT Distillation')+section(tx(('在投稿件','Submitted manuscript'),lang),research(lang),reading=True)
    write_page('research.html',tx(('研究','Research'),lang),lead,body,lang,'research')


def resume(lang: str) -> None:
    title=tx(('冯浩然','Haoran Feng'),lang)
    contacts='<div class="quick-links">'+link('mailto:'+EMAIL,EMAIL,False)+link(GITHUB,'GitHub: XFDG')+ilink('index.html',tx(('个人网站','Website'),lang),lang)+'</div>'
    body=head(title,tx(('大模型系统与 GPU 性能工程','LLM systems & GPU performance engineering'),lang),lang,'Résumé',contacts+'<p class="no-print"><button class="print-button" type="button" onclick="window.print()">'+tx(('打印 / 保存 PDF','Print / save PDF'),lang)+'</button></p>')
    body+=section(tx(('教育经历','Education'),lang),education(lang)+f'<p class="section-note">{tx(("山东大学学业奖学金（前 20%）、特长奖学金（竞赛创新）。","Shandong University Academic Scholarship (top 20%) and Competition & Innovation Scholarship."),lang)}</p>')
    body+=experience_body(lang,True)
    body+=section(tx(('开源贡献','Open source'),lang),oss_summary(lang),ilink('opensource.html',tx(('全部 PR 链接','All PR links'),lang),lang))
    q=by_slug('quant-runtime')
    items=[tx(q['work'],lang),tx(('Qwen2.5-Coder-32B W4A16 对照部署：checkpoint / 峰值显存 −70.5% / −66.8%，端到端输出吞吐 +76.8%；代表 shape 四类 Sanitizer 0 error / 0 hazard，通过数值、跨 rank token 与交互验收。','Paired Qwen2.5-Coder-32B W4A16 deployment: checkpoint / peak memory −70.5% / −66.8%; output throughput +76.8%. Four sanitizer checks on representative shapes showed zero errors/hazards; numerical, cross-rank token and interactive acceptance passed.'),lang)]
    body+=section(tx(('项目与科研','Projects & research'),lang),f'<div class="exp-heading"><h3>{ilink("projects/quant-runtime.html",tx(q["title"],lang),lang)}</h3><time>2025.12 — {tx(("至今","Present"),lang)}</time></div>'+bullets(items)+'<div style="margin-top:24px">'+research(lang)+'</div>')
    skills=tx(('C/C++、Python、CUDA、Triton、PyTorch Extension；Nsys、NCU、Compute Sanitizer；Attention、MoE、量化 GEMM、Tensor Parallel、CUDA Graph。','C/C++, Python, CUDA, Triton, PyTorch Extension; Nsys, NCU, Compute Sanitizer; attention, MoE, quantized GEMM, tensor parallelism and CUDA Graph.'),lang)
    body+=section(tx(('技能','Skills'),lang),para(skills)+f'<p class="section-note">IELTS 6.5 · CET-6 · HCIA-AI</p>')
    write_page('resume.html',tx(('公开简历','Résumé'),lang),tx(('冯浩然的公开简历','Haoran Feng’s public resume'),lang),body,lang,'resume')


def opensource(lang: str) -> None:
    title=tx(('开源贡献','Open source'),lang)
    lead=tx((f'{TOTAL} 个已合入 PR，覆盖 5 个 AI Infra 项目。社区贡献与实习期间的公开产出分别标注。',f'{TOTAL} merged PRs across five AI infrastructure projects, with community and internship contributions identified separately.'),lang)
    body=head(title,lead,lang,'Upstream contributions',f'<p class="section-note">{tx(("状态核验","Verified"),lang)}: {SNAPSHOT}</p>')
    body+=section(tx(('概览','Overview'),lang),oss_summary(lang))
    ids=['mooncake','musa','ray','flashinfer','mirage']
    for ident,g in zip(ids,GROUPS):
        label=tx(('实习期间 · 已合入','During internship · merged'),lang) if g['category']=='internship' else tx(('社区贡献 · 已合入','Community · merged'),lang)
        body+=section(g['name'],pr_table(g,lang),f'<span>{label} · {len(g["prs"])}</span>',ident)
    note=tx((f'统计包含 {COMMUNITY} 个社区 PR 与 {INTERNSHIP} 个实习 PR，均为本人向相应上游提交且 GitHub 标记为 merged 的记录。个人 fork 内合并、课程协作、Git 测试及其他文档协作未纳入本页的 AI Infra 统计。',f'This scoped total includes {COMMUNITY} community PRs and {INTERNSHIP} internship PRs authored by XFDG and marked merged upstream. Personal-fork merges, course collaboration, Git practice and other documentation collaboration are excluded from this AI infrastructure summary.'),lang)
    body+=section(tx(('统计口径','Counting scope'),lang),para(note)+para(link('https://github.com/kvcache-ai/Mooncake/pull/3661','Mooncake #3661 ↗')+' · '+tx(('仍为 Open；有界队列与失败传播工作不计入已合入的 7 个 Mooncake PR。','Still open; bounded-queue and failure-propagation work is not included in the seven merged Mooncake PRs.'),lang)),reading=True)
    write_page('opensource.html',title,lead,body,lang,'opensource')
    g=GROUPS[0]
    body=head('Mooncake',tx(('分布式 KV Cache 的存储、RDMA 与正确性修复。','Storage, RDMA and correctness fixes for a distributed KV cache.'),lang),lang,'Open source',f'<p class="section-note">7 merged · {SNAPSHOT}</p>')
    body+=section(tx(('已合入上游','Merged upstream'),lang),pr_table(g,lang))
    body+=section(tx(('持续跟进','Ongoing work'),lang),para(link('https://github.com/kvcache-ai/Mooncake/pull/3661','#3661 ↗')+' · '+esc(STATUS['tracked_open'][0][lang]))+f'<p class="boundary-note">{tx(("#3662 最终合入的是本地 MEMORY 优先级与副本排序修复，不是 SSD session 功能。#4016 是聚焦 Store 的 macOS 构建修复，不代表所有 RDMA / Transfer Engine 路径已在 macOS 上可用。","The final #3662 scope is local MEMORY preference and replica ordering, not SSD session functionality. #4016 is a focused macOS Store build fix, not macOS support for all RDMA / Transfer Engine paths."),lang)}</p>',reading=True)
    write_page('projects/mooncake-contributions.html','Mooncake',tx(('Mooncake 上游贡献','Mooncake upstream contributions'),lang),body,lang)
    g=GROUPS[-1]
    body=head('Mirage',tx(('Qwen3 示例中的 padding / Argmax 正确性修复。','Padding / Argmax correctness in Qwen3 demos.'),lang),lang,'Open source')+section(tx(('已合入记录','Merged record'),lang),pr_table(g,lang))
    body+=section(tx(('修改范围','Scope'),lang),para(tx(('PR #755 调整了 9 个示例脚本中 lm_head 超出真实词表部分的初始化，由 0 改为 −1e4。修改范围为示例脚本，不将其描述为通用 Argmax kernel 重写。','PR #755 changes the initialization of lm_head rows beyond the true vocabulary from 0 to −1e4 in nine demo scripts. The change is limited to demo scripts, not a rewrite of the general Argmax kernel.'),lang)),reading=True)
    write_page('projects/mirage-contribution.html','Mirage',tx(('Mirage 上游贡献','Mirage upstream contribution'),lang),body,lang)


def supporting(lang: str) -> None:
    channels='<div class="profile-links">'+link(CSDN,'CSDN ↗')+link(ZHIHU,tx(('知乎 ↗','Zhihu ↗'),lang))+link(GITHUB,'GitHub ↗')+'</div>'
    body=head(tx(('技术文章','Writing'),lang),tx(('工程记录、机制解释与研究笔记。','Engineering records, mechanisms and research notes.'),lang),lang,'Writing')
    body+=section(tx(('发布渠道','Publishing channels'),lang),channels+f'<p class="section-note">{tx(("以下为站内技术记录；外部文章请以 CSDN / 知乎实际发布内容为准。","The notes below are hosted on this site. External publication status follows the actual CSDN / Zhihu posts."),lang)}</p>')
    body+=section(tx(('技术记录','Engineering notes'),lang),work_rows([by_slug(s) for s in ['fa3-deterministic-swa','fc1-communication','deterministic-router-gemm','router-replay','quant-runtime']],lang))
    body+=section(tx(('研究','Research'),lang),research_blurb(lang))
    write_page('writing.html',tx(('文章','Writing'),lang),tx(('技术文章与工程记录','Technical writing and engineering notes'),lang),body,lang,'writing')
    body=head(tx(('现在与下一步','Now & next'),lang),tx(('把优化沉淀为可复现的工程结果。','Turn optimization work into reproducible engineering results.'),lang),lang,'Roadmap')
    body+=section('Now',bullets([tx(('IQuest-Q1 训练、推理与 RL 基础设施：整理已经验证的优化与边界。','IQuest-Q1 infrastructure: document validated training, inference and RL work with its scope.'),lang),tx(('维护上游贡献与回归测试；单独跟进尚未合入的 PR。','Maintain upstream contributions and regression tests; track open PRs separately.'),lang),tx(('具备 H200 / B200 开发环境，推进跨代适配与确定性验证。','Use available H200 / B200 development environments for cross-generation compatibility and determinism validation.'),lang)]))
    body+=section('Next',bullets([tx(('补充可公开的 workload、baseline 与复现实验配置，而不是只展示加速比。','Add public workloads, baselines and reproducible configurations, not just speedup figures.'),lang),tx(('在统一实验条件下比较 Hopper / Blackwell；未形成对照的数据不作跨代性能结论。','Compare Hopper and Blackwell under controlled conditions; do not infer cross-generation gains from unmatched runs.'),lang),tx(('继续量化 Runtime、CoT 蒸馏评测与技术写作。','Continue quantized runtime work, CoT distillation evaluation and technical writing.'),lang)]))
    write_page('roadmap.html','Now & next',tx(('当前工作与项目规划','Current work and plans'),lang),body,lang,'roadmap')
    body=head(tx(('联系','Contact'),lang),tx(('欢迎交流大模型系统、GPU 算子与工程实践。','Get in touch about LLM systems, GPU kernels and engineering.'),lang),lang,'Contact')
    body+=section(tx(('公开联系方式','Public profiles'),lang),f'<div class="contact-grid"><div><h3>Email</h3>{link("mailto:"+EMAIL,EMAIL,False)}<button class="copy-button" type="button" data-copy-email="{EMAIL}">{tx(("复制","Copy"),lang)}</button></div><div><h3>GitHub</h3>{link(GITHUB,"XFDG ↗")}</div><div><h3>CSDN</h3>{link(CSDN,"XFDG01 ↗")}</div><div><h3>{tx(("知乎","Zhihu"),lang)}</h3>{link(ZHIHU,tx(("个人主页 ↗","Profile ↗"),lang))}</div></div>')
    write_page('contact.html',tx(('联系','Contact'),lang),tx(('冯浩然的公开联系方式','Contact Haoran Feng'),lang),body,lang,'contact')


def sitemap() -> None:
    entries=[]
    for f in sorted(ROOT.rglob('*.html')):
        rel=f.relative_to(ROOT).as_posix()
        if rel.startswith(('.git/','tools/')) or f.name=='404.html':
            continue
        path=rel[3:] if rel.startswith('en/') else rel
        lang='en' if rel.startswith('en/') else 'zh'
        loc=BASE+local(path,lang)
        zh,en=BASE+local(path,'zh'),BASE+local(path,'en')
        alts=f'<xhtml:link rel="alternate" hreflang="zh-CN" href="{zh}"/><xhtml:link rel="alternate" hreflang="en" href="{en}"/>'
        entries.append(f'<url><loc>{loc}</loc>{alts}</url>')
    (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'+'\n'.join(entries)+'\n</urlset>\n',encoding='utf-8')


def main() -> None:
    assert TOTAL > 0 and COMMUNITY + INTERNSHIP == TOTAL
    assert len({(g['repo'],p['number']) for g in GROUPS for p in g['prs']})==TOTAL
    assert all(p['state']=='merged' for g in GROUPS for p in g['prs'])
    for lang in ['zh','en']:
        home(lang); projects(lang); iquest(lang); details(lang)
        experiences(lang); research_page(lang); resume(lang); opensource(lang); supporting(lang)
    sitemap()
    print(f'Built {len(BUILT)} bilingual pages; {TOTAL} verified, scoped upstream PRs.')


if __name__=='__main__':
    main()
