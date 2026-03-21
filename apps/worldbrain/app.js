// ── Translations ─────────────────────────────────────────────────
const LANGS = {
  en: {
    code: 'en', label: 'EN', name: 'English',
    appSub:        'MNHEME · NARRATIVE ENGINE',
    noChars:       'No characters yet.<br>Begin your world.',
    newChar:       '+ NEW CHARACTER',
    lmSaved:       '✓ saved',
    lmModelPh:     'model name (leave blank = auto)',
    themeLight:    '— LIGHT —',
    themeDark:     '— DARK —',
    emptyQuote:    '"Memory does not overwrite. It stratifies."',
    emptySub:      'MNHEME · emotional memory engine for narrative worlds',
    createFirst:   'CREATE YOUR FIRST CHARACTER',
    memory:        'memory',
    memories:      'memories',
    tabMem:        'MEMORIES',
    tabBrain:      'BRAIN',
    tabAnalytics:  'ANALYTICS',
    formTitle:     'RECORD A MEMORY',
    concept:       'CONCEPT',
    feeling:       'FEELING',
    content:       'CONTENT',
    note:          'NOTE',
    optional:      '— optional',
    conceptPh:     'Betrayal, Home, War…',
    notePh:        'World context, location…',
    appendBtn:     'APPEND TO ARCHIVE',
    archiveEmpty:  'The archive is empty.',
    noMemYet:      'No memories recorded yet.',
    brainCtx:      (name, n) => `Brain · ${name} · ${n} ${n===1?'memory':'memories'}`,
    clearChat:     'clear chat',
    brainAwaits:   name => `The Brain of ${name} awaits`,
    brainSub:      'Ask about their emotional history,<br>a concept, a relationship, the arc of their inner life.',
    suggs:         name => [
      `What is ${name}'s emotional arc around their dominant concept?`,
      `How does ${name} relate to power and control?`,
      `What hidden fear shapes ${name}'s decisions?`,
      `Describe ${name}'s psychological portrait in three sentences.`,
    ],
    askPh:         name => `Ask the Brain about ${name}…`,
    askBtn:        'ASK',
    emotDist:      'EMOTIONAL DISTRIBUTION',
    conceptMap:    'CONCEPT MAP',
    timeline:      n => `MEMORY TIMELINE — ${n} entries`,
    noAnalytics:   'No memories to analyse yet.',
    modalTitle:    'NEW CHARACTER',
    mName:         'NAME',
    mArch:         'ARCHETYPE',
    mNamePh:       'Elara Voss',
    mArchPh:       'Exiled healer, keeper of lost things',
    cancel:        'Cancel',
    create:        'Create',
    contentPh:     name => `What ${name} lived, in their own voice…`,
    lmToggle:      'LM STUDIO',
    feelLabels: {
      gioia:'Joy', tristezza:'Sadness', rabbia:'Rage', paura:'Fear',
      nostalgia:'Nostalgia', amore:'Love', malinconia:'Melancholy',
      serenità:'Serenity', sorpresa:'Surprise', ansia:'Anxiety',
      gratitudine:'Gratitude', vergogna:'Shame', orgoglio:'Pride',
      noia:'Boredom', curiosità:'Curiosity',
    },
  },

  it: {
    code: 'it', label: 'IT', name: 'Italiano',
    appSub:        'MNHEME · MOTORE NARRATIVO',
    noChars:       'Nessun personaggio.<br>Inizia il tuo mondo.',
    newChar:       '+ NUOVO PERSONAGGIO',
    lmSaved:       '✓ salvato',
    lmModelPh:     'nome modello (vuoto = automatico)',
    themeLight:    '— CHIARO —',
    themeDark:     '— SCURO —',
    emptyQuote:    '"La memoria non si sovrascrive. Si stratifica."',
    emptySub:      'MNHEME · motore di memoria emotiva per mondi narrativi',
    createFirst:   'CREA IL TUO PRIMO PERSONAGGIO',
    memory:        'ricordo',
    memories:      'ricordi',
    tabMem:        'RICORDI',
    tabBrain:      'CERVELLO',
    tabAnalytics:  'ANALISI',
    formTitle:     'REGISTRA UN RICORDO',
    concept:       'CONCETTO',
    feeling:       'SENTIMENTO',
    content:       'CONTENUTO',
    note:          'NOTA',
    optional:      '— opzionale',
    conceptPh:     'Tradimento, Casa, Guerra…',
    notePh:        'Contesto narrativo, luogo…',
    appendBtn:     'AGGIUNGI ALL\'ARCHIVIO',
    archiveEmpty:  'L\'archivio è vuoto.',
    noMemYet:      'Nessun ricordo registrato.',
    brainCtx:      (name, n) => `Cervello · ${name} · ${n} ${n===1?'ricordo':'ricordi'}`,
    clearChat:     'cancella chat',
    brainAwaits:   name => `Il Cervello di ${name} attende`,
    brainSub:      'Chiedi della loro storia emotiva,<br>un concetto, una relazione, l\'arco della loro vita interiore.',
    suggs:         name => [
      `Qual è l'arco emotivo di ${name} attorno al concetto dominante?`,
      `Come si rapporta ${name} al potere e al controllo?`,
      `Quale paura nascosta guida le decisioni di ${name}?`,
      `Descrivi il ritratto psicologico di ${name} in tre frasi.`,
    ],
    askPh:         name => `Chiedi al Cervello di ${name}…`,
    askBtn:        'CHIEDI',
    emotDist:      'DISTRIBUZIONE EMOTIVA',
    conceptMap:    'MAPPA DEI CONCETTI',
    timeline:      n => `TIMELINE DEI RICORDI — ${n} voci`,
    noAnalytics:   'Nessun ricordo da analizzare.',
    modalTitle:    'NUOVO PERSONAGGIO',
    mName:         'NOME',
    mArch:         'ARCHETIPO',
    mNamePh:       'Elara Voss',
    mArchPh:       'Guaritrice in esilio, custode delle cose perdute',
    cancel:        'Annulla',
    create:        'Crea',
    contentPh:     name => `Cosa ha vissuto ${name}, con la sua voce…`,
    lmToggle:      'LM STUDIO',
    feelLabels: {
      gioia:'Gioia', tristezza:'Tristezza', rabbia:'Rabbia', paura:'Paura',
      nostalgia:'Nostalgia', amore:'Amore', malinconia:'Malinconia',
      serenità:'Serenità', sorpresa:'Sorpresa', ansia:'Ansia',
      gratitudine:'Gratitudine', vergogna:'Vergogna', orgoglio:'Orgoglio',
      noia:'Noia', curiosità:'Curiosità',
    },
  },

  es: {
    code: 'es', label: 'ES', name: 'Español',
    appSub:        'MNHEME · MOTOR NARRATIVO',
    noChars:       'Sin personajes aún.<br>Comienza tu mundo.',
    newChar:       '+ NUEVO PERSONAJE',
    lmSaved:       '✓ guardado',
    lmModelPh:     'nombre del modelo (vacío = automático)',
    themeLight:    '— CLARO —',
    themeDark:     '— OSCURO —',
    emptyQuote:    '"La memoria no se sobreescribe. Se estratifica."',
    emptySub:      'MNHEME · motor de memoria emocional para mundos narrativos',
    createFirst:   'CREA TU PRIMER PERSONAJE',
    memory:        'recuerdo',
    memories:      'recuerdos',
    tabMem:        'RECUERDOS',
    tabBrain:      'MENTE',
    tabAnalytics:  'ANÁLISIS',
    formTitle:     'REGISTRAR UN RECUERDO',
    concept:       'CONCEPTO',
    feeling:       'SENTIMIENTO',
    content:       'CONTENIDO',
    note:          'NOTA',
    optional:      '— opcional',
    conceptPh:     'Traición, Hogar, Guerra…',
    notePh:        'Contexto del mundo, lugar…',
    appendBtn:     'AÑADIR AL ARCHIVO',
    archiveEmpty:  'El archivo está vacío.',
    noMemYet:      'Ningún recuerdo registrado aún.',
    brainCtx:      (name, n) => `Mente · ${name} · ${n} ${n===1?'recuerdo':'recuerdos'}`,
    clearChat:     'limpiar chat',
    brainAwaits:   name => `La Mente de ${name} aguarda`,
    brainSub:      'Pregunta sobre su historia emocional,<br>un concepto, una relación, el arco de su vida interior.',
    suggs:         name => [
      `¿Cuál es el arco emocional de ${name} en torno a su concepto dominante?`,
      `¿Cómo se relaciona ${name} con el poder y el control?`,
      `¿Qué miedo oculto moldea las decisiones de ${name}?`,
      `Describe el retrato psicológico de ${name} en tres frases.`,
    ],
    askPh:         name => `Pregunta a la Mente sobre ${name}…`,
    askBtn:        'PREGUNTAR',
    emotDist:      'DISTRIBUCIÓN EMOCIONAL',
    conceptMap:    'MAPA DE CONCEPTOS',
    timeline:      n => `LÍNEA DE TIEMPO — ${n} entradas`,
    noAnalytics:   'Sin recuerdos para analizar aún.',
    modalTitle:    'NUEVO PERSONAJE',
    mName:         'NOMBRE',
    mArch:         'ARQUETIPO',
    mNamePh:       'Elara Voss',
    mArchPh:       'Sanadora exiliada, guardiana de cosas perdidas',
    cancel:        'Cancelar',
    create:        'Crear',
    contentPh:     name => `Lo que vivió ${name}, en su propia voz…`,
    lmToggle:      'LM STUDIO',
    feelLabels: {
      gioia:'Alegría', tristezza:'Tristeza', rabbia:'Rabia', paura:'Miedo',
      nostalgia:'Nostalgia', amore:'Amor', malinconia:'Melancolía',
      serenità:'Serenidad', sorpresa:'Sorpresa', ansia:'Ansiedad',
      gratitudine:'Gratitud', vergogna:'Vergüenza', orgoglio:'Orgullo',
      noia:'Aburrimiento', curiosità:'Curiosidad',
    },
  },

  zh: {
    code: 'zh', label: '中', name: '中文',
    appSub:        'MNHEME · 叙事引擎',
    noChars:       '尚无角色。<br>开始你的世界。',
    newChar:       '+ 新角色',
    lmSaved:       '✓ 已保存',
    lmModelPh:     '模型名称（留空=自动）',
    themeLight:    '— 浅色 —',
    themeDark:     '— 深色 —',
    emptyQuote:    '"记忆不会被覆盖，只会层层叠加。"',
    emptySub:      'MNHEME · 叙事世界的情感记忆引擎',
    createFirst:   '创建你的第一个角色',
    memory:        '条记忆',
    memories:      '条记忆',
    tabMem:        '记忆',
    tabBrain:      '大脑',
    tabAnalytics:  '分析',
    formTitle:     '记录一段记忆',
    concept:       '概念',
    feeling:       '情感',
    content:       '内容',
    note:          '备注',
    optional:      '— 可选',
    conceptPh:     '背叛、家园、战争……',
    notePh:        '世界背景、地点……',
    appendBtn:     '添加到档案',
    archiveEmpty:  '档案为空。',
    noMemYet:      '尚未记录任何记忆。',
    brainCtx:      (name, n) => `大脑 · ${name} · ${n} 条记忆`,
    clearChat:     '清除对话',
    brainAwaits:   name => `${name} 的大脑正在等待`,
    brainSub:      '询问关于他们的情感历史，<br>一个概念、一段关系，或内心世界的弧线。',
    suggs:         name => [
      `${name} 围绕主导概念的情感弧线是什么？`,
      `${name} 如何与权力和控制相处？`,
      `什么隐藏的恐惧塑造了 ${name} 的决定？`,
      `用三句话描述 ${name} 的心理画像。`,
    ],
    askPh:         name => `向大脑询问关于 ${name} 的问题……`,
    askBtn:        '提问',
    emotDist:      '情感分布',
    conceptMap:    '概念地图',
    timeline:      n => `记忆时间线 — ${n} 条`,
    noAnalytics:   '尚无可分析的记忆。',
    modalTitle:    '新角色',
    mName:         '姓名',
    mArch:         '原型',
    mNamePh:       'Elara Voss',
    mArchPh:       '流放的治愈者，失落之物的守护者',
    cancel:        '取消',
    create:        '创建',
    contentPh:     name => `${name} 亲历的事，用他们自己的声音……`,
    lmToggle:      'LM STUDIO',
    feelLabels: {
      gioia:'喜悦', tristezza:'悲伤', rabbia:'愤怒', paura:'恐惧',
      nostalgia:'怀旧', amore:'爱', malinconia:'忧郁',
      serenità:'宁静', sorpresa:'惊讶', ansia:'焦虑',
      gratitudine:'感恩', vergogna:'羞耻', orgoglio:'自豪',
      noia:'无聊', curiosità:'好奇',
    },
  },
};

