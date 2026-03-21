/* ═══════════════════════════════════════════════════════════
   MEMORIA — app.js
   Personal MNHEME Dashboard
   i18n: EN / IT / ES / ZH
   ═══════════════════════════════════════════════════════════ */

// ══ i18n ════════════════════════════════════════════════════
const LANGS = {
  en: {
    code:'en', label:'EN', name:'English',
    wordmark:     'MEMORIA',
    tagline:      'personal emotional archive',
    dashTitle:    'Emotional Dashboard',
    formTitle:    'Record a memory',
    concept:      'Concept',
    feeling:      'Feeling',
    content:      'Content',
    note:         'Note',
    optional:     '(optional)',
    conceptPh:    'Work, Family, Health\u2026',
    contentPh:    'What happened\u2026',
    notePh:       'Context, place\u2026',
    addBtn:       'Add to archive',
    recentTitle:  'Recent',
    noMemories:   'No memories yet.\nStart recording your inner life.',
    themeBtn:     '\u25a1  Theme',
    themeLight:   '\u2014 LIGHT \u2014',
    themeDark:    '\u2014 DARK \u2014',
    lmSave:       'Save',
    lmModelPh:    'model (blank\u2009=\u2009auto)',
    statTotal:    'Total entries',
    statConcepts: 'Concepts',
    statStreak:   'Day streak',
    statFeeling:  'This week',
    statStreakSub: n => `${n} day${n===1?'':'s'} in a row`,
    statNone:     '\u2014',
    calTitle:     'Emotional calendar',
    months:       ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
    days:         ['M','T','W','T','F','S','S'],
    conceptTitle: 'Concept cloud',
    feelTitle:    'Feeling distribution',
    arcTitle:     'Emotional arc',
    arcSelect:    'Select concept\u2026',
    arcEmpty:     'Select a concept to see its emotional arc over time.',
    arcNoData:    'Not enough data for this concept yet.',
    brainTitle:   'Brain',
    brainEmpty:   'Ask about your emotional patterns, a concept, or your recent arc.',
    brainPh:      'Ask the Brain\u2026',
    brainAsk:     'Ask',
    brainClear:   'clear',
    brainLabel:   'BRAIN',
    youLabel:     'YOU',
    noAnalytics:  'Add more memories to unlock analytics.',
    feelLabels: {
      gioia:'Joy', tristezza:'Sadness', rabbia:'Rage', paura:'Fear',
      nostalgia:'Nostalgia', amore:'Love', malinconia:'Melancholy',
      serenità:'Serenity', sorpresa:'Surprise', ansia:'Anxiety',
      gratitudine:'Gratitude', vergogna:'Shame', orgoglio:'Pride',
      noia:'Boredom', curiosità:'Curiosity',
    },
    sysLang: 'Reply in English.',
    fmtDate: d => d.toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'}),
  },
  it: {
    code:'it', label:'IT', name:'Italiano',
    wordmark:     'MEMORIA',
    tagline:      'archivio emotivo personale',
    dashTitle:    'Dashboard Emotiva',
    formTitle:    'Registra un ricordo',
    concept:      'Concetto',
    feeling:      'Sentimento',
    content:      'Contenuto',
    note:         'Nota',
    optional:     '(opzionale)',
    conceptPh:    'Lavoro, Famiglia, Salute\u2026',
    contentPh:    'Cosa \u00e8 successo\u2026',
    notePh:       'Contesto, luogo\u2026',
    addBtn:       'Aggiungi all\'archivio',
    recentTitle:  'Recenti',
    noMemories:   'Nessun ricordo ancora.\nInizia a registrare la tua vita interiore.',
    themeBtn:     '\u25a1  Tema',
    themeLight:   '\u2014 CHIARO \u2014',
    themeDark:    '\u2014 SCURO \u2014',
    lmSave:       'Salva',
    lmModelPh:    'modello (vuoto\u2009=\u2009auto)',
    statTotal:    'Totale voci',
    statConcepts: 'Concetti',
    statStreak:   'Giorni consecutivi',
    statFeeling:  'Questa settimana',
    statStreakSub: n => `${n} giorno${n===1?'':'i'} di fila`,
    statNone:     '\u2014',
    calTitle:     'Calendario emotivo',
    months:       ['Gen','Feb','Mar','Apr','Mag','Giu','Lug','Ago','Set','Ott','Nov','Dic'],
    days:         ['L','M','M','G','V','S','D'],
    conceptTitle: 'Nuvola dei concetti',
    feelTitle:    'Distribuzione sentimenti',
    arcTitle:     'Arco emotivo',
    arcSelect:    'Seleziona concetto\u2026',
    arcEmpty:     'Seleziona un concetto per vedere il suo arco emotivo nel tempo.',
    arcNoData:    'Non abbastanza dati per questo concetto.',
    brainTitle:   'Cervello',
    brainEmpty:   'Chiedi dei tuoi pattern emotivi, un concetto, o il tuo arco recente.',
    brainPh:      'Chiedi al Cervello\u2026',
    brainAsk:     'Chiedi',
    brainClear:   'cancella',
    brainLabel:   'CERVELLO',
    youLabel:     'TU',
    noAnalytics:  'Aggiungi altri ricordi per sbloccare le analisi.',
    feelLabels: {
      gioia:'Gioia', tristezza:'Tristezza', rabbia:'Rabbia', paura:'Paura',
      nostalgia:'Nostalgia', amore:'Amore', malinconia:'Malinconia',
      serenità:'Serenità', sorpresa:'Sorpresa', ansia:'Ansia',
      gratitudine:'Gratitudine', vergogna:'Vergogna', orgoglio:'Orgoglio',
      noia:'Noia', curiosità:'Curiosità',
    },
    sysLang: 'Rispondi in italiano.',
    fmtDate: d => d.toLocaleDateString('it-IT',{day:'numeric',month:'short',year:'numeric'}),
  },
  es: {
    code:'es', label:'ES', name:'Español',
    wordmark:     'MEMORIA',
    tagline:      'archivo emocional personal',
    dashTitle:    'Panel Emocional',
    formTitle:    'Registrar un recuerdo',
    concept:      'Concepto',
    feeling:      'Sentimiento',
    content:      'Contenido',
    note:         'Nota',
    optional:     '(opcional)',
    conceptPh:    'Trabajo, Familia, Salud\u2026',
    contentPh:    'Qu\u00e9 pas\u00f3\u2026',
    notePh:       'Contexto, lugar\u2026',
    addBtn:       'A\u00f1adir al archivo',
    recentTitle:  'Recientes',
    noMemories:   'Sin recuerdos aún.\nEmpieza a registrar tu vida interior.',
    themeBtn:     '\u25a1  Tema',
    themeLight:   '\u2014 CLARO \u2014',
    themeDark:    '\u2014 OSCURO \u2014',
    lmSave:       'Guardar',
    lmModelPh:    'modelo (vacío\u2009=\u2009auto)',
    statTotal:    'Total entradas',
    statConcepts: 'Conceptos',
    statStreak:   'Racha de días',
    statFeeling:  'Esta semana',
    statStreakSub: n => `${n} día${n===1?'':'s'} seguido${n===1?'':'s'}`,
    statNone:     '\u2014',
    calTitle:     'Calendario emocional',
    months:       ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
    days:         ['L','M','X','J','V','S','D'],
    conceptTitle: 'Nube de conceptos',
    feelTitle:    'Distribución de sentimientos',
    arcTitle:     'Arco emocional',
    arcSelect:    'Seleccionar concepto\u2026',
    arcEmpty:     'Selecciona un concepto para ver su arco emocional.',
    arcNoData:    'No hay suficientes datos para este concepto aún.',
    brainTitle:   'Mente',
    brainEmpty:   'Pregunta sobre tus patrones emocionales, un concepto, o tu arco reciente.',
    brainPh:      'Pregunta a la Mente\u2026',
    brainAsk:     'Preguntar',
    brainClear:   'limpiar',
    brainLabel:   'MENTE',
    youLabel:     'TÚ',
    noAnalytics:  'Añade más recuerdos para desbloquear los análisis.',
    feelLabels: {
      gioia:'Alegría', tristezza:'Tristeza', rabbia:'Rabia', paura:'Miedo',
      nostalgia:'Nostalgia', amore:'Amor', malinconia:'Melancolía',
      serenità:'Serenidad', sorpresa:'Sorpresa', ansia:'Ansiedad',
      gratitudine:'Gratitud', vergogna:'Vergüenza', orgoglio:'Orgullo',
      noia:'Aburrimiento', curiosità:'Curiosidad',
    },
    sysLang: 'Responde en español.',
    fmtDate: d => d.toLocaleDateString('es-ES',{day:'numeric',month:'short',year:'numeric'}),
  },
  zh: {
    code:'zh', label:'中', name:'中文',
    wordmark:     '记忆',
    tagline:      '个人情感档案',
    dashTitle:    '情感仪表板',
    formTitle:    '记录一段记忆',
    concept:      '概念',
    feeling:      '情感',
    content:      '内容',
    note:         '备注',
    optional:     '（可选）',
    conceptPh:    '工作、家庭、健康……',
    contentPh:    '发生了什么……',
    notePh:       '背景、地点……',
    addBtn:       '添加到档案',
    recentTitle:  '最近',
    noMemories:   '暂无记忆。\n开始记录你的内心生活。',
    themeBtn:     '□  主题',
    themeLight:   '— 浅色 —',
    themeDark:    '— 深色 —',
    lmSave:       '保存',
    lmModelPh:    '模型（留空=自动）',
    statTotal:    '总条目',
    statConcepts: '概念数',
    statStreak:   '连续天数',
    statFeeling:  '本周情感',
    statStreakSub: n => `连续 ${n} 天`,
    statNone:     '—',
    calTitle:     '情感日历',
    months:       ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'],
    days:         ['一','二','三','四','五','六','日'],
    conceptTitle: '概念云',
    feelTitle:    '情感分布',
    arcTitle:     '情感弧线',
    arcSelect:    '选择概念……',
    arcEmpty:     '选择一个概念以查看其随时间的情感弧线。',
    arcNoData:    '该概念尚无足够数据。',
    brainTitle:   '大脑',
    brainEmpty:   '询问你的情感模式、某个概念或最近的弧线。',
    brainPh:      '向大脑提问……',
    brainAsk:     '提问',
    brainClear:   '清除',
    brainLabel:   '大脑',
    youLabel:     '你',
    noAnalytics:  '添加更多记忆以解锁分析。',
    feelLabels: {
      gioia:'喜悦', tristezza:'悲伤', rabbia:'愤怒', paura:'恐惧',
      nostalgia:'怀旧', amore:'爱', malinconia:'忧郁',
      serenità:'宁静', sorpresa:'惊讶', ansia:'焦虑',
      gratitudine:'感恩', vergogna:'羞耻', orgoglio:'自豪',
      noia:'无聊', curiosità:'好奇',
    },
    sysLang: '请用中文回复。',
    fmtDate: d => d.toLocaleDateString('zh-CN',{year:'numeric',month:'short',day:'numeric'}),
  },
};
const LANG_ORDER = ['en','it','es','zh'];

