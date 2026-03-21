/* ═══════════════════════════════════════════════════════════
   PHANTOM ARCHIVE — app.js
   Cases, i18n (EN/IT/ES/ZH), themes, full game logic
   ═══════════════════════════════════════════════════════════ */

// ══ Feeling data ════════════════════════════════════════════
const FEELING_COLORS = {
  gioia:'#f59e0b', tristezza:'#6ea8fe', rabbia:'#f87171', paura:'#a78bfa',
  nostalgia:'#fb923c', amore:'#f472b6', malinconia:'#818cf8', serenità:'#34d399',
  sorpresa:'#fcd34d', ansia:'#94a3b8', gratitudine:'#6ee7b7', vergogna:'#fca5a5',
  orgoglio:'#c084fc', noia:'#6b7280', curiosità:'#67e8f9',
};

// ══ i18n ════════════════════════════════════════════════════
const LANGS = {
  en: {
    code:'en', label:'EN', name:'English',
    emblem:        'MNHEME INVESTIGATIVE DIVISION · CASE ARCHIVE UNIT',
    appSub:        'an emotional memory investigation',
    introDesc:     `An unknown subject's emotional memory archive has been recovered.<br>
                    <strong>You have 10 questions.</strong> Interrogate the archive through the Brain.<br>
                    Each answer unlocks a fragment. Then name the phantom.`,
    lmTitle:       'LM STUDIO CONNECTION',
    lmModelPh:     'model name (blank = auto)',
    lmSave:        'SAVE',
    themeLabel:    'THEME',
    themeLight:    '— LIGHT —',
    themeDark:     '— DARK —',
    memFrags:      n => `${n} memory fragments`,
    caseLabel:     'CASE',
    questLeft:     (n,m) => `${n} / ${m} QUESTIONS`,
    closeCase:     'CLOSE CASE',
    back:          '← BACK',
    archiveTitle:  'EMOTIONAL ARCHIVE — SUBJECT',
    archiveAnon:   '[IDENTITY WITHHELD]',
    archiveStats:  (u,t) => `${u} of ${t} fragments unlocked`,
    classified:    '— CLASSIFIED —',
    systemMsg:     (max, every) =>
      `You have access to a partial emotional memory archive. The subject's identity has been redacted.<br><br>
       You have <strong>${max} questions</strong>. Ask what you need. When ready, close the case and file your verdict.<br><br>
       Every ${every} questions you ask will unlock another memory fragment.`,
    investigator:  'INVESTIGATOR',
    brainLabel:    'PHANTOM ARCHIVE · BRAIN',
    unlockNotice:  frag => `▶ ARCHIVE FRAGMENT UNLOCKED — ${frag}`,
    askPh:         'Type your question and press Enter…',
    ask:           'ASK',
    conclude:      'CONCLUDE',
    verdictTitle:  'FILE YOUR VERDICT',
    verdictSub:    'WHO IS THE PHANTOM?',
    verdictNameL:  'SUBJECT IDENTITY — name the character',
    verdictProfileL:'PSYCHOLOGICAL PROFILE — what happened to them?',
    verdictNamePh: 'Your best guess…',
    verdictProfPh: 'Describe the arc you\'ve reconstructed from the archive. What defines this character? What was their wound?',
    submitVerdict: 'SUBMIT VERDICT',
    caseFile:      'CASE FILE',
    trueIdentity:  'TRUE IDENTITY',
    officialProf:  'OFFICIAL PROFILE',
    yourVerdict:   'YOUR VERDICT',
    aiEval:        'AI EVALUATION',
    noProfile:     '(no profile filed)',
    scoreConfirmed:  (q,m) => `IDENTITY CONFIRMED · ${q} of ${m} questions used`,
    scoreUnconfirmed:(q,m) => `IDENTITY UNCONFIRMED · ${q} of ${m} questions used`,
    playAgain:     'OPEN NEW CASE',
    feelLabels: {
      gioia:'Joy', tristezza:'Sadness', rabbia:'Rage', paura:'Fear',
      nostalgia:'Nostalgia', amore:'Love', malinconia:'Melancholy', serenità:'Serenity',
      sorpresa:'Surprise', ansia:'Anxiety', gratitudine:'Gratitude', vergogna:'Shame',
      orgoglio:'Pride', noia:'Boredom', curiosità:'Curiosity',
    },
    sysPromptInstr: 'Reply in English.',
    daysAgo: d => {
      if (d<7)   return `${d}d ago`;
      if (d<30)  return `${Math.round(d/7)}w ago`;
      if (d<365) return `${Math.round(d/30)}mo ago`;
      return `${Math.round(d/365)}y ago`;
    },
  },

  it: {
    code:'it', label:'IT', name:'Italiano',
    emblem:        'DIVISIONE INVESTIGATIVA MNHEME · UNITÀ ARCHIVI',
    appSub:        'un\'indagine sulla memoria emotiva',
    introDesc:     `L'archivio di memoria emotiva di un soggetto sconosciuto è stato recuperato.<br>
                    <strong>Hai 10 domande.</strong> Interroga l'archivio attraverso il Cervello.<br>
                    Ogni risposta sblocca un frammento. Poi nomina il fantasma.`,
    lmTitle:       'CONNESSIONE LM STUDIO',
    lmModelPh:     'nome modello (vuoto = automatico)',
    lmSave:        'SALVA',
    themeLabel:    'TEMA',
    themeLight:    '— CHIARO —',
    themeDark:     '— SCURO —',
    memFrags:      n => `${n} frammenti di memoria`,
    caseLabel:     'CASO',
    questLeft:     (n,m) => `${n} / ${m} DOMANDE`,
    closeCase:     'CHIUDI IL CASO',
    back:          '← INDIETRO',
    archiveTitle:  'ARCHIVIO EMOTIVO — SOGGETTO',
    archiveAnon:   '[IDENTITÀ OSCURATA]',
    archiveStats:  (u,t) => `${u} di ${t} frammenti sbloccati`,
    classified:    '— CLASSIFICATO —',
    systemMsg:     (max, every) =>
      `Hai accesso a un archivio parziale di memorie emotive. L'identità del soggetto è stata oscurata.<br><br>
       Hai <strong>${max} domande</strong>. Chiedi ciò che ti serve. Quando sei pronto, chiudi il caso e registra il tuo verdetto.<br><br>
       Ogni ${every} domande sblocchi un nuovo frammento dell'archivio.`,
    investigator:  'INVESTIGATORE',
    brainLabel:    'ARCHIVIO FANTASMA · CERVELLO',
    unlockNotice:  frag => `▶ FRAMMENTO SBLOCCATO — ${frag}`,
    askPh:         'Scrivi la tua domanda e premi Invio…',
    ask:           'CHIEDI',
    conclude:      'CONCLUDI',
    verdictTitle:  'REGISTRA IL VERDETTO',
    verdictSub:    'CHI È IL FANTASMA?',
    verdictNameL:  'IDENTITÀ — nome il personaggio',
    verdictProfileL:'PROFILO PSICOLOGICO — cosa gli è successo?',
    verdictNamePh: 'La tua ipotesi migliore…',
    verdictProfPh: 'Descrivi l\'arco che hai ricostruito dall\'archivio. Cosa definisce questo personaggio? Qual era la sua ferita?',
    submitVerdict: 'INVIA IL VERDETTO',
    caseFile:      'FASCICOLO',
    trueIdentity:  'VERA IDENTITÀ',
    officialProf:  'PROFILO UFFICIALE',
    yourVerdict:   'IL TUO VERDETTO',
    aiEval:        'VALUTAZIONE AI',
    noProfile:     '(nessun profilo registrato)',
    scoreConfirmed:  (q,m) => `IDENTITÀ CONFERMATA · ${q} di ${m} domande usate`,
    scoreUnconfirmed:(q,m) => `IDENTITÀ NON CONFERMATA · ${q} di ${m} domande usate`,
    playAgain:     'APRI NUOVO CASO',
    feelLabels: {
      gioia:'Gioia', tristezza:'Tristezza', rabbia:'Rabbia', paura:'Paura',
      nostalgia:'Nostalgia', amore:'Amore', malinconia:'Malinconia', serenità:'Serenità',
      sorpresa:'Sorpresa', ansia:'Ansia', gratitudine:'Gratitudine', vergogna:'Vergogna',
      orgoglio:'Orgoglio', noia:'Noia', curiosità:'Curiosità',
    },
    sysPromptInstr: 'Rispondi in italiano.',
    daysAgo: d => {
      if (d<7)   return `${d}g fa`;
      if (d<30)  return `${Math.round(d/7)} sett. fa`;
      if (d<365) return `${Math.round(d/30)} mesi fa`;
      return `${Math.round(d/365)} anni fa`;
    },
  },

  es: {
    code:'es', label:'ES', name:'Español',
    emblem:        'DIVISIÓN INVESTIGATIVA MNHEME · UNIDAD DE ARCHIVOS',
    appSub:        'una investigación de memoria emocional',
    introDesc:     `Se ha recuperado el archivo de memoria emocional de un sujeto desconocido.<br>
                    <strong>Tienes 10 preguntas.</strong> Interroga el archivo a través de la Mente.<br>
                    Cada respuesta desbloquea un fragmento. Luego nombra al fantasma.`,
    lmTitle:       'CONEXIÓN LM STUDIO',
    lmModelPh:     'nombre del modelo (vacío = automático)',
    lmSave:        'GUARDAR',
    themeLabel:    'TEMA',
    themeLight:    '— CLARO —',
    themeDark:     '— OSCURO —',
    memFrags:      n => `${n} fragmentos de memoria`,
    caseLabel:     'CASO',
    questLeft:     (n,m) => `${n} / ${m} PREGUNTAS`,
    closeCase:     'CERRAR CASO',
    back:          '← VOLVER',
    archiveTitle:  'ARCHIVO EMOCIONAL — SUJETO',
    archiveAnon:   '[IDENTIDAD OCULTA]',
    archiveStats:  (u,t) => `${u} de ${t} fragmentos desbloqueados`,
    classified:    '— CLASIFICADO —',
    systemMsg:     (max, every) =>
      `Tienes acceso a un archivo parcial de memorias emocionales. La identidad del sujeto ha sido redactada.<br><br>
       Tienes <strong>${max} preguntas</strong>. Pregunta lo que necesites. Cuando estés listo, cierra el caso y presenta tu veredicto.<br><br>
       Cada ${every} preguntas desbloquearás otro fragmento del archivo.`,
    investigator:  'INVESTIGADOR',
    brainLabel:    'ARCHIVO FANTASMA · MENTE',
    unlockNotice:  frag => `▶ FRAGMENTO DESBLOQUEADO — ${frag}`,
    askPh:         'Escribe tu pregunta y presiona Enter…',
    ask:           'PREGUNTAR',
    conclude:      'CONCLUIR',
    verdictTitle:  'PRESENTA TU VEREDICTO',
    verdictSub:    '¿QUIÉN ES EL FANTASMA?',
    verdictNameL:  'IDENTIDAD — nombra al personaje',
    verdictProfileL:'PERFIL PSICOLÓGICO — ¿qué le ocurrió?',
    verdictNamePh: 'Tu mejor hipótesis…',
    verdictProfPh: 'Describe el arco que has reconstruido del archivo. ¿Qué define a este personaje? ¿Cuál fue su herida?',
    submitVerdict: 'ENVIAR VEREDICTO',
    caseFile:      'EXPEDIENTE',
    trueIdentity:  'VERDADERA IDENTIDAD',
    officialProf:  'PERFIL OFICIAL',
    yourVerdict:   'TU VEREDICTO',
    aiEval:        'EVALUACIÓN IA',
    noProfile:     '(sin perfil presentado)',
    scoreConfirmed:  (q,m) => `IDENTIDAD CONFIRMADA · ${q} de ${m} preguntas usadas`,
    scoreUnconfirmed:(q,m) => `IDENTIDAD NO CONFIRMADA · ${q} de ${m} preguntas usadas`,
    playAgain:     'ABRIR NUEVO CASO',
    feelLabels: {
      gioia:'Alegría', tristezza:'Tristeza', rabbia:'Rabia', paura:'Miedo',
      nostalgia:'Nostalgia', amore:'Amor', malinconia:'Melancolía', serenità:'Serenidad',
      sorpresa:'Sorpresa', ansia:'Ansiedad', gratitudine:'Gratitud', vergogna:'Vergüenza',
      orgoglio:'Orgullo', noia:'Aburrimiento', curiosità:'Curiosidad',
    },
    sysPromptInstr: 'Responde en español.',
    daysAgo: d => {
      if (d<7)   return `hace ${d}d`;
      if (d<30)  return `hace ${Math.round(d/7)} sem.`;
      if (d<365) return `hace ${Math.round(d/30)} meses`;
      return `hace ${Math.round(d/365)} años`;
    },
  },

  zh: {
    code:'zh', label:'中', name:'中文',
    emblem:        'MNHEME 调查部 · 案例档案单位',
    appSub:        '一场情感记忆调查',
    introDesc:     `一名未知人物的情感记忆档案已被找回。<br>
                    <strong>你有10个问题。</strong>通过大脑审讯档案。<br>
                    每次回答解锁一个片段。然后说出幽灵的名字。`,
    lmTitle:       'LM STUDIO 连接',
    lmModelPh:     '模型名称（留空=自动）',
    lmSave:        '保存',
    themeLabel:    '主题',
    themeLight:    '— 浅色 —',
    themeDark:     '— 深色 —',
    memFrags:      n => `${n} 条记忆片段`,
    caseLabel:     '案例',
    questLeft:     (n,m) => `${n} / ${m} 个问题`,
    closeCase:     '结案',
    back:          '← 返回',
    archiveTitle:  '情感档案 — 主体',
    archiveAnon:   '【身份已隐藏】',
    archiveStats:  (u,t) => `已解锁 ${u} / ${t} 个片段`,
    classified:    '— 机密 —',
    systemMsg:     (max, every) =>
      `你可以访问一个部分情感记忆档案。主体身份已被隐去。<br><br>
       你有 <strong>${max} 个问题</strong>。尽情提问。准备好后，结案并提交你的裁决。<br><br>
       每 ${every} 个问题解锁一个新的记忆片段。`,
    investigator:  '调查员',
    brainLabel:    '幽灵档案 · 大脑',
    unlockNotice:  frag => `▶ 片段已解锁 — ${frag}`,
    askPh:         '输入你的问题并按回车……',
    ask:           '提问',
    conclude:      '结案',
    verdictTitle:  '提交裁决',
    verdictSub:    '幽灵是谁？',
    verdictNameL:  '主体身份 — 说出角色名字',
    verdictProfileL:'心理画像 — 他/她经历了什么？',
    verdictNamePh: '你最好的猜测……',
    verdictProfPh: '描述你从档案中重建的弧线。这个角色的核心是什么？他们的伤口是什么？',
    submitVerdict: '提交裁决',
    caseFile:      '案件档案',
    trueIdentity:  '真实身份',
    officialProf:  '官方档案',
    yourVerdict:   '你的裁决',
    aiEval:        'AI 评估',
    noProfile:     '（未提交画像）',
    scoreConfirmed:  (q,m) => `身份已确认 · 使用了 ${q} / ${m} 个问题`,
    scoreUnconfirmed:(q,m) => `身份未确认 · 使用了 ${q} / ${m} 个问题`,
    playAgain:     '开启新案例',
    feelLabels: {
      gioia:'喜悦', tristezza:'悲伤', rabbia:'愤怒', paura:'恐惧',
      nostalgia:'怀旧', amore:'爱', malinconia:'忧郁', serenità:'宁静',
      sorpresa:'惊讶', ansia:'焦虑', gratitudine:'感恩', vergogna:'羞耻',
      orgoglio:'自豪', noia:'无聊', curiosità:'好奇',
    },
    sysPromptInstr: '请用中文回复。',
    daysAgo: d => {
      if (d<7)   return `${d}天前`;
      if (d<30)  return `${Math.round(d/7)}周前`;
      if (d<365) return `${Math.round(d/30)}个月前`;
      return `${Math.round(d/365)}年前`;
    },
  },
};
const LANG_ORDER = ['en','it','es','zh'];