const LANG_ORDER = ['en', 'it', 'es', 'zh'];

// ── Theme data ────────────────────────────────────────────────────
const THEMES = [
  { id:'parchment', label:'Parchment', bg:'#f5f0e8', accent:'#8b4513', dark:false },
  { id:'arctic',    label:'Arctic',    bg:'#f0f4f8', accent:'#1d4ed8', dark:false },
  { id:'linen',     label:'Linen',     bg:'#f7f5f2', accent:'#6b5a3e', dark:false },
  { id:'sage',      label:'Sage',      bg:'#eef2ec', accent:'#2d6a2d', dark:false },
  { id:'rose',      label:'Rose',      bg:'#fdf0f2', accent:'#b03060', dark:false },
  { id:'slate',     label:'Slate',     bg:'#eef0f5', accent:'#3d5a8a', dark:false },
  { id:'sand',      label:'Sand',      bg:'#f8f3ea', accent:'#c07820', dark:false },
  { id:'ivory',     label:'Ivory',     bg:'#fafaf5', accent:'#0e0e0c', dark:false },
  { id:'lavender',  label:'Lavender',  bg:'#f4f0f8', accent:'#6b3fa0', dark:false },
  { id:'moss',      label:'Moss',      bg:'#eef2ea', accent:'#4a6a28', dark:false },
  { id:'obsidian',  label:'Obsidian',  bg:'#0c0b0a', accent:'#c9a96e', dark:true  },
  { id:'midnight',  label:'Midnight',  bg:'#080c18', accent:'#6090e0', dark:true  },
  { id:'ember',     label:'Ember',     bg:'#0e0a06', accent:'#e07820', dark:true  },
  { id:'forest',    label:'Forest',    bg:'#060e08', accent:'#40c060', dark:true  },
  { id:'void',      label:'Void',      bg:'#000000', accent:'#e0e0e0', dark:true  },
  { id:'crimson',   label:'Crimson',   bg:'#0e0606', accent:'#e04040', dark:true  },
  { id:'ocean',     label:'Ocean',     bg:'#060c10', accent:'#18b8cc', dark:true  },
  { id:'dusk',      label:'Dusk',      bg:'#0a0614', accent:'#9060e0', dark:true  },
  { id:'copper',    label:'Copper',    bg:'#0c0906', accent:'#c07030', dark:true  },
  { id:'noir',      label:'Noir',      bg:'#0e0e0e', accent:'#909090', dark:true  },
];

