/* ═══════════════════════════════════════════════════════════
   MNHEME API CONSOLE — api.js
   Vanilla JS — zero dependencies
   ═══════════════════════════════════════════════════════════ */

'use strict';

/* ── Config ─────────────────────────────────────────────── */
let BASE_URL = 'http://localhost:8000';

/* ── Theme config ────────────────────────────────────────── */
const THEMES = [
  /* dark */
  { id: 'terminal',   label: 'Terminal',   dark: true,  bg: '#080c08', accent: '#4ade80' },
  { id: 'midnight',   label: 'Midnight',   dark: true,  bg: '#060810', accent: '#38bdf8' },
  { id: 'synthwave',  label: 'Synthwave',  dark: true,  bg: '#0d0515', accent: '#f472b6' },
  { id: 'dracula',    label: 'Dracula',    dark: true,  bg: '#1e1f29', accent: '#bd93f9' },
  { id: 'amber-crt',  label: 'Amber CRT',  dark: true,  bg: '#0a0800', accent: '#f59e0b' },
  { id: 'blood-moon', label: 'Blood Moon', dark: true,  bg: '#0c0608', accent: '#f87171' },
  { id: 'deep-ocean', label: 'Deep Ocean', dark: true,  bg: '#040e12', accent: '#2dd4bf' },
  { id: 'obsidian',   label: 'Obsidian',   dark: true,  bg: '#0f0f12', accent: '#e2e8f0' },
  { id: 'matrix',     label: 'Matrix',     dark: true,  bg: '#000000', accent: '#00ff41' },
  { id: 'dusk',       label: 'Dusk',       dark: true,  bg: '#0f0a14', accent: '#fb923c' },
  { id: 'neon-city',    label: 'Neon City',    dark: true,  bg: '#0a0f1f', accent: '#22c55e' },
  { id: 'cyberpunk',    label: 'Cyberpunk',    dark: true,  bg: '#0b0a1a', accent: '#facc15' },
  { id: 'void',         label: 'Void',         dark: true,  bg: '#050505', accent: '#a78bfa' },
  { id: 'ember',        label: 'Ember',        dark: true,  bg: '#120708', accent: '#fb7185' },
  { id: 'storm',        label: 'Storm',        dark: true,  bg: '#0c1118', accent: '#60a5fa' },
  { id: 'toxic',        label: 'Toxic',        dark: true,  bg: '#0a120a', accent: '#84cc16' },
  { id: 'galaxy',       label: 'Galaxy',       dark: true,  bg: '#0b0f2a', accent: '#818cf8' },
  { id: 'infrared',     label: 'Infrared',     dark: true,  bg: '#140a0a', accent: '#ef4444' },
  { id: 'deep-space',   label: 'Deep Space',   dark: true,  bg: '#020617', accent: '#38bdf8' },
  { id: 'hacker',       label: 'Hacker',       dark: true,  bg: '#000000', accent: '#10b981' },

  /* light */
  { id: 'sky',          label: 'Sky',          dark: false, bg: '#e0f2fe', accent: '#0284c7' },
  { id: 'sunrise',      label: 'Sunrise',      dark: false, bg: '#fff7ed', accent: '#f97316' },
  { id: 'blossom',      label: 'Blossom',      dark: false, bg: '#fff1f2', accent: '#db2777' },
  { id: 'ice',          label: 'Ice',          dark: false, bg: '#ecfeff', accent: '#0891b2' },
  { id: 'meadow',       label: 'Meadow',       dark: false, bg: '#f7fee7', accent: '#65a30d' },
  { id: 'cream',        label: 'Cream',        dark: false, bg: '#fffdf5', accent: '#a16207' },
  { id: 'cotton',       label: 'Cotton',       dark: false, bg: '#f9fafb', accent: '#6b7280' },
  { id: 'aqua',         label: 'Aqua',         dark: false, bg: '#ecfeff', accent: '#06b6d4' },
  { id: 'lemon',        label: 'Lemon',        dark: false, bg: '#fefce8', accent: '#ca8a04' },
  { id: 'orchid',       label: 'Orchid',       dark: false, bg: '#fdf4ff', accent: '#c026d3' },
  { id: 'paper',      label: 'Paper',      dark: false, bg: '#faf6f0', accent: '#5c3d11' },
  { id: 'arctic',     label: 'Arctic',     dark: false, bg: '#f0f7ff', accent: '#0369a1' },
  { id: 'rose',       label: 'Rose',       dark: false, bg: '#fff0f3', accent: '#9f0a30' },
  { id: 'solarized',  label: 'Solarized',  dark: false, bg: '#fdf6e3', accent: '#2aa198' },
  { id: 'forest',     label: 'Forest',     dark: false, bg: '#f0f7f0', accent: '#14532d' },
  { id: 'lavender',   label: 'Lavender',   dark: false, bg: '#f5f0ff', accent: '#5b21b6' },
  { id: 'sepia',      label: 'Sepia',      dark: false, bg: '#f7f0e6', accent: '#78350f' },
  { id: 'mint',       label: 'Mint',       dark: false, bg: '#f0fffe', accent: '#0f766e' },
  { id: 'sand',       label: 'Sand',       dark: false, bg: '#fdf8ef', accent: '#92400e' },
  { id: 'pearl',      label: 'Pearl',      dark: false, bg: '#f8f9fc', accent: '#312e81' },
];

function applyTheme(id) {
  const theme = THEMES.find(t => t.id === id) || THEMES[0];
  document.documentElement.setAttribute('data-theme', id);
  localStorage.setItem('mnheme-theme', id);
  const nameEl = document.getElementById('theme-current-name');
  if (nameEl) nameEl.textContent = theme.label;
  document.querySelectorAll('.theme-swatch').forEach(s => {
    s.classList.toggle('active', s.dataset.theme === id);
  });
}

function buildThemePicker() {
  const darkEl  = document.getElementById('swatches-dark');
  const lightEl = document.getElementById('swatches-light');
  const active  = document.documentElement.getAttribute('data-theme') || 'dracula';

  THEMES.forEach(t => {
    const sw = document.createElement('button');
    sw.className = 'theme-swatch' + (t.id === active ? ' active' : '');
    sw.dataset.theme = t.id;
    sw.title = t.label;
    sw.style.setProperty('--sw-bg',     t.bg);
    sw.style.setProperty('--sw-accent', t.accent);
    sw.addEventListener('click', () => applyTheme(t.id));
    (t.dark ? darkEl : lightEl).appendChild(sw);
  });
}

// Init from localStorage
(function () {
  const saved = localStorage.getItem('mnheme-theme') || 'dracula';
  const theme = THEMES.find(t => t.id === saved) || THEMES[0];
  document.documentElement.setAttribute('data-theme', theme.id);
  const nameEl = document.getElementById('theme-current-name');
  if (nameEl) nameEl.textContent = theme.label;
})();
buildThemePicker();


/* i18n — loaded from i18n.js (FEELINGS_I18N and UI_I18N are defined there) */

let _lang = localStorage.getItem('mnheme_lang') || 'en';


function ui(key, ...args) {
  const d = UI_I18N[_lang] || UI_I18N.en;
  const fn = d[key] ?? (UI_I18N.en[key]);
  return typeof fn === 'function' ? fn(...args) : (fn || key);
}

function feelingLabel(val) {
  return (FEELINGS_I18N[_lang] || FEELINGS_I18N.en)[val] || val;
}
const FEELING_LABELS = new Proxy({}, { get: (_, k) => feelingLabel(k) });

/* Apply all data-i18n attributes to DOM */
function applyI18n() {
  const u = UI_I18N[_lang] || UI_I18N.en;
  // textContent
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    if (u[key] !== undefined) el.textContent = typeof u[key] === 'function' ? u[key]() : u[key];
  });
  // placeholder
  document.querySelectorAll('[data-i18n-ph]').forEach(el => {
    const key = el.dataset.i18nPh;
    if (u[key] !== undefined) el.placeholder = u[key];
  });
}

