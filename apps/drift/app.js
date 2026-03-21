/* ═══════════════════════════════════════════════════════════
   DRIFT — app.js
   MNHEME Time Capsule · Emotional Archive
   i18n: EN / IT / ES / ZH · 20 themes
   ═══════════════════════════════════════════════════════════ */

// ══ i18n ════════════════════════════════════════════════════
const LANGS = {
  en: {
    code:'en', label:'EN', name:'English',
    wordmark: 'DRIFT',
    tagline:  'seal your feelings · unseal your past',
    formTitle:'Seal a capsule',
    fConcept: 'Concept',
    fFeeling: 'Feeling',
    fContent: 'What you feel now',
    fNote:    'Context',
    fNoteOpt: '(optional)',
    fSealDate:'Seal until',
    fSealDateHint:'Capsule opens on this date',
    sealBtn:  'Seal the capsule',
    listTitle:'Your capsules',
    listEmpty:'No capsules sealed yet.\nWrite what you feel and seal it in time.',
    themeLight:'— LIGHT —', themeDark:'— DARK —',
    lmSave:   'Save',
    lmModelPh:'model',
    conceptPh:'Work, Love, Fear…',
    contentPh:'Write honestly. No one will read this until the date you choose.',
    notePh:   'Where, with whom, what was happening…',
    statusSealed:'sealed',
    statusOpen:  'unsealed',
    opensIn:  'Opens in',
    openedOn: 'Opened',
    sealedOn: 'Sealed',
    dDays:'d', dHours:'h', dMinutes:'m', dSeconds:'s',
    daysFull: n => `${n} day${n===1?'':'s'}`,
    hoursFull:n => `${n} hour${n===1?'':'s'}`,
    minsFull: n => `${n} minute${n===1?'':'s'}`,
    secsFull: n => `${n} second${n===1?'':'s'}`,
    sealedHint:'This capsule opens on {date}.\nCome back then to read what you wrote.',
    pastLbl:  'What you felt — {date}',
    nowLbl:   'What you feel now',
    reentryPh:'Read what you wrote above.\nHow do you feel about it now?',
    reentryFeel:'Your feeling today',
    saveLbl:  'Save re-entry note',
    brainTitle:'Brain',
    brainEmpty:'Ask about the gap between past-you and present-you.',
    brainAsk: 'Ask',
    brainClear:'clear',
    brainLbl: 'BRAIN',
    youLbl:   'YOU',
    suggests: concept => [
      `What changed most in how I feel about "${concept}"?`,
      `What would past-me think of this re-entry note?`,
      `What does this capsule reveal about my emotional patterns?`,
    ],
    openedBadge:'UNSEALED',
    feelLabels:{
      gioia:'Joy',tristezza:'Sadness',rabbia:'Rage',paura:'Fear',
      nostalgia:'Nostalgia',amore:'Love',malinconia:'Melancholy',
      serenità:'Serenity',sorpresa:'Surprise',ansia:'Anxiety',
      gratitudine:'Gratitude',vergogna:'Shame',orgoglio:'Pride',
      noia:'Boredom',curiosità:'Curiosity',
    },
    sysLang:'Reply in English.',
    fmtDate: d => d.toLocaleDateString('en-GB',{day:'numeric',month:'long',year:'numeric'}),
    fmtShort:d => d.toLocaleDateString('en-GB',{day:'numeric',month:'short'}),
  },
  it:{
    code:'it', label:'IT', name:'Italiano',
    wordmark:'DRIFT',
    tagline:'sigilla i tuoi sentimenti · riapri il tuo passato',
    formTitle:'Sigilla una capsula',
    fConcept:'Concetto',
    fFeeling:'Sentimento',
    fContent:'Come ti senti ora',
    fNote:   'Contesto',
    fNoteOpt:'(opzionale)',
    fSealDate:'Sigilla fino al',
    fSealDateHint:'La capsula si apre in questa data',
    sealBtn: 'Sigilla la capsula',
    listTitle:'Le tue capsule',
    listEmpty:'Nessuna capsula sigillata.\nScrivi cosa senti e sigillaolo nel tempo.',
    themeLight:'— CHIARO —', themeDark:'— SCURO —',
    lmSave:  'Salva',
    lmModelPh:'modello',
    conceptPh:'Lavoro, Amore, Paura…',
    contentPh:'Scrivi onestamente. Nessuno leggerà questo fino alla data scelta.',
    notePh:  'Dove, con chi, cosa stava accadendo…',
    statusSealed:'sigillata',
    statusOpen:  'aperta',
    opensIn: 'Si apre tra',
    openedOn:'Aperta il',
    sealedOn:'Sigillata il',
    dDays:'g', dHours:'h', dMinutes:'m', dSeconds:'s',
    daysFull: n=>`${n} giorno${n===1?'':'i'}`,
    hoursFull:n=>`${n} ora${n===1?'':'e'}`,
    minsFull: n=>`${n} minuto${n===1?'':'i'}`,
    secsFull: n=>`${n} secondo${n===1?'':'i'}`,
    sealedHint:'Questa capsula si apre il {date}.\nTorna allora per leggere quello che hai scritto.',
    pastLbl: 'Cosa sentivi — {date}',
    nowLbl:  'Cosa senti ora',
    reentryPh:'Leggi quello che hai scritto sopra.\nCome ti senti adesso?',
    reentryFeel:'Il tuo sentimento oggi',
    saveLbl: 'Salva la nota di rientro',
    brainTitle:'Cervello',
    brainEmpty:'Chiedi del gap tra il te passato e quello presente.',
    brainAsk:'Chiedi',
    brainClear:'cancella',
    brainLbl:'CERVELLO',
    youLbl:  'TU',
    suggests:concept=>[
      `Cos\'è cambiato di più nel modo in cui mi sento riguardo a "${concept}"?`,
      `Cosa penserebbe il me passato di questa nota di rientro?`,
      `Cosa rivela questa capsula sui miei pattern emotivi?`,
    ],
    openedBadge:'APERTA',
    feelLabels:{
      gioia:'Gioia',tristezza:'Tristezza',rabbia:'Rabbia',paura:'Paura',
      nostalgia:'Nostalgia',amore:'Amore',malinconia:'Malinconia',
      serenità:'Serenità',sorpresa:'Sorpresa',ansia:'Ansia',
      gratitudine:'Gratitudine',vergogna:'Vergogna',orgoglio:'Orgoglio',
      noia:'Noia',curiosità:'Curiosità',
    },
    sysLang:'Rispondi in italiano.',
    fmtDate: d=>d.toLocaleDateString('it-IT',{day:'numeric',month:'long',year:'numeric'}),
    fmtShort:d=>d.toLocaleDateString('it-IT',{day:'numeric',month:'short'}),
  },
  es:{
    code:'es', label:'ES', name:'Español',
    wordmark:'DRIFT',
    tagline:'sella tus sentimientos · reabre tu pasado',
    formTitle:'Sellar una cápsula',
    fConcept:'Concepto',
    fFeeling:'Sentimiento',
    fContent:'Cómo te sientes ahora',
    fNote:   'Contexto',
    fNoteOpt:'(opcional)',
    fSealDate:'Sellar hasta',
    fSealDateHint:'La cápsula se abre en esta fecha',
    sealBtn: 'Sellar la cápsula',
    listTitle:'Tus cápsulas',
    listEmpty:'Sin cápsulas selladas.\nEscribe lo que sientes y séllalo en el tiempo.',
    themeLight:'— CLARO —', themeDark:'— OSCURO —',
    lmSave:  'Guardar',
    lmModelPh:'modelo',
    conceptPh:'Trabajo, Amor, Miedo…',
    contentPh:'Escribe honestamente. Nadie leerá esto hasta la fecha que elijas.',
    notePh:  'Dónde, con quién, qué estaba pasando…',
    statusSealed:'sellada',
    statusOpen:  'abierta',
    opensIn: 'Se abre en',
    openedOn:'Abierta el',
    sealedOn:'Sellada el',
    dDays:'d', dHours:'h', dMinutes:'m', dSeconds:'s',
    daysFull: n=>`${n} día${n===1?'':'s'}`,
    hoursFull:n=>`${n} hora${n===1?'':'s'}`,
    minsFull: n=>`${n} minuto${n===1?'':'s'}`,
    secsFull: n=>`${n} segundo${n===1?'':'s'}`,
    sealedHint:'Esta cápsula se abre el {date}.\nVuelve entonces para leer lo que escribiste.',
    pastLbl: 'Lo que sentías — {date}',
    nowLbl:  'Lo que sientes ahora',
    reentryPh:'Lee lo que escribiste arriba.\n¿Cómo te sientes ahora?',
    reentryFeel:'Tu sentimiento hoy',
    saveLbl: 'Guardar nota de reentrada',
    brainTitle:'Mente',
    brainEmpty:'Pregunta sobre la diferencia entre tú del pasado y tú del presente.',
    brainAsk:'Preguntar',
    brainClear:'limpiar',
    brainLbl:'MENTE',
    youLbl:  'TÚ',
    suggests:concept=>[
      `¿Qué cambió más en cómo me siento respecto a "${concept}"?`,
      `¿Qué pensaría el yo del pasado de esta nota de reentrada?`,
      `¿Qué revela esta cápsula sobre mis patrones emocionales?`,
    ],
    openedBadge:'ABIERTA',
    feelLabels:{
      gioia:'Alegría',tristezza:'Tristeza',rabbia:'Rabia',paura:'Miedo',
      nostalgia:'Nostalgia',amore:'Amor',malinconia:'Melancolía',
      serenità:'Serenidad',sorpresa:'Sorpresa',ansia:'Ansiedad',
      gratitudine:'Gratitud',vergogna:'Vergüenza',orgoglio:'Orgullo',
      noia:'Aburrimiento',curiosità:'Curiosidad',
    },
    sysLang:'Responde en español.',
    fmtDate: d=>d.toLocaleDateString('es-ES',{day:'numeric',month:'long',year:'numeric'}),
    fmtShort:d=>d.toLocaleDateString('es-ES',{day:'numeric',month:'short'}),
  },
  zh:{
    code:'zh', label:'中', name:'中文',
    wordmark:'DRIFT',
    tagline:'封存你的感受 · 解封你的过去',
    formTitle:'封存一颗时间胶囊',
    fConcept:'概念',
    fFeeling:'情感',
    fContent:'你现在的感受',
    fNote:   '背景',
    fNoteOpt:'（可选）',
    fSealDate:'封存至',
    fSealDateHint:'胶囊将在此日期开启',
    sealBtn: '封存胶囊',
    listTitle:'你的胶囊',
    listEmpty:'还没有封存的胶囊。\n写下你的感受，将它封存在时间里。',
    themeLight:'— 浅色 —', themeDark:'— 深色 —',
    lmSave:  '保存',
    lmModelPh:'模型',
    conceptPh:'工作、爱、恐惧……',
    contentPh:'诚实地写。直到你选择的日期，没有人会看到这些。',
    notePh:  '在哪里，和谁在一起，发生了什么……',
    statusSealed:'已封存',
    statusOpen:  '已开启',
    opensIn: '将在…后开启',
    openedOn:'开启于',
    sealedOn:'封存于',
    dDays:'天', dHours:'时', dMinutes:'分', dSeconds:'秒',
    daysFull: n=>`${n}天`,
    hoursFull:n=>`${n}小时`,
    minsFull: n=>`${n}分钟`,
    secsFull: n=>`${n}秒`,
    sealedHint:'这颗胶囊将于 {date} 开启。\n到时候回来阅读你写下的内容。',
    pastLbl: '你当时的感受 — {date}',
    nowLbl:  '你现在的感受',
    reentryPh:'读一读你上面写的内容。\n你现在有什么感受？',
    reentryFeel:'你今天的情感',
    saveLbl: '保存重返记录',
    brainTitle:'大脑',
    brainEmpty:'询问过去的你和现在的你之间的差距。',
    brainAsk:'提问',
    brainClear:'清除',
    brainLbl:'大脑',
    youLbl:  '你',
    suggests:concept=>[
      `关于"${concept}"，我的感受最大的变化是什么？`,
      `过去的我会怎么看这条重返记录？`,
      `这颗胶囊揭示了我的情感模式的什么？`,
    ],
    openedBadge:'已解封',
    feelLabels:{
      gioia:'喜悦',tristezza:'悲伤',rabbia:'愤怒',paura:'恐惧',
      nostalgia:'怀旧',amore:'爱',malinconia:'忧郁',
      serenità:'宁静',sorpresa:'惊讶',ansia:'焦虑',
      gratitudine:'感恩',vergogna:'羞耻',orgoglio:'自豪',
      noia:'无聊',curiosità:'好奇',
    },
    sysLang:'请用中文回复。',
    fmtDate: d=>d.toLocaleDateString('zh-CN',{year:'numeric',month:'long',day:'numeric'}),
    fmtShort:d=>d.toLocaleDateString('zh-CN',{month:'short',day:'numeric'}),
  },
};
const LANG_ORDER = ['en','it','es','zh'];