// ── Constants ────────────────────────────────────────────────────
const SK = 'mnheme-wb4';
const FEELING_COLORS = {
  gioia:'#f59e0b', tristezza:'#6ea8fe', rabbia:'#f87171', paura:'#a78bfa',
  nostalgia:'#fb923c', amore:'#f472b6', malinconia:'#818cf8', serenità:'#34d399',
  sorpresa:'#fcd34d', ansia:'#94a3b8', gratitudine:'#6ee7b7', vergogna:'#fca5a5',
  orgoglio:'#c084fc', noia:'#6b7280', curiosità:'#67e8f9',
};
const FEELING_KEYS = Object.keys(FEELING_COLORS);

// ── State ─────────────────────────────────────────────────────────
let state          = { characters:[], memories:{}, chats:{} };
let selId          = null;
let activeTab      = 'memories';
let chatLoading    = false;
let currentTheme   = 'parchment';
let currentLang    = 'en';
let themePanelOpen = false;
let langPanelOpen  = false;

// ── i18n helper ───────────────────────────────────────────────────
const L = () => LANGS[currentLang] || LANGS.en;
const feelLabel = key => L().feelLabels[key] || key;

// ── Utils ─────────────────────────────────────────────────────────
const uid     = () => Math.random().toString(36).slice(2, 10);
const fmtDate = ts => new Date(ts).toLocaleDateString(currentLang === 'zh' ? 'zh-CN' : currentLang === 'es' ? 'es-ES' : currentLang === 'it' ? 'it-IT' : 'en-GB');
const save    = () => { try { localStorage.setItem(SK, JSON.stringify(state)); } catch(e) {} };
const esc     = s  => String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');

