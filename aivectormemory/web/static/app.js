const $ = s => document.querySelector(s);
const $$ = s => document.querySelectorAll(s);

let currentProject = null;

const api = (path, opts = {}) => {
  const sep = path.includes('?') ? '&' : '?';
  const url = currentProject !== null ? `/api/${path}${sep}project=${encodeURIComponent(currentProject)}` : `/api/${path}`;
  return fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  }).then(r => r.json());
};

const PAGE_SIZE = 50;
const state = { projectPage: 1, userPage: 1 };

const i18n = { get status() { return t('status') || {}; } };

function parseTags(v) {
  try { return typeof v === 'string' ? JSON.parse(v) : (v || []); } catch { return []; }
}
function escHtml(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function debounce(fn, ms) { let timer; return (...a) => { clearTimeout(timer); timer = setTimeout(() => fn(...a), ms); }; }

function toast(msg, type = 'success') {
  const el = document.createElement('div');
  el.className = `toast toast--${type}`;
  el.textContent = msg;
  $('#toast-container').appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

function switchTab(tab) {
  $$('.nav-item').forEach(i => i.classList.remove('active'));
  $$('.tab-panel').forEach(p => p.classList.remove('active'));
  const navItem = $(`.nav-item[data-tab="${tab}"]`);
  if (navItem) navItem.classList.add('active');
  const panel = $(`#tab-${tab}`);
  if (panel) panel.classList.add('active');
  loadTab(tab);
}

$$('.nav-item').forEach(item => {
  item.addEventListener('click', () => switchTab(item.dataset.tab));
});

function showModal(title, html, onSave) {
  $('#modal-title').textContent = title;
  $('#modal-content').innerHTML = html;
  $('#modal-save').style.display = onSave ? 'block' : 'none';
  $('#modal-save').onclick = onSave;
  $('#modal').classList.remove('hidden');
}
function hideModal() { $('#modal').classList.add('hidden'); }
$$('.modal-close').forEach(b => b.addEventListener('click', hideModal));
$('.modal-overlay').addEventListener('click', hideModal);

function renderIssueCard(i) {
  const badgeMap = { pending: 'warning', in_progress: 'info', completed: 'success' };
  const isArchived = !!i.archived_at;
  const badge = isArchived ? 'muted' : (badgeMap[i.status] || 'muted');
  const label = i18n.status[isArchived ? 'archived' : i.status] || i.status;
  const meta = isArchived ? `${i.date} · ${t('archivedAt')} ${i.archived_at}` : `${i.date} · ${t('createdAt')} ${i.created_at}`;
  return `
  <div class="issue-card" onclick="this.classList.toggle('expanded')">
    <div class="issue-card__header">
      <div class="issue-card__title"><span class="issue-card__number">#${i.issue_number}</span>${escHtml(i.title)}</div>
      <span class="badge badge--${badge}">${escHtml(label)}</span>
    </div>
    ${i.content ? `<div class="issue-card__content">${escHtml(i.content)}</div>` : ''}
    <div class="issue-card__meta">${meta}</div>
    ${i.content ? `<div class="issue-card__expand">${t('clickExpand')}</div>` : ''}
  </div>`;
}

function renderMemoryCard(m) {
  const tags = parseTags(m.tags);
  return `<div class="memory-card">
    <div class="memory-card__header">
      <div class="memory-card__id">${m.id}</div>
      <div class="memory-card__actions">
        <button class="btn btn--ghost btn--sm" onclick="event.stopPropagation();editMemory('${m.id}')">${t('edit')}</button>
        <button class="btn btn--ghost-danger btn--sm" onclick="event.stopPropagation();deleteMemory('${m.id}')">${t('delete')}</button>
      </div>
    </div>
    <div class="memory-card__content" onclick="this.classList.toggle('expanded')">${escHtml(m.content)}</div>
    <div class="memory-card__footer">
      <div class="memory-card__tags">${tags.map(tg => `<span class="tag">${escHtml(tg)}</span>`).join('')}</div>
      <div class="memory-card__time">${m.created_at || ''}</div>
    </div>
  </div>`;
}

function pagerInfo(total, page, pages) {
  return `${t('total')} ${total} ${t('items')}，${page}/${pages} ${t('page')}`;
}

function buildPagerBtns(page, pages) {
  if (pages <= 7) return Array.from({length: pages}, (_, i) => i + 1);
  const s = new Set([1, pages, page]);
  for (let d = 1; d <= 2; d++) { if (page - d > 1) s.add(page - d); if (page + d < pages) s.add(page + d); }
  const arr = [...s].sort((a, b) => a - b), result = [];
  arr.forEach((n, i) => { if (i > 0 && n - arr[i - 1] > 1) result.push('...'); result.push(n); });
  return result;
}

function renderPager(containerId, page, total, onPage) {
  const pages = Math.ceil(total / PAGE_SIZE) || 1;
  if (pages <= 1) { $(containerId).innerHTML = ''; return; }
  const items = buildPagerBtns(page, pages);
  const btns = items.map(n => n === '...' ? '<span class="pager__ellipsis">…</span>' : `<button class="pager__btn${n === page ? ' pager__btn--active' : ''}" data-page="${n}">${n}</button>`).join('');
  $(containerId).innerHTML = `<span class="pager__info">${pagerInfo(total, page, pages)}</span>${btns}`;
  $(containerId).querySelectorAll('.pager__btn').forEach(btn => {
    btn.addEventListener('click', () => onPage(parseInt(btn.dataset.page)));
  });
}

async function loadMemoriesByScope(scope, listId, pagerId, searchId, countId, pageKey) {
  const query = $(searchId).value;
  const page = state[pageKey];
  const offset = (page - 1) * PAGE_SIZE;
  const params = `memories?scope=${scope}&limit=${PAGE_SIZE}&offset=${offset}` + (query ? `&query=${encodeURIComponent(query)}` : '');
  const data = await api(params);
  const memories = data.memories || [];
  const total = data.total || memories.length;

  $(countId).textContent = `${t('total')} ${total} ${t('items')}`;
  $(listId).innerHTML = memories.length
    ? memories.map(renderMemoryCard).join('')
    : `<div class="empty-state">${t('noMemories')}</div>`;

  renderPager(pagerId, page, total, p => { state[pageKey] = p; loadMemoriesByScope(scope, listId, pagerId, searchId, countId, pageKey); });
}

function loadProjectMemories() {
  loadMemoriesByScope('project', '#project-memory-list', '#project-pager', '#project-search', '#project-count', 'projectPage');
}
function loadUserMemories() {
  loadMemoriesByScope('user', '#user-memory-list', '#user-pager', '#user-search', '#user-count', 'userPage');
}

window.editMemory = async (id) => {
  const m = await api(`memories/${id}`);
  const tags = parseTags(m.tags);
  showModal(t('editMemory'), `
    <div class="form-field"><label class="form-label">${t('content')}</label>
      <textarea class="form-textarea" id="edit-content">${escHtml(m.content)}</textarea></div>
    <div class="form-field"><label class="form-label">${t('tagsCommaSep')}</label>
      <input class="form-input" id="edit-tags" value="${tags.join(', ')}"></div>
  `, async () => {
    const content = $('#edit-content').value;
    const newTags = $('#edit-tags').value.split(',').map(s => s.trim()).filter(Boolean);
    await api(`memories/${id}`, { method: 'PUT', body: { content, tags: newTags } });
    hideModal();
    toast(t('memorySaved'));
    loadProjectMemories();
    loadUserMemories();
  });
};

window.deleteMemory = async (id) => {
  if (!confirm(t('confirmDelete'))) return;
  await api(`memories/${id}`, { method: 'DELETE' });
  toast(t('memoryDeleted'));
  loadProjectMemories();
  loadUserMemories();
};

function bindSearchClear(inputId, clearId, pageKey, loadFn) {
  const input = $(inputId), btn = $(clearId);
  const toggle = () => btn.classList.toggle('hidden', !input.value);
  input.addEventListener('input', debounce(() => { toggle(); state[pageKey] = 1; loadFn(); }, 300));
  btn.addEventListener('click', () => { input.value = ''; toggle(); state[pageKey] = 1; loadFn(); });
}
bindSearchClear('#project-search', '#project-search-clear', 'projectPage', loadProjectMemories);
bindSearchClear('#user-search', '#user-search-clear', 'userPage', loadUserMemories);

const MODAL_PAGE_SIZE = 10;

async function showMemoryModal(title, scope, query, page = 1, tag = null) {
  const offset = (page - 1) * MODAL_PAGE_SIZE;
  let params = `memories?scope=${scope}&limit=${MODAL_PAGE_SIZE}&offset=${offset}`;
  if (tag) params += `&tag=${encodeURIComponent(tag)}`;
  else if (query) params += `&query=${encodeURIComponent(query)}`;
  const data = await api(params);
  const memories = data.memories || [];
  const total = data.total || memories.length;
  const pages = Math.ceil(total / MODAL_PAGE_SIZE) || 1;

  const list = memories.length
    ? memories.map(renderMemoryCard).join('')
    : `<div class="empty-state">${t('noMemories')}</div>`;

  let pagerHtml = '';
  if (pages > 1) {
    const items = buildPagerBtns(page, pages);
    const btns = items.map(n => n === '...' ? '<span class="pager__ellipsis">…</span>' : `<button class="pager__btn${n === page ? ' pager__btn--active' : ''}" data-page="${n}">${n}</button>`).join('');
    pagerHtml = `<div class="pager"><span class="pager__info">${pagerInfo(total, page, pages)}</span>${btns}</div>`;
  }

  showModal(title, `<div class="modal-list">${list}</div>${pagerHtml}`);
  $$('#modal-content .pager__btn').forEach(btn => {
    btn.addEventListener('click', () => showMemoryModal(title, scope, query, parseInt(btn.dataset.page), tag));
  });
}

async function showIssueModal(title, status, page = 1) {
  const url = status === 'archived' ? 'issues?status=archived' : `issues?status=${status}`;
  const data = await api(url);
  const issues = data.issues || [];
  const total = issues.length;
  const pages = Math.ceil(total / MODAL_PAGE_SIZE) || 1;
  const start = (page - 1) * MODAL_PAGE_SIZE;
  const slice = issues.slice(start, start + MODAL_PAGE_SIZE);

  const list = slice.length ? slice.map(i => renderIssueCard(i)).join('') : `<div class="empty-state">${t('noIssues')}</div>`;

  let pagerHtml = '';
  if (pages > 1) {
    const items = buildPagerBtns(page, pages);
    const btns = items.map(n => n === '...' ? '<span class="pager__ellipsis">…</span>' : `<button class="pager__btn${n === page ? ' pager__btn--active' : ''}" data-page="${n}">${n}</button>`).join('');
    pagerHtml = `<div class="pager"><span class="pager__info">${pagerInfo(total, page, pages)}</span>${btns}</div>`;
  }

  showModal(title, `<div class="modal-list">${list}</div>${pagerHtml}`);
  $$('#modal-content .pager__btn').forEach(btn => {
    btn.addEventListener('click', () => showIssueModal(title, status, parseInt(btn.dataset.page)));
  });
}

async function loadStats() {
  const s = await api('stats');
  const mem = s.memories || {};
  const issues = s.issues || {};
  const tags = s.tags || {};
  const tagList = Object.entries(tags).sort((a, b) => b[1] - a[1]);

  const cards = [
    { label: t('projectMemories'), num: mem.project || 0, cls: 'blue', action: 'goto-tab', tab: 'project-memories' },
    { label: t('globalMemories'), num: mem.user || 0, cls: 'cyan', action: 'goto-tab', tab: 'user-memories' },
    { label: i18n.status.pending, num: issues.pending || 0, cls: 'warning', action: 'filter-issues', status: 'pending' },
    { label: i18n.status.in_progress, num: issues.in_progress || 0, cls: 'info', action: 'filter-issues', status: 'in_progress' },
    { label: i18n.status.completed, num: issues.completed || 0, cls: 'success', action: 'filter-issues', status: 'completed' },
    { label: i18n.status.archived, num: issues.archived || 0, cls: 'muted', action: 'filter-issues', status: 'archived' },
  ];

  $('#stats-content').innerHTML = cards.map(c =>
    `<div class="mini-card mini-card--${c.cls}" data-action="${c.action}" data-tab="${c.tab || ''}" data-status="${c.status || ''}">
      <div class="mini-card__label">${c.label}</div>
      <div class="mini-card__number">${c.num}</div>
    </div>`
  ).join('');

  renderVectorNetwork(tagList);

  const totalCount = (mem.project || 0) + (mem.user || 0) + (issues.pending || 0) + (issues.in_progress || 0) + (issues.completed || 0);
  const oldHint = document.getElementById('empty-stats-hint');
  if (oldHint) oldHint.remove();
  if (totalCount === 0) {
    $('#stats-content').insertAdjacentHTML('afterend', `<div id="empty-stats-hint" class="welcome-guide"><div class="welcome-guide__desc">${t('emptyStatsHint')}</div></div>`);
  }

  $$('#stats-content .mini-card').forEach(card => {
    card.addEventListener('click', () => {
      const action = card.dataset.action;
      if (action === 'filter-issues') {
        const labelMap = i18n.status;
        showIssueModal(labelMap[card.dataset.status] || t('issueList'), card.dataset.status);
      } else if (action === 'goto-tab') {
        const tab = card.dataset.tab;
        const scope = tab === 'user-memories' ? 'user' : 'project';
        showMemoryModal(scope === 'user' ? t('globalMemories') : t('projectMemories'), scope, '');
      }
    });
  });
}

function renderVectorNetwork(tagList) {
  const MAX_NODES = 100, FL = 600;
  const items = tagList.slice(0, MAX_NODES);
  const container = $('#vector-network-container');
  if (!items.length) { container.innerHTML = ''; return; }

  const nodeCount = items.length;
  const R = Math.min(200, 80 + nodeCount * 2);

  const maxC = items[0][1], minC = items[items.length - 1][1] || 1;
  const colors = ['#3B82F6','#2563EB','#60A5FA','#818CF8','#A78BFA','#34D399','#F59E0B','#EF4444','#EC4899','#14B8A6','#8B5CF6','#F97316','#06B6D4','#84CC16','#E879F9'];

  const nodes3d = items.map(([label, count], i) => {
    const ratio = maxC === minC ? 0.5 : (count - minC) / (maxC - minC);
    const baseR = 4 + ratio * (nodeCount > 30 ? 8 : 14);
    const phi = Math.acos(1 - 2 * (i + 0.5) / nodeCount);
    const theta = Math.PI * (1 + Math.sqrt(5)) * i;
    return { label, count, baseR, x: R * Math.sin(phi) * Math.cos(theta), y: R * Math.cos(phi), z: R * Math.sin(phi) * Math.sin(theta), px: 0, py: 0, pz: 0 };
  });

  const edges = [];
  for (let i = 0; i < nodes3d.length; i++) {
    if (i + 1 < nodes3d.length) edges.push([i, i + 1]);
    if (i + 3 < nodes3d.length) edges.push([i, i + 3]);
  }
  if (nodes3d.length > 2) edges.push([nodes3d.length - 1, 0]);

  const vectorSub = t('vectorSub').replace('{n}', nodeCount);
  const moreLink = tagList.length > 0 ? `<a class="vector-network__more" id="vn-show-all">${t('showMore')}</a>` : '';
  container.innerHTML = `
    <div class="vector-network">
      <div class="vector-network__header">
        <div class="vector-network__left">
          <span class="vector-network__label">${t('vectorNetwork')}</span>
          <span class="vector-network__sub">${vectorSub}</span>
        </div>
        ${moreLink}
      </div>
      <svg class="vector-graph" viewBox="0 0 800 600" preserveAspectRatio="xMidYMid meet"></svg>
    </div>`;

  const W = 800, H = 600;
  const svg = container.querySelector('.vector-graph');
  const ns = 'http://www.w3.org/2000/svg';

  const showAllBtn = container.querySelector('#vn-show-all');
  if (showAllBtn) {
    showAllBtn.addEventListener('click', () => {
      const html = tagList.length ? `<ul class="stat-list stat-list--tags">${tagList.map(([k, v]) =>
        `<li><a class="stat-link" data-tag="${escHtml(k)}" style="cursor:pointer"><span>${escHtml(k)}</span><span class="tag-count">${v}</span></a></li>`
      ).join('')}</ul>` : `<div class="empty-state">${t('noTags')}</div>`;
      showModal(t('allTags').replace('{n}', tagList.length), html);
      $$('#modal-content .stat-link').forEach(link => {
        link.addEventListener('click', () => { hideModal(); showMemoryModal(t('tagLabel').replace('{name}', link.dataset.tag), 'all', '', 1, link.dataset.tag); });
      });
    });
  }

  const edgeEls = edges.map(([a, b]) => {
    const line = document.createElementNS(ns, 'line');
    line.setAttribute('class', a % 3 === 0 ? 'vg-edge vg-edge--weak' : 'vg-edge');
    svg.appendChild(line);
    return { el: line, a, b };
  });

  const nodeEls = nodes3d.map((n, i) => {
    const g = document.createElementNS(ns, 'g');
    g.setAttribute('class', 'vg-node');
    const color = colors[i % colors.length];
    const glow = document.createElementNS(ns, 'circle');
    glow.setAttribute('class', 'vg-node__glow');
    glow.style.fill = color + '15';
    const core = document.createElementNS(ns, 'circle');
    core.setAttribute('class', 'vg-node__core');
    core.style.fill = color;
    const text = document.createElementNS(ns, 'text');
    text.setAttribute('class', 'vg-node__label');
    text.textContent = n.label;
    g.appendChild(glow); g.appendChild(core); g.appendChild(text);
    svg.appendChild(g);
    return { g, glow, core, text, label: n.label };
  });

  let rotY = 0, rotX = 0.3, autoSpeed = 0.003, isHovering = false;
  let dragging = false, lastX = 0, lastY = 0, startX = 0, startY = 0, didDrag = false;

  const update = () => {
    const cosY = Math.cos(rotY), sinY = Math.sin(rotY), cosX = Math.cos(rotX), sinX = Math.sin(rotX);
    nodes3d.forEach(n => {
      const x1 = n.x * cosY - n.z * sinY, z1 = n.x * sinY + n.z * cosY;
      n.px = x1; n.py = n.y * cosX - z1 * sinX; n.pz = n.y * sinX + z1 * cosX;
    });

    const order = nodes3d.map((_, i) => i).sort((a, b) => nodes3d[b].pz - nodes3d[a].pz);

    edgeEls.forEach(({ el, a, b }) => {
      const na = nodes3d[a], nb = nodes3d[b];
      const sa = FL / (FL + na.pz), sb = FL / (FL + nb.pz);
      el.setAttribute('x1', (W / 2 + na.px * sa).toFixed(1));
      el.setAttribute('y1', (H / 2 + na.py * sa).toFixed(1));
      el.setAttribute('x2', (W / 2 + nb.px * sb).toFixed(1));
      el.setAttribute('y2', (H / 2 + nb.py * sb).toFixed(1));
      el.style.opacity = (0.08 + 0.25 * ((na.pz + nb.pz) / 2 + R) / (2 * R)).toFixed(2);
    });

    order.forEach(i => {
      const n = nodes3d[i], el = nodeEls[i];
      const s = FL / (FL + n.pz);
      const depth = (n.pz + R) / (2 * R);
      const cr = n.baseR * s, gr = cr * 2.5;
      el.g.setAttribute('transform', `translate(${(W / 2 + n.px * s).toFixed(1)},${(H / 2 + n.py * s).toFixed(1)})`);
      el.g.style.opacity = (0.4 + 0.6 * depth).toFixed(2);
      el.glow.setAttribute('r', gr.toFixed(1));
      el.core.setAttribute('r', cr.toFixed(1));
      el.text.setAttribute('dy', (gr + 10).toFixed(0));
      svg.appendChild(el.g);
    });
  };

  let animId;
  const animate = () => {
    if (!isHovering) rotY += autoSpeed;
    update();
    animId = requestAnimationFrame(animate);
  };

  svg.addEventListener('mouseenter', () => { isHovering = true; });
  svg.addEventListener('mouseleave', () => { isHovering = false; dragging = false; });
  svg.addEventListener('mousedown', (e) => { dragging = true; didDrag = false; startX = e.clientX; startY = e.clientY; lastX = e.clientX; lastY = e.clientY; e.preventDefault(); });
  svg.addEventListener('mousemove', (e) => {
    if (!dragging) return;
    const dx = e.clientX - startX, dy = e.clientY - startY;
    if (dx * dx + dy * dy > 9) didDrag = true;
    rotY += (e.clientX - lastX) * 0.008;
    rotX = Math.max(-1.2, Math.min(1.2, rotX + (e.clientY - lastY) * 0.008));
    lastX = e.clientX; lastY = e.clientY;
  });
  svg.addEventListener('mouseup', (e) => {
    dragging = false;
    if (!didDrag) {
      const el = document.elementFromPoint(e.clientX, e.clientY);
      const g = el && el.closest('.vg-node');
      if (g) {
        const idx = nodeEls.findIndex(n => n.g === g);
        if (idx >= 0) showMemoryModal(t('tagLabel').replace('{name}', nodeEls[idx].label), 'all', '', 1, nodeEls[idx].label);
      }
    }
  });

  update();
  animate();

  const observer = new MutationObserver(() => {
    if (!document.contains(svg)) { cancelAnimationFrame(animId); observer.disconnect(); }
  });
  observer.observe(document.body, { childList: true, subtree: true });
}

async function loadStatus() {
  const s = await api('status');
  if (s.empty) { $('#status-content').innerHTML = `<div class="empty-state">${t('noStatus')}</div>`; return; }

  const isBlocked = s.is_blocked;
  const dotClass = isBlocked ? 'status-dot--blocked' : 'status-dot--ok';
  const blockText = isBlocked ? `${t('yes')} - ${escHtml(s.block_reason || '')}` : t('no');

  const gridItems = [
    [t('blocked'), `<span class="status-dot ${dotClass}"></span>${blockText}`, 'status-item--alert'],
    [t('currentTask'), escHtml(s.current_task || '-')],
    [t('nextStep'), escHtml(s.next_step || '-')],
    [t('updateTime'), s.updated_at || '-'],
  ];

  const sections = [
    [t('progress'), s.progress],
    [t('recentChanges'), s.recent_changes],
    [t('pending'), s.pending],
  ].filter(([, arr]) => arr && arr.length);

  $('#status-content').innerHTML = `
    <div class="status-grid">
      ${gridItems.map(([label, value, cls]) =>
        `<div class="status-item${cls ? ' ' + cls : ''}">
          <div class="status-item__label">${label}</div>
          <div class="status-item__value">${value}</div>
        </div>`
      ).join('')}
    </div>
    ${sections.map(([title, items]) => `
      <div class="status-section">
        <div class="status-section__title">${title}</div>
        <div class="status-section__list">
          ${items.map(p => `<div class="status-section__item">· ${escHtml(p)}</div>`).join('')}
        </div>
      </div>
    `).join('')}
  `;
}

async function loadIssues() {
  const date = $('#issue-date').value;
  const status = $('#issue-status-filter').value;
  let url = 'issues?';
  if (date) url += `date=${date}&`;
  if (status === 'archived') url += 'include_archived=true';
  else if (status) url += `status=${status}`;
  const data = await api(url);
  const issues = data.issues || [];

  $('#issue-list').innerHTML = issues.length ? issues.map(i => renderIssueCard(i)).join('') : `<div class="empty-state">${t('noIssues')}</div>`;
}

$('#issue-date').value = new Date().toISOString().slice(0, 10);
$('#issue-date').addEventListener('change', loadIssues);
$('#issue-status-filter').addEventListener('change', loadIssues);

let tagData = [], tagSelected = new Set();

async function loadTags() {
  const query = $('#tag-search')?.value || '';
  const params = query ? `tags?query=${encodeURIComponent(query)}` : 'tags';
  const data = await api(params);
  tagData = data.tags || [];
  tagSelected.clear();
  updateTagBatchBar();
  $('#tag-total-count').textContent = `${t('total')} ${data.total || tagData.length} ${t('tagsUnit')}`;
  $('#tag-select-all').checked = false;
  renderTagTable();
}

function renderTagTable() {
  const tbody = $('#tag-table-body');
  if (!tagData.length) { tbody.innerHTML = `<tr><td colspan="4"><div class="empty-state">${t('noTags')}</div></td></tr>`; return; }
  tbody.innerHTML = tagData.map(tg => `
    <tr data-tag="${escHtml(tg.name)}">
      <td><input type="checkbox" class="tag-cell__check" ${tagSelected.has(tg.name) ? 'checked' : ''}></td>
      <td><span class="tag-cell__name">${escHtml(tg.name)}</span></td>
      <td><span class="tag-count">${tg.project_count ? `${tg.project_count} 📁` : ''}${tg.project_count && tg.user_count ? '  ' : ''}${tg.user_count ? `${tg.user_count} 🌐` : ''}</span></td>
      <td class="tag-actions">
        <button class="btn btn--ghost btn--sm tag-rename">${t('rename')}</button>
        <button class="btn btn--ghost btn--sm tag-view" style="color:#60A5FA">${t('view')}</button>
        <button class="btn btn--ghost btn--sm tag-delete" style="color:#F87171">${t('delete')}</button>
      </td>
    </tr>`).join('');

  tbody.querySelectorAll('.tag-cell__check').forEach(cb => {
    cb.addEventListener('change', () => {
      const name = cb.closest('tr').dataset.tag;
      cb.checked ? tagSelected.add(name) : tagSelected.delete(name);
      updateTagBatchBar();
    });
  });
  tbody.querySelectorAll('.tag-rename').forEach(btn => {
    btn.addEventListener('click', () => renameTagAction(btn.closest('tr').dataset.tag));
  });
  tbody.querySelectorAll('.tag-view').forEach(btn => {
    btn.addEventListener('click', () => showMemoryModal(t('tagLabel').replace('{name}', btn.closest('tr').dataset.tag), 'all', '', 1, btn.closest('tr').dataset.tag));
  });
  tbody.querySelectorAll('.tag-delete').forEach(btn => {
    btn.addEventListener('click', () => deleteTagAction([btn.closest('tr').dataset.tag]));
  });
}

function updateTagBatchBar() {
  const bar = $('#tag-batch-bar');
  if (tagSelected.size > 0) {
    bar.style.display = 'flex';
    $('#tag-selected-count').textContent = tagSelected.size;
  } else {
    bar.style.display = 'none';
  }
}

function renameTagAction(oldName) {
  showModal(t('renameTag'), `
    <div class="form-field"><label class="form-label">${t('currentName')}</label>
      <input class="form-input" value="${escHtml(oldName)}" disabled></div>
    <div class="form-field"><label class="form-label">${t('newName')}</label>
      <input class="form-input" id="rename-new-name" value="${escHtml(oldName)}"></div>
  `, async () => {
    const newName = $('#rename-new-name').value.trim();
    if (!newName || newName === oldName) return;
    await api('tags/rename', { method: 'PUT', body: { old_name: oldName, new_name: newName } });
    hideModal();
    toast(t('tagRenamed'));
    loadTags();
  });
  setTimeout(() => { const inp = $('#rename-new-name'); inp && inp.select(); }, 100);
}

async function deleteTagAction(names) {
  if (!confirm(t('confirmDeleteTag').replace('{names}', names.join(', ')))) return;
  await api('tags/delete', { method: 'DELETE', body: { tags: names } });
  toast(t('tagsDeleted'));
  loadTags();
}

$('#tag-select-all')?.addEventListener('change', (e) => {
  tagSelected = e.target.checked ? new Set(tagData.map(tg => tg.name)) : new Set();
  renderTagTable();
  updateTagBatchBar();
});

$('#tag-batch-merge')?.addEventListener('click', () => {
  if (tagSelected.size < 2) return;
  const names = [...tagSelected];
  showModal(t('mergeTags'), `
    <div class="form-field"><label class="form-label">${t('mergeFollowing')}</label>
      <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px">${names.map(n => `<span class="tag">${escHtml(n)}</span>`).join('')}</div></div>
    <div class="form-field"><label class="form-label">${t('mergeInto')}</label>
      <input class="form-input" id="merge-target" value="${escHtml(names[0])}"></div>
  `, async () => {
    const target = $('#merge-target').value.trim();
    if (!target) return;
    await api('tags/merge', { method: 'PUT', body: { source_tags: names, target_name: target } });
    hideModal();
    toast(t('tagsMerged'));
    loadTags();
  });
});

$('#tag-batch-delete')?.addEventListener('click', () => {
  if (!tagSelected.size) return;
  deleteTagAction([...tagSelected]);
});

$('#tag-batch-cancel')?.addEventListener('click', () => {
  tagSelected.clear();
  $('#tag-select-all').checked = false;
  renderTagTable();
  updateTagBatchBar();
});

const tagSearchHandler = debounce(() => { loadTags(); }, 300);
$('#tag-search')?.addEventListener('input', () => {
  const val = $('#tag-search').value;
  $('#tag-search-clear').classList.toggle('hidden', !val);
  tagSearchHandler();
});
$('#tag-search-clear')?.addEventListener('click', () => {
  $('#tag-search').value = '';
  $('#tag-search-clear').classList.add('hidden');
  loadTags();
});

function loadTab(tab) {
  ({
    stats: loadStats,
    'project-memories': loadProjectMemories,
    'user-memories': loadUserMemories,
    status: loadStatus,
    issues: loadIssues,
    tags: loadTags,
  })[tab]?.();
}

window._reloadCurrentView = () => {
  if (currentProject) {
    const active = $('.nav-item.active');
    if (active) loadTab(active.dataset.tab);
  } else {
    loadProjects();
  }
};

const folderIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>';

function loadProjects() {
  fetch('/api/projects').then(r => r.json()).then(data => {
    const grid = $('#project-grid');
    const addCard = `<div class="project-card project-card--add" onclick="showAddProjectModal()" style="animation-delay:0s">
      <div class="project-card__icon project-card__icon--add"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></div>
      <div class="project-card__name">${t('addProject')}</div>
    </div>`;
    const cards = data.projects.map((p, i) => `
      <div class="project-card" data-project="${escHtml(p.project_dir)}" style="animation-delay:${(i + 1) * 0.05}s">
        <button class="project-card__delete" onclick="event.stopPropagation();deleteProject('${escHtml(p.project_dir)}','${escHtml(p.name)}')" title="${t('deleteProjectBtn')}">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
        </button>
        <div class="project-card__icon">${folderIcon}</div>
        <div class="project-card__name">${escHtml(p.name)}</div>
        <div class="project-card__path">${escHtml(p.project_dir)}</div>
        <div class="project-card__stats">
          <div class="project-card__stat"><div class="project-card__stat-num project-card__stat-num--blue">${p.memories}</div><div class="project-card__stat-label">${t('memories')}</div></div>
          <div class="project-card__stat"><div class="project-card__stat-num project-card__stat-num--amber">${p.issues}</div><div class="project-card__stat-label">${t('issues')}</div></div>
          <div class="project-card__stat"><div class="project-card__stat-num project-card__stat-num--cyan">${p.tags}</div><div class="project-card__stat-label">${t('tags')}</div></div>
        </div>
      </div>
    `).join('');
    const welcome = data.projects.length === 0 ? `<div class="welcome-guide" style="grid-column:1/-1">
      <div class="welcome-guide__title">${t('welcomeTitle')}</div>
      <div class="welcome-guide__desc">${t('welcomeDesc').replace(/\\n/g, '<br>')}</div>
      <div class="welcome-guide__cmd">${t('welcomeCmd')}</div>
    </div>` : '';
    grid.innerHTML = addCard + cards + welcome;
    $('#project-select-footer').innerHTML = `${t('footer').replace('{n}', data.projects.length)} · <a href="https://github.com/Edlineas/aivectormemory" target="_blank" rel="noopener" style="color:#6366F1;text-decoration:none">GitHub</a>`;
    grid.querySelectorAll('.project-card[data-project]').forEach(card => {
      card.addEventListener('click', () => enterProject(card.dataset.project));
    });
  });
}

function enterProject(projectDir) {
  currentProject = projectDir;
  location.hash = encodeURIComponent(projectDir);
  $('#project-select').style.display = 'none';
  $('#app').style.display = '';
  const info = $('#sidebar-project-info');
  info.style.display = '';
  $('#sidebar-project-name').textContent = projectDir.replace(/\\/g, '/').split('/').pop();
  $$('.nav-item').forEach((el, i) => el.classList.toggle('active', i === 0));
  $$('.tab-panel').forEach(el => el.classList.remove('active'));
  $('#tab-stats').classList.add('active');
  renderLangSwitcher('lang-switcher-sidebar');
  loadStats();
}

function exitProject() {
  currentProject = null;
  location.hash = '';
  $('#app').style.display = 'none';
  $('#project-select').style.display = '';
  $('#sidebar-project-info').style.display = 'none';
  loadProjects();
}

function showAddProjectModal() {
  const html = `<div class="add-project-form">
    <label>${t('projectPath')}</label>
    <div class="add-project-input-row">
      <input type="text" id="add-project-path" placeholder="${t('addProjectPlaceholder')}" />
      <button class="btn-browse" onclick="browseDirs()">${t('browse')}</button>
    </div>
    <div id="dir-browser" class="dir-browser hidden">
      <div id="dir-browser-path" class="dir-browser__path"></div>
      <div id="dir-browser-list" class="dir-browser__list"></div>
    </div>
  </div>`;
  showModal(t('addProjectTitle'), html, () => {
    const path = $('#add-project-path').value.trim();
    if (!path) return alert(t('pathRequired'));
    fetch('/api/projects', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ project_dir: path }) })
      .then(r => r.json()).then(d => { if (d.success) { hideModal(); toast(t('addProjectSuccess'), 'success'); toast(t('addProjectInstallHint'), 'info'); loadProjects(); } });
  });
}