function rebuildFeelingSelects() {
  const f = FEELINGS_I18N[_lang] || FEELINGS_I18N.en;
  const u = UI_I18N[_lang] || UI_I18N.en;
  document.querySelectorAll('.feeling-select').forEach(sel => {
    const mode = sel.dataset.mode || 'all';
    const cur  = sel.value;
    sel.innerHTML = '';
    const first = document.createElement('option');
    first.value = '';
    first.textContent = mode === 'select' ? u.selectFeeling
                      : mode === 'auto'   ? u.autoFeeling
                      : mode === 'all2'   ? u.allFeelings2
                      : u.allFeelings;
    sel.appendChild(first);
    Object.entries(f).forEach(([val, label]) => {
      const o = document.createElement('option');
      o.value = val; o.textContent = label;
      sel.appendChild(o);
    });
    if (cur && [...sel.options].some(o => o.value === cur)) sel.value = cur;
  });
  document.querySelectorAll('.style-select').forEach(sel => {
    const cur = sel.value;
    const u2 = UI_I18N[_lang] || UI_I18N.en;
    sel.innerHTML = `
      <option value="narrativo">${u2.styleNarrative}</option>
      <option value="analitico">${u2.styleAnalytical}</option>
      <option value="poetico">${u2.stylePoetic}</option>`;
    if (cur) sel.value = cur;
  });
}

function setLang(lang) {
  if (!UI_I18N[lang]) return;
  _lang = lang;
  localStorage.setItem('mnheme_lang', lang);
  document.querySelectorAll('.lang-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.lang === lang));
  applyI18n();
  rebuildFeelingSelects();
  // Re-render any feeling chips already visible in the DOM
  document.querySelectorAll('.memory-feeling[data-feeling]').forEach(el => {
    el.textContent = feelingLabel(el.dataset.feeling);
    el.className = `memory-feeling feeling-${CSS.escape(el.dataset.feeling)}`;
  });
}

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
  const label = feelingLabel(feeling);
  return `<span class="memory-feeling feeling-${CSS.escape(feeling)}" data-feeling="${esc(feeling)}">${label}</span>`;
}

function memoryContentHtml(m) {
  const mt      = (m.media_type || 'text').toLowerCase();
  const content = m.content || '';

  // Rileva se il content è un data URL o base64 puro
  const isDataUrl = content.startsWith('data:');
  const isB64     = !isDataUrl && mt !== 'text' && content.length > 100 && !/\s/.test(content.slice(0, 60));

  // Ricostruisci il src URL
  let src = '';
  if (isDataUrl) {
    src = content;
  } else if (isB64) {
    const mimeMap = { image: 'image/jpeg', video: 'video/mp4', audio: 'audio/mpeg', doc: 'application/octet-stream' };
    src = `data:${mimeMap[mt] || 'application/octet-stream'};base64,${content}`;
  }

  if (mt === 'image' && src) {
    return `<div class="memory-media-wrap">
      <img class="memory-img" src="${src}" alt="memory image" loading="lazy"
           onclick="this.classList.toggle('memory-img-full')">
    </div>`;
  }

  if (mt === 'video' && src) {
    return `<div class="memory-media-wrap">
      <video class="memory-video" controls preload="metadata" src="${src}"></video>
    </div>`;
  }

  if (mt === 'audio' && src) {
    return `<div class="memory-media-wrap">
      <audio class="memory-audio" controls preload="metadata" src="${src}"></audio>
    </div>`;
  }

  if (mt === 'doc' && src) {
    // Dimensione stimata dal b64
    const kb = Math.round(content.length * 0.75 / 1024);
    return `<div class="memory-doc-block">
      <span class="memory-doc-icon">📄</span>
      <span class="memory-doc-label">Document (~${kb} KB)</span>
      <a class="memory-doc-dl" href="${src}" download="document">↓ Download</a>
    </div>`;
  }

  // Testo puro (o fallback)
  return `<div class="memory-content">${esc(content)}</div>`;
}