// ── Persistence ───────────────────────────────────────────────────
function load() {
  try { const raw = localStorage.getItem(SK); if (raw) state = JSON.parse(raw); } catch(e) {}
  const savedTheme = localStorage.getItem('wb-theme');
  if (savedTheme && THEMES.find(t => t.id === savedTheme)) currentTheme = savedTheme;
  const savedLang = localStorage.getItem('wb-lang');
  if (savedLang && LANGS[savedLang]) currentLang = savedLang;
  applyTheme(currentTheme, false);
  const u = localStorage.getItem('wb-lm-url');
  const m = localStorage.getItem('wb-lm-model');
  if (u) document.getElementById('lm-url').value = u;
  if (m) document.getElementById('lm-model').value = m;
}

// ── Theme ─────────────────────────────────────────────────────────
function applyTheme(id, persist = true) {
  currentTheme = id;
  document.documentElement.setAttribute('data-theme', id);
  if (persist) localStorage.setItem('wb-theme', id);
  document.querySelectorAll('.theme-swatch').forEach(s => s.classList.toggle('active', s.dataset.theme === id));
  const th = THEMES.find(t => t.id === id);
  const toggle = document.getElementById('btn-theme-toggle');
  if (toggle && th)
    toggle.innerHTML = `<span class="swatch" style="background:${th.accent}"></span>${th.label} <span style="font-size:9px;opacity:.6">${th.dark?'●':'○'}</span>`;
}

function buildThemePanel() {
  const light = THEMES.filter(t => !t.dark);
  const dark  = THEMES.filter(t =>  t.dark);
  const sw = group => group.map(t => `
    <div class="theme-swatch${t.id===currentTheme?' active':''}" data-theme="${t.id}" title="${t.label}"
      style="background:${t.bg};border:2px solid ${t.accent}44" onclick="applyTheme('${t.id}')"></div>`).join('');
  return `
    <div class="theme-section-label">${L().themeLight}</div>
    <div class="theme-swatches">${sw(light)}</div>
    <div class="theme-section-label">${L().themeDark}</div>
    <div class="theme-swatches">${sw(dark)}</div>`;
}

function toggleThemePanel() {
  themePanelOpen = !themePanelOpen;
  if (langPanelOpen) { langPanelOpen = false; document.getElementById('lang-panel')?.classList.remove('open'); }
  const panel = document.getElementById('theme-panel');
  if (panel) { panel.innerHTML = themePanelOpen ? buildThemePanel() : ''; panel.classList.toggle('open', themePanelOpen); }
}

