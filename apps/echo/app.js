/* ═══════════════════════════════════════════════════════════
   ECHO — app.js
   MNHEME Narrative Content Generator
   i18n: EN / IT / ES / ZH · 20 themes
   ═══════════════════════════════════════════════════════════ */

// ══ i18n ════════════════════════════════════════════════════
const LANGS = {
  en: {
    code:'en', label:'EN', name:'English',
    wordmark:       'ECHO',
    tagline:        'emotional narrative generator',
    archiveTitle:   'Emotional archive',
    addCard:        '+ Add memory',
    presetsLabel:   'Sample archives',
    presets:        ['Hamlet','Havisham','Frankenstein'],
    fmtLabel:       'Format',
    toneLabel:      'Tone',
    lengthLabel:    'Length',
    lenShort:       'Short',
    lenMedium:      'Medium',
    lenLong:        'Long',
    generateBtn:    'Generate',
    generating:     'Writing from the archive\u2026',
    placeholderIcon:'',
    placeholderText:'Add emotional memories to the archive,\nchoose a format and tone,\nthen hit Generate.',
    copyBtn:        'Copy',
    regenBtn:       'Regenerate',
    copiedMsg:      'Copied!',
    metaLabel:      (fmt, tone, n) => `${fmt} · ${tone} · ${n} memories`,
    formats: {
      letter:     'Letter',
      journal:    'Journal entry',
      monologue:  'Monologue',
      scene:      'Fiction scene',
      therapy:    'Therapy transcript',
      poem:       'Poem',
    },
    tones: {
      raw:      'Raw',
      polished: 'Polished',
      fragmented:'Fragmented',
      distant:  'Distant',
    },
    conceptPh:  'Concept',
    contentPh:  'What was felt\u2026',
    feelLabels: {
      gioia:'Joy', tristezza:'Sadness', rabbia:'Rage', paura:'Fear',
      nostalgia:'Nostalgia', amore:'Love', malinconia:'Melancholy',
      serenità:'Serenity', sorpresa:'Surprise', ansia:'Anxiety',
      gratitudine:'Gratitude', vergogna:'Shame', orgoglio:'Pride',
      noia:'Boredom', curiosità:'Curiosity',
    },
    themeLight: '— LIGHT —',
    themeDark:  '— DARK —',
    lmSave:     'Save',
    lmModelPh:  'model',
    promptFmts: {
      letter:    'Write a letter',
      journal:   'Write a journal entry',
      monologue: 'Write an interior monologue',
      scene:     'Write a short fiction scene',
      therapy:   'Write a therapy session transcript (patient speaking)',
      poem:      'Write a poem',
    },
    promptTones:{
      raw:       'in a raw, unpolished, confessional style',
      polished:  'in a literary, polished style with careful sentence craft',
      fragmented:'in a fragmented, non-linear style — broken sentences, white space, discontinuity',
      distant:   'in a detached, third-person-observational style, as if watching from outside',
    },
    promptLen:  { short:'Keep it short (100–150 words).', medium:'Aim for medium length (250–350 words).', long:'Write a longer piece (500–700 words).' },
    sysLang:    'Write in English.',
  },

  it: {
    code:'it', label:'IT', name:'Italiano',
    wordmark:       'ECHO',
    tagline:        'generatore narrativo emotivo',
    archiveTitle:   'Archivio emotivo',
    addCard:        '+ Aggiungi ricordo',
    presetsLabel:   'Archivi esempio',
    presets:        ['Hamlet','Havisham','Frankenstein'],
    fmtLabel:       'Formato',
    toneLabel:      'Tono',
    lengthLabel:    'Lunghezza',
    lenShort:       'Breve',
    lenMedium:      'Medio',
    lenLong:        'Lungo',
    generateBtn:    'Genera',
    generating:     'Scrittura dall\'archivio\u2026',
    placeholderIcon:'',
    placeholderText:'Aggiungi ricordi emotivi all\'archivio,\nscegli formato e tono,\npoi clicca Genera.',
    copyBtn:        'Copia',
    regenBtn:       'Rigenera',
    copiedMsg:      'Copiato!',
    metaLabel:      (fmt, tone, n) => `${fmt} · ${tone} · ${n} ricordi`,
    formats: {
      letter:     'Lettera',
      journal:    'Diario',
      monologue:  'Monologo',
      scene:      'Scena fiction',
      therapy:    'Trascrizione terapia',
      poem:       'Poesia',
    },
    tones: {
      raw:      'Grezzo',
      polished: 'Levigato',
      fragmented:'Frammentato',
      distant:  'Distante',
    },
    conceptPh:  'Concetto',
    contentPh:  'Cosa \u00e8 stato sentito\u2026',
    feelLabels: {
      gioia:'Gioia', tristezza:'Tristezza', rabbia:'Rabbia', paura:'Paura',
      nostalgia:'Nostalgia', amore:'Amore', malinconia:'Malinconia',
      serenità:'Serenità', sorpresa:'Sorpresa', ansia:'Ansia',
      gratitudine:'Gratitudine', vergogna:'Vergogna', orgoglio:'Orgoglio',
      noia:'Noia', curiosità:'Curiosità',
    },
    themeLight: '— CHIARO —',
    themeDark:  '— SCURO —',
    lmSave:     'Salva',
    lmModelPh:  'modello',
    promptFmts: {
      letter:    'Scrivi una lettera',
      journal:   'Scrivi un\'entrata di diario',
      monologue: 'Scrivi un monologo interiore',
      scene:     'Scrivi una breve scena di narrativa',
      therapy:   'Scrivi una trascrizione di seduta terapeutica (il paziente parla)',
      poem:      'Scrivi una poesia',
    },
    promptTones:{
      raw:       'in uno stile grezzo, non rifinito, confessionale',
      polished:  'in uno stile letterario, levigato, con cura per la costruzione delle frasi',
      fragmented:'in uno stile frammentato e non lineare — frasi spezzate, spazi bianchi, discontinuità',
      distant:   'in uno stile distaccato, come se si osservasse dall\'esterno in terza persona',
    },
    promptLen:  { short:'Tienilo breve (100–150 parole).', medium:'Punta a una lunghezza media (250–350 parole).', long:'Scrivi un pezzo pi\u00f9 lungo (500–700 parole).' },
    sysLang:    'Scrivi in italiano.',
  },

  es: {
    code:'es', label:'ES', name:'Español',
    wordmark:       'ECHO',
    tagline:        'generador narrativo emocional',
    archiveTitle:   'Archivo emocional',
    addCard:        '+ Añadir recuerdo',
    presetsLabel:   'Archivos de muestra',
    presets:        ['Hamlet','Havisham','Frankenstein'],
    fmtLabel:       'Formato',
    toneLabel:      'Tono',
    lengthLabel:    'Longitud',
    lenShort:       'Corto',
    lenMedium:      'Medio',
    lenLong:        'Largo',
    generateBtn:    'Generar',
    generating:     'Escribiendo desde el archivo\u2026',
    placeholderIcon:'',
    placeholderText:'Añade recuerdos emocionales al archivo,\nelige formato y tono,\nluego haz clic en Generar.',
    copyBtn:        'Copiar',
    regenBtn:       'Regenerar',
    copiedMsg:      '¡Copiado!',
    metaLabel:      (fmt, tone, n) => `${fmt} · ${tone} · ${n} recuerdos`,
    formats: {
      letter:     'Carta',
      journal:    'Diario',
      monologue:  'Monólogo',
      scene:      'Escena de ficción',
      therapy:    'Transcripción de terapia',
      poem:       'Poema',
    },
    tones: {
      raw:      'Crudo',
      polished: 'Pulido',
      fragmented:'Fragmentado',
      distant:  'Distante',
    },
    conceptPh:  'Concepto',
    contentPh:  'Qué se sintió\u2026',
    feelLabels: {
      gioia:'Alegría', tristezza:'Tristeza', rabbia:'Rabia', paura:'Miedo',
      nostalgia:'Nostalgia', amore:'Amor', malinconia:'Melancolía',
      serenità:'Serenidad', sorpresa:'Sorpresa', ansia:'Ansiedad',
      gratitudine:'Gratitud', vergogna:'Vergüenza', orgoglio:'Orgullo',
      noia:'Aburrimiento', curiosità:'Curiosidad',
    },
    themeLight: '— CLARO —',
    themeDark:  '— OSCURO —',
    lmSave:     'Guardar',
    lmModelPh:  'modelo',
    promptFmts: {
      letter:    'Escribe una carta',
      journal:   'Escribe una entrada de diario',
      monologue: 'Escribe un monólogo interior',
      scene:     'Escribe una breve escena de ficción',
      therapy:   'Escribe una transcripción de sesión de terapia (habla el paciente)',
      poem:      'Escribe un poema',
    },
    promptTones:{
      raw:       'en un estilo crudo, sin pulir, confesional',
      polished:  'en un estilo literario y cuidado, con atención a la construcción de las frases',
      fragmented:'en un estilo fragmentado y no lineal — frases rotas, espacios, discontinuidad',
      distant:   'en un estilo distante, observacional desde fuera, como en tercera persona',
    },
    promptLen:  { short:'Mantenlo corto (100–150 palabras).', medium:'Apunta a una longitud media (250–350 palabras).', long:'Escribe una pieza más larga (500–700 palabras).' },
    sysLang:    'Escribe en español.',
  },

  zh: {
    code:'zh', label:'中', name:'中文',
    wordmark:       'ECHO',
    tagline:        '情感叙事生成器',
    archiveTitle:   '情感档案',
    addCard:        '+ 添加记忆',
    presetsLabel:   '示例档案',
    presets:        ['哈姆雷特','哈维沙姆','弗兰肯斯坦'],
    fmtLabel:       '格式',
    toneLabel:      '语气',
    lengthLabel:    '长度',
    lenShort:       '短',
    lenMedium:      '中',
    lenLong:        '长',
    generateBtn:    '生成',
    generating:     '从档案中写作……',
    placeholderIcon:'',
    placeholderText:'向档案中添加情感记忆，\n选择格式和语气，\n然后点击生成。',
    copyBtn:        '复制',
    regenBtn:       '重新生成',
    copiedMsg:      '已复制！',
    metaLabel:      (fmt, tone, n) => `${fmt} · ${tone} · ${n} 条记忆`,
    formats: {
      letter:     '信件',
      journal:    '日记',
      monologue:  '内心独白',
      scene:      '小说场景',
      therapy:    '心理咨询记录',
      poem:       '诗歌',
    },
    tones: {
      raw:      '原始',
      polished: '精炼',
      fragmented:'碎片化',
      distant:  '疏离',
    },
    conceptPh:  '概念',
    contentPh:  '感受到了什么……',
    feelLabels: {
      gioia:'喜悦', tristezza:'悲伤', rabbia:'愤怒', paura:'恐惧',
      nostalgia:'怀旧', amore:'爱', malinconia:'忧郁',
      serenità:'宁静', sorpresa:'惊讶', ansia:'焦虑',
      gratitudine:'感恩', vergogna:'羞耻', orgoglio:'自豪',
      noia:'无聊', curiosità:'好奇',
    },
    themeLight: '— 浅色 —',
    themeDark:  '— 深色 —',
    lmSave:     '保存',
    lmModelPh:  '模型',
    promptFmts: {
      letter:    '写一封信',
      journal:   '写一篇日记',
      monologue: '写一段内心独白',
      scene:     '写一段短篇小说场景',
      therapy:   '写一段心理咨询记录（来访者发言）',
      poem:      '写一首诗',
    },
    promptTones:{
      raw:       '风格原始、未经雕琢、倾诉式',
      polished:  '风格文学、精炼，注重句子结构',
      fragmented:'风格碎片化、非线性——断裂的句子、空白、不连贯',
      distant:   '风格疏离，以旁观者视角，如同第三人称观察',
    },
    promptLen:  { short:'保持简短（100–150字）。', medium:'目标中等长度（250–350字）。', long:'写一篇较长的作品（500–700字）。' },
    sysLang:    '请用中文写作。',
  },
};
const LANG_ORDER = ['en','it','es','zh'];

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

