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


/* ── i18n system ─────────────────────────────────────────── */
let _lang = localStorage.getItem('mnheme_lang') || 'en';

const FEELINGS_I18N = {
  en: {
    ansia:'🌀 Anxiety', paura:'🌑 Fear', sollievo:'😮‍💨 Relief',
    tristezza:'🌧 Sadness', gioia:'✨ Joy', rabbia:'🔥 Anger',
    vergogna:'◈ Shame', senso_di_colpa:'😔 Guilt',
    nostalgia:'🍂 Nostalgia', speranza:'🌱 Hope',
    orgoglio:'▲ Pride', delusione:'💔 Disappointment',
    solitudine:'🌙 Loneliness', confusione:'🌀 Confusion',
    gratitudine:'✿ Gratitude', invidia:'💚 Envy',
    imbarazzo:'😳 Embarrassment', eccitazione:'⚡ Excitement',
    rassegnazione:'🏳 Resignation', stupore:'✨ Awe',
    amore:'❤ Love', malinconia:'🌊 Melancholy',
    serenità:'🌿 Serenity', sorpresa:'⚡ Surprise',
    noia:'— Boredom', curiosità:'◎ Curiosity',
  },
  it: {
    ansia:'🌀 Ansia', paura:'🌑 Paura', sollievo:'😮‍💨 Sollievo',
    tristezza:'🌧 Tristezza', gioia:'✨ Gioia', rabbia:'🔥 Rabbia',
    vergogna:'◈ Vergogna', senso_di_colpa:'😔 Senso di colpa',
    nostalgia:'🍂 Nostalgia', speranza:'🌱 Speranza',
    orgoglio:'▲ Orgoglio', delusione:'💔 Delusione',
    solitudine:'🌙 Solitudine', confusione:'🌀 Confusione',
    gratitudine:'✿ Gratitudine', invidia:'💚 Invidia',
    imbarazzo:'😳 Imbarazzo', eccitazione:'⚡ Eccitazione',
    rassegnazione:'🏳 Rassegnazione', stupore:'✨ Stupore',
    amore:'❤ Amore', malinconia:'🌊 Malinconia',
    serenità:'🌿 Serenità', sorpresa:'⚡ Sorpresa',
    noia:'— Noia', curiosità:'◎ Curiosità',
  },
  es: {
    ansia:'🌀 Ansiedad', paura:'🌑 Miedo', sollievo:'😮‍💨 Alivio',
    tristezza:'🌧 Tristeza', gioia:'✨ Alegría', rabbia:'🔥 Ira',
    vergogna:'◈ Vergüenza', senso_di_colpa:'😔 Culpa',
    nostalgia:'🍂 Nostalgia', speranza:'🌱 Esperanza',
    orgoglio:'▲ Orgullo', delusione:'💔 Decepción',
    solitudine:'🌙 Soledad', confusione:'🌀 Confusión',
    gratitudine:'✿ Gratitud', invidia:'💚 Envidia',
    imbarazzo:'😳 Embarazo', eccitazione:'⚡ Emoción',
    rassegnazione:'🏳 Resignación', stupore:'✨ Asombro',
    amore:'❤ Amor', malinconia:'🌊 Melancolía',
    serenità:'🌿 Serenidad', sorpresa:'⚡ Sorpresa',
    noia:'— Aburrimiento', curiosità:'◎ Curiosidad',
  },
  zh: {
    ansia:'🌀 焦虑', paura:'🌑 恐惧', sollievo:'😮‍💨 如释重负',
    tristezza:'🌧 悲伤', gioia:'✨ 喜悦', rabbia:'🔥 愤怒',
    vergogna:'◈ 羞耻', senso_di_colpa:'😔 内疚',
    nostalgia:'🍂 怀旧', speranza:'🌱 希望',
    orgoglio:'▲ 自豪', delusione:'💔 失望',
    solitudine:'🌙 孤独', confusione:'🌀 困惑',
    gratitudine:'✿ 感激', invidia:'💚 嫉妒',
    imbarazzo:'😳 尴尬', eccitazione:'⚡ 兴奋',
    rassegnazione:'🏳 听天由命', stupore:'✨ 惊叹',
    amore:'❤ 爱', malinconia:'🌊 忧郁',
    serenità:'🌿 宁静', sorpresa:'⚡ 惊讶',
    noia:'— 无聊', curiosità:'◎ 好奇',
  },
};