function memoryCardHtml(m, i) {
  const tags   = (m.tags || []).map(t => `<span class="memory-tag">${esc(t)}</span>`).join('');
  const tagRow = tags ? `<div class="memory-tags">${tags}</div>` : '';
  const note   = m.note ? `<div class="memory-note">${esc(m.note)}</div>` : '';
  const mt     = (m.media_type || 'text').toLowerCase();
  const mtClass = mt !== 'text' ? ` media-${mt}` : '';
  return `
    <div class="memory-card${mtClass}" style="animation-delay:${i*30}ms">
      <div class="memory-card-header">
        <span class="memory-concept">${esc(m.concept)}</span>
        ${feelingHtml(m.feeling)}
        <span class="memory-mediatype">${mt.toUpperCase()}</span>
        <span class="memory-ts">${fmtDate(m.timestamp)}</span>
      </div>
      ${memoryContentHtml(m)}
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

/* ── Markdown renderer ───────────────────────────────────────
   Converts markdown to safe HTML. Falls back gracefully if the
   input contains no markdown — plain text is preserved as-is.
   Supported: headings, bold, italic, inline code, code blocks,
   blockquotes, unordered/ordered lists, horizontal rules, links.
   ─────────────────────────────────────────────────────────── */
function renderMarkdown(str) {
  if (!str) return '';
  let s = String(str);

  // Escape HTML first so injected tags are inert
  s = s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

  // Fenced code blocks  ```lang\n...\n```
  s = s.replace(/```[\w]*\n?([\s\S]*?)```/g, (_, code) =>
    `<pre class="md-code"><code>${code.trim()}</code></pre>`);

  // Inline code  `code`
  s = s.replace(/`([^`\n]+)`/g, '<code class="md-inline-code">$1</code>');

  // Headings  ### H3 / ## H2 / # H1
  s = s.replace(/^### (.+)$/gm, '<h3 class="md-h3">$1</h3>');
  s = s.replace(/^## (.+)$/gm,  '<h2 class="md-h2">$1</h2>');
  s = s.replace(/^# (.+)$/gm,   '<h1 class="md-h1">$1</h1>');

  // Blockquote  > text
  s = s.replace(/^&gt; (.+)$/gm, '<blockquote class="md-blockquote">$1</blockquote>');

  // Horizontal rule  --- / ***
  s = s.replace(/^[-*]{3,}\s*$/gm, '<hr class="md-hr">');

  // Bold  **text** or __text__
  s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/__(.+?)__/g,     '<strong>$1</strong>');

  // Italic  *text* or _text_
  s = s.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');
  s = s.replace(/_([^_\n]+)_/g,   '<em>$1</em>');

  // Links  [label](url)
  s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g,
    '<a class="md-link" href="$2" target="_blank" rel="noopener">$1</a>');

  // Unordered lists  - item / * item
  s = s.replace(/((?:^[-*] .+\n?)+)/gm, match => {
    const items = match.trim().split('\n')
      .map(l => `<li>${l.replace(/^[-*] /, '')}</li>`).join('');
    return `<ul class="md-ul">${items}</ul>`;
  });

  // Ordered lists  1. item
  s = s.replace(/((?:^\d+\. .+\n?)+)/gm, match => {
    const items = match.trim().split('\n')
      .map(l => `<li>${l.replace(/^\d+\. /, '')}</li>`).join('');
    return `<ol class="md-ol">${items}</ol>`;
  });

  // Paragraphs — wrap blocks separated by blank lines
  // (skip lines that are already block-level HTML)
  const blockTags = /^<(h[1-3]|ul|ol|li|pre|blockquote|hr)/;
  s = s.split(/\n{2,}/).map(block => {
    block = block.trim();
    if (!block) return '';
    if (blockTags.test(block)) return block;
    // Single newlines within a paragraph → <br>
    return `<p class="md-p">${block.replace(/\n/g,'<br>')}</p>`;
  }).join('\n');

  return s;
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
  _applyMediaType('text');
  _clearFileSelection();
  document.getElementById('new-file-input').value = '';
  const ra = document.getElementById('new-memory-response');
  ra.classList.remove('visible','error');
  ra.innerHTML = '';
});

/* ═══════════════════════════════════════════════════════════
   MEDIA TYPE — dynamic content area
   ═══════════════════════════════════════════════════════════ */

const MEDIA_CONFIG = {
  text:  { label: 'Content',   hint: '',                          icon: '✦', accept: '' },
  image: { label: 'Image file', hint: 'jpg, png, gif, webp, svg', icon: '⬆', accept: 'image/*' },
  video: { label: 'Video file', hint: 'mp4, webm, mov, avi',      icon: '⬆', accept: 'video/*' },
  audio: { label: 'Audio file', hint: 'mp3, wav, ogg, m4a, flac', icon: '⬆', accept: 'audio/*' },
  doc:   { label: 'Document',   hint: 'pdf, docx, txt, md',       icon: '⬆', accept: '.pdf,.doc,.docx,.txt,.md,application/pdf' },
};

let _selectedFile = null;

function _applyMediaType(mt) {
  const isText  = mt === 'text';
  const fieldT  = document.getElementById('field-content-text');
  const fieldF  = document.getElementById('field-content-file');
  if (!fieldT || !fieldF) return;

  fieldT.style.display = isText ? '' : 'none';
  fieldF.style.display = isText ? 'none' : '';

  if (!isText) {
    const cfg = MEDIA_CONFIG[mt] || MEDIA_CONFIG.doc;
    document.getElementById('file-field-label').textContent = cfg.label;
    document.getElementById('file-drop-hint').textContent   = cfg.hint;
    document.getElementById('file-drop-icon').textContent   = cfg.icon;
    document.getElementById('new-file-input').accept        = cfg.accept;
    // reset preview whenever media type changes
    _clearFileSelection();
  }
}

function _clearFileSelection() {
  _selectedFile = null;
  document.getElementById('file-selected').style.display   = 'none';
  document.getElementById('file-drop-inner').style.display = '';
  document.getElementById('file-preview-wrap').style.display = 'none';
  ['file-preview-img','file-preview-video','file-preview-audio'].forEach(id => {
    const el = document.getElementById(id);
    el.style.display = 'none';
    el.src = '';
  });
  document.getElementById('file-preview-doc').style.display = 'none';
  document.getElementById('new-content-file-data').value   = '';
  document.getElementById('file-char-count').textContent   = '';
}

function _handleFileSelect(file) {
  if (!file) return;
  _selectedFile = file;

  const mt   = document.getElementById('new-mediatype').value;
  const name = file.name;
  const size = file.size > 1024*1024
    ? (file.size / (1024*1024)).toFixed(2) + ' MB'
    : (file.size / 1024).toFixed(1) + ' KB';

  document.getElementById('file-drop-inner').style.display = 'none';
  document.getElementById('file-selected').style.display   = 'flex';
  document.getElementById('file-selected-name').textContent = name;
  document.getElementById('file-selected-size').textContent = size;

  // Preview
  const wrap = document.getElementById('file-preview-wrap');
  wrap.style.display = '';

  const reader = new FileReader();
  reader.onload = (e) => {
    const dataUrl  = e.target.result;
    const b64      = dataUrl.split(',')[1];
    document.getElementById('new-content-file-data').value = dataUrl; // store full dataURL
    document.getElementById('file-char-count').textContent = `${(b64.length / 1024).toFixed(1)} KB base64`;

    ['file-preview-img','file-preview-video','file-preview-audio'].forEach(id => {
      document.getElementById(id).style.display = 'none';
    });
    document.getElementById('file-preview-doc').style.display = 'none';

    if (mt === 'image') {
      const img = document.getElementById('file-preview-img');
      img.src = dataUrl; img.style.display = '';
    } else if (mt === 'video') {
      const vid = document.getElementById('file-preview-video');
      vid.src = dataUrl; vid.style.display = '';
    } else if (mt === 'audio') {
      const aud = document.getElementById('file-preview-audio');
      aud.src = dataUrl; aud.style.display = '';
    } else {
      const doc = document.getElementById('file-preview-doc');
      doc.textContent = `📄 ${name}`;
      doc.style.display = '';
    }
  };
  reader.readAsDataURL(file);
}

document.getElementById('new-mediatype').addEventListener('change', function () {
  _applyMediaType(this.value);
});

// Click to open file dialog
document.getElementById('file-drop-zone').addEventListener('click', (e) => {
  if (e.target.id === 'file-clear-btn') return;
  document.getElementById('new-file-input').click();
});

document.getElementById('new-file-input').addEventListener('change', function () {
  if (this.files[0]) _handleFileSelect(this.files[0]);
});

document.getElementById('file-clear-btn').addEventListener('click', (e) => {
  e.stopPropagation();
  _clearFileSelection();
  document.getElementById('new-file-input').value = '';
});

// Drag and drop
const _dz = document.getElementById('file-drop-zone');
_dz.addEventListener('dragover',  (e) => { e.preventDefault(); _dz.classList.add('drag-over'); });
_dz.addEventListener('dragleave', ()  => { _dz.classList.remove('drag-over'); });
_dz.addEventListener('drop',      (e) => {
  e.preventDefault();
  _dz.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) _handleFileSelect(file);
});


