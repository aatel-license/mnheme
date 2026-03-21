/**
 * MNHEME Constants
 * ================
 * Feelings, media types, system prompt, and provider presets.
 */

export const FEELINGS = [
  'gioia', 'tristezza', 'rabbia', 'paura', 'nostalgia',
  'amore', 'malinconia', 'serenità', 'sorpresa', 'ansia',
  'gratitudine', 'vergogna', 'orgoglio', 'noia', 'curiosità',
];

export const FEELING_LABELS = {
  gioia: 'Joy', tristezza: 'Sadness', rabbia: 'Anger',
  paura: 'Fear', nostalgia: 'Nostalgia', amore: 'Love',
  malinconia: 'Melancholy', serenità: 'Serenity', sorpresa: 'Surprise',
  ansia: 'Anxiety', gratitudine: 'Gratitude', vergogna: 'Shame',
  orgoglio: 'Pride', noia: 'Boredom', curiosità: 'Curiosity',
};

export const FEELING_COLORS = {
  gioia: '#f4c430', tristezza: '#6b9ec7', rabbia: '#e05c3a',
  paura: '#8b7db5', nostalgia: '#c47e3a', amore: '#d95f7a',
  malinconia: '#4a8fa8', serenità: '#5a9e6f', sorpresa: '#d4a017',
  ansia: '#9b7fa8', gratitudine: '#7a9e5a', vergogna: '#9b5a5a',
  orgoglio: '#c4933a', noia: '#5a5a6a', curiosità: '#6a8a9b',
};

export const MEDIA_TYPES = ['text', 'image', 'video', 'audio', 'doc'];

export const SYSTEM_PROMPT =
  'Sei il cervello cognitivo di MNHEME, un sistema di memoria umana digitale.\n' +
  'Elabora ricordi, emozioni e pattern cognitivi con profondità e sensibilità.\n' +
  'Rispondi sempre in italiano.\n' +
  'Sii diretto, profondo, mai banale. Niente disclaimer né frasi introduttive generiche.';

export const PROVIDER_PRESETS = {
  'LM Studio':       { url: 'http://localhost:1234/v1/chat/completions', model: '' },
  'Ollama':          { url: 'http://localhost:11434/v1/chat/completions', model: '' },
  'OpenRouter':      { url: 'https://openrouter.ai/api/v1/chat/completions', model: '' },
  'Groq':            { url: 'https://api.groq.com/openai/v1/chat/completions', model: '' },
  'Anthropic':       { url: 'https://api.anthropic.com/v1/messages', model: 'claude-sonnet-4-20250514' },
  'Google AI Studio':{ url: 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions', model: '' },
  'Mistral':         { url: 'https://api.mistral.ai/v1/chat/completions', model: '' },
  'SambaNova':       { url: 'https://api.sambanova.ai/v1/chat/completions', model: '' },
  'Together':        { url: 'https://api.together.xyz/v1/chat/completions', model: '' },
  'Fireworks':       { url: 'https://api.fireworks.ai/inference/v1/chat/completions', model: '' },
  'Cerebras':        { url: 'https://api.cerebras.ai/v1/chat/completions', model: '' },
};