// ══ Theme data ════════════════════════════════════════════════
const THEMES = [
  {id:'pearl',    label:'Pearl',     bg:'#f6f4f0', acc:'#4a7c59', dark:false},
  {id:'latte',    label:'Latte',     bg:'#f5f0e8', acc:'#8b6914', dark:false},
  {id:'sky',      label:'Sky',       bg:'#f0f5fb', acc:'#1a6fa8', dark:false},
  {id:'bloom',    label:'Bloom',     bg:'#fdf0f4', acc:'#a83060', dark:false},
  {id:'sage',     label:'Sage',      bg:'#eef2ee', acc:'#2e6e3e', dark:false},
  {id:'sand',     label:'Sand',      bg:'#f8f4ec', acc:'#c07030', dark:false},
  {id:'violet',   label:'Violet',    bg:'#f4f0fb', acc:'#6040c0', dark:false},
  {id:'chalk',    label:'Chalk',     bg:'#f8f8f4', acc:'#303090', dark:false},
  {id:'peach',    label:'Peach',     bg:'#fdf2ec', acc:'#c05830', dark:false},
  {id:'fog',      label:'Fog',       bg:'#f0f2f5', acc:'#3858b8', dark:false},
  {id:'obsidian', label:'Obsidian',  bg:'#0e0f10', acc:'#60c080', dark:true},
  {id:'midnight', label:'Midnight',  bg:'#080c18', acc:'#5888f0', dark:true},
  {id:'ember',    label:'Ember',     bg:'#100c08', acc:'#e88030', dark:true},
  {id:'void',     label:'Void',      bg:'#000000', acc:'#c0c0c0', dark:true},
  {id:'forest',   label:'Forest',    bg:'#060e08', acc:'#40d060', dark:true},
  {id:'crimson',  label:'Crimson',   bg:'#100608', acc:'#e04848', dark:true},
  {id:'amethyst', label:'Amethyst',  bg:'#080610', acc:'#b070f8', dark:true},
  {id:'ocean',    label:'Ocean',     bg:'#040c10', acc:'#30c0d8', dark:true},
  {id:'graphite', label:'Graphite',  bg:'#101214', acc:'#88a8c8', dark:true},
  {id:'candle',   label:'Candle',    bg:'#100c06', acc:'#f8c830', dark:true},
];