document.getElementById('btn-remember').addEventListener('click', async () => {
  const concept    = document.getElementById('new-concept').value.trim();
  const feeling    = document.getElementById('new-feeling').value;
  const mediaType  = document.getElementById('new-mediatype').value;
  const note       = document.getElementById('new-note').value.trim();
  const tagsRaw    = document.getElementById('new-tags').value;
  const tags       = tagsRaw.split(',').map(t => t.trim()).filter(Boolean);

  // Content depends on media type
  let content;
  if (mediaType === 'text') {
    content = document.getElementById('new-content').value.trim();
  } else {
    content = document.getElementById('new-content-file-data').value;
    if (!content) {
      toast('Please select a file first.', 'error');
      return;
    }
  }

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
          <div class="concept-card-actions">
            <button class="concept-action-btn timeline-btn" data-concept="${esc(c.concept)}" title="Open Timeline">
              <span>⟿</span> Timeline
            </button>
            <button class="concept-action-btn reflect-btn" data-concept="${esc(c.concept)}" title="Reflect with Brain">
              <span>⟳</span> Reflect
            </button>
          </div>
        </div>`;
    }).join('');

    // Click card body → open detail; click action buttons → navigate
    container.querySelectorAll('.concept-card').forEach(card => {
      card.addEventListener('click', () => openConceptDetail(card.dataset.concept));
    });

    container.querySelectorAll('.timeline-btn').forEach(btn => {
      btn.addEventListener('click', e => {
        e.stopPropagation();
        goToTimeline(btn.dataset.concept);
      });
    });

    container.querySelectorAll('.reflect-btn').forEach(btn => {
      btn.addEventListener('click', e => {
        e.stopPropagation();
        goToReflect(btn.dataset.concept);
      });
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

/* Navigate to Timeline view and trigger load for a given concept */
function goToTimeline(concept) {
  // Switch nav + view
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  const navBtn = document.querySelector('.nav-btn[data-view="timeline"]');
  if (navBtn) navBtn.classList.add('active');
  const view = document.getElementById('view-timeline');
  if (view) view.classList.add('active');

  // Pre-fill and fire
  document.getElementById('timeline-concept').value = concept;
  loadTimeline();
}

/* Navigate to Reflect view and trigger reflection for a given concept */
function goToReflect(concept) {
  // Switch nav + view
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  const navBtn = document.querySelector('.nav-btn[data-view="reflect"]');
  if (navBtn) navBtn.classList.add('active');
  const view = document.getElementById('view-reflect');
  if (view) view.classList.add('active');

  // Pre-fill and fire
  document.getElementById('reflect-concept').value = concept;
  checkBrainStatus().then(() => {
    document.getElementById('btn-reflect').click();
  });
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
   VIEW: GRAPH — D3 force simulation
   ═══════════════════════════════════════════════════════════ */

/* ── Colori feeling ── */
const FEELING_COLORS = {
  amore     : '#ff6b9d', gioia       : '#ffd93d', serenità   : '#6bcb77',
  orgoglio  : '#4d96ff', nostalgia   : '#c77dff', malinconia : '#9d9d9d',
  ansia     : '#ff9f43', paura       : '#ee5a24', rabbia     : '#e74c3c',
  tristezza : '#74b9ff', vergogna    : '#a29bfe', solitudine : '#636e72',
  gratitudine:'#00b894', speranza    : '#00cec9', sorpresa   : '#fdcb6e',
  neutro    : '#b2bec3',
};
const FEELING_COLOR_DEFAULT = '#b2bec3';

function feelingColor(f) {
  return FEELING_COLORS[(f||'').toLowerCase()] || FEELING_COLOR_DEFAULT;
}

/* ── Stato grafo ── */
let _graphSim      = null;   // d3 simulation
let _graphData     = null;   // { nodes, links }
let _graphMode     = 'concept';
let _graphZoom     = null;

/* ── Util: troncatura ── */
const trunc = (s, n=28) => s && s.length > n ? s.slice(0, n) + '…' : (s || '');

/* ── Build graph data from memories ── */
function buildGraphData(memories, mode) {
  const nodeMap  = new Map();   // id → node
  const linkMap  = new Map();   // "a|b" → link

  const addNode = (id, data) => {
    if (!nodeMap.has(id)) nodeMap.set(id, { id, ...data });
  };
  const addLink = (a, b, type, label='') => {
    if (a === b) return;
    const key = a < b ? `${a}|${b}` : `${b}|${a}`;
    if (linkMap.has(key)) {
      linkMap.get(key).strength = Math.min(linkMap.get(key).strength + 0.15, 1);
    } else {
      linkMap.set(key, { source: a, target: b, type, label, strength: 0.4 });
    }
  };

  // ── Memory nodes (always added) ──
  memories.forEach(m => {
    addNode(m.memory_id, {
      kind    : 'memory',
      concept : m.concept,
      feeling : m.feeling,
      content : m.content,
      media_type: m.media_type || 'text',
      tags    : m.tags || [],
      ts      : m.timestamp,
      color   : feelingColor(m.feeling),
      radius  : 9,
      label   : trunc(m.concept, 18),
    });
  });

  if (mode === 'concept' || mode === 'all') {
    // Group by concept: link memories sharing the same concept
    const byConceptMap = new Map();
    memories.forEach(m => {
      if (!byConceptMap.has(m.concept)) byConceptMap.set(m.concept, []);
      byConceptMap.get(m.concept).push(m.memory_id);
    });
    byConceptMap.forEach((ids, concept) => {
      if (ids.length < 2) return;
      // Add a concept hub node
      const hubId = `__concept__${concept}`;
      addNode(hubId, {
        kind   : 'concept',
        label  : concept,
        color  : '#4d96ff',
        radius : 18,
        concept,
      });
      ids.forEach(id => addLink(id, hubId, 'concept', concept));
    });
  }

  if (mode === 'feeling' || mode === 'all') {
    const byFeelingMap = new Map();
    memories.forEach(m => {
      if (!byFeelingMap.has(m.feeling)) byFeelingMap.set(m.feeling, []);
      byFeelingMap.get(m.feeling).push(m.memory_id);
    });
    byFeelingMap.forEach((ids, feeling) => {
      if (ids.length < 2) return;
      const hubId = `__feeling__${feeling}`;
      addNode(hubId, {
        kind    : 'feeling',
        label   : feeling,
        color   : feelingColor(feeling),
        radius  : 16,
        feeling,
      });
      ids.forEach(id => addLink(id, hubId, 'feeling', feeling));
    });
  }

  if (mode === 'tag' || mode === 'all') {
    const byTagMap = new Map();
    memories.forEach(m => {
      (m.tags || []).forEach(tag => {
        if (!byTagMap.has(tag)) byTagMap.set(tag, []);
        byTagMap.get(tag).push(m.memory_id);
      });
    });
    byTagMap.forEach((ids, tag) => {
      if (ids.length < 2) return;
      const hubId = `__tag__${tag}`;
      addNode(hubId, {
        kind   : 'tag',
        label  : tag,
        color  : '#ffd93d',
        radius : 13,
        tag,
      });
      ids.forEach(id => addLink(id, hubId, 'tag', tag));
    });
  }

  return {
    nodes : [...nodeMap.values()],
    links : [...linkMap.values()],
  };
}

/* ── Render legend ── */
function renderGraphLegend(mode, memories) {
  const el = document.getElementById('graph-legend');
  if (!el) return;
  const items = [];

  if (mode === 'feeling' || mode === 'all') {
    const feelings = [...new Set(memories.map(m => m.feeling))];
    feelings.forEach(f => {
      items.push(`<span class="graph-legend-item">
        <span class="graph-legend-dot" style="background:${feelingColor(f)}"></span>${esc(f)}
      </span>`);
    });
  }

  const kindLabels = {
    memory  : ['◉', '#888',    'Memory'],
    concept : ['⬡', '#4d96ff', 'Concept hub'],
    feeling : ['⬡', '#ff6b9d', 'Feeling hub'],
    tag     : ['⬡', '#ffd93d', 'Tag hub'],
  };
  if (mode === 'all') {
    ['concept','feeling','tag'].forEach(k => {
      const [sym, col, lbl] = kindLabels[k];
      items.push(`<span class="graph-legend-item">
        <span class="graph-legend-dot" style="background:${col}"></span>${lbl}
      </span>`);
    });
  }

  el.innerHTML = items.join('');
}

/* ── Main render ── */
function renderGraph(memories, mode) {
  const wrap  = document.getElementById('graph-wrap');
  const svg   = document.getElementById('graph-svg');
  const empty = document.getElementById('graph-empty');
  const tt    = document.getElementById('graph-tooltip');

  empty.style.display = 'none';
  svg.style.display   = 'block';

  // Legge le dimensioni reali dopo il layout — usa getBoundingClientRect
  // che funziona anche con position:absolute e unità percentuali
  const rect = wrap.getBoundingClientRect();
  const W    = rect.width  > 0 ? rect.width  : 900;
  const H    = rect.height > 0 ? rect.height : 480;

  // Clear previous
  if (_graphSim) { _graphSim.stop(); _graphSim = null; }
  d3.select(svg).selectAll('*').remove();

  const data = buildGraphData(memories, mode);
  _graphData = data;

  if (!data.nodes.length) {
    empty.style.display = '';
    svg.style.display   = 'none';
    return;
  }

  const svgEl = d3.select(svg)
    .attr('width',   W)
    .attr('height',  H)
    .attr('viewBox', `0 0 ${W} ${H}`)
    .style('width',  '100%')
    .style('height', '100%');

  // Defs: arrowhead marker
  const defs = svgEl.append('defs');
  ['concept','feeling','tag','all'].forEach(type => {
    const color = type === 'concept' ? '#4d96ff'
                : type === 'feeling' ? '#ff6b9d'
                : type === 'tag'     ? '#ffd93d'
                : '#555';
    defs.append('marker')
      .attr('id',           `arrow-${type}`)
      .attr('viewBox',      '0 -4 10 8')
      .attr('refX',         20)
      .attr('refY',         0)
      .attr('markerWidth',  6)
      .attr('markerHeight', 6)
      .attr('orient',       'auto')
      .append('path')
        .attr('d',    'M0,-4L10,0L0,4')
        .attr('fill', color)
        .attr('opacity', 0.5);
  });

  // Zoom container
  const g = svgEl.append('g').attr('class', 'graph-g');
  _graphZoom = d3.zoom()
    .scaleExtent([0.15, 4])
    .on('zoom', (e) => g.attr('transform', e.transform));
  svgEl.call(_graphZoom);

  // Force simulation
  _graphSim = d3.forceSimulation(data.nodes)
    .force('link',   d3.forceLink(data.links)
      .id(d => d.id)
      .distance(d => {
        if (d.type === 'concept') return 90;
        if (d.type === 'feeling') return 80;
        return 70;
      })
      .strength(d => d.strength))
    .force('charge', d3.forceManyBody()
      .strength(d => d.kind === 'memory' ? -180 : -320))
    .force('center', d3.forceCenter(W / 2, H / 2))
    .force('collide', d3.forceCollide(d => d.radius + 8))
    .alphaDecay(0.025);

  // Links
  const linkColor = t => t === 'concept' ? '#4d96ff44'
                       : t === 'feeling' ? '#ff6b9d44'
                       : t === 'tag'     ? '#ffd93d44'
                       : '#55555544';

  const link = g.append('g').attr('class','graph-links')
    .selectAll('line')
    .data(data.links)
    .join('line')
      .attr('stroke',        d => linkColor(d.type))
      .attr('stroke-width',  d => 1 + d.strength * 2)
      .attr('stroke-dasharray', d => d.type === 'tag' ? '4,3' : null);

  // Nodes
  const node = g.append('g').attr('class','graph-nodes')
    .selectAll('g')
    .data(data.nodes)
    .join('g')
      .attr('class', d => `graph-node graph-node-${d.kind}`)
      .call(d3.drag()
        .on('start', (e, d) => {
          if (!e.active) _graphSim.alphaTarget(0.3).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on('drag',  (e, d) => { d.fx = e.x; d.fy = e.y; })
        .on('end',   (e, d) => {
          if (!e.active) _graphSim.alphaTarget(0);
          d.fx = null; d.fy = null;
        })
      );

  // Circle
  node.append('circle')
    .attr('r',           d => d.radius)
    .attr('fill',        d => d.color + (d.kind === 'memory' ? 'cc' : 'ee'))
    .attr('stroke',      d => d.color)
    .attr('stroke-width',d => d.kind === 'memory' ? 1.5 : 2.5)
    .attr('class',       'graph-circle');

  // Icon inside hub nodes
  node.filter(d => d.kind !== 'memory')
    .append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('font-size', d => d.kind === 'concept' ? 11 : 9)
      .attr('fill', '#fff')
      .attr('pointer-events', 'none')
      .text(d => d.kind === 'concept' ? '◈' : d.kind === 'feeling' ? '◉' : '⬡');

  // Label below node
  node.append('text')
    .attr('class', 'graph-label')
    .attr('text-anchor', 'middle')
    .attr('dy', d => d.radius + 12)
    .attr('font-size', d => d.kind === 'memory' ? 9 : 10)
    .attr('fill', d => d.kind === 'memory' ? '#aaa' : '#ddd')
    .attr('pointer-events', 'none')
    .text(d => d.label || '');

  // Tooltip + click
  node.on('mouseover', (e, d) => {
      tt.style.display = '';
      let html = `<b>${esc(d.label)}</b>`;
      if (d.kind === 'memory') {
        const mt = (d.media_type || 'text').toUpperCase();
        const preview = d.content && d.content.startsWith('data:')
          ? `[${mt} file]`
          : trunc(d.content || '', 80);
        html += `<br><span style="color:${d.color}">${esc(d.feeling)}</span>`;
        html += `<br><span style="opacity:.6">${esc(preview)}</span>`;
        if (d.tags?.length) html += `<br>${d.tags.map(t=>`<span class="graph-tt-tag">${esc(t)}</span>`).join('')}`;
      } else {
        html += ` <span style="opacity:.5">(${d.kind})</span>`;
      }
      tt.innerHTML = html;
    })
    .on('mousemove', (e) => {
      const rect = wrap.getBoundingClientRect();
      let x = e.clientX - rect.left + 14;
      let y = e.clientY - rect.top  - 10;
      if (x + 200 > W) x -= 220;
      tt.style.left = x + 'px';
      tt.style.top  = y + 'px';
    })
    .on('mouseout',  ()  => { tt.style.display = 'none'; })
    .on('click', (e, d) => {
      e.stopPropagation();
      showGraphDetail(d, memories);
    });

  svgEl.on('click', () => {
    document.getElementById('graph-detail').style.display = 'none';
  });

  // Simulation tick
  _graphSim.on('tick', () => {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);
    node.attr('transform', d => `translate(${d.x},${d.y})`);
  });

  renderGraphLegend(mode, memories);
}

/* ── Detail panel ── */
function showGraphDetail(d, memories) {
  const panel = document.getElementById('graph-detail');
  const title = document.getElementById('graph-detail-title');
  const body  = document.getElementById('graph-detail-body');

  title.textContent = d.label;
  panel.style.display = '';

  if (d.kind === 'memory') {
    const m = memories.find(m => m.memory_id === d.id);
    if (!m) return;
    const mt = (m.media_type || 'text').toLowerCase();
    const isMedia = mt !== 'text';
    const contentHtml = isMedia
      ? memoryContentHtml(m)
      : `<div class="graph-detail-content">${esc(m.content)}</div>`;

    body.innerHTML = `
      <div class="graph-detail-chips">
        <span class="perceive-chip concept">◈ ${esc(m.concept)}</span>
        <span class="perceive-chip feeling" style="background:${feelingColor(m.feeling)}22;border-color:${feelingColor(m.feeling)}66;color:${feelingColor(m.feeling)}">${esc(m.feeling)}</span>
        ${mt !== 'text' ? `<span class="perceive-chip media-type">${mt.toUpperCase()}</span>` : ''}
      </div>
      ${contentHtml}
      ${m.note ? `<div class="graph-detail-note">${esc(m.note)}</div>` : ''}
      ${m.tags?.length ? `<div class="memory-tags">${m.tags.map(t=>`<span class="memory-tag">${esc(t)}</span>`).join('')}</div>` : ''}
      <div class="memory-id">${m.memory_id}</div>`;
  } else {
    // Hub node — list connected memories
    const related = memories.filter(m => {
      if (d.kind === 'concept') return m.concept === d.concept;
      if (d.kind === 'feeling') return m.feeling === d.feeling;
      if (d.kind === 'tag')     return (m.tags||[]).includes(d.tag);
      return false;
    });
    body.innerHTML = `<div class="graph-detail-hub-count">${related.length} memories</div>` +
      related.map(m => `
        <div class="graph-detail-mem-item">
          <span class="graph-detail-mem-dot" style="background:${feelingColor(m.feeling)}"></span>
          <span class="graph-detail-mem-text">${esc(trunc(m.content?.startsWith('data:') ? `[${(m.media_type||'file').toUpperCase()}]` : m.content, 60))}</span>
        </div>`).join('');
  }
}

/* ── Load + wire controls ── */
let _graphMemories = [];

async function loadGraph() {
  const btn     = document.getElementById('btn-graph-load');
  const wrap    = document.getElementById('graph-wrap');
  const empty   = document.getElementById('graph-empty');
  const feeling = document.getElementById('graph-feeling-filter').value;
  const concept = document.getElementById('graph-concept-filter').value.trim();
  const limit   = parseInt(document.getElementById('graph-limit').value) || 60;

  btn.disabled = true;
  btn.innerHTML = `<span class="loading"></span> ${ui('graphLoading') || 'Loading…'}`;
  empty.innerHTML = `<span class="graph-empty-icon">⬡</span><span>${ui('graphLoading') || 'Loading…'}</span>`;
  empty.style.display = '';
  document.getElementById('graph-svg').style.display = 'none';

  try {
    let path = `/memories?limit=${limit}&oldest_first=false`;
    if (feeling) path += `&feeling=${encodeURIComponent(feeling)}`;
    let memories = await GET(path);

    if (concept) {
      memories = memories.filter(m =>
        m.concept.toLowerCase().includes(concept.toLowerCase())
      );
    }

    _graphMemories = memories;

    if (!memories.length) {
      empty.innerHTML = `<span class="graph-empty-icon">◎</span><span>${ui('graphNoMemories') || 'No memories match the current filters.'}</span>`;
      return;
    }

    // rAF: aspetta che il browser abbia fatto il layout della view
    requestAnimationFrame(() => {
      renderGraph(memories, _graphMode);
    });
    toast(ui('graphToastLoaded', memories.length) || `Graph: ${memories.length} nodes loaded`, 'success');
  } catch(e) {
    empty.innerHTML = `<span class="graph-empty-icon">✗</span><span>${esc(e.detail || String(e))}</span>`;
    toast((ui('graphToastFail') || 'Graph load failed') + ': ' + (e.detail || String(e)), 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span class="btn-icon">⬡</span> ${ui('graphBtnLoad') || 'Load graph'}`;
  }
}