function browseDirs(path) {
  const url = path ? `/api/browse?path=${encodeURIComponent(path)}` : '/api/browse';
  fetch(url).then(r => r.json()).then(data => {
    if (data.error) return;
    const browser = $('#dir-browser');
    browser.classList.remove('hidden');
    $('#add-project-path').value = data.path;
    $('#dir-browser-path').textContent = data.path;
    const parentPath = data.path.replace(/\/[^/]+\/?$/, '') || '/';
    const items = [`<div class="dir-browser__item dir-browser__item--parent" onclick="browseDirs('${escHtml(parentPath)}')">⬆ ${t('parentDir')}</div>`];
    data.dirs.forEach(d => {
      const full = data.path.replace(/\/$/, '') + '/' + d;
      items.push(`<div class="dir-browser__item" onclick="event.stopPropagation();$('#add-project-path').value='${escHtml(full)}';browseDirs('${escHtml(full)}')">${escHtml(d)}</div>`);
    });
    $('#dir-browser-list').innerHTML = items.join('');
  });
}
window.showAddProjectModal = showAddProjectModal;
window.browseDirs = browseDirs;

window.deleteProject = function(projectDir, name) {
  if (!confirm(t('confirmDeleteProject').replace('{name}', name))) return;
  fetch('/api/projects/' + encodeURIComponent(projectDir), { method: 'DELETE' })
    .then(r => r.json())
    .then(d => { if (d.success) loadProjects(); else alert(d.error || 'Failed'); });
};


$('#sidebar-project-info')?.addEventListener('click', exitProject);

// 导出
$('#btn-export')?.addEventListener('click', async () => {
  const data = await api('export?scope=project');
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `aivectormemory-export-${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
  toast(t('exportSuccess'));
});

// 导入
$('#btn-import')?.addEventListener('click', () => $('#import-file').click());
$('#import-file')?.addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  try {
    const text = await file.text();
    const body = JSON.parse(text);
    const res = await api('import', { method: 'POST', body });
    if (res.imported !== undefined) {
      toast(t('importSuccess').replace('{n}', res.imported));
      loadProjectMemories();
    } else {
      toast(t('importFailed'), 'error');
    }
  } catch { toast(t('importFailed'), 'error'); }
  e.target.value = '';
});

// 初始化
setLang(currentLang);
renderLangSwitcher('lang-switcher-project');

const _hashProject = location.hash ? decodeURIComponent(location.hash.slice(1)) : '';
_hashProject ? enterProject(_hashProject) : loadProjects();
