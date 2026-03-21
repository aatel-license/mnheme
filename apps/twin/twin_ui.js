/* ═══════════════════════════════════════════════════════════════
   MNHEME Digital Twin — twin_ui.js
   ═══════════════════════════════════════════════════════════════ */

/* ── Theme system ─────────────────────────────────────────── */

const THEMES = [
  // Light themes
  { id: 'light-parchment', label: 'Pergamena',  bg: '#f5f0e8', accent: '#8b4513', dark: false },
  { id: 'light-ivory',     label: 'Avorio',     bg: '#fafaf7', accent: '#2c5f8a', dark: false },
  { id: 'light-linen',     label: 'Lino',       bg: '#f8f4ee', accent: '#7b4f2e', dark: false },
  { id: 'light-sage',      label: 'Salvia',     bg: '#f2f5f0', accent: '#3d6b2e', dark: false },
  { id: 'light-cloud',     label: 'Nuvola',     bg: '#f4f6f8', accent: '#2d5a8e', dark: false },
  { id: 'light-rose',      label: 'Rosa',       bg: '#fdf6f4', accent: '#9b3a3a', dark: false },
  { id: 'light-sand',      label: 'Sabbia',     bg: '#f7f2ea', accent: '#8a6020', dark: false },
  { id: 'light-mint',      label: 'Menta',      bg: '#f0faf6', accent: '#1a7a5a', dark: false },
  { id: 'light-stone',     label: 'Pietra',     bg: '#f2f2f0', accent: '#4a4a40', dark: false },
  { id: 'light-wheat',     label: 'Frumento',   bg: '#faf5e8', accent: '#7a5a10', dark: false },
  // Dark themes
  { id: 'dark-obsidian',   label: 'Ossidiana',  bg: '#0a0a0a', accent: '#c9a84c', dark: true },
  { id: 'dark-midnight',   label: 'Mezzanotte', bg: '#080c14', accent: '#6090d8', dark: true },
  { id: 'dark-forest',     label: 'Foresta',    bg: '#080e08', accent: '#50c860', dark: true },
  { id: 'dark-ember',      label: 'Brace',      bg: '#0e0808', accent: '#e0603a', dark: true },
  { id: 'dark-slate',      label: 'Ardesia',    bg: '#0c1018', accent: '#7898c8', dark: true },
  { id: 'dark-sepia',      label: 'Seppia',     bg: '#100c08', accent: '#d09840', dark: true },
  { id: 'dark-violet',     label: 'Viola',      bg: '#0a0810', accent: '#9870e0', dark: true },
  { id: 'dark-charcoal',   label: 'Grafite',    bg: '#141414', accent: '#e8c040', dark: true },
  { id: 'dark-ocean',      label: 'Oceano',     bg: '#040c14', accent: '#30a8c8', dark: true },
  { id: 'dark-bronze',     label: 'Bronzo',     bg: '#0c0a06', accent: '#c88830', dark: true },
];

const DEFAULT_THEME = 'light-parchment';

function applyTheme(id) {
  document.documentElement.setAttribute('data-theme', id);
  localStorage.setItem('twin_theme', id);
  // Update active swatch
  document.querySelectorAll('.theme-swatch').forEach(s => {
    s.classList.toggle('active', s.dataset.themeId === id);
  });
}

function buildThemeGrid() {
  const grid = document.getElementById('theme-grid');
  if (!grid) return;
  grid.innerHTML = THEMES.map(t => `
    <div class="theme-swatch ${t.dark ? 'dark' : 'light'}"
         data-theme-id="${t.id}"
         title="${t.label}"
         style="background:${t.bg}; border-color:${t.accent}33;"
         onclick="applyTheme('${t.id}')">
    </div>
  `).join('');
  // Mark active
  const saved = localStorage.getItem('twin_theme') || DEFAULT_THEME;
  applyTheme(saved);
}

/* ── Config ─────────────────────────────────────────────────── */

const _defaultApiUrl = () => {
  const stored = localStorage.getItem('twin_api_url');
  if (stored) return stored;
  return `${window.location.protocol}//${window.location.hostname}:8001`;
};
let API          = _defaultApiUrl();
let CURRENT_TIER = 'family';
let TWIN_NAME    = '';
let TWIN_INITIAL = '✦';

/* ── Helpers ─────────────────────────────────────────────────── */

const esc = s => String(s)
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/"/g,'&quot;');