document.getElementById('btn-graph-load').addEventListener('click', loadGraph);

document.getElementById('graph-detail-close').addEventListener('click', () => {
  document.getElementById('graph-detail').style.display = 'none';
});

// Mode buttons
document.querySelectorAll('.graph-mode-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.graph-mode-btn').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    _graphMode = this.dataset.mode;
    if (_graphMemories.length) {
      requestAnimationFrame(() => renderGraph(_graphMemories, _graphMode));
    }
  });
});

// Fit / reset zoom
function graphFitZoom() {
  const svg  = document.getElementById('graph-svg');
  const wrap = document.getElementById('graph-wrap');
  if (!_graphZoom || !svg) return;
  d3.select(svg).transition().duration(400)
    .call(_graphZoom.transform, d3.zoomIdentity
      .translate(wrap.clientWidth/2, wrap.clientHeight/2)
      .scale(0.9));
}

// Reload on view enter
document.querySelectorAll('.nav-btn[data-view="graph"]').forEach(btn => {
  btn.addEventListener('click', () => {
    // Populate feeling filter if empty
    const sel = document.getElementById('graph-feeling-filter');
    if (sel && sel.options.length <= 1) {
      populateFeelingSelect(sel);
    }
  });
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
   IMPORT — JSON restore
   ═══════════════════════════════════════════════════════════ */

let _importData = null;

function _setImportFile(file) {
  if (!file || !file.name.endsWith('.json')) {
    toast('Please select a valid .json file.', 'error');
    return;
  }
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result);
      // Accept both array and {memories:[...]} shapes
      const memories = Array.isArray(data) ? data : (data.memories || data.records || []);
      if (!Array.isArray(memories)) throw new Error('Unrecognized format');

      _importData = memories;
      const size = file.size > 1024 ? (file.size/1024).toFixed(1)+' KB' : file.size+' B';

      document.getElementById('import-drop-inner').style.display  = 'none';
      document.getElementById('import-file-selected').style.display = 'flex';
      document.getElementById('import-file-name').textContent = file.name;
      document.getElementById('import-file-size').textContent = size;

      // Preview stats
      const concepts = [...new Set(memories.map(m => m.concept).filter(Boolean))];
      const feelings = [...new Set(memories.map(m => m.feeling).filter(Boolean))];
      const preview  = document.getElementById('import-preview');
      document.getElementById('import-preview-meta').innerHTML =
        `<span class="import-stat"><b>${memories.length}</b> memories</span>` +
        `<span class="import-stat"><b>${concepts.length}</b> concepts</span>` +
        `<span class="import-stat"><b>${feelings.length}</b> feelings</span>`;
      preview.style.display = '';

      document.getElementById('btn-import').disabled = false;
      toast(`Loaded ${memories.length} memories from file`, 'success');
    } catch (err) {
      toast('Invalid JSON or unrecognized format: ' + err.message, 'error');
    }
  };
  reader.readAsText(file);
}

