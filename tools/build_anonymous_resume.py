"""Build standalone, identifier-free sharing copies from reviewed resume content."""
from __future__ import annotations
import json
from html import escape
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

ROOT = Path(__file__).resolve().parents[1]
CONTENT = {
 'zh': [
  [('教育背景', [
    ('工科硕士在读 | 2025.09 - 2027.06（预计）', '集成电路与系统。'),
    ('工学本科 | 2021.09 - 2025.06', '电子科学与技术；计算机科学与技术辅修。获学业及竞赛创新奖学金。')]),
   ('实习经历', [
    ('基础模型研发团队 | 大模型与高性能计算 | 2026.04 - 至今', '参与 MoE 模型训练、推理与 RL rollout 基础设施开发，负责算子优化、确定性验证与稳定性排障。'),
    ('确定性 Attention 反向优化', '定位长序列滑窗反向传播的同步依赖并调整调度。代表工作负载完整 backward 加速 3.98 倍；通过 3,601 项回归及 1,000 次逐位确定性测试，完成 wheel 交付。'),
    ('计算与通信协同', '搭建多 GPU 双 stream 代理，联合调整通信并行度与计算资源预算。AllGatherV 代理联合耗时降低 12.80%；固定通信设置下，控核独立贡献 7.58%。'),
    ('确定性 MoE Router GEMM', '接入 DeepGEMM / Triton Full-K / persistent 三级后端与 Graph preflight、cache、fallback。代表工作负载 Router 耗时降低 73.39%；135/135 kernel、20/20 模型场景逐位一致。async OE + prefix-cache hit 下，TP1/TP2 整请求吞吐提升 3.81%/4.36%。'),
    ('异步 GPU 状态管理', '历史 token 状态保留在 GPU，优化计算并修复请求恢复、slot 复用等跨 step 状态。TP1 通过 28/28 case，吞吐提升 4.99%；TP2/TP4 安全路径各通过 84/84 case，0 mismatch。'),
    ('MoE 训推路由一致性', '打通 rollout 路由采集、传输与训练侧回放，建立 mask 对齐及概率漂移监控。短程对照中执行路由不一致率由 17%-19% 降至 0；完成更大规模多卡 rollout 验证。'),
    ('CUDA Graph 稳定性', '构建两卡最小复现，定位浮点 FTZ 对同步标记的误判；回移上游位级判断修复，完成模型级回归。')])],
  [('实习经历（续）', [
    ('国产 GPU 企业 | 算子与编译器优化 | 2026.01 - 2026.04', '参与深度学习框架后端的算子、优化器适配、图融合、性能分析与长跑稳定性修复。'),
    ('图融合与热点算子', '完成整网 GELU 融合；真实 shape 测试耗时降低 36.6%。Logical_Or 从 21.2 us 降至 10.7 us，补齐优化器实现及测试。'),
    ('长跑稳定性', '定位 shape tensor 的 host/device 路径错误，修复资源变量与 session 关闭问题。测试由 500 轮约 30% 成功率提升至 1,000 轮 100%，通过最高 80 万轮长跑。')]),
   ('项目与研究', [
    ('量化推理 Runtime | 2025.12 - 至今', '基于 PyTorch Extension 完成 W4A16 / W8A8 / FP8 后端、Attention 与 TP=2 集成。使用 Compute Sanitizer 修复尾组越界，代表 shape 四类检查均为 0 error / 0 hazard。'),
    ('双卡量化部署', '在公开 32B 模型的对照部署中，checkpoint / 峰值显存降低 70.5% / 66.8%，端到端输出吞吐提升 76.8%；通过数值及跨 rank token 一致性验收。'),
    ('关键 Token 加权思维链蒸馏 | 已投稿', '参与结构恢复、关键 token 加权监督与偏好优化框架；负责模型训练、超参调优、LoRA / DPO 及多卡评测。')]),
   ('开源与技能', [
    ('上游贡献', '{total} 个已合入 PR，其中 {community} 个社区贡献、{internship} 个实习产出；覆盖训练、推理、分布式存储及框架后端。'),
    ('开发与性能工程', 'C/C++、Python、CUDA、Triton、PyTorch Extension；Nsight Systems、Nsight Compute、Compute Sanitizer。'),
    ('语言与证书', 'IELTS 6.5、CET-6、HCIA-AI。')])]
 ],
 'en': [
  [('Education', [
    ('M.Sc. candidate | Sep 2025 - Jun 2027 (expected)', 'Integrated Circuits and Systems.'),
    ('B.Eng. | Sep 2021 - Jun 2025', 'Electronic Science and Technology; minor in Computer Science. Academic and competition/innovation scholarships.')]),
   ('Experience', [
    ('Foundation-model team | LLM and HPC intern | Apr 2026 - Present', 'Training, inference and RL rollout infrastructure for MoE models: kernel optimization, determinism validation and stability debugging.'),
    ('Deterministic attention backward', 'Diagnosed synchronization dependencies in long-context sliding-window backward and revised scheduling. Representative full-backward speedup: 3.98x; 3,601 regressions and 1,000 repeated bitwise checks; delivered a wheel.'),
    ('Compute-communication coordination', 'Built a multi-GPU dual-stream proxy and co-tuned communication and compute budgets. AllGatherV proxy joint latency fell 12.80%; isolated compute-budget gain at fixed communication settings: 7.58%.'),
    ('Deterministic MoE router GEMM', 'Integrated DeepGEMM / Triton Full-K / persistent backends, Graph preflight and fallback. Router latency fell 73.39% on the tested workload; 135/135 kernel and 20/20 model cases matched bitwise. Full-request throughput with async OE and prefix-cache hits: TP1 +3.81%, TP2 +4.36%.'),
    ('Asynchronous GPU state', 'Kept token history on the GPU and fixed cross-step recovery and slot reuse. TP1: 28/28 cases, +4.99% throughput. TP2/TP4 safe paths: 84/84 each, zero mismatches.'),
    ('Training-rollout consistency', 'Connected route capture, transport and replay, response masks and drift metrics. Executed-route mismatch fell from 17%-19% to zero in a short controlled run; completed larger multi-GPU rollout validation.'),
    ('CUDA Graph stability', 'Isolated FTZ-sensitive synchronization sentinel handling with a two-GPU reproducer; backported an upstream bitwise fix and completed model-level regression.')])],
  [('Experience (continued)', [
    ('GPU company | Operator/compiler optimization intern | Jan - Apr 2026', 'Deep-learning framework backend: operators, optimizers, graph fusion, profiling and long-run stability.'),
    ('Fusion and hot operators', 'Completed GELU fusion across the tested graph; workload-shaped latency fell 36.6%. Logical_Or improved from 21.2 us to 10.7 us; added optimizer implementations and tests.'),
    ('Long-run reliability', 'Fixed host/device shape-tensor semantics, resource-variable updates and session shutdown. Success improved from about 30% over 500 iterations to 100% over 1,000; validated runs up to 800,000 iterations.')]),
   ('Projects and research', [
    ('Quantized inference runtime | Dec 2025 - Present', 'Integrated W4A16 / W8A8 / FP8 backends, attention and TP=2 through PyTorch Extension. Fixed tail-group memory errors; four Compute Sanitizer checks showed zero errors/hazards on representative shapes.'),
    ('Two-GPU quantized deployment', 'In a paired deployment of a public 32B model, checkpoint / peak memory fell 70.5% / 66.8% and output throughput rose 76.8%; numerical and cross-rank token checks passed.'),
    ('Token-weighted CoT distillation | Submitted', 'Contributed to structure recovery, token-weighted supervision and preference optimization. Owned training, hyperparameter tuning, LoRA / DPO and multi-GPU evaluation.')]),
   ('Open source and skills', [
    ('Upstream contributions', '{total} merged PRs: {community} community contributions and {internship} internship outputs, spanning training, inference, distributed storage and framework backends.'),
    ('Engineering', 'C/C++, Python, CUDA, Triton, PyTorch Extension; Nsight Systems, Nsight Compute and Compute Sanitizer.'),
    ('Language and certification', 'IELTS 6.5; CET-6; HCIA-AI.')])]
 ]
}
CSS = '''*{box-sizing:border-box}body{font-family:Arial,"Noto Sans CJK SC","Microsoft YaHei",sans-serif;margin:0;background:#eee;color:#171717;line-height:1.6}.page{width:210mm;min-height:297mm;margin:24px auto;padding:15mm 17mm;background:#fff}h1{font-size:25px;margin:0 0 4px}h2{font-size:15px;border-bottom:1px solid #bbb;padding-bottom:4px;margin:17px 0 8px}h3{font-size:12px;margin:10px 0 3px}p{font-size:11.6px;margin:0 0 6px}.meta{font-size:11px;color:#666}.controls{margin:18px auto;max-width:210mm;padding:0 15px}button{padding:8px 16px;background:white;border:1px solid #aaa;cursor:pointer}a{color:inherit}.pdf-link{margin-left:16px}@page{size:A4;margin:0}@media print{body{background:white}.controls{display:none}.page{margin:0;break-after:page}.page:last-child{break-after:auto}}@media(max-width:800px){.page{width:auto;min-height:0;margin:0;padding:22px}.controls{margin:12px 0}}'''


