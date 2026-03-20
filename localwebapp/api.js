/* ═══════════════════════════════════════════════════════════
   MNHEME API CONSOLE — api.js
   Vanilla JS — zero dependencies
   ═══════════════════════════════════════════════════════════ */

'use strict';

/* ── Config ─────────────────────────────────────────────── */
let BASE_URL = 'http://localhost:8000';

/* ── Feeling color map ───────────────────────────────────── */
const FEELING_LABELS = {
  gioia: '✨ Joy', tristezza: '🌧 Sadness', rabbia: '🔥 Anger',
  paura: '🌑 Fear', nostalgia: '🍂 Nostalgia', amore: '❤ Love',
  malinconia: '🌊 Melancholy', serenità: '🌿 Serenity', sorpresa: '⚡ Surprise',
  ansia: '🌀 Anxiety', gratitudine: '✿ Gratitude', vergogna: '◈ Shame',
  orgoglio: '▲ Pride', noia: '— Boredom', curiosità: '◎ Curiosity',
};

/* ═══════════════════════════════════════════════════════════
   HTTP CLIENT
   ═══════════════════════════════════════════════════════════ */

async function api(method, path, body = null) {
  const url     = BASE_URL + path;
  const logId   = addLog(method, path, 'pending');
  const started = performance.now();

  const opts = {
    method,
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);

  try {
    const res  = await fetch(url, opts);
    const data = await res.json();
    const ms   = Math.round(performance.now() - started);
    updateLog(logId, res.ok ? 'ok' : 'err', res.status, ms);
    if (!res.ok) throw { status: res.status, detail: data.detail || JSON.stringify(data) };
    return data;
  } catch (e) {
    const ms = Math.round(performance.now() - started);
    if (e.status) {
      updateLog(logId, 'err', e.status, ms);
      throw e;
    }
    updateLog(logId, 'err', 'ERR', ms);
    throw { status: 0, detail: 'Cannot reach server at ' + BASE_URL };
  }
}

const GET  = (path)        => api('GET',  path);
const POST = (path, body)  => api('POST', path, body);

/* ═══════════════════════════════════════════════════════════
   REQUEST LOG
   ═══════════════════════════════════════════════════════════ */

let logCounter = 0;
function addLog(method, url, status) {
  const id  = ++logCounter;
  const el  = document.createElement('div');
  el.className = 'log-entry';
  el.id = 'log-' + id;
  const now = new Date();
  const ts  = now.toTimeString().slice(0,8);
  el.innerHTML = `
    <span class="log-time">${ts}</span>
    <span class="log-method ${method}">${method}</span>
    <span class="log-url" title="${url}">${url}</span>
    <span class="log-status pending" id="log-status-${id}">…</span>`;
  document.getElementById('req-log-entries').prepend(el);
  return id;
}
function updateLog(id, type, status, ms) {
  const el = document.getElementById('log-status-' + id);
  if (!el) return;
  el.textContent = `${status} ${ms}ms`;
  el.className   = 'log-status ' + type;
}
document.getElementById('btn-clear-log').addEventListener('click', () => {
  document.getElementById('req-log-entries').innerHTML = '';
});

/* ═══════════════════════════════════════════════════════════
   SERVER STATUS + CONNECT
   ═══════════════════════════════════════════════════════════ */

const dot      = document.getElementById('status-dot');
const label    = document.getElementById('status-label');
const urlLabel = document.getElementById('status-url');

async function checkConnection() {
  dot.className   = 'status-dot';
  label.textContent = 'connecting…';
  try {
    const stats = await GET('/stats');
    dot.className     = 'status-dot connected';
    label.textContent = 'connected';
    urlLabel.textContent = BASE_URL.replace('http://','');
    updateSidebarStats(stats);
  } catch (e) {
    dot.className     = 'status-dot error';
    label.textContent = 'offline';
  }
}

document.getElementById('btn-connect').addEventListener('click', () => {
  const val = document.getElementById('api-url').value.trim().replace(/\/$/, '');
  if (val) BASE_URL = val;
  checkConnection();
});

function updateSidebarStats(stats) {
  document.getElementById('total-memories').textContent =
    `${(stats.total_memories || 0).toLocaleString()} memories`;
  document.getElementById('total-concepts').textContent =
    `${(stats.concepts || 0)} concepts`;
}

/* ═══════════════════════════════════════════════════════════
   NAVIGATION
   ═══════════════════════════════════════════════════════════ */