// ══ Preset archives ═══════════════════════════════════════════
const PRESETS = {
  Hamlet: [
    { concept:'Father',   feeling:'amore',      content:'He used to wake me before dawn to watch the sea fog lift. He said the world looked honest for exactly one hour. I believed him.' },
    { concept:'Betrayal', feeling:'rabbia',      content:'The same cup. The same smile. The same hand that poured for thirty years. I cannot make the geometry of it work in my head.' },
    { concept:'Purpose',  feeling:'ansia',       content:'Every hour I choose not to act is a choice. I have made it four hundred times and I do not know why.' },
    { concept:'Love',     feeling:'vergogna',    content:'I was cruel to her today. She looked at me like I was already a ghost. Maybe I am.' },
    { concept:'Fate',     feeling:'serenità',    content:'There is a special providence in the fall of a sparrow. Whatever comes, comes. I think I am ready now.' },
  ],
  Havisham: [
    { concept:'Time',     feeling:'rabbia',      content:'I stopped them all. Every clock at twenty minutes to nine. They cannot take anything further from me if there is no further.' },
    { concept:'Wedding',  feeling:'vergogna',    content:'The dress is still on. I refuse to give that moment the dignity of my acknowledgement. I am still waiting.' },
    { concept:'Estella',  feeling:'orgoglio',    content:'She will feel nothing. I have made sure of it. That is the only mercy I know how to give.' },
    { concept:'Love',     feeling:'malinconia',  content:'What I cultivated in her was not strength but emptiness. I confused them and now I cannot go back.' },
    { concept:'Regret',   feeling:'tristezza',   content:'I made her that way. I spent a childhood building what I am now asking her to undo. The cruelty of me.' },
  ],
  Frankenstein: [
    { concept:'Creation', feeling:'orgoglio',    content:'It worked. For one second before I saw its eyes I was God.' },
    { concept:'Creation', feeling:'paura',       content:'Its eyes opened. Yellow, watery. And I ran. I left it there, alone, in the dark. I have never told anyone this.' },
    { concept:'Guilt',    feeling:'ansia',       content:'I cannot sleep without seeing them. The creature did not murder them. I murdered them by making the creature.' },
    { concept:'Ambition', feeling:'malinconia',  content:'I thought I was doing it for humanity. Now I think I was doing it because I was afraid of my father dying.' },
    { concept:'Ice',      feeling:'serenità',    content:'The cold has a clarity I was denied in the laboratory. The creature and I are the same — both ruined by the other.' },
  ],
};

