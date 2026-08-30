from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://xfdg.github.io/"
GITHUB = "https://github.com/XFDG"
CSDN = "https://blog.csdn.net/XFDG01"
ZHIHU = "https://www.zhihu.com/people/xian-feng-dao-gu-73-49"
MOONCAKE = "https://github.com/kvcache-ai/Mooncake"
SNAPSHOT = "2026-08-30"


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def nav(prefix: str = "") -> str:
    return f"""
<header class="site-header compact-header">
  <div class="shell header-inner">
    <a class="brand" href="{prefix}index.html" aria-label="返回首页">
      <span class="brand-mark">HF</span>
      <span class="brand-copy">Haoran Feng <small>AI Infra</small></span>
    </a>
    <button class="menu-toggle" type="button" aria-label="打开导航" aria-expanded="false"><span></span></button>
    <nav class="site-nav" aria-label="主导航">
      <a href="{prefix}index.html" data-nav="home">首页</a>
      <a href="{prefix}projects.html" data-nav="projects">项目</a>
      <a href="{prefix}experience.html" data-nav="experience">经历</a>
      <a href="{prefix}writing.html" data-nav="writing">文章</a>
      <a href="{prefix}contact.html" data-nav="contact">联系</a>
      <a class="nav-cta" href="{prefix}resume.html" data-nav="resume">简历</a>
    </nav>
  </div>
</header>
"""


def footer(prefix: str = "") -> str:
    return f"""
<footer class="site-footer compact-footer">
  <div class="shell footer-inner">
    <span>© <span data-year></span> Haoran Feng</span>
    <div class="footer-links">
      <a href="mailto:225010160@link.cuhk.edu.cn">Email</a>
      <a href="{GITHUB}" target="_blank" rel="noreferrer">GitHub</a>
      <a href="{CSDN}" target="_blank" rel="me noopener noreferrer">CSDN</a>
      <a href="{ZHIHU}" target="_blank" rel="me noopener noreferrer">知乎</a>
      <a href="{prefix}resume.html">Resume</a>
    </div>
  </div>
</footer>
"""


def page(title: str, description: str, page_name: str, body: str, prefix: str = "") -> str:
    canonical = SITE if page_name == "home" else f"{SITE}{'projects/mooncake-contributions.html' if page_name == 'mooncake' else page_name + '.html'}"
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{description}">
  <meta name="theme-color" content="#0b0d10">
  <link rel="canonical" href="{canonical}">
  <title>{title}</title>
  <link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{prefix}styles.css">
  <script src="{prefix}script.js" defer></script>
</head>
<body data-page="{'projects' if page_name == 'mooncake' else page_name}" class="compact-site">
{nav(prefix)}
{body}
{footer(prefix)}
</body>
</html>
"""


project_rows = [
    (
        "01",
        "OPEN SOURCE",
        "Mooncake：分布式 KV Cache / RDMA 稳定性贡献",
        "向 Mooncake Store 与 Transfer Engine 提交稳定性修复；当前公开记录包含 2 个已合并 PR 与多项审阅中修复。",
        "2 merged · 4 open",
        "projects/mooncake-contributions.html",
        "opensource systems inference",
    ),
    (
        "02",
        "GPU DEBUG",
        "FlashInfer CUDA Graph Hang：FTZ / Sentinel 根因",
        "从下游 timeout 反向定位 fused allreduce + RMSNorm 的 GPU 首因，并完成位级修复与 graph replay 回归。",
        "0/3→2/2 · SASS 8→0",
        "projects/flashinfer-ftz.html",
        "systems inference gpu",
    ),
    (
        "03",
        "RL INFRA",
        "R3 Router Replay：MoE 训推一致性",
        "贯通 token-layer-top-k 路由采集、observe/replay、response mask 与概率漂移指标。",
        "mismatch 17–19%→0",
        "projects/router-replay.html",
        "rl systems inference",
    ),
    (
        "04",
        "ASYNC OP",
        "OE Async：GPU Token History 与 Triton Fused Hash",
        "消除异步 decode 热路径中的 CPU 往返，并验证 mixed batch、恢复、slot reuse 与多卡状态。",
        "TP1 +5.0% · TP2/4 0 mismatch",
        "projects/oe-async.html",
        "systems inference gpu",
    ),
    (
        "05",
        "GPU PERF",
        "H200 MoE Grouped GEMM Profiling 与调优",
        "纠正 expanded / compact rows 口径，构造线上回放并扩展 SM90 候选配置。",
        "1,024 ranges · target +5.3%",
        "projects/gemm-profiling.html",
        "gpu inference",
    ),
    (
        "06",
        "DELIVERY",
        "DeepGEMM 离线 Cubin 与 Wheel 交付",
        "将运行时 JIT 产物转化为可校验 bundle，覆盖单卡与 TP=2 的 cold compile 清零验证。",
        "109→359 kernels · load 7.7×",
        "projects/deepgemm-offline.html",
        "systems inference gpu",
    ),
    (
        "07",
        "OPEN SOURCE",
        "TensorFlow MUSA Extension",
        "处理算子、Fusion、HostMemory、长跑稳定性与 Kernel Timing，并保留公开合入记录。",
        "PR #57 merged · 11/11 fused",
        "projects/musa-extension.html",
        "opensource heterogeneous gpu systems",
    ),
    (
        "08",
        "RUNTIME",
        "LLMQRT 量化推理 Runtime",
        "贯通 W4A16、W8A8、FP8、Attention 后端、KV Cache 与 H200 kernel 适配。",
        "AWQ · INT8 · FP8",
        "projects/quant-runtime.html",
        "systems inference gpu",
    ),
    (
        "09",
        "ML SYSTEMS",
        "ICS6201 无人机检测实验流水线",
        "统一 171K 样本、六模型实验设计、多 GPU 调度与恢复验证，并区分完整设计与已完成核心任务。",
        "171,568 samples · 14/14 smoke",
        "projects/drone-detection-pipeline.html",
        "ml systems",
    ),
]


def render_work_row(row: tuple[str, str, str, str, str, str, str], filterable: bool = False) -> str:
    number, badge, title, desc, evidence, href, categories = row
    extra = f' filter-item" data-category="{categories}' if filterable else ""
    return f"""
