(() => {
  'use strict';
  document.documentElement.style.colorScheme = 'light';
  // Preserve design-token compatibility for existing archival project pages.
  const tokens = {'--bg':'var(--paper)','--bg-soft':'var(--paper-2)','--surface':'transparent','--surface-solid':'var(--paper)','--surface-2':'var(--paper-2)','--text':'var(--ink)','--text-soft':'var(--ink-soft)','--line':'var(--rule)','--line-strong':'var(--rule-strong)','--accent-strong':'var(--accent)','--accent-2':'var(--accent)','--shadow':'none','--radius-sm':'0px','--radius':'0px','--radius-lg':'0px'};
  Object.entries(tokens).forEach(([key,value]) => document.documentElement.style.setProperty(key,value));
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content','#f4f2ed');
  document.querySelectorAll('.brand-copy small').forEach(node => { node.textContent = 'AI Infrastructure'; });
  const nav = document.querySelector('.site-nav');
  const toggle = document.querySelector('.menu-toggle');
  const closeMenu = () => { toggle?.setAttribute('aria-expanded','false'); nav?.classList.remove('open'); };
  toggle?.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded',String(open));
    nav?.classList.toggle('open',open);
  });
  document.addEventListener('keydown', event => { if (event.key === 'Escape') closeMenu(); });
  if (nav) {
    const links = new Map(Array.from(nav.querySelectorAll('a[data-nav]'), link => [link.dataset.nav,link]));
    nav.querySelectorAll('a[data-nav="roadmap"]').forEach(link => link.remove());
    ['home','projects','experience','writing','contact','resume'].forEach(key => {
      const link = links.get(key);
      if (link?.isConnected) nav.appendChild(link);
    });
    const english = /^\/en(?:\/|$)/.test(location.pathname);
    let switcher = nav.querySelector('.language-switch');
    if (!switcher) {
      switcher = document.createElement('span');
      switcher.className = 'language-switch';
      switcher.setAttribute('aria-label','Language');
      switcher.innerHTML = '<a lang="zh-CN">中</a><span class="language-divider" aria-hidden="true">/</span><a lang="en">EN</a>';
    }
    nav.appendChild(switcher);
    const normalized = location.pathname.replace(/\/index\.html$/, '/');
    const zhPath = english ? (normalized.replace(/^\/en/, '') || '/') : normalized;
    const suffix = location.search + location.hash;
    const alternatives = switcher.querySelectorAll('a');
    alternatives.forEach((link,index) => {
      const isEn = index === 1;
      link.href = (isEn ? '/en' + (zhPath.startsWith('/') ? zhPath : '/' + zhPath) : zhPath) + suffix;
      link.lang = isEn ? 'en' : 'zh-CN';
      link.classList.toggle('is-active',isEn === english);
      if (isEn === english) link.setAttribute('aria-current','page'); else link.removeAttribute('aria-current');
      link.addEventListener('click',() => {
        try { localStorage.setItem('site-language',isEn ? 'en' : 'zh-CN'); } catch (_) { /* Storage may be disabled. */ }
      });
    });
    nav.querySelectorAll('a').forEach(link => link.addEventListener('click',closeMenu));
    const active = links.get(document.body.dataset.page);
    active?.classList.add('active');
  }
  const header = document.querySelector('.site-header');
  const onScroll = () => header?.classList.toggle('is-scrolled',scrollY > 8);
  onScroll();
  window.addEventListener('scroll',onScroll,{passive:true});
  document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'));
  document.querySelectorAll('[data-year]').forEach(el => { el.textContent = String(new Date().getFullYear()); });
  document.querySelectorAll('[data-copy-email]').forEach(button => {
    button.addEventListener('click',async () => {
      const original = button.textContent;
      try {
        await navigator.clipboard.writeText(button.dataset.copyEmail);
        button.textContent = document.documentElement.lang.startsWith('en') ? 'Copied' : '已复制';
        setTimeout(() => { button.textContent = original; },1600);
      } catch (_) { location.href = 'mailto:' + button.dataset.copyEmail; }
    });
  });
  const filters = document.querySelectorAll('[data-filter]');
  filters.forEach(button => button.addEventListener('click',() => {
    filters.forEach(item => item.classList.toggle('active',item === button));
    document.querySelectorAll('[data-category]').forEach(item => {
      item.hidden = button.dataset.filter !== 'all' && !(item.dataset.category || '').split(' ').includes(button.dataset.filter);
    });
  }));
})();