// ══ Feelings & Themes ════════════════════════════════════════
const FEELING_KEYS = ['gioia','tristezza','rabbia','paura','nostalgia','amore','malinconia','serenità','sorpresa','ansia','gratitudine','vergogna','orgoglio','noia','curiosità'];
const FEELING_COLORS = {gioia:'#f59e0b',tristezza:'#6ea8fe',rabbia:'#f87171',paura:'#a78bfa',nostalgia:'#fb923c',amore:'#f472b6',malinconia:'#818cf8',serenità:'#34d399',sorpresa:'#fcd34d',ansia:'#94a3b8',gratitudine:'#6ee7b7',vergogna:'#fca5a5',orgoglio:'#c084fc',noia:'#6b7280',curiosità:'#67e8f9'};

const THEMES = [
  {id:'parchment',label:'Parchment',bg:'#f7f4ee',acc:'#7a5230',dark:false},
  {id:'linen',    label:'Linen',    bg:'#fafaf5',acc:'#6a5a30',dark:false},
  {id:'cloud',    label:'Cloud',    bg:'#f0f4f8',acc:'#2a68a8',dark:false},
  {id:'sage',     label:'Sage',     bg:'#eef2ee',acc:'#2a7a3a',dark:false},
  {id:'blush',    label:'Blush',    bg:'#fdf2f4',acc:'#a82850',dark:false},
  {id:'sand',     label:'Sand',     bg:'#f8f4ec',acc:'#c87830',dark:false},
  {id:'stone',    label:'Stone',    bg:'#f2f0ec',acc:'#4a4840',dark:false},
  {id:'lilac',    label:'Lilac',    bg:'#f6f4fc',acc:'#6848c8',dark:false},
  {id:'dawn',     label:'Dawn',     bg:'#fdf6f0',acc:'#c85c28',dark:false},
  {id:'chalk',    label:'Chalk',    bg:'#f8f8f4',acc:'#303090',dark:false},
  {id:'obsidian', label:'Obsidian', bg:'#0e0f10',acc:'#c8a870',dark:true},
  {id:'midnight', label:'Midnight', bg:'#080c18',acc:'#6898f8',dark:true},
  {id:'ember',    label:'Ember',    bg:'#100c08',acc:'#e08038',dark:true},
  {id:'void',     label:'Void',     bg:'#000000',acc:'#b8b8b8',dark:true},
  {id:'forest',   label:'Forest',   bg:'#060e08',acc:'#58d878',dark:true},
  {id:'crimson',  label:'Crimson',  bg:'#100608',acc:'#e05868',dark:true},
  {id:'amethyst', label:'Amethyst', bg:'#080610',acc:'#c080f8',dark:true},
  {id:'graphite', label:'Graphite', bg:'#101214',acc:'#90b8d8',dark:true},
  {id:'candle',   label:'Candle',   bg:'#100c06',acc:'#f8d848',dark:true},
  {id:'ocean',    label:'Ocean',    bg:'#040c10',acc:'#40c8e0',dark:true},
];