<a class="work-row{extra}" href="{href}">
  <span class="work-index">{number}</span>
  <span class="work-main"><strong>{title}</strong><small>{desc}</small></span>
  <span class="work-evidence">{evidence}</span>
  <span class="work-badge">{badge}</span>
  <span class="work-arrow">↗</span>
</a>
"""


index_body = f"""
<main>
  <section class="compact-hero">
    <div class="shell">
      <div class="identity-line">
        <div>
          <span class="eyebrow">AI Infrastructure · LLM Systems · GPU Performance</span>
          <h1>冯浩然 <span>Haoran Feng</span></h1>
          <p>香港中文大学（深圳）集成电路与系统硕士在读。关注大模型训练推理、RL Infra、GPU Kernel、分布式存储与性能工程。</p>
        </div>
        <div class="quick-links" aria-label="快捷链接">
          <a href="mailto:225010160@link.cuhk.edu.cn">Email</a>
          <a href="{GITHUB}" target="_blank" rel="noreferrer">GitHub ↗</a>
          <a href="resume.html">Resume</a>
        </div>
      </div>
      <div class="metric-strip">
        <div><strong>2</strong><span>Mooncake merged PRs</span></div>
        <div><strong>8×H200</strong><span>MoE-RL 主实验</span></div>
        <div><strong>1,024</strong><span>GEMM ranges</span></div>
        <div><strong>2027</strong><span>Expected graduation</span></div>
      </div>
    </div>
  </section>

  <section class="dense-section">
    <div class="shell">
      <div class="dense-heading"><h2>Latest open-source activity</h2><span>Snapshot · {SNAPSHOT}</span></div>
      <a class="activity-row" href="projects/mooncake-contributions.html">
        <div class="activity-title"><strong>Mooncake</strong><span>Distributed KV Cache · Store · RDMA Transfer Engine</span></div>
        <p>已合并两项 Transfer Engine 稳定性修复：恢复 RDMA Memory Region 的 Fork State，避免 VMA 耗尽；在端口恢复时淘汰失效 Endpoint / QP，使连接重新建立。</p>
        <div class="activity-meta"><span>2 merged</span><span>4 under review</span><span>View evidence ↗</span></div>
      </a>
    </div>
  </section>

  <section class="dense-section section-line" id="selected-work">
    <div class="shell">
      <div class="dense-heading"><h2>Selected work</h2><a href="projects.html">All projects →</a></div>
      <div class="work-list">
        {''.join(render_work_row(row) for row in project_rows[:7])}
      </div>
    </div>
  </section>

  <section class="dense-section section-line">
    <div class="shell two-column-dense">
      <div>
        <div class="dense-heading"><h2>Experience</h2><a href="experience.html">Details →</a></div>
        <div class="timeline-compact">
          <div><time>2026.04 — Present</time><strong>大模型系统与高性能计算</strong><span>MoE-RL · CUDA Graph · OE Async · H200 GEMM</span></div>
          <div><time>2026.02 — 2026.05</time><strong>TensorFlow MUSA Extension</strong><span>Framework backend · Fusion · Kernel debugging</span></div>
          <div><time>2024.08 — 2024.12</time><strong>大型 C/C++ 软件工程</strong><span>Static analysis · Automation · CI</span></div>
        </div>
      </div>
      <div>
        <div class="dense-heading"><h2>Open source</h2><span>Accepted contributions</span></div>
        <div class="os-list">
          <a href="projects/mooncake-contributions.html"><strong>Mooncake</strong><span>2 merged bugfix PRs in RDMA lifecycle and recovery</span><b>↗</b></a>
          <a href="projects/musa-extension.html"><strong>TensorFlow MUSA</strong><span>Kernel timing and framework-backend contribution</span><b>↗</b></a>
        </div>
      </div>
    </div>
  </section>

  <section class="dense-section section-line">
    <div class="shell">
      <div class="dense-heading"><h2>Writing & profiles</h2><a href="writing.html">Writing index →</a></div>
      <div class="profile-links">
        <a href="{CSDN}" target="_blank" rel="me noopener noreferrer"><strong>CSDN</strong><span>工程教程、Benchmark 与排障复盘</span></a>
        <a href="{ZHIHU}" target="_blank" rel="me noopener noreferrer"><strong>知乎</strong><span>机制解释、技术比较与观点讨论</span></a>
        <a href="{GITHUB}" target="_blank" rel="noreferrer"><strong>GitHub</strong><span>代码、PR 与公开工程证据</span></a>
      </div>
    </div>
  </section>
