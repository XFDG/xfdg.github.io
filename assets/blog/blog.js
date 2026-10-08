/* Website-side Wechatsync bridge. No passwords, cookies or GitHub tokens.
 * Compatible with the extension's documented $syncer API:
 * https://github.com/wechatsync/Wechatsync/blob/v2/packages/extension/public/inject-api.js
 * https://github.com/wechatsync/Wechatsync/blob/v2/packages/extension/src/content/api.ts
 * Account discovery and draft creation run only after explicit button clicks.
 */
(() => {
  'use strict';
  const en = document.documentElement.lang === 'en';
  const t = (zh, english) => en ? english : zh;
  const $ = selector => document.querySelector(selector);
  const setText = (node, value) => { if (node) node.textContent = value; };
  const storage = {
    get(key) { try { return localStorage.getItem(key); } catch { return null; } },
    set(key, value) { try { localStorage.setItem(key, value); return true; } catch { return false; } },
    remove(key) { try { localStorage.removeItem(key); } catch { /* unavailable */ } }
  };
  async function copy(text) {
    try { await navigator.clipboard.writeText(text); return; } catch { /* fallback */ }
    const node = document.createElement('textarea');
    node.value = text; node.readOnly = true;
    node.style.cssText = 'position:fixed;left:-9999px;top:0';
    document.body.append(node); node.select();
    const ok = document.execCommand('copy'); node.remove();
    if (!ok) throw new Error(t('复制失败，请使用下载按钮。', 'Copy failed; please use Download.'));
  }
  function download(text, name) {
    const url = URL.createObjectURL(new Blob([text], {type:'text/markdown;charset=utf-8'}));
    const a = document.createElement('a'); a.href = url; a.download = name;
    document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }
  const search = $('#blog-search'), tag = $('#blog-tag');
  const rows = Array.from(document.querySelectorAll('.blog-row[data-search]'));
  function filter() {
    const words = (search?.value || '').trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let visible = 0;
    rows.forEach(row => {
      let tags = []; try { tags = JSON.parse(row.dataset.tags || '[]'); } catch { /* none */ }
      row.hidden = !words.every(word => row.dataset.search.includes(word)) || Boolean(tag?.value && !tags.includes(tag.value));
      if (!row.hidden) visible++;
    });
    if ($('#blog-no-results')) $('#blog-no-results').hidden = visible > 0 || rows.length === 0;
  }
  search?.addEventListener('input', filter); tag?.addEventListener('change', filter);

  // Math failures leave readable TeX in place. Raw HTML is disabled at build time.
  if (window.katex) document.querySelectorAll('.blog-prose .math').forEach(node => {
    try { window.katex.render(node.textContent, node, {displayMode:node.classList.contains('math-display'),throwOnError:false,trust:false,maxExpand:1000}); } catch { /* leave TeX */ }
  });
  const scratch = $('#scratch');
  if (scratch) {
    const key = 'haoran:local-scratch:v1';
    scratch.value = storage.get(key) || '';
    scratch.addEventListener('input', () => {
      const ok = storage.set(key, scratch.value);
      setText($('#scratch-status'), ok ? t('已暂存到当前浏览器。', 'Saved in this browser.') : t('本地存储不可用，请立即导出备份。', 'Local storage unavailable; export a backup.'));
    });
    $('#scratch-export')?.addEventListener('click', () => download(scratch.value, 'local-draft.md'));
    $('#scratch-copy')?.addEventListener('click', async () => {
      try { await copy(scratch.value); setText($('#scratch-status'), t('正文已复制。', 'Copied.')); }
      catch (error) { setText($('#scratch-status'), error.message); }
    });
    $('#scratch-clear')?.addEventListener('click', () => {
      if (window.confirm(t('清空当前浏览器中的草稿？此操作不能撤回。', 'Clear the local scratchpad? This cannot be undone.'))) {
        scratch.value = ''; storage.remove(key); setText($('#scratch-status'), t('已清空。', 'Cleared.'));
      }
    });
  }
  const holder = $('#blog-payload');
  if (!holder) return;
  let articlePromise;
  function article() {
    if (!articlePromise) articlePromise = (async () => {
      const url = new URL(holder.dataset.url, location.href);
      if (url.origin !== location.origin) throw new Error('Invalid article origin');
      const response = await fetch(url, {credentials:'omit'});
      if (!response.ok) throw new Error(t('读取原文失败，请刷新重试。', 'Could not load the source article.'));
      const data = await response.json();
      if (!data.title || !data.url || typeof data.markdown !== 'string' || typeof data.html !== 'string') throw new Error('Invalid article data');
      return data;
    })().catch(error => { articlePromise = null; throw error; });
    return articlePromise;
  }
  document.querySelectorAll('[data-blog-copy]').forEach(button => {
    button.addEventListener('click', async () => {
      try {
        const p = await article(); let text = p.url;
        if (button.dataset.blogCopy === 'citation') text = `[${p.title.replace(/[\[\]\\]/g, '\\$&')}](${p.url})`;
        if (button.dataset.blogCopy === 'markdown') text = p.markdown;
        await copy(text); setText($('#blog-status'), t('已复制。', 'Copied.'));
      } catch (error) { setText($('#blog-status'), error.message); }
    });
  });
  const dialog = $('#sync-dialog'), status = $('#sync-status'), targets = $('#sync-accounts');
  const start = $('#start-sync'), detect = $('#detect-sync'), results = $('#sync-results');
  let accounts = [], running = false, timer;
  const bridge = () => window.$syncer || window.$poster;
  $('#open-sync')?.addEventListener('click', () => dialog.showModal());
  detect?.addEventListener('click', () => {
    if (running) return;
    const api = bridge();
    start.disabled = true; accounts = [];
    targets.querySelectorAll('label,p').forEach(x => x.remove());
    if (!api || typeof api.getAccounts !== 'function' || typeof api.addTask !== 'function') {
      setText(status, t('未检测到 Wechatsync。请安装扩展、允许它访问本站，并刷新本页。', 'Wechatsync was not detected. Install it, allow access to this site, and refresh.')); return;
    }
    detect.disabled = true;
    setText(status, t('正在检测 CSDN / 知乎账号……', 'Checking CSDN / Zhihu accounts…'));
    let settled = false;
    const timeout = setTimeout(() => {
      settled = true; detect.disabled = false;
      setText(status, t('检测超时。请检查扩展权限及平台登录状态，再点击检测。', 'Account detection timed out. Check extension permissions and platform sign-in.'));
    }, 15000);
    try {
      api.getAccounts(response => {
        if (settled) return;
        settled = true; clearTimeout(timeout); detect.disabled = false;
        accounts = (Array.isArray(response) ? response : []).filter(a => ['csdn','zhihu'].includes(a.type));
        const seen = new Set(); accounts = accounts.filter(a => !seen.has(a.type) && seen.add(a.type));
        accounts.forEach((a,index) => {
          const label = document.createElement('label'), input = document.createElement('input');
          input.type = 'checkbox'; input.value = String(index);
          input.addEventListener('change', () => { start.disabled = !targets.querySelector('input:checked'); });
          label.append(input, document.createTextNode(`${a.type === 'csdn' ? 'CSDN' : '知乎'} · ${String(a.title || a.uid || '').slice(0,120)}`)); targets.append(label);
        });
        setText(status, accounts.length ? t('勾选需要接收本文的账号。', 'Select the accounts that should receive this article.') : t('未检测到已登录账号。请在当前浏览器登录 CSDN / 知乎后重试。', 'No signed-in accounts found. Sign into CSDN / Zhihu in this browser.'));
      });
    } catch (error) {
      settled = true; clearTimeout(timeout); detect.disabled = false; setText(status, error.message);
    }
  });
  function safeDraftUrl(raw, type) {
    try {
      const url = new URL(raw);
      const domain = type === 'csdn' ? 'csdn.net' : 'zhihu.com';
      return url.protocol === 'https:' && (url.hostname === domain || url.hostname.endsWith('.'+domain)) && !url.username && !url.password ? url.href : null;
    } catch { return null; }
  }
  function historyKey(p, type) { return `haoran:sync:${p.url}:${type}`; }
  function drawProgress(task, selected, p) {
    const updates = Array.isArray(task?.accounts) ? task.accounts : [];
    results.replaceChildren();
    selected.forEach(a => {
      const update = updates.find(x => x.type === a.type);
      const line = document.createElement('p');
      const label = a.type === 'csdn' ? 'CSDN' : '知乎';
      if (update?.status === 'done') {
        line.textContent = label+' · '+t('草稿已保存', 'Draft saved');
        const href = safeDraftUrl(update.editResp?.draftLink, a.type);
        if (href) { const link = document.createElement('a'); link.href = href; link.textContent = t(' 打开草稿 ↗',' Open draft ↗'); link.target = '_blank'; link.rel = 'noopener noreferrer'; line.append(link); }
        storage.set(historyKey(p,a.type), JSON.stringify({digest:p.digest,at:new Date().toISOString(),draftUrl:href}));
      } else if (update?.status === 'failed') {
        line.textContent = label+' · '+t('失败：', 'Failed: ')+String(update.error || update.msg || t('请检查平台登录和扩展状态。','Check platform sign-in and extension status.')).slice(0,240);
      } else line.textContent = label+' · '+String(update?.msg || t('等待同步结果……','Waiting for a result…')).slice(0,160);
      results.append(line);
    });
    const complete = selected.every(a => updates.some(u => u.type === a.type && ['done','failed'].includes(u.status)));
    if (complete) {
      clearTimeout(timer); running = false; detect.disabled = false; start.disabled = false;
      const failed = updates.some(u => selected.some(a=>a.type===u.type) && u.status==='failed');
      setText(status, failed ? t('部分平台未成功；已成功的草稿不会自动回滚。', 'Some platforms failed; successful drafts have not been rolled back.') : t('草稿已同步，请到平台检查并确认发布。', 'Drafts synced. Review and publish them on the platforms.'));
    }
  }
  start?.addEventListener('click', async () => {
    if (running) return;
    const selected = Array.from(targets.querySelectorAll('input:checked')).map(x=>accounts[Number(x.value)]).filter(Boolean);
    if (!selected.length) return;
    running = true; start.disabled = true; detect.disabled = true;
    try {
      const p = await article();
      const prior = selected.some(a => storage.get(historyKey(p,a.type)));
      if (prior && !window.confirm(t('本文之前同步过，再次发送可能创建新草稿。继续？', 'This article was sent before; resending may create a new draft. Continue?'))) {
        running = false; start.disabled = false; detect.disabled = false; return;
      }
      const api = bridge();
      if (!api || typeof api.addTask !== 'function') throw new Error(t('扩展连接已失效，请刷新。', 'The extension connection is no longer available.'));
      results.replaceChildren(); setText(status, t('正在同步，请保持本页打开，勿重复点击。', 'Syncing. Keep this page open and do not resend.'));
      timer = setTimeout(() => {
        running = false; detect.disabled = false; start.disabled = false;
        setText(status, t('尚未收到最终结果；任务可能仍在运行。请先检查平台草稿箱，避免重复创建。', 'No final response yet; the task may still be running. Check platform drafts before resending.'));
      }, 120000);
      api.addTask({post:{title:p.title,desc:p.summary,content:p.html,markdown:p.markdown,thumb:p.cover || ''},accounts:selected}, task=>drawProgress(task,selected,p), response=>{
        if (response?.error) {
          clearTimeout(timer); running = false; detect.disabled = false; start.disabled = false;
          setText(status,String(response.error).slice(0,240));
        }
      });
    } catch (error) {
      clearTimeout(timer); running = false; start.disabled = false; detect.disabled = false; setText(status,error.message);
    }
  });
})();
