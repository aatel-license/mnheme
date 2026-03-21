/* ═══════════════════════════════════════════════════════════
   STRATA — app.js
   Collective MNHEME Emotional Archive
   i18n: EN / IT / ES / ZH · 20 themes
   ═══════════════════════════════════════════════════════════ */

// ══ i18n ════════════════════════════════════════════════════
const LANGS = {
  en:{
    code:'en',label:'EN',name:'English',
    wordmark:'STRATA',tagline:'collective emotional archive',
    community:'Community name',
    members: n=>`${n} voice${n===1?'':'s'}`,
    inputTitle:'Add a memory',
    voiceLbl:'Your name or alias',
    anonLbl:'Anonymous',
    eventLbl:'Event / topic',
    feelLbl:'Feeling',
    contentLbl:'What you felt',
    contentPh:'Describe your emotional experience\u2026',
    eventPh:'e.g. The Closure, First Day, The Storm\u2026',
    voicePh:'Name or alias\u2026',
    addBtn:'Add to the archive',
    feedTitle:'Archive feed',
    themeLight:'\u2014 LIGHT \u2014',themeDark:'\u2014 DARK \u2014',
    exportBtn:'Export',importBtn:'Import',clearBtn:'Clear all',
    tabConsensus:'Consensus',tabVoices:'Voices',tabTimeline:'Timeline',
    statEntries:'Total entries',statEvents:'Events',statVoices:'Voices',statDominant:'Dominant feeling',
    consensusTitle:'Consensus map',divergTitle:'Emotional divergence',
    emptyConsensus:'Add memories for multiple events to see consensus patterns.',
    emptyDiverg:'Divergence appears when voices feel differently about the same event.',
    emptyVoices:'Add memories with different names to see individual fingerprints.',
    emptyFeed:'No memories yet.\nBe the first voice in this archive.',
    emptyTimeline:'No entries yet.',
    agreed:'Agreed',mixed:'Mixed',split:'Split',
    voiceEntries: n=>`${n} entr${n===1?'y':'ies'}`,
    anonName:'Anonymous',
    timelineTitle:'Collective timeline',
    clearConfirm:'Delete all entries? This cannot be undone.',
    feelLabels:{
      gioia:'Joy',tristezza:'Sadness',rabbia:'Rage',paura:'Fear',
      nostalgia:'Nostalgia',amore:'Love',malinconia:'Melancholy',
      serenità:'Serenity',sorpresa:'Surprise',ansia:'Anxiety',
      gratitudine:'Gratitude',vergogna:'Shame',orgoglio:'Pride',
      noia:'Boredom',curiosità:'Curiosity',
    },
    fmtDate:d=>d.toLocaleDateString('en-GB',{day:'numeric',month:'short'}),
    fmtDateFull:d=>d.toLocaleDateString('en-GB',{day:'numeric',month:'long',year:'numeric'}),
  },
  it:{
    code:'it',label:'IT',name:'Italiano',
    wordmark:'STRATA',tagline:'archivio emotivo collettivo',
    community:'Nome della comunità',
    members:n=>`${n} voce${n===1?'':'i'}`,
    inputTitle:'Aggiungi un ricordo',
    voiceLbl:'Il tuo nome o alias',
    anonLbl:'Anonimo',
    eventLbl:'Evento / tema',
    feelLbl:'Sentimento',
    contentLbl:'Cosa hai sentito',
    contentPh:'Descrivi la tua esperienza emotiva\u2026',
    eventPh:'es. La Chiusura, Il Primo Giorno\u2026',
    voicePh:'Nome o alias\u2026',
    addBtn:'Aggiungi all\'archivio',
    feedTitle:'Feed dell\'archivio',
    themeLight:'\u2014 CHIARO \u2014',themeDark:'\u2014 SCURO \u2014',
    exportBtn:'Esporta',importBtn:'Importa',clearBtn:'Cancella tutto',
    tabConsensus:'Consenso',tabVoices:'Voci',tabTimeline:'Timeline',
    statEntries:'Voci totali',statEvents:'Eventi',statVoices:'Voci',statDominant:'Sentimento dominante',
    consensusTitle:'Mappa del consenso',divergTitle:'Divergenza emotiva',
    emptyConsensus:'Aggiungi ricordi per più eventi per vedere i pattern di consenso.',
    emptyDiverg:'La divergenza appare quando le voci sentono diversamente lo stesso evento.',
    emptyVoices:'Aggiungi ricordi con nomi diversi per vedere le impronte individuali.',
    emptyFeed:'Nessun ricordo ancora.\nSii la prima voce in questo archivio.',
    emptyTimeline:'Nessuna voce ancora.',
    agreed:'Accordo',mixed:'Misto',split:'Diviso',
    voiceEntries:n=>`${n} voce${n===1?'':'i'}`,
    anonName:'Anonimo',
    timelineTitle:'Timeline collettiva',
    clearConfirm:'Eliminare tutte le voci? Non si può annullare.',
    feelLabels:{
      gioia:'Gioia',tristezza:'Tristezza',rabbia:'Rabbia',paura:'Paura',
      nostalgia:'Nostalgia',amore:'Amore',malinconia:'Malinconia',
      serenità:'Serenità',sorpresa:'Sorpresa',ansia:'Ansia',
      gratitudine:'Gratitudine',vergogna:'Vergogna',orgoglio:'Orgoglio',
      noia:'Noia',curiosità:'Curiosità',
    },
    fmtDate:d=>d.toLocaleDateString('it-IT',{day:'numeric',month:'short'}),
    fmtDateFull:d=>d.toLocaleDateString('it-IT',{day:'numeric',month:'long',year:'numeric'}),
  },
  es:{
    code:'es',label:'ES',name:'Español',
    wordmark:'STRATA',tagline:'archivo emocional colectivo',
    community:'Nombre de la comunidad',
    members:n=>`${n} voz${n===1?'':'es'}`,
    inputTitle:'Añadir un recuerdo',
    voiceLbl:'Tu nombre o alias',
    anonLbl:'Anónimo',
    eventLbl:'Evento / tema',
    feelLbl:'Sentimiento',
    contentLbl:'Lo que sentiste',
    contentPh:'Describe tu experiencia emocional\u2026',
    eventPh:'p.ej. El Cierre, El Primer Día\u2026',
    voicePh:'Nombre o alias\u2026',
    addBtn:'Añadir al archivo',
    feedTitle:'Feed del archivo',
    themeLight:'\u2014 CLARO \u2014',themeDark:'\u2014 OSCURO \u2014',
    exportBtn:'Exportar',importBtn:'Importar',clearBtn:'Borrar todo',
    tabConsensus:'Consenso',tabVoices:'Voces',tabTimeline:'Línea de tiempo',
    statEntries:'Entradas totales',statEvents:'Eventos',statVoices:'Voces',statDominant:'Sentimiento dominante',
    consensusTitle:'Mapa de consenso',divergTitle:'Divergencia emocional',
    emptyConsensus:'Añade recuerdos de varios eventos para ver patrones de consenso.',
    emptyDiverg:'La divergencia aparece cuando las voces sienten diferente sobre el mismo evento.',
    emptyVoices:'Añade recuerdos con nombres distintos para ver huellas individuales.',
    emptyFeed:'Sin recuerdos aún.\nSé la primera voz en este archivo.',
    emptyTimeline:'Sin entradas aún.',
    agreed:'Acuerdo',mixed:'Mixto',split:'Dividido',
    voiceEntries:n=>`${n} entrada${n===1?'':'s'}`,
    anonName:'Anónimo',
    timelineTitle:'Línea de tiempo colectiva',
    clearConfirm:'¿Eliminar todas las entradas? No se puede deshacer.',
    feelLabels:{
      gioia:'Alegría',tristezza:'Tristeza',rabbia:'Rabia',paura:'Miedo',
      nostalgia:'Nostalgia',amore:'Amor',malinconia:'Melancolía',
      serenità:'Serenidad',sorpresa:'Sorpresa',ansia:'Ansiedad',
      gratitudine:'Gratitud',vergogna:'Vergüenza',orgoglio:'Orgullo',
      noia:'Aburrimiento',curiosità:'Curiosidad',
    },
    fmtDate:d=>d.toLocaleDateString('es-ES',{day:'numeric',month:'short'}),
    fmtDateFull:d=>d.toLocaleDateString('es-ES',{day:'numeric',month:'long',year:'numeric'}),
  },
  zh:{
    code:'zh',label:'中',name:'中文',
    wordmark:'STRATA',tagline:'集体情感档案',
    community:'社区名称',
    members:n=>`${n} 个声音`,
    inputTitle:'添加一条记忆',
    voiceLbl:'你的名字或别名',
    anonLbl:'匿名',
    eventLbl:'事件 / 主题',
    feelLbl:'情感',
    contentLbl:'你的感受',
    contentPh:'描述你的情感体验……',
    eventPh:'例如：封城、第一天、那场风暴……',
    voicePh:'名字或别名……',
    addBtn:'添加到档案',
    feedTitle:'档案动态',
    themeLight:'— 浅色 —',themeDark:'— 深色 —',
    exportBtn:'导出',importBtn:'导入',clearBtn:'清除全部',
    tabConsensus:'共识',tabVoices:'声音',tabTimeline:'时间线',
    statEntries:'总条目',statEvents:'事件数',statVoices:'声音数',statDominant:'主导情感',
    consensusTitle:'共识地图',divergTitle:'情感分歧',
    emptyConsensus:'为多个事件添加记忆以查看共识模式。',
    emptyDiverg:'当不同声音对同一事件有不同感受时，分歧就会出现。',
    emptyVoices:'用不同名字添加记忆以查看个人情感指纹。',
    emptyFeed:'暂无记忆。\n成为这个档案中的第一个声音。',
    emptyTimeline:'暂无条目。',
    agreed:'一致',mixed:'混合',split:'分歧',
    voiceEntries:n=>`${n} 条`,
    anonName:'匿名',
    timelineTitle:'集体时间线',
    clearConfirm:'删除所有条目？此操作无法撤销。',
    feelLabels:{
      gioia:'喜悦',tristezza:'悲伤',rabbia:'愤怒',paura:'恐惧',
      nostalgia:'怀旧',amore:'爱',malinconia:'忧郁',
      serenità:'宁静',sorpresa:'惊讶',ansia:'焦虑',
      gratitudine:'感恩',vergogna:'羞耻',orgoglio:'自豪',
      noia:'无聊',curiosità:'好奇',
    },
    fmtDate:d=>d.toLocaleDateString('zh-CN',{month:'short',day:'numeric'}),
    fmtDateFull:d=>d.toLocaleDateString('zh-CN',{year:'numeric',month:'long',day:'numeric'}),
  },
};
const LANG_ORDER=['en','it','es','zh'];

