"""
conversation_ingester.py — MNHEME Conversation Ingestion Pipeline
==================================================================
Estrae ricordi strutturati da conversazioni reali (WhatsApp, email,
Telegram, iMessage, testo generico) e li inserisce in un database MNHEME.

Il pipeline in 4 fasi
---------------------
  1. PARSE      — legge il formato sorgente e produce MessageChunk normalizzati
  2. FILTER     — rimuove messaggi irrilevanti, separa "io" dagli altri
  3. SEGMENT    — raggruppa i messaggi in episodi narrativi coerenti
  4. EXTRACT    — LLM analizza ogni episodio e produce 0-N ricordi MNHEME

Fonti supportate
----------------
  --source whatsapp    export .txt o .zip di WhatsApp
  --source gmail       file .mbox o directory di .eml
  --source telegram    export JSON di Telegram Desktop
  --source imessage    export .txt di iMessage o backup SQLite
  --source text        qualsiasi file .txt/.md con conversazione generica

Utilizzo
--------
    python conversation_ingester.py chat.txt --me "Mario" --source whatsapp
    python conversation_ingester.py export.json --me "Mario Rossi" --source telegram
    python conversation_ingester.py mail.mbox --me "mario@example.com" --source gmail
    python conversation_ingester.py . --me "Mario" --source whatsapp --dry-run

    # Con DB e provider espliciti
    python conversation_ingester.py chat.txt \\
        --me "Mario" --source whatsapp \\
        --db vita.mnheme --provider lm-studio \\
        --min-length 3 --batch-size 8 --verbose

Dipendenze
----------
    Solo stdlib Python 3.10+ — nessun pip install.
    mnheme.py e llm_provider.py devono essere nel path.
"""

from __future__ import annotations

import argparse
import email
import email.policy
import json
import mailbox
import os
import re
import sqlite3
import sys
import textwrap
import time
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

# ── Import progetto ───────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # root progetto

try:
    from mnheme       import MemoryDB, Feeling
    from llm_provider import LLMProvider, load_env
    VALID_FEELINGS = [f.value for f in Feeling]
except ImportError as e:
    print(f"Errore import: {e}")
    print("Assicurati che mnheme.py e llm_provider.py siano nel path.")
    sys.exit(1)

# ── ANSI ─────────────────────────────────────────────────────
GRN="\033[32m"; RED="\033[31m"; YLW="\033[33m"
CYN="\033[36m"; DIM="\033[2m"; BOLD="\033[1m"; NC="\033[0m"
def _c(col,t): return f"{col}{t}{NC}"
def ok(m):   print(f"  {_c(GRN,'✓')}  {m}")
def err(m):  print(f"  {_c(RED,'✗')}  {m}", file=sys.stderr)
def info(m): print(f"  {_c(CYN,'→')}  {m}")
def warn(m): print(f"  {_c(YLW,'⚠')}  {m}")


# ═══════════════════════════════════════════════════════════════
# DATA MODEL
# ═══════════════════════════════════════════════════════════════

@dataclass
class Message:
    """Messaggio normalizzato da qualsiasi sorgente."""
    sender    : str               # nome o indirizzo del mittente
    text      : str               # testo del messaggio
    timestamp : datetime          # quando è stato inviato
    is_me     : bool = False      # True se il mittente siamo noi
    source    : str = ""          # whatsapp | telegram | gmail | imessage | text
    thread_id : str = ""          # id conversazione/thread
    media_type: str = "text"      # text | image | audio | video | doc
    media_hint: str = ""          # descrizione del media se non testo


@dataclass
class Episode:
    """
    Gruppo di messaggi che forma un episodio narrativo coerente.
    Unità di analisi per il LLM — ogni episodio può produrre 0-N ricordi.
    """
    messages    : list[Message]
    start_time  : datetime
    end_time    : datetime
    participants: list[str]
    thread_id   : str = ""

    @property
    def my_messages(self) -> list[Message]:
        return [m for m in self.messages if m.is_me]

    @property
    def text_for_llm(self) -> str:
        lines = []
        for m in self.messages:
            ts   = m.timestamp.strftime("%d/%m/%Y %H:%M")
            who  = "IO" if m.is_me else m.sender
            text = m.text if m.media_type == "text" else f"[{m.media_type.upper()}: {m.media_hint}]"
            lines.append(f"[{ts}] {who}: {text}")
        return "\n".join(lines)