document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    btn.classList.add('active');
    const view = document.getElementById('view-' + btn.dataset.view);
    if (view) view.classList.add('active');
  });
});

/* ═══════════════════════════════════════════════════════════
   TOAST
   ═══════════════════════════════════════════════════════════ */

function toast(msg, type = 'info', duration = 3000) {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(() => el.remove(), duration);
}

/* ═══════════════════════════════════════════════════════════
   HELPERS — render
   ═══════════════════════════════════════════════════════════ */

function fmtDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

function feelingHtml(feeling) {
  const label = FEELING_LABELS[feeling] || feeling;
  return `<span class="memory-feeling feeling-${CSS.escape(feeling)}">${label}</span>`;
}

function memoryCardHtml(m, i) {
  const tags   = (m.tags || []).map(t => `<span class="memory-tag">${esc(t)}</span>`).join('');
  const tagRow = tags ? `<div class="memory-tags">${tags}</div>` : '';
  const note   = m.note ? `<div class="memory-note">${esc(m.note)}</div>` : '';
  return `
    <div class="memory-card" style="animation-delay:${i*30}ms">
      <div class="memory-card-header">
        <span class="memory-concept">${esc(m.concept)}</span>
        ${feelingHtml(m.feeling)}
        <span class="memory-mediatype">${(m.media_type||'text').toUpperCase()}</span>
        <span class="memory-ts">${fmtDate(m.timestamp)}</span>
      </div>
      <div class="memory-content">${esc(m.content)}</div>
      ${note}
      ${tagRow}
      <div class="memory-id">${m.memory_id}</div>
    </div>`;
}

function renderMemories(container, memories) {
  if (!memories.length) {
    container.innerHTML = `<div class="empty-state"><div class="empty-state-icon">◎</div>No memories found.</div>`;
    return;
  }
  container.innerHTML = memories.map((m, i) => memoryCardHtml(m, i)).join('');
}

function esc(str) {
  return String(str || '')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;');
}

function loading(container) {
  container.innerHTML = `<div class="empty-state"><span class="loading"></span> Loading…</div>`;
}

function showError(container, msg) {
  container.innerHTML = `<div class="empty-state" style="color:var(--red)">✗ ${esc(msg)}</div>`;
}

/* ═══════════════════════════════════════════════════════════
   VIEW: NEW MEMORY
   ═══════════════════════════════════════════════════════════ */

const contentEl = document.getElementById('new-content');
contentEl.addEventListener('input', () => {
  document.getElementById('char-count').textContent = contentEl.value.length + ' chars';
});

document.getElementById('new-tags').addEventListener('input', function () {
  const tags    = this.value.split(',').map(t => t.trim()).filter(Boolean);
  const preview = document.getElementById('tag-preview');
  preview.innerHTML = tags.map(t => `<span class="tag-chip">${esc(t)}</span>`).join('');
});

document.getElementById('btn-clear').addEventListener('click', () => {
  ['new-concept','new-content','new-note','new-tags'].forEach(id => {
    document.getElementById(id).value = '';
  });
  document.getElementById('new-feeling').value     = '';
  document.getElementById('new-mediatype').value   = 'text';
  document.getElementById('char-count').textContent = '0 chars';
  document.getElementById('tag-preview').innerHTML  = '';
  const ra = document.getElementById('new-memory-response');
  ra.classList.remove('visible','error');
  ra.innerHTML = '';
});