// ══ State ══════════════════════════════════════════════════════
const SK        = 'drift-v1';
let capsules    = [];
let currentLang = 'en';
let currentTheme= 'parchment';
let selectedId  = null;
let themePanelOpen = false;
let langPanelOpen  = false;
let brainHistory   = [];
let brainLoading   = false;
let countdownTimer = null;

// ══ Utils ══════════════════════════════════════════════════════
const uid  = () => Math.random().toString(36).slice(2,10);
const esc  = s => String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const L    = () => LANGS[currentLang] || LANGS.en;
const fl   = k => L().feelLabels[k] || k;
const col  = k => FEELING_COLORS[k] || '#888';
const isOpen = c => Date.now() >= c.sealUntil;

// ══ Persistence ════════════════════════════════════════════════
function load() {
  try { const r = localStorage.getItem(SK); if (r) capsules = JSON.parse(r); } catch(e) {}
  const t = localStorage.getItem('drift-theme');
  const g = localStorage.getItem('drift-lang');
  const u = localStorage.getItem('drift-lm-url');
  const m = localStorage.getItem('drift-lm-model');
  if (t && THEMES.find(x=>x.id===t)) currentTheme = t;
  if (g && LANGS[g]) currentLang = g;
  if (u) document.getElementById('lm-url').value = u;
  if (m) document.getElementById('lm-model').value = m;
  applyTheme(currentTheme, false);
  applyLang(currentLang, false);
}