// ── Language ──────────────────────────────────────────────────────
function applyLang(code, persist = true) {
  currentLang = code;
  if (persist) localStorage.setItem('wb-lang', code);
  document.querySelectorAll('.lang-option').forEach(b => b.classList.toggle('active', b.dataset.lang === code));
  const btn = document.getElementById('btn-lang-toggle');
  if (btn) btn.textContent = L().label;
  // update LM toggle label
  const lmt = document.getElementById('lm-toggle');
  if (lmt) lmt.textContent = L().lmToggle;
  // update modal placeholders
  const mn = document.getElementById('modal-name');
  const ma = document.getElementById('modal-arch');
  if (mn) mn.placeholder = L().mNamePh;
  if (ma) ma.placeholder = L().mArchPh;
  render();
}

function buildLangPanel() {
  return LANG_ORDER.map(code => {
    const lang = LANGS[code];
    return `<button class="lang-option${code===currentLang?' active':''}" data-lang="${code}"
      onclick="applyLang('${code}');toggleLangPanel()">${lang.label} <span style="opacity:.6;font-size:10px">${lang.name}</span></button>`;
  }).join('');
}

function toggleLangPanel() {
  langPanelOpen = !langPanelOpen;
  if (themePanelOpen) { themePanelOpen = false; document.getElementById('theme-panel')?.classList.remove('open'); }
  const panel = document.getElementById('lang-panel');
  if (panel) { panel.innerHTML = langPanelOpen ? buildLangPanel() : ''; panel.classList.toggle('open', langPanelOpen); }
}

// close panels on outside click
document.addEventListener('click', e => {
  if (themePanelOpen && !document.getElementById('theme-picker-wrapper')?.contains(e.target)) {
    themePanelOpen = false; document.getElementById('theme-panel')?.classList.remove('open');
  }
  if (langPanelOpen && !document.getElementById('lang-picker-wrapper')?.contains(e.target)) {
    langPanelOpen = false; document.getElementById('lang-panel')?.classList.remove('open');
  }
});

// ── LM Studio ─────────────────────────────────────────────────────
function saveLmConfig() {
  localStorage.setItem('wb-lm-url',   document.getElementById('lm-url').value.trim());
  localStorage.setItem('wb-lm-model', document.getElementById('lm-model').value.trim());
  const el = document.getElementById('lm-saved');
  el.style.display = 'inline';
  setTimeout(() => el.style.display = 'none', 2000);
}

// ── Modal ─────────────────────────────────────────────────────────
function openModal() {
  const l = L();
  document.getElementById('modal-title').textContent  = l.modalTitle;
  document.getElementById('modal-name-label').textContent = l.mName;
  document.getElementById('modal-arch-label').textContent = l.mArch;
  document.getElementById('modal-name').placeholder   = l.mNamePh;
  document.getElementById('modal-arch').placeholder   = l.mArchPh;
  document.getElementById('btn-modal-cancel').textContent = l.cancel;
  document.getElementById('btn-modal-ok').textContent     = l.create;
  document.getElementById('modal-name').value = '';
  document.getElementById('modal-arch').value = '';
  document.getElementById('modal-overlay').classList.add('open');
  setTimeout(() => document.getElementById('modal-name').focus(), 50);
}
function closeModal() { document.getElementById('modal-overlay').classList.remove('open'); }
function modalOk() {
  const name = document.getElementById('modal-name').value.trim();
  if (!name) return;
  const arch = document.getElementById('modal-arch').value.trim();
  const c = { id:uid(), name, archetype:arch, createdAt:Date.now() };
  state.characters.push(c);
  save(); closeModal();
  selId = c.id; activeTab = 'memories'; render();
}

// ── Render ────────────────────────────────────────────────────────
function render() { renderSidebar(); renderMain(); updateTopbar(); }

function renderSidebar() {
  const list = document.getElementById('char-list');
  const l = L();
  list.innerHTML = state.characters.length
    ? state.characters.map(c => `
        <button class="char-item${c.id===selId?' active':''}" onclick="selectChar('${c.id}')">
          <div class="char-item-name">${esc(c.name)}</div>
          <div class="char-item-arch">${esc(c.archetype||'—')}</div>
        </button>`).join('')
    : `<div id="sidebar-empty">${l.noChars}</div>`;
  document.getElementById('btn-new-char').textContent = l.newChar;
  applyTheme(currentTheme, false);
  // update lang button
  const lb = document.getElementById('btn-lang-toggle');
  if (lb) lb.textContent = l.label;
}

function renderMain() {
  const area = document.getElementById('content-area');
  const l    = L();
  const char = state.characters.find(c => c.id === selId);
  if (!char) {
    area.innerHTML = `
      <div id="empty-state">
        <div id="empty-logo">WORLDBRAIN</div>
        <div id="empty-quote">${l.emptyQuote}</div>
        <div id="empty-sub">${l.emptySub}</div>
        <button id="btn-empty-new" onclick="openModal()">${l.createFirst}</button>
      </div>`;
    return;
  }
  const mems = state.memories[selId] || [];
  const memCount = `${mems.length} ${mems.length===1 ? l.memory : l.memories}`;
  area.innerHTML = `
    <div id="char-header">
      <span id="char-name">${esc(char.name)}</span>
      ${char.archetype ? `<span id="char-arch-tag">${esc(char.archetype)}</span>` : ''}
      <span id="char-count">${memCount}</span>
    </div>
    <div id="tabs">
      <button class="tab-btn${activeTab==='memories'?' active':''}" onclick="switchTab('memories')">
        ${l.tabMem}${mems.length ? `<span class="tab-badge">${mems.length}</span>` : ''}
      </button>
      <button class="tab-btn${activeTab==='brain'?' active':''}" onclick="switchTab('brain')">${l.tabBrain}</button>
      <button class="tab-btn${activeTab==='analytics'?' active':''}" onclick="switchTab('analytics')">${l.tabAnalytics}</button>
    </div>
    <div id="tab-content"></div>`;
  renderTab();
}