// Preset names map by language
const PRESET_MAP = {
  en: { 'Hamlet':'Hamlet', 'Havisham':'Havisham', 'Frankenstein':'Frankenstein' },
  it: { 'Hamlet':'Hamlet', 'Havisham':'Havisham', 'Frankenstein':'Frankenstein' },
  es: { 'Hamlet':'Hamlet', 'Havisham':'Havisham', 'Frankenstein':'Frankenstein' },
  zh: { '哈姆雷特':'Hamlet', '哈维沙姆':'Havisham', '弗兰肯斯坦':'Frankenstein' },
};

// ══ Themes ═════════════════════════════════════════════════════
const THEMES = [
  {id:'ivory',    label:'Ivory',    bg:'#fafaf6', acc:'#7a5c2e', dark:false},
  {id:'paper',    label:'Paper',    bg:'#f5f2eb', acc:'#8b6020', dark:false},
  {id:'mint',     label:'Mint',     bg:'#f0f8f4', acc:'#1e7a58', dark:false},
  {id:'rose',     label:'Rose',     bg:'#fdf4f6', acc:'#b83858', dark:false},
  {id:'slate',    label:'Slate',    bg:'#f0f2f6', acc:'#3858b8', dark:false},
  {id:'cream',    label:'Cream',    bg:'#fefcf6', acc:'#c07838', dark:false},
  {id:'stone',    label:'Stone',    bg:'#f2f0ec', acc:'#4a4840', dark:false},
  {id:'lilac',    label:'Lilac',    bg:'#f6f4fc', acc:'#6848c8', dark:false},
  {id:'dawn',     label:'Dawn',     bg:'#fdf6f0', acc:'#c85c28', dark:false},
  {id:'sage',     label:'Sage',     bg:'#eef2ec', acc:'#386848', dark:false},
  {id:'obsidian', label:'Obsidian', bg:'#0e0f10', acc:'#c8a870', dark:true},
  {id:'midnight', label:'Midnight', bg:'#080c18', acc:'#6898f8', dark:true},
  {id:'ember',    label:'Ember',    bg:'#100c08', acc:'#e08030', dark:true},
  {id:'void',     label:'Void',     bg:'#000000', acc:'#c0c0c0', dark:true},
  {id:'forest',   label:'Forest',   bg:'#060e08', acc:'#50d870', dark:true},
  {id:'crimson',  label:'Crimson',  bg:'#100608', acc:'#e85060', dark:true},
  {id:'amethyst', label:'Amethyst', bg:'#080610', acc:'#c080f8', dark:true},
  {id:'graphite', label:'Graphite', bg:'#101214', acc:'#90b8d8', dark:true},
  {id:'candle',   label:'Candle',   bg:'#100c06', acc:'#f8d040', dark:true},
  {id:'ocean',    label:'Ocean',    bg:'#040c10', acc:'#38c8e0', dark:true},
];