function save() { try { localStorage.setItem(SK, JSON.stringify(capsules)); } catch(e) {} }

function saveLm() {
  localStorage.setItem('drift-lm-url',   document.getElementById('lm-url').value.trim());
  localStorage.setItem('drift-lm-model', document.getElementById('lm-model').value.trim());
  const el = document.getElementById('lm-ok');
  el.style.display = 'inline';
  setTimeout(() => el.style.display = 'none', 2000);
}

// ══ Theme ══════════════════════════════════════════════════════
function applyTheme(id, persist=true) {
  currentTheme = id;
  document.documentElement.setAttribute('data-theme', id);
  if (persist) localStorage.setItem('drift-theme', id);
  document.querySelectorAll('.th-dot').forEach(d => d.classList.toggle('active', d.dataset.theme===id));
  const th = THEMES.find(t => t.id===id);
  const btn = document.getElementById('btn-theme');
  if (btn && th)
    btn.innerHTML = `<span style="display:inline-block;width:11px;height:11px;background:${th.acc};border-radius:3px;flex-shrink:0"></span>${th.label}`;
}

function buildThemePanel() {
  const l = L();
  const sw = g => g.map(t =>
    `<div class="th-dot${t.id===currentTheme?' active':''}" data-theme="${t.id}" title="${t.label}"
      style="background:${t.bg};outline:2px solid ${t.acc}44"
      onclick="applyTheme('${t.id}')"></div>`).join('');
  return `<div class="p-lbl">${l.themeLight}</div><div class="swatch-row">${sw(THEMES.filter(t=>!t.dark))}</div>
    <div class="p-lbl">${l.themeDark}</div><div class="swatch-row">${sw(THEMES.filter(t=>t.dark))}</div>`;
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
  if (persist) localStorage.setItem('drift-lang', code);
  document.querySelectorAll('.lang-opt').forEach(b => b.classList.toggle('active', b.dataset.lang===code));
  renderStaticText();
  renderList();
  if (selectedId) renderDetail(selectedId);
}