// ══ Themes ══════════════════════════════════════════════════
const THEMES = [
  { id:'manuscript', label:'Manuscript', bg:'#f4efe4', acc:'#8b4513', dark:false },
  { id:'birch',      label:'Birch',      bg:'#f0ece2', acc:'#5a7a3a', dark:false },
  { id:'fog',        label:'Fog',        bg:'#eef0f4', acc:'#3d5a8a', dark:false },
  { id:'sepia',      label:'Sepia',      bg:'#f6eed8', acc:'#b07020', dark:false },
  { id:'ash',        label:'Ash',        bg:'#f2f0ec', acc:'#484844', dark:false },
  { id:'rosedust',   label:'Rose Dust',  bg:'#f6eee8', acc:'#a04040', dark:false },
  { id:'vellum',     label:'Vellum',     bg:'#faf8f0', acc:'#0e0c08', dark:false },
  { id:'duskrose',   label:'Dusk Rose',  bg:'#f4ecf2', acc:'#8a3888', dark:false },
  { id:'sandcourt',  label:'Sand Court', bg:'#f8f0e0', acc:'#c89020', dark:false },
  { id:'chalk',      label:'Chalk',      bg:'#f8f8f4', acc:'#2060c0', dark:false },
  { id:'noir',       label:'Noir',       bg:'#080706', acc:'#c8952a', dark:true  },
  { id:'midnight',   label:'Midnight',   bg:'#060810', acc:'#5080e0', dark:true  },
  { id:'ember',      label:'Ember',      bg:'#0c0804', acc:'#e88020', dark:true  },
  { id:'catacombs',  label:'Catacombs',  bg:'#060808', acc:'#40c0a0', dark:true  },
  { id:'abyss',      label:'Abyss',      bg:'#000000', acc:'#d8d8d8', dark:true  },
  { id:'blood',      label:'Blood',      bg:'#0a0404', acc:'#e03030', dark:true  },
  { id:'absinthe',   label:'Absinthe',   bg:'#04080a', acc:'#58c850', dark:true  },
  { id:'amethyst',   label:'Amethyst',   bg:'#080610', acc:'#a878f8', dark:true  },
  { id:'iron',       label:'Iron',       bg:'#0a0c0e', acc:'#a0b8c8', dark:true  },
  { id:'candle',     label:'Candle',     bg:'#0e0a06', acc:'#f8c840', dark:true  },
];

