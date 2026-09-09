from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = "2026-09-09"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_many(path: str, replacements: list[tuple[str, str]]) -> None:
    file = ROOT / path
    if not file.exists():
        return
    text = file.read_text(encoding="utf-8")
    for old, new in replacements:
        text = text.replace(old, new)
    file.write_text(text, encoding="utf-8")


def insert_before_main_end(path: str, marker: str, block: str) -> None:
    file = ROOT / path
    if not file.exists():
        return
    text = file.read_text(encoding="utf-8")
    if marker in text:
        return
    if "</main>" not in text:
        return
    text = text.replace("</main>", block + "\n</main>", 1)
    file.write_text(text, encoding="utf-8")


# Compact facts used across the static Chinese and English pages.
common_replacements = [
    ("<strong>3</strong><span>Merged upstream PRs</span>", "<strong>5</strong><span>Merged upstream PRs</span>"),
    ("2 merged · 4 open", "4 merged · 2 review"),
    ("2 merged PRs", "4 merged PRs"),
    ("2 个 PR 已合并", "4 个 PR 已合并"),
    ("当前公开记录包含 2 个已合并 PR 与多项审阅中修复", "当前公开记录包含 4 个已合并 PR；#3661 / #3662 仍在审阅中"),
    ("2 个 RDMA 生命周期与故障恢复修复已合入上游", "4 个 Bugfix PR 已合入上游，覆盖 RDMA 生命周期、故障恢复、存储持久性与 Offloading 任务语义"),
    ("2 个已合并 bugfix PR", "4 个已合并 Bugfix PR"),
    ("2 个已合并 Bugfix PR", "4 个已合并 Bugfix PR"),
    ("其中 2 个 PR 已合并", "其中 4 个 PR 已合并"),
    ("Two merged reliability fixes across RDMA lifecycle and fault recovery", "Four merged fixes across RDMA lifecycle, fault recovery, storage durability, and offload bookkeeping"),
    ("Two merged reliability fixes", "Four merged reliability fixes"),
    ("Two merged bug-fix PRs", "Four merged bug-fix PRs"),
]

for page in [
    "index.html", "projects.html", "experience.html", "resume.html",
    "en/index.html", "en/projects.html", "en/experience.html", "en/resume.html",
]:
    replace_many(page, common_replacements)

# Homepage hardware signal: broaden the old H200-only metric now that Blackwell
# hardware is available, without claiming a specific SKU or unverified result.
replace_many("index.html", [
    ("<strong>8×H200</strong><span>MoE-RL 主实验环境</span>", "<strong>H200 · Blackwell</strong><span>实机 GPU 环境</span>"),
])
replace_many("en/index.html", [
    ("<strong>8×H200</strong><span>Primary MoE-RL environment</span>", "<strong>H200 · Blackwell</strong><span>Hands-on GPU access</span>"),
])

# Add a careful current-hardware note to the experience pages. Existing public
# results remain H200-grounded; Blackwell is described only as newly available
# hardware for cross-generation validation.
replace_many("experience.html", [
    ("围绕 H200 上的大模型训练推理链路，", "围绕 H200 上的大模型训练推理链路；现已具备 Blackwell 实机环境，用于后续跨代验证。"),
])
replace_many("en/experience.html", [
    ("H200", "H200 / Blackwell", 1) if False else ("__NOOP__", "__NOOP__"),
])

# Roadmap: reflect the new Blackwell access without inventing a B200/B300 SKU
# or publishing performance before measurements exist.
cn_blackwell = '''
<section class="dense-section section-line" id="blackwell-access">
  <div class="shell">
    <div class="dense-heading"><h2>Blackwell 实机验证</h2><span>Now</span></div>
    <p>已获得 Blackwell GPU 实机环境。下一阶段把 H→B 迁移从资料梳理推进到实测：Kernel 兼容性、TMA / Shared Memory 约束、低精度路径与端到端 Profiling。具体型号与性能结果只在完成验证后公开。</p>
  </div>
</section>'''

en_blackwell = '''
<section class="dense-section section-line" id="blackwell-access">
  <div class="shell">
    <div class="dense-heading"><h2>Blackwell validation</h2><span>Now</span></div>
    <p>Blackwell hardware is now available for hands-on testing. The next step is to move H→B migration work from documentation into reproducible measurements: kernel compatibility, TMA/shared-memory constraints, low-precision paths, and end-to-end profiling. Exact SKU and performance numbers will be published only after validation.</p>
  </div>
</section>'''