// ══ Feelings & Themes ════════════════════════════════════════
const FEELING_KEYS=['gioia','tristezza','rabbia','paura','nostalgia','amore','malinconia','serenità','sorpresa','ansia','gratitudine','vergogna','orgoglio','noia','curiosità'];
const FEELING_COLORS={gioia:'#f59e0b',tristezza:'#6ea8fe',rabbia:'#f87171',paura:'#a78bfa',nostalgia:'#fb923c',amore:'#f472b6',malinconia:'#818cf8',serenità:'#34d399',sorpresa:'#fcd34d',ansia:'#94a3b8',gratitudine:'#6ee7b7',vergogna:'#fca5a5',orgoglio:'#c084fc',noia:'#6b7280',curiosità:'#67e8f9'};

const THEMES=[
  {id:'civic',    label:'Civic',      bg:'#f4f6f8',acc:'#2858b8',dark:false},
  {id:'town',     label:'Town',       bg:'#f5f2ec',acc:'#8b5e1a',dark:false},
  {id:'meadow',   label:'Meadow',     bg:'#eef4f0',acc:'#2a7a3a',dark:false},
  {id:'terracotta',label:'Terracotta',bg:'#f8f0ec',acc:'#b84828',dark:false},
  {id:'linen',    label:'Linen',      bg:'#fafaf5',acc:'#6a5a30',dark:false},
  {id:'sky',      label:'Sky',        bg:'#eef4fb',acc:'#1068b8',dark:false},
  {id:'chalk',    label:'Chalk',      bg:'#f8f8f4',acc:'#383090',dark:false},
  {id:'blossom',  label:'Blossom',    bg:'#fdf2f6',acc:'#a82850',dark:false},
  {id:'pearl',    label:'Pearl',      bg:'#f4f4f0',acc:'#506870',dark:false},
  {id:'sand',     label:'Sand',       bg:'#f8f4ec',acc:'#c87830',dark:false},
  {id:'night',    label:'Night',      bg:'#0c0e10',acc:'#5888e8',dark:true},
  {id:'slate',    label:'Slate',      bg:'#101418',acc:'#78a8c8',dark:true},
  {id:'ember',    label:'Ember',      bg:'#100c08',acc:'#e08038',dark:true},
  {id:'obsidian', label:'Obsidian',   bg:'#0c0d0e',acc:'#68c8a8',dark:true},
  {id:'void',     label:'Void',       bg:'#000000',acc:'#b8b8b8',dark:true},
  {id:'crimson',  label:'Crimson',    bg:'#100608',acc:'#e05868',dark:true},
  {id:'amethyst', label:'Amethyst',   bg:'#080610',acc:'#b880f8',dark:true},
  {id:'forest',   label:'Forest',     bg:'#060e08',acc:'#58d878',dark:true},
  {id:'ocean',    label:'Ocean',      bg:'#040c10',acc:'#40c8e0',dark:true},
  {id:'candle',   label:'Candle',     bg:'#100c06',acc:'#f8d848',dark:true},
];