const UI_I18N = {
  en: {
    selectFeeling: '— select —', allFeelings: 'All feelings',
    allFeelings2: 'All', autoFeeling: 'auto',
    styleNarrative: 'Narrative', styleAnalytical: 'Analytical', stylePoetic: 'Poetic',

    // Static UI text
    navMemory:'Memory', navExplore:'Explore', navSystem:'System', navBrain:'Brain · LLM',
    titleNewMemory:'New Memory', descNewMemory:'Append a new immutable memory to the database.',
    labelConcept:'Concept', labelConcept2:'Concept', labelConcept3:'Concept',
    labelConcept4:'Concept', labelConcept5:'Concept',
    labelFeeling:'Feeling', labelFeeling2:'Feeling',
    labelContent:'Content', labelNote:'Note', labelNote2:'Note',
    labelMediaType:'Media type', labelTags:'Tags',
    labelRawInput:'Raw input', labelConceptOverride:'Concept',
    labelQuestion:'Question', labelMaxMemories:'Max memories',
    labelMaxMem2:'Max memories', labelMemSample:'Memories to sample',
    labelFeelingFilter:'Feeling filter', labelFilterFeeling:'Filter feeling',
    labelLimit:'Limit', labelOrder:'Order', labelByTag:'By tag:',
    labelConceptFilter:'Concept filter', labelFeelingOpt:'Feeling',
    labelConceptOpt:'Concept', labelStyle:'Style',
    labelIncludeContent:'Include content field',
    labelReqLog:'Request log',
    optOptional:'optional', optCommaSep:'comma separated',
    optOverrideLLM:'override LLM', optNewest:'Newest first', optOldest:'Oldest first',
    btnRemember:'Remember', btnClear:'Clear', btnFetch:'Fetch',
    btnSearch:'Search', btnTagSearch:'Tag search',
    btnLoadConcepts:'Load concepts', btnClose:'✕ Close',
    btnFetchMemories:'Fetch memories', btnLoadDist:'Load distribution',
    btnLoadTimeline:'Load timeline', btnRefreshStats:'Refresh stats',
    btnExportJSON:'Export JSON', btnDownload:'Download file',
    btnClearLog:'clear',
    titleBrowse:'Browse Memories', descBrowse:'Retrieve memories with optional filters.',
    titleSearch:'Search', descSearch:'Full-text search via inverted index — O(k).',
    titleConcepts:'Concepts', descConcepts:'All conceptual keys with emotional distribution.',
    titleFeelings:'Feelings', descFeelings:'Emotional distribution across the entire database.',
    titleTimeline:'Timeline', descTimeline:'Emotional arc of a concept over time.',
    titleStats:'Stats', descStats:'General database statistics and storage info.',
    titleExport:'Export', descExport:'Export memories as JSON with optional filters.',
    phConcept:'Debt, Family, Work…', phContent:'Write the memory…',
    phNote:'Context, annotations…', phTags:'house, 2024, urgent…',
    phSearch:'Type to search memories…', phTag:'home, work, urgent…',
    phConceptFilter:'All concepts if empty', phRawInput:'Write freely — a thought, an event, an emotion…',
    phAuto:'auto', phQuestion:"How do I feel about money? Is there anything unresolved?",
    phAllConcepts:'All concepts',
    // Brain loading
    loadPerceiving: () => 'Brain is perceiving…',
    loadAsking:     () => 'Brain is searching memories…',
    loadReflecting: (c) => `Emotional analysis of "${c}"`,
    loadDreaming:   (n) => `Sampling ${n} memories from different emotions`,
    loadIntrospect: () => 'Analysing entire memory…',
    loadSummarize:  (s) => `Style ${s} — collecting memories`,
    // Toasts
    toastRequired:   () => 'Concept, feeling and content are required.',
    toastEnterInput: () => 'Enter an input.',
    toastEnterQ:     () => 'Enter a question.',
    toastEnterConcept: () => 'Enter a concept name.',
    toastSaved:    (c,f) => `Memory saved: ${c} / ${f}`,
    toastPerceived:(c,f) => `Perception saved: ${c} / ${f}`,
    toastPercErr:  () => 'Perceive failed',
    toastAskErr:   () => 'Ask failed',
    toastRefErr:   () => 'Reflect failed',
    toastDreamErr: () => 'Dream failed',
    toastIntErr:   () => 'Introspect failed',
    toastSumErr:   () => 'Summarize failed',
    // Response headers
    respPerceived: () => '✦ Memory perceived',
    respAnswer:    () => '✦ Answer',
    respReflect:   (c) => `✦ Reflection — ${c}`,
    respDream:     () => '✦ Dream',
    respIntrospect:() => '✦ Introspection',
    respSummary:   (s) => `✦ Summary — ${s}`,
    // Counts
    memoriesCtx:     (n) => `${n} memor${n!==1?'ies':'y'} used as context`,
    memoriesOf:      (n) => `${n} memor${n!==1?'ies':'y'}`,
    memoriesSampled: (n) => `${n} memor${n!==1?'ies':'y'} sampled`,
    memoriesAnalysed:(n) => `${n} memor${n!==1?'ies':'y'} analysed`,
  },
  it: {
    selectFeeling: '— seleziona —', allFeelings: 'Tutti i sentimenti',
    allFeelings2: 'Tutti', autoFeeling: 'auto',
    styleNarrative: 'Narrativo', styleAnalytical: 'Analitico', stylePoetic: 'Poetico',
    loadPerceiving: () => 'Il Brain sta percependo…',
    loadAsking:     () => 'Il Brain sta cercando nei ricordi…',
    loadReflecting: (c) => `Analisi emotiva di "${c}"`,
    loadDreaming:   (n) => `Campionamento di ${n} ricordi`,
    loadIntrospect: () => "Analisi dell'intera memoria…",
    loadSummarize:  (s) => `Stile ${s} — raccogliendo ricordi`,
    toastRequired:   () => 'Concept, sentimento e contenuto sono obbligatori.',
    toastEnterInput: () => 'Inserisci un input.',
    toastEnterQ:     () => 'Inserisci una domanda.',
    toastEnterConcept: () => 'Inserisci un concetto.',
    toastSaved:    (c,f) => `Ricordo salvato: ${c} / ${f}`,
    toastPerceived:(c,f) => `Percezione salvata: ${c} / ${f}`,
    toastPercErr:  () => 'Perceive fallito',
    toastAskErr:   () => 'Ask fallito',
    toastRefErr:   () => 'Reflect fallito',
    toastDreamErr: () => 'Dream fallito',
    toastIntErr:   () => 'Introspect fallito',
    toastSumErr:   () => 'Summarize fallito',
    respPerceived: () => '✦ Ricordo percepito',
    respAnswer:    () => '✦ Risposta',
    respReflect:   (c) => `✦ Riflessione — ${c}`,
    respDream:     () => '✦ Sogno',
    respIntrospect:() => '✦ Introspezione',
    respSummary:   (s) => `✦ Riassunto — ${s}`,
    memoriesCtx:     (n) => `${n} ricord${n!==1?'i':'o'} come contesto`,
    memoriesOf:      (n) => `${n} ricord${n!==1?'i':'o'}`,
    memoriesSampled: (n) => `${n} ricord${n!==1?'i':'o'} campionati`,
    memoriesAnalysed:(n) => `${n} ricord${n!==1?'i':'o'} analizzati`,
  },
  es: {
    selectFeeling: '— seleccionar —', allFeelings: 'Todos los sentimientos',
    allFeelings2: 'Todos', autoFeeling: 'auto',
    styleNarrative: 'Narrativo', styleAnalytical: 'Analítico', stylePoetic: 'Poético',
    loadPerceiving: () => 'El Brain está percibiendo…',
    loadAsking:     () => 'El Brain está buscando recuerdos…',
    loadReflecting: (c) => `Análisis emocional de "${c}"`,
    loadDreaming:   (n) => `Muestreando ${n} recuerdos`,
    loadIntrospect: () => 'Analizando toda la memoria…',
    loadSummarize:  (s) => `Estilo ${s} — recopilando recuerdos`,
    toastRequired:   () => 'Concept, sentimiento y contenido son obligatorios.',
    toastEnterInput: () => 'Introduce un input.',
    toastEnterQ:     () => 'Introduce una pregunta.',
    toastEnterConcept: () => 'Introduce un concepto.',
    toastSaved:    (c,f) => `Recuerdo guardado: ${c} / ${f}`,
    toastPerceived:(c,f) => `Percepción guardada: ${c} / ${f}`,
    toastPercErr:  () => 'Perceive falló',
    toastAskErr:   () => 'Ask falló',
    toastRefErr:   () => 'Reflect falló',
    toastDreamErr: () => 'Dream falló',
    toastIntErr:   () => 'Introspect falló',
    toastSumErr:   () => 'Summarize falló',
    respPerceived: () => '✦ Recuerdo percibido',
    respAnswer:    () => '✦ Respuesta',
    respReflect:   (c) => `✦ Reflexión — ${c}`,
    respDream:     () => '✦ Sueño',
    respIntrospect:() => '✦ Introspección',
    respSummary:   (s) => `✦ Resumen — ${s}`,
    memoriesCtx:     (n) => `${n} recuerdo${n!==1?'s':''} como contexto`,
    memoriesOf:      (n) => `${n} recuerdo${n!==1?'s':''}`,
    memoriesSampled: (n) => `${n} recuerdo${n!==1?'s':''} muestreados`,
    memoriesAnalysed:(n) => `${n} recuerdo${n!==1?'s':''} analizados`,
  },
  zh: {
    selectFeeling: '— 选择 —', allFeelings: '所有情感',
    allFeelings2: '全部', autoFeeling: '自动',
    styleNarrative: '叙述式', styleAnalytical: '分析式', stylePoetic: '诗意式',
    loadPerceiving: () => 'Brain 正在感知…',
    loadAsking:     () => 'Brain 正在搜索记忆…',
    loadReflecting: (c) => `情感分析：「${c}」`,
    loadDreaming:   (n) => `从不同情感中抽取 ${n} 条记忆`,
    loadIntrospect: () => '正在分析全部记忆…',
    loadSummarize:  (s) => `${s}风格 — 收集记忆中`,
    toastRequired:   () => '概念、情感和内容为必填项。',
    toastEnterInput: () => '请输入内容。',
    toastEnterQ:     () => '请输入问题。',
    toastEnterConcept: () => '请输入概念名称。',
    toastSaved:    (c,f) => `记忆已保存：${c} / ${f}`,
    toastPerceived:(c,f) => `感知已保存：${c} / ${f}`,
    toastPercErr:  () => 'Perceive 失败',
    toastAskErr:   () => 'Ask 失败',
    toastRefErr:   () => 'Reflect 失败',
    toastDreamErr: () => 'Dream 失败',
    toastIntErr:   () => 'Introspect 失败',
    toastSumErr:   () => 'Summarize 失败',
    respPerceived: () => '✦ 记忆已感知',
    respAnswer:    () => '✦ 回答',
    respReflect:   (c) => `✦ 反思 — ${c}`,
    respDream:     () => '✦ 梦境',
    respIntrospect:() => '✦ 内省',
    respSummary:   (s) => `✦ 摘要 — ${s}`,
    memoriesCtx:     (n) => `${n} 条记忆作为上下文`,
    memoriesOf:      (n) => `${n} 条记忆`,
    memoriesSampled: (n) => `${n} 条记忆已抽取`,
    memoriesAnalysed:(n) => `${n} 条记忆已分析`,
    navMemory:'记忆', navExplore:'探索', navSystem:'系统', navBrain:'Brain · LLM',
    titleNewMemory:'新记忆', descNewMemory:'向数据库追加一条不可变记忆。',
    labelConcept:'概念', labelConcept2:'概念', labelConcept3:'概念',
    labelConcept4:'概念', labelConcept5:'概念',
    labelFeeling:'情感', labelFeeling2:'情感',
    labelContent:'内容', labelNote:'备注', labelNote2:'备注',
    labelMediaType:'媒体类型', labelTags:'标签',
    labelRawInput:'自由输入', labelConceptOverride:'概念',
    labelQuestion:'问题', labelMaxMemories:'最多记忆数',
    labelMaxMem2:'最多记忆数', labelMemSample:'抽取记忆数',
    labelFeelingFilter:'筛选情感', labelFilterFeeling:'筛选情感',
    labelLimit:'限制', labelOrder:'排序', labelByTag:'按标签:',
    labelConceptFilter:'筛选概念', labelFeelingOpt:'情感',
    labelConceptOpt:'概念', labelStyle:'风格',
    labelIncludeContent:'包含内容字段',
    labelReqLog:'请求日志',
    optOptional:'可选', optCommaSep:'逗号分隔',
    optOverrideLLM:'覆盖LLM', optNewest:'最新优先', optOldest:'最旧优先',
    btnRemember:'记住', btnClear:'清除', btnFetch:'获取',
    btnSearch:'搜索', btnTagSearch:'按标签搜索',
    btnLoadConcepts:'加载概念', btnClose:'✕ 关闭',
    btnFetchMemories:'加载记忆', btnLoadDist:'加载分布',
    btnLoadTimeline:'加载时间线', btnRefreshStats:'刷新统计',
    btnExportJSON:'导出 JSON', btnDownload:'下载文件',
    btnClearLog:'清空',
    titleBrowse:'浏览记忆', descBrowse:'获取记忆，支持可选筛选条件。',
    titleSearch:'搜索', descSearch:'基于倒排索引的全文搜索 — O(k)。',
    titleConcepts:'概念', descConcepts:'所有概念键及其情感分布。',
    titleFeelings:'情感', descFeelings:'整个数据库的情感分布。',
    titleTimeline:'时间线', descTimeline:'概念随时间的情感弧线。',
    titleStats:'统计', descStats:'数据库总体统计及存储信息。',
    titleExport:'导出', descExport:'将记忆导出为JSON，支持可选筛选。',
    phConcept:'债务、家庭、工作…', phContent:'写下记忆…',
    phNote:'上下文、备注…', phTags:'家, 2024, 紧急…',
    phSearch:'搜索记忆…', phTag:'家, 工作, 紧急…',
    phConceptFilter:'空则全部', phRawInput:'自由书写 — 一个想法、一件事、一种情绪…',
    phAuto:'自动', phQuestion:'我对金钱的真实感受是什么？',
    phAllConcepts:'所有概念',
  },
};

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
  const raw     = document.getElementById('perceive-input').value.trim();
  const concept = document.getElementById('perceive-concept').value.trim();
  const feeling = document.getElementById('perceive-feeling').value;
  const note    = document.getElementById('perceive-note').value.trim();
  if (!raw) { toast(ui('toastEnterInput'), 'info'); return; }

  const restore = disableBtn('btn-perceive', 'Perceiving');
  brainLoading('perceive-result', ui('loadPerceiving'));
  const t0 = performance.now();

  try {
    const r = await POST('/brain/perceive', {
      raw_input: raw,
      concept:   concept || null,
      feeling:   feeling || null,
      note,
    });
    const ms   = Math.round(performance.now() - t0);
    const tags = (r.extracted_tags || [])
      .map(t => `<span class="perceive-chip tag">${esc(t)}</span>`).join('');

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