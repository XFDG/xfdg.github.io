from __future__ import annotations

from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import re

ROOT = Path(".")
BASE = "https://xfdg.github.io"
EMAIL = "225010160@link.cuhk.edu.cn"
GITHUB = "https://github.com/XFDG"
CSDN = "https://blog.csdn.net/XFDG01"
ZHIHU = "https://www.zhihu.com/people/xian-feng-dao-gu-73-49"
OPENREVIEW = "https://openreview.net/forum?id=6eDZdA6IGW"
MIRAGE_PR = "https://github.com/mirage-project/mirage/pull/755"
KAGGLE = "https://www.kaggle.com/competitions/dl2023autumexp2"

OUTPUTS: list[str] = [
    "index.html",
    "projects.html",
    "experience.html",
    "writing.html",
    "contact.html",
    "resume.html",
    "research.html",
    "roadmap.html",
    "404.html",
    "projects/mooncake-contributions.html",
    "projects/mirage-contribution.html",
    "projects/flashinfer-ftz.html",
    "projects/router-replay.html",
    "projects/oe-async.html",
    "projects/gemm-profiling.html",
    "projects/deepgemm-offline.html",
    "projects/musa-extension.html",
    "projects/quant-runtime.html",
    "projects/drone-detection-pipeline.html",
]


def output_url(path: str) -> str:
    return f"{BASE}/en/" if path == "index.html" else f"{BASE}/en/{path}"


def zh_url(path: str) -> str:
    return f"{BASE}/" if path == "index.html" else f"{BASE}/{path}"


def depth_for(path: str) -> int:
    return len(Path(path).parts)


def prefix_for(path: str) -> str:
    return "../" * depth_for(path)


def nav(path: str) -> str:
    prefix = prefix_for(path)
    items = [
        ("home", "Home", f"{prefix}en/index.html"),
        ("projects", "Work", f"{prefix}en/projects.html"),
        ("experience", "Experience", f"{prefix}en/experience.html"),
        ("writing", "Writing", f"{prefix}en/writing.html"),
        ("contact", "Contact", f"{prefix}en/contact.html"),
        ("resume", "Résumé", f"{prefix}en/resume.html"),
    ]
    return "".join(
        f'<a data-nav="{key}" href="{href}"{" class=\"nav-cta\"" if key == "resume" else ""}>{label}</a>'
        for key, label, href in items
    )


def footer(path: str, extra: str = "") -> str:
    prefix = prefix_for(path)
    links = [
        f'<a href="mailto:{EMAIL}">Email</a>',
        f'<a href="{GITHUB}" target="_blank" rel="noreferrer">GitHub</a>',
        f'<a href="{CSDN}" target="_blank" rel="me noopener noreferrer">CSDN</a>',
        f'<a href="{ZHIHU}" target="_blank" rel="me noopener noreferrer">Zhihu</a>',
        f'<a href="{prefix}en/resume.html">Résumé</a>',
    ]
    if extra:
        links.insert(-1, extra)
    return (
        '<footer class="site-footer"><div class="shell footer-inner">'
        '<span>© <span data-year></span> Haoran Feng</span>'
        f'<div class="footer-links">{"".join(links)}</div>'
        '</div></footer>'
    )


def page(path: str, *, title: str, description: str, page_key: str, body: str,
         body_class: str = "compact-site editorial-site", extra_footer: str = "") -> str:
    prefix = prefix_for(path)
    canonical = output_url(path)
    zh = zh_url(path)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(description, quote=True)}">
  <meta name="theme-color" content="#f4f2ed">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" hreflang="en" href="{canonical}">
  <link rel="alternate" hreflang="zh-CN" href="{zh}">
  <link rel="alternate" hreflang="x-default" href="{zh}">
  <title>{escape(title)} — Haoran Feng</title>
  <link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{prefix}styles.css">
  <script src="{prefix}script.js" defer></script>
</head>
<body class="{body_class}" data-page="{page_key}">
<header class="site-header">
  <div class="shell header-inner">
    <a class="brand" href="{prefix}en/index.html" aria-label="Home">
      <span class="brand-copy">Haoran Feng <small>AI Infrastructure</small></span>
    </a>
    <button class="menu-toggle" type="button" aria-label="Open navigation" aria-expanded="false"><span></span></button>
    <nav class="site-nav" aria-label="Primary navigation">{nav(path)}</nav>
  </div>
</header>
<main>
{body}
</main>
{footer(path, extra_footer)}
</body>
</html>
"""


WORK_ITEMS = [
    {
        "href": "projects/mooncake-contributions.html",
        "title": "Mooncake: RDMA and storage reliability",
        "summary": "Upstream fixes for memory-region lifecycle and endpoint recovery in a distributed KV-cache system.",
        "evidence": "2 merged PRs",
        "badge": "OPEN SOURCE",
        "cat": "opensource systems inference",
    },
    {
        "href": "projects/mirage-contribution.html",
        "title": "Mirage: out-of-range tokens caused by Argmax padding",
        "summary": "Fixed padded lm_head rows winning Argmax when every valid logit is negative.",
        "evidence": "PR #755 merged",
        "badge": "OPEN SOURCE",
        "cat": "opensource systems inference",
    },
    {
        "href": "projects/flashinfer-ftz.html",
        "title": "FlashInfer CUDA Graph hang: FTZ and sentinel semantics",
        "summary": "Traced a downstream rollout timeout to a fused collective kernel and validated a bit-exact fix.",
        "evidence": "SASS predicate 8→0",
        "badge": "GPU DEBUG",
        "cat": "systems inference gpu",
    },
    {
        "href": "projects/router-replay.html",
        "title": "R3 Router Replay for MoE training–rollout consistency",
        "summary": "Connected route capture, observe/replay, response masks, and probability-drift metrics.",
        "evidence": "mismatch 17–19%→0",
        "badge": "RL INFRA",
        "cat": "rl systems inference",
    },
    {
        "href": "projects/oe-async.html",
        "title": "OE Async: GPU token history and fused hashing",
        "summary": "Removed CPU round trips from asynchronous decode while preserving state correctness across requests.",
        "evidence": "TP1 +5.0%",
        "badge": "ASYNC OP",
        "cat": "systems inference gpu",
    },
    {
        "href": "projects/gemm-profiling.html",
        "title": "H200 MoE Grouped GEMM profiling and tuning",
        "summary": "Corrected the expanded/compact workload definition before replaying production shapes and tuning SM90 kernels.",
        "evidence": "workload error 4–6×",
        "badge": "GPU PERF",
        "cat": "gpu inference",
    },
    {
        "href": "projects/deepgemm-offline.html",
        "title": "DeepGEMM offline cubin and wheel delivery",
        "summary": "Turned runtime JIT artifacts into a verifiable offline bundle for isolated inference environments.",
        "evidence": "109→359 kernels",
        "badge": "DELIVERY",
        "cat": "systems inference gpu",
    },
    {
        "href": "projects/musa-extension.html",
        "title": "TensorFlow MUSA Extension",
        "summary": "Framework-backend work spanning operators, graph fusion, host/device semantics, stability, and profiling tools.",
        "evidence": "11/11 GELU fused",
        "badge": "FRAMEWORK",
        "cat": "heterogeneous gpu systems",
    },
    {
        "href": "projects/quant-runtime.html",
        "title": "LLMQRT quantized inference runtime",
        "summary": "A lightweight runtime covering AWQ W4A16, W8A8, FP8, attention backends, KV cache, and tensor parallelism.",
        "evidence": "AWQ · INT8 · FP8",
        "badge": "RUNTIME",
        "cat": "systems inference gpu",
    },
    {
        "href": "projects/drone-detection-pipeline.html",
        "title": "Drone detection experiment pipeline",
        "summary": "Unified three datasets and built a recoverable, multi-GPU, multi-model evaluation workflow.",
        "evidence": "171,568 samples",
        "badge": "ML SYSTEMS",
        "cat": "ml systems",
    },
]


def work_rows(items: list[dict], *, prefix: str = "", include_categories: bool = False) -> str:
    rows = []
    for idx, item in enumerate(items, 1):
        data = f' data-category="{item["cat"]}"' if include_categories else ""
        rows.append(
            f'<a class="work-row{" filter-item" if include_categories else ""}"{data} href="{prefix}{item["href"]}">'
            f'<span class="work-index">{idx:02d}</span>'
            f'<span class="work-main"><strong>{item["title"]}</strong><small>{item["summary"]}</small></span>'
            f'<span class="work-evidence">{item["evidence"]}</span>'
            f'<span class="work-badge">{item["badge"]}</span>'
            '<span class="work-arrow">↗</span></a>'
        )
    return "".join(rows)


def home_page() -> str:
    selected = WORK_ITEMS[:8]
    body = f"""