// Voice colors (for avatar dots)
const VOICE_PALETTE=['#6ea8fe','#f472b6','#34d399','#f59e0b','#a78bfa','#fb923c','#67e8f9','#fca5a5','#c084fc','#6ee7b7','#f87171','#818cf8'];

// ══ State ══════════════════════════════════════════════════════
const SK='strata-v1';
let entries=[];
let currentLang='en';
let currentTheme='civic';
let activeTab='consensus';
let themePanelOpen=false;
let langPanelOpen=false;

// ══ Utils ══════════════════════════════════════════════════════
const uid=()=>Math.random().toString(36).slice(2,10);
const esc=s=>String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const L=()=>LANGS[currentLang]||LANGS.en;
const fl=k=>L().feelLabels[k]||k;
const col=k=>FEELING_COLORS[k]||'#888';

function voiceColor(name){
  if(!name)return VOICE_PALETTE[0];
  let h=0;for(let i=0;i<name.length;i++)h=(h*31+name.charCodeAt(i))&0xffff;
  return VOICE_PALETTE[h%VOICE_PALETTE.length];
}
function voiceInitial(name){return(name||'?')[0].toUpperCase()}

// ══ Persistence ════════════════════════════════════════════════
function load(){
  try{const r=localStorage.getItem(SK);if(r)entries=JSON.parse(r)}catch(e){}
  const t=localStorage.getItem('str-theme'),g=localStorage.getItem('str-lang');
  if(t&&THEMES.find(x=>x.id===t))currentTheme=t;
  if(g&&LANGS[g])currentLang=g;
  const cn=localStorage.getItem('str-community');
  if(cn)document.getElementById('community-name').value=cn;
  applyTheme(currentTheme,false);
  applyLang(currentLang,false);
}
function save(){try{localStorage.setItem(SK,JSON.stringify(entries))}catch(e){}}
function saveCommunity(){
  const v=document.getElementById('community-name').value.trim();
  if(v)localStorage.setItem('str-community',v);
}