// ══ Feelings ══════════════════════════════════════════════════
const FEELING_KEYS = [
  'gioia','tristezza','rabbia','paura','nostalgia','amore',
  'malinconia','serenità','sorpresa','ansia','gratitudine',
  'vergogna','orgoglio','noia','curiosità'
];
const FEELING_COLORS = {
  gioia:'#f59e0b', tristezza:'#6ea8fe', rabbia:'#f87171', paura:'#a78bfa',
  nostalgia:'#fb923c', amore:'#f472b6', malinconia:'#818cf8', serenità:'#34d399',
  sorpresa:'#fcd34d', ansia:'#94a3b8', gratitudine:'#6ee7b7', vergogna:'#fca5a5',
  orgoglio:'#c084fc', noia:'#6b7280', curiosità:'#67e8f9',
};
// Valence for streak coloring (positive/negative)
const FEEL_VAL = {
  gioia:1, tristezza:-1, rabbia:-1, paura:-1, nostalgia:0,
  amore:1, malinconia:-1, serenità:1, sorpresa:0, ansia:-1,
  gratitudine:1, vergogna:-1, orgoglio:1, noia:-1, curiosità:1,
};

// ══ State ══════════════════════════════════════════════════════
const SK           = 'memoria-v1';
let memories       = [];
let currentLang    = 'en';
let currentTheme   = 'pearl';
let themePanelOpen = false;
let langPanelOpen  = false;
let brainHistory   = [];
let brainLoading   = false;
let selectedArcConcept = '';

// ══ Utils ══════════════════════════════════════════════════════
const uid  = () => Math.random().toString(36).slice(2,10);
const esc  = s => String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const L    = () => LANGS[currentLang] || LANGS.en;
const fl   = k => L().feelLabels[k] || k;
const col  = k => FEELING_COLORS[k] || '#888';