async function apiFetch(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json', 'accept': 'application/json' },
    ...opts,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
  return data;
}

function setStatus(online) {
  const dot   = document.getElementById('status-dot');
  const label = document.getElementById('status-label');
  dot.className     = 'status-dot ' + (online ? 'online' : 'offline');
  label.textContent = online ? 'connesso' : 'offline';
}

/* ── Profile ─────────────────────────────────────────────────── */

async function loadProfile() {
  try {
    const p = await apiFetch('/twin/profile');
    TWIN_NAME    = p.name || 'Sconosciuto';
    TWIN_INITIAL = TWIN_NAME.charAt(0).toUpperCase();

    document.getElementById('twin-avatar').textContent = TWIN_INITIAL;
    document.getElementById('twin-name').textContent   = TWIN_NAME;
    const died = p.died ? ` — ${p.died}` : '';
    document.getElementById('twin-dates').textContent  = p.born ? `${p.born}${died}` : '';
    if (p.epitaph) {
      document.getElementById('twin-epitaph').textContent = `"${p.epitaph}"`;
    }
    // Mostra la cartella del personaggio
    const charDir = document.getElementById('twin-chardir');
    if (charDir && p.character_slug) {
      charDir.textContent = `character/${p.character_slug}/`;
    }

    document.getElementById('setup-overlay').style.display = 'none';
    setStatus(true);

    // Carica la lista dei personaggi disponibili
    loadCharacters();
  } catch(e) {
    setStatus(false);
    document.getElementById('setup-overlay').style.display = 'flex';
  }
}

async function connectToServer() {
  const urlInput = document.getElementById('setup-url');
  API = urlInput.value.trim();
  document.getElementById('server-url').value = API;
  localStorage.setItem('twin_api_url', API);
  const err = document.getElementById('setup-error');
  err.textContent = '';
  try {
    await loadProfile();
  } catch(e) {
    err.textContent = 'Impossibile connettersi. Verifica URL e server.';
  }
}

/* ── Tier ────────────────────────────────────────────────────── */

document.querySelectorAll('.tier-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.tier-btn').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    CURRENT_TIER = this.dataset.tier;
  });
});

/* ── Nav ─────────────────────────────────────────────────────── */

document.querySelectorAll('.nav-btn[data-view]').forEach(btn => {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    this.classList.add('active');
    const view = document.getElementById('view-' + this.dataset.view);
    if (view) view.classList.add('active');
  });
});

/* ── Server URL sync ─────────────────────────────────────────── */

document.getElementById('server-url').value = API;
document.getElementById('setup-url') &&
  (document.getElementById('setup-url').value = API);

document.getElementById('server-url').addEventListener('change', function() {
  API = this.value.trim();
  localStorage.setItem('twin_api_url', API);
  loadProfile();
});

/* ── Ask ─────────────────────────────────────────────────────── */

function handleAskKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendQuestion(); }
}

async function sendQuestion() {
  const input = document.getElementById('ask-input');
  const q     = input.value.trim();
  if (!q) return;

  const conv  = document.getElementById('conversation');
  document.getElementById('ask-empty').style.display = 'none';
  input.value = '';
  input.style.height = '';

  conv.innerHTML += `
    <div class="msg msg-visitor">
      <div class="msg-bubble">${esc(q)}</div>
    </div>`;

  const loadId = 'load-' + Date.now();
  conv.innerHTML += `
    <div class="msg msg-twin" id="${loadId}">
      <div class="msg-meta">
        <div class="msg-avatar">${TWIN_INITIAL}</div>
        <span class="msg-name">${esc(TWIN_NAME)}</span>
      </div>
      <div class="msg-bubble">
        <div class="loading-dots"><span></span><span></span><span></span></div>
      </div>
    </div>`;
  conv.scrollTop = conv.scrollHeight;

  const btn = document.getElementById('btn-ask');
  btn.disabled = true;

  try {
    const r = await apiFetch('/twin/ask', {
      method: 'POST',
      body: JSON.stringify({ question: q, tier: CURRENT_TIER }),
    });

    const confColor = r.confidence && r.confidence.includes('alta')
      ? 'var(--success)'
      : r.confidence && r.confidence.includes('bassa')
        ? 'var(--danger)'
        : 'var(--fg-muted)';

    document.getElementById(loadId).outerHTML = `
      <div class="msg msg-twin">
        <div class="msg-meta">
          <div class="msg-avatar">${TWIN_INITIAL}</div>
          <span class="msg-name">${esc(TWIN_NAME)}</span>
          <span class="msg-confidence" style="color:${confColor}">${esc(r.confidence || '')}</span>
        </div>
        <div class="msg-bubble">${formatResponse(r.response)}</div>
        ${r.caveat ? `<div class="msg-caveat">${esc(r.caveat)}</div>` : ''}
        <div class="msg-memories-count">${r.memories_used} ricordi usati</div>
      </div>`;
  } catch(e) {
    document.getElementById(loadId).outerHTML = `
      <div class="msg msg-twin">
        <div class="msg-meta">
          <div class="msg-avatar">${TWIN_INITIAL}</div>
          <span class="msg-name">${esc(TWIN_NAME)}</span>
        </div>
        <div class="msg-bubble" style="color:var(--danger)">${esc(e.message)}</div>
      </div>`;
  } finally {
    btn.disabled = false;
    conv.scrollTop = conv.scrollHeight;
  }
}

