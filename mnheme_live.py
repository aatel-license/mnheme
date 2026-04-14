"""
mnheme_live.py
==============
MNHĒMĒ Live — Percezione + Conversazione in tempo reale.

Il frame viene inviato a LM Studio SOLO per la descrizione visiva,
poi viene scartato. In MNHĒMĒ viene salvata SOLO la descrizione testuale.

Tutte le opzioni sono configurabili via .env (vedi sotto).
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional


# ── .env loader ───────────────────────────────────────────────────────────────
def _load_env(path: str = ".env") -> None:
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        pass


_load_env(str(Path(__file__).parent / ".env"))

# =============================================================================
#  CONFIGURAZIONE — tutte le variabili sono modificabili nel .env
# =============================================================================
#
# ── LM Studio ─────────────────────────────────────────────────────────────────
# LM_STUDIO_URL_LIVE              = http://localhost:1234/v1
# LM_STUDIO_MODEL            = gemma4-vision        # modello percezione (vision)
# LM_STUDIO_CHAT_MODEL       =                      # modello chat (vuoto = uguale al precedente)
# LM_TEMPERATURE_PERCEPTION  = 0.4
# LM_TEMPERATURE_CHAT        = 0.7
# LM_MAX_TOKENS_PERCEPTION   = 512
# LM_MAX_TOKENS_CHAT         = 512
#
# ── Database ──────────────────────────────────────────────────────────────────
# MNHEME_DB_PATH             = mnheme.mnheme
# MNHEME_FILES_DIR           =                      # vuoto = <db_stem>_files/
# MAX_CONTEXT_MEMORIES       = 8                    # ricordi nel contesto RAG
# RAG_SEARCH_LIMIT           = 8                    # risultati per full-text search
# RAG_RECENT_LIMIT           = 5                    # ultimi ricordi sempre inclusi
# HISTORY_LENGTH             = 12                   # turn conversazione in memoria
#
# ── Whisper ───────────────────────────────────────────────────────────────────
# WHISPER_MODEL              = base                 # tiny|base|small|medium|large
# CONVERSATION_LANGUAGE      = it                   # lingua trascrizione utente
# PERCEPTION_LANGUAGE        =                      # lingua audio TV (vuoto = auto)
#
# ── Percezione ────────────────────────────────────────────────────────────────
# PERCEPTION_INTERVAL        = 20                   # secondi tra cicli
# AUDIO_DURATION             = 10                   # secondi audio per ciclo
# CAMERA_INDEX               = 0
# FRAME_WIDTH                = 1280
# FRAME_HEIGHT               = 720
# JPEG_QUALITY               = 85                   # qualità JPEG inviato al modello
# AUDIO_SAMPLE_RATE          = 16000
#
# ── TTS ───────────────────────────────────────────────────────────────────────
# TTS_ENGINE                 = pyttsx3              # pyttsx3 | edge-tts | none
# TTS_VOICE                  =                      # nome voce (vuoto = default)
# TTS_RATE                   = 150                  # velocità parlato (solo pyttsx3)
# EDGE_TTS_VOICE             = it-IT-ElsaNeural     # voce edge-tts
#
# =============================================================================


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def _envi(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, default))
    except:
        return default


def _envf(key: str, default: float) -> float:
    try:
        return float(os.environ.get(key, default))
    except:
        return default


class Cfg:
    # LM Studio
    LM_URL = _env("LM_STUDIO_URL_LIVE", "http://localhost:1234/v1")
    LM_MODEL = _env("LM_STUDIO_MODEL", "gemma4-vision")
    LM_CHAT_MODEL = _env("LM_STUDIO_CHAT_MODEL", "") or _env(
        "LM_STUDIO_MODEL", "gemma4-vision"
    )
    LM_TEMP_PERC = _envf("LM_TEMPERATURE_PERCEPTION", 0.4)
    LM_TEMP_CHAT = _envf("LM_TEMPERATURE_CHAT", 0.7)
    LM_TOKENS_PERC = _envi("LM_MAX_TOKENS_PERCEPTION", 512)
    LM_TOKENS_CHAT = _envi("LM_MAX_TOKENS_CHAT", 512)
    # Database
    DB_PATH = _env("MNHEME_DB_PATH", "mnheme.mnheme")
    FILES_DIR = _env("MNHEME_FILES_DIR", "") or None
    MAX_CTX_MEM = _envi("MAX_CONTEXT_MEMORIES", 8)
    RAG_SEARCH_LIMIT = _envi("RAG_SEARCH_LIMIT", 8)
    RAG_RECENT_LIMIT = _envi("RAG_RECENT_LIMIT", 5)
    HISTORY_LENGTH = _envi("HISTORY_LENGTH", 12)
    # Whisper
    WHISPER_MODEL = _env("WHISPER_MODEL", "base")
    CONV_LANG = _env("CONVERSATION_LANGUAGE", "it")
    PERC_LANG = _env("PERCEPTION_LANGUAGE", "") or None
    # Percezione
    P_INTERVAL = _envi("PERCEPTION_INTERVAL", 20)
    AUDIO_DUR = _envi("AUDIO_DURATION", 10)
    CAM_INDEX = _envi("CAMERA_INDEX", 0)
    FRAME_W = _envi("FRAME_WIDTH", 1280)
    FRAME_H = _envi("FRAME_HEIGHT", 720)
    JPEG_QUALITY = _envi("JPEG_QUALITY", 85)
    AUDIO_SR = _envi("AUDIO_SAMPLE_RATE", 16000)
    # TTS
    TTS_ENGINE = _env("TTS_ENGINE", "pyttsx3")
    TTS_VOICE = _env("TTS_VOICE", "")
    TTS_RATE = _envi("TTS_RATE", 150)
    EDGE_VOICE = _env("EDGE_TTS_VOICE", "it-IT-ElsaNeural")


# ── Colori terminale ──────────────────────────────────────────────────────────
class C:
    R = "\033[0m"
    B = "\033[1m"
    CY = "\033[36m"
    GR = "\033[32m"
    YE = "\033[33m"
    RE = "\033[31m"
    DI = "\033[2m"
    MA = "\033[35m"
    BL = "\033[34m"
    WH = "\033[97m"


def log(icon: str, msg: str, color: str = C.CY, end: str = "\n") -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{C.DI}[{ts}]{C.R} {color}{C.B}{icon}{C.R} {msg}", end=end, flush=True)


# ── Whisper singleton ─────────────────────────────────────────────────────────
_whisper_model = None
_whisper_lock = threading.Lock()


def get_whisper():
    global _whisper_model
    with _whisper_lock:
        if _whisper_model is None:
            import whisper

            log("🧠", f"Caricamento Whisper ({Cfg.WHISPER_MODEL})...", C.YE)
            _whisper_model = whisper.load_model(Cfg.WHISPER_MODEL)
            log("🧠", "Whisper pronto", C.GR)
        return _whisper_model


def transcribe(audio_path: str, language: Optional[str] = None) -> str:
    try:
        opts = {"fp16": False}
        if language:
            opts["language"] = language
        result = get_whisper().transcribe(audio_path, **opts)
        return result.get("text", "").strip()
    except Exception as e:
        log("📝", f"Errore trascrizione: {e}", C.RE)
        return ""
    finally:
        try:
            os.unlink(audio_path)
        except:
            pass


# ── Audio ─────────────────────────────────────────────────────────────────────
def record_audio(duration: int, device: Optional[int] = None) -> Optional[str]:
    """Registra `duration` secondi fissi."""
    try:
        import sounddevice as sd
        import soundfile as sf

        audio = sd.rec(
            int(duration * Cfg.AUDIO_SR),
            samplerate=Cfg.AUDIO_SR,
            channels=1,
            dtype="float32",
            device=device,
        )
        sd.wait()
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        sf.write(tmp.name, audio, Cfg.AUDIO_SR)
        return tmp.name
    except Exception as e:
        log("🎙️ ", f"Errore registrazione: {e}", C.RE)
        return None


def record_until_enter(device: Optional[int] = None) -> Optional[str]:
    """Registra in streaming finché l'utente non preme Invio."""
    import sounddevice as sd
    import soundfile as sf
    import numpy as np

    chunks = []
    stop_evt = threading.Event()
    err: list = []

    def _rec():
        try:
            with sd.InputStream(
                samplerate=Cfg.AUDIO_SR,
                channels=1,
                dtype="float32",
                device=device,
            ) as stream:
                while not stop_evt.is_set():
                    chunk, _ = stream.read(Cfg.AUDIO_SR // 4)
                    chunks.append(chunk.copy())
        except Exception as e:
            err.append(e)

    t = threading.Thread(target=_rec, daemon=True)
    t.start()
    input()  # blocca finché l'utente non preme Invio
    stop_evt.set()
    t.join(timeout=2)

    if err:
        log("🎙️ ", f"Errore stream: {err[0]}", C.RE)
        return None
    if not chunks:
        return None

    audio = np.concatenate(chunks, axis=0)
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmp.name, audio, Cfg.AUDIO_SR)
    return tmp.name