@dataclass
class ExtractedMemory:
    """Ricordo estratto dal LLM da un episodio."""
    concept    : str
    feeling    : str
    content    : str
    note       : str
    tags       : list[str]
    timestamp  : str          # ISO 8601
    confidence : str          # alta | media | bassa


# ═══════════════════════════════════════════════════════════════
# PARSERS — una classe per sorgente
# ═══════════════════════════════════════════════════════════════

class WhatsAppParser:
    """
    Parser per export WhatsApp (.txt o .zip).

    Formati supportati:
      [DD/MM/YYYY, HH:MM:SS] Mittente: Testo
      [DD/MM/YYYY, HH:MM] Mittente: Testo
      DD/MM/YY, HH:MM - Mittente: Testo  (formato US)
    """

    # Pattern per righe di messaggio WhatsApp
    _PATTERNS = [
        # [01/01/2024, 14:30:45] Nome: testo
        re.compile(
            r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?)\]\s*([^:]+):\s*(.+)$"
        ),
        # 01/01/2024, 14:30 - Nome: testo
        re.compile(
            r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.+)$"
        ),
    ]

    _SYSTEM_MSGS = re.compile(
        r"(Messages and calls are end-to-end encrypted|"
        r"I messaggi sono protetti|"
        r"ha aggiunto|ha rimosso|ha lasciato il gruppo|"
        r"<Media omesso>|<Media omitted>|"
        r"This message was deleted|Questo messaggio è stato eliminato)",
        re.IGNORECASE
    )

    def parse(self, path: Path) -> Iterator[Message]:
        if path.suffix == ".zip":
            yield from self._parse_zip(path)
        else:
            yield from self._parse_txt(path.read_text("utf-8", errors="replace"))

    def _parse_zip(self, path: Path) -> Iterator[Message]:
        with zipfile.ZipFile(path) as zf:
            for name in zf.namelist():
                if name.endswith(".txt"):
                    text = zf.read(name).decode("utf-8", errors="replace")
                    yield from self._parse_txt(text)

    def _parse_txt(self, text: str) -> Iterator[Message]:
        current: Optional[dict] = None

        for line in text.splitlines():
            matched = False
            for pat in self._PATTERNS:
                m = pat.match(line)
                if m:
                    # Emetti il messaggio precedente
                    if current:
                        yield from self._emit(current)
                    date_s, time_s, sender, body = m.groups()
                    current = {
                        "date": date_s, "time": time_s,
                        "sender": sender.strip(), "text": body.strip()
                    }
                    matched = True
                    break

            if not matched and current and line.strip():
                # Continuazione del messaggio precedente
                current["text"] += "\n" + line.strip()

        if current:
            yield from self._emit(current)

    def _emit(self, d: dict) -> Iterator[Message]:
        text = d["text"].strip()
        if not text or self._SYSTEM_MSGS.search(text):
            return

        # Riconosce media
        media_type, media_hint = "text", ""
        if re.match(r"<.*omesso>|<.*omitted>", text, re.I):
            return
        if re.match(r"\[?foto\]?|\[?image\]?", text, re.I):
            media_type, media_hint = "image", text
            text = ""
        elif re.match(r"\[?video\]?", text, re.I):
            media_type, media_hint = "video", text
            text = ""
        elif re.match(r"\[?audio\]?|\[?voice\]?|\[?ptt\]?", text, re.I):
            media_type, media_hint = "audio", text
            text = ""
        elif re.match(r"\[?doc\]?|\[?file\]?", text, re.I):
            media_type, media_hint = "doc", text
            text = ""

        if media_type == "text" and not text:
            return

        ts = self._parse_dt(d["date"], d["time"])
        yield Message(
            sender     = d["sender"],
            text       = text,
            timestamp  = ts,
            source     = "whatsapp",
            media_type = media_type,
            media_hint = media_hint,
        )

    @staticmethod
    def _parse_dt(date_s: str, time_s: str) -> datetime:
        for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M",
                    "%d/%m/%y %H:%M:%S", "%d/%m/%y %H:%M",
                    "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M",
                    "%m/%d/%y %H:%M:%S", "%m/%d/%y %H:%M"):
            try:
                return datetime.strptime(f"{date_s} {time_s}", fmt)
            except ValueError:
                continue
        return datetime.now()