// ══ Cases ════════════════════════════════════════════════════
const CASES = [
  {
    id:'A',
    title_en:'The Broken Prince',      title_it:'Il Principe Spezzato',
    title_es:'El Príncipe Roto',       title_zh:'破碎的王子',
    desc_en:'A ruler who lost everything to the one he trusted most.',
    desc_it:'Un sovrano che ha perso tutto per mano di chi si fidava di più.',
    desc_es:'Un gobernante que lo perdió todo por quien más confiaba.',
    desc_zh:'一位统治者因最信任的人而失去一切。',
    identity:'Hamlet, Prince of Denmark',
    profile:'A philosopher-prince paralysed by grief and the weight of duty. He witnessed betrayal at the highest level — his father murdered, his mother complicit, his love weaponised against him. His tragedy is not incapacity but excess of thought: he sees too clearly to act simply.',
    archetype:'Philosophical prince, heir to a poisoned legacy',
    memories:[
      { concept:'Father',   feeling:'amore',      content:'He used to wake me before dawn to watch the sea fog lift from the ramparts. He said the world looked honest for exactly one hour. I believed him.',                                                                            note:'My earliest memory.',                          daysAgo:3650 },
      { concept:'Betrayal', feeling:'rabbia',      content:'I have been going over the night again and again. The same cup. The same smile. The same hand that poured for thirty years. I cannot make the geometry of it work in my head.',                                              note:'After learning the truth from the ghost.',      daysAgo:30   },
      { concept:'Death',    feeling:'malinconia',  content:'Poor Yorick. I knew him — a fellow of infinite jest. And now nothing. A skull. The skull laughs at me because it knows what I do not yet know how to say.',                                                                note:'In the graveyard.',                             daysAgo:20   },
      { concept:'Love',     feeling:'vergogna',    content:'I was cruel to her today. She came to return my letters and I told her to get to a nunnery. She looked at me like I was already a ghost. Maybe I am.',                                                                    note:'After the play within the play.',               daysAgo:18   },
      { concept:'Purpose',  feeling:'ansia',       content:'To be or not to be — it is not a poetic question, it is a practical one. Every hour I choose not to act is a choice. I have made it four hundred times.',                                                                 note:'Alone in the great hall at 3 a.m.',             daysAgo:15   },
      { concept:'Mother',   feeling:'tristezza',   content:'She chose so quickly. The speed of it — the speed of it. Less than a month.',                                                                                                                                              note:'At her wedding banquet.',                       daysAgo:28   },
      { concept:'Justice',  feeling:'orgoglio',    content:'The play is the thing. When he flinched I felt something I have not felt in months — that I am still here, still sharp, still capable of something.',                                                                     note:'After The Mousetrap succeeded.',                daysAgo:17   },
      { concept:'Fate',     feeling:'serenità',    content:'There is a special providence in the fall of a sparrow. I feel strangely calm today. Whatever comes, comes. I think I am ready now.',                                                                                    note:'The morning before the duel.',                  daysAgo:1    },
      { concept:'Kingdom',  feeling:'nostalgia',   content:'Denmark. The word used to mean something to me. A promise. Now it feels like a word in a language I once spoke fluently and have since forgotten.',                                                                       note:'Looking out from the battlements at night.',    daysAgo:25   },
      { concept:'Truth',    feeling:'curiosità',   content:'What if the ghost lied? What if I have destroyed everything — Ophelia, Polonius, my mother — for a fever dream of a spirit? I must know. I must be certain.',                                                            note:'Before commissioning the play.',                daysAgo:22   },
    ],
  },
  {
    id:'B',
    title_en:'The Lighthouse Woman',   title_it:'La Donna del Faro',
    title_es:'La Mujer del Faro',      title_zh:'灯塔女人',
    desc_en:'A woman who stopped time and let her heart rot with the house.',
    desc_it:'Una donna che ha fermato il tempo e ha lasciato marcire il cuore con la casa.',
    desc_es:'Una mujer que detuvo el tiempo y dejó que su corazón se pudriera con la casa.',
    desc_zh:'一个停住时间、任凭心与房子一同腐烂的女人。',
    identity:'Miss Havisham (Great Expectations)',
    profile:'A woman of immense wealth abandoned at the altar who chose to freeze the moment of her humiliation forever — clocks stopped, wedding cake rotting, dress never removed. She raised a girl specifically to break men\'s hearts, but never understood that revenge consumed her, not her enemy.',
    archetype:'Jilted aristocrat, architect of another\'s cruelty',
    memories:[
      { concept:'Time',     feeling:'rabbia',      content:'I stopped them all. Every clock in the house at twenty minutes to nine. They cannot take anything further from me if there is no further.',                                                                                 note:'The morning after the wedding that never was.',  daysAgo:9000 },
      { concept:'Wedding',  feeling:'vergogna',    content:'The dress is still on. I will not remove it. I refuse to give that moment the dignity of my acknowledgement. It happened to someone else. I am still waiting.',                                                           note:'The dress has been on for decades.',             daysAgo:8000 },
      { concept:'Estella',  feeling:'orgoglio',    content:'She is perfect. She will feel nothing. I have made sure of it. When she breaks them it will not hurt her, and that is the only mercy I know how to give.',                                                               note:'Watching Estella return from school.',           daysAgo:1800 },
      { concept:'Love',     feeling:'malinconia',  content:'I think sometimes that what I cultivated in her was not strength but emptiness. There is a difference. I confused them and now I cannot go back.',                                                                        note:'After Estella said she could not feel.',         daysAgo:400  },
      { concept:'Compeyson',feeling:'ansia',       content:'His name. I cannot write it without my hand trembling. Twenty years and it still works on me like a key in a lock. He built me to break. He succeeded.',                                                                 note:'Finding an old letter by accident.',             daysAgo:200  },
      { concept:'Pip',      feeling:'curiosità',   content:'The boy has something. An earnestness I had forgotten existed. He looks at Estella the way someone once looked at me. I watch him and feel something loosening.',                                                        note:'After Pip\'s third visit.',                     daysAgo:300  },
      { concept:'Cake',     feeling:'noia',        content:'The cake is collapsing inward now. Mice have had it. It has become a geography of rot. I find it more honest than anything else in the room.',                                                                           note:'Looking at the wedding table.',                 daysAgo:5000 },
      { concept:'Fire',     feeling:'paura',       content:'I dreamed of fire. Of the dress catching. I woke and felt — not horror — something closer to relief. What does it mean when destruction feels like release?',                                                            note:'Recurring dream.',                              daysAgo:100  },
      { concept:'Regret',   feeling:'tristezza',   content:'I told her to love him if she could. She said she could not. I made her that way. I spent a childhood building what I am now asking her to undo. The cruelty of me.',                                                   note:'Their final conversation.',                     daysAgo:50   },
      { concept:'Pip',      feeling:'gratitudine', content:'He forgave me. I do not understand why. I used his love as currency in a game he never agreed to play. And he forgave me. Something in me broke open when he did.',                                                     note:'After asking for his forgiveness.',              daysAgo:40   },
    ],
  },
  {
    id:'C',
    title_en:"The Monster's Architect",  title_it:"L'Architetto del Mostro",
    title_es:'El Arquitecto del Monstruo',title_zh:'怪物的建筑师',
    desc_en:'The creator who fled his creation and was hunted by his own guilt.',
    desc_it:'Il creatore che fuggì dalla sua creazione e fu perseguitato dal proprio senso di colpa.',
    desc_es:'El creador que huyó de su creación y fue acechado por su propia culpa.',
    desc_zh:'那个逃离自己创造物、被罪恶感追猎的创造者。',
    identity:'Victor Frankenstein (Frankenstein, M. Shelley)',
    profile:'A brilliant scientist consumed by the ambition to overcome death. He succeeded — and immediately abandoned what he made. His tragedy is not scientific hubris but moral cowardice: he never took responsibility for his creation, and so the creature\'s suffering and his own guilt became the same wound, feeding each other across ice and ruin.',
    archetype:'Promethean scientist, abdicated creator',
    memories:[
      { concept:'Creation', feeling:'orgoglio',    content:'It worked. Two years of obsession and then it worked. For one second before I saw its eyes I was God.',                                                                                                                   note:'The night of the experiment.',                  daysAgo:2900 },
      { concept:'Creation', feeling:'paura',       content:'Its eyes opened. Yellow, watery, unfocused. And I ran. I simply ran. I left it there, alone, in the dark laboratory. I have never told anyone this.',                                                                    note:'The same night, one minute later.',             daysAgo:2900 },
      { concept:'Justine',  feeling:'vergogna',    content:'She hanged for William\'s murder. I knew who did it. I stood in the crowd and said nothing. She died with my silence in her ears.',                                                                                      note:'After the execution.',                          daysAgo:2600 },
      { concept:'Ambition', feeling:'malinconia',  content:'I wanted to conquer death. I thought I was doing it for humanity. Now I think I was doing it because I was afraid of my father dying, and I dressed the fear in the language of science.',                              note:'Reflection during illness.',                    daysAgo:2400 },
      { concept:'Creature', feeling:'rabbia',      content:'He came to me on the glacier. He was eloquent. He had read Paradise Lost. He asked for a companion and I almost felt something like kinship. Then he smiled and I felt only horror.',                                   note:'Mont Blanc, the Mer de Glace.',                 daysAgo:2200 },
      { concept:'Elizabeth',feeling:'amore',       content:'She is the only thing between me and total dissolution. When I look at her I can still locate the version of myself that existed before the laboratory. I am terrified for her.',                                        note:'Before their wedding.',                         daysAgo:800  },
      { concept:'Elizabeth',feeling:'tristezza',   content:'She is dead. He was true to his word. I should have known when he said "I will be with you on your wedding night." I did know. I chose not to understand.',                                                             note:'The wedding chamber.',                          daysAgo:790  },
      { concept:'Guilt',    feeling:'ansia',       content:'I cannot sleep without seeing them. Justine. William. Henry. Elizabeth. The creature did not murder them. I murdered them by making the creature and abandoning it to itself.',                                          note:'Recurring insomnia.',                           daysAgo:600  },
      { concept:'Ice',      feeling:'serenità',    content:'I am dying. The cold has a clarity I was denied in the laboratory. I understand now that the creature and I are the same — both born incomplete, both capable of tenderness, both ruined by the other.',               note:'On Walton\'s ship.',                            daysAgo:10   },
      { concept:'Science',  feeling:'curiosità',   content:'If I had it to do again — would I? I have asked a thousand times. The honest answer, the one that condemns me most fully, is yes. Not for glory. For the question itself.',                                             note:'Final journal entry.',                          daysAgo:3    },
    ],
  },
];