function _clearImportFile() {
  _importData = null;
  document.getElementById('import-drop-inner').style.display    = '';
  document.getElementById('import-file-selected').style.display = 'none';
  document.getElementById('import-preview').style.display       = 'none';
  document.getElementById('import-file-input').value            = '';
  document.getElementById('btn-import').disabled                = true;
  const ra = document.getElementById('import-result');
  ra.classList.remove('visible','error');
  ra.innerHTML = '';
}

// Drop zone — click
const _idz = document.getElementById('import-drop-zone');
_idz.addEventListener('click', (e) => {
  if (e.target.id === 'import-file-clear') return;
  document.getElementById('import-file-input').click();
});
document.getElementById('import-file-input').addEventListener('change', function() {
  if (this.files[0]) _setImportFile(this.files[0]);
});
document.getElementById('import-file-clear').addEventListener('click', (e) => {
  e.stopPropagation();
  _clearImportFile();
});
// Drag and drop
_idz.addEventListener('dragover',  (e) => { e.preventDefault(); _idz.classList.add('drag-over'); });
_idz.addEventListener('dragleave', ()  => { _idz.classList.remove('drag-over'); });
_idz.addEventListener('drop', (e) => {
  e.preventDefault();
  _idz.classList.remove('drag-over');
  if (e.dataTransfer.files[0]) _setImportFile(e.dataTransfer.files[0]);
});

document.getElementById('btn-import').addEventListener('click', async () => {
  if (!_importData || _importData.length === 0) {
    toast('No data to import.', 'error');
    return;
  }

  const skipDup  = document.getElementById('import-skip-dup').checked;
  const ra       = document.getElementById('import-result');
  const progWrap = document.getElementById('import-progress');
  const progBar  = document.getElementById('import-progress-bar');
  const progText = document.getElementById('import-progress-text');
  const btn      = document.getElementById('btn-import');

  btn.disabled = true;
  btn.innerHTML = '<span class="loading"></span> Importing…';
  progWrap.style.display = '';
  ra.classList.add('visible');
  ra.classList.remove('error');
  ra.innerHTML = '';

  let ok = 0, skipped = 0, errors = 0;
  const total    = _importData.length;
  const seenContent = new Set();

  // Pre-fetch existing content for dedup (best effort)
  if (skipDup) {
    try {
      const existing = await GET('/memories?limit=9999');
      (Array.isArray(existing) ? existing : []).forEach(m => {
        if (m.content) seenContent.add(m.content.trim());
      });
    } catch (_) { /* skip dedup pre-fetch if fails */ }
  }

  for (let i = 0; i < total; i++) {
    const m = _importData[i];

    // Update progress bar
    const pct = Math.round(((i+1) / total) * 100);
    progBar.style.width = pct + '%';
    progText.textContent = `${i+1} / ${total}`;

    // Skip duplicate by content
    if (skipDup && m.content && seenContent.has(m.content.trim())) {
      skipped++;
      continue;
    }

    try {
      await POST('/memories', {
        concept    : m.concept    || 'Imported',
        feeling    : m.feeling    || 'neutro',
        content    : m.content    || '',
        media_type : m.media_type || 'text',
        note       : m.note       || '',
        tags       : Array.isArray(m.tags) ? m.tags : [],
      });
      if (m.content) seenContent.add(m.content.trim());
      ok++;
    } catch (err) {
      errors++;
    }
  }

  progWrap.style.display = 'none';
  progBar.style.width    = '0%';

  const summary = `✦ Import complete — ${ok} imported, ${skipped} skipped (dup), ${errors} errors`;
  ra.innerHTML  = `<div class="response-label">${summary}</div>`;
  if (errors > 0) ra.classList.add('error');

  toast(`Imported ${ok} memories (${skipped} skipped, ${errors} errors)`, errors ? 'error' : 'success');
  btn.disabled  = false;
  btn.innerHTML = 'Import memories';
  checkConnection();
});