document.getElementById('btn-remember').addEventListener('click', async () => {
  const concept    = document.getElementById('new-concept').value.trim();
  const feeling    = document.getElementById('new-feeling').value;
  const content    = document.getElementById('new-content').value.trim();
  const note       = document.getElementById('new-note').value.trim();
  const mediaType  = document.getElementById('new-mediatype').value;
  const tagsRaw    = document.getElementById('new-tags').value;
  const tags       = tagsRaw.split(',').map(t => t.trim()).filter(Boolean);

  if (!concept || !feeling || !content) {
    toast('Concept, feeling and content are required.', 'error');
    return;
  }

  const btn = document.getElementById('btn-remember');
  btn.disabled = true;
  btn.innerHTML = '<span class="loading"></span> Remembering…';

  const ra = document.getElementById('new-memory-response');
  ra.classList.add('visible');
  ra.classList.remove('error');

  try {
    const mem = await POST('/memories', { concept, feeling, content, note, media_type: mediaType, tags });
    ra.innerHTML = `<div class="response-label">✦ Memory created</div>${JSON.stringify(mem, null, 2)}`;
    toast(`Memory saved: ${concept} / ${feeling}`, 'success');
    checkConnection();
  } catch (e) {
    ra.classList.add('error');
    ra.innerHTML = `<div class="response-label">✗ Error</div>${esc(e.detail || String(e))}`;
    toast('Error: ' + (e.detail || 'Unknown error'), 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span class="btn-icon">✦</span> Remember';
  }
});

/* ═══════════════════════════════════════════════════════════
   VIEW: BROWSE
   ═══════════════════════════════════════════════════════════ */

document.getElementById('btn-browse').addEventListener('click', async () => {
  const feeling     = document.getElementById('browse-feeling').value;
  const limit       = document.getElementById('browse-limit').value || 20;
  const oldestFirst = document.getElementById('browse-order').value;

  const container = document.getElementById('browse-results');
  loading(container);

  let path = `/memories?limit=${limit}&oldest_first=${oldestFirst}`;
  if (feeling) path += `&feeling=${encodeURIComponent(feeling)}`;

  try {
    const data = await GET(path);
    renderMemories(container, data);
  } catch (e) {
    showError(container, e.detail || 'Request failed');
  }
});

/* ═══════════════════════════════════════════════════════════
   VIEW: SEARCH
   ═══════════════════════════════════════════════════════════ */

document.getElementById('btn-search').addEventListener('click', doSearch);
document.getElementById('search-query').addEventListener('keydown', e => {
  if (e.key === 'Enter') doSearch();
});

async function doSearch() {
  const q     = document.getElementById('search-query').value.trim();
  const limit = document.getElementById('search-limit').value || 20;
  if (!q) { toast('Enter a search query.', 'info'); return; }

  const container = document.getElementById('search-results');
  loading(container);

  try {
    const data = await GET(`/memories/search?q=${encodeURIComponent(q)}&limit=${limit}`);
    const header = `<div style="margin-bottom:10px;font-size:10px;color:var(--muted);letter-spacing:.1em">
      ${data.length} result${data.length !== 1 ? 's' : ''} for <span style="color:var(--green)">"${esc(q)}"</span>
    </div>`;
    container.innerHTML = header;
    if (data.length) {
      container.innerHTML += data.map((m, i) => memoryCardHtml(m, i)).join('');
    } else {
      container.innerHTML += `<div class="empty-state">No results.</div>`;
    }
  } catch (e) {
    showError(container, e.detail || 'Search failed');
  }
}

document.getElementById('btn-tag-search').addEventListener('click', async () => {
  const tag       = document.getElementById('tag-query').value.trim();
  const limit     = document.getElementById('search-limit').value || 20;
  if (!tag) { toast('Enter a tag.', 'info'); return; }

  const container = document.getElementById('search-results');
  loading(container);

  try {
    const data = await GET(`/memories/by-tag/${encodeURIComponent(tag)}?limit=${limit}`);
    const header = `<div style="margin-bottom:10px;font-size:10px;color:var(--muted);letter-spacing:.1em">
      ${data.length} memor${data.length !== 1 ? 'ies' : 'y'} tagged <span style="color:var(--green)">#${esc(tag)}</span>
    </div>`;
    container.innerHTML = header + (data.length
      ? data.map((m, i) => memoryCardHtml(m, i)).join('')
      : '<div class="empty-state">No results.</div>');
  } catch (e) {
    showError(container, e.detail || 'Tag search failed');
  }
});

/* ═══════════════════════════════════════════════════════════
   VIEW: CONCEPTS
   ═══════════════════════════════════════════════════════════ */

let _currentConcept = null;

document.getElementById('btn-load-concepts').addEventListener('click', loadConcepts);

async function loadConcepts() {
  const container = document.getElementById('concepts-list');
  loading(container);
  try {
    const concepts = await GET('/concepts');
    if (!concepts.length) {
      container.innerHTML = '<div class="empty-state">No concepts yet.</div>';
      return;
    }
    container.innerHTML = concepts.map(c => {
      const feelingTags = Object.entries(c.feelings || {})
        .map(([f, n]) => `<span class="concept-feeling-tag">${f} ×${n}</span>`).join('');
      return `
        <div class="concept-card" data-concept="${esc(c.concept)}">
          <div class="memory-concept">${esc(c.concept)}</div>
          <div class="concept-count">${c.total} memor${c.total !== 1 ? 'ies' : 'y'}</div>
          <div class="concept-feelings">${feelingTags}</div>
        </div>`;
    }).join('');

    // Click to open detail
    container.querySelectorAll('.concept-card').forEach(card => {
      card.addEventListener('click', () => openConceptDetail(card.dataset.concept));
    });
  } catch (e) {
    showError(container, e.detail || 'Failed to load concepts');
  }
}

async function openConceptDetail(concept) {
  _currentConcept = concept;
  document.getElementById('detail-concept-name').textContent = concept;
  document.getElementById('concept-detail').style.display = 'block';
  document.getElementById('detail-results').innerHTML = '';
  document.getElementById('detail-feeling').value = '';
}

document.getElementById('btn-detail-fetch').addEventListener('click', async () => {
  if (!_currentConcept) return;
  const feeling = document.getElementById('detail-feeling').value;
  const limit   = document.getElementById('detail-limit').value || 20;
  const container = document.getElementById('detail-results');
  loading(container);

  let path = `/concepts/${encodeURIComponent(_currentConcept)}?limit=${limit}`;
  if (feeling) path += `&feeling=${encodeURIComponent(feeling)}`;

  try {
    const data = await GET(path);
    renderMemories(container, data);
  } catch (e) {
    showError(container, e.detail || 'Failed');
  }
});

document.getElementById('btn-close-detail').addEventListener('click', () => {
  document.getElementById('concept-detail').style.display = 'none';
  _currentConcept = null;
});

/* ═══════════════════════════════════════════════════════════
   VIEW: FEELINGS
   ═══════════════════════════════════════════════════════════ */

document.getElementById('btn-load-feelings').addEventListener('click', async () => {
  const chart = document.getElementById('feelings-chart');
  const list  = document.getElementById('feelings-list');
  chart.innerHTML = '<div class="empty-state"><span class="loading"></span> Loading…</div>';
  list.innerHTML  = '';

  try {
    const [dist, feelings] = await Promise.all([
      GET('/feelings/distribution'),
      GET('/feelings'),
    ]);

    // Bar chart
    const max = Math.max(...Object.values(dist), 1);
    const sorted = Object.entries(dist).sort((a, b) => b[1] - a[1]);
    chart.innerHTML = sorted.map(([f, n]) => `
      <div class="bar-row">
        <span class="bar-label">${FEELING_LABELS[f] || f}</span>
        <div class="bar-track">
          <div class="bar-fill feeling-bar" style="width:0" data-pct="${Math.round(n/max*100)}"></div>
        </div>
        <span class="bar-val">${n}</span>
      </div>`).join('');

    // Animate bars
    requestAnimationFrame(() => {
      chart.querySelectorAll('.bar-fill').forEach(bar => {
        bar.style.width = bar.dataset.pct + '%';
      });
    });

    // Feelings detail list
    list.innerHTML = feelings.map(f => `
      <div class="feeling-concept-card">
        <div class="feeling-concept-name">${FEELING_LABELS[f.feeling] || f.feeling}</div>
        <div class="feeling-concept-list">
          ${(f.concepts || []).map(c => `<span>${esc(c)}</span>`).join(' · ')}
        </div>
      </div>`).join('');

  } catch (e) {
    chart.innerHTML = '';
    showError(list, e.detail || 'Failed to load feelings');
  }
});

/* ═══════════════════════════════════════════════════════════
   VIEW: TIMELINE
   ═══════════════════════════════════════════════════════════ */

document.getElementById('btn-load-timeline').addEventListener('click', loadTimeline);
document.getElementById('timeline-concept').addEventListener('keydown', e => {
  if (e.key === 'Enter') loadTimeline();
});

async function loadTimeline() {
  const concept   = document.getElementById('timeline-concept').value.trim();
  if (!concept) { toast('Enter a concept name.', 'info'); return; }

  const container = document.getElementById('timeline-result');
  loading(container);

  try {
    const data = await GET(`/concepts/${encodeURIComponent(concept)}/timeline`);
    if (!data.length) {
      showError(container, `No timeline data for "${concept}"`);
      return;
    }

    const entries = data.map((entry, i) => {
      const tags = (entry.tags || []).map(t => `<span class="memory-tag">${esc(t)}</span>`).join('');
      return `
        <div class="timeline-entry" style="animation-delay:${i*40}ms">
          <div class="timeline-card">
            <div class="timeline-meta">
              ${feelingHtml(entry.feeling)}
              <span class="timeline-ts">${fmtDate(entry.timestamp)}</span>
            </div>
            ${entry.note ? `<div class="timeline-note">${esc(entry.note)}</div>` : ''}
            ${tags ? `<div class="timeline-tags">${tags}</div>` : ''}
          </div>
        </div>`;
    }).join('');

    container.innerHTML = `
      <div style="margin-bottom:14px;font-size:10px;color:var(--muted);letter-spacing:.1em">
        ${data.length} entries for <span style="color:var(--green)">${esc(concept)}</span>
      </div>
      <div class="timeline-track">${entries}</div>`;
  } catch (e) {
    showError(container, e.detail || 'Failed to load timeline');
  }
}

/* ═══════════════════════════════════════════════════════════
   VIEW: STATS
   ═══════════════════════════════════════════════════════════ */

document.getElementById('btn-load-stats').addEventListener('click', loadStats);

async function loadStats() {
  const grid = document.getElementById('stats-grid');
  loading(grid);
  try {
    const stats = await GET('/stats');
    updateSidebarStats(stats);

    const dist    = stats.distribution || {};
    const distHtml = Object.entries(dist)
      .sort((a,b) => b[1]-a[1])
      .map(([f,n]) => `<div class="storage-row">
        <span class="storage-key">${FEELING_LABELS[f] || f}</span>
        <span class="storage-val">${n}</span>
      </div>`).join('');

    const s    = stats.storage || {};
    const info = s.log_size_kb
      ? `<div class="storage-row"><span class="storage-key">Log file</span><span class="storage-val">${s.log_path || '—'}</span></div>
         <div class="storage-row"><span class="storage-key">Size</span><span class="storage-val">${s.log_size_kb} KB</span></div>
         <div class="storage-row"><span class="storage-key">Records</span><span class="storage-val">${s.total_records}</span></div>`
      : '';

    grid.innerHTML = `
      <div class="stat-card">
        <div class="stat-label">Total memories</div>
        <div class="stat-value">${(stats.total_memories || 0).toLocaleString()}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Concepts</div>
        <div class="stat-value">${stats.concepts || 0}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Feelings used</div>
        <div class="stat-value">${stats.feelings_used || 0}</div>
        <div class="stat-sub">of 15 total</div>
      </div>
      <div class="storage-info" style="grid-column:1/-1">
        <div class="storage-title">Emotional distribution</div>
        ${distHtml}
      </div>
      ${info ? `<div class="storage-info" style="grid-column:1/-1">
        <div class="storage-title">Storage</div>
        ${info}
      </div>` : ''}`;
  } catch (e) {
    showError(grid, e.detail || 'Failed to load stats');
  }
}

/* ═══════════════════════════════════════════════════════════
   VIEW: EXPORT
   ═══════════════════════════════════════════════════════════ */

let _exportData = null;

document.getElementById('btn-export').addEventListener('click', async () => {
  const concept  = document.getElementById('export-concept').value.trim();
  const feeling  = document.getElementById('export-feeling').value;
  const content  = document.getElementById('export-content').checked;
  const ra       = document.getElementById('export-result');

  ra.classList.add('visible');
  ra.classList.remove('error');
  ra.innerHTML = '<span class="loading"></span> Exporting…';

  let path = `/export?include_content=${content}`;
  if (concept) path += `&concept=${encodeURIComponent(concept)}`;
  if (feeling) path += `&feeling=${encodeURIComponent(feeling)}`;

  try {
    const data  = await GET(path);
    _exportData = data;
    const count = (data.memories || []).length;
    ra.innerHTML = `<div class="response-label">✓ ${count} memories exported</div>${JSON.stringify(data, null, 2)}`;
    toast(`Exported ${count} memories`, 'success');
  } catch (e) {
    ra.classList.add('error');
    ra.innerHTML = `<div class="response-label">✗ Error</div>${esc(e.detail || String(e))}`;
    toast('Export failed', 'error');
  }
});

document.getElementById('btn-download').addEventListener('click', () => {
  if (!_exportData) { toast('Run export first.', 'info'); return; }
  const blob = new Blob([JSON.stringify(_exportData, null, 2)], { type: 'application/json' });
  const a    = document.createElement('a');
  a.href     = URL.createObjectURL(blob);
  a.download = `mnheme_export_${new Date().toISOString().slice(0,10)}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
  toast('Download started', 'success');
});

/* ═══════════════════════════════════════════════════════════
   BOOT
   ═══════════════════════════════════════════════════════════ */

checkConnection();