// ══ State ════════════════════════════════════════════════════
let activeCase    = null;
let questionsLeft = 10;
let unlockedCount = 0;
let chatHistory   = [];
let isLoading     = false;
let currentLang   = 'en';
let currentTheme  = 'noir';
let themePanelOpen = false;
let langPanelOpen  = false;
const MAX_Q        = 10;
const UNLOCK_EVERY = 2;

// ══ Utils ════════════════════════════════════════════════════
const esc = s => String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const L   = () => LANGS[currentLang] || LANGS.en;
const fl  = key => L().feelLabels[key] || key;

function caseTitle(c) {
  return c[`title_${currentLang}`] || c.title_en;
}
function caseDesc(c) {
  return c[`desc_${currentLang}`] || c.desc_en;
}

// ══ Persistence ══════════════════════════════════════════════
function loadPrefs() {
  const t = localStorage.getItem('pa-theme');
  const g = localStorage.getItem('pa-lang');
  const u = localStorage.getItem('pa-lm-url');
  const m = localStorage.getItem('pa-lm-model');
  if (t && THEMES.find(x=>x.id===t)) currentTheme = t;
  if (g && LANGS[g]) currentLang = g;
  if (u) document.getElementById('lm-url').value = u;
  if (m) document.getElementById('lm-model').value = m;
  applyTheme(currentTheme, false);
  applyLang(currentLang, false);
}