function switchTab(tab) { activeTab = tab; renderMain(); }
function renderTab() {
  const el = document.getElementById('tab-content');
  if (!el) return;
  if      (activeTab === 'memories')  renderMem(el);
  else if (activeTab === 'brain')     renderBrain(el);
  else                                renderAnalytics(el);
}

// ── Memories Tab ──────────────────────────────────────────────────
function renderMem(el) {
  const l    = L();
  const mems = state.memories[selId] || [];
  const char = state.characters.find(c => c.id === selId);
  const feelOpts = FEELING_KEYS
    .map(k => `<option value="${k}">${feelLabel(k)} — ${k}</option>`).join('');

  el.style.cssText = 'flex:1;overflow:hidden;display:flex;flex-direction:column';
  el.innerHTML = `
    <div id="mem-tab">
      <div id="mem-form">
        <div class="form-section-title">${l.formTitle}</div>
        <label class="form-label">${l.concept}</label>
        <input id="f-concept" class="finp" placeholder="${l.conceptPh}">
        <label class="form-label">${l.feeling}</label>
        <select id="f-feeling" class="finp">${feelOpts}</select>
        <label class="form-label">${l.content}</label>
        <textarea id="f-content" class="finp" rows="5" placeholder="${l.contentPh(esc(char.name))}"></textarea>
        <label class="form-label">${l.note} <span style="color:var(--text-muted)">${l.optional}</span></label>
        <input id="f-note" class="finp" placeholder="${l.notePh}">
        <button id="btn-add-mem" disabled onclick="addMemory()">${l.appendBtn}</button>
      </div>
      <div id="mem-list">${
        mems.length
          ? mems.map(memCard).join('')
          : `<div id="mem-empty">${l.archiveEmpty}<br><span style="font-size:11px;font-family:monospace;color:var(--text-muted)">${l.noMemYet}</span></div>`
      }</div>
    </div>`;

  const fc = document.getElementById('f-concept');
  const ft = document.getElementById('f-content');
  fc.oninput = ft.oninput = () => {
    document.getElementById('btn-add-mem').disabled = !fc.value.trim() || !ft.value.trim();
  };
  const fs = document.getElementById('f-feeling');
  fs.value = 'nostalgia';
  fs.style.color = FEELING_COLORS['nostalgia'];
  fs.onchange = () => fs.style.color = FEELING_COLORS[fs.value] || 'var(--text)';
}

function addMemory() {
  const l       = L();
  const concept = document.getElementById('f-concept').value.trim();
  const feeling = document.getElementById('f-feeling').value;
  const content = document.getElementById('f-content').value.trim();
  const note    = document.getElementById('f-note').value.trim();
  if (!concept || !content) return;
  if (!state.memories[selId]) state.memories[selId] = [];
  state.memories[selId].unshift({ id:uid(), concept, feeling, content, note, timestamp:Date.now() });
  save();
  document.getElementById('f-concept').value = '';
  document.getElementById('f-content').value = '';
  document.getElementById('f-note').value    = '';
  document.getElementById('btn-add-mem').disabled = true;
  const mems = state.memories[selId];
  document.getElementById('mem-list').innerHTML = mems.map(memCard).join('');
  const cc = document.getElementById('char-count');
  if (cc) cc.textContent = `${mems.length} ${mems.length===1 ? l.memory : l.memories}`;
  const tb = document.querySelector('#tabs .tab-badge');
  if (tb) tb.textContent = mems.length;
  else { const ft = document.querySelector('#tabs .tab-btn'); if (ft) ft.innerHTML = `${l.tabMem}<span class="tab-badge">${mems.length}</span>`; }
}

function memCard(m) {
  const color = FEELING_COLORS[m.feeling] || 'var(--accent)';
  const label = feelLabel(m.feeling);
  return `
    <div class="mem-card" style="border-left:3px solid ${color}">
      <div class="mem-card-header">
        <span class="mem-concept">${esc(m.concept)}</span>
        <span class="mem-pill" style="background:${color}1a;color:${color}">${label}</span>
        <span class="mem-date">${fmtDate(m.timestamp)}</span>
      </div>
      <div class="mem-content">"${esc(m.content)}"</div>
      ${m.note ? `<div class="mem-note">${esc(m.note)}</div>` : ''}
    </div>`;
}

