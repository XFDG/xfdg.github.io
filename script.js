(() => {
  document.documentElement.style.colorScheme = 'light';
  const rootStyle = document.documentElement.style;
  const legacyTokens = {
    '--bg': 'var(--paper)',
    '--bg-soft': 'var(--paper-2)',
    '--surface': 'transparent',
    '--surface-solid': 'var(--paper)',
    '--surface-2': 'var(--paper-2)',
    '--text': 'var(--ink)',
    '--text-soft': 'var(--ink-soft)',
    '--line': 'var(--rule)',
    '--line-strong': 'var(--rule-strong)',
    '--accent-strong': 'var(--accent)',
    '--accent-2': 'var(--accent)',
    '--shadow': 'none',
    '--radius-sm': '0px',
    '--radius': '0px',
    '--radius-lg': '0px'
  };
  Object.entries(legacyTokens).forEach(([name, value]) => rootStyle.setProperty(name, value));

  const themeMeta = document.querySelector('meta[name="theme-color"]');
  if (themeMeta) themeMeta.setAttribute('content', '#f4f2ed');

  const header = document.querySelector('.site-header');
  const menuToggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.site-nav');
  const page = document.body.dataset.page;

  const updateHeader = () => {
    header?.classList.toggle('is-scrolled', window.scrollY > 8);
  };

  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });

  if (menuToggle && nav) {
    menuToggle.addEventListener('click', () => {
      const open = menuToggle.getAttribute('aria-expanded') === 'true';
      menuToggle.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('open', !open);
    });

    nav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        menuToggle.setAttribute('aria-expanded', 'false');
        nav.classList.remove('open');
      });
    });
  }

  if (page) {
    document.querySelectorAll(`[data-nav="${page}"]`).forEach((item) => item.classList.add('active'));
  }

  document.querySelectorAll('.reveal').forEach((element) => element.classList.add('visible'));

  document.querySelectorAll('[data-year]').forEach((element) => {
    element.textContent = String(new Date().getFullYear());
  });

  document.querySelectorAll('[data-copy-email]').forEach((button) => {
    const original = button.textContent;
    button.addEventListener('click', async () => {
      const email = button.dataset.copyEmail;
      try {
        await navigator.clipboard.writeText(email);
        button.textContent = '邮箱已复制';
        setTimeout(() => { button.textContent = original; }, 1600);
      } catch {
        window.location.href = `mailto:${email}`;
      }
    });
  });

  const filterButtons = document.querySelectorAll('[data-filter]');
  const filterItems = document.querySelectorAll('[data-category]');

  filterButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const filter = button.dataset.filter;
      filterButtons.forEach((item) => item.classList.toggle('active', item === button));
      filterItems.forEach((item) => {
        const categories = (item.dataset.category || '').split(' ');
        item.hidden = filter !== 'all' && !categories.includes(filter);
      });
    });
  });
})();