function buildLangPanel() {
  return LANG_ORDER.map(code => {
    const lg = LANGS[code];
    return `<button class="lang-opt${code===currentLang?' active':''}" data-lang="${code}"
      onclick="applyLang('${code}');toggleLangPanel()">${lg.label}<span class="ln">${lg.name}</span></button>`;
  }).join('');
}

function toggleLangPanel() {
  langPanelOpen = !langPanelOpen;
  if (themePanelOpen) { themePanelOpen=false; document.getElementById('theme-panel')?.classList.remove('open'); }
  const p = document.getElementById('lang-panel');
  if (p) { p.innerHTML = langPanelOpen ? buildLangPanel() : ''; p.classList.toggle('open', langPanelOpen); }
}

document.addEventListener('click', e => {
  const tw = document.getElementById('theme-wrap');
  const lw = document.getElementById('lang-wrap');
  if (themePanelOpen && tw && !tw.contains(e.target)) { themePanelOpen=false; document.getElementById('theme-panel')?.classList.remove('open'); }
  if (langPanelOpen  && lw && !lw.contains(e.target)) { langPanelOpen=false;  document.getElementById('lang-panel')?.classList.remove('open'); }
});

// ══ Static text ════════════════════════════════════════════════
function renderStaticText() {
  const l = L();
  const s = (id,t)=>{const e=document.getElementById(id);if(e)e.textContent=t};
  const p = (id,t)=>{const e=document.getElementById(id);if(e)e.placeholder=t};

  s('wordmark',    l.wordmark);
  s('tagline',     l.tagline);
  s('form-title',  l.formTitle);
  s('lbl-concept', l.fConcept);
  s('lbl-feeling', l.fFeeling);
  s('lbl-content', l.fContent);
  s('lbl-note',    `${l.fNote} ${l.fNoteOpt}`);
  s('lbl-sealdate',l.fSealDate);
  s('seal-date-hint', l.fSealDateHint);
  s('btn-seal',    l.sealBtn);
  s('list-title',  l.listTitle);
  s('btn-lm-save', l.lmSave);
  p('lm-model',    l.lmModelPh);
  p('f-concept',   l.conceptPh);
  p('f-content',   l.contentPh);
  p('f-note',      l.notePh);

  // feeling options
  const fs = document.getElementById('f-feeling');
  if (fs) {
    const cur = fs.value;
    fs.innerHTML = FEELING_KEYS.map(k=>`<option value="${k}">${fl(k)}</option>`).join('');
    fs.value = cur || 'gioia';
    fs.style.color = col(fs.value);
  }

  // lang btn
  const lb = document.getElementById('btn-lang');
  if (lb) lb.textContent = l.label;

  // theme btn
  const th = THEMES.find(t=>t.id===currentTheme);
  const tb = document.getElementById('btn-theme');
  if (tb && th)
    tb.innerHTML = `<span style="display:inline-block;width:11px;height:11px;background:${th.acc};border-radius:3px;flex-shrink:0"></span>${th.label}`;
}

// ══ Seal form ══════════════════════════════════════════════════
function setupForm() {
  const fc = document.getElementById('f-concept');
  const ft = document.getElementById('f-content');
  const fd = document.getElementById('f-sealdate');
  const btn = document.getElementById('btn-seal');
  const fs = document.getElementById('f-feeling');

  fs.onchange = () => fs.style.color = col(fs.value);
  fs.style.color = col(fs.value || 'gioia');

  const check = () => { btn.disabled = !fc.value.trim() || !ft.value.trim() || !fd.value; };
  fc.oninput = ft.oninput = fd.oninput = check;
  btn.disabled = true;

  // default seal date: 30 days from today
  const def = new Date(); def.setDate(def.getDate() + 30);
  fd.value = def.toISOString().slice(0,10);
}