// ── Brain Tab ─────────────────────────────────────────────────────
function renderBrain(el) {
  const l    = L();
  const char = state.characters.find(c => c.id === selId);
  const mems = state.memories[selId] || [];
  const msgs = state.chats[selId]   || [];
  el.style.cssText = 'flex:1;overflow:hidden;display:flex;flex-direction:column';
  el.innerHTML = `
    <div id="brain-tab">
      <div id="brain-ctx">
        <span id="brain-ctx-info">${l.brainCtx(esc(char.name), mems.length)}</span>
        <span id="brain-error"></span>
        <button id="btn-clear-chat" onclick="clearChat()" style="${msgs.length?'':'display:none'}">${l.clearChat}</button>
      </div>
      <div id="chat-messages">${
        msgs.length
          ? msgs.map(msgHTML).join('') + '<div id="chat-bottom"></div>'
          : brainEmpty(char)
      }</div>
      <div id="chat-input-row">
        <input id="chat-input" placeholder="${l.askPh(esc(char.name))}"
          onkeydown="if(event.key==='Enter'&&!event.shiftKey)sendBrain()">
        <button id="btn-send" disabled onclick="sendBrain()">${l.askBtn}</button>
      </div>
    </div>`;
  document.getElementById('chat-input').oninput = function() {
    document.getElementById('btn-send').disabled = !this.value.trim() || chatLoading;
  };
  scrollChat();
}

function brainEmpty(char) {
  const l = L();
  return `
    <div id="chat-empty">
      <div id="chat-empty-title">${l.brainAwaits(esc(char.name))}</div>
      <div id="chat-empty-sub">${l.brainSub}</div>
      <div id="suggestions">${l.suggs(char.name).map(s =>
        `<button class="sugg-btn" onclick="fillSugg(this)">${esc(s)}</button>`
      ).join('')}</div>
    </div>
    <div id="chat-bottom"></div>`;
}

function fillSugg(btn) {
  const i = document.getElementById('chat-input');
  i.value = btn.textContent; i.dispatchEvent(new Event('input')); i.focus();
}
function msgHTML(m) {
  if (m.role === 'assistant')
    return `<div class="msg assistant"><div class="msg-avatar">B</div><div class="bubble ai">${esc(m.content)}</div></div>`;
  return `<div class="msg user"><div class="bubble user">${esc(m.content)}</div></div>`;
}
function scrollChat() {
  setTimeout(() => document.getElementById('chat-bottom')?.scrollIntoView({ behavior:'smooth' }), 40);
}
function clearChat() { state.chats[selId] = []; save(); renderMain(); }