// ══ Export / Import ═════════════════════════════════════════════
function exportArchive(){
  const data={community:document.getElementById('community-name').value,entries,exported:new Date().toISOString()};
  const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download=`strata-${Date.now()}.json`;
  a.click();URL.revokeObjectURL(a.href);
}
function importArchive(){
  const inp=document.createElement('input');
  inp.type='file';inp.accept='.json';
  inp.onchange=e=>{
    const file=e.target.files[0];if(!file)return;
    const reader=new FileReader();
    reader.onload=ev=>{
      try{
        const data=JSON.parse(ev.target.result);
        if(Array.isArray(data.entries)){
          entries=[...entries,...data.entries];
          save();
          if(data.community)document.getElementById('community-name').value=data.community;
          render();
        }
      }catch(err){alert('Invalid archive file.')}
    };
    reader.readAsText(file);
  };
  inp.click();
}
function clearArchive(){
  if(!confirm(L().clearConfirm))return;
  entries=[];save();render();
}

// ══ Theme ══════════════════════════════════════════════════════
function applyTheme(id,persist=true){
  currentTheme=id;
  document.documentElement.setAttribute('data-theme',id);
  if(persist)localStorage.setItem('str-theme',id);
  document.querySelectorAll('.th-dot').forEach(d=>d.classList.toggle('active',d.dataset.theme===id));
  const th=THEMES.find(t=>t.id===id);
  const btn=document.getElementById('btn-theme');
  if(btn&&th)btn.innerHTML=`<span style="display:inline-block;width:11px;height:11px;background:${th.acc};border-radius:3px;flex-shrink:0"></span>${th.label}`;
}
function buildThemePanel(){
  const l=L();
  const sw=g=>g.map(t=>`<div class="th-dot${t.id===currentTheme?' active':''}" data-theme="${t.id}" title="${t.label}" style="background:${t.bg};outline:2px solid ${t.acc}44" onclick="applyTheme('${t.id}')"></div>`).join('');
  return `<div class="p-lbl">${l.themeLight}</div><div class="swatch-row">${sw(THEMES.filter(t=>!t.dark))}</div><div class="p-lbl">${l.themeDark}</div><div class="swatch-row">${sw(THEMES.filter(t=>t.dark))}</div>`;
}
function toggleThemePanel(){
  themePanelOpen=!themePanelOpen;
  if(langPanelOpen){langPanelOpen=false;document.getElementById('lang-panel')?.classList.remove('open')}
  const p=document.getElementById('theme-panel');
  if(p){p.innerHTML=themePanelOpen?buildThemePanel():'';p.classList.toggle('open',themePanelOpen)}
}