class TelegramParser:
    """
    Parser per export JSON di Telegram Desktop.
    Supporta chat private, gruppi e canali.
    """

    def parse(self, path: Path) -> Iterator[Message]:
        data = json.loads(path.read_text("utf-8"))
        msgs = data.get("messages", [])
        for m in msgs:
            yield from self._parse_msg(m)

    def _parse_msg(self, m: dict) -> Iterator[Message]:
        if m.get("type") not in ("message", None):
            return

        sender = m.get("from") or m.get("actor") or "Sconosciuto"
        ts_str = m.get("date", "")
        try:
            ts = datetime.fromisoformat(ts_str)
        except ValueError:
            ts = datetime.now()

        # Testo: può essere stringa o lista di entità
        text_raw = m.get("text", "")
        if isinstance(text_raw, list):
            text = "".join(
                t if isinstance(t, str) else t.get("text", "")
                for t in text_raw
            )
        else:
            text = str(text_raw)

        # Media
        media_type, media_hint = "text", ""
        mtype = m.get("media_type") or m.get("file", "")
        if "photo" in str(mtype).lower() or m.get("photo"):
            media_type, media_hint = "image", "foto"
        elif "video" in str(mtype).lower():
            media_type, media_hint = "video", "video"
        elif "voice" in str(mtype).lower() or "audio" in str(mtype).lower():
            media_type, media_hint = "audio", "messaggio vocale"
        elif mtype and media_type == "text":
            media_type, media_hint = "doc", str(mtype)

        if not text and media_type == "text":
            return

        yield Message(
            sender     = sender,
            text       = text.strip(),
            timestamp  = ts,
            source     = "telegram",
            thread_id  = str(m.get("id", "")),
            media_type = media_type,
            media_hint = media_hint,
        )


class GmailParser:
    """
    Parser per file .mbox (export Gmail Takeout) o directory di .eml.
    Estrae solo le email inviate da o a "me".
    """

    def parse(self, path: Path) -> Iterator[Message]:
        if path.is_dir():
            for eml in path.glob("**/*.eml"):
                yield from self._parse_eml_file(eml)
        elif path.suffix == ".mbox":
            yield from self._parse_mbox(path)
        elif path.suffix == ".eml":
            yield from self._parse_eml_file(path)

    def _parse_mbox(self, path: Path) -> Iterator[Message]:
        mbox = mailbox.mbox(str(path))
        for msg in mbox:
            yield from self._parse_email(msg)

    def _parse_eml_file(self, path: Path) -> Iterator[Message]:
        try:
            with open(path, "rb") as f:
                msg = email.message_from_binary_file(f, policy=email.policy.default)
            yield from self._parse_email(msg)
        except Exception:
            pass

    def _parse_email(self, msg) -> Iterator[Message]:
        try:
            from_addr = str(msg.get("From", ""))
            subject   = str(msg.get("Subject", ""))
            date_str  = str(msg.get("Date", ""))

            try:
                from email.utils import parsedate_to_datetime
                ts = parsedate_to_datetime(date_str)
            except Exception:
                ts = datetime.now()

            # Estrai corpo testo
            body = ""
            if hasattr(msg, "get_body"):
                part = msg.get_body(preferencelist=("plain", "html"))
                if part:
                    body = part.get_content()
            else:
                if msg.get_content_type() == "text/plain":
                    body = msg.get_payload(decode=True).decode("utf-8", errors="replace")

            # Pulizia: rimuove quote (linee che iniziano con >)
            lines = [l for l in body.splitlines() if not l.startswith(">")]
            body  = "\n".join(lines).strip()

            # Aggiunge subject come contesto
            if subject and body:
                body = f"[{subject}]\n{body}"
            elif subject:
                body = subject

            if not body:
                return

            yield Message(
                sender    = from_addr,
                text      = body[:2000],   # limita dimensione
                timestamp = ts,
                source    = "gmail",
                thread_id = str(msg.get("Message-ID", "")),
            )
        except Exception:
            pass


