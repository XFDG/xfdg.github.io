"""Render verified research additions after build_portfolio.py, before build_blog.py.

Public source: https://arxiv.org/abs/2610.30949 (checked 2026-10-28).
The author list includes Haoran Feng; the report was first posted 2026-10-22.
No public OpenReview submission/ratings were found. Do not invent a venue.
Anonymous resume files are intentionally untouched.
"""
from __future__ import annotations

import re
from html import escape
from pathlib import Path

import build_portfolio as base

ROOT = Path(__file__).resolve().parents[1]
TITLE = 'IQuest-Q1: Advancing Foundation Capabilities for Agentic CLI Systems'
ARXIV = 'https://arxiv.org/abs/2610.30949'
START = '<!-- iquest-q1-report:start -->'
END = '<!-- iquest-q1-report:end -->'
IDENT = 'iquest-q1-report'
PAGES = ('index.html', 'experience.html', 'writing.html', 'resume.html')


def choose(zh: str, en: str, lang: str) -> str:
    return zh if lang == 'zh' else en


def card(lang: str, detailed: bool = False, full_title: bool = False) -> str:
    status = choose('arXiv · 技术报告', 'arXiv · Technical report', lang)
    title = TITLE if detailed or full_title else 'IQuest-Q1'
    href = ARXIV if detailed or full_title else base.local('research.html', lang) + '#' + IDENT
    heading = base.link(href, escape(title), detailed or full_title)
    author = choose('合作者', 'Co-author', lang)
    text = (
        START + f'<article id="{IDENT}" style="margin-bottom:28px">'
        f'<div class="publication-state">{status} · <time datetime="2026-10-22">2026-10-22</time></div>'
        f'<div class="paper-title">{heading}</div>'
        f'<p class="paper-meta"><strong>Haoran Feng</strong> · {author}</p>'
    )
    if detailed:
        text += base.para(choose(
            'IQuest Research 的 320B-A15B MoE 基础模型技术报告，介绍预训练、中期训练与面向 CLI 智能体的后训练。',
            'The IQuest Research technical report for a 320B-A15B MoE foundation model, covering pre-training, mid-training and post-training for CLI agents.', lang))
        text += base.para(choose(
            '参与模型训练、推理与 RL rollout 基础设施开发，围绕算子性能、训推一致性和多卡稳定性开展工程实践。',
            'Contributed to training, inference and RL rollout infrastructure, focusing on kernel performance, training–rollout consistency and multi-GPU stability.', lang))
        text += '<div class="quick-links">' + base.link(ARXIV, 'arXiv ↗')
        text += base.link('https://arxiv.org/pdf/2610.30949', 'PDF ↗')
        text += base.ilink('projects/iquest-q1.html', choose('工程项目 →', 'Engineering work →', lang), lang)
        text += base.link(base.MODEL, 'GitHub ↗') + '</div>'
    return text + '</article>' + END


def remove_managed(text: str) -> str:
    return re.sub(re.escape(START) + r'.*?' + re.escape(END), '', text, flags=re.S)


def update_summaries(lang: str) -> None:
    prefix = 'en/' if lang == 'en' else ''
    anchor = '<div class="publication-state">AAAI 2027'
    for name in PAGES:
        path = ROOT / (prefix + name)
        text = remove_managed(path.read_text(encoding='utf-8'))
        if text.count(anchor) != 1:
            raise ValueError(f'{path}: expected one existing CoT publication anchor')
        text = text.replace(anchor, card(lang, full_title=name == 'resume.html') + anchor, 1)
        path.write_text(text, encoding='utf-8')


def research_page(lang: str) -> None:
    title = choose('研究', 'Research', lang)
    lead = choose('基础模型技术报告与思维链蒸馏研究。', 'Foundation model reports and chain-of-thought distillation.', lang)
    body = base.head(title, lead, lang, 'Research')
    body += base.section(choose('技术报告', 'Technical report', lang), card(lang, detailed=True), reading=True)
    body += base.section(choose('在投稿件', 'Submitted manuscript', lang), base.research(lang), reading=True)
    base.write_page('research.html', title, lead, body, lang, 'research')


def project_link(lang: str) -> None:
    path = ROOT / (('en/' if lang == 'en' else '') + 'projects/iquest-q1.html')
    text = path.read_text(encoding='utf-8')
    marker = 'data-iquest-report="true"'
    text = re.sub(r'<a\b[^>]*data-iquest-report="true"[^>]*>.*?</a>', '', text, flags=re.S)
    label = choose('技术报告 · 合作者 ↗', 'Technical report · Co-author ↗', lang)
    addition = f'<a {marker} href="{ARXIV}" target="_blank" rel="noopener noreferrer">{label}</a>'
    text, count = re.subn(r'(<div class="quick-links">)(.*?)(</div>)', lambda m: m[1] + m[2] + addition + m[3], text, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f'{path}: missing project resource links')
    path.write_text(text, encoding='utf-8')


def check() -> None:
    for lang in ('zh', 'en'):
        prefix = 'en/' if lang == 'en' else ''
        for name in (*PAGES, 'research.html'):
            text = (ROOT / (prefix + name)).read_text(encoding='utf-8')
            assert text.count(f'id="{IDENT}"') == 1, (prefix, name)
            assert '2026-10-22' in text and 'Haoran Feng' in text, (prefix, name)
            assert base.PAPER_TITLE in text, 'Existing CoT manuscript must be preserved'
        research = (ROOT / (prefix + 'research.html')).read_text(encoding='utf-8')
        assert TITLE in research and ARXIV in research
        project = (ROOT / (prefix + 'projects/iquest-q1.html')).read_text(encoding='utf-8')
        assert project.count('data-iquest-report="true"') == 1
        assert 'Scope of results' not in project and '结果范围' not in project
    print('PASS: IQuest-Q1 report, co-authorship, dates, links and both languages')


def main() -> None:
    for lang in ('zh', 'en'):
        update_summaries(lang)
        research_page(lang)
        project_link(lang)
    check()


if __name__ == '__main__':
    main()