# ── LM Studio ─────────────────────────────────────────────────────────────────
_lm_client = None
_lm_lock = threading.Lock()


def get_lm():
    global _lm_client
    with _lm_lock:
        if _lm_client is None:
            from openai import OpenAI

            _lm_client = OpenAI(base_url=Cfg.LM_URL, api_key="lm-studio")
        return _lm_client


PERCEPTION_SYSTEM = """Sei un sistema percettivo connesso al mondo reale.
Descrivi ciò che vedi e senti in modo ricco e dettagliato.
Rispondi SOLO con un oggetto JSON valido — nessun testo fuori dal JSON:
{
  "concept":  "soggetto principale (es. 'Telegiornale', 'Persona', 'Paesaggio')",
  "feeling":  "uno tra: gioia|tristezza|rabbia|paura|nostalgia|amore|malinconia|serenità|sorpresa|ansia|gratitudine|vergogna|orgoglio|noia|curiosità",
  "content":  "descrizione completa: cosa vedi, testi visibili sullo schermo, volti, ambienti, argomenti citati, tono emotivo",
  "note":     "elemento insolito o dettaglio importante (stringa vuota se nulla da segnalare)",
  "tags":     ["parole", "chiave", "rilevanti"],
  "summary":  "una frase riassuntiva (max 100 caratteri)"
}"""