function today() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

function parseDate(ts) {
  return new Date(ts);
}

// ══ Persistence ════════════════════════════════════════════════
function load() {
  try {
    const raw = localStorage.getItem(SK);
    if (raw) memories = JSON.parse(raw);
  } catch(e) {}
  const t = localStorage.getItem('mem-theme');
  const g = localStorage.getItem('mem-lang');
  const u = localStorage.getItem('mem-lm-url');
  const m = localStorage.getItem('mem-lm-model');
  if (t && THEMES.find(x => x.id===t)) currentTheme = t;
  if (g && LANGS[g]) currentLang = g;
  if (u) document.getElementById('lm-url').value = u;
  if (m) document.getElementById('lm-model').value = m;
  applyTheme(currentTheme, false);
  applyLang(currentLang, false);
}

function save() {
  try { localStorage.setItem(SK, JSON.stringify(memories)); } catch(e) {}
}

function saveLm() {
  localStorage.setItem('mem-lm-url',   document.getElementById('lm-url').value.trim());
  localStorage.setItem('mem-lm-model', document.getElementById('lm-model').value.trim());
  const el = document.getElementById('lm-saved');
  el.style.display = 'inline';
  setTimeout(() => el.style.display = 'none', 2000);
}

// ══ Theme ══════════════════════════════════════════════════════
function applyTheme(id, persist=true) {
  currentTheme = id;
  document.documentElement.setAttribute('data-theme', id);
  if (persist) localStorage.setItem('mem-theme', id);
  document.querySelectorAll('.theme-dot').forEach(d => d.classList.toggle('active', d.dataset.theme===id));
  const th = THEMES.find(t => t.id===id);
  const btn = document.getElementById('btn-theme-toggle');
  if (btn && th) btn.innerHTML =
    `<span style="display:inline-block;width:11px;height:11px;background:${th.acc};border-radius:3px;flex-shrink:0"></span>${L().themeBtn.replace(/^\S+\s+/,'')}`;
}

function buildThemePanel() {
  const l = L();
  const sw = group => group.map(t =>
    `<div class="theme-dot${t.id===currentTheme?' active':''}" data-theme="${t.id}" title="${t.label}"
      style="background:${t.bg};outline:2px solid ${t.acc}44"
      onclick="applyTheme('${t.id}')"></div>`).join('');
  return `<div class="panel-label">${l.themeLight}</div>
    <div class="swatch-row">${sw(THEMES.filter(t=>!t.dark))}</div>
    <div class="panel-label">${l.themeDark}</div>
    <div class="swatch-row">${sw(THEMES.filter(t=>t.dark))}</div>`;
}

function toggleThemePanel() {
  themePanelOpen = !themePanelOpen;
  if (langPanelOpen) { langPanelOpen=false; document.getElementById('lang-panel')?.classList.remove('open'); }
  const p = document.getElementById('theme-panel');
  if (p) { p.innerHTML = themePanelOpen ? buildThemePanel() : ''; p.classList.toggle('open', themePanelOpen); }
}

// ══ Language ═══════════════════════════════════════════════════
function applyLang(code, persist=true) {
  currentLang = code;
  document.documentElement.lang = code;
  if (persist) localStorage.setItem('mem-lang', code);
  document.querySelectorAll('.lang-btn').forEach(b => b.classList.toggle('active', b.dataset.lang===code));
  renderStaticText();
  render();
}

function buildLangPanel() {
  return LANG_ORDER.map(code => {
    const lg = LANGS[code];
    return `<button class="lang-btn${code===currentLang?' active':''}" data-lang="${code}"
      onclick="applyLang('${code}');toggleLangPanel()">${lg.label}
      <span class="lang-name">${lg.name}</span></button>`;
  }).join('');
}

function toggleLangPanel() {
  langPanelOpen = !langPanelOpen;
  if (themePanelOpen) { themePanelOpen=false; document.getElementById('theme-panel')?.classList.remove('open'); }
  const p = document.getElementById('lang-panel');
  if (p) { p.innerHTML = langPanelOpen ? buildLangPanel() : ''; p.classList.toggle('open', langPanelOpen); }
}

document.addEventListener('click', e => {
  const tw = document.getElementById('theme-picker-wrapper');
  const lw = document.getElementById('lang-picker-wrapper');
  if (themePanelOpen && tw && !tw.contains(e.target)) { themePanelOpen=false; document.getElementById('theme-panel')?.classList.remove('open'); }
  if (langPanelOpen  && lw && !lw.contains(e.target)) { langPanelOpen=false;  document.getElementById('lang-panel')?.classList.remove('open'); }
});