// ══ State ══════════════════════════════════════════════════════
let currentLang    = 'en';
let currentTheme   = 'ivory';
let themePanelOpen = false;
let langPanelOpen  = false;
let selectedFormat = 'letter';
let selectedTone   = 'raw';
let selectedLength = 'medium';
let activePreset   = null;
let cardCount      = 0;
const SK_PREFS     = 'echo-prefs';

// ══ Utils ══════════════════════════════════════════════════════
const uid  = () => Math.random().toString(36).slice(2,9);
const esc  = s => String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const L    = () => LANGS[currentLang] || LANGS.en;
const fl   = k => L().feelLabels[k] || k;
const col  = k => FEELING_COLORS[k] || '#888';

// ══ Persistence ════════════════════════════════════════════════
function loadPrefs() {
  try {
    const p = JSON.parse(localStorage.getItem(SK_PREFS)||'{}');
    if (p.theme && THEMES.find(t=>t.id===p.theme)) currentTheme = p.theme;
    if (p.lang  && LANGS[p.lang])  currentLang  = p.lang;
    if (p.lmUrl)   document.getElementById('lm-url').value   = p.lmUrl;
    if (p.lmModel) document.getElementById('lm-model').value = p.lmModel;
  } catch(e) {}
  applyTheme(currentTheme, false);
  applyLang(currentLang, false);
}

