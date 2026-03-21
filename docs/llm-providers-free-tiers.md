# MNHEME — Analisi Free Tier Provider LLM Supportati

> Ultimo aggiornamento: Marzo 2026

MNHEME supporta 30+ provider LLM. Questa analisi documenta quali offrono un piano gratuito e i relativi limiti.

---

## Completamente Gratuiti (Locali)

| Provider | Note |
|----------|------|
| **LM Studio** | 100% gratuito, GUI desktop, modelli GGUF da HuggingFace. API OpenAI-compatibile su porta 1234. Limite = solo il tuo hardware |
| **Ollama** | 100% gratuito, CLI. Llama, Mistral, DeepSeek, Qwen, Gemma ecc. API OpenAI-compatibile. Limite = solo il tuo hardware |

---

## Free Tier Continuativo (non scade)

| Provider | Limiti Free |
|----------|-------------|
| **Google AI Studio** | Il migliore in assoluto. Gemini 2.5 Pro: 5 RPM, 100 RPD. Flash: 10 RPM, 250 RPD. Flash-Lite: 15 RPM, 1000 RPD. Context 1M token |
| **Mistral / Codestral** | Piano "Experiment": 1 miliardo di token/mese, tutti i modelli inclusi. Solo verifica telefono |
| **Groq** | ~30 RPM. LLaMA 3.3 70B: ~6000 TPM, ~500K token/giorno. Velocità altissima |
| **Cerebras** | 1M token/giorno, context fino a 64K. Inference a 2600+ token/sec |
| **Cloudflare Workers AI** | 10.000 Neurons/giorno (reset a mezzanotte UTC) |
| **Cohere** | 1000 chiamate API/mese, 5-20 RPM. Solo prototipazione, no uso commerciale |
| **GitHub Models** | Modelli "high" (GPT-4o): 10 RPM, 50 RPD. Modelli "low": limiti più alti |
| **OpenRouter** | ~27 modelli gratuiti (ID `:free`). 20 RPM, 50 RPD (o 1000 RPD con $10+ di crediti) |
| **Hugging Face** | Crediti mensili gratuiti (importo non documentato). PRO ($9/mese) dà 20x |
| **NVIDIA NIM** | ~1000 crediti API gratuiti, 40 RPM. Solo dev/prototipazione, no produzione |

---

## Solo Crediti Iniziali (si esauriscono o scadono)

| Provider | Crediti | Scadenza |
|----------|---------|----------|
| **Together AI** | Fino a $100 | Non specificata |
| **Alibaba Cloud (Aliyun)** | 70M token + $200 crediti | Regione Singapore |
| **Vertex AI** | $300 Google Cloud credits | 90 giorni |
| **AI21** | $10 | 3 mesi |
| **OpenAI** | $5 (solo GPT-3.5 Turbo, 3 RPM) | 3 mesi |
| **Anthropic** | $5 (studenti: fino a $300) | Una tantum |
| **SambaNova** | $5 (~30M token su Llama 8B) | 30 giorni |
| **Novita AI** | ~$10 | Non specificata |
| **Fireworks AI** | $1 | Non specificata |
| **Hyperbolic** | $1 (60 RPM tier base) | Non specificata |
| **Nebius** | $1 (richiede deposito $25) | Non specificata |
| **Scaleway** | 1M token gratis | Una tantum |

---

## Nessun Piano Gratuito

| Provider | Note |
|----------|------|
| **Upstage** | Promozione gratuita scaduta il 2 marzo 2026. Ora solo piani a pagamento |
| **Inference.net** | Solo pay-per-token |

---

## Raccomandazione per MNHEME

Per un uso gratuito continuativo i migliori sono:

1. **Ollama / LM Studio** — Zero costi, privacy totale, nessun limite se hai hardware decente
2. **Google AI Studio** — Il free tier API più generoso in assoluto
3. **Mistral** — 1 miliardo di token/mese gratis è enorme
4. **Groq** — Velocità eccezionale, limiti ragionevoli per uso personale

### Configurazione consigliata per `.env`

```bash
# Priorità: locale gratuito → cloud gratuito → cloud a pagamento

# 1. Locale (zero costi)
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
LM_STUDIO_MODEL=local-model
LM_STUDIO_RPM=60

# 2. Fallback cloud gratuito
GROQ_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_...
GROQ_RPM=30

# 3. Secondo fallback cloud gratuito
MISTRAL_URL=https://api.mistral.ai/v1/chat/completions
MISTRAL_MODEL=mistral-large-latest
MISTRAL_API_KEY=...
MISTRAL_RPM=60

USE_MULTI_PROVIDER=true
TEMPERATURE=0.3
```

---

## Riepilogo Visuale

```
GRATUITI LOCALI          FREE TIER CONTINUATIVO         SOLO CREDITI INIZIALI
(nessun limite esterno)  (limiti di rate/token)         (si esauriscono)

  LM Studio              Google AI Studio (migliore)    Together AI ($100)
  Ollama                 Mistral (1B token/mese)        Alibaba ($200+70M tok)
                         Groq (~500K tok/giorno)        Vertex AI ($300/90gg)
                         Cerebras (1M tok/giorno)       AI21 ($10/3 mesi)
                         Cloudflare (10K Neurons/gg)    OpenAI ($5/3 mesi)
                         Cohere (1000 call/mese)        Anthropic ($5)
                         GitHub Models (50 RPD)         SambaNova ($5/30gg)
                         OpenRouter (50 RPD free)       Novita (~$10)
                         Hugging Face (crediti mensili) Fireworks ($1)
                         NVIDIA NIM (1000 crediti)      Hyperbolic ($1)
                                                        Nebius ($1)
                                                        Scaleway (1M tok)
```