function formatResponse(text) {
  return text.split('\n\n')
    .filter(p => p.trim())
    .map(p => `<p>${esc(p.trim())}</p>`)
    .join('');
}

/* ── Letter ──────────────────────────────────────────────────── */

async function generateLetter() {
  const to    = document.getElementById('letter-to').value.trim();
  const theme = document.getElementById('letter-theme').value.trim();
  if (!to || !theme) return;

  const btn    = document.getElementById('btn-letter');
  const output = document.getElementById('letter-output');
  btn.disabled     = true;
  btn.textContent  = 'Generazione…';
  output.style.display = 'none';

  try {
    const r = await apiFetch('/twin/letter', {
      method: 'POST',
      body: JSON.stringify({ to, theme, tier: CURRENT_TIER }),
    });
    document.getElementById('letter-text').textContent = r.text;
    document.getElementById('letter-meta').textContent =
      `${r.memories_used} ricordi  ·  tema: ${r.theme}`;
    output.style.display = '';
  } catch(e) {
    document.getElementById('letter-text').textContent = 'Errore: ' + e.message;
    output.style.display = '';
  } finally {
    btn.disabled    = false;
    btn.textContent = 'Genera lettera';
  }
}

/* ── Legacy ──────────────────────────────────────────────────── */

async function loadLegacy() {
  const btn     = document.getElementById('btn-legacy');
  const empty   = document.getElementById('legacy-empty');
  const content = document.getElementById('legacy-content');
  btn.disabled  = true;
  btn.textContent = 'Caricamento…';
  empty.style.display   = '';
  content.style.display = 'none';
  empty.innerHTML = '<div class="loading-dots"><span></span><span></span><span></span></div>';

  try {
    const r = await apiFetch(`/twin/legacy?tier=${CURRENT_TIER}`);
    document.getElementById('leg-portrait').textContent   = r.portrait;
    document.getElementById('leg-values').textContent     = r.core_values;
    document.getElementById('leg-unresolved').textContent = r.unresolved;
    document.getElementById('leg-message').textContent    = r.message;
    document.getElementById('leg-arc').textContent        = r.emotional_arc;
    document.getElementById('leg-concepts').innerHTML     =
      (r.dominant_concepts || []).map(c =>
        `<span class="concept-chip">${esc(c)}</span>`
      ).join('');
    empty.style.display   = 'none';
    content.style.display = '';
  } catch(e) {
    empty.innerHTML = `<span style="color:var(--danger)">${esc(e.message)}</span>`;
  } finally {
    btn.disabled    = false;
    btn.textContent = 'Carica eredità';
  }
}

/* ── Timeline ────────────────────────────────────────────────── */

const POSITIVE_FEELINGS = new Set([
  'gioia','amore','serenità','gratitudine','orgoglio','speranza',
  'eccitazione','sollievo','stupore','curiosità','sorpresa',
]);
const NEGATIVE_FEELINGS = new Set([
  'ansia','paura','tristezza','rabbia','vergogna','senso_di_colpa',
  'solitudine','delusione','invidia','imbarazzo','rassegnazione',
]);

function feelingClass(f) {
  if (POSITIVE_FEELINGS.has(f)) return 'feeling-positive';
  if (NEGATIVE_FEELINGS.has(f)) return 'feeling-negative';
  return 'feeling-neutral';
}