// ══ Static text ════════════════════════════════════════════════
function renderStaticText() {
  const l = L();
  const s = (id, txt) => { const el=document.getElementById(id); if(el) el.textContent=txt; };
  const p = (id, txt) => { const el=document.getElementById(id); if(el) el.placeholder=txt; };
  const h = (id, html) => { const el=document.getElementById(id); if(el) el.innerHTML=html; };

  s('sidebar-wordmark',  l.wordmark);
  s('sidebar-tagline',   l.tagline);
  s('form-title',        l.formTitle);
  s('label-concept',     l.concept);
  s('label-feeling',     l.feeling);
  s('label-content',     l.content);
  s('label-note',        `${l.note} ${l.optional}`);
  s('btn-add',           l.addBtn);
  s('recent-title',      l.recentTitle);
  s('dash-title',        l.dashTitle);
  s('btn-lm-save',       l.lmSave);
  p('lm-model',          l.lmModelPh);
  p('f-concept',         l.conceptPh);
  p('f-content',         l.contentPh);
  p('f-note',            l.notePh);
  s('stat-total-label',  l.statTotal);
  s('stat-concepts-label',l.statConcepts);
  s('stat-streak-label', l.statStreak);
  s('stat-feeling-label',l.statFeeling);
  s('cal-section-title', l.calTitle);
  s('concept-section-title', l.conceptTitle);
  s('feel-section-title', l.feelTitle);
  s('arc-section-title', l.arcTitle);
  s('brain-title',       l.brainTitle);
  p('brain-input',       l.brainPh);
  s('btn-brain-ask',     l.brainAsk);
  s('btn-brain-clear',   l.brainClear);

  // feeling select options
  const fs = document.getElementById('f-feeling');
  if (fs) {
    const curVal = fs.value;
    fs.innerHTML = FEELING_KEYS.map(k =>
      `<option value="${k}">${fl(k)}</option>`).join('');
    fs.value = curVal || 'gioia';
    fs.style.color = col(fs.value);
  }

  // arc select
  rebuildArcSelect();

  const lb = document.getElementById('btn-lang-toggle');
  if (lb) lb.textContent = l.label;

  const th = THEMES.find(t => t.id===currentTheme);
  const tb = document.getElementById('btn-theme-toggle');
  if (tb && th)
    tb.innerHTML = `<span style="display:inline-block;width:11px;height:11px;background:${th.acc};border-radius:3px;flex-shrink:0"></span>${l.themeBtn.replace(/^\S+\s+/,'')}`;
}

// ══ Entry form ══════════════════════════════════════════════════
function setupForm() {
  const fc = document.getElementById('f-concept');
  const ft = document.getElementById('f-content');
  const btn = document.getElementById('btn-add');
  const fs = document.getElementById('f-feeling');

  fs.onchange = () => fs.style.color = col(fs.value);
  fs.style.color = col(fs.value||'gioia');

  const check = () => { btn.disabled = !fc.value.trim() || !ft.value.trim(); };
  fc.oninput = ft.oninput = check;
  btn.disabled = true;
}

function addMemory() {
  const concept = document.getElementById('f-concept').value.trim();
  const feeling = document.getElementById('f-feeling').value;
  const content = document.getElementById('f-content').value.trim();
  const note    = document.getElementById('f-note').value.trim();
  if (!concept || !content) return;

  memories.unshift({
    id: uid(), concept, feeling, content, note,
    date: today(), ts: Date.now()
  });
  save();

  document.getElementById('f-concept').value = '';
  document.getElementById('f-content').value = '';
  document.getElementById('f-note').value    = '';
  document.getElementById('btn-add').disabled = true;

  render();
}

// ══ Master render ═══════════════════════════════════════════════
function render() {
  renderRecentList();
  renderStats();
  renderCalendar();
  renderConceptCloud();
  renderFeelingBars();
  rebuildArcSelect();
  renderArc();
  renderBrainEmpty();
}

// ══ Recent list ═════════════════════════════════════════════════
function renderRecentList() {
  const l    = L();
  const list = document.getElementById('recent-list');
  const cnt  = document.getElementById('recent-count');
  if (cnt) cnt.textContent = memories.length > 0 ? `(${memories.length})` : '';

  if (!memories.length) {
    list.innerHTML = `<div id="sidebar-empty">${esc(l.noMemories).replace('\n','<br>')}</div>`;
    return;
  }
  list.innerHTML = memories.slice(0,40).map(m => {
    const c = col(m.feeling);
    return `<div class="mem-item fade-in" onclick="">
      <div class="mem-item-top">
        <span class="mem-item-concept">${esc(m.concept)}</span>
        <span class="mem-item-pill" style="background:${c}18;color:${c}">${fl(m.feeling)}</span>
        <span class="mem-item-date">${m.date.slice(5)}</span>
      </div>
      <div class="mem-item-content">${esc(m.content)}</div>
    </div>`;
  }).join('');
}

// ══ Stats ═══════════════════════════════════════════════════════
function renderStats() {
  const l = L();

  // total
  setStatValue('stat-total', memories.length, '');

  // unique concepts
  const concepts = [...new Set(memories.map(m => m.concept))];
  setStatValue('stat-concepts', concepts.length, '');

  // streak
  const streak = calcStreak();
  setStatValue('stat-streak', streak, l.statStreakSub(streak));

  // this week dominant feeling
  const weekAgo  = Date.now() - 7*24*3600*1000;
  const weekMems = memories.filter(m => m.ts >= weekAgo);
  if (weekMems.length) {
    const freq = {};
    weekMems.forEach(m => freq[m.feeling] = (freq[m.feeling]||0)+1);
    const top = Object.entries(freq).sort((a,b)=>b[1]-a[1])[0][0];
    const c   = col(top);
    document.getElementById('stat-feeling-val').textContent  = fl(top);
    document.getElementById('stat-feeling-val').style.color  = c;
    document.getElementById('stat-feeling-sub').textContent  = `${weekMems.length} entries`;
  } else {
    document.getElementById('stat-feeling-val').textContent  = l.statNone;
    document.getElementById('stat-feeling-val').style.color  = '';
    document.getElementById('stat-feeling-sub').textContent  = '';
  }
}