function sealCapsule() {
  const l = L();
  const concept = document.getElementById('f-concept').value.trim();
  const feeling = document.getElementById('f-feeling').value;
  const content = document.getElementById('f-content').value.trim();
  const note    = document.getElementById('f-note').value.trim();
  const dateval = document.getElementById('f-sealdate').value;
  if (!concept || !content || !dateval) return;

  const sealUntil = new Date(dateval + 'T23:59:59').getTime();

  const cap = {
    id: uid(),
    concept, feeling, content, note,
    sealedAt: Date.now(),
    sealUntil,
    reentry: null, // { feeling, content, at }
    brainHistory: [],
  };
  capsules.unshift(cap);
  save();

  // reset form
  document.getElementById('f-concept').value = '';
  document.getElementById('f-content').value = '';
  document.getElementById('f-note').value    = '';
  document.getElementById('btn-seal').disabled = true;

  renderList();
  selectCapsule(cap.id);
}

// ══ Capsule list ═══════════════════════════════════════════════
function renderList() {
  const l    = L();
  const list = document.getElementById('capsule-list');
  const cnt  = document.getElementById('list-counts');
  if (cnt) cnt.textContent = capsules.length ? `(${capsules.length})` : '';

  if (!capsules.length) {
    list.innerHTML = `<div id="list-empty">${esc(l.listEmpty).replace('\n','<br>')}</div>`;
    return;
  }

  list.innerHTML = capsules.map(c => {
    const open = isOpen(c);
    const statusColor = open ? col('serenità') : col('ansia');
    const statusLabel = open ? l.statusOpen : l.statusSealed;
    const dateLabel   = open
      ? `${l.openedOn} ${l.fmtShort(new Date(c.sealUntil))}`
      : `${l.opensIn} ${l.fmtShort(new Date(c.sealUntil))}`;
    const isSel = c.id === selectedId;
    const feelC = col(c.feeling);

    return `<div class="mini-capsule${isSel?' selected':''} fade-in" onclick="selectCapsule('${c.id}')">
      <div class="mini-cap-top">
        <span class="mini-cap-concept">${esc(c.concept)}</span>
        <span class="mini-cap-pill" style="background:${feelC}18;color:${feelC}">${fl(c.feeling)}</span>
        <span class="mini-cap-date">${l.fmtShort(new Date(c.sealedAt))}</span>
      </div>
      <div class="mini-cap-status">
        <span class="status-dot" style="background:${statusColor}"></span>
        <span style="color:${statusColor}">${statusLabel}</span>
        <span style="margin-left:4px">${dateLabel}</span>
      </div>
    </div>`;
  }).join('');
}

// ══ Select & render detail ════════════════════════════════════
function selectCapsule(id) {
  selectedId = id;
  brainHistory = [];
  brainLoading = false;
  if (countdownTimer) clearInterval(countdownTimer);

  // update list selection
  document.querySelectorAll('.mini-capsule').forEach(el => {
    el.classList.toggle('selected', el.onclick?.toString().includes(id));
  });
  renderList(); // re-render to update selection
  renderDetail(id);

  // close sidebar on mobile
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sb-backdrop').classList.remove('open');
}

function renderDetail(id) {
  const cap = capsules.find(c => c.id === id);
  if (!cap) return;
  const l = L();

  document.getElementById('main-empty').style.display   = 'none';
  document.getElementById('capsule-detail').style.display = 'block';

  if (!isOpen(cap)) {
    renderSealed(cap);
  } else {
    renderOpen(cap);
  }
}

// ══ Sealed view ════════════════════════════════════════════════
function renderSealed(cap) {
  const l = L();
  document.getElementById('sealed-view').style.display  = 'block';
  document.getElementById('open-view').style.display    = 'none';

  const feelC = col(cap.feeling);
  const openDate = new Date(cap.sealUntil);
  const hint = l.sealedHint.replace('{date}', l.fmtDate(openDate));

  document.getElementById('sealed-view').innerHTML = `
    <div class="sealed-card fade-in">
      <div class="sealed-icon">🔒</div>
      <div class="sealed-concept">${esc(cap.concept)}</div>
      <span class="sealed-pill" style="background:${feelC}18;color:${feelC};border:1px solid ${feelC}44">${fl(cap.feeling)}</span>
      <div class="sealed-meta">
        ${l.sealedOn} ${l.fmtDate(new Date(cap.sealedAt))}
      </div>
      <div class="countdown-box">
        <div class="countdown-label" id="cd-label">${l.opensIn}</div>
        <div class="countdown-units" id="cd-units">
          <div class="countdown-unit"><div class="countdown-n" id="cd-d">--</div><div class="countdown-u">${l.dDays}</div></div>
          <div class="countdown-unit"><div class="countdown-n" id="cd-h">--</div><div class="countdown-u">${l.dHours}</div></div>
          <div class="countdown-unit"><div class="countdown-n" id="cd-m">--</div><div class="countdown-u">${l.dMinutes}</div></div>
          <div class="countdown-unit"><div class="countdown-n" id="cd-s">--</div><div class="countdown-u">${l.dSeconds}</div></div>
        </div>
      </div>
      <div class="sealed-hint">${esc(hint).replace('\n','<br>')}</div>
    </div>`;

  startCountdown(cap);
}