function feelingColor(f) {
  const map = {
    gioia:'#50b870',  amore:'#d06080',    serenità:'#50a8a0',
    gratitudine:'#70b060', orgoglio:'#6090d0', speranza:'#9070d0',
    nostalgia:'#9868c0',  malinconia:'#7890a8', ansia:'#d09040',
    paura:'#d06050',  rabbia:'#d04040',   tristezza:'#7888a8',
    vergogna:'#c07050', solitudine:'#6878a0',
  };
  return map[f] || 'var(--fg-muted)';
}

async function loadTimeline() {
  const concept = document.getElementById('timeline-concept').value.trim();
  if (!concept) return;

  const btn     = document.getElementById('btn-timeline');
  const empty   = document.getElementById('timeline-empty');
  const content = document.getElementById('timeline-content');
  btn.disabled  = true;
  btn.textContent = 'Caricamento…';
  empty.style.display   = '';
  content.style.display = 'none';
  empty.innerHTML = '<div class="loading-dots"><span></span><span></span><span></span></div>';

  try {
    const r = await apiFetch(
      `/twin/timeline/${encodeURIComponent(concept)}?tier=${CURRENT_TIER}`
    );
    document.getElementById('tl-arc').textContent = r.arc;
    document.getElementById('tl-track').innerHTML = (r.entries || []).map(e => `
      <div class="timeline-entry ${feelingClass(e.feeling)}">
        <div class="entry-date">${esc(e.date)}</div>
        <div class="entry-feeling" style="color:${feelingColor(e.feeling)}">${esc(e.feeling)}</div>
        <div class="entry-excerpt">${esc(e.excerpt)}</div>
        <div class="entry-tags">
          ${(e.tags||[]).map(t => `<span class="entry-tag">${esc(t)}</span>`).join('')}
        </div>
      </div>`).join('');
    empty.style.display   = 'none';
    content.style.display = '';
  } catch(e) {
    empty.innerHTML = `<span style="color:var(--danger)">${esc(e.message)}</span>`;
  } finally {
    btn.disabled    = false;
    btn.textContent = 'Carica arco';
  }
}

/* ── Characters ──────────────────────────────────────────────── */

async function loadCharacters() {
  try {
    const res  = await apiFetch('/twin/characters');
    const list = res.characters || [];
    const panel = document.getElementById('character-selector');
    const ul    = document.getElementById('character-list');
    if (!panel || !ul) return;

    if (list.length <= 1) {
      // Un solo personaggio — non serve il selettore
      panel.style.display = 'none';
      return;
    }

    ul.innerHTML = list.map(c => `
      <button class="character-btn ${c.active ? 'active' : ''}"
              data-slug="${esc(c.slug)}"
              onclick="switchCharacter('${esc(c.slug)}')">
        <span class="character-btn-initial">${esc(c.name.charAt(0).toUpperCase())}</span>
        <span class="character-btn-info">
          <span class="character-btn-name">${esc(c.name)}</span>
          <span class="character-btn-dates">${c.birth_year || '?'}${c.death_year ? ` — ${c.death_year}` : ''}</span>
        </span>
        ${c.active ? '<span class="character-btn-dot">●</span>' : ''}
      </button>`).join('');

    panel.style.display = '';
  } catch(e) {
    // Endpoint non disponibile o zero personaggi — silenzioso
    const panel = document.getElementById('character-selector');
    if (panel) panel.style.display = 'none';
  }
}

async function switchCharacter(slug) {
  // Il server twin è già dedicato a un personaggio — per switchare
  // bisogna ricaricare la pagina con un parametro che indica il personaggio.
  // Poiché il server legge TWIN_CHARACTER all'avvio, la UI informa l'utente.
  const current = document.querySelector('.character-btn.active')?.dataset.slug;
  if (slug === current) return;

  // Mostra info su come switchare via run.sh
  const name = document.querySelector(`.character-btn[data-slug="${slug}"] .character-btn-name`)
                        ?.textContent || slug;
  const confirmed = confirm(
    `Per consultare "${name}" devi riavviare il server:\n\n` +
    `  ./run.sh --character ${slug} --no-setup\n\n` +
    `Vuoi aprire la documentazione API?`
  );
  if (confirmed) {
    window.open(API + '/docs', '_blank');
  }
}

/* ── Auto-resize textarea ────────────────────────────────────── */

document.getElementById('ask-input').addEventListener('input', function() {
  this.style.height = '';
  this.style.height = Math.min(this.scrollHeight, 130) + 'px';
});

/* ── Init ────────────────────────────────────────────────────── */

buildThemeGrid();
loadProfile();