function savePrefs() {
  try {
    localStorage.setItem(SK_PREFS, JSON.stringify({
      theme:   currentTheme,
      lang:    currentLang,
      lmUrl:   document.getElementById('lm-url').value.trim(),
      lmModel: document.getElementById('lm-model').value.trim(),
    }));
  } catch(e) {}
}

function saveLm() {
  savePrefs();
  const el = document.getElementById('lm-ok');
  el.style.display='inline';
  setTimeout(()=>el.style.display='none', 2000);
}

// ══ Theme ══════════════════════════════════════════════════════
function applyTheme(id, persist=true) {
  currentTheme = id;
  document.documentElement.setAttribute('data-theme', id);
  if (persist) savePrefs();
  document.querySelectorAll('.th-dot').forEach(d=>d.classList.toggle('active',d.dataset.theme===id));
  const th  = THEMES.find(t=>t.id===id);
  const btn = document.getElementById('btn-theme');
  if (btn && th)
    btn.innerHTML = `<span style="display:inline-block;width:11px;height:11px;background:${th.acc};border-radius:3px;flex-shrink:0"></span>${th.label}`;
}

function buildThemePanel() {
  const l = L();
  const sw = group => group.map(t =>
    `<div class="th-dot${t.id===currentTheme?' active':''}" data-theme="${t.id}" title="${t.label}"
      style="background:${t.bg};outline:2px solid ${t.acc}44"
      onclick="applyTheme('${t.id}')"></div>`).join('');
  return `<div class="panel-lbl">${l.themeLight}</div><div class="swatch-row">${sw(THEMES.filter(t=>!t.dark))}</div>
    <div class="panel-lbl">${l.themeDark}</div><div class="swatch-row">${sw(THEMES.filter(t=>t.dark))}</div>`;
}

function toggleThemePanel() {
  themePanelOpen=!themePanelOpen;
  if(langPanelOpen){langPanelOpen=false;document.getElementById('lang-panel')?.classList.remove('open')}
  const p=document.getElementById('theme-panel');
  if(p){p.innerHTML=themePanelOpen?buildThemePanel():'';p.classList.toggle('open',themePanelOpen)}
}

// ══ Language ═══════════════════════════════════════════════════
function applyLang(code, persist=true) {
  currentLang = code;
  document.documentElement.lang = code;
  if (persist) savePrefs();
  document.querySelectorAll('.lang-opt').forEach(b=>b.classList.toggle('active',b.dataset.lang===code));
  renderStaticText();
}