class IMessageParser:
    """
    Parser per export iMessage.
    Supporta:
    - .txt export da app terze (es. iExplorer)
    - chat.db SQLite (backup iPhone)
    """

    # Pattern txt generico: HH:MM  Nome: testo
    _LINE = re.compile(r"^(\d{1,2}:\d{2}(?::\d{2})?)\s+([^:]+):\s*(.+)$")
    # Pattern con data: DD/MM/YYYY HH:MM  Nome: testo
    _LINE_DATE = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4})\s+(\d{1,2}:\d{2})\s+([^:]+):\s*(.+)$")

    def parse(self, path: Path) -> Iterator[Message]:
        if path.suffix in (".db", ".sqlite"):
            yield from self._parse_sqlite(path)
        else:
            yield from self._parse_txt(path)

    def _parse_txt(self, path: Path) -> Iterator[Message]:
        text = path.read_text("utf-8", errors="replace")
        today = datetime.now().date()

        for line in text.splitlines():
            m = self._LINE_DATE.match(line)
            if m:
                date_s, time_s, sender, body = m.groups()
                try:
                    ts = datetime.strptime(f"{date_s} {time_s}", "%d/%m/%Y %H:%M")
                except ValueError:
                    ts = datetime.now()
                yield Message(sender=sender.strip(), text=body.strip(),
                              timestamp=ts, source="imessage")
                continue

            m = self._LINE.match(line)
            if m:
                time_s, sender, body = m.groups()
                try:
                    ts = datetime.strptime(f"{today} {time_s}", "%Y-%m-%d %H:%M")
                except ValueError:
                    ts = datetime.now()
                yield Message(sender=sender.strip(), text=body.strip(),
                              timestamp=ts, source="imessage")

    def _parse_sqlite(self, path: Path) -> Iterator[Message]:
        try:
            conn = sqlite3.connect(str(path))
            cur  = conn.cursor()
            cur.execute("""
                SELECT
                    m.text,
                    m.date / 1000000000.0 + 978307200 as unix_ts,
                    m.is_from_me,
                    h.id as contact
                FROM message m
                LEFT JOIN handle h ON m.handle_id = h.rowid
                WHERE m.text IS NOT NULL AND m.text != ''
                ORDER BY m.date
            """)
            for row in cur.fetchall():
                text, unix_ts, is_from_me, contact = row
                try:
                    ts = datetime.fromtimestamp(unix_ts)
                except (ValueError, OSError):
                    ts = datetime.now()
                yield Message(
                    sender    = "Me" if is_from_me else (contact or "Contatto"),
                    text      = str(text),
                    timestamp = ts,
                    is_me     = bool(is_from_me),
                    source    = "imessage",
                )
            conn.close()
        except Exception as e:
            warn(f"SQLite parse error: {e}")


class TextParser:
    """
    Parser generico per file .txt/.md con formato Speaker: Testo.
    Fallback per qualsiasi formato non riconosciuto.
    """

    _LINE = re.compile(r"^([A-Za-zÀ-ÿ][\w\s]{0,30}):\s*(.+)$")

    def parse(self, path: Path) -> Iterator[Message]:
        text = path.read_text("utf-8", errors="replace")
        ts   = datetime.now()

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            m = self._LINE.match(line)
            if m:
                sender, body = m.groups()
                yield Message(sender=sender.strip(), text=body.strip(),
                              timestamp=ts, source="text")
            # Linee senza speaker: ignorate o attribuite all'ultimo speaker noto


# ═══════════════════════════════════════════════════════════════
# SEGMENTER — raggruppa messaggi in episodi
# ═══════════════════════════════════════════════════════════════

class ConversationSegmenter:
    """
    Raggruppa i messaggi in episodi narrativi.

    Un nuovo episodio inizia quando:
    - Passa più di `gap_hours` ore dall'ultimo messaggio
    - L'episodio supera `max_messages` messaggi
    - Cambia il thread/conversazione

    Solo gli episodi che contengono almeno un messaggio di "me"
    vengono considerati — gli altri vengono scartati.
    """

    def __init__(
        self,
        gap_hours    : float = 4.0,
        max_messages : int   = 40,
        min_my_msgs  : int   = 1,
    ) -> None:
        self.gap_seconds  = gap_hours * 3600
        self.max_messages = max_messages
        self.min_my_msgs  = min_my_msgs

    def segment(self, messages: list[Message]) -> list[Episode]:
        if not messages:
            return []

        episodes: list[Episode] = []
        current: list[Message]  = [messages[0]]

        for msg in messages[1:]:
            prev = current[-1]
            gap  = (msg.timestamp - prev.timestamp).total_seconds()

            split = (
                gap > self.gap_seconds or
                len(current) >= self.max_messages or
                (msg.thread_id and msg.thread_id != prev.thread_id)
            )

            if split:
                ep = self._make_episode(current)
                if ep:
                    episodes.append(ep)
                current = [msg]
            else:
                current.append(msg)

        if current:
            ep = self._make_episode(current)
            if ep:
                episodes.append(ep)

        return episodes

    def _make_episode(self, messages: list[Message]) -> Optional[Episode]:
        my_msgs = [m for m in messages if m.is_me]
        if len(my_msgs) < self.min_my_msgs:
            return None
        participants = list({m.sender for m in messages})
        return Episode(
            messages     = messages,
            start_time   = messages[0].timestamp,
            end_time     = messages[-1].timestamp,
            participants = participants,
            thread_id    = messages[0].thread_id,
        )