<section class="editorial-hero">
  <div class="shell">
    <div class="editorial-hero-grid">
      <div class="hero-primary">
        <span class="eyebrow">AI Infrastructure / GPU Systems / Open Source</span>
        <h1>Haoran Feng<span>冯浩然</span></h1>
      </div>
      <div class="hero-secondary">
        <p class="hero-statement">M.Sc. candidate at CUHK-Shenzhen, focused on LLM systems and GPU performance engineering.</p>
        <dl class="hero-facts">
          <div><dt>Current</dt><dd>LLM post-training and inference infrastructure</dd></div>
          <div><dt>Focus</dt><dd>CUDA · MoE · RDMA · distributed inference</dd></div>
          <div><dt>Research</dt><dd>AAAI 2027 submission on CoT distillation</dd></div>
          <div><dt>Open source</dt><dd>Mooncake · Mirage</dd></div>
        </dl>
        <div class="quick-links">
          <a href="mailto:{EMAIL}">Email</a>
          <a href="{GITHUB}" target="_blank" rel="noreferrer">GitHub ↗</a>
          <a href="resume.html">Résumé</a>
          <a href="research.html">Research</a>
        </div>
      </div>
    </div>
    <div class="metric-strip">
      <div><strong>3</strong><span>Merged upstream PRs</span></div>
      <div><strong>8×H200</strong><span>Primary MoE-RL environment</span></div>
      <div><strong>128 GPUs</strong><span>Largest validation scale</span></div>
      <div><strong>2027</strong><span>Expected graduation</span></div>
    </div>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell">
    <div class="dense-heading"><h2>Selected work</h2><a href="projects.html">All work →</a></div>
    <div class="work-list">{work_rows(selected)}</div>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell">
    <div class="dense-heading"><h2>Research</h2><span>AAAI 2027 · Under review</span></div>
    <a class="activity-row" href="research.html">
      <div class="activity-title">
        <strong>From Structure to Preference</strong>
        <span>Token-weighted chain-of-thought distillation</span>
      </div>
      <p>A three-stage framework combining rationale structure recovery, intervention-based token weighting, and preference optimization.</p>
      <div class="activity-meta"><span>Revised manuscript</span><span>OpenReview ↗</span></div>
    </a>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell">
    <div class="dense-heading"><h2>Education</h2><a href="experience.html">Details →</a></div>
    <div class="timeline-compact education-compact">
      <div><time>2025 — 2027</time><strong>The Chinese University of Hong Kong, Shenzhen</strong><span>M.Sc. in Integrated Circuits and Systems</span></div>
      <div><time>2021 — 2025</time><strong>Shandong University</strong><span>B.Eng. in Electronic Science and Technology · Minor in Computer Science</span></div>
      <div><time>Undergraduate</time><strong>Early technical work</strong><span>Academic scholarship; semi-supervised ResNet classification, Top-1 51.8% → 85.1%, 7th in a Kaggle competition.</span></div>
    </div>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell two-column-dense">
    <div>
      <div class="dense-heading"><h2>Experience</h2><a href="experience.html">Details →</a></div>
      <div class="timeline-compact">
        <div><time>2026.04 — Present</time><strong>LLM systems and high-performance computing</strong><span>MoE-RL · CUDA Graph · asynchronous decode · H200 kernels</span></div>
        <div><time>2026.01 — 2026.04</time><strong>Moore Threads · TensorFlow MUSA Extension</strong><span>Framework backend · graph fusion · kernel debugging</span></div>
        <div><time>2024.08 — 2024.12</time><strong>Huawei · General software engineering</strong><span>Large C/C++ systems · static analysis · automation</span></div>
      </div>
    </div>
    <div>
      <div class="dense-heading"><h2>Open source</h2><span>Independent upstream contributions</span></div>
      <div class="os-list">
        <a href="projects/mooncake-contributions.html"><strong>Mooncake</strong><span>Two merged reliability fixes across RDMA lifecycle and fault recovery</span><b>↗</b></a>
        <a href="projects/mirage-contribution.html"><strong>Mirage</strong><span>Merged Qwen3 inference correctness fix for padded Argmax rows</span><b>↗</b></a>
      </div>
    </div>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell">
    <div class="dense-heading"><h2>Writing & profiles</h2><a href="writing.html">Writing index →</a></div>
    <div class="profile-links">
      <a href="{CSDN}" target="_blank" rel="me noopener noreferrer"><strong>CSDN</strong><span>Engineering notes, benchmarks, and debugging reports</span></a>
      <a href="{ZHIHU}" target="_blank" rel="me noopener noreferrer"><strong>Zhihu</strong><span>System explanations, technical comparisons, and commentary</span></a>
      <a href="{GITHUB}" target="_blank" rel="noreferrer"><strong>GitHub</strong><span>Code, pull requests, and public engineering evidence</span></a>
    </div>
  </div>
</section>
"""
    return page(
        "index.html",
        title="AI Infrastructure",
        description="Haoran Feng's portfolio: LLM systems, GPU performance, research, and upstream open-source contributions.",
        page_key="home",
        body=body,
    )


def projects_page() -> str:
    filters = "".join(
        f'<button class="filter-button{" active" if key == "all" else ""}" data-filter="{key}" type="button">{label}</button>'
        for key, label in [
            ("all", "ALL"),
            ("opensource", "OPEN SOURCE"),
            ("systems", "SYSTEMS"),
            ("rl", "RL INFRA"),
            ("inference", "INFERENCE"),
            ("gpu", "GPU PERF"),
            ("heterogeneous", "HETEROGENEOUS"),
            ("ml", "ML PIPELINE"),
        ]
    )
    earlier = {
        "href": KAGGLE,
        "title": "Semi-supervised image classification with ResNet-18",
        "summary": "Used pseudo-labeling and mixed augmentation to improve classification under limited labels and class imbalance.",
        "evidence": "Top-1 51.8%→85.1% · 7th",
        "badge": "EARLIER WORK",
        "cat": "ml",
    }
    body = f"""
<section class="compact-page-head">
  <div class="shell">
    <span class="eyebrow">Projects / Public evidence</span>
    <div class="page-title-line"><h1>Selected engineering work</h1><p>Organized by problem, method, evidence, and claim boundaries—not by tool names.</p></div>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell">
    <div class="filter-bar compact-filters">{filters}</div>
    <div class="work-list project-index-list">
      {work_rows(WORK_ITEMS, include_categories=True)}
      <a class="work-row filter-item" data-category="ml" href="{KAGGLE}" target="_blank" rel="noreferrer">
        <span class="work-index">11</span>
        <span class="work-main"><strong>{earlier["title"]}</strong><small>{earlier["summary"]}</small></span>
        <span class="work-evidence">{earlier["evidence"]}</span>
        <span class="work-badge">{earlier["badge"]}</span>
        <span class="work-arrow">↗</span>
      </a>
    </div>
    <p class="index-note">Company work is presented through anonymized methods and aggregated results. Open-source status follows the linked upstream pull requests.</p>
  </div>