function buildLangPanel() {
  return LANG_ORDER.map(code=>{
    const lg=LANGS[code];
    return `<button class="lang-opt${code===currentLang?' active':''}" data-lang="${code}"
      onclick="applyLang('${code}');toggleLangPanel()">${lg.label}<span class="ln">${lg.name}</span></button>`;
  }).join('');
}

function toggleLangPanel() {
  langPanelOpen=!langPanelOpen;
  if(themePanelOpen){themePanelOpen=false;document.getElementById('theme-panel')?.classList.remove('open')}
  const p=document.getElementById('lang-panel');
  if(p){p.innerHTML=langPanelOpen?buildLangPanel():'';p.classList.toggle('open',langPanelOpen)}
}

document.addEventListener('click', e=>{
  const tw=document.getElementById('theme-wrap');
  const lw=document.getElementById('lang-wrap');
  if(themePanelOpen&&tw&&!tw.contains(e.target)){themePanelOpen=false;document.getElementById('theme-panel')?.classList.remove('open')}
  if(langPanelOpen&&lw&&!lw.contains(e.target)){langPanelOpen=false;document.getElementById('lang-panel')?.classList.remove('open')}
});

// ══ Static text ════════════════════════════════════════════════
function renderStaticText() {
  const l = L();
  const s = (id,txt)=>{const e=document.getElementById(id);if(e)e.textContent=txt};
  const h = (id,html)=>{const e=document.getElementById(id);if(e)e.innerHTML=html};
  const p = (id,txt)=>{const e=document.getElementById(id);if(e)e.placeholder=txt};

  s('wordmark',        l.wordmark);
  s('tagline',         l.tagline);
  s('archive-title',   l.archiveTitle);
  s('btn-add-card',    l.addCard);
  s('presets-label',   l.presetsLabel);
  s('fmt-label',       l.fmtLabel);
  s('tone-label',      l.toneLabel);
  s('length-label',    l.lengthLabel);
  s('btn-generate',    l.generateBtn);
  s('lm-save-btn',     l.lmSave);
  p('lm-model',        l.lmModelPh);
  s('gen-label',       l.generating);

  // format chips
  const fc = document.getElementById('fmt-chips');
  if (fc) fc.innerHTML = Object.entries(l.formats).map(([k,v])=>
    `<button class="fmt-chip${k===selectedFormat?' active':''}" onclick="selectFormat('${k}')">${v}</button>`
  ).join('');

  // tone chips
  const tc = document.getElementById('tone-chips');
  if (tc) tc.innerHTML = Object.entries(l.tones).map(([k,v])=>
    `<button class="tone-chip${k===selectedTone?' active':''}" onclick="selectTone('${k}')">${v}</button>`
  ).join('');

  // length labels
  const ls = document.getElementById('len-short-lbl');
  const lm = document.getElementById('len-long-lbl');
  if (ls) ls.textContent = l.lenShort;
  if (lm) lm.textContent = l.lenLong;

  // preset buttons
  const pr = document.getElementById('preset-row');
  if (pr) pr.innerHTML = l.presets.map(name=>{
    const key = PRESET_MAP[currentLang]?.[name] || name;
    return `<button class="preset-btn${activePreset===key?' active':''}" onclick="loadPreset('${key}')">${name}</button>`;
  }).join('');

  // placeholder
  s('output-placeholder-text', l.placeholderText.replace('\n','<br>'));

  // lang btn
  const lb = document.getElementById('btn-lang');
  if (lb) lb.textContent = l.label;

  // theme btn
  const th = THEMES.find(t=>t.id===currentTheme);
  const tb = document.getElementById('btn-theme');
  if (tb && th)
    tb.innerHTML = `<span style="display:inline-block;width:11px;height:11px;background:${th.acc};border-radius:3px;flex-shrink:0"></span>${th.label}`;

  // update existing cards' feel options
  document.querySelectorAll('.mc-feeling').forEach(sel=>{
    const cur = sel.value;
    sel.innerHTML = feelingOptions();
    sel.value = cur;
    sel.style.color = col(sel.value);
  });

  // update existing cards' placeholders
  document.querySelectorAll('.mc-concept').forEach(i=>i.placeholder=l.conceptPh);
  document.querySelectorAll('.mc-content').forEach(t=>t.placeholder=l.contentPh);
}