function startCountdown(cap) {
  if (countdownTimer) clearInterval(countdownTimer);
  function tick() {
    const diff = cap.sealUntil - Date.now();
    if (diff <= 0) {
      clearInterval(countdownTimer);
      renderDetail(cap.id); // switch to open view
      return;
    }
    const dd = Math.floor(diff / 86400000);
    const hh = Math.floor((diff % 86400000) / 3600000);
    const mm = Math.floor((diff % 3600000) / 60000);
    const ss = Math.floor((diff % 60000) / 1000);
    const set = (id, v) => { const e=document.getElementById(id); if(e) e.textContent=String(v).padStart(2,'0'); };
    set('cd-d',dd); set('cd-h',hh); set('cd-m',mm); set('cd-s',ss);
  }
  tick();
  countdownTimer = setInterval(tick, 1000);
}

// ══ Open view ══════════════════════════════════════════════════
function renderOpen(cap) {
  const l = L();
  document.getElementById('sealed-view').style.display = 'none';
  const ov = document.getElementById('open-view');
  ov.style.display = 'block';

  const feelC    = col(cap.feeling);
  const pastDate = l.fmtDate(new Date(cap.sealedAt));
  const pastLbl  = l.pastLbl.replace('{date}', pastDate);

  // Reentry section
  let reentryHTML = '';
  if (cap.reentry) {
    const rc = col(cap.reentry.feeling);
    reentryHTML = `
      <div class="reentry-block">
        <div class="block-label" id="lbl-now">${l.nowLbl}</div>
        <div class="reentry-existing">${esc(cap.reentry.content)}</div>
        <div class="reentry-feeling-note" style="color:${rc}">${fl(cap.reentry.feeling)} · ${l.fmtDate(new Date(cap.reentry.at))}</div>
      </div>`;
  } else {
    const feelOpts = FEELING_KEYS.map(k=>`<option value="${k}">${fl(k)}</option>`).join('');
    reentryHTML = `
      <div class="reentry-block">
        <div class="block-label" id="lbl-now">${l.nowLbl}</div>
        <div class="reentry-form">
          <div>
            <div class="reentry-label">${l.reentryFeel}</div>
            <select id="reentry-feel" class="reentry-sel" onchange="this.style.color=feelCol(this.value)">${feelOpts}</select>
          </div>
          <textarea id="reentry-text" class="reentry-ta" rows="4"
            placeholder="${l.reentryPh.replace('\n','&#10;')}"></textarea>
          <button id="btn-save-reentry" onclick="saveReentry('${cap.id}')">${l.saveLbl}</button>
        </div>
      </div>`;
  }

  // Brain suggests
  const suggests = l.suggests(cap.concept);

  ov.innerHTML = `
    <div class="open-card unseal-anim">
      <div class="open-header">
        <div class="open-concept">${esc(cap.concept)}</div>
        <span class="open-pill" style="background:${feelC}18;color:${feelC};border:1px solid ${feelC}44">${fl(cap.feeling)}</span>
        <span class="open-badge">${l.openedBadge}</span>
        <span class="open-meta">${l.sealedOn} ${l.fmtDate(new Date(cap.sealedAt))}</span>
      </div>

      <div class="memory-block">
        <div class="block-label">${pastLbl}</div>
        <div class="memory-text">${esc(cap.content)}</div>
        ${cap.note ? `<div class="memory-note">${esc(cap.note)}</div>` : ''}
      </div>

      ${reentryHTML}

      <div class="brain-section">
        <div class="brain-title">
          <span id="brain-title-lbl">${l.brainTitle}</span>
          <button id="btn-brain-clear" onclick="clearBrain('${cap.id}')" style="display:${cap.brainHistory?.length?'inline':'none'}">${l.brainClear}</button>
        </div>
        <div class="brain-suggest-row">
          ${suggests.map(s=>`<button class="brain-suggest" onclick="fillBrain(this)">${esc(s)}</button>`).join('')}
        </div>
        <div id="brain-msgs">
          ${!cap.brainHistory?.length
            ? `<div class="brain-empty">${l.brainEmpty}</div>`
            : cap.brainHistory.map(m=>brainMsgHTML(m)).join('')}
        </div>
        <div id="brain-input-row">
          <input id="brain-input" type="text" placeholder="${l.brainAsk}…"
            onkeydown="if(event.key==='Enter')askBrain('${cap.id}')">
          <button id="btn-brain-ask" onclick="askBrain('${cap.id}')">${l.brainAsk}</button>
        </div>
      </div>
    </div>`;

  // init reentry feel color
  const rf = document.getElementById('reentry-feel');
  if (rf) { rf.value = cap.feeling; rf.style.color = col(rf.value); }

  // scroll brain to bottom
  setTimeout(() => {
    const msgs = document.getElementById('brain-msgs');
    if (msgs) msgs.scrollTop = msgs.scrollHeight;
  }, 40);
}