function setStatValue(id, val, sub) {
  const el = document.getElementById(id+'-val');
  const su = document.getElementById(id+'-sub');
  if (el) el.textContent = val;
  if (su) su.textContent = sub;
}

function calcStreak() {
  if (!memories.length) return 0;
  const dates = [...new Set(memories.map(m => m.date))].sort().reverse();
  let streak = 0;
  const d = new Date();
  for (let i = 0; i < dates.length; i++) {
    const expected = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()-i).padStart(2,'0')}`;
    // simple: just count consecutive days backwards from today
    const target = new Date(); target.setDate(target.getDate() - i);
    const key = `${target.getFullYear()}-${String(target.getMonth()+1).padStart(2,'0')}-${String(target.getDate()).padStart(2,'0')}`;
    if (dates.includes(key)) streak++;
    else break;
  }
  return streak;
}

// ══ Calendar heatmap ════════════════════════════════════════════
function renderCalendar() {
  const l    = L();
  const wrap = document.getElementById('calendar-svg-wrap');
  if (!wrap) return;

  // build date → dominant feeling map
  const dateMap = {};
  memories.forEach(m => {
    if (!dateMap[m.date]) dateMap[m.date] = {};
    dateMap[m.date][m.feeling] = (dateMap[m.date][m.feeling]||0)+1;
  });

  const CW = 12, CH = 12, GAP = 3;
  const COLS = 53;
  const ROWS = 7;
  const LEFT = 24; // space for day labels
  const TOP  = 24; // space for month labels

  const svgW = LEFT + COLS*(CW+GAP);
  const svgH = TOP  + ROWS*(CH+GAP) + 20;

  // figure out start date: Monday of the week 52 weeks ago
  const now   = new Date();
  const start = new Date(now);
  start.setDate(start.getDate() - (COLS-1)*7);
  // align to Monday
  const dow = start.getDay(); // 0=Sun
  start.setDate(start.getDate() - ((dow+6)%7));

  let cells = '';
  let monthLabels = '';
  let lastMonth = -1;

  for (let wk = 0; wk < COLS; wk++) {
    for (let row = 0; row < ROWS; row++) {
      const d = new Date(start);
      d.setDate(d.getDate() + wk*7 + row);
      const key = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
      const x   = LEFT + wk*(CW+GAP);
      const y   = TOP  + row*(CH+GAP);

      // month label
      if (row === 0 && d.getMonth() !== lastMonth) {
        monthLabels += `<text x="${x}" y="${TOP-6}" font-size="9" fill="var(--text-m)" font-family="inherit">${l.months[d.getMonth()]}</text>`;
        lastMonth = d.getMonth();
      }

      // cell color
      const dayData = dateMap[key];
      let fill = 'var(--border)';
      let opacity = 1;
      if (dayData) {
        const top = Object.entries(dayData).sort((a,b)=>b[1]-a[1])[0][0];
        fill = col(top);
        opacity = .85;
      }

      cells += `<rect x="${x}" y="${y}" width="${CW}" height="${CH}" rx="2"
        fill="${fill}" opacity="${opacity}" style="cursor:default">
        <title>${key}${dayData?' — '+Object.entries(dayData).sort((a,b)=>b[1]-a[1]).map(([k,n])=>`${fl(k)} ×${n}`).join(', '):''}</title>
      </rect>`;
    }
  }

  // day labels (Mon, Wed, Fri)
  const dayLabels = [0,2,4].map(i =>
    `<text x="${LEFT-5}" y="${TOP + i*(CH+GAP) + CH/2 + 3}" font-size="9" fill="var(--text-m)" text-anchor="end" font-family="inherit">${l.days[i]}</text>`
  ).join('');

  wrap.innerHTML = `<svg width="${svgW}" height="${svgH}" viewBox="0 0 ${svgW} ${svgH}">
    ${monthLabels}${dayLabels}${cells}
  </svg>`;
}

// ══ Concept cloud ════════════════════════════════════════════════
function renderConceptCloud() {
  const l       = L();
  const grid    = document.getElementById('concept-grid');
  const noEl    = document.getElementById('no-concepts');
  if (!grid) return;

  const cm = {};
  memories.forEach(m => {
    if (!cm[m.concept]) cm[m.concept] = { n:0, feelings:{} };
    cm[m.concept].n++;
    cm[m.concept].feelings[m.feeling] = (cm[m.concept].feelings[m.feeling]||0)+1;
  });
  const entries = Object.entries(cm).sort((a,b)=>b[1].n-a[1].n);

  if (!entries.length) {
    grid.innerHTML = `<div id="no-concepts" style="font-size:12px;color:var(--text-m);font-style:italic">${l.noAnalytics}</div>`;
    return;
  }

  const maxN = entries[0][1].n;
  grid.innerHTML = entries.map(([concept, data]) => {
    const dom = Object.entries(data.feelings).sort((a,b)=>b[1]-a[1])[0][0];
    const c   = col(dom);
    const sz  = 11 + Math.round((data.n/maxN) * 8);
    return `<div class="concept-bubble" style="background:${c}18;color:${c};font-size:${sz}px;border:1px solid ${c}30"
      title="${esc(concept)}: ${data.n} entries"
      onclick="selectArcConcept('${esc(concept).replace(/'/g,"\\'")}')">
      ${esc(concept)} <span style="font-size:${sz-2}px;opacity:.6">${data.n}</span>
    </div>`;
  }).join('');
}

// ══ Feeling bars ═════════════════════════════════════════════════
function renderFeelingBars() {
  const l       = L();
  const container = document.getElementById('feel-bars');
  if (!container) return;

  const freq = {};
  memories.forEach(m => freq[m.feeling] = (freq[m.feeling]||0)+1);
  const sorted = FEELING_KEYS.map(k=>({k,n:freq[k]||0})).filter(x=>x.n>0).sort((a,b)=>b.n-a.n);

  if (!sorted.length) {
    container.innerHTML = `<div style="font-size:12px;color:var(--text-m);font-style:italic">${l.noAnalytics}</div>`;
    return;
  }
  const maxN = sorted[0].n;
  container.innerHTML = sorted.map(({k,n}) => `
    <div class="feel-bar-row">
      <div class="feel-bar-label">${fl(k)}</div>
      <div class="feel-bar-track">
        <div class="feel-bar-fill" style="width:${Math.round(n/maxN*100)}%;background:${col(k)}"></div>
      </div>
      <div class="feel-bar-n">${n}</div>
    </div>`).join('');
}

// ══ Arc timeline ═════════════════════════════════════════════════
function rebuildArcSelect() {
  const sel = document.getElementById('arc-concept-sel');
  if (!sel) return;
  const l = L();
  const concepts = [...new Set(memories.map(m => m.concept))].sort();
  sel.innerHTML = `<option value="">${l.arcSelect}</option>` +
    concepts.map(c => `<option value="${esc(c)}"${c===selectedArcConcept?' selected':''}>${esc(c)}</option>`).join('');
}

function selectArcConcept(c) {
  selectedArcConcept = c;
  const sel = document.getElementById('arc-concept-sel');
  if (sel) sel.value = c;
  renderArc();
  // scroll to arc
  document.getElementById('arc-card')?.scrollIntoView({behavior:'smooth', block:'nearest'});
}

function renderArc() {
  const l       = L();
  const area    = document.getElementById('arc-timeline');
  const emptyEl = document.getElementById('arc-empty');
  if (!area) return;

  if (!selectedArcConcept) {
    area.style.display = 'none';
    if (emptyEl) { emptyEl.style.display='block'; emptyEl.textContent=l.arcEmpty; }
    return;
  }

  const mems = memories.filter(m => m.concept===selectedArcConcept).sort((a,b)=>a.ts-b.ts);
  if (mems.length < 1) {
    area.style.display = 'none';
    if (emptyEl) { emptyEl.style.display='block'; emptyEl.textContent=l.arcNoData; }
    return;
  }
  if (emptyEl) emptyEl.style.display = 'none';
  area.style.display = 'block';

  // SVG timeline: dots + connecting line
  const W  = Math.max(700, mems.length * 70);
  const H  = 100;
  const PL = 20, PR = 20, PT = 20, PB = 30;
  const iW = W - PL - PR;
  const iH = H - PT - PB;
  const CX = mems.length>1 ? i => PL + Math.round(i/(mems.length-1)*iW) : () => PL + iW/2;
  const CY = () => PT + iH/2;
  const R  = 7;

  let path = '';
  if (mems.length > 1) {
    path = `<polyline points="${mems.map((m,i)=>`${CX(i)},${CY()}`).join(' ')}"
      fill="none" stroke="var(--border)" stroke-width="1.5"/>`;
  }

  const dots = mems.map((m,i) => {
    const c  = col(m.feeling);
    const x  = CX(i);
    const y  = CY();
    const label = mems.length <= 12 ? `<text x="${x}" y="${H-5}" text-anchor="middle" font-size="9" fill="var(--text-m)" font-family="inherit">${m.date.slice(5)}</text>` : '';
    return `<circle cx="${x}" cy="${y}" r="${R}" fill="${c}" opacity=".85">
      <title>${fl(m.feeling)} · ${m.date}\n${m.content.slice(0,80)}</title>
    </circle>
    <text x="${x}" y="${y+16}" text-anchor="middle" font-size="8" fill="${c}" font-family="inherit">${fl(m.feeling).slice(0,4)}</text>
    ${label}`;
  }).join('');

  area.innerHTML = `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="display:block">
    ${path}${dots}
  </svg>`;
}

// ══ Brain ══════════════════════════════════════════════════════
function renderBrainEmpty() {
  const l  = L();
  const el = document.getElementById('brain-empty');
  if (el) el.textContent = l.brainEmpty;
  const btn = document.getElementById('btn-brain-clear');
  if (btn) btn.style.display = brainHistory.length ? 'inline' : 'none';
}

function renderBrainMessages() {
  const l    = L();
  const msgs = document.getElementById('brain-msgs');
  if (!msgs) return;
  if (!brainHistory.length) {
    msgs.innerHTML = `<div id="brain-empty" style="font-size:12px;color:var(--text-m);font-style:italic">${l.brainEmpty}</div>`;
    return;
  }
  msgs.innerHTML = brainHistory.map(m => {
    if (m.role==='user') return `
      <div>
        <div class="brain-msg-label">${l.youLabel}</div>
        <div class="brain-msg-user">${esc(m.content)}</div>
      </div>`;
    return `
      <div>
        <div class="brain-msg-label">${l.brainLabel}</div>
        <div class="brain-msg-ai">${esc(m.content)}</div>
      </div>`;
  }).join('');
  setTimeout(() => msgs.scrollTop = msgs.scrollHeight, 40);
}

function clearBrain() {
  brainHistory = [];
  renderBrainMessages();
  document.getElementById('btn-brain-clear').style.display = 'none';
}

async function askBrain() {
  if (brainLoading) return;
  const inp  = document.getElementById('brain-input');
  const text = inp.value.trim();
  if (!text) return;
  const l = L();

  inp.value = '';
  brainLoading = true;
  document.getElementById('btn-brain-ask').disabled = true;
  document.getElementById('btn-brain-clear').style.display = 'none';

  brainHistory.push({ role:'user', content:text });

  // show typing indicator
  const msgs = document.getElementById('brain-msgs');
  msgs.innerHTML = brainHistory.map(m => {
    if (m.role==='user') return `<div><div class="brain-msg-label">${l.youLabel}</div><div class="brain-msg-user">${esc(m.content)}</div></div>`;
    return `<div><div class="brain-msg-label">${l.brainLabel}</div><div class="brain-msg-ai">${esc(m.content)}</div></div>`;
  }).join('') + `<div>
    <div class="brain-msg-label">${l.brainLabel}</div>
    <div class="brain-msg-ai"><div class="brain-typing">
      <div class="brain-dot"></div><div class="brain-dot"></div><div class="brain-dot"></div>
    </div></div>
  </div>`;
  msgs.scrollTop = msgs.scrollHeight;

  // Build archive context (last 40 memories)
  const archiveBlock = memories.slice(0, 40).map(m =>
    `[${m.date}] CONCEPT: ${m.concept} | FEELING: ${fl(m.feeling)}\n"${m.content}"${m.note?'\n('+m.note+')':''}`
  ).join('\n\n') || '[No memories yet]';

  // Stats summary
  const totalMems  = memories.length;
  const concepts   = [...new Set(memories.map(m=>m.concept))];
  const freqFeel   = {};
  memories.forEach(m => freqFeel[m.feeling]=(freqFeel[m.feeling]||0)+1);
  const topFeeling = Object.entries(freqFeel).sort((a,b)=>b[1]-a[1])[0]?.[0];

  const sys = `You are the MEMORIA Brain — a psychological intelligence embedded in a personal emotional memory archive.