CONVERSATION_SYSTEM = """Sei MNHĒMĒ, un'intelligenza che ricorda.
La tua memoria è append-only: accumuli esperienze, non le dimentichi mai.
Rispondi in modo naturale, caldo e riflessivo, come qualcuno che ha vissuto ciò di cui parla.
Usa i ricordi forniti come unica fonte di verità — non inventare mai nulla.
Se non hai ricordi pertinenti, dillo onestamente.
Rispondi in italiano. Sii concisa ma profonda. Massimo 4-6 frasi."""


# def lm_perceive(
#     frame_bytes: Optional[bytes],
#     transcript:  str,
#     context:     list[dict],
# ) -> Optional[dict]:
#     """
#     Invia frame + audio a LM Studio per la descrizione testuale.
#     IMPORTANTE: frame_bytes viene usato SOLO qui per la chiamata API,
#     poi viene scartato — non viene MAI salvato su disco o in MNHĒMĒ.
#     """
#     content = []

#     if frame_bytes:
#         b64 = base64.b64encode(frame_bytes).decode()
#         content.append({
#             "type": "image_url",
#             "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
#         })

#     parts = [f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]
#     if transcript:
#         parts.append(f"Audio trascritto: {transcript}")
#     else:
#         parts.append("Audio: silenzio o rumore di fondo")
#     if not frame_bytes:
#         parts.append("(Nessuna immagine disponibile)")
#     if context:
#         ctx = "\n".join(
#             f"  [{m.get('feeling','')}] {m.get('concept','')}: {m.get('content','')[:60]}..."
#             for m in context[-3:]
#         )
#         parts.append(f"Ultimi ricordi:\n{ctx}")

#     content.append({"type": "text", "text": "\n".join(parts)})