insert_before_main_end("roadmap.html", 'id="blackwell-access"', cn_blackwell)
insert_before_main_end("en/roadmap.html", 'id="blackwell-access"', en_blackwell)

# Mooncake detail pages are intentionally concise and status-driven. Rewriting
# them here keeps the public page accurate when the bilingual generator runs.
cn_mooncake = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Haoran Feng 在 Mooncake 分布式 KV Cache 项目中的公开上游贡献：RDMA、Store durability 与 offloading correctness。">
  <meta name="theme-color" content="#f4f2ed">
  <link rel="canonical" href="https://xfdg.github.io/projects/mooncake-contributions.html">
  <link rel="alternate" hreflang="zh-CN" href="https://xfdg.github.io/projects/mooncake-contributions.html">
  <link rel="alternate" hreflang="en" href="https://xfdg.github.io/en/projects/mooncake-contributions.html">
  <link rel="alternate" hreflang="x-default" href="https://xfdg.github.io/projects/mooncake-contributions.html">
  <title>Mooncake 开源贡献 — Haoran Feng</title>
  <link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../styles.css">
  <script src="../script.js" defer></script>
</head>
<body class="compact-site editorial-site" data-page="projects">
<header class="site-header"><div class="shell header-inner"><a class="brand" href="../index.html"><span class="brand-copy">Haoran Feng <small>AI Infrastructure</small></span></a><button class="menu-toggle" type="button" aria-label="打开导航" aria-expanded="false"><span></span></button><nav class="site-nav" aria-label="主导航"><a href="../index.html" data-nav="home">首页</a><a href="../projects.html" data-nav="projects">项目</a><a href="../experience.html" data-nav="experience">经历</a><a href="../writing.html" data-nav="writing">文章</a><a href="../contact.html" data-nav="contact">联系</a><a class="nav-cta" href="../resume.html" data-nav="resume">简历</a></nav></div></header>
<main>
<section class="compact-page-head"><div class="shell"><div class="detail-breadcrumbs"><a href="../projects.html">Projects</a><span>/</span><span>Mooncake</span></div><span class="eyebrow">Open Source · Distributed KV Cache · RDMA · Storage</span><div class="page-title-line"><h1>Mooncake：从 RDMA 生命周期到 Store 正确性。</h1><p>截至 {SNAPSHOT}，4 个 Bugfix PR 已合入上游，另有 2 个 PR 处于审阅中。</p></div><div class="metric-strip detail-strip"><div><strong>4</strong><span>Merged PRs</span></div><div><strong>2</strong><span>Under review</span></div><div><strong>TE + Store</strong><span>覆盖模块</span></div><div><strong>2026.09</strong><span>Status snapshot</span></div></div></div></section>
<section class="dense-section section-line"><div class="shell detail-narrow"><div class="dense-heading"><h2>已合入上游</h2><span>Accepted</span></div><div class="contribution-table-wrap"><table class="compact-table"><thead><tr><th>PR</th><th>模块</th><th>问题与修复</th><th>状态</th></tr></thead><tbody>
<tr><td><a href="https://github.com/kvcache-ai/Mooncake/pull/3726" target="_blank" rel="noreferrer">#3726 ↗</a></td><td>Store</td><td>修复 Offloading Queue “未入队却返回成功”的语义漏洞，避免 phantom task 与引用计数泄漏。</td><td>MERGED</td></tr>
<tr><td><a href="https://github.com/kvcache-ai/Mooncake/pull/3601" target="_blank" rel="noreferrer">#3601 ↗</a></td><td>Store</td><td>在提交 Bucket Metadata 前执行 datasync / fdatasync，并覆盖同步失败后的孤儿文件清理，恢复写入顺序持久性。</td><td>MERGED</td></tr>
<tr><td><a href="https://github.com/kvcache-ai/Mooncake/pull/3604" target="_blank" rel="noreferrer">#3604 ↗</a></td><td>Transfer Engine</td><td>RDMA 端口恢复后淘汰 stale Endpoint / QP，使下一次访问重建连接，避免复用错误状态 QP。</td><td>MERGED</td></tr>
<tr><td><a href="https://github.com/kvcache-ai/Mooncake/pull/3660" target="_blank" rel="noreferrer">#3660 ↗</a></td><td>Transfer Engine</td><td>MR 注销后恢复 MADV_DOFORK，避免高频注册/注销留下永久 VMA 分裂并耗尽 vm.max_map_count。</td><td>MERGED</td></tr>
</tbody></table></div></div></section>
<section class="dense-section section-line"><div class="shell detail-narrow"><div class="dense-heading"><h2>审阅中</h2><span>Open</span></div><div class="timeline-compact"><div><time>#3661</time><strong>TENT bounded queue / retry admission</strong><span>把 queue-full 从永久自旋/活锁改成可失败的非阻塞提交，并继续收紧 batch admission 与异步生命周期边界。 <a href="https://github.com/kvcache-ai/Mooncake/pull/3661" target="_blank" rel="noreferrer">PR ↗</a></span></div><div><time>#3662</time><strong>Store session replica selection</strong><span>围绕 SSD offloading 场景下的 session ranged-get 与 replica selection 继续完善语义和回归覆盖。 <a href="https://github.com/kvcache-ai/Mooncake/pull/3662" target="_blank" rel="noreferrer">PR ↗</a></span></div></div><p class="boundary-note"><strong>状态边界。</strong> 本页只把 GitHub 当前显示为 merged 的 PR 计入“已合入”；Open PR 不计入 5 个独立上游合入总数。TensorFlow MUSA PR 属于摩尔线程实习产出，也不计入这一独立开源口径。</p></div></section>
</main>
<footer class="site-footer"><div class="shell footer-inner"><span>© <span data-year></span> Haoran Feng</span><div class="footer-links"><a href="mailto:225010160@link.cuhk.edu.cn">Email</a><a href="https://github.com/XFDG" target="_blank" rel="noreferrer">GitHub</a><a href="../resume.html">Resume</a></div></div></footer>
</body></html>'''

en_mooncake = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Haoran Feng's upstream Mooncake contributions across RDMA lifecycle, storage durability, and offload correctness.">
  <meta name="theme-color" content="#f4f2ed">
  <link rel="canonical" href="https://xfdg.github.io/en/projects/mooncake-contributions.html">
  <link rel="alternate" hreflang="en" href="https://xfdg.github.io/en/projects/mooncake-contributions.html">
  <link rel="alternate" hreflang="zh-CN" href="https://xfdg.github.io/projects/mooncake-contributions.html">
  <link rel="alternate" hreflang="x-default" href="https://xfdg.github.io/projects/mooncake-contributions.html">
  <title>Mooncake Contributions — Haoran Feng</title>
  <link rel="icon" href="../../assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../../styles.css">
  <script src="../../script.js" defer></script>
</head>
<body class="compact-site editorial-site" data-page="projects">
<header class="site-header"><div class="shell header-inner"><a class="brand" href="../index.html"><span class="brand-copy">Haoran Feng <small>AI Infrastructure</small></span></a><button class="menu-toggle" type="button" aria-label="Open navigation" aria-expanded="false"><span></span></button><nav class="site-nav" aria-label="Primary navigation"><a href="../index.html" data-nav="home">Home</a><a href="../projects.html" data-nav="projects">Work</a><a href="../experience.html" data-nav="experience">Experience</a><a href="../writing.html" data-nav="writing">Writing</a><a href="../contact.html" data-nav="contact">Contact</a><a class="nav-cta" href="../resume.html" data-nav="resume">Résumé</a></nav></div></header>
<main>
<section class="compact-page-head"><div class="shell"><div class="detail-breadcrumbs"><a href="../projects.html">Projects</a><span>/</span><span>Mooncake</span></div><span class="eyebrow">Open Source · Distributed KV Cache · RDMA · Storage</span><div class="page-title-line"><h1>Mooncake: from RDMA lifecycle to storage correctness.</h1><p>As of {SNAPSHOT}, four bug-fix PRs have been merged upstream and two remain under review.</p></div><div class="metric-strip detail-strip"><div><strong>4</strong><span>Merged PRs</span></div><div><strong>2</strong><span>Under review</span></div><div><strong>TE + Store</strong><span>Modules</span></div><div><strong>2026.09</strong><span>Status snapshot</span></div></div></div></section>
<section class="dense-section section-line"><div class="shell detail-narrow"><div class="dense-heading"><h2>Merged upstream</h2><span>Accepted</span></div><div class="contribution-table-wrap"><table class="compact-table"><thead><tr><th>PR</th><th>Area</th><th>Problem and fix</th><th>Status</th></tr></thead><tbody>
<tr><td><a href="https://github.com/kvcache-ai/Mooncake/pull/3726" target="_blank" rel="noreferrer">#3726 ↗</a></td><td>Store</td><td>Stopped no-op offload paths from reporting success, preventing phantom tasks and leaked replica references.</td><td>MERGED</td></tr>
<tr><td><a href="https://github.com/kvcache-ai/Mooncake/pull/3601" target="_blank" rel="noreferrer">#3601 ↗</a></td><td>Store</td><td>Flushes bucket data before metadata commit and cleans orphan files on sync failure, restoring write-ordering durability.</td><td>MERGED</td></tr>
<tr><td><a href="https://github.com/kvcache-ai/Mooncake/pull/3604" target="_blank" rel="noreferrer">#3604 ↗</a></td><td>Transfer Engine</td><td>Evicts stale endpoints/QPs after RDMA port recovery so subsequent access rebuilds a healthy connection.</td><td>MERGED</td></tr>
<tr><td><a href="https://github.com/kvcache-ai/Mooncake/pull/3660" target="_blank" rel="noreferrer">#3660 ↗</a></td><td>Transfer Engine</td><td>Restores MADV_DOFORK after MR deregistration to prevent persistent VMA fragmentation and vm.max_map_count exhaustion.</td><td>MERGED</td></tr>
</tbody></table></div></div></section>
<section class="dense-section section-line"><div class="shell detail-narrow"><div class="dense-heading"><h2>Under review</h2><span>Open</span></div><div class="timeline-compact"><div><time>#3661</time><strong>TENT bounded queue and retry admission</strong><span>Reworks queue-full handling from permanent spinning toward non-blocking failure and tighter batch-admission/lifetime semantics. <a href="https://github.com/kvcache-ai/Mooncake/pull/3661" target="_blank" rel="noreferrer">PR ↗</a></span></div><div><time>#3662</time><strong>Store session replica selection</strong><span>Refines session ranged-get and replica-selection behavior around SSD-offloading scenarios with regression coverage. <a href="https://github.com/kvcache-ai/Mooncake/pull/3662" target="_blank" rel="noreferrer">PR ↗</a></span></div></div><p class="boundary-note"><strong>Status boundary.</strong> Only PRs currently marked merged by GitHub are counted as accepted. Open PRs are excluded from the five independent merged-upstream contributions. Moore Threads MUSA PRs remain internship evidence, not independent community contributions.</p></div></section>
</main>
<footer class="site-footer"><div class="shell footer-inner"><span>© <span data-year></span> Haoran Feng</span><div class="footer-links"><a href="mailto:225010160@link.cuhk.edu.cn">Email</a><a href="https://github.com/XFDG" target="_blank" rel="noreferrer">GitHub</a><a href="../resume.html">Résumé</a></div></div></footer>
</body></html>'''

write("projects/mooncake-contributions.html", cn_mooncake)
write("en/projects/mooncake-contributions.html", en_mooncake)

# Keep generator text from reintroducing stale counts where it contains the old
# literal copy. The post-generation sync above is still the source of truth.
generator = ROOT / "tools/build_bilingual.py"
if generator.exists():
    text = generator.read_text(encoding="utf-8")
    for old, new in [
        ("2 merged PRs", "4 merged PRs"),
        ("Two merged reliability fixes", "Four merged reliability fixes"),
        ("<strong>3</strong><span>Merged upstream PRs</span>", "<strong>5</strong><span>Merged upstream PRs</span>"),
        ("<strong>8×H200</strong><span>Primary MoE-RL environment</span>", "<strong>H200 · Blackwell</strong><span>Hands-on GPU access</span>"),
    ]:
        text = text.replace(old, new)
    generator.write_text(text, encoding="utf-8")

print("profile status synced: 5 independent merged PRs; Mooncake 4 merged / 2 review; Blackwell access added")