/* ═══════════════════════════════════════════════════════════
   BRAIN — LLM helpers
   ═══════════════════════════════════════════════════════════ */

const BRAIN_VIEWS = ['perceive','ask','reflect','dream','introspect','summarize'];

/* Render the amber status bar inside each Brain view */
function setBrainBar(viewId, { ok, provider, model, error } = {}) {
  const el = document.getElementById('brain-status-' + viewId);
  if (!el) return;
  if (ok) {
    el.className   = 'brain-bar ok';
    el.innerHTML   = `<span class="brain-status-dot on"></span>
      Brain active &nbsp;·&nbsp; <span style="opacity:.7">${esc(provider)}</span>
      &nbsp;/&nbsp; <span style="opacity:.5">${esc(model)}</span>`;
  } else {
    el.className   = 'brain-bar err';
    el.innerHTML   = `<span class="brain-status-dot off"></span>
      Brain offline &nbsp;·&nbsp; ${esc(error || 'LLM non disponibile — configura .env')}`;
  }
}

/* Check /brain/status and update all bars */
async function checkBrainStatus() {
  try {
    const s = await GET('/brain/status');
    const info = { ok: s.available, provider: s.provider, model: s.model };
    BRAIN_VIEWS.forEach(v => setBrainBar(v, info));
    return s.available;
  } catch (e) {
    const info = { ok: false, error: e.detail || 'Server non raggiungibile' };
    BRAIN_VIEWS.forEach(v => setBrainBar(v, info));
    return false;
  }
}

/* Generic brain response container */
function brainPanel(id) {
  const el = document.getElementById(id);
  el.classList.add('visible');
  el.classList.remove('error');
  return el;
}

function brainError(id, msg) {
  const el = document.getElementById(id);
  el.classList.add('visible', 'error');
  el.innerHTML = `
    <div class="brain-response-header">
      <span>✗ Error</span>
    </div>
    <div class="brain-response-body" style="color:var(--red)">${esc(msg)}</div>`;
}

function brainLoading(id, label) {
  const el = brainPanel(id);
  el.innerHTML = `
    <div class="brain-response-header">
      <span><span class="loading"></span> ${label}…</span>
    </div>`;
  return el;
}

function disableBtn(id, label) {
  const btn = document.getElementById(id);
  btn.disabled = true;
  btn._orig    = btn.innerHTML;
  btn.innerHTML = `<span class="loading"></span> ${label}`;
  return () => { btn.disabled = false; btn.innerHTML = btn._orig; };
}

/* ── PERCEIVE ──────────────────────────────────────────────── */

document.getElementById('btn-perceive').addEventListener('click', async () => {
  const raw        = document.getElementById('perceive-input').value.trim();
  const concept    = document.getElementById('perceive-concept').value.trim();
  const feeling    = document.getElementById('perceive-feeling').value;
  const note       = document.getElementById('perceive-note').value.trim();
  if (!raw) { toast(ui('toastEnterInput'), 'info'); return; }

  // Raccoglie media dal form New Memory se presente (media_type != text)
  // Il Perceive Brain usa lo stesso media selezionato nella form
  const mediaType = document.getElementById('new-mediatype')?.value || 'text';
  const mediaData = mediaType !== 'text'
    ? (document.getElementById('new-content-file-data')?.value || null)
    : null;
  // Ricava il MIME dal data URL (data:<mime>;base64,...)
  let mediaMime = null;
  if (mediaData && mediaData.startsWith('data:')) {
    try { mediaMime = mediaData.split(':')[1].split(';')[0]; } catch (_) {}
  }

  const restore = disableBtn('btn-perceive', 'Perceiving');
  brainLoading('perceive-result', ui('loadPerceiving'));
  const t0 = performance.now();

  try {
    const body = {
      raw_input  : raw,
      concept    : concept || null,
      feeling    : feeling || null,
      note,
      media_type : mediaType,
      media_data : mediaData || null,
      media_mime : mediaMime || null,
    };

    const r = await POST('/brain/perceive', body);
    const ms   = Math.round(performance.now() - t0);
    const tags = (r.extracted_tags || [])
      .map(t => `<span class="perceive-chip tag">${esc(t)}</span>`).join('');

    // Badge media type se non testuale
    const mediaBadge = mediaType !== 'text'
      ? `<span class="perceive-chip media-type">${mediaType.toUpperCase()}</span>`
      : '';

    const el = brainPanel('perceive-result');
    el.innerHTML = `
      <div class="brain-response-header">
        <span>✦ Memory perceived</span>
        <span class="latency">${ms}ms</span>
      </div>
      <div class="perceive-card">
        <div class="perceive-extracted">
          <span class="perceive-chip concept">◈ ${esc(r.extracted_concept)}</span>
          <span class="perceive-chip feeling">${esc(r.extracted_feeling)}</span>
          ${mediaBadge}
          ${tags}
        </div>
        <div class="perceive-enriched md-content">${renderMarkdown(r.enriched_content)}</div>
        <div class="perceive-id">memory_id: ${r.memory_id}</div>
      </div>`;
    toast(ui('toastPerceived', r.extracted_concept, r.extracted_feeling), 'success');
    checkConnection();
  } catch (e) {
    brainError('perceive-result', e.detail || String(e));
    toast(ui('toastPercErr'), 'error');
  } finally {
    restore();
  }
});

/* ── ASK ───────────────────────────────────────────────────── */

document.getElementById('btn-ask').addEventListener('click', doAsk);
document.getElementById('ask-question').addEventListener('keydown', e => {
  if (e.key === 'Enter' && e.ctrlKey) doAsk();
});

async function doAsk() {
  const question = document.getElementById('ask-question').value.trim();
  const max      = parseInt(document.getElementById('ask-max').value) || 15;
  if (!question) { toast(ui('toastEnterQ'), 'info'); return; }

  const restore = disableBtn('btn-ask', 'Asking');
  brainLoading('ask-result', ui('loadAsking'));
  const t0 = performance.now();

  try {
    const r  = await POST('/brain/ask', { question, max_memories: max });
    const ms = Math.round(performance.now() - t0);
    const el = brainPanel('ask-result');
    el.innerHTML = `
      <div class="brain-response-header">
        <span>✦ Answer</span>
        <span class="latency">${ms}ms</span>
      </div>
      <div class="ask-card">
        <div class="ask-answer md-content">${renderMarkdown(r.answer)}</div>
        <div class="ask-meta">
          <span>${ui('memoriesCtx', r.memories_used)}</span>
          <span class="ask-confidence">${esc(r.confidence_note)}</span>
          <span style="margin-left:auto">${esc(r.provider_used)}</span>
        </div>
      </div>`;
  } catch (e) {
    brainError('ask-result', e.detail || String(e));
    toast(ui('toastAskErr'), 'error');
  } finally {
    restore();
  }
}

/* ── REFLECT ───────────────────────────────────────────────── */