</main>
"""
write(
    "index.html",
    page(
        "Haoran Feng — AI Infra",
        "冯浩然的高信息密度 AI Infra 个人主页：LLM 系统、GPU 性能、开源贡献与项目证据。",
        "home",
        index_body,
    ),
)


project_buttons = [
    ("all", "ALL"),
    ("opensource", "OPEN SOURCE"),
    ("systems", "SYSTEMS"),
    ("rl", "RL INFRA"),
    ("inference", "INFERENCE"),
    ("gpu", "GPU PERF"),
    ("heterogeneous", "HETEROGENEOUS"),
    ("ml", "ML PIPELINE"),
]
projects_body = f"""
<main>
  <section class="compact-page-head">
    <div class="shell">
      <span class="eyebrow">Projects / Evidence</span>
      <div class="page-title-line"><h1>项目与公开证据</h1><p>按问题、方法、结果和结论边界组织，不用大卡片堆技术名词。</p></div>
    </div>
  </section>
  <section class="dense-section section-line">
    <div class="shell">
      <div class="filter-bar compact-filters">
        {''.join(f'<button class="filter-button{" active" if value == "all" else ""}" type="button" data-filter="{value}">{label}</button>' for value, label in project_buttons)}
      </div>
      <div class="work-list project-index-list">
        {''.join(render_work_row(row, True) for row in project_rows)}
      </div>
      <p class="index-note">企业项目仅展示脱敏后的方法、聚合结果与公开边界；开源贡献以 GitHub PR 状态为准。</p>
    </div>
  </section>