# ═══════════════════════════════════════════════════════════════
# EXTRACTOR — LLM estrae ricordi dagli episodi
# ═══════════════════════════════════════════════════════════════

_SYSTEM_EXTRACTOR = (
    "Sei un analista di memoria autobiografica. "
    "Il tuo compito è estrarre ricordi emotivamente significativi "
    "da conversazioni reali, SOLO dal punto di vista della persona 'IO'. "
    "Ignora i messaggi degli altri — interessano solo come contesto per comprendere "
    "cosa ho vissuto IO. "
    "Rispondi SEMPRE e SOLO con JSON valido. Nessun testo extra."
)


def _build_extraction_prompt(
    episode   : Episode,
    my_name   : str,
    feelings  : list[str],
) -> str:
    duration_min = int((episode.end_time - episode.start_time).total_seconds() / 60)
    others       = [p for p in episode.participants if p != my_name]

    return textwrap.dedent(f"""
        CONVERSAZIONE ({episode.start_time.strftime('%d/%m/%Y %H:%M')} — durata: {duration_min} min)
        Partecipanti: IO ({my_name}), {', '.join(others) if others else 'nessuno'}

        {episode.text_for_llm}

        ---
        Analizza questa conversazione dal punto di vista di IO ({my_name}).

        COMPITO:
        Estrai i ricordi emotivamente significativi vissuti da IO.
        Un ricordo è significativo se rivela qualcosa su come IO si sente,
        cosa gli/le importa, cosa sta attraversando nella vita.

        IGNORA:
        - Messaggi puramente logistici ("ci vediamo alle 5")
        - Scambi di cortesia senza contenuto emotivo
        - Messaggi degli altri che non impattano su IO

        REGOLE:
        - concept: UNA sola parola (sostantivo, es: "divorzio", "promozione", "salute")
        - feeling: ESATTO tra: {json.dumps(feelings, ensure_ascii=False)}
        - content: in prima persona come IO, specifico e concreto (max 200 caratteri)
        - note: contesto della conversazione (con chi, quando, dove)
        - tags: 2-4 tag minuscolo
        - timestamp: data ISO 8601 della conversazione ({episode.start_time.isoformat()})
        - confidence: "alta" | "media" | "bassa"

        Se non ci sono ricordi significativi, ritorna un array vuoto [].

        OUTPUT — array JSON (0-3 ricordi max per episodio):
        [
          {{
            "concept": "parolasingola",
            "feeling": "uno_dei_valori_validi",
            "content": "In prima persona, cosa ho vissuto/sentito...",
            "note": "Conversazione con [nome], [data/contesto]",
            "tags": ["tag1", "tag2"],
            "timestamp": "{episode.start_time.isoformat()}",
            "confidence": "alta"
          }}
        ]
    """).strip()