function saveLm() {
  localStorage.setItem('pa-lm-url',   document.getElementById('lm-url').value.trim());
  localStorage.setItem('pa-lm-model', document.getElementById('lm-model').value.trim());
  const s = document.getElementById('lm-status');
  s.textContent = L().lmSave === 'SAVE' ? '✓' : '✓';
  s.style.display = 'inline';
  setTimeout(() => s.style.display = 'none', 2000);
}

// ══ Theme ════════════════════════════════════════════════════
function applyTheme(id, persist=true) {
  currentTheme = id;
  document.documentElement.setAttribute('data-theme', id);
  if (persist) localStorage.setItem('pa-theme', id);
  document.querySelectorAll('.theme-swatch-btn').forEach(s => s.classList.toggle('active', s.dataset.theme===id));
  const th = THEMES.find(t=>t.id===id);
  const btn = document.getElementById('btn-theme-toggle');
  if (btn && th)
    btn.innerHTML = `<span style="display:inline-block;width:12px;height:12px;background:${th.acc};border-radius:2px;margin-right:5px;flex-shrink:0"></span>${th.label}`;
}

function buildThemePanel() {
  const l = L();
  const sw = group => group.map(t=>`
    <div class="theme-swatch-btn${t.id===currentTheme?' active':''}"
      data-theme="${t.id}" title="${t.label}"
      style="background:${t.bg};border:2px solid ${t.acc}55"
      onclick="applyTheme('${t.id}')"></div>`).join('');
  return `
    <div class="panel-section-label">${l.themeLight}</div>
    <div class="swatch-row">${sw(THEMES.filter(t=>!t.dark))}</div>
    <div class="panel-section-label">${l.themeDark}</div>
    <div class="swatch-row">${sw(THEMES.filter(t=>t.dark))}</div>`;
}