document.getElementById('btn-reflect').addEventListener('click', async () => {
  const concept = document.getElementById('reflect-concept').value.trim();
  if (!concept) { toast(ui('toastEnterConcept'), 'info'); return; }

  const restore = disableBtn('btn-reflect', 'Reflecting');
  brainLoading('reflect-result', ui('loadReflecting', concept));
  const t0 = performance.now();

  try {
    const r  = await GET(`/brain/reflect/${encodeURIComponent(concept)}`);
    const ms = Math.round(performance.now() - t0);
    const el = brainPanel('reflect-result');
    el.innerHTML = `
      <div class="brain-response-header">
        <span>✦ Reflection — ${esc(r.concept)}</span>
        <span class="latency">${ms}ms &nbsp;·&nbsp; ${ui('memoriesOf', r.memories)}</span>
      </div>
      <div class="reflect-card">
        ${r.arc ? `<div class="reflect-arc md-content">${renderMarkdown(r.arc)}</div>` : ''}
        <div class="reflect-text md-content">${renderMarkdown(r.reflection)}</div>
      </div>`;
  } catch (e) {
    brainError('reflect-result', e.detail || String(e));
    toast(ui('toastRefErr'), 'error');
  } finally {
    restore();
  }
});

/* ── DREAM ─────────────────────────────────────────────────── */

document.getElementById('btn-dream').addEventListener('click', async () => {
  const n       = parseInt(document.getElementById('dream-n').value) || 8;
  const restore = disableBtn('btn-dream', 'Dreaming');
  brainLoading('dream-result', ui('loadDreaming', n));
  const t0 = performance.now();

  try {
    const r  = await GET(`/brain/dream?n_memories=${n}`);
    const ms = Math.round(performance.now() - t0);

    // Per avere i dettagli dei ricordi campionati dobbiamo
    // fare una seconda chiamata a /memories/search o usare i dati del result
    // Il backend non ritorna i Memory, solo il testo delle connessioni.
    const el = brainPanel('dream-result');
    el.innerHTML = `
      <div class="brain-response-header">
        <span>✦ Dream</span>
        <span class="latency">${ms}ms &nbsp;·&nbsp; ${ui('memoriesSampled', r.memories)}</span>
      </div>
      <div class="dream-card">
        <div class="dream-connections md-content">${renderMarkdown(r.connections)}</div>
        <div style="margin-top:12px;font-size:10px;color:var(--muted);font-family:var(--mono)">
          Provider: ${esc(r.provider_used)}
        </div>
      </div>`;
  } catch (e) {
    brainError('dream-result', e.detail || String(e));
    toast(ui('toastDreamErr'), 'error');
  } finally {
    restore();
  }
});

/* ── INTROSPECT ────────────────────────────────────────────── */

document.getElementById('btn-introspect').addEventListener('click', async () => {
  const restore = disableBtn('btn-introspect', 'Introspecting');
  brainLoading('introspect-result', ui('loadIntrospect'));
  const t0 = performance.now();

  try {
    const r  = await GET('/brain/introspect');
    const ms = Math.round(performance.now() - t0);

    const chips = (r.dominant_concepts || [])
      .map(c => `<span class="perceive-chip concept">${esc(c)}</span>`).join('');

    const emoRows = Object.entries(r.emotional_map || {})
      .sort((a,b) => b[1]-a[1])
      .map(([f,n]) => `
        <div class="emomap-item">
          <span>${FEELING_LABELS[f] || f}</span>
          <span class="emomap-count">${n}</span>
        </div>`).join('');

    const el = brainPanel('introspect-result');
    el.innerHTML = `
      <div class="brain-response-header">
        <span>✦ Introspection</span>
        <span class="latency">${ms}ms &nbsp;·&nbsp; ${ui('memoriesAnalysed', r.total_memories)}</span>
      </div>
      <div class="introspect-card">
        ${chips ? `<div class="introspect-dominant">${chips}</div>` : ''}
        <div class="introspect-portrait md-content">${renderMarkdown(r.portrait)}</div>
        ${emoRows ? `<div class="introspect-emomap">${emoRows}</div>` : ''}
        <div style="margin-top:12px;font-size:10px;color:var(--muted);font-family:var(--mono)">
          Provider: ${esc(r.provider_used)}
        </div>
      </div>`;
  } catch (e) {
    brainError('introspect-result', e.detail || String(e));
    toast(ui('toastIntErr'), 'error');
  } finally {
    restore();
  }
});

/* ── SUMMARIZE ─────────────────────────────────────────────── */

document.getElementById('btn-summarize').addEventListener('click', async () => {
  const concept = document.getElementById('sum-concept').value.trim();
  const feeling = document.getElementById('sum-feeling').value;
  const style   = document.getElementById('sum-style').value;
  const limit   = parseInt(document.getElementById('sum-limit').value) || 20;

  const restore = disableBtn('btn-summarize', 'Summarizing');
  brainLoading('summarize-result', ui('loadSummarize', style));
  const t0 = performance.now();

  try {
    const r  = await POST('/brain/summarize', { concept: concept||null, feeling: feeling||null, style, limit });
    const ms = Math.round(performance.now() - t0);
    const el = brainPanel('summarize-result');
    el.innerHTML = `
      <div class="brain-response-header">
        <span>✦ Summary — ${esc(style)}</span>
        <span class="latency">${ms}ms &nbsp;·&nbsp; ${ui('memoriesOf', r.memories_used)}</span>
      </div>
      <div class="summarize-card">
        <div class="summarize-meta">
          ${concept ? `concept: ${esc(concept)} &nbsp;·&nbsp;` : ''}
          ${feeling ? `feeling: ${esc(feeling)} &nbsp;·&nbsp;` : ''}
          style: ${esc(style)}
        </div>
        <div class="summarize-text md-content">${renderMarkdown(r.text)}</div>
      </div>`;
  } catch (e) {
    brainError('summarize-result', e.detail || String(e));
    toast(ui('toastSumErr'), 'error');
  } finally {
    restore();
  }
});

/* ── Check Brain when switching to a Brain view ───────────── */
document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    if (BRAIN_VIEWS.includes(btn.dataset.view)) {
      checkBrainStatus();
    }
  });
});

/* ═══════════════════════════════════════════════════════════
   BOOT
   ═══════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════
   RESPONSIVE — hamburger + sidebar drawer
   ═══════════════════════════════════════════════════════════ */

(function initResponsive() {
  const sidebar     = document.getElementById('sidebar');
  const overlay     = document.getElementById('sidebar-overlay');
  const burgerTop   = document.getElementById('hamburger-top');
  const burgerSide  = document.getElementById('hamburger');
  const topbarDot   = document.getElementById('topbar-dot');
  const topbarLabel = document.getElementById('topbar-label');

  function openSidebar() {
    sidebar.classList.add('open');
    overlay.classList.add('visible');
    [burgerTop, burgerSide].forEach(b => {
      if (b) { b.classList.add('open'); b.setAttribute('aria-expanded','true'); }
    });
  }
  function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('visible');
    [burgerTop, burgerSide].forEach(b => {
      if (b) { b.classList.remove('open'); b.setAttribute('aria-expanded','false'); }
    });
  }

  burgerTop?.addEventListener('click', () =>
    sidebar.classList.contains('open') ? closeSidebar() : openSidebar());
  burgerSide?.addEventListener('click', () =>
    sidebar.classList.contains('open') ? closeSidebar() : openSidebar());
  overlay?.addEventListener('click', closeSidebar);

  // Close when a nav item is picked on mobile
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      if (window.matchMedia('(max-width: 900px)').matches) closeSidebar();
    });
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeSidebar();
  });

  // Mirror server status dot → topbar
  const mainDot   = document.getElementById('status-dot');
  const mainLabel = document.getElementById('status-label');
  if (topbarDot && mainDot) {
    new MutationObserver(() => {
      topbarDot.className    = mainDot.className;
      topbarLabel.textContent = mainLabel.textContent;
    }).observe(mainDot,   { attributes: true });
    new MutationObserver(() => {
      topbarLabel.textContent = mainLabel.textContent;
    }).observe(mainLabel, { childList: true, subtree: true, characterData: true });
  }
})();

document.addEventListener('DOMContentLoaded', () => {
  // Language buttons
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', () => setLang(btn.dataset.lang));
  });

  // Apply saved/default language — builds all feeling selects from scratch
  setLang(_lang);

  // Server connection
  checkConnection();
});