</main>
"""
write(
    "projects.html",
    page(
        "项目 — Haoran Feng",
        "冯浩然的 AI Infra、Mooncake、RL Infra、GPU 性能与异构计算项目索引。",
        "projects",
        projects_body,
    ),
)


mooncake_body = f"""
<main>
  <section class="compact-page-head">
    <div class="shell">
      <div class="detail-breadcrumbs"><a href="../projects.html">Projects</a><span>/</span><span>Mooncake</span></div>
      <span class="eyebrow">Open Source · Distributed KV Cache · RDMA</span>
      <div class="page-title-line"><h1>Mooncake 开源贡献</h1><p>围绕 Mooncake Store 与 Transfer Engine 的稳定性、资源生命周期和故障恢复提交修复。</p></div>
      <div class="metric-strip detail-strip">
        <div><strong>2</strong><span>Merged PRs</span></div>
        <div><strong>4</strong><span>Open PRs</span></div>
        <div><strong>Store + TE</strong><span>主要模块</span></div>
        <div><strong>{SNAPSHOT}</strong><span>状态快照</span></div>
      </div>
    </div>
  </section>

  <section class="dense-section section-line">
    <div class="shell detail-narrow">
      <div class="dense-heading"><h2>已合并贡献</h2><a href="{MOONCAKE}" target="_blank" rel="noreferrer">Upstream repository ↗</a></div>
      <div class="contribution-table-wrap">
        <table class="compact-table">
          <thead><tr><th>PR</th><th>问题</th><th>修复</th><th>状态</th></tr></thead>
          <tbody>
            <tr>
              <td><a href="https://github.com/kvcache-ai/Mooncake/pull/3660" target="_blank" rel="noreferrer">#3660 ↗</a></td>
              <td>RDMA Memory Region 注销后未恢复 Fork State，持续切分 VMA；高频注册/注销下可能耗尽 <code>vm.max_map_count</code>。</td>
              <td>在 <code>ibv_dereg_mr</code> 成功后对原地址范围调用 <code>MADV_DOFORK</code>，并处理 Deregister 后访问 MR 的生命周期问题。</td>
              <td><span class="status merged">MERGED</span><small>2026-08-26</small></td>
            </tr>
            <tr>
              <td><a href="https://github.com/kvcache-ai/Mooncake/pull/3604" target="_blank" rel="noreferrer">#3604 ↗</a></td>
              <td>RDMA 端口恢复后，Endpoint Store 仍返回已进入 Error 状态的旧 QP，导致恢复后传输持续超时。</td>
              <td>在端口恢复时淘汰 FIFO / SIEVE Store 中的全部失效 Endpoint，使后续请求创建新的 QP。</td>
              <td><span class="status merged">MERGED</span><small>2026-08-27</small></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <section class="dense-section section-line">
    <div class="shell detail-narrow">
      <div class="dense-heading"><h2>审阅中的修复</h2><span>状态可能随上游审阅变化</span></div>
      <div class="issue-list">
        <a href="https://github.com/kvcache-ai/Mooncake/pull/3726" target="_blank" rel="noreferrer"><strong>#3726</strong><span>修复 Offloading Queue “未入队却返回成功”导致的幽灵任务与引用计数泄漏</span><b>OPEN</b></a>
        <a href="https://github.com/kvcache-ai/Mooncake/pull/3661" target="_blank" rel="noreferrer"><strong>#3661</strong><span>为有界 MPSC Queue 增加非阻塞提交，避免 Retry Path 在满队列下永久活锁</span><b>OPEN</b></a>
        <a href="https://github.com/kvcache-ai/Mooncake/pull/3662" target="_blank" rel="noreferrer"><strong>#3662</strong><span>Batch Get Session 使用 Best Replica，支持仅存在于 SSD 的副本</span><b>OPEN</b></a>
        <a href="https://github.com/kvcache-ai/Mooncake/pull/3601" target="_blank" rel="noreferrer"><strong>#3601</strong><span>在提交 Bucket Metadata 前 Flush 数据，恢复 Write-ordering Durability</span><b>OPEN</b></a>
      </div>
    </div>
  </section>

  <section class="dense-section section-line">
    <div class="shell detail-narrow two-column-dense">
      <div>
        <div class="dense-heading"><h2>体现的工程能力</h2></div>
        <ul class="compact-list">
          <li>从 Issue、调用链和资源生命周期中定位分布式系统故障，而不是只修补表层报错。</li>
          <li>覆盖 C++ 并发、RDMA Verbs、QP / MR 生命周期、存储持久性与异步任务状态。</li>
          <li>根据 Review 反馈补充锁粒度、Use-after-free 与失败语义等边界，再完成合入。</li>
        </ul>
      </div>
      <div>
        <div class="dense-heading"><h2>表述边界</h2></div>
        <p class="boundary-note">“为 Mooncake 做开源贡献”是准确表述；已合并部分可写为 Accepted / Merged Contributions。审阅中的 PR 只写 Submitted / Under Review，不作为已经进入上游的交付成果。</p>
      </div>
    </div>
  </section>