function feelingOptions() {
  return FEELING_KEYS.map(k=>`<option value="${k}">${fl(k)}</option>`).join('');
}

// ══ Format / Tone / Length ═════════════════════════════════════
function selectFormat(k) {
  selectedFormat = k;
  document.querySelectorAll('.fmt-chip').forEach(c=>c.classList.toggle('active',c.textContent===L().formats[k]));
  // simpler: re-render chips
  const fc = document.getElementById('fmt-chips');
  if (fc) fc.innerHTML = Object.entries(L().formats).map(([fk,fv])=>
    `<button class="fmt-chip${fk===selectedFormat?' active':''}" onclick="selectFormat('${fk}')">${fv}</button>`
  ).join('');
}

function selectTone(k) {
  selectedTone = k;
  const tc = document.getElementById('tone-chips');
  if (tc) tc.innerHTML = Object.entries(L().tones).map(([tk,tv])=>
    `<button class="tone-chip${tk===selectedTone?' active':''}" onclick="selectTone('${tk}')">${tv}</button>`
  ).join('');
}

function updateLength() {
  const val = parseInt(document.getElementById('length-slider').value);
  selectedLength = val <= 33 ? 'short' : val <= 66 ? 'medium' : 'long';
  document.getElementById('length-display').textContent =
    selectedLength === 'short' ? L().lenShort :
    selectedLength === 'long'  ? L().lenLong  : L().lenMedium;
}

// ══ Memory cards ═══════════════════════════════════════════════
function addCard(data) {
  cardCount++;
  const id  = 'card-' + uid();
  const l   = L();
  const fOpts = feelingOptions();
  const defFeel = data?.feeling || FEELING_KEYS[cardCount % FEELING_KEYS.length];

  const card = document.createElement('div');
  card.className = 'mem-input-card fade-in';
  card.id = id;
  card.innerHTML = `
    <span class="card-index">#${cardCount}</span>
    <button class="btn-remove-card" onclick="removeCard('${id}')" title="Remove">×</button>
    <div class="mem-card-row">
      <input class="mc-concept" type="text" placeholder="${l.conceptPh}" value="${esc(data?.concept||'')}">
      <select class="mc-feeling" onchange="this.style.color=feelCol(this.value)">
        ${fOpts}
      </select>
    </div>
    <textarea class="mc-content" rows="2" placeholder="${l.contentPh}">${esc(data?.content||'')}</textarea>`;

  document.getElementById('cards-container').appendChild(card);

  const sel = card.querySelector('.mc-feeling');
  sel.value = defFeel;
  sel.style.color = col(defFeel);
}

function feelCol(k) { return col(k); }

function removeCard(id) {
  document.getElementById(id)?.remove();
  activePreset = null;
  // update preset buttons
  const pr = document.getElementById('preset-row');
  if (pr) pr.querySelectorAll('.preset-btn').forEach(b=>b.classList.remove('active'));
}

function getCards() {
  return [...document.querySelectorAll('.mem-input-card')].map(card=>{
    return {
      concept: card.querySelector('.mc-concept').value.trim(),
      feeling: card.querySelector('.mc-feeling').value,
      content: card.querySelector('.mc-content').value.trim(),
    };
  }).filter(c=>c.concept && c.content);
}

function clearCards() {
  document.getElementById('cards-container').innerHTML = '';
  cardCount = 0;
  activePreset = null;
  const pr = document.getElementById('preset-row');
  if (pr) pr.querySelectorAll('.preset-btn').forEach(b=>b.classList.remove('active'));
}

function loadPreset(key) {
  clearCards();
  activePreset = key;
  const mems = PRESETS[key];
  if (!mems) return;
  mems.forEach(m => addCard(m));
  // highlight preset btn
  const pr = document.getElementById('preset-row');
  if (pr) pr.querySelectorAll('.preset-btn').forEach(b=>{
    const bKey = PRESET_MAP[currentLang]?.[b.textContent] || b.textContent;
    b.classList.toggle('active', bKey===key);
  });
}