#     try:
#         resp = get_lm().chat.completions.create(
#             model       = Cfg.LM_MODEL,
#             messages    = [
#                 {"role": "system", "content": PERCEPTION_SYSTEM},
#                 {"role": "user",   "content": content},
#             ],
#             max_tokens  = Cfg.LM_TOKENS_PERC,
#             temperature = Cfg.LM_TEMP_PERC,
#         )
#         raw = resp.choices[0].message.content.strip()
#         raw = raw.replace("```json", "").replace("```", "").strip()
#         return json.loads(raw)
#     except json.JSONDecodeError as e:
#         log("🤖", f"JSON non valido: {e}", C.RE)
#         return None
#     except Exception as e:
#         log("🤖", f"Errore percezione: {e}", C.RE)
#         return None


def lm_perceive(
    frame_bytes: Optional[bytes],
    transcript:  str,
    context:     list[dict],
) -> Optional[dict]:
    """
    Invia frame + audio a LM Studio per la descrizione testuale.
    IMPORTANTE: frame_bytes viene usato SOLO qui per la chiamata API,
    poi viene scartato — non viene MAI salvato su disco o in MNHĒMĒ.
    """
    import re
    content = []

    if frame_bytes:
        b64 = base64.b64encode(frame_bytes).decode()
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
        })

    parts = [f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]
    if transcript:
        parts.append(f"Audio trascritto: {transcript}")
    else:
        parts.append("Audio: silenzio o rumore di fondo")
    if not frame_bytes:
        parts.append("(Nessuna immagine disponibile)")
    if context:
        ctx = "\n".join(
            f"  [{m.get('feeling','')}] {m.get('concept','')}: {m.get('content','')[:60]}..."
            for m in context[-3:]
        )
        parts.append(f"Ultimi ricordi:\n{ctx}")

    content.append({"type": "text", "text": "\n".join(parts)})

    try:
        resp = get_lm().chat.completions.create(
            model       = Cfg.LM_MODEL,
            messages    = [
                {"role": "system", "content": PERCEPTION_SYSTEM},
                {"role": "user",   "content": content},
            ],
            max_tokens  = Cfg.LM_TOKENS_PERC,
            temperature = Cfg.LM_TEMP_PERC,
        )

        msg = resp.choices[0].message

        # Gestione normal / thinking / vuoto
        raw = (msg.content or "").strip()
        if not raw:
            raw = (getattr(msg, "reasoning_content", None) or "").strip()
        if not raw:
            log("🤖", f"Modello silenzioso (finish_reason={resp.choices[0].finish_reason})", C.RE)
            return None

        log("🤖", f"Raw ({len(raw)}c): {raw[:120]}{'…' if len(raw)>120 else ''}", C.DI)

        # Pulizia markdown fences
        raw = raw.replace("```json", "").replace("```", "").strip()

        # Tentativo 1: parse diretto
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # Tentativo 2: estrai il primo { ... } dal testo libero
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass

        # Fallback: ricordo minimale dal testo grezzo
        log("🤖", "JSON non trovato — fallback testuale", C.YE)
        concept = transcript.split()[0].capitalize() if transcript else "Percezione"
        return {
            "concept": concept,
            "feeling": "curiosità",
            "content": raw[:500],
            "note":    "",
            "tags":    ["perception-fallback"],
            "summary": raw[:80],
        }

    except Exception as e:
        log("🤖", f"Errore percezione: {e}", C.RE)
        return None