</main>
"""
write(
    "projects/mooncake-contributions.html",
    page(
        "Mooncake 开源贡献 — Haoran Feng",
        "冯浩然向 Mooncake 分布式 KV Cache 项目提交的 RDMA 与 Store 稳定性修复。",
        "mooncake",
        mooncake_body,
        "../",
    ),
)


def insert_open_source_experience() -> None:
    path = ROOT / "experience.html"
    if not path.exists():
        return
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    old = soup.find(id="open-source-contributions")
    if old:
        old.decompose()
    block = BeautifulSoup(
        f"""
<section class="section section-line dense-section" id="open-source-contributions">
  <div class="shell">
    <div class="section-head"><div><span class="section-kicker">Open Source / 开源贡献</span><h2>从内部工程走向公开协作。</h2></div><p>只将 GitHub 已公开、可复核的提交列为开源贡献。</p></div>
    <div class="os-list os-list-wide">
      <a href="projects/mooncake-contributions.html"><strong>Mooncake</strong><span>2 个已合并 bugfix PR：RDMA Memory Region Fork State 与端口恢复后的 Endpoint / QP 重建；另有 Store / TENT 修复处于审阅中。</span><b>View ↗</b></a>
      <a href="projects/musa-extension.html"><strong>TensorFlow MUSA Extension</strong><span>参与国产 GPU TensorFlow 后端、算子、Fusion、稳定性与 Kernel Timing，公开 PR #57 已合入。</span><b>View ↗</b></a>
    </div>
  </div>
</section>
""",
        "html.parser",
    ).section
    main = soup.find("main")
    sections = main.find_all("section", recursive=False) if main else []
    if sections:
        sections[-1].insert_before(block)
    if soup.body:
        classes = list(soup.body.get("class", []))
        if "compact-site" not in classes:
            classes.append("compact-site")
        soup.body["class"] = classes
    path.write_text(str(soup), encoding="utf-8")


def insert_open_source_resume() -> None:
    path = ROOT / "resume.html"
    if not path.exists():
        return
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    old = soup.find(id="resume-open-source")
    if old:
        old.decompose()
    section = BeautifulSoup(
        """
<section class="resume-section" id="resume-open-source">
  <h2>Open Source</h2>
  <div class="resume-entry">
    <div class="resume-entry-head"><div><h3>Mooncake Contributor</h3><span class="sub">Distributed KV Cache · RDMA · Storage</span></div><span class="date">2026.08</span></div>
    <ul><li>向 Mooncake 提交 Transfer Engine / Store 稳定性修复；其中 2 个 PR 已合并，覆盖 RDMA Memory Region 的 Fork State 恢复及端口恢复后的失效 Endpoint / QP 重建。</li></ul>
  </div>
  <div class="resume-entry">
    <div class="resume-entry-head"><div><h3>TensorFlow MUSA Extension Contributor</h3><span class="sub">Framework Backend · Kernel Debugging</span></div><span class="date">2026</span></div>
    <ul><li>参与算子、Fusion、稳定性与 Kernel Timing，公开 PR #57 已合入。</li></ul>
  </div>
</section>
""",
        "html.parser",
    ).section
    target = None
    for h2 in soup.find_all("h2"):
        if "Selected Projects" in h2.get_text(" ", strip=True):
            target = h2.find_parent("section")
            break
    if target:
        target.insert_before(section)
    elif soup.select_one(".resume-sheet"):
        soup.select_one(".resume-sheet").append(section)
    if soup.body:
        classes = list(soup.body.get("class", []))
        if "compact-site" not in classes:
            classes.append("compact-site")
        soup.body["class"] = classes
    path.write_text(str(soup), encoding="utf-8")


insert_open_source_experience()
insert_open_source_resume()

# Apply the compact visual system to every existing page without rewriting its content.
for html_path in ROOT.rglob("*.html"):
    text = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(text, "html.parser")
    if soup.body:
        classes = list(soup.body.get("class", []))
        if "compact-site" not in classes:
            classes.append("compact-site")
        soup.body["class"] = classes
    html_path.write_text(str(soup), encoding="utf-8")

css_path = ROOT / "styles.css"
css = css_path.read_text(encoding="utf-8")
marker = "/* COMPACT-REDESIGN-2026 */"
if marker in css:
    css = css.split(marker, 1)[0].rstrip() + "\n\n"
css += marker + r"""