</section>
"""
    return page(
        "projects.html",
        title="Projects",
        description="Selected AI infrastructure, GPU performance, distributed systems, and open-source work by Haoran Feng.",
        page_key="projects",
        body=body,
    )


def experience_page() -> str:
    body = f"""
<section class="compact-page-head">
  <div class="shell">
    <span class="eyebrow">Experience / Education / Research</span>
    <div class="page-title-line"><h1>From hardware-aware foundations to LLM systems.</h1><p>My work sits between model behavior, framework semantics, runtime execution, and GPU performance.</p></div>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell two-column-dense">
    <div>
      <div class="dense-heading"><h2>Education</h2><span>2021 — 2027</span></div>
      <div class="timeline-compact">
        <div><time>2025 — 2027</time><strong>The Chinese University of Hong Kong, Shenzhen</strong><span>M.Sc. in Integrated Circuits and Systems</span></div>
        <div><time>2021 — 2025</time><strong>Shandong University</strong><span>B.Eng. in Electronic Science and Technology · Minor in Computer Science</span></div>
      </div>
    </div>
    <div>
      <div class="dense-heading"><h2>Undergraduate foundation</h2><span>Selected evidence</span></div>
      <div class="timeline-compact">
        <div><time>Coursework</time><strong>Electronics + computer science</strong><span>Digital/analog circuits, microprocessors, FPGA, embedded systems, data structures, networks, and databases.</span></div>
        <div><time>Awards</time><strong>Academic and innovation scholarships</strong><span>Academic scholarship (top 20%) and an innovation-oriented merit scholarship.</span></div>
        <div><time>Project</time><strong>ResNet semi-supervised classification</strong><span>Top-1 51.8% → 85.1%; 7th in a Kaggle competition. <a href="{KAGGLE}" target="_blank" rel="noreferrer">Competition ↗</a></span></div>
      </div>
    </div>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell">
    <div class="dense-heading"><h2>Research</h2><span>AAAI 2027 · Under review</span></div>
    <a class="activity-row" href="research.html">
      <div class="activity-title"><strong>From Structure to Preference</strong><span>Haoran Feng and co-authors</span></div>
      <p>Intervention-based token importance for structured chain-of-thought distillation, followed by preference optimization.</p>
      <div class="activity-meta"><span>OpenReview</span><span>Details ↗</span></div>
    </a>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell">
    <div class="dense-heading"><h2>Professional experience</h2><span>Selected technical scope</span></div>
    <div class="timeline-compact">
      <div><time>2026.04 — Present</time><strong>LLM post-training and inference infrastructure</strong><span>CUDA Graph stability, MoE Router Replay, asynchronous decode state, Grouped GEMM workload reconstruction, and offline inference delivery on H200 systems.</span></div>
      <div><time>2026.01 — 2026.04</time><strong>Moore Threads · Operator and compiler optimization intern</strong><span>TensorFlow MUSA backend, graph fusion, host/device semantics, long-run stability, operator hot paths, and kernel observability.</span></div>
      <div><time>2024.08 — 2024.12</time><strong>Huawei · General software engineering intern</strong><span>Large C/C++ codebases, static-analysis rules, log-driven debugging, Python automation, testing, and CI workflows.</span></div>
    </div>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell two-column-dense">
    <div>
      <div class="dense-heading"><h2>Technical scope</h2><span>Systems</span></div>
      <div class="timeline-compact">
        <div><time>LLM systems</time><strong>veRL · Megatron-LM · vLLM · SGLang</strong><span>Training–rollout consistency, speculative decode, CUDA Graphs, and MoE execution.</span></div>
        <div><time>GPU</time><strong>CUDA · CUTLASS · CuTe · DeepGEMM</strong><span>Profiling, kernel replay, memory/layout reasoning, and architecture-aware tuning.</span></div>
        <div><time>Frameworks</time><strong>TensorFlow and PyTorch extensions</strong><span>Operator registration, graph fusion, device placement, and host/device contracts.</span></div>
      </div>
    </div>
    <div>
      <div class="dense-heading"><h2>Independent open source</h2><span>Accepted upstream</span></div>
      <div class="os-list">
        <a href="projects/mooncake-contributions.html"><strong>Mooncake</strong><span>Two merged reliability fixes in a distributed KV-cache system</span><b>View ↗</b></a>
        <a href="projects/mirage-contribution.html"><strong>Mirage</strong><span>Merged Qwen3 inference correctness fix</span><b>View ↗</b></a>
      </div>
      <p class="boundary-note">TensorFlow MUSA pull requests were produced as part of the Moore Threads internship and are therefore presented under professional experience, not as independent community work.</p>
    </div>
  </div>
</section>
"""
    return page(
        "experience.html",
        title="Experience",
        description="Education, research, professional experience, and technical scope of Haoran Feng.",
        page_key="experience",
        body=body,
    )


def research_page() -> str:
    body = f"""
<section class="compact-page-head">
  <div class="shell">
    <div class="detail-breadcrumbs"><a href="writing.html">Writing</a><span>/</span><span>Research</span></div>
    <span class="eyebrow">Research · Chain-of-Thought Distillation</span>
    <div class="page-title-line">
      <h1>From Structure to Preference: Token Weighting for Chain-of-Thought Distillation in Large Language Models</h1>
      <p>AAAI 2027 submission · revised manuscript posted on OpenReview · currently under review.</p>
    </div>
    <div class="metric-strip detail-strip">
      <div><strong>3 stages</strong><span>Structure → Weighting → Preference</span></div>
      <div><strong>94.01%</strong><span>Qwen2.5-7B · GSM8K</span></div>
      <div><strong>94.00%</strong><span>Qwen2.5-7B · SVAMP</span></div>
      <div><strong>Under review</strong><span>AAAI 2027</span></div>
    </div>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell detail-narrow">
    <div class="dense-heading"><h2>Paper</h2><a href="{OPENREVIEW}" target="_blank" rel="noreferrer">OpenReview ↗</a></div>
    <p><strong>Authors:</strong> Shankui Han, Zhaoyu Li, Weiwen Yuan, Yuyuan Yang, <strong>Haoran Feng</strong>, Jinke Ren.</p>
    <p>Most chain-of-thought distillation methods supervise rationale tokens almost uniformly. This work asks a more specific question: which reasoning tokens are actually necessary for the teacher to reach the reference answer?</p>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell detail-narrow">
    <div class="dense-heading"><h2>Method</h2><span>Three-stage framework</span></div>
    <div class="timeline-compact">
      <div><time>Stage 1</time><strong>Structure recovery</strong><span>Recover a canonical four-part rationale from shuffled or masked inputs.</span></div>
      <div><time>Stage 2</time><strong>Token-weighted supervision</strong><span>Perturb each rationale token and measure the drop in the teacher's likelihood of the reference answer; apply stronger supervision to answer-critical positions.</span></div>
      <div><time>Stage 3</time><strong>Preference optimization</strong><span>Construct preference pairs from student outputs and optimize toward responses that are both correct and structurally complete.</span></div>
    </div>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell detail-narrow">
    <div class="dense-heading"><h2>Reported results</h2><span>GSM8K / SVAMP</span></div>
    <div class="contribution-table-wrap">
      <table class="compact-table">
        <thead><tr><th>Student model</th><th>GSM8K</th><th>SVAMP</th><th>Interpretation</th></tr></thead>
        <tbody>
          <tr><td>Qwen2.5-7B-Instruct</td><td>94.01%</td><td>94.00%</td><td>+5.51 / +10.10 percentage points over the strongest baselines reported in the manuscript</td></tr>
          <tr><td>Qwen2.5-0.5B-Instruct</td><td>38.51%</td><td>50.33%</td><td>The benefit depends on student capacity</td></tr>
        </tbody>
      </table>
    </div>
    <p class="boundary-note"><strong>Status boundary.</strong> The manuscript is under review at AAAI 2027. These numbers are reported submission results, not an accepted or peer-reviewed publication claim.</p>
  </div>