// ══ Language ═══════════════════════════════════════════════════
function applyLang(code,persist=true){
  currentLang=code;
  document.documentElement.lang=code;
  if(persist)localStorage.setItem('str-lang',code);
  document.querySelectorAll('.lang-opt').forEach(b=>b.classList.toggle('active',b.dataset.lang===code));
  renderStaticText();render();
}
function buildLangPanel(){
  return LANG_ORDER.map(code=>{const lg=LANGS[code];return`<button class="lang-opt${code===currentLang?' active':''}" data-lang="${code}" onclick="applyLang('${code}');toggleLangPanel()">${lg.label}<span class="ln">${lg.name}</span></button>`}).join('');
}
function toggleLangPanel(){
  langPanelOpen=!langPanelOpen;
  if(themePanelOpen){themePanelOpen=false;document.getElementById('theme-panel')?.classList.remove('open')}
  const p=document.getElementById('lang-panel');
  if(p){p.innerHTML=langPanelOpen?buildLangPanel():'';p.classList.toggle('open',langPanelOpen)}
}
document.addEventListener('click',e=>{
  const tw=document.getElementById('theme-wrap');
  const lw=document.getElementById('lang-wrap');
  if(themePanelOpen&&tw&&!tw.contains(e.target)){themePanelOpen=false;document.getElementById('theme-panel')?.classList.remove('open')}
  if(langPanelOpen&&lw&&!lw.contains(e.target)){langPanelOpen=false;document.getElementById('lang-panel')?.classList.remove('open')}
});