/* A restrained, high-information-density visual system. */
body.compact-site{background:#0b0d10;color:#e7e9ec;font-size:15px;line-height:1.65}
body.compact-site::before,body.compact-site::after{display:none!important}
.compact-site .shell{width:min(1160px,calc(100% - 32px))}
.compact-site .site-header{background:rgba(11,13,16,.94);border-bottom:1px solid #24282f;backdrop-filter:none}
.compact-site .header-inner{min-height:56px}
.compact-site .brand-mark{width:30px;height:30px;border-radius:6px;background:#e7e9ec;color:#0b0d10;box-shadow:none;font-size:.78rem}
.compact-site .brand-copy{font-size:.9rem}.compact-site .brand-copy small{font-size:.65rem;color:#7f8792}
.compact-site .site-nav{gap:4px}.compact-site .site-nav a{padding:7px 9px;font-size:.8rem;color:#9da4ae;border-radius:5px}
.compact-site .site-nav a:hover,.compact-site .site-nav a.active{background:#171a20;color:#fff}
.compact-site .nav-cta{border:1px solid #343a44!important;background:transparent!important;color:#e7e9ec!important}
.compact-site .gradient-text{background:none!important;color:inherit!important;-webkit-text-fill-color:currentColor!important}
.compact-site .reveal{opacity:1!important;transform:none!important;transition:none!important}
.compact-site .terminal{display:none!important}
.compact-site .hero,.compact-site .page-hero,.compact-site .detail-hero{padding:52px 0 28px}
.compact-site .hero-grid,.compact-site .page-hero-grid{grid-template-columns:1fr;gap:20px}
.compact-site .hero h1,.compact-site .page-hero h1,.compact-site .detail-hero h1{font-size:clamp(2rem,4.6vw,3.4rem);line-height:1.08;letter-spacing:-.04em;max-width:900px}
.compact-site .hero-lead,.compact-site .page-lead,.compact-site .detail-lead{font-size:1rem;max-width:820px;color:#aeb4bd}
.compact-site .section{padding:38px 0}.compact-site .section.compact{padding:24px 0}
.compact-site .section-head,.compact-site .section-title-row{margin-bottom:22px}
.compact-site .section-head h2,.compact-site .section-title-row h2,.compact-site .detail-content h2{font-size:clamp(1.35rem,2.5vw,1.85rem);letter-spacing:-.02em}
.compact-site .card{background:transparent;border:1px solid #292e36;border-radius:8px;box-shadow:none;padding:18px}
.compact-site .card:hover{border-color:#555e6b;transform:none;background:#11151a}
.compact-site .card-grid{gap:12px}
.compact-site .project-evidence{gap:6px;margin-top:14px}.compact-site .evidence-chip{border-radius:5px;padding:8px 10px;background:#11151a;border-color:#292e36}
.compact-site .button{border-radius:5px;padding:9px 13px;box-shadow:none}.compact-site .button.primary{background:#e7e9ec;color:#0b0d10;border-color:#e7e9ec}
.compact-site .badge{border-radius:4px;font-size:.62rem;letter-spacing:.08em}
.compact-site .tag{border-radius:4px;padding:5px 8px}
.compact-site .detail-layout{grid-template-columns:minmax(0,1fr) 230px;gap:34px}
.compact-site .detail-content section{margin-bottom:34px}.compact-site .detail-sidebar{top:76px}
.compact-site .project-figure{border-radius:8px;padding:8px;background:#0f1216}.compact-site .project-figure img{border-radius:4px}
.compact-site .source-banner{border-radius:8px;padding:20px;background:#10141a}
.compact-site .data-table,.compact-site .compact-table{font-size:.86rem}
.compact-site .data-table th,.compact-site .data-table td,.compact-site .compact-table th,.compact-site .compact-table td{padding:10px 12px}
.compact-site .site-footer{padding:24px 0;border-top:1px solid #24282f}

.compact-hero{padding:68px 0 30px;border-bottom:1px solid #24282f}
.identity-line{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:32px;align-items:end}
.identity-line h1{margin:8px 0 10px;font-size:clamp(2.25rem,5vw,3.8rem);line-height:1;letter-spacing:-.055em}.identity-line h1 span{display:block;margin-top:8px;color:#7f8792;font-size:.42em;font-weight:500;letter-spacing:.01em}
.identity-line p{max-width:760px;margin:0;color:#aeb4bd;font-size:1rem}
.quick-links{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}.quick-links a{padding:7px 10px;border:1px solid #303640;border-radius:5px;color:#cbd0d7;font-size:.8rem}.quick-links a:hover{border-color:#697383;color:#fff}
.metric-strip{display:grid;grid-template-columns:repeat(4,1fr);margin-top:28px;border-top:1px solid #24282f;border-bottom:1px solid #24282f}
.metric-strip>div{padding:15px 18px;border-right:1px solid #24282f}.metric-strip>div:last-child{border-right:0}.metric-strip strong{display:block;font-size:1.15rem}.metric-strip span{color:#7f8792;font-size:.75rem}
.dense-section{padding:30px 0}.dense-heading{display:flex;align-items:baseline;justify-content:space-between;gap:16px;margin-bottom:14px}.dense-heading h2{margin:0;font-size:1.05rem;letter-spacing:0}.dense-heading>a,.dense-heading>span{color:#7f8792;font-size:.75rem}
.activity-row{display:grid;grid-template-columns:210px minmax(0,1fr) auto;gap:22px;align-items:center;padding:18px 0;border-top:1px solid #24282f;border-bottom:1px solid #24282f;color:inherit}.activity-row:hover{background:#0f1216}.activity-title strong{display:block;font-size:1.15rem}.activity-title span{display:block;color:#7f8792;font-size:.72rem}.activity-row p{margin:0;color:#aeb4bd}.activity-meta{display:flex;flex-direction:column;align-items:flex-end;gap:4px;color:#aeb4bd;font-size:.72rem}
.work-list{border-top:1px solid #2a2f37}.work-row{display:grid;grid-template-columns:38px minmax(0,1fr) 210px 92px 18px;gap:14px;align-items:center;padding:15px 8px;border-bottom:1px solid #24282f;color:inherit}.work-row:hover{background:#101318}.work-index{font-family:var(--mono);color:#68707b;font-size:.72rem}.work-main strong{display:block;font-size:.93rem}.work-main small{display:block;margin-top:3px;color:#8f97a2;line-height:1.45}.work-evidence{font-family:var(--mono);color:#bbc1c9;font-size:.72rem;text-align:right}.work-badge{color:#727b87;font-size:.62rem;letter-spacing:.08em;text-align:right}.work-arrow{color:#69717c}
.compact-page-head{padding:58px 0 24px}.page-title-line{display:grid;grid-template-columns:minmax(0,1fr) 430px;gap:30px;align-items:end}.page-title-line h1{margin:7px 0 0;font-size:clamp(2rem,4.8vw,3.25rem);letter-spacing:-.045em}.page-title-line p{margin:0;color:#9ca3ad}
.compact-filters{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}.compact-filters .filter-button{padding:6px 9px;border-radius:4px;font-size:.65rem;background:transparent;border:1px solid #2c323b}.compact-filters .filter-button.active{background:#e7e9ec;color:#0b0d10;border-color:#e7e9ec}
.index-note{margin:18px 0 0;color:#747c87;font-size:.75rem}
.two-column-dense{display:grid;grid-template-columns:1.15fr .85fr;gap:48px}
.timeline-compact{border-top:1px solid #2a2f37}.timeline-compact>div{display:grid;grid-template-columns:140px minmax(0,1fr);gap:4px 16px;padding:13px 0;border-bottom:1px solid #24282f}.timeline-compact time{grid-row:1/3;color:#747c87;font-family:var(--mono);font-size:.7rem}.timeline-compact strong{font-size:.9rem}.timeline-compact span{color:#89919c;font-size:.75rem}
.os-list{border-top:1px solid #2a2f37}.os-list a{display:grid;grid-template-columns:145px minmax(0,1fr) 20px;gap:12px;padding:14px 0;border-bottom:1px solid #24282f;color:inherit}.os-list a:hover{background:#101318}.os-list strong{font-size:.9rem}.os-list span{color:#89919c;font-size:.76rem}.os-list b{font-weight:400;color:#69717c}.os-list-wide a{grid-template-columns:200px minmax(0,1fr) 70px}
.profile-links{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid #2a2f37}.profile-links a{padding:14px 16px;border-right:1px solid #24282f;border-bottom:1px solid #24282f;color:inherit}.profile-links a:last-child{border-right:0}.profile-links strong{display:block}.profile-links span{display:block;color:#89919c;font-size:.75rem;margin-top:3px}
.detail-narrow{max-width:1000px}.detail-strip{margin-top:22px}.contribution-table-wrap{overflow-x:auto}.compact-table{width:100%;border-collapse:collapse;border-top:1px solid #2a2f37}.compact-table th,.compact-table td{border-bottom:1px solid #24282f;text-align:left;vertical-align:top}.compact-table th{color:#7f8792;font-size:.68rem;letter-spacing:.06em}.compact-table td:first-child{white-space:nowrap}.compact-table code{font-family:var(--mono);font-size:.82em}.status{display:inline-block;font-size:.64rem;letter-spacing:.08em}.status.merged{color:#7fd5b5}.compact-table td small{display:block;color:#747c87;margin-top:3px}
.issue-list{border-top:1px solid #2a2f37}.issue-list a{display:grid;grid-template-columns:72px minmax(0,1fr) 58px;gap:12px;padding:12px 0;border-bottom:1px solid #24282f;color:inherit}.issue-list strong{font-family:var(--mono);font-size:.78rem}.issue-list span{color:#9ca3ad}.issue-list b{font-size:.62rem;letter-spacing:.08em;color:#d1b26f;text-align:right}
.compact-list{margin:0;padding-left:18px}.compact-list li{margin:8px 0;color:#aeb4bd}.boundary-note{margin:0;padding:16px;border-left:2px solid #737c88;background:#101318;color:#aeb4bd}

@media(max-width:900px){
  .identity-line,.page-title-line,.two-column-dense{grid-template-columns:1fr}
  .quick-links{justify-content:flex-start}
  .metric-strip{grid-template-columns:repeat(2,1fr)}.metric-strip>div:nth-child(2){border-right:0}.metric-strip>div:nth-child(-n+2){border-bottom:1px solid #24282f}
  .activity-row{grid-template-columns:1fr}.activity-meta{align-items:flex-start;flex-direction:row;flex-wrap:wrap}
  .work-row{grid-template-columns:30px minmax(0,1fr) 18px}.work-evidence,.work-badge{grid-column:2;text-align:left}.work-arrow{grid-column:3;grid-row:1/4}
  .profile-links{grid-template-columns:1fr}.profile-links a{border-right:0}
  .compact-site .detail-layout{grid-template-columns:1fr}.compact-site .detail-sidebar{position:static}
}
@media(max-width:620px){
  .compact-site .shell{width:min(100% - 24px,1160px)}
  .compact-hero{padding-top:48px}.identity-line h1{font-size:2.25rem}
  .metric-strip{grid-template-columns:1fr}.metric-strip>div{border-right:0!important;border-bottom:1px solid #24282f}.metric-strip>div:last-child{border-bottom:0}
  .work-row{padding:13px 2px}.work-main small{display:none}.work-evidence{font-size:.66rem}
  .os-list a,.os-list-wide a{grid-template-columns:1fr 20px}.os-list span{grid-column:1}.os-list b{grid-column:2;grid-row:1/3}
  .compact-table{min-width:760px}.issue-list a{grid-template-columns:62px minmax(0,1fr)}.issue-list b{grid-column:2;text-align:left}
}
"""
css_path.write_text(css, encoding="utf-8")

# Keep the new project discoverable.
sitemap_path = ROOT / "sitemap.xml"
if sitemap_path.exists():
    text = sitemap_path.read_text(encoding="utf-8")
    url = f"{SITE}projects/mooncake-contributions.html"
    if url not in text:
        text = text.replace("</urlset>", f"  <url><loc>{url}</loc></url>\n</urlset>")
        sitemap_path.write_text(text, encoding="utf-8")

# Lightweight local validation.
required = [
    "index.html",
    "projects.html",
    "projects/mooncake-contributions.html",
    "experience.html",
    "resume.html",
    "styles.css",
]
for rel in required:
    assert (ROOT / rel).exists(), rel

for rel in ["index.html", "projects.html", "projects/mooncake-contributions.html"]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    assert "Mooncake" in text
    assert "compact-site" in text

mooncake_text = (ROOT / "projects/mooncake-contributions.html").read_text(encoding="utf-8")
assert "#3660" in mooncake_text and "#3604" in mooncake_text
assert "MERGED" in mooncake_text
assert "审阅中的修复" in mooncake_text

missing: list[str] = []
for html_path in ROOT.rglob("*.html"):
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    for node in soup.find_all(["a", "img", "script", "link"]):
        target = node.get("href") or node.get("src")
        if not target or target.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
            continue
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        candidate = (html_path.parent / parsed.path).resolve()
        if parsed.path.endswith("/"):
            candidate /= "index.html"
        if not candidate.exists():
            missing.append(f"{html_path.relative_to(ROOT)} -> {target}")
assert not missing, "\n".join(missing)

print("compact redesign generated and validated")