</section>
"""
    return page(
        "research.html",
        title="Research",
        description="AAAI 2027 submission on token-weighted chain-of-thought distillation by Haoran Feng and co-authors.",
        page_key="writing",
        body=body,
        extra_footer=f'<a href="{OPENREVIEW}" target="_blank" rel="noreferrer">OpenReview</a>',
    )


def writing_page() -> str:
    body = f"""
<section class="compact-page-head">
  <div class="shell">
    <span class="eyebrow">Writing / Notes / Distribution</span>
    <div class="page-title-line"><h1>Technical writing</h1><p>The website is the canonical index; external platforms are used for distribution and discussion.</p></div>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell">
    <div class="dense-heading"><h2>Publishing channels</h2><span>External profiles</span></div>
    <div class="profile-links">
      <a href="{CSDN}" target="_blank" rel="me noopener noreferrer"><strong>CSDN</strong><span>Reproducible engineering notes, build steps, benchmarks, and debugging reports</span></a>
      <a href="{ZHIHU}" target="_blank" rel="me noopener noreferrer"><strong>Zhihu</strong><span>Mechanism explanations, technical comparisons, and longer-form commentary</span></a>
      <a href="{GITHUB}" target="_blank" rel="noreferrer"><strong>GitHub</strong><span>Code, pull requests, public documents, and traceable engineering evidence</span></a>
    </div>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell">
    <div class="dense-heading"><h2>Public evidence notes</h2><span>Selected long-form material</span></div>
    <div class="work-list">
      <a class="work-row" href="projects/flashinfer-ftz.html"><span class="work-index">01</span><span class="work-main"><strong>From rollout timeout to FTZ/sentinel semantics</strong><small>A debugging narrative across RPC symptoms, CUDA Graph capture, a fused collective kernel, and SASS verification.</small></span><span class="work-evidence">GPU correctness</span><span class="work-badge">SYSTEMS</span><span class="work-arrow">↗</span></a>
      <a class="work-row" href="projects/oe-async.html"><span class="work-index">02</span><span class="work-main"><strong>State management in asynchronous decode</strong><small>GPU-resident token history, fused hashing, mixed batches, slot reuse, and multi-rank validation.</small></span><span class="work-evidence">TP1 / TP2 / TP4</span><span class="work-badge">INFERENCE</span><span class="work-arrow">↗</span></a>
      <a class="work-row" href="projects/gemm-profiling.html"><span class="work-index">03</span><span class="work-main"><strong>Define the workload before tuning the kernel</strong><small>Why expanded and compact MoE row counts changed the optimization conclusion by 4–6×.</small></span><span class="work-evidence">H200 · SM90</span><span class="work-badge">PERFORMANCE</span><span class="work-arrow">↗</span></a>
      <a class="work-row" href="research.html"><span class="work-index">04</span><span class="work-main"><strong>Token-weighted chain-of-thought distillation</strong><small>Research manuscript combining structure recovery, intervention-based importance, and preference optimization.</small></span><span class="work-evidence">AAAI 2027</span><span class="work-badge">RESEARCH</span><span class="work-arrow">↗</span></a>
    </div>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell detail-narrow">
    <div class="dense-heading"><h2>Editorial principle</h2><span>Show the evidence</span></div>
    <p>Each technical note should answer four questions: what failed, how the hypothesis space was reduced, what evidence supports the conclusion, and what the result does <em>not</em> prove.</p>
  </div>
</section>
"""
    return page(
        "writing.html",
        title="Writing",
        description="Technical notes, engineering reports, and public writing channels of Haoran Feng.",
        page_key="writing",
        body=body,
    )


def contact_page() -> str:
    body = f"""
<section class="compact-page-head">
  <div class="shell">
    <span class="eyebrow">Contact</span>
    <div class="page-title-line"><h1>Get in touch</h1><p>For AI infrastructure, GPU performance, LLM systems, research, or open-source collaboration.</p></div>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell two-column-dense">
    <div>
      <div class="dense-heading"><h2>Direct</h2><span>Preferred</span></div>
      <div class="os-list">
        <a href="mailto:{EMAIL}"><strong>Email</strong><span>{EMAIL}</span><b>↗</b></a>
        <a href="{GITHUB}" target="_blank" rel="noreferrer"><strong>GitHub</strong><span>Repositories, pull requests, and public engineering evidence</span><b>↗</b></a>
      </div>
    </div>
    <div>
      <div class="dense-heading"><h2>Writing</h2><span>Public profiles</span></div>
      <div class="os-list">
        <a href="{CSDN}" target="_blank" rel="me noopener noreferrer"><strong>CSDN</strong><span>Engineering tutorials and performance notes</span><b>↗</b></a>
        <a href="{ZHIHU}" target="_blank" rel="me noopener noreferrer"><strong>Zhihu</strong><span>System explanations and technical discussion</span><b>↗</b></a>
      </div>
    </div>
  </div>
</section>
<section class="dense-section section-line">
  <div class="shell detail-narrow">
    <div class="dense-heading"><h2>Current interests</h2><span>2026</span></div>
    <p>LLM post-training infrastructure, inference systems, MoE execution, CUDA/CUTLASS kernels, distributed KV cache, numerical consistency, and reproducible performance work.</p>
    <div class="button-row"><a class="button primary" href="mailto:{EMAIL}">Send email</a><a class="button" href="resume.html">View résumé</a></div>
  </div>
</section>
"""
    return page(
        "contact.html",
        title="Contact",
        description="Contact Haoran Feng for AI infrastructure, GPU performance, research, and open-source collaboration.",
        page_key="contact",
        body=body,
    )


def resume_page() -> str:
    body = f"""
<section class="compact-page-head print-hidden">
  <div class="shell">
    <span class="eyebrow">Public résumé</span>
    <div class="page-title-line"><h1>Résumé</h1><p>A public, privacy-safe version. Use the print command to save it as PDF.</p></div>
    <div class="button-row"><button class="button primary" onclick="window.print()" type="button">Print / Save PDF</button><a class="button" href="projects.html">Project evidence</a></div>
  </div>