function feelCol(k) { return col(k); }

function saveReentry(id) {
  const cap = capsules.find(c=>c.id===id);
  if (!cap) return;
  const feel = document.getElementById('reentry-feel')?.value;
  const text = document.getElementById('reentry-text')?.value.trim();
  if (!text) return;
  cap.reentry = { feeling: feel, content: text, at: Date.now() };
  save();
  renderOpen(cap);
}

// ══ Brain ══════════════════════════════════════════════════════
function brainMsgHTML(m) {
  const l = L();
  if (m.role==='user') return `<div><div class="bmsg-lbl">${l.youLbl}</div><div class="bmsg-user">${esc(m.content)}</div></div>`;
  return `<div><div class="bmsg-lbl">${l.brainLbl}</div><div class="bmsg-ai">${esc(m.content)}</div></div>`;
}

function fillBrain(btn) {
  const inp = document.getElementById('brain-input');
  if (inp) { inp.value = btn.textContent; inp.focus(); }
}

function clearBrain(id) {
  const cap = capsules.find(c=>c.id===id);
  if (!cap) return;
  cap.brainHistory = [];
  save();
  renderOpen(cap);
}

async function askBrain(id) {
  if (brainLoading) return;
  const cap = capsules.find(c=>c.id===id);
  if (!cap) return;
  const inp = document.getElementById('brain-input');
  const text = inp?.value.trim();
  if (!text) return;
  const l = L();

  inp.value = '';
  brainLoading = true;
  document.getElementById('btn-brain-ask').disabled = true;

  if (!cap.brainHistory) cap.brainHistory = [];
  cap.brainHistory.push({ role:'user', content:text });

  // typing indicator
  const msgs = document.getElementById('brain-msgs');
  if (msgs) {
    msgs.innerHTML = cap.brainHistory.map(m=>brainMsgHTML(m)).join('') +
      `<div><div class="bmsg-lbl">${l.brainLbl}</div>
      <div class="bmsg-ai"><div class="typing-dots"><div class="td"></div><div class="td"></div><div class="td"></div></div></div></div>`;
    msgs.scrollTop = msgs.scrollHeight;
  }
  document.getElementById('btn-brain-clear').style.display = 'inline';

  const pastDate = l.fmtDate(new Date(cap.sealedAt));
  const nowDate  = l.fmtDate(new Date());

  const sys = `You are a psychological Brain analyzing the gap between a person's past and present emotional self.

PAST MEMORY (sealed on ${pastDate}):
CONCEPT: ${cap.concept}
FEELING then: ${fl(cap.feeling)}
"${cap.content}"
${cap.note ? `Context: ${cap.note}` : ''}

${cap.reentry
  ? `RE-ENTRY NOTE (written today, ${nowDate}):
FEELING now: ${fl(cap.reentry.feeling)}
"${cap.reentry.content}"`
  : `(No re-entry note written yet)`}

Analyze the emotional arc between past and present. Be insightful, compassionate, and honest.
Keep responses to 3-5 sentences. Do not repeat the memory verbatim.
${l.sysLang}`;

  const lmUrl   = document.getElementById('lm-url').value.trim();
  const lmModel = document.getElementById('lm-model').value.trim();
  let reply = '';
  try {
    const res = await fetch(lmUrl, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        model: lmModel||'local-model', max_tokens:400, temperature:.75,
        messages:[
          {role:'system', content:sys},
          ...cap.brainHistory.map(m=>({role:m.role,content:m.content}))
        ]
      })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status} — is LM Studio running?`);
    const data = await res.json();
    reply = data.choices?.[0]?.message?.content || '[Empty response]';
  } catch(e) {
    reply = `[Brain unreachable — ${e.message}]`;
  }

  cap.brainHistory.push({role:'assistant', content:reply});
  save();
  brainLoading = false;

  document.getElementById('btn-brain-ask').disabled = false;
  if (msgs) {
    msgs.innerHTML = cap.brainHistory.map(m=>brainMsgHTML(m)).join('');
    msgs.scrollTop = msgs.scrollHeight;
  }
  document.getElementById('brain-input')?.focus();
}

// ══ Mobile ═════════════════════════════════════════════════════
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('sb-backdrop').classList.toggle('open');
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sb-backdrop').classList.remove('open');
}

// ══ Boot ═══════════════════════════════════════════════════════
load();
setupForm();
renderStaticText();
renderList();

// Show first open capsule if any, else first capsule
if (capsules.length) {
  const first = capsules.find(c=>isOpen(c)) || capsules[0];
  selectCapsule(first.id);
}