def main() -> None:
    status = json.loads((ROOT/'content/portfolio_status.json').read_text(encoding='utf-8'))
    groups = status['groups']
    counts = {'total':sum(len(g['prs']) for g in groups), 'community':sum(len(g['prs']) for g in groups if g['category']=='community'), 'internship':sum(len(g['prs']) for g in groups if g['category']=='internship')}
    assets=ROOT/'assets/resume'; assets.mkdir(parents=True,exist_ok=True)
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    for lang,pages in CONTENT.items():
        title='AI Infra | 技术简历' if lang=='zh' else 'AI Infrastructure | Resume'
        subtitle='匿名分享版 · 大模型系统与 GPU 性能工程' if lang=='zh' else 'Anonymous sharing copy | LLM systems and GPU performance'
        font='STSong-Light' if lang=='zh' else 'Helvetica'
        styles={key:ParagraphStyle(key,fontName=font,fontSize=size,leading=leading,spaceAfter=after,textColor=colors.HexColor('#171717'),wordWrap='CJK' if lang=='zh' else None) for key,size,leading,after in [('title',22,29,6),('meta',9,14,10),('section',12,18,7),('heading',10.3,15,3),('body',9.5,14.4,8)]}
        story=[]; html_pages=[]; md=[]
        for idx,sections in enumerate(pages):
            if idx: story.append(PageBreak())
            story += [Paragraph(escape(title),styles['title']),Paragraph(escape(subtitle),styles['meta'])]
            parts=[f'<h1>{escape(title)}</h1><p class="meta">{escape(subtitle)}</p>']
            for heading,items in sections:
                story.extend([Spacer(1,6),Paragraph(escape(heading),styles['section'])]); parts.append(f'<h2>{escape(heading)}</h2>'); md.append('## '+heading)
                for label,text in items:
                    text=text.format(**counts)
                    story.extend([Paragraph(escape(label),styles['heading']),Paragraph(escape(text),styles['body'])])
                    parts.append(f'<h3>{escape(label)}</h3><p>{escape(text)}</p>'); md.extend(['### '+label,text,''])
            html_pages.append('<section class="page">'+''.join(parts)+'</section>')
        out=assets/f'anonymous-{lang}.pdf'
        doc=SimpleDocTemplate(str(out),pagesize=A4,leftMargin=45,rightMargin=45,topMargin=36,bottomMargin=32,title='AI Infrastructure Resume - Anonymous',author='',subject='Anonymous technical resume',creator='Resume generator',invariant=1)
        def footer(canvas, document):
            canvas.setFont('Helvetica',8); canvas.setFillColor(colors.HexColor('#777777')); canvas.drawRightString(A4[0]-45,19,str(document.page))
        doc.build(story,onFirstPage=footer,onLaterPages=footer)
        controls='打印 / 保存 PDF' if lang=='zh' else 'Print / save PDF'
        download='下载匿名 PDF' if lang=='zh' else 'Download anonymous PDF'
        html=f'<!doctype html><html lang="{"zh-CN" if lang=="zh" else "en"}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{escape(title)}</title><style>{CSS}</style></head><body><div class="controls"><button onclick="window.print()">{controls}</button><a class="pdf-link" href="{"../" if lang=="en" else ""}assets/resume/anonymous-{lang}.pdf" download="ai-infra-resume-anonymous-{lang}.pdf">{download}</a></div>'+''.join(html_pages)+'</body></html>'
        forbidden=['冯浩然','Haoran Feng','XFDG','@','IQuest','九坤','至知','Moore','摩尔','山东大学','中文大学','openreview','github.com']
        text='\n'.join(md)
        assert not any(t in text for t in forbidden), 'Identifier leaked into anonymous copy'
        target=ROOT/('en/anonymous-resume.html' if lang=='en' else 'anonymous-resume.html'); target.parent.mkdir(exist_ok=True)
        target.write_text(html,encoding='utf-8'); (assets/f'anonymous-{lang}.md').write_text('# '+title+'\n\n'+text,encoding='utf-8')
    print('Built standalone Chinese/English anonymous HTML, PDF and Markdown')

if __name__=='__main__': main()