// ══ Static text ════════════════════════════════════════════════
function renderStaticText(){
  const l=L();
  const s=(id,t)=>{const e=document.getElementById(id);if(e)e.textContent=t};
  const p=(id,t)=>{const e=document.getElementById(id);if(e)e.placeholder=t};
  const h=(id,html)=>{const e=document.getElementById(id);if(e)e.innerHTML=html};

  s('wordmark',l.wordmark);s('tagline',l.tagline);
  p('community-name',l.community);
  s('input-title',l.inputTitle);
  s('lbl-voice',l.voiceLbl);s('lbl-event',l.eventLbl);
  s('lbl-feel',l.feelLbl);s('lbl-content',l.contentLbl);
  p('f-voice',l.voicePh);p('f-event',l.eventPh);p('f-content',l.contentPh);
  s('btn-add',l.addBtn);
  s('feed-title',l.feedTitle);
  s('btn-export',l.exportBtn);s('btn-import',l.importBtn);s('btn-clear',l.clearBtn);
  // tabs — update only the label text node, preserve badge spans
  const updateTabLabel = (id, txt) => {
    const el = document.getElementById(id);
    if (!el) return;
    // replace first text node only, leave child spans intact
    const nodes = [...el.childNodes].filter(n => n.nodeType === 3);
    if (nodes.length) nodes[0].textContent = txt + ' ';
    else el.insertBefore(document.createTextNode(txt + ' '), el.firstChild);
  };
  updateTabLabel('tab-consensus', l.tabConsensus);
  updateTabLabel('tab-voices',    l.tabVoices);
  updateTabLabel('tab-timeline',  l.tabTimeline);
  s('stat-entries-lbl',l.statEntries);
  s('stat-events-lbl',l.statEvents);
  s('stat-voices-lbl',l.statVoices);
  s('stat-dominant-lbl',l.statDominant);

  // feeling select
  const fs=document.getElementById('f-feeling');
  if(fs){const cur=fs.value;fs.innerHTML=FEELING_KEYS.map(k=>`<option value="${k}">${fl(k)}</option>`).join('');fs.value=cur||'gioia';fs.style.color=col(fs.value)}

  // anon label
  const al=document.getElementById('lbl-anon');if(al)al.textContent=l.anonLbl;

  // lang btn
  const lb=document.getElementById('btn-lang');if(lb)lb.textContent=l.label;

  // theme btn
  const th=THEMES.find(t=>t.id===currentTheme);
  const tb=document.getElementById('btn-theme');
  if(tb&&th)tb.innerHTML=`<span style="display:inline-block;width:11px;height:11px;background:${th.acc};border-radius:3px;flex-shrink:0"></span>${th.label}`;
}

// ══ Form ═══════════════════════════════════════════════════════
function setupForm(){
  const fs=document.getElementById('f-feeling');
  fs.onchange=()=>fs.style.color=col(fs.value);
  fs.style.color=col(fs.value||'gioia');

  const anon=document.getElementById('anon-check');
  const voiceInp=document.getElementById('f-voice');
  anon.onchange=()=>{
    voiceInp.disabled=anon.checked;
    voiceInp.style.opacity=anon.checked?'.4':'1';
  };

  const check=()=>{
    const ev=document.getElementById('f-event').value.trim();
    const ct=document.getElementById('f-content').value.trim();
    document.getElementById('btn-add').disabled=!ev||!ct;
  };
  document.getElementById('f-event').oninput=check;
  document.getElementById('f-content').oninput=check;
  document.getElementById('btn-add').disabled=true;
}

function addEntry(){
  const l=L();
  const anon=document.getElementById('anon-check').checked;
  const voiceRaw=document.getElementById('f-voice').value.trim();
  const voice=anon?l.anonName:(voiceRaw||l.anonName);
  const event=document.getElementById('f-event').value.trim();
  const feeling=document.getElementById('f-feeling').value;
  const content=document.getElementById('f-content').value.trim();
  if(!event||!content)return;

  entries.unshift({id:uid(),voice,event,feeling,content,ts:Date.now(),date:today()});
  save();

  document.getElementById('f-event').value='';
  document.getElementById('f-content').value='';
  document.getElementById('btn-add').disabled=true;
  render();
}