function toggleThemePanel() {
  themePanelOpen = !themePanelOpen;
  if (langPanelOpen) { langPanelOpen=false; document.getElementById('lang-panel')?.classList.remove('open'); }
  const p = document.getElementById('theme-panel');
  if (p) { p.innerHTML = themePanelOpen ? buildThemePanel() : ''; p.classList.toggle('open', themePanelOpen); }
}

// ══ Language ═════════════════════════════════════════════════
function applyLang(code, persist=true) {
  currentLang = code;
  document.documentElement.lang = code;
  if (persist) localStorage.setItem('pa-lang', code);
  document.querySelectorAll('.lang-btn').forEach(b => b.classList.toggle('active', b.dataset.lang===code));
  const lb = document.getElementById('btn-lang-toggle');
  if (lb) lb.textContent = L().label;
  updateIntroText();
}

function updateIntroText() {
  const l = L();
  const el = id => document.getElementById(id);
  if (el('intro-emblem')) el('intro-emblem').textContent = l.emblem;
  if (el('intro-sub'))    el('intro-sub').textContent    = l.appSub;
  if (el('intro-desc'))   el('intro-desc').innerHTML     = l.introDesc;
  if (el('lm-config-title')) el('lm-config-title').textContent = l.lmTitle;
  if (el('lm-model'))     el('lm-model').placeholder     = l.lmModelPh;
  if (el('btn-lm-save'))  el('btn-lm-save').textContent  = l.lmSave;
  if (el('btn-theme-toggle')) {
    const th = THEMES.find(t=>t.id===currentTheme);
    if (th) el('btn-theme-toggle').innerHTML =
      `<span style="display:inline-block;width:12px;height:12px;background:${th.acc};border-radius:2px;margin-right:5px"></span>${th.label}`;
  }
  buildCaseCards();
}