def _parse_extracted(raw: str) -> list[dict]:
    """Parse JSON dalla risposta LLM con fallback robusto."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = "\n".join(
            l for l in raw.splitlines() if not l.strip().startswith("```")
        ).strip()
    try:
        result = json.loads(raw)
        return result if isinstance(result, list) else []
    except json.JSONDecodeError:
        m = re.search(r"\[\s*\{.*?\}\s*\]", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass
    return []


def _validate_memory(item: dict, episode: Episode) -> Optional[ExtractedMemory]:
    """Valida e normalizza un ricordo estratto."""
    concept = str(item.get("concept", "")).strip().split()[0].lower()
    if not concept:
        return None
    concept = re.sub(r"[^\w]", "", concept, flags=re.UNICODE) or "ricordo"

    feeling = str(item.get("feeling", "")).strip().replace(" ", "_")
    if feeling not in VALID_FEELINGS:
        feeling_norm = feeling.lower()
        closest = next((f for f in VALID_FEELINGS if f in feeling_norm or feeling_norm in f), None)
        feeling = closest or "nostalgia"

    content = str(item.get("content", "")).strip()
    if not content or len(content) < 10:
        return None
    if len(content) > 400:
        content = content[:397] + "…"

    note = str(item.get("note", "")).strip()[:200]

    raw_tags = item.get("tags", [])
    if isinstance(raw_tags, str):
        raw_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    tags = [str(t).strip().lower() for t in raw_tags if t][:6]

    # Aggiunge tag sorgente
    if episode.messages:
        src = episode.messages[0].source
        if src and src not in tags:
            tags.append(src)

    confidence = str(item.get("confidence", "media")).strip()

    return ExtractedMemory(
        concept    = concept,
        feeling    = feeling,
        content    = content,
        note       = note,
        tags       = tags,
        timestamp  = item.get("timestamp", episode.start_time.isoformat()),
        confidence = confidence,
    )


# ═══════════════════════════════════════════════════════════════
# INGESTION PIPELINE
# ═══════════════════════════════════════════════════════════════

class ConversationIngester:
    """
    Pipeline completo: conversazione → ricordi MNHEME.

    Parametri
    ---------
    db         : database MNHEME di destinazione
    llm        : provider LLM
    my_name    : come appare il nome di "me" nella conversazione
    min_length : lunghezza minima testo per considerare un messaggio
    batch_size : episodi per batch LLM (per throttling)
    dry_run    : se True, genera senza scrivere nel DB
    verbose    : output dettagliato
    """

    def __init__(
        self,
        db         : MemoryDB,
        llm        : LLMProvider,
        my_name    : str,
        *,
        min_length : int   = 5,
        batch_size : int   = 5,
        dry_run    : bool  = False,
        verbose    : bool  = False,
        max_retries: int   = 3,
        skip_low_conf: bool = False,
    ) -> None:
        self._db           = db
        self._llm          = llm
        self._my_name      = my_name.lower()
        self._min_length   = min_length
        self._batch_size   = batch_size
        self._dry_run      = dry_run
        self._verbose      = verbose
        self._max_retries  = max_retries
        self._skip_low     = skip_low_conf
        self._segmenter    = ConversationSegmenter()

        # Stats
        self.stats = {
            "messages_parsed"  : 0,
            "messages_filtered": 0,
            "episodes"         : 0,
            "memories_extracted": 0,
            "memories_saved"   : 0,
            "errors"           : 0,
        }

    # ── Fase 1: Parse ─────────────────────────────────────────

    def _get_parser(self, source: str):
        parsers = {
            "whatsapp": WhatsAppParser(),
            "telegram": TelegramParser(),
            "gmail"   : GmailParser(),
            "imessage": IMessageParser(),
            "text"    : TextParser(),
        }
        return parsers.get(source, TextParser())

    # ── Fase 2: Filter ────────────────────────────────────────

    def _filter_messages(self, messages: list[Message]) -> list[Message]:
        """Filtra e marca is_me sui messaggi."""
        filtered = []
        for m in messages:
            # Filtra per lunghezza minima
            if m.media_type == "text" and len(m.text) < self._min_length:
                continue
            # Marca is_me
            m.is_me = self._my_name in m.sender.lower()
            filtered.append(m)
        return filtered

    # ── Fase 3-4: Segment + Extract ──────────────────────────

    def _extract_from_episode(self, episode: Episode) -> list[ExtractedMemory]:
        """LLM estrae ricordi da un episodio."""
        prompt = _build_extraction_prompt(
            episode, self._my_name, VALID_FEELINGS
        )

        for attempt in range(1, self._max_retries + 1):
            try:
                raw  = self._llm.complete(
                    _SYSTEM_EXTRACTOR, prompt,
                    temperature=0.3, max_tokens=1024
                )
                items = _parse_extracted(raw)
                break
            except Exception as e:
                if attempt == self._max_retries:
                    self.stats["errors"] += 1
                    if self._verbose:
                        warn(f"Estrazione fallita: {e}")
                    return []
                time.sleep(2 ** attempt)

        memories = []
        for item in items:
            mem = _validate_memory(item, episode)
            if mem is None:
                continue
            if self._skip_low and mem.confidence == "bassa":
                continue
            memories.append(mem)

        return memories

    # ── Main pipeline ─────────────────────────────────────────

    def ingest(self, path: Path, source: str) -> int:
        """
        Processa un file o directory e salva i ricordi nel DB.
        Ritorna il numero di ricordi salvati.
        """
        info(f"Parsing {source}: {path}")

        # 1. Parse
        parser   = self._get_parser(source)
        messages = list(parser.parse(path))
        self.stats["messages_parsed"] = len(messages)
        info(f"Messaggi letti: {len(messages)}")

        if not messages:
            warn("Nessun messaggio trovato — controlla formato e path.")
            return 0

        # Ordina per timestamp
        messages.sort(key=lambda m: m.timestamp)

        # 2. Filter
        messages = self._filter_messages(messages)
        self.stats["messages_filtered"] = len(messages)
        my_count = sum(1 for m in messages if m.is_me)
        info(f"Messaggi filtrati: {len(messages)}  (miei: {my_count})")

        if my_count == 0:
            warn(
                f"Nessun messaggio trovato per '{self._my_name}'.\n"
                f"  Controlla --me: i sender trovati sono: "
                f"{list({m.sender for m in messages})[:10]}"
            )
            return 0

        # 3. Segment
        episodes = self._segmenter.segment(messages)
        self.stats["episodes"] = len(episodes)
        info(f"Episodi: {len(episodes)}")

        # 4. Extract + Save
        saved_total = 0

        for i, episode in enumerate(episodes, 1):
            if self._verbose:
                print(
                    f"\n  {_c(DIM, f'Episodio {i}/{len(episodes)}')} "
                    f"{episode.start_time.strftime('%d/%m/%Y %H:%M')} "
                    f"({len(episode.messages)} messaggi)"
                )

            memories = self._extract_from_episode(episode)
            self.stats["memories_extracted"] += len(memories)

            for mem in memories:
                if self._verbose:
                    conf_color = GRN if mem.confidence == "alta" else (YLW if mem.confidence == "media" else DIM)
                    print(
                        f"    {_c(GRN,'✓') if not self._dry_run else _c(YLW,'○')}  "
                        f"{_c(BOLD, mem.concept):<20} "
                        f"{_c(CYN, mem.feeling):<22} "
                        f"{_c(conf_color, mem.confidence)}"
                    )
                    if self._verbose:
                        wrapped = textwrap.fill(mem.content, 65, initial_indent="       ")
                        print(_c(DIM, wrapped))

                if not self._dry_run:
                    try:
                        self._db.remember(
                            concept = mem.concept,
                            feeling = mem.feeling,
                            content = mem.content,
                            note    = mem.note,
                            tags    = mem.tags,
                        )
                        saved_total += 1
                        self.stats["memories_saved"] += 1
                    except Exception as e:
                        self.stats["errors"] += 1
                        if self._verbose:
                            warn(f"Salvataggio fallito: {e}")
                else:
                    saved_total += 1
                    self.stats["memories_saved"] += 1

            # Throttling tra batch
            if i % self._batch_size == 0 and i < len(episodes):
                time.sleep(0.5)

        return saved_total


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="MNHEME Conversation Ingester — estrae ricordi da conversazioni.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Esempi:
              python conversation_ingester.py chat.txt \\
                --me "Mario" --source whatsapp

              python conversation_ingester.py export.json \\
                --me "Mario Rossi" --source telegram \\
                --db vita.mnheme --verbose

              python conversation_ingester.py ~/Mail/inbox.mbox \\
                --me "mario@example.com" --source gmail \\
                --skip-low-confidence

              python conversation_ingester.py chats/ \\
                --me "Mario" --source whatsapp \\
                --dry-run --verbose
        """),
    )
    parser.add_argument("path",
                        help="File o directory da elaborare")
    parser.add_argument("--me",
                        required=True,
                        help="Nome/indirizzo con cui appaiono i tuoi messaggi")
    parser.add_argument("--source",
                        choices=["whatsapp","telegram","gmail","imessage","text"],
                        default="whatsapp",
                        help="Formato sorgente (default: whatsapp)")
    parser.add_argument("--db",
                        default=os.environ.get("MNHEME_DB", "mnheme.mnheme"),
                        help="Path al database MNHEME (default: mnheme.mnheme)")
    parser.add_argument("--env",
                        default=os.environ.get("MNHEME_ENV", ".env"),
                        help="Path al file .env (default: .env)")
    parser.add_argument("--provider",
                        default=None,
                        help="Provider LLM (es: lm-studio, groq). Default: ACTIVE_PROVIDER dal .env")
    parser.add_argument("--min-length",
                        type=int, default=5,
                        help="Lunghezza minima testo messaggio (default: 5)")
    parser.add_argument("--batch-size",
                        type=int, default=5,
                        help="Episodi per batch (default: 5)")
    parser.add_argument("--gap-hours",
                        type=float, default=4.0,
                        help="Ore di silenzio per dividere episodi (default: 4)")
    parser.add_argument("--max-messages",
                        type=int, default=40,
                        help="Max messaggi per episodio (default: 40)")
    parser.add_argument("--skip-low-confidence",
                        action="store_true",
                        help="Scarta ricordi a bassa confidenza")
    parser.add_argument("--dry-run",
                        action="store_true",
                        help="Analizza senza scrivere nel DB")
    parser.add_argument("--verbose",
                        action="store_true",
                        help="Output dettagliato")
    args = parser.parse_args()

    # ── Banner ──────────────────────────────────────────────
    print(f"\n{_c(BOLD,'MNHEME Conversation Ingester')}")
    print("─" * 52)
    info(f"Sorgente:   {args.source}  ←  {args.path}")
    info(f"Persona:    {args.me}")
    info(f"Database:   {args.db}")
    if args.dry_run:
        print(f"  {_c(YLW,'→')}  DRY-RUN — nessuna scrittura nel DB")

    # ── Setup LLM ───────────────────────────────────────────
    env = load_env(args.env)
    active = args.provider or env.get("ACTIVE_PROVIDER") or None
    try:
        llm = LLMProvider.from_env(args.env, active=active)
        ok(f"LLM: {llm.active_profile.name} / {llm.active_profile.model}")
    except Exception as e:
        err(f"LLM non disponibile: {e}")
        sys.exit(1)

    # ── Setup DB ────────────────────────────────────────────
    if not args.dry_run:
        try:
            db = MemoryDB(args.db)
            ok(f"DB: {args.db}  ({db.count()} ricordi esistenti)")
        except Exception as e:
            err(f"DB non accessibile: {e}")
            sys.exit(1)
    else:
        db = MemoryDB(":memory:")

    # ── Setup segmenter custom ───────────────────────────────
    ingester = ConversationIngester(
        db            = db,
        llm           = llm,
        my_name       = args.me,
        min_length    = args.min_length,
        batch_size    = args.batch_size,
        dry_run       = args.dry_run,
        verbose       = args.verbose,
        skip_low_conf = args.skip_low_confidence,
    )
    ingester._segmenter = ConversationSegmenter(
        gap_hours    = args.gap_hours,
        max_messages = args.max_messages,
    )

    print("─" * 52)

    # ── Ingest ──────────────────────────────────────────────
    path  = Path(args.path)
    start = time.perf_counter()

    if not path.exists():
        err(f"Path non trovato: {path}")
        sys.exit(1)

    # Se è una directory, processa tutti i file compatibili
    if path.is_dir():
        ext_map = {
            "whatsapp" : ["*.txt", "*.zip"],
            "telegram" : ["*.json"],
            "gmail"    : ["*.mbox", "*.eml"],
            "imessage" : ["*.txt", "*.db"],
            "text"     : ["*.txt", "*.md"],
        }
        patterns = ext_map.get(args.source, ["*"])
        files    = []
        for pat in patterns:
            files.extend(path.glob(pat))
        files = sorted(set(files))

        if not files:
            warn(f"Nessun file compatibile trovato in {path}")
            sys.exit(1)

        info(f"File trovati: {len(files)}")
        total = 0
        for f in files:
            print(f"\n  {_c(DIM, str(f))}")
            total += ingester.ingest(f, args.source)
    else:
        total = ingester.ingest(path, args.source)

    elapsed = time.perf_counter() - start

    # ── Riepilogo ────────────────────────────────────────────
    s = ingester.stats
    print(f"\n{'─'*52}")
    print(f"  {_c(BOLD,'Completato')} in {elapsed:.1f}s")
    print(f"  Messaggi letti:    {s['messages_parsed']}")
    print(f"  Dopo filtro:       {s['messages_filtered']}")
    print(f"  Episodi:           {s['episodes']}")
    print(f"  Ricordi estratti:  {s['memories_extracted']}")
    print(
        f"  {_c(GRN,'Ricordi salvati:')}   {s['memories_saved']}"
        + (f"  {_c(YLW,'(dry-run)')}" if args.dry_run else "")
    )
    if s["errors"]:
        print(f"  {_c(RED,'Errori:')}            {s['errors']}")
    print()


if __name__ == "__main__":
    main()