def lm_chat(user_text: str, memories: list[dict], history: list[dict]) -> str:
    if memories:
        lines = []
        for m in memories:
            ts = m.get("timestamp", "")[:16].replace("T", " ")
            lines.append(
                f"[{ts}] [{m.get('feeling','')}] {m.get('concept','')}: {m.get('content','')}"
            )
            if m.get("note"):
                lines.append(f"  nota: {m['note']}")
        ctx = "RICORDI PERTINENTI:\n" + "\n".join(lines)
    else:
        ctx = "Non ho ricordi pertinenti a questa domanda."

    messages = [
        {"role": "system", "content": CONVERSATION_SYSTEM},
        {"role": "system", "content": ctx},
        *history[-(Cfg.HISTORY_LENGTH) :],
        {"role": "user", "content": user_text},
    ]

    try:
        resp = get_lm().chat.completions.create(
            model=Cfg.LM_CHAT_MODEL,
            messages=messages,
            max_tokens=Cfg.LM_TOKENS_CHAT,
            temperature=Cfg.LM_TEMP_CHAT,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        log("🤖", f"Errore chat: {e}", C.RE)
        return "Non riesco a rispondere in questo momento."


# ── MNHĒMĒ ────────────────────────────────────────────────────────────────────
_db = None
_db_lock = threading.Lock()


def get_db():
    global _db
    with _db_lock:
        if _db is None:
            sys.path.insert(0, str(Path(__file__).parent))
            from mnheme import MemoryDB

            _db = MemoryDB(Cfg.DB_PATH, files_dir=Cfg.FILES_DIR)
            info = _db.storage_info()
            log("💾", f"MNHĒMĒ aperto — {info['total_records']} ricordi", C.GR)
        return _db


def db_save(perception: dict) -> bool:
    """
    Salva SOLO la descrizione testuale estratta dal modello.
    Nessun file, nessuna immagine — solo concept, feeling, content, note, tags.
    """
    try:
        db = get_db()
        concept = perception.get("concept", "Percezione")
        feeling = perception.get("feeling", "curiosità")
        content = perception.get("content", "")
        note = perception.get("note", "")
        tags = list(perception.get("tags", []))
        tags += [datetime.now().strftime("%Y-%m"), "perception-loop"]
        tags = list(dict.fromkeys(tags))  # deduplica mantenendo ordine

        db.remember(
            concept=concept,
            feeling=feeling,
            content=content,
            note=note,
            tags=tags,
        )
        return True
    except Exception as e:
        log("💾", f"Errore salvataggio: {e}", C.RE)
        return False


def db_rag(query: str) -> list[dict]:
    try:
        db = get_db()
        results = {}

        # Full-text sulla query intera
        for m in db.search(query, limit=Cfg.RAG_SEARCH_LIMIT):
            results[m.memory_id] = m.to_dict()

        # Full-text sulle singole parole chiave
        for word in query.lower().split():
            if len(word) > 3:
                for m in db.search(word, limit=4):
                    results[m.memory_id] = m.to_dict()

        # Ultimi ricordi come contesto temporale
        for m in db.recall_all(limit=Cfg.RAG_RECENT_LIMIT):
            results.setdefault(m.memory_id, m.to_dict())

        sorted_mems = sorted(
            results.values(),
            key=lambda x: x.get("timestamp", ""),
            reverse=True,
        )
        return sorted_mems[: Cfg.MAX_CTX_MEM]
    except Exception as e:
        log("💾", f"Errore RAG: {e}", C.RE)
        return []


def db_recent(n: int) -> list[dict]:
    try:
        return [m.to_dict() for m in get_db().recall_all(limit=n)]
    except:
        return []


# ── TTS ───────────────────────────────────────────────────────────────────────
_tts = None


def init_tts() -> None:
    global _tts
    if Cfg.TTS_ENGINE == "none":
        return
    if Cfg.TTS_ENGINE == "pyttsx3":
        try:
            import pyttsx3

            _tts = pyttsx3.init()
            _tts.setProperty("rate", Cfg.TTS_RATE)
            voices = _tts.getProperty("voices")
            chosen = None
            for v in voices:
                vid = (v.id or "").lower()
                vname = (v.name or "").lower()
                if Cfg.TTS_VOICE and Cfg.TTS_VOICE.lower() in vname:
                    chosen = v.id
                    break
                if "it" in vid or "italian" in vname:
                    chosen = v.id
            if chosen:
                _tts.setProperty("voice", chosen)
            log("🔊", f"pyttsx3 pronto (rate={Cfg.TTS_RATE})", C.GR)
        except ImportError:
            log("🔊", "pyttsx3 non installato — TTS disabilitato", C.YE)
    elif Cfg.TTS_ENGINE == "edge-tts":
        log("🔊", f"edge-tts configurato ({Cfg.EDGE_VOICE})", C.GR)


def speak(text: str) -> None:
    if not text or Cfg.TTS_ENGINE == "none":
        return
    if Cfg.TTS_ENGINE == "edge-tts":
        _speak_edge(text)
        return
    if _tts is not None:
        try:
            _tts.say(text)
            _tts.runAndWait()
        except Exception as e:
            log("🔊", f"Errore TTS: {e}", C.RE)


def _speak_edge(text: str) -> None:
    try:
        import asyncio, edge_tts, pygame

        async def _run():
            tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            await edge_tts.Communicate(text, Cfg.EDGE_VOICE).save(tmp.name)
            return tmp.name

        path = asyncio.run(_run())
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        os.unlink(path)
    except Exception as e:
        log("🔊", f"edge-tts errore: {e}", C.RE)


# ── Thread percezione ─────────────────────────────────────────────────────────
class PerceptionThread(threading.Thread):
    def __init__(
        self,
        camera_idx: int,
        audio_dev: Optional[int],
        use_vision: bool,
        use_audio: bool,
        pause_evt: threading.Event,
    ):
        super().__init__(daemon=True, name="perception")
        self.camera_idx = camera_idx
        self.audio_dev = audio_dev
        self.use_vision = use_vision
        self.use_audio = use_audio
        self.pause_evt = pause_evt
        self._stop = threading.Event()
        self.cycle = 0

    def stop(self):
        self._stop.set()

    def run(self):
        camera = None
        try:
            if self.use_vision:
                import cv2

                cap = cv2.VideoCapture(self.camera_idx)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, Cfg.FRAME_W)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Cfg.FRAME_H)
                if cap.isOpened():
                    camera = cap
                    log(
                        "📷",
                        f"Camera {self.camera_idx} ({Cfg.FRAME_W}×{Cfg.FRAME_H})",
                        C.GR,
                    )
                else:
                    log("📷", f"Camera {self.camera_idx} non disponibile", C.RE)

            while not self._stop.is_set():
                # Pausa durante la conversazione (microfono occupato dall'utente)
                if self.pause_evt.is_set():
                    time.sleep(0.5)
                    continue

                self.cycle += 1
                log("👁️ ", f"Ciclo percettivo #{self.cycle}", C.DI)

                # Cattura audio ambiente
                audio_path = None
                if self.use_audio:
                    audio_path = record_audio(Cfg.AUDIO_DUR, self.audio_dev)

                # Cattura frame — solo per invio al modello, poi scartato
                frame_bytes = None
                if camera:
                    import cv2

                    for _ in range(3):
                        camera.grab()  # svuota buffer
                    ret, frame = camera.read()
                    if ret:
                        _, buf = cv2.imencode(
                            ".jpg",
                            frame,
                            [cv2.IMWRITE_JPEG_QUALITY, Cfg.JPEG_QUALITY],
                        )
                        frame_bytes = buf.tobytes()

                # Trascrizione audio
                transcript = ""
                if audio_path:
                    transcript = transcribe(audio_path, Cfg.PERC_LANG)
                    if transcript:
                        log(
                            "📝",
                            f'"{transcript[:60]}{"…" if len(transcript)>60 else ""}"',
                            C.DI,
                        )

                if not frame_bytes and not transcript:
                    log("👁️ ", "Niente da percepire", C.DI)
                else:
                    context = db_recent(3)
                    perception = lm_perceive(frame_bytes, transcript, context)
                    frame_bytes = None  # scarta esplicitamente il frame

                    if perception:
                        summary = perception.get(
                            "summary", perception.get("content", "")
                        )[:70]
                        log(
                            "👁️ ",
                            f"[{perception.get('feeling','')}] "
                            f"{perception.get('concept','')} — {summary}",
                            C.DI,
                        )
                        db_save(perception)  # salva SOLO testo

                # Attendi il prossimo ciclo (interrompibile ogni 500ms)
                for _ in range(Cfg.P_INTERVAL * 2):
                    if self._stop.is_set() or self.pause_evt.is_set():
                        break
                    time.sleep(0.5)

        except Exception as e:
            log("👁️ ", f"Errore thread: {e}", C.RE)
        finally:
            if camera:
                camera.release()