function buildLangPanel() {
  return LANG_ORDER.map(code => {
    const lg = LANGS[code];
    return `<button class="lang-btn${code===currentLang?' active':''}" data-lang="${code}"
      onclick="applyLang('${code}');toggleLangPanel();updateIntroText()">${lg.label}
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

// ══ Intro ════════════════════════════════════════════════════
function buildCaseCards() {
  const l = L();
  const container = document.getElementById('case-cards');
  if (!container) return;
  container.innerHTML = CASES.map(c => `
    <div class="case-card" onclick="startCase('${c.id}')">
      <div class="case-card-num">${l.caseLabel} ${c.id}</div>
      <div class="case-card-title">${esc(caseTitle(c))}</div>
      <div class="case-card-desc">${esc(caseDesc(c))}</div>
      <div class="case-card-mems">${l.memFrags(c.memories.length)}</div>
    </div>`).join('');
}

// ══ Game ═════════════════════════════════════════════════════
function startCase(id) {
  activeCase    = CASES.find(c=>c.id===id);
  questionsLeft = MAX_Q;
  unlockedCount = 2;
  chatHistory   = [];
  isLoading     = false;
  const l = L();

  document.getElementById('intro').style.display = 'none';
  document.getElementById('verdict').classList.remove('active');
  document.getElementById('result').classList.remove('active');
  document.getElementById('game').classList.add('active');

  document.getElementById('topbar-case').textContent    = `${l.caseLabel} ${activeCase.id} · ${caseTitle(activeCase).toUpperCase()}`;
  document.getElementById('btn-conclude-top').textContent    = l.closeCase;
  document.getElementById('btn-conclude-bottom').textContent = l.conclude;
  document.getElementById('btn-back').textContent            = l.back;
  document.getElementById('question-input').placeholder      = l.askPh;
  document.getElementById('btn-ask').textContent             = l.ask;
  document.getElementById('archive-title').textContent       = l.archiveTitle;
  document.getElementById('archive-subject').textContent     = l.archiveAnon;

  updateQuestionsLeft();
  renderArchive();
  renderChat();
}

function backToIntro() {
  document.getElementById('game').classList.remove('active');
  document.getElementById('verdict').classList.remove('active');
  document.getElementById('result').classList.remove('active');
  document.getElementById('intro').style.display = 'flex';
  activeCase = null;
}

function updateQuestionsLeft() {
  const el = document.getElementById('questions-left');
  el.textContent = L().questLeft(questionsLeft, MAX_Q);
  el.classList.toggle('low', questionsLeft <= 3);
}

function renderArchive() {
  const l    = L();
  const mems = activeCase.memories;
  document.getElementById('archive-stats').textContent = l.archiveStats(unlockedCount, mems.length);
  document.getElementById('archive-list').innerHTML = mems.map((m,i) => {
    if (i >= unlockedCount) return `<div class="locked-placeholder">${l.classified}</div>`;
    const col = FEELING_COLORS[m.feeling] || '#888';
    return `
      <div class="mem-fragment">
        <div class="mem-frag-concept">${esc(m.concept)}</div>
        <span class="mem-frag-feel" style="background:${col}18;color:${col}">${fl(m.feeling)}</span>
        <div class="mem-frag-content">"${esc(m.content)}"</div>
        ${m.note ? `<div class="mem-frag-note">${esc(m.note)} · ${l.daysAgo(m.daysAgo)}</div>` : ''}
      </div>`;
  }).join('');
}

function renderChat() {
  const area = document.getElementById('chat-area');
  const l    = L();
  if (!chatHistory.length) {
    area.innerHTML = `<div class="chat-msg system"><div class="bubble">${l.systemMsg(MAX_Q, UNLOCK_EVERY)}</div></div>`;
  } else {
    area.innerHTML = chatHistory.map(m => msgHTML(m, l)).join('') + '<div id="chat-bottom"></div>';
  }
  setTimeout(() => document.getElementById('chat-bottom')?.scrollIntoView({behavior:'smooth'}), 40);
}

function msgHTML(m, l) {
  l = l || L();
  if (m.role==='user') return `
    <div class="chat-msg user">
      <div class="msg-label">${l.investigator}</div>
      <div class="bubble">${esc(m.content)}</div>
    </div>`;
  if (m.role==='unlock') return `
    <div class="chat-msg unlock-notice">
      <div class="bubble">${esc(l.unlockNotice(m.content))}</div>
    </div>`;
  return `
    <div class="chat-msg archive">
      <div class="msg-label">${l.brainLabel}</div>
      <div class="bubble">${esc(m.content)}</div>
    </div>`;
}

async function askBrain() {
  if (isLoading || questionsLeft<=0) return;
  const inp  = document.getElementById('question-input');
  const text = inp.value.trim();
  if (!text) return;
  const l = L();

  inp.value = '';
  questionsLeft--;
  updateQuestionsLeft();
  isLoading = true;
  document.getElementById('btn-ask').disabled = true;

  chatHistory.push({ role:'user', content:text });
  renderChatWithTyping(l);

  const shouldUnlock = (MAX_Q - questionsLeft) % UNLOCK_EVERY === 0;
  const newUnlock    = shouldUnlock && unlockedCount < activeCase.memories.length
    ? activeCase.memories[unlockedCount] : null;

  const memBlock = activeCase.memories.slice(0, unlockedCount).map(m =>
    `[${l.daysAgo(m.daysAgo)}] CONCEPT: ${m.concept} | FEELING: ${fl(m.feeling)}\n"${m.content}"${m.note?'\n[context: '+m.note+']':''}`
  ).join('\n\n') || '[No fragments unlocked yet]';

  const sys = `You are the PHANTOM ARCHIVE BRAIN — the psychological intelligence embedded in an anonymous character's emotional memory database.
The investigator is trying to identify who this character is.
You must answer questions truthfully based ONLY on the memories provided.
NEVER reveal the character's name or the work they come from.
Describe their psychology, patterns, relationships, and emotional life in depth.
Keep responses to 2–4 sentences maximum.
${l.sysPromptInstr}

═══ UNLOCKED ARCHIVE FRAGMENTS ═══
${memBlock}
══════════════════════════════════`;

  const lmUrl   = document.getElementById('lm-url').value.trim();
  const lmModel = document.getElementById('lm-model').value.trim();
  let reply = '';
  try {
    const res = await fetch(lmUrl, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        model: lmModel||'local-model', max_tokens:320, temperature:.75,
        messages:[
          {role:'system', content:sys},
          ...chatHistory.filter(m=>m.role==='user'||m.role==='assistant')
            .map(m=>({role:m.role, content:m.content}))
        ]
      })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    reply = data.choices?.[0]?.message?.content || '[No response — check LM Studio]';
  } catch(e) {
    reply = `[Archive connection lost — ${e.message}]`;
  }

  chatHistory.push({role:'assistant', content:reply});

  if (newUnlock) {
    unlockedCount++;
    chatHistory.push({role:'unlock', content:`"${newUnlock.concept}" — ${fl(newUnlock.feeling)}`});
    renderArchive();
  }

  isLoading = false;
  document.getElementById('btn-ask').disabled = false;
  renderChat();
  if (questionsLeft<=0) setTimeout(showVerdict, 900);
}

function renderChatWithTyping(l) {
  const area = document.getElementById('chat-area');
  l = l || L();
  area.innerHTML = chatHistory.map(m=>msgHTML(m,l)).join('') +
    `<div class="chat-msg archive">
      <div class="msg-label">${l.brainLabel}</div>
      <div class="bubble"><div class="typing-dots">
        ${[0,1,2].map(i=>`<div class="typing-dot" style="animation-delay:${i*.22}s"></div>`).join('')}
      </div></div>
    </div><div id="chat-bottom"></div>`;
  setTimeout(()=>document.getElementById('chat-bottom')?.scrollIntoView({behavior:'smooth'}),40);
}

// ══ Verdict ══════════════════════════════════════════════════
function showVerdict() {
  const l = L();
  document.getElementById('game').classList.remove('active');
  const v = document.getElementById('verdict');
  v.classList.add('active');
  v.style.display = '';
  document.getElementById('verdict-title').textContent     = l.verdictTitle;
  document.getElementById('verdict-sub').textContent       = l.verdictSub;
  document.getElementById('verdict-name-label').textContent= l.verdictNameL;
  document.getElementById('verdict-prof-label').textContent= l.verdictProfileL;
  document.getElementById('verdict-name').placeholder      = l.verdictNamePh;
  document.getElementById('verdict-text').placeholder      = l.verdictProfPh;
  document.getElementById('btn-submit-verdict').textContent= l.submitVerdict;
  document.getElementById('verdict-name').value = '';
  document.getElementById('verdict-text').value = '';
  setTimeout(()=>document.getElementById('verdict-name').focus(), 100);
}

async function submitVerdict() {
  const l            = L();
  const playerName   = document.getElementById('verdict-name').value.trim();
  const playerProf   = document.getElementById('verdict-text').value.trim();
  if (!playerName && !playerProf) return;

  document.getElementById('verdict').classList.remove('active');
  const r = document.getElementById('result');
  r.classList.add('active');

  document.getElementById('result-dossier').setAttribute('data-label', l.caseFile);
  document.getElementById('result-identity-label').textContent  = l.trueIdentity;
  document.getElementById('result-identity').textContent        = activeCase.identity;
  document.getElementById('result-profile-label').textContent   = l.officialProf;
  document.getElementById('result-profile').textContent         = activeCase.profile;
  document.getElementById('result-verdict-label').textContent   = l.yourVerdict;
  document.getElementById('result-verdict').textContent         =
    (playerName ? `"${playerName}"\n\n` : '') + (playerProf || l.noProfile);
  document.getElementById('result-ai-eval-section').style.display = 'none';
  document.getElementById('btn-play-again').textContent         = l.playAgain;

  const nameMatch = playerName.toLowerCase().includes(
    activeCase.identity.split(',')[0].split(' ')[0].toLowerCase()
  );
  const questionsUsed = MAX_Q - questionsLeft;
  const score         = Math.min(100, (nameMatch?80:20) + Math.max(0,(MAX_Q-questionsUsed)*2));
  document.getElementById('score-display').textContent = `${score}`;
  document.getElementById('score-label').textContent   = nameMatch
    ? l.scoreConfirmed(questionsUsed, MAX_Q)
    : l.scoreUnconfirmed(questionsUsed, MAX_Q);

  setTimeout(()=>{ if (nameMatch) document.getElementById('result-stamp').classList.add('show'); }, 600);

  // AI eval
  const lmUrl   = document.getElementById('lm-url').value.trim();
  const lmModel = document.getElementById('lm-model').value.trim();
  try {
    const evalPrompt = `The character is: ${activeCase.identity}. Official profile: "${activeCase.profile}". Investigator's guess: "${playerProf}". In 2-3 sentences, compare the investigator's profile to the official one. ${l.sysPromptInstr}`;
    const res = await fetch(lmUrl, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({ model:lmModel||'local-model', max_tokens:200, temperature:.6,
        messages:[{role:'user', content:evalPrompt}] })
    });
    if (res.ok) {
      const data = await res.json();
      const ev   = data.choices?.[0]?.message?.content;
      if (ev) {
        document.getElementById('result-ai-eval-label').textContent = l.aiEval;
        document.getElementById('result-ai-eval').textContent       = ev;
        document.getElementById('result-ai-eval-section').style.display = 'block';
      }
    }
  } catch(e) {}
}

// ══ Boot ═════════════════════════════════════════════════════
loadPrefs();
buildCaseCards();
updateIntroText();