function today(){
  const d=new Date();
  return`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

// ══ Master render ═══════════════════════════════════════════════
function render(){
  renderCommunityBar();
  renderFeed();
  renderStats();
  renderActiveTab();
}

// ══ Community bar ═══════════════════════════════════════════════
function renderCommunityBar(){
  const l=L();
  const voices=new Set(entries.map(e=>e.voice)).size;
  document.getElementById('community-members').textContent=l.members(voices);
}

// ══ Feed ════════════════════════════════════════════════════════
function renderFeed(){
  const l=L();
  const feed=document.getElementById('feed');
  const cnt=document.getElementById('feed-count');
  if(cnt)cnt.textContent=entries.length?`(${entries.length})`:'';

  if(!entries.length){
    feed.innerHTML=`<div id="feed-empty">${esc(l.emptyFeed).replace('\n','<br>')}</div>`;
    return;
  }
  feed.innerHTML=entries.slice(0,50).map(e=>{
    const c=col(e.feeling);
    const vc=voiceColor(e.voice);
    return`<div class="feed-item fade-in">
      <div class="feed-item-top">
        <span class="feed-event">${esc(e.event)}</span>
        <span class="feed-pill" style="background:${c}18;color:${c}">${fl(e.feeling)}</span>
        <span class="feed-voice" style="color:${vc}">${esc(e.voice)}</span>
      </div>
      <div class="feed-content">${esc(e.content)}</div>
    </div>`;
  }).join('');
}

// ══ Stats ═══════════════════════════════════════════════════════
function renderStats(){
  const l=L();
  const voices=new Set(entries.map(e=>e.voice)).size;
  const events=new Set(entries.map(e=>e.event)).size;
  document.getElementById('stat-entries-val').textContent=entries.length;
  document.getElementById('stat-events-val').textContent=events;
  document.getElementById('stat-voices-val').textContent=voices;

  if(entries.length){
    const freq={};entries.forEach(e=>freq[e.feeling]=(freq[e.feeling]||0)+1);
    const top=Object.entries(freq).sort((a,b)=>b[1]-a[1])[0][0];
    document.getElementById('stat-dominant-val').textContent=fl(top);
    document.getElementById('stat-dominant-val').style.color=col(top);
  }else{
    document.getElementById('stat-dominant-val').textContent='—';
    document.getElementById('stat-dominant-val').style.color='';
  }

  // update tab badges
  document.getElementById('tab-voices-badge').textContent=voices;
  document.getElementById('tab-events-badge').textContent=events;
}

// ══ Tabs ═══════════════════════════════════════════════════════
function switchTab(tab){
  activeTab=tab;
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.toggle('active',b.dataset.tab===tab));
  document.querySelectorAll('.tab-pane').forEach(p=>p.classList.toggle('active',p.id==='pane-'+tab));
  renderActiveTab();
}

function renderActiveTab(){
  if(activeTab==='consensus')renderConsensusTab();
  else if(activeTab==='voices')renderVoicesTab();
  else renderTimelineTab();
}

// ══ Consensus tab ═══════════════════════════════════════════════
function renderConsensusTab(){
  const l=L();

  // Group by event
  const eventMap={};
  entries.forEach(e=>{
    if(!eventMap[e.event])eventMap[e.event]={voices:{},feelings:{}};
    eventMap[e.event].voices[e.voice]=(eventMap[e.event].voices[e.voice]||[]);
    eventMap[e.event].voices[e.voice].push(e.feeling);
    eventMap[e.event].feelings[e.feeling]=(eventMap[e.event].feelings[e.feeling]||0)+1;
  });
  const events=Object.entries(eventMap).sort((a,b)=>Object.keys(b[1].voices).length-Object.keys(a[1].voices).length);

  // Consensus map
  const consEl=document.getElementById('consensus-map');
  if(!events.length){consEl.innerHTML=`<div class="empty-state">${l.emptyConsensus}</div>`;
  }else{
    consEl.innerHTML=events.map(([event,data])=>{
      const voiceKeys=Object.keys(data.voices);
      const topFeel=Object.entries(data.feelings).sort((a,b)=>b[1]-a[1]);
      const totalVotes=Object.values(data.feelings).reduce((a,b)=>a+b,0);
      const topN=topFeel[0]?.[1]||0;
      const consensusRatio=totalVotes>0?topN/totalVotes:0;
      const level=consensusRatio>=.75?'agreed':consensusRatio>=.5?'mixed':'split';
      const levelColor=level==='agreed'?'#34d399':level==='mixed'?'#f59e0b':'#f87171';
      const levelLabel=l[level];

      const dots=voiceKeys.map(v=>{
        const feels=data.voices[v];
        const domFeel=feels.sort((a,b)=>feels.filter(x=>x===b).length-feels.filter(x=>x===a).length)[0];
        const vc=voiceColor(v);
        return`<div class="voice-dot" style="background:${vc}" title="${esc(v)}: ${fl(domFeel)}">${voiceInitial(v)}</div>`;
      }).join('');

      return`<div class="event-row">
        <div class="event-name" title="${esc(event)}">${esc(event)}</div>
        <div class="event-voices">${dots}</div>
        <span class="event-consensus" style="background:${levelColor}18;color:${levelColor};border:1px solid ${levelColor}44">${levelLabel}</span>
      </div>`;
    }).join('');
  }

  // Divergence
  const divEl=document.getElementById('divergence-map');
  const multiVoiceEvents=events.filter(([_,d])=>Object.keys(d.voices).length>=2);
  if(!multiVoiceEvents.length){divEl.innerHTML=`<div class="empty-state">${l.emptyDiverg}</div>`;
  }else{
    divEl.innerHTML=multiVoiceEvents.map(([event,data])=>{
      const total=Object.values(data.feelings).reduce((a,b)=>a+b,0);
      const segs=Object.entries(data.feelings).sort((a,b)=>b[1]-a[1]).map(([k,n])=>{
        const pct=Math.round(n/total*100);
        return`<div class="diverg-seg" style="flex:${n};background:${col(k)};opacity:.8" title="${fl(k)}: ${n}×"></div>`;
      }).join('');
      return`<div class="diverg-row">
        <div class="diverg-event">${esc(event)}</div>
        <div class="diverg-bar">${segs}</div>
      </div>`;
    }).join('');
  }
}

// ══ Voices tab ══════════════════════════════════════════════════
function renderVoicesTab(){
  const l=L();
  const grid=document.getElementById('voices-grid');
  const voiceMap={};
  entries.forEach(e=>{
    if(!voiceMap[e.voice])voiceMap[e.voice]={n:0,feelings:{}};
    voiceMap[e.voice].n++;
    voiceMap[e.voice].feelings[e.feeling]=(voiceMap[e.voice].feelings[e.feeling]||0)+1;
  });
  const voices=Object.entries(voiceMap).sort((a,b)=>b[1].n-a[1].n);

  if(!voices.length){grid.innerHTML=`<div class="empty-state" style="grid-column:1/-1">${l.emptyVoices}</div>`;return}

  grid.innerHTML=voices.map(([name,data])=>{
    const vc=voiceColor(name);
    const topFeels=Object.entries(data.feelings).sort((a,b)=>b[1]-a[1]).slice(0,4);
    const maxN=topFeels[0]?.[1]||1;
    const bars=topFeels.map(([k,n])=>`<div class="vmb-row">
      <div class="vmb-label">${fl(k)}</div>
      <div class="vmb-track"><div class="vmb-fill" style="width:${Math.round(n/maxN*100)}%;background:${col(k)}"></div></div>
    </div>`).join('');

    return`<div class="voice-card fade-in">
      <div class="voice-header">
        <div class="voice-avatar" style="background:${vc}">${voiceInitial(name)}</div>
        <div>
          <div class="voice-name">${esc(name)}</div>
          <div class="voice-count">${l.voiceEntries(data.n)}</div>
        </div>
      </div>
      <div class="voice-mini-bars">${bars}</div>
    </div>`;
  }).join('');
}

// ══ Timeline tab ════════════════════════════════════════════════
function renderTimelineTab(){
  const l=L();
  const list=document.getElementById('timeline-list');
  if(!entries.length){list.innerHTML=`<div class="empty-state">${l.emptyTimeline}</div>`;return}

  // Group by date
  const byDate={};
  entries.forEach(e=>{byDate[e.date]=byDate[e.date]||[];byDate[e.date].push(e)});
  const dates=Object.keys(byDate).sort().reverse();

  list.innerHTML=dates.map(date=>{
    const d=new Date(date+'T12:00:00');
    const items=byDate[date].map(e=>{
      const c=col(e.feeling);
      const vc=voiceColor(e.voice);
      return`<div class="tl-entry">
        <div class="tl-left">
          <div class="tl-feel-dot" style="background:${c}"></div>
        </div>
        <div class="tl-body">
          <div class="tl-meta">
            <span class="tl-event">${esc(e.event)}</span>
            <span class="tl-voice" style="color:${vc}">${esc(e.voice)}</span>
            <span class="tl-feel-lbl" style="color:${c}">${fl(e.feeling)}</span>
          </div>
          <div class="tl-content">${esc(e.content)}</div>
        </div>
      </div>`;
    }).join('');
    return`<div class="tl-group">
      <div class="tl-date">${l.fmtDateFull(d)}</div>
      <div class="tl-entries">${items}</div>
    </div>`;
  }).join('');
}

// ══ Mobile ══════════════════════════════════════════════════════
function toggleSidebar(){
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('sb-backdrop').classList.toggle('open');
}
function closeSidebar(){
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sb-backdrop').classList.remove('open');
}

// ══ Boot ══════════════════════════════════════════════════════
load();
setupForm();
renderStaticText();
render();
// set initial active tab
document.querySelector('[data-tab="consensus"]')?.classList.add('active');
document.getElementById('pane-consensus')?.classList.add('active');