</section>
<section class="section compact section-line">
  <div class="narrow">
    <article class="resume-sheet">
      <header class="resume-header">
        <div><h1>Haoran Feng <span style="color:var(--muted);font-weight:500">冯浩然</span></h1><p style="margin:0">AI Infrastructure · LLM Systems · GPU Performance</p></div>
        <div class="resume-contact"><a href="mailto:{EMAIL}">{EMAIL}</a><a href="{GITHUB}" target="_blank" rel="noreferrer">github.com/XFDG</a><span>Shenzhen / Beijing · Expected 2027</span></div>
      </header>
      <section class="resume-section"><h2>Profile</h2><p style="font-size:.88rem;margin:0">M.Sc. candidate in Integrated Circuits and Systems at CUHK-Shenzhen. Engineering experience spans large C/C++ systems, a TensorFlow backend for a domestic GPU platform, quantized LLM runtimes, and MoE post-training/inference infrastructure on H200 clusters. Interested in training–inference consistency, GPU kernels, distributed inference, and reproducible performance engineering.</p></section>
      <section class="resume-section"><h2>Education</h2>
        <div class="resume-entry"><div class="resume-entry-head"><div><h3>The Chinese University of Hong Kong, Shenzhen</h3><span class="sub">M.Sc. in Integrated Circuits and Systems</span></div><span class="date">2025.09 — 2027.06 expected</span></div></div>
        <div class="resume-entry"><div class="resume-entry-head"><div><h3>Shandong University</h3><span class="sub">B.Eng. in Electronic Science and Technology · Minor in Computer Science</span></div><span class="date">2021.09 — 2025.06</span></div><ul><li>Academic scholarship (top 20%) and an innovation-oriented merit scholarship.</li></ul></div>
      </section>
      <section class="resume-section"><h2>Research</h2>
        <div class="resume-entry"><div class="resume-entry-head"><div><h3>From Structure to Preference: Token Weighting for Chain-of-Thought Distillation in Large Language Models</h3><span class="sub">Shankui Han, Zhaoyu Li, Weiwen Yuan, Yuyuan Yang, Haoran Feng, Jinke Ren</span></div><span class="date">AAAI 2027 · Under review</span></div><ul><li>Three-stage CoT distillation with structure recovery, intervention-based token weighting, and preference optimization. <a href="{OPENREVIEW}" target="_blank" rel="noreferrer">OpenReview ↗</a></li></ul></div>
      </section>
      <section class="resume-section"><h2>Experience</h2>
        <div class="resume-entry"><div class="resume-entry-head"><div><h3>LLM Post-training & Inference Infrastructure</h3><span class="sub">Company work · anonymized public summary</span></div><span class="date">2026.04 — Present</span></div><ul><li>Debugged a TP=2 FULL CUDA Graph rollout hang to FTZ/sentinel behavior in a fused collective path; completed minimal reproduction, bit-level patching, SASS verification, and model-level replay regression.</li><li>Built MoE route capture and Router Replay across rollout and training; in an 8×H200 controlled run, route mismatch fell from approximately 17–19% to 0, with large reductions in probability-drift metrics.</li><li>Maintained GPU-resident recent-token state for asynchronous decode and validated mixed batches, recovery, slot reuse, and TP1/TP2/TP4 correctness and throughput.</li></ul></div>
        <div class="resume-entry"><div class="resume-entry-head"><div><h3>Moore Threads · Operator & Compiler Optimization Intern</h3><span class="sub">TensorFlow MUSA Extension</span></div><span class="date">2026.01 — 2026.04</span></div><ul><li>Integrated muDNN GELU, repaired graph-fusion coverage, and built real-shape benchmarks; achieved 11/11 GELU fusion and approximately 36.6% improvement in the targeted shape benchmark.</li><li>Resolved long-run instability caused by host/device shape semantics and asynchronous metadata lifetimes.</li><li>Built kernel observability tooling and optimized a scalar-broadcast Logical_Or hot path from 21.2 μs to 10.7 μs.</li></ul></div>
        <div class="resume-entry"><div class="resume-entry-head"><div><h3>Huawei · General Software Engineering Intern</h3><span class="sub">Large C/C++ systems and static-analysis tooling</span></div><span class="date">2024.08 — 2024.12</span></div><ul><li>Improved static-analysis rules and built Python automation for rule generation, validation, and CI workflows.</li></ul></div>
      </section>
      <section class="resume-section"><h2>Open Source Contributions</h2>
        <div class="resume-entry"><div class="resume-entry-head"><div><h3>Mooncake Contributor</h3><span class="sub">Distributed KV Cache · RDMA · Storage</span></div><span class="date">2026.08</span></div><ul><li>Two merged reliability fixes: restoring fork state after RDMA memory-region deregistration and rebuilding stale endpoints/QPs after port recovery.</li></ul></div>
        <div class="resume-entry"><div class="resume-entry-head"><div><h3>Mirage Contributor</h3><span class="sub">Qwen3 inference correctness</span></div><span class="date">2026.08</span></div><ul><li>Merged <a href="{MIRAGE_PR}" target="_blank" rel="noreferrer">PR #755</a>, preventing padded lm_head rows from producing out-of-range token IDs during Argmax.</li></ul></div>
      </section>
      <section class="resume-section"><h2>Selected Projects</h2>
        <div class="resume-entry"><div class="resume-entry-head"><div><h3>LLMQRT Quantized Inference Runtime</h3><span class="sub">PyTorch Extension · CUTLASS · AWQ / INT8 / FP8</span></div><span class="date">Ongoing</span></div><ul><li>Lightweight runtime work across quantized linear layers, decode GEMV, attention backends, KV cache, and tensor parallelism.</li></ul></div>
        <div class="resume-entry"><div class="resume-entry-head"><div><h3>Semi-supervised Image Classification</h3><span class="sub">ResNet-18 · pseudo-labeling · augmentation</span></div><span class="date">2024</span></div><ul><li>Improved Top-1 accuracy from 51.8% to 85.1% and placed 7th in a <a href="{KAGGLE}" target="_blank" rel="noreferrer">Kaggle competition</a>.</li></ul></div>
      </section>
      <section class="resume-section"><h2>Technical Stack</h2><p style="font-size:.84rem;margin:0"><strong>Systems:</strong> veRL, Megatron-LM, vLLM, SGLang, TensorFlow, PyTorch extensions · <strong>GPU:</strong> CUDA, CUTLASS, CuTe, DeepGEMM, Nsight Systems/Compute, MUSA · <strong>Engineering:</strong> C++, Python, Linux, Docker, Git, benchmarking and ablation.</p></section>
    </article>
  </div>
</section>
"""
    return page(
        "resume.html",
        title="Résumé",
        description="Public English résumé of Haoran Feng, focused on AI infrastructure, LLM systems, and GPU performance.",
        page_key="resume",
        body=body,
        body_class="compact-site editorial-site",
    )


def roadmap_page() -> str:
    body = """
<section class="compact-page-head"><div class="shell"><span class="eyebrow">Now / Next / Later</span><div class="page-title-line"><h1>Technical roadmap</h1><p>A living view of current work rather than a list of vague long-term goals.</p></div></div></section>
<section class="dense-section section-line"><div class="shell"><div class="timeline-compact">
  <div><time>Now</time><strong>Consolidate public evidence</strong><span>Turn MoE-RL, CUDA Graph, asynchronous decode, and open-source debugging work into concise, verifiable case studies.</span></div>
  <div><time>Next</time><strong>Deepen GPU systems work</strong><span>Blackwell programming models, kernel portability, low-precision formats, profiling methodology, and compiler/runtime interaction.</span></div>
  <div><time>Later</time><strong>Contribute to production LLM infrastructure</strong><span>Inference engines, RL infrastructure, MoE systems, distributed storage, and open-source GPU kernels.</span></div>
</div></div></section>
"""
    return page(
        "roadmap.html",
        title="Roadmap",
        description="Current and planned technical directions of Haoran Feng.",
        page_key="roadmap",
        body=body,
    )


PROJECT_DETAILS: dict[str, dict] = {
    "mooncake-contributions.html": {
        "title": "Mooncake: RDMA and storage reliability contributions",
        "eyebrow": "Open Source · Distributed KV Cache · RDMA",
        "lead": "Independent upstream work on failure recovery and resource lifecycle in Mooncake's Transfer Engine and Store.",
        "metrics": [("2", "Merged upstream PRs"), ("RDMA", "Transfer Engine"), ("VMA / QP", "Failure modes"), ("Public", "Traceable evidence")],
        "sections": [
            ("Why it matters", "Distributed inference", "<p>Mooncake manages KV-cache movement and storage across memory, RDMA, SSD, and distributed services. Small lifecycle errors can surface as system-wide timeouts, silent degradation, or resource exhaustion.</p>"),
            ("PR #3660", "Restore fork state after memory unregister", "<p><code>ibv_reg_mr</code> marks registered ranges as <code>MADV_DONTFORK</code> after fork safety is initialized. The unregister path did not restore <code>MADV_DOFORK</code>, leaving VMAs permanently split under registration churn. The fix restores fork state after successful deregistration and avoids using MR metadata after deregistration.</p>"),
            ("PR #3604", "Rebuild stale endpoints after RDMA port recovery", "<p>When a port recovered, old QPs could remain in an error state inside the endpoint store. The fix evicts all stale endpoints on resume so the next access creates fresh endpoints and QPs.</p>"),
            ("Claim boundary", "Current public status", "<p class=\"boundary-note\">Two pull requests are merged. Additional Mooncake fixes may still be under review; their status should always be read from GitHub rather than inferred from this snapshot.</p>"),
        ],
        "external": "https://github.com/kvcache-ai/Mooncake/pulls?q=is%3Apr+author%3AXFDG",
    },
    "mirage-contribution.html": {
        "title": "Mirage: fixing out-of-range tokens caused by Argmax padding",
        "eyebrow": "Open Source · Qwen3 Inference · Correctness",
        "lead": "A small code change with a precise semantic failure chain: padded vocabulary rows could win Argmax and return invalid token IDs.",
        "metrics": [("#755", "Merged upstream PR"), ("9", "Qwen3 demo scripts"), ("2", "Related issues closed"), ("Correctness", "Valid token IDs")],
        "sections": [
            ("Root cause", "Padding meets Argmax", "<p>Qwen3 demos padded <code>lm_head</code> from the real vocabulary size of 151,936 to 153,600 rows using zeros. When all valid logits were negative, a padded row with logit 0 could win Argmax, producing <code>token_id &gt;= vocab_size</code>.</p>"),
            ("Fix", "Finite negative padding", "<p>The padding value was changed from <code>0</code> to <code>-1e4</code> in nine Qwen3 demo entry points. The value is finite and BF16-safe while staying far below realistic valid logits.</p>"),
            ("Verification", "Merged and approved", "<ul class=\"compact-list\"><li>Reproduced the failure on Qwen3-8B BF16 when valid logits were all negative.</li><li>Verified that Argmax returns IDs in <code>[0, vocab_size)</code> after the fix.</li><li>The upstream PR was approved, merged, and closed related issues #751 and #752.</li></ul>"),
            ("Claim boundary", "Value is in the diagnosis", "<p class=\"boundary-note\">The patch is intentionally small. Its engineering value lies in connecting padding semantics, logit distributions, the Argmax scan range, and invalid downstream token IDs.</p>"),
        ],
        "external": MIRAGE_PR,
    },
    "flashinfer-ftz.html": {
        "title": "FlashInfer CUDA Graph hang: FTZ and sentinel semantics",
        "eyebrow": "GPU Debugging · CUDA Graph · Collective Kernel",
        "lead": "Tracing a rollout RPC timeout backward to a fused GPU kernel and validating a bit-exact sentinel fix.",
        "metrics": [("TP=2", "FULL Graph reproduction"), ("8→0", "Target SASS predicates"), ("0/3→2/2", "Graph regression"), ("Bit-exact", "Sentinel check")],
        "sections": [
            ("Failure chain", "The timeout was not the root cause", "<p>The visible symptom was a <code>sample_tokens</code> RPC timeout during rollout. Controlled experiments across tensor parallelism, graph capture, fusion, and versions narrowed the first failure to a fused all-reduce plus RMSNorm path.</p>"),
            ("Root cause", "Flush-to-zero changed sentinel semantics", "<p>A Lamport-style <code>-0.0</code> sentinel relied on floating-point equality. Under FTZ behavior, the comparison could misclassify the sentinel and leave the graph replay waiting indefinitely. The repair used exact bit-pattern testing rather than arithmetic comparison.</p>"),
            ("Verification", "Minimal to model-level", "<ul class=\"compact-list\"><li>Two-GPU minimal reproduction.</li><li>Before/after SASS inspection of the target predicate.</li><li>Prompt-level and model-level CUDA Graph replay regression.</li></ul>"),
            ("Claim boundary", "Backport and validation", "<p class=\"boundary-note\">This page presents root-cause isolation, patch integration, and regression work. It does not claim original authorship of every upstream component involved in the final fix.</p>"),
        ],
        "external": "https://github.com/flashinfer-ai/flashinfer",
    },
    "router-replay.html": {
        "title": "R3 Router Replay for MoE training–rollout consistency",
        "eyebrow": "RL Infrastructure · MoE · Training–Inference Consistency",
        "lead": "Capturing rollout routes and replaying them during training to separate routing divergence from the rest of the post-training stack.",
        "metrics": [("17–19%→0", "Route mismatch"), ("36–145×", "Lower f_tau_2"), ("4–7×", "Lower KL"), ("8×H200", "Controlled run")],
        "sections": [
            ("Problem", "The same model can route differently", "<p>Rollout and training execute through different frameworks, kernels, precision paths, and graph modes. Small numerical differences around router boundaries can select different experts and amplify downstream probability drift.</p>"),
            ("Data contract", "Token × layer × top-k", "<p>The pipeline records routed-expert IDs on the rollout side, aligns them with response masks, observes the natural training route, and optionally replaces it with the recorded route during replay.</p>"),
            ("Experiment", "Baseline / record / replay", "<p>A controlled comparison separated ordinary execution, route recording, and route replay. Replay reduced route mismatch to zero and substantially reduced multiple log-probability drift metrics.</p>"),
            ("Claim boundary", "Consistency is not final quality", "<p class=\"boundary-note\">The evidence supports a stronger training–rollout consistency claim. It does not by itself prove higher reward, better downstream accuracy, or improved final convergence.</p>"),
        ],
        "external": "https://github.com/volcengine/verl",
    },
    "oe-async.html": {
        "title": "OE Async: GPU token history and fused hashing",
        "eyebrow": "Inference · Async Decode · Triton",
        "lead": "Keeping recent-token state on the GPU to remove synchronization and host round trips from an asynchronous decode path.",
        "metrics": [("+5.0%", "TP1 vs synchronous"), ("+4.6%", "TP2 decode"), ("+3.0%", "TP4 decode"), ("0", "State mismatches")],
        "sections": [
            ("Hot path", "Why host round trips were expensive", "<p>The original path copied recent tokens to the CPU, built a hash/input representation, and sent data back to the GPU. In decode, this imposed synchronization and transfer overhead on every step.</p>"),
            ("Design", "State lives with execution", "<p>Recent-token history remains GPU-resident. A Triton fused-hash path constructs the required input while explicit update rules handle mixed prefill/decode batches, request recovery, slot reuse, and reorder.</p>"),
            ("Validation", "State correctness before speed", "<p>Tests covered TP1, TP2, and TP4, including request lifecycle transitions rather than only steady-state microbenchmarks. The safe multi-rank path reported zero state mismatches.</p>"),
            ("Claim boundary", "Different paths by TP mode", "<p class=\"boundary-note\">The TP2/TP4 result uses the batch-invariant safe path. It should not be described as identical to the TP1 fused implementation.</p>"),
        ],
        "external": "https://github.com/triton-lang/triton",
    },
    "gemm-profiling.html": {
        "title": "H200 MoE Grouped GEMM profiling and tuning",
        "eyebrow": "GPU Performance · MoE · SM90",
        "lead": "The main lesson was methodological: define the real workload before searching for a faster kernel.",
        "metrics": [("4–6×", "Workload overcount corrected"), ("+5.3%", "Target shape"), ("+1.84%", "Full matrix aggregate"), ("≈66.5%", "Pure GEMM MFU")],
        "sections": [
            ("Workload definition", "Expanded rows are not compact rows", "<p>Mixing <code>T × top-k</code> expanded rows with DeepEP compact rows overstated work by roughly 4–6×. The corrected compact-row count changed both the benchmark distribution and the optimization target.</p>"),
            ("Replay", "Production shapes, local control", "<p>Steady-state forward ranges were collected, filtered, and replayed locally. This preserved representative shapes while making kernel configuration, warmup, and repeated A/B measurement controllable.</p>"),
            ("Tuning", "Configuration-level search", "<p>Candidate SM90 configurations varied tile shape, cluster shape, swizzle, and expert distribution. A selected target shape improved by about 5.3%, while the full shape/distribution matrix improved by about 1.84% in aggregate.</p>"),
            ("Claim boundary", "Microkernel is not end-to-end", "<p class=\"boundary-note\">Pure GEMM MFU and local latency do not equal end-to-end MoE or model throughput. Dispatch, communication, imbalance, launch overhead, and synchronization remain outside that metric.</p>"),
        ],
        "external": "https://github.com/deepseek-ai/DeepGEMM",
    },
    "deepgemm-offline.html": {
        "title": "DeepGEMM offline cubin and wheel delivery",
        "eyebrow": "Inference Delivery · JIT · Offline Runtime",
        "lead": "Converting runtime compilation artifacts into a complete, verifiable bundle for isolated production environments.",
        "metrics": [("109→359", "Bundled kernels"), ("0", "Cold compile in 8 models"), ("TP=2", "Representative coverage"), ("7.7×", "Precompiled load")],
        "sections": [
            ("Problem", "JIT and isolated environments do not mix", "<p>Runtime compilation can fail or add unpredictable startup cost in environments without compilers, network access, or writable caches.</p>"),
            ("Pipeline", "Collect, union, verify, package", "<p>Required shapes were collected from model execution, cubins were unioned and deduplicated, integrity metadata was generated, and the result was packaged into an offline-installable wheel/bundle.</p>"),
            ("Coverage", "Single-GPU and tensor parallel", "<p>Eight single-GPU model configurations and a representative TP=2 configuration loaded without cold compilation in the tested scope.</p>"),
            ("Claim boundary", "Startup result, not hot GEMM speed", "<p class=\"boundary-note\">The 7.7× figure refers to cold/precompiled loading behavior. It is not a claim that steady-state GEMM TFLOPS improved by 7.7×.</p>"),
        ],
        "external": "https://github.com/deepseek-ai/DeepGEMM",
    },
    "musa-extension.html": {
        "title": "TensorFlow MUSA Extension",
        "eyebrow": "Framework Backend · Heterogeneous Computing",
        "lead": "Internship work across TensorFlow operator semantics, graph rewriting, device kernels, stability, and performance observability on a domestic GPU platform.",
        "metrics": [("2026.01–04", "Internship"), ("11/11", "GELU fusion"), ("+36.6%", "Target shape benchmark"), ("21.2→10.7 μs", "Logical_Or")],
        "sections": [
            ("Framework chain", "More than a kernel", "<p>A device extension spans TensorFlow op definitions, placement, kernel registration, graph optimizer passes, runtime memory semantics, backend libraries, and correctness/performance tests.</p>"),
            ("GELU fusion", "From support to actual graph coverage", "<p>Integrated the backend GELU implementation, repaired fusion matching in larger graphs, and used real input shapes to verify that all 11 target GELU nodes were fused.</p>"),
            ("Stability", "Shape metadata and asynchronous lifetimes", "<p>Long-run failures were traced to host/device shape semantics and asynchronous pointer lifetimes rather than simply insufficient device memory.</p>"),
            ("Observability and hot paths", "Measure before optimizing", "<p>Built lightweight kernel timing/debug tooling and optimized a scalar-broadcast Logical_Or path from 21.2 μs to 10.7 μs.</p><p class=\"boundary-note\">Public MUSA PRs are evidence of internship work, not classified here as independent open-source activity.</p>"),
        ],
        "external": "https://github.com/MooreThreads/tensorflow_musa_extension",
    },
    "quant-runtime.html": {
        "title": "LLMQRT quantized inference runtime",
        "eyebrow": "Quantization · PyTorch Extension · CUDA",
        "lead": "An ongoing lightweight runtime used to understand quantized data formats, kernel dispatch, attention backends, KV cache, and multi-GPU execution as one system.",
        "metrics": [("W4A16", "AWQ path"), ("W8A8", "SmoothQuant path"), ("FP8", "Dynamic / static"), ("H200", "Validation platform")],
        "sections": [
            ("Scope", "Runtime rather than isolated kernels", "<p>The project connects model loading, quantization metadata, custom linear operators, attention backends, KV-cache management, and tensor parallelism.</p>"),
            ("Kernel paths", "Prefill and decode are different workloads", "<p>Prefill emphasizes matrix-matrix multiplication; decode often becomes GEMV-like and more sensitive to memory traffic, launch overhead, packing, and dequantization layout.</p>"),
            ("Formats", "AWQ, INT8, and FP8", "<p>Implemented or evaluated W4A16 AWQ, W8A8 SmoothQuant/CUTLASS paths, and dynamic/static FP8, with explicit attention to schema compatibility and scale layout.</p>"),
            ("Status", "Work in progress", "<p class=\"boundary-note\">The page describes architecture and validated paths. It avoids publishing performance claims that are not yet backed by a stable, comparable end-to-end benchmark matrix.</p>"),
        ],
        "external": GITHUB,
    },
    "drone-detection-pipeline.html": {
        "title": "Drone detection experiment pipeline",
        "eyebrow": "ML Systems · Data Engineering · Multi-GPU Experiments",
        "lead": "A recoverable experiment system for comparing detection models across heterogeneous datasets—not merely a single training run.",
        "metrics": [("171,568", "Unified samples"), ("3", "Source datasets"), ("18 days→10–20 min", "Video extraction"), ("14/14", "Smoke gates")],
        "sections": [
            ("Data engineering", "One task, incompatible sources", "<p>Three visible-light drone datasets arrived as VOC XML and video/XML combinations. They were normalized into YOLO and COCO representations with consistent class semantics and dataset splits.</p>"),
            ("Pipeline acceleration", "Batch the expensive boundary", "<p>The original ARD-MAV process invoked ffmpeg frame by frame and was projected to take about 18 days. Exporting all frames once per video reduced the process to roughly 10–20 minutes.</p>"),
            ("Experiment operations", "Make failures recoverable", "<p>The system included environment checks, small-subset smoke tests, multi-GPU scheduling, manifests, checkpoint reuse, three-seed tracking, and lightweight result aggregation.</p>"),
            ("Claim boundary", "Design versus completed runs", "<p class=\"boundary-note\">The complete design covered six model families and three seeds. The strongest fully completed core comparison included RT-DETR-L and Faster R-CNN across three seeds each; other model results are reported separately with their own stability caveats.</p>"),
        ],
        "external": KAGGLE,
    },
}


def project_page(filename: str, cfg: dict) -> str:
    metrics = "".join(f"<div><strong>{v}</strong><span>{label}</span></div>" for v, label in cfg["metrics"])
    sections = "".join(
        f'<section class="dense-section section-line"><div class="shell detail-narrow">'
        f'<div class="dense-heading"><h2>{heading}</h2><span>{subtitle}</span></div>{content}</div></section>'
        for heading, subtitle, content in cfg["sections"]
    )
    body = f"""