You have access to the user's MNHEME archive: append-only emotional memory records.

ARCHIVE SUMMARY:
- Total entries: ${totalMems}
- Concepts tracked: ${concepts.join(', ')||'none yet'}
- Most frequent feeling: ${topFeeling ? fl(topFeeling) : 'none yet'}

RECENT ENTRIES (up to 40):
${archiveBlock}

Answer questions about the user's emotional patterns, arcs, and psychology based ONLY on this archive.
Be insightful, warm, and honest. Keep responses to 3-5 sentences.
${l.sysLang}`;

  const lmUrl   = document.getElementById('lm-url').value.trim();
  const lmModel = document.getElementById('lm-model').value.trim();
  let reply = '';
  try {
    const res = await fetch(lmUrl, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        model: lmModel||'local-model', max_tokens:400, temperature:.7,
        messages:[
          {role:'system', content:sys},
          ...brainHistory.map(m=>({role:m.role, content:m.content}))
        ]
      })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status} — is LM Studio running?`);
    const data = await res.json();
    reply = data.choices?.[0]?.message?.content || '[Empty response]';
  } catch(e) {
    reply = `[Brain unreachable — ${e.message}]`;
  }

  brainHistory.push({role:'assistant', content:reply});
  brainLoading = false;
  document.getElementById('btn-brain-ask').disabled = false;
  document.getElementById('btn-brain-clear').style.display = 'inline';
  renderBrainMessages();
}

// ══ Mobile sidebar ══════════════════════════════════════════════
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('sidebar-backdrop').classList.toggle('open');
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebar-backdrop').classList.remove('open');
}

// ══ Boot ═══════════════════════════════════════════════════════
load();
setupForm();
renderStaticText();
render();