async function sendBrain() {
  if (chatLoading) return;
  const l   = L();
  const inp = document.getElementById('chat-input');
  const text = inp.value.trim();
  if (!text) return;
  const char = state.characters.find(c => c.id === selId);
  const mems = state.memories[selId] || [];
  if (!state.chats[selId]) state.chats[selId] = [];
  state.chats[selId].push({ role:'user', content:text });
  inp.value = ''; chatLoading = true;
  document.getElementById('btn-send').disabled = true;

  const msgsEl = document.getElementById('chat-messages');
  msgsEl.innerHTML = state.chats[selId].map(msgHTML).join('') +
    `<div class="msg assistant"><div class="msg-avatar">B</div>
      <div class="bubble ai"><div class="typing">
        ${[0,1,2].map(i=>`<div class="dot" style="animation-delay:${i*.22}s"></div>`).join('')}
      </div></div></div>
    <div id="chat-bottom"></div>`;
  scrollChat();
  document.getElementById('btn-clear-chat').style.display = 'inline';

  const memBlock = mems.length
    ? mems.slice(0, 30).map(m =>
        `[${fmtDate(m.timestamp)}] CONCEPT: ${m.concept} | FEELING: ${feelLabel(m.feeling)}\n"${m.content}"${m.note?'\n[note:'+m.note+']':''}`
      ).join('\n\n')
    : '[Archive is empty]';

  const sys = `You are the psychological Brain of ${char.name} — ${char.archetype||'a narrative character'}.
You have access to this character's MNHEME: an append-only emotional memory archive.
═══ EMOTIONAL MEMORY ARCHIVE ═══\n${memBlock}\n════════════════════════════════
Stay faithful to these memories. Never fabricate experiences not in the archive. Speak with psychological depth and narrative richness. If the archive is sparse, acknowledge it honestly. Reply in the same language as the user's question.`;

  const lmUrl   = document.getElementById('lm-url').value.trim();
  const lmModel = document.getElementById('lm-model').value.trim();
  let reply = '';
  try {
    const res = await fetch(lmUrl, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({
        model: lmModel || 'local-model',
        max_tokens: 1000, temperature: 0.7,
        messages: [
          { role:'system', content:sys },
          ...state.chats[selId].map(m => ({ role:m.role, content:m.content }))
        ]
      })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status} — LM Studio running? Model loaded?`);
    const data = await res.json();
    reply = data.choices?.[0]?.message?.content || '[Empty response]';
    const errEl = document.getElementById('brain-error'); if (errEl) errEl.textContent = '';
  } catch(e) {
    reply = `[Brain unreachable — ${e.message}]`;
    const errEl = document.getElementById('brain-error'); if (errEl) errEl.textContent = '⚠ ' + e.message;
  }
  state.chats[selId].push({ role:'assistant', content:reply });
  save(); chatLoading = false;
  msgsEl.innerHTML = state.chats[selId].map(msgHTML).join('') + '<div id="chat-bottom"></div>';
  scrollChat();
  const si = document.getElementById('btn-send'); const ci = document.getElementById('chat-input');
  if (si && ci) { si.disabled = !ci.value.trim(); ci.focus(); }
}

// ── Analytics Tab ─────────────────────────────────────────────────
function renderAnalytics(el) {
  el.style.cssText = 'flex:1;overflow:hidden;display:flex;flex-direction:column';
  const l    = L();
  const mems = state.memories[selId] || [];
  if (!mems.length) {
    el.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;height:100%;color:var(--text-muted);font-style:italic;font-size:14px">${l.noAnalytics}</div>`;
    return;
  }
  const feelDist = FEELING_KEYS
    .map(k => ({ k, label:feelLabel(k), color:FEELING_COLORS[k], n:mems.filter(m=>m.feeling===k).length }))
    .filter(d => d.n > 0).sort((a,b) => b.n - a.n);
  const maxF = feelDist[0]?.n || 1;
  const cm = {};
  mems.forEach(m => {
    if (!cm[m.concept]) cm[m.concept] = { total:0, f:{} };
    cm[m.concept].total++;
    cm[m.concept].f[m.feeling] = (cm[m.concept].f[m.feeling]||0) + 1;
  });
  const concepts = Object.entries(cm).sort((a,b) => b[1].total - a[1].total);

  el.innerHTML = `
    <div id="analytics-tab">
      <div class="a-grid">
        <div class="a-card">
          <div class="a-title">${l.emotDist}</div>
          ${feelDist.map(d => `
            <div class="bar-row">
              <div class="bar-label">${d.label}</div>
              <div class="bar-track"><div class="bar-fill" style="width:${Math.round(d.n/maxF*100)}%;background:${d.color}"></div></div>
              <div class="bar-n">${d.n}</div>
            </div>`).join('')}
        </div>
        <div class="a-card">
          <div class="a-title">${l.conceptMap}</div>
          ${concepts.map(([concept, data]) => {
            const dom = Object.entries(data.f).sort((a,b) => b[1]-a[1])[0];
            const col = FEELING_COLORS[dom[0]] || 'var(--accent)';
            return `<div class="c-row">
              <div class="c-dot" style="background:${col}"></div>
              <div class="c-name">${esc(concept)}</div>
              <span class="c-dom" style="background:${col}1a;color:${col}">${feelLabel(dom[0])}</span>
              <div class="c-n">${data.total}</div>
            </div>`;
          }).join('')}
        </div>
      </div>
      <div class="a-card" style="max-width:800px">
        <div class="a-title">${l.timeline(mems.length)}</div>
        ${mems.map((m, i) => {
          const col = FEELING_COLORS[m.feeling] || 'var(--accent)';
          return `<div class="tl-row">
            <div class="tl-spine">
              <div class="tl-dot" style="background:${col};box-shadow:0 0 5px ${col}55"></div>
              ${i < mems.length-1 ? '<div class="tl-line"></div>' : ''}
            </div>
            <div class="tl-body">
              <div class="tl-meta">
                <span class="tl-concept">${esc(m.concept)}</span>
                <span class="tl-feel" style="color:${col}">${feelLabel(m.feeling)}</span>
                <span class="tl-date">${fmtDate(m.timestamp)}</span>
              </div>
              <div class="tl-text">"${esc(m.content.length>120 ? m.content.slice(0,120)+'…' : m.content)}"</div>
            </div>
          </div>`;
        }).join('')}
      </div>
    </div>`;
}

// ── Mobile sidebar ────────────────────────────────────────────────
function toggleSidebar() {
  const s = document.getElementById('sidebar');
  const b = document.getElementById('sidebar-backdrop');
  const isOpen = s.classList.contains('open');
  s.classList.toggle('open', !isOpen); b.classList.toggle('open', !isOpen);
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebar-backdrop').classList.remove('open');
}

// ── LM bar toggle ─────────────────────────────────────────────────
function toggleLmBar() {
  document.getElementById('lm-bar').classList.toggle('collapsed');
  document.getElementById('lm-toggle').classList.toggle('open');
}

// ── Topbar ────────────────────────────────────────────────────────
function updateTopbar() {
  const el = document.getElementById('topbar-char');
  if (!el) return;
  const char = state.characters.find(c => c.id === selId);
  el.textContent = char ? char.name : '';
}

// ── Nav ───────────────────────────────────────────────────────────
function selectChar(id) {
  selId = id; activeTab = 'memories'; chatLoading = false;
  closeSidebar(); render();
}

// ── Boot ──────────────────────────────────────────────────────────
load();
render();