// ══ Generate ═══════════════════════════════════════════════════
async function generate() {
  const cards = getCards();
  if (!cards.length) return;
  const l = L();

  // show overlay
  document.getElementById('gen-overlay').classList.add('show');
  document.getElementById('btn-generate').disabled = true;
  document.getElementById('output-placeholder').style.display = 'none';
  document.getElementById('output-doc').style.display = 'none';

  const archiveBlock = cards.map(c =>
    `CONCEPT: ${c.concept} | FEELING: ${fl(c.feeling)}\n"${c.content}"`
  ).join('\n\n');

  const lenKey = selectedLength;
  const fmtKey = selectedFormat;
  const toneKey = selectedTone;

  const promptInstr = `${l.promptFmts[fmtKey]} ${l.promptTones[toneKey]}. ${l.promptLen[lenKey]}`;

  const sys = `You are a literary writer working from an emotional memory archive.
Your task: generate narrative content grounded ONLY in the emotional memories provided.
Do not invent events outside the archive. The memories are the emotional soil — the writing grows from them.
Do not include titles, headings, labels, or meta-commentary. Output only the piece itself.
${l.sysLang}`;

  const userMsg = `${promptInstr}

The piece must be emotionally grounded in this archive:

${archiveBlock}`;

  const lmUrl   = document.getElementById('lm-url').value.trim();
  const lmModel = document.getElementById('lm-model').value.trim();
  const maxToks = lenKey==='short'?300:lenKey==='long'?900:550;

  let output = '';
  try {
    const res = await fetch(lmUrl, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        model: lmModel||'local-model',
        max_tokens: maxToks,
        temperature: toneKey==='raw'?0.9 : toneKey==='fragmented'?0.95 : toneKey==='polished'?0.65 : 0.75,
        messages:[
          {role:'system', content:sys},
          {role:'user',   content:userMsg}
        ]
      })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status} — is LM Studio running?`);
    const data = await res.json();
    output = data.choices?.[0]?.message?.content?.trim() || '[Empty response from model]';
  } catch(e) {
    output = `[Generation failed — ${e.message}\n\nCheck that LM Studio is running and a model is loaded.]`;
  }

  // hide overlay, show output
  document.getElementById('gen-overlay').classList.remove('show');
  document.getElementById('btn-generate').disabled = false;
  showOutput(output, fmtKey, toneKey, cards.length);
}

function showOutput(text, fmtKey, toneKey, n) {
  const l = L();
  document.getElementById('output-placeholder').style.display = 'none';
  const doc = document.getElementById('output-doc');
  doc.style.display = 'block';
  doc.classList.add('fade-in');

  document.getElementById('output-format-badge').textContent = L().formats[fmtKey];
  document.getElementById('output-format-badge').style.cssText +=
    ';background:var(--accent-bg);color:var(--accent);border-color:var(--accent)';
  document.getElementById('output-meta').textContent = l.metaLabel(l.formats[fmtKey], l.tones[toneKey], n);
  document.getElementById('output-text').textContent = text;
  document.getElementById('btn-copy').textContent  = l.copyBtn;
  document.getElementById('btn-regen').textContent = l.regenBtn;

  // store for regen
  doc.dataset.lastFmt  = fmtKey;
  doc.dataset.lastTone = toneKey;
  doc.dataset.lastN    = n;
}

function copyOutput() {
  const text = document.getElementById('output-text').textContent;
  navigator.clipboard.writeText(text).then(()=>{
    const btn = document.getElementById('btn-copy');
    btn.textContent = L().copiedMsg;
    setTimeout(()=>btn.textContent=L().copyBtn, 2000);
  }).catch(()=>{
    // fallback
    const ta = document.createElement('textarea');
    ta.value = text; ta.style.position='fixed'; ta.style.opacity='0';
    document.body.appendChild(ta); ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    const btn = document.getElementById('btn-copy');
    btn.textContent = L().copiedMsg;
    setTimeout(()=>btn.textContent=L().copyBtn, 2000);
  });
}

// ══ Mobile sidebar ══════════════════════════════════════════════
function toggleSidebar() {
  document.getElementById('left-panel').classList.toggle('open');
  document.getElementById('left-backdrop').classList.toggle('open');
}
function closeSidebar() {
  document.getElementById('left-panel').classList.remove('open');
  document.getElementById('left-backdrop').classList.remove('open');
}

// ══ Boot ═══════════════════════════════════════════════════════
loadPrefs();
renderStaticText();
// start with 3 blank cards
addCard(); addCard(); addCard();