<section class="compact-page-head">
  <div class="shell">
    <div class="detail-breadcrumbs"><a href="../projects.html">Projects</a><span>/</span><span>{cfg["title"]}</span></div>
    <span class="eyebrow">{cfg["eyebrow"]}</span>
    <div class="page-title-line"><h1>{cfg["title"]}</h1><p>{cfg["lead"]}</p></div>
    <div class="metric-strip detail-strip">{metrics}</div>
  </div>
</section>
{sections}
<section class="dense-section section-line"><div class="shell detail-narrow"><div class="button-row"><a class="button primary" href="{cfg["external"]}" target="_blank" rel="noreferrer">Public source ↗</a><a class="button" href="../projects.html">All projects</a></div></div></section>
"""
    return page(
        f"projects/{filename}",
        title=cfg["title"],
        description=cfg["lead"],
        page_key="projects",
        body=body,
    )


def not_found_page() -> str:
    body = """
<section class="compact-page-head"><div class="shell"><span class="eyebrow">404</span><div class="page-title-line"><h1>Page not found</h1><p>The page may have moved, or the address may be incomplete.</p></div><div class="button-row"><a class="button primary" href="index.html">Back home</a><a class="button" href="projects.html">View projects</a></div></div></section>
"""
    return page(
        "404.html",
        title="Page not found",
        description="Page not found on Haoran Feng's personal website.",
        page_key="",
        body=body,
    )


def inject_chinese_alternates() -> None:
    paths = [Path(p) for p in OUTPUTS]
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        text = re.sub(r'\s*<link[^>]+rel=["\']alternate["\'][^>]*>\s*', "\n", text, flags=re.I)
        rel = str(path).replace("\\", "/")
        en_href = output_url(rel)
        zh_href = zh_url(rel)
        block = (
            f'  <link rel="alternate" hreflang="zh-CN" href="{zh_href}">\n'
            f'  <link rel="alternate" hreflang="en" href="{en_href}">\n'
            f'  <link rel="alternate" hreflang="x-default" href="{zh_href}">\n'
        )
        if "</head>" not in text:
            raise RuntimeError(f"missing </head>: {path}")
        text = text.replace("</head>", block + "</head>", 1)
        path.write_text(text, encoding="utf-8")


def update_script() -> None:
    path = ROOT / "script.js"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "button.textContent = '邮箱已复制';",
        "button.textContent = document.documentElement.lang.startsWith('en') ? 'Copied' : '邮箱已复制';",
    )
    marker = "/* bilingual-language-switch */"
    if marker not in text:
        text += r'''

// bilingual-language-switch
(() => {
  const path = window.location.pathname || '/';
  const isEnglish = path === '/en' || path.startsWith('/en/');
  if (isEnglish) document.documentElement.lang = 'en';

  const normalized = path.replace(/\/index\.html$/, '/');
  let counterpart;
  if (isEnglish) {
    counterpart = normalized.replace(/^\/en/, '') || '/';
    if (!counterpart.startsWith('/')) counterpart = `/${counterpart}`;
  } else {
    counterpart = normalized === '/' ? '/en/' : `/en${normalized}`;
  }

  const nav = document.querySelector('.site-nav');
  if (!nav || nav.querySelector('.language-switch')) return;

  const switcher = document.createElement('span');
  switcher.className = 'language-switch';
  switcher.setAttribute('aria-label', isEnglish ? 'Language' : '语言');

  const zh = document.createElement('a');
  zh.href = isEnglish ? counterpart : normalized;
  zh.textContent = '中';
  zh.lang = 'zh-CN';
  zh.classList.toggle('is-active', !isEnglish);
  zh.setAttribute('aria-current', !isEnglish ? 'page' : 'false');

  const divider = document.createElement('span');
  divider.className = 'language-divider';
  divider.textContent = '/';

  const en = document.createElement('a');
  en.href = isEnglish ? normalized : counterpart;
  en.textContent = 'EN';
  en.lang = 'en';
  en.classList.toggle('is-active', isEnglish);
  en.setAttribute('aria-current', isEnglish ? 'page' : 'false');

  zh.addEventListener('click', () => localStorage.setItem('site-language', 'zh-CN'));
  en.addEventListener('click', () => localStorage.setItem('site-language', 'en'));

  switcher.append(zh, divider, en);
  nav.appendChild(switcher);
})();
'''
    path.write_text(text, encoding="utf-8")


def update_styles() -> None:
    path = ROOT / "styles.css"
    text = path.read_text(encoding="utf-8")
    marker = "/* bilingual-language-switch */"
    if marker not in text:
        text += r'''

/* bilingual-language-switch */
.language-switch {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-left: 2px;
  padding-left: 18px;
  border-left: 1px solid var(--rule);
  white-space: nowrap;
}
.site-nav .language-switch a {
  padding: 0;
  color: var(--faint);
  font-family: var(--mono);
  font-size: .65rem;
  letter-spacing: .04em;
}
.site-nav .language-switch a::after { display: none; }
.site-nav .language-switch a:hover { color: var(--ink); }
.site-nav .language-switch a.is-active {
  color: var(--ink);
  font-weight: 650;
  pointer-events: none;
}
.language-divider {
  color: var(--rule-strong);
  font-family: var(--mono);
  font-size: .62rem;
}
@media (max-width: 900px) {
  .language-switch {
    width: 100%;
    margin: 8px 0 0;
    padding: 14px 0 2px;
    border-top: 1px solid var(--rule);
    border-left: 0;
  }
}
'''
    path.write_text(text, encoding="utf-8")


def update_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    urls = [output_url(p) for p in OUTPUTS if p != "404.html"]
    for url in urls:
        if url not in text:
            text = text.replace("</urlset>", f"  <url><loc>{url}</loc></url>\n</urlset>")
    path.write_text(text, encoding="utf-8")


def validate() -> None:
    required = [ROOT / "en" / p for p in OUTPUTS]
    missing_files = [str(p) for p in required if not p.exists()]
    if missing_files:
        raise RuntimeError("Missing generated pages:\n" + "\n".join(missing_files))

    for p in required:
        text = p.read_text(encoding="utf-8")
        if '<html lang="en">' not in text:
            raise RuntimeError(f"English lang missing: {p}")
        if 'hreflang="zh-CN"' not in text or 'hreflang="en"' not in text:
            raise RuntimeError(f"hreflang missing: {p}")

    index = (ROOT / "en/index.html").read_text(encoding="utf-8")
    assert "M.Sc. candidate at CUHK-Shenzhen" in index
    assert "Mooncake · Mirage" in index
    assert "Merged upstream PRs" in index
    assert "projects/mirage-contribution.html" in index

    missing_links: list[str] = []
    href_re = re.compile(r'(?:href|src)=["\']([^"\']+)["\']')
    for html_path in required:
        text = html_path.read_text(encoding="utf-8")
        ids = re.findall(r'\sid=["\']([^"\']+)["\']', text)
        if len(ids) != len(set(ids)):
            raise RuntimeError(f"duplicate id: {html_path}")
        for target in href_re.findall(text):
            if target.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                continue
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            candidate = (html_path.parent / parsed.path).resolve()
            if parsed.path.endswith("/"):
                candidate /= "index.html"
            if not candidate.exists():
                missing_links.append(f"{html_path}: {target}")
    if missing_links:
        raise RuntimeError("Broken internal links:\n" + "\n".join(missing_links))


def main() -> None:
    out = ROOT / "en"
    (out / "projects").mkdir(parents=True, exist_ok=True)

    pages = {
        "index.html": home_page(),
        "projects.html": projects_page(),
        "experience.html": experience_page(),
        "research.html": research_page(),
        "writing.html": writing_page(),
        "contact.html": contact_page(),
        "resume.html": resume_page(),
        "roadmap.html": roadmap_page(),
        "404.html": not_found_page(),
    }
    for filename, cfg in PROJECT_DETAILS.items():
        pages[f"projects/{filename}"] = project_page(filename, cfg)

    for rel, content in pages.items():
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    inject_chinese_alternates()
    update_script()
    update_styles()
    update_sitemap()
    validate()
    print(f"Generated {len(pages)} English pages and bilingual navigation.")


if __name__ == "__main__":
    main()