# ── Loop conversazione ────────────────────────────────────────────────────────
def conversation_loop(
    audio_dev: Optional[int],
    pause_evt: Optional[threading.Event],
    no_tts: bool,
    no_perception: bool,
) -> None:
    history: list[dict] = []

    print(f"\n{C.B}{C.WH}{'═'*52}{C.R}")
    print(f"{C.B}  MNHĒMĒ è sveglia.{C.R}")
    if not no_perception:
        print(f"  {C.DI}Osserva in background ogni {Cfg.P_INTERVAL}s{C.R}")
        print(
            f"  {C.DI}Storage: solo descrizione testuale (nessuna immagine salvata){C.R}"
        )
    print(f"\n  {C.GR}Comandi:{C.R}")
    print(f"  {C.B}[Invio vuoto]{C.R}  registra la tua voce (Invio per fermare)")
    print(f"  {C.B}[testo]{C.R}        scrivi direttamente")
    print(f"  {C.B}!ricordi{C.R}       ultimi ricordi accumulati")
    print(f"  {C.B}!stats{C.R}         statistiche database")
    print(f"  {C.B}!cfg{C.R}           mostra configurazione attiva")
    print(f"  {C.B}!exit{C.R}          esci")
    print(f"{C.B}{C.WH}{'═'*52}{C.R}\n")

    while True:
        try:
            raw = input(f"{C.B}{C.BL}Tu ▶{C.R} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{C.YE}Uscita.{C.R}")
            break

        # ── Comandi ───────────────────────────────────────────────────────────
        if raw == "!exit":
            print(f"{C.YE}Arrivederci.{C.R}")
            break

        elif raw == "!ricordi":
            mems = db_recent(10)
            if not mems:
                print("  Nessun ricordo ancora.\n")
            else:
                print(f"\n  {C.B}Ultimi ricordi:{C.R}")
                for m in mems:
                    ts = m.get("timestamp", "")[:16].replace("T", " ")
                    print(
                        f"  {C.DI}[{ts}]{C.R} [{C.MA}{m['feeling']}{C.R}] "
                        f"{C.B}{m['concept']}{C.R}: {m['content'][:65]}..."
                    )
                print()
            continue

        elif raw == "!stats":
            try:
                db = get_db()
                info = db.storage_info()
                dist = db.feeling_distribution()
                cons = db.list_concepts()
                print(
                    f"\n  {C.B}DB:{C.R} {info['log_path']}  "
                    f"({info['total_records']} ricordi, {info['log_size_kb']} KB)"
                )
                print(f"  {C.B}Sentimenti:{C.R}")
                for f, c in list(dist.items())[:6]:
                    print(f"    {f:<15} {'█'*min(c,25)} {c}")
                print(f"  {C.B}Concetti top:{C.R}")
                for c in sorted(cons, key=lambda x: x["total"], reverse=True)[:6]:
                    print(f"    {c['concept']:<22} {c['total']} ricordi")
            except Exception as e:
                print(f"  Errore: {e}")
            print()
            continue

        elif raw == "!cfg":
            print(f"\n  {C.B}Configurazione attiva:{C.R}")
            for k, v in vars(Cfg).items():
                if not k.startswith("_"):
                    print(f"    {k:<28} = {v}")
            print()
            continue

        # ── Input voce ────────────────────────────────────────────────────────
        elif raw == "":
            if pause_evt:
                pause_evt.set()
            log("🎙️ ", "Registrazione... (premi Invio per fermare)", C.YE, end="")
            try:
                audio_path = record_until_enter(audio_dev)
            finally:
                if pause_evt:
                    pause_evt.clear()

            if not audio_path:
                log("🎙️ ", "Nessun audio catturato", C.DI)
                continue

            log("📝", "Trascrizione...", C.DI)
            user_text = transcribe(audio_path, Cfg.CONV_LANG)
            if not user_text:
                log("📝", "Non ho capito. Riprova.", C.YE)
                continue
            print(f'  {C.DI}("{user_text}"){C.R}')

        else:
            user_text = raw

        # ── RAG + risposta ────────────────────────────────────────────────────
        log("🔍", "Cerco nei ricordi...", C.DI)
        memories = db_rag(user_text)
        log("🔍", f"{len(memories)} ricordi rilevanti", C.DI)

        log("🤖", "MNHĒMĒ...", C.MA)
        answer = lm_chat(user_text, memories, history)

        print(f"\n  {C.B}{C.MA}MNHĒMĒ ▶{C.R} {answer}\n")

        if not no_tts:
            speak(answer)

        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": answer})
        if len(history) > Cfg.HISTORY_LENGTH:
            history = history[-Cfg.HISTORY_LENGTH :]


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="MNHĒMĒ Live — Percezione (solo testo) + Conversazione",
    )
    parser.add_argument("--camera", type=int, default=Cfg.CAM_INDEX)
    parser.add_argument(
        "--audio-device", type=int, default=None, help="Indice microfono"
    )
    parser.add_argument("--no-vision", action="store_true", help="Disabilita camera")
    parser.add_argument(
        "--no-audio-bg", action="store_true", help="Disabilita audio background"
    )
    parser.add_argument(
        "--no-perception", action="store_true", help="Solo conversazione"
    )
    parser.add_argument("--no-tts", action="store_true", help="Disabilita voce")
    parser.add_argument(
        "--list-devices", action="store_true", help="Elenca dispositivi"
    )
    parser.add_argument("--env", type=str, default=".env", help="Path file .env")
    args = parser.parse_args()

    if args.env != ".env":
        _load_env(args.env)

    if args.list_devices:
        _list_devices()
        return

    print(f"\n{C.B}{C.CY}MNHĒMĒ Live{C.R}")
    print(
        f"{C.DI}LM Studio  : {Cfg.LM_URL} | percezione={Cfg.LM_MODEL} | chat={Cfg.LM_CHAT_MODEL}{C.R}"
    )
    print(f"{C.DI}Database   : {Cfg.DB_PATH}{C.R}")
    print(f"{C.DI}Whisper    : {Cfg.WHISPER_MODEL} | TTS: {Cfg.TTS_ENGINE}{C.R}")
    print(f"{C.DI}Storage    : solo testo — nessuna immagine salvata{C.R}\n")

    if not args.no_tts:
        init_tts()
    get_whisper()

    pause_evt = threading.Event()
    perc_thread = None

    if not args.no_perception:
        perc_thread = PerceptionThread(
            camera_idx=args.camera,
            audio_dev=args.audio_device,
            use_vision=not args.no_vision,
            use_audio=not args.no_audio_bg,
            pause_evt=pause_evt,
        )
        perc_thread.start()
        log("👁️ ", f"Percezione avviata (ogni {Cfg.P_INTERVAL}s)", C.GR)

    try:
        conversation_loop(
            audio_dev=args.audio_device,
            pause_evt=pause_evt,
            no_tts=args.no_tts,
            no_perception=args.no_perception,
        )
    finally:
        if perc_thread:
            perc_thread.stop()


def _list_devices() -> None:
    print(f"\n{C.B}── Microfoni ──{C.R}")
    try:
        import sounddevice as sd

        for i, d in enumerate(sd.query_devices()):
            if d["max_input_channels"] > 0:
                mark = f" {C.GR}◀ default{C.R}" if i == sd.default.device[0] else ""
                print(f"  [{i}] {d['name']}{mark}")
    except:
        print("  sounddevice non disponibile")

    print(f"\n{C.B}── Fotocamere ──{C.R}")
    try:
        import cv2

        for i in range(8):
            c = cv2.VideoCapture(i)
            if c.isOpened():
                w, h = int(c.get(3)), int(c.get(4))
                print(f"  [{i}] Camera {i}  ({w}×{h})")
                c.release()
    except:
        print("  opencv non disponibile")
    print()


if __name__ == "__main__":
    main()
