"""
╔══════════════════════════════════════════════════════════╗
║              J.A.R.V.I.S  v5.0  FIXED                   ║
║   Fixes: LAST_RESPONSE, _hist, _search_lbl, Reminder,   ║
║          TTS-Injection, dead code, wakeword-loop         ║
╚══════════════════════════════════════════════════════════╝

pip install speechrecognition pyttsx3 pyautogui psutil pillow
    pyaudio pyperclip requests duckduckgo-search keyboard

python jarvis_v5_fixed.py
"""

import os, sys, subprocess, webbrowser, datetime, time, threading
import re, json, math, shutil, string, random, ctypes, socket, warnings
from pathlib import Path
from collections import deque
from urllib.parse import quote_plus
from html import unescape
import ast
import operator

# ── Imports ─────────────────────────────
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog, filedialog
    import speech_recognition as sr
    import pyttsx3
    import pyautogui, psutil
    from PIL import Image, ImageTk
except ImportError as e:
    sys.exit(f"[FEHLER] {e}\npip install speechrecognition pyttsx3 pyautogui psutil pillow pyaudio")

try: import pyperclip;         CLIP_OK = True
except ImportError: CLIP_OK = False
try: import requests;          REQ_OK  = True
except ImportError: REQ_OK  = False
try:
    from ddgs import DDGS
    DDG_OK = True
except ImportError:
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r"This package \(`duckduckgo_search`\) has been renamed to `ddgs`! Use `pip install ddgs` instead\.")
            from duckduckgo_search import DDGS
        DDG_OK = True
    except ImportError:
        DDG_OK = False
try: import keyboard;          KB_OK   = True
except ImportError: KB_OK   = False

# ══════════════════════════════════════════
#  DESIGN TOKENS  (dynamisch – aus Config geladen)
# ══════════════════════════════════════════
_COLOR_DEFAULTS = {
    "BG0":    "#02040a",
    "BG1":    "#070c16",
    "BG2":    "#0c1220",
    "BG3":    "#111a2e",
    "BG4":    "#172238",
    "BORDER": "#1e3050",
    "DIM":    "#253a58",
    "DIM2":   "#4a6a8a",
    "CYAN":   "#00d9ff",
    "CYAN2":  "#00b8d4",
    "AMBER":  "#ffb800",
    "AMBER2": "#ff9800",
    "GREEN":  "#00ff7f",
    "GREEN2": "#00dd66",
    "RED":    "#ff4466",
    "PURPLE": "#9966ff",
    "BLUE":   "#4488ff",
    "TEXT":   "#e0f0ff",
    "TEXT2":  "#8aafcc",
    "WHITE":  "#ffffff",
}

# Vordefinierte Farbschemata
COLOR_THEMES = {
    "Dark Anthracite (Standard)": {
        "BG0":"#02040a","BG1":"#070c16","BG2":"#0c1220","BG3":"#111a2e","BG4":"#172238",
        "BORDER":"#1e3050","DIM":"#253a58","DIM2":"#4a6a8a",
        "CYAN":"#00d9ff","CYAN2":"#00b8d4","AMBER":"#ffb800","AMBER2":"#ff9800",
        "GREEN":"#00ff7f","GREEN2":"#00dd66","RED":"#ff4466",
        "PURPLE":"#9966ff","BLUE":"#4488ff",
        "TEXT":"#e0f0ff","TEXT2":"#8aafcc","WHITE":"#ffffff",
    },
    "Midnight Purple": {
        "BG0":"#04020a","BG1":"#0a0614","BG2":"#110a1e","BG3":"#18102c","BG4":"#20163a",
        "BORDER":"#2e1a50","DIM":"#3d2468","DIM2":"#6a4a8a",
        "CYAN":"#cc88ff","CYAN2":"#aa66dd","AMBER":"#ffb800","AMBER2":"#ff9800",
        "GREEN":"#44ffaa","GREEN2":"#22dd88","RED":"#ff4466",
        "PURPLE":"#ff88ff","BLUE":"#8866ff",
        "TEXT":"#f0e0ff","TEXT2":"#c0a0dd","WHITE":"#ffffff",
    },
    "Ocean Blue": {
        "BG0":"#020a10","BG1":"#061420","BG2":"#0a1e2e","BG3":"#102838","BG4":"#163244",
        "BORDER":"#1a4060","DIM":"#205080","DIM2":"#4a7aaa",
        "CYAN":"#00ccff","CYAN2":"#00aadd","AMBER":"#ffcc00","AMBER2":"#ffaa00",
        "GREEN":"#00ffcc","GREEN2":"#00ddaa","RED":"#ff6644",
        "PURPLE":"#8899ff","BLUE":"#2266ff",
        "TEXT":"#d0eeff","TEXT2":"#80aacc","WHITE":"#ffffff",
    },
    "Hacker Green": {
        "BG0":"#000800","BG1":"#001200","BG2":"#001a00","BG3":"#002200","BG4":"#002c00",
        "BORDER":"#004400","DIM":"#006600","DIM2":"#228822",
        "CYAN":"#00ff41","CYAN2":"#00cc33","AMBER":"#ccff00","AMBER2":"#aadd00",
        "GREEN":"#00ff41","GREEN2":"#00dd33","RED":"#ff3300",
        "PURPLE":"#88ff44","BLUE":"#44ff88",
        "TEXT":"#ccffcc","TEXT2":"#66aa66","WHITE":"#aaffaa",
    },
    "Warm Sunset": {
        "BG0":"#0a0400","BG1":"#140800","BG2":"#1e0e00","BG3":"#281400","BG4":"#321a00",
        "BORDER":"#4a2800","DIM":"#663800","DIM2":"#8a5a22",
        "CYAN":"#ffaa00","CYAN2":"#ee8800","AMBER":"#ff6600","AMBER2":"#ee4400",
        "GREEN":"#88ff44","GREEN2":"#66dd22","RED":"#ff2244",
        "PURPLE":"#ff88aa","BLUE":"#ffcc66",
        "TEXT":"#fff0d0","TEXT2":"#ccaa88","WHITE":"#ffffff",
    },
    "Ice White": {
        "BG0":"#f0f4f8","BG1":"#e4ecf4","BG2":"#d8e4f0","BG3":"#ccdaec","BG4":"#c0d0e8",
        "BORDER":"#a0bcd8","DIM":"#809ab8","DIM2":"#6080a0",
        "CYAN":"#0066cc","CYAN2":"#0055aa","AMBER":"#cc6600","AMBER2":"#aa4400",
        "GREEN":"#006644","GREEN2":"#004433","RED":"#cc0022",
        "PURPLE":"#6600cc","BLUE":"#0044aa",
        "TEXT":"#1a2a3a","TEXT2":"#3a5a7a","WHITE":"#0a1a2a",
    },
}

def _load_colors():
    """Lädt Farben aus Config oder nimmt Defaults."""
    try:
        if CFG_FILE.exists():
            with open(CFG_FILE) as f:
                saved = json.load(f).get("colors", {})
            d = dict(_COLOR_DEFAULTS)
            d.update(saved)
            return d
    except Exception: pass
    return dict(_COLOR_DEFAULTS)

_c = _load_colors()
BG0    = _c["BG0"];    BG1    = _c["BG1"];    BG2    = _c["BG2"]
BG3    = _c["BG3"];    BG4    = _c["BG4"];    BORDER = _c["BORDER"]
DIM    = _c["DIM"];    DIM2   = _c["DIM2"]
CYAN   = _c["CYAN"];   CYAN2  = _c["CYAN2"];  AMBER  = _c["AMBER"]
AMBER2 = _c["AMBER2"]; GREEN  = _c["GREEN"];  GREEN2 = _c["GREEN2"]
RED    = _c["RED"];    PURPLE = _c["PURPLE"]; BLUE   = _c["BLUE"]
TEXT   = _c["TEXT"];   TEXT2  = _c["TEXT2"];  WHITE  = _c["WHITE"]

FN = "Segoe UI"
FC = "Consolas"
F_TITLE  = (FN, 16, "bold")
F_HEAD   = (FN, 12, "bold")
F_BODY   = (FN, 11)
F_SMALL  = (FN, 10)
F_TINY   = (FN,  9)
F_MONO   = (FC, 11)
F_MONO_B = (FC, 11, "bold")
F_MONO_S = (FC, 10)
F_BIG    = (FN, 24, "bold")
F_HUGE   = (FN, 40, "bold")

# ══════════════════════════════════════════
#  CONFIG & PERSISTENZ
# ══════════════════════════════════════════
CFG_FILE   = Path.home() / ".jarvis_v5.json"
NOTES_FILE = Path.home() / ".jarvis_v5_notes.json"
HIST_FILE  = Path.home() / ".jarvis_v5_history.json"
USER_DEFAULT_NAME = os.environ.get("USERNAME", "Freund")

def cfg_load():
    d = {"tts_rate": 150, "volume": 1.0, "wakeword": "jarvis",
         "wakeword_enabled": True, "speech_input_enabled": True,
         "voice": 0, "weather_city": "Berlin", "custom_apps": {},
         "reminders": [], "search_lang": "de-de", "speak_answers": True,
         "speech_lang": "de-DE", "user_name": USER_DEFAULT_NAME,
         }
    if CFG_FILE.exists():
        try:
            with open(CFG_FILE) as f: d.update(json.load(f))
        except (IOError, json.JSONDecodeError) as e: print(f"Config load error: {e}")
    return d

def cfg_save(c):
    with open(CFG_FILE, "w", encoding="utf-8") as f: json.dump(c, f, indent=2, ensure_ascii=False)

def notes_load():
    if NOTES_FILE.exists():
        try:
            with open(NOTES_FILE) as f: return json.load(f)
        except (IOError, json.JSONDecodeError) as e: print(f"Notes load error: {e}")
    return [{"title": "Erste Notiz", "body": "Willkommen bei JARVIS v5! 🚀",
             "pinned": False, "created": str(datetime.datetime.now())}]

def notes_save(n):
    with open(NOTES_FILE, "w", encoding="utf-8") as f: json.dump(n, f, indent=2, ensure_ascii=False)

def hist_load():
    if HIST_FILE.exists():
        try:
            with open(HIST_FILE) as f: return json.load(f)
        except (IOError, json.JSONDecodeError) as e: print(f"History load error: {e}")
    return []

def hist_save(h):
    with open(HIST_FILE, "w", encoding="utf-8") as f: json.dump(h[-200:], f, indent=2, ensure_ascii=False)


# ══════════════════════════════════════════
#  THREAD-SICHERER CONFIG-MANAGER
# ══════════════════════════════════════════
class ConfigManager:
    """Thread-sichere Verwaltung von Config, Notizen und Verlauf."""

    def __init__(self):
        self._lock = threading.RLock()
        self.config    = cfg_load()
        self.all_notes = notes_load()
        self.history   = hist_load()
        self._last_response = ""   # FIX: privat, nie direkt als Alias exportieren

    # ── Config ──────────────────────────
    def get(self, key, default=None):
        with self._lock:
            return self.config.get(key, default)

    def set(self, key, value):
        with self._lock:
            self.config[key] = value
            cfg_save(self.config)

    def update_config(self, data):
        with self._lock:
            self.config.update(data)
            cfg_save(self.config)

    # ── Notizen ──────────────────────────
    def add_note(self, note):
        with self._lock:
            self.all_notes.append(note)
            notes_save(self.all_notes)

    def update_note(self, idx, note):
        with self._lock:
            if 0 <= idx < len(self.all_notes):
                self.all_notes[idx] = note
                notes_save(self.all_notes)

    def delete_note(self, idx):
        with self._lock:
            if 0 <= idx < len(self.all_notes):
                del self.all_notes[idx]
                notes_save(self.all_notes)

    # ── Verlauf ──────────────────────────
    def add_history(self, item):
        with self._lock:
            self.history.append(item)
            hist_save(self.history)

    def clear_history(self):
        with self._lock:
            self.history.clear()
            hist_save(self.history)

    # ── Letzte Antwort (FIX 3) ───────────
    def set_response(self, text: str):
        """Letzte JARVIS-Antwort speichern (thread-safe)."""
        with self._lock:
            self._last_response = text

    def get_response(self) -> str:
        """Letzte JARVIS-Antwort abrufen (thread-safe)."""
        with self._lock:
            return self._last_response


# Globale Instanz
app_state = ConfigManager()

# Bequeme Aliases für die häufig genutzten Collections
# (Mutations werden reflektiert – funktioniert für dict/list)
config    = app_state.config
all_notes = app_state.all_notes
history   = app_state.history
# KEIN Alias für last_response – immer app_state.get/set_response() nutzen


# ══════════════════════════════════════════
#  NUTZER-NAME
# ══════════════════════════════════════════
def get_user_name() -> str:
    return app_state.get("user_name", USER_DEFAULT_NAME)

def set_user_name(name: str):
    if not name: return
    app_state.set("user_name", name.strip().title())


def conversation_response(text: str):
    t = text.lower().strip()
    name = get_user_name()
    if any(w in t for w in ["hallo jarvis","hi jarvis","hey jarvis","servus jarvis","yo jarvis"]):
        return f"Hallo {name}! Schön, dass du mich ansprichst. Wie geht es dir?", None
    if any(w in t for w in ["hallo","hi","hey","servus","moin"]) and "jarvis" in t:
        return f"Hallo {name}! Wie kann ich dir helfen?", None
    if any(w in t for w in ["wie geht es dir","wie gehts dir","wie geht's dir"]):
        return "Mir geht es gut, danke! Und wie geht es dir?", None
    if any(w in t for w in ["mir geht es gut","mir gehts gut","alles gut","gut danke","super","sehr gut"]):
        return "Das freut mich sehr zu hören! Was möchtest du als Nächstes machen?", None
    if any(w in t for w in ["mir geht es nicht gut","nicht so gut","schlecht","mies","traurig"]):
        return "Oh nein, das tut mir leid. Wenn du möchtest, kann ich dir etwas Abwechslung oder einen schnellen Tipp anbieten.", None
    if any(w in t for w in ["und dir","und dir?","und du","und du?"]):
        return "Auch gut, danke der Nachfrage!", None
    if any(w in t for w in ["wie heißt du","wie heißt du?","wer bist du","wer bist du?"]):
        return f"Ich heiße J.A.R.V.I.S. und bin dein smarter Assistent, {name}", None
    match = re.search(r"ich heiße\s+([a-zäöüß]+)", t)
    if not match:
        match = re.search(r"mein name ist\s+([a-zäöüß]+)", t)
    if match:
        set_user_name(match.group(1).title())
        return f"Freut mich, dich kennenzulernen, {get_user_name()}!", None
    match = re.search(r"ich bin\s+([a-zäöüß]+)", t)
    if match and "jarvis" not in match.group(1).lower():
        set_user_name(match.group(1).title())
        return f"Schön, dich kennenzulernen, {get_user_name()}!", None
    return None


# ══════════════════════════════════════════
#  SICHERE MATHE-EVAL
# ══════════════════════════════════════════
def safe_eval_math(expr):
    allowed = set('0123456789.+-*/()')
    if not all(c in allowed or c.isspace() for c in expr):
        raise ValueError("Ungültige Zeichen in Expression")
    ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.USub: operator.neg, ast.UAdd: operator.pos}
    def safe_eval(node):
        if isinstance(node, ast.Num):    return node.n
        elif isinstance(node, ast.Constant): return node.value
        elif isinstance(node, ast.BinOp):
            return ops[type(node.op)](safe_eval(node.left), safe_eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](safe_eval(node.operand))
        else: raise ValueError("Nicht unterstützte Operation")
    try:
        tree = ast.parse(expr, mode='eval')
        return safe_eval(tree.body)
    except ZeroDivisionError: raise ValueError("Division durch Null")
    except (ValueError, SyntaxError) as e: raise ValueError(f"Ungültige Berechnung: {e}")


# ══════════════════════════════════════════
#  TTS  (PowerShell, FIX 6: Pfad-Injection)
# ══════════════════════════════════════════
import tempfile

try:
    _temp_engine = pyttsx3.init()
    all_voices = _temp_engine.getProperty("voices")
    try: _temp_engine.stop()
    except Exception: pass
    del _temp_engine
except Exception:
    all_voices = []

def spreche(text):
    if not config.get("speak_answers", True): return
    text = str(text).strip()
    if not text: return

    # TTS-tauglichen Text bauen: Sonderzeichen raus, Inhalt bleibt
    clean = text
    clean = re.sub(r"https?://\S+", "Link", clean)          # URLs → "Link"
    clean = re.sub(r"[─━═]+", ". ", clean)                   # Trennlinien → Pause
    clean = re.sub(r"[•·▪▸►◈⚡📖🔗🌐📋📌🔍⚙️🗑✓✂️↩⬇🔁👋😴💤🔒📶📵📡🌙☀️💡🔊🔉🔇▶️⏸⏭⏮⏹🗂🪟🖥️⬅➡➕❌🔄💾🖨🔍🔎☑️✂↶↷⌨⎋↹🗑🖱📋⏱🔔🌙🌤❌⚡🔋🔌]", " ", clean)  # Emojis raus
    clean = re.sub(r"[^\w\s\.,;:!?\-äöüÄÖÜß\(\)\n]", " ", clean)
    clean = re.sub(r"[ \t]+", " ", clean)
    clean = re.sub(r"\n+", ". ", clean)                       # Zeilenumbrüche → Pause
    clean = re.sub(r"\s+", " ", clean).strip()
    clean = re.sub(r"\.{2,}", ".", clean)

    if not clean: return

    # TTS-Rate sicher berechnen: -5 bis +5 ist der PS-Bereich
    raw_rate = config.get("tts_rate", 150)
    try:
        ps_rate = max(-5, min(5, int(raw_rate) // 50 - 2))
    except Exception:
        ps_rate = 0

    word_count  = len(clean.split())
    # Wörter/Min bei Rate 0 ≈ 150, bei -2 ≈ 120
    wpm         = max(80, 150 - abs(ps_rate) * 15)
    est_seconds = max(20, int(word_count / wpm * 60) + 10)

    def _talk():
        tmp = None
        try:
            # Text in Temp-Datei schreiben (kein PS-String-Limit)
            with tempfile.NamedTemporaryFile(
                    mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(clean)
                tmp = f.name

            safe = tmp.replace("'", "''")
            ps   = f"""
$ErrorActionPreference = 'SilentlyContinue'
Add-Type -AssemblyName System.Speech
$content = [System.IO.File]::ReadAllText('{safe}', [System.Text.Encoding]::UTF8)
$tts = New-Object System.Speech.Synthesis.SpeechSynthesizer
$tts.Rate   = {ps_rate}
$tts.Volume = 100
try {{ $tts.SelectVoiceByHints('Female', 'German') }} catch {{}}
$tts.Speak($content)
$tts.Dispose()
"""
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                capture_output=True, timeout=est_seconds)
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
        finally:
            if tmp:
                try: Path(tmp).unlink(missing_ok=True)
                except Exception: pass

    threading.Thread(target=_talk, daemon=True).start()




# ══════════════════════════════════════════
#  SPRACHE
# ══════════════════════════════════════════
rec = sr.Recognizer()
rec.dynamic_energy_threshold = True
rec.pause_threshold = 0.5
rec.energy_threshold = 250
mic_ok = True
try:
    with sr.Microphone(): pass
except Exception: mic_ok = False

def lausche(timeout=6, limit=12, language=None):
    if not mic_ok or not config.get("speech_input_enabled", True): return None
    lang = language or config.get("speech_lang", "de-DE")
    try:
        with sr.Microphone() as s:
            rec.adjust_for_ambient_noise(s, duration=0.4)
            a = rec.listen(s, timeout=timeout, phrase_time_limit=limit)
            return rec.recognize_google(a, language=lang).lower()
    except Exception: return None


# ══════════════════════════════════════════
#  WEB-SUCHE  – maximale Qualität ohne API-Key
# ══════════════════════════════════════════

_search_cache: dict = {}

# ── Stopwörter DE+EN ──
_SW = {
    "was","ist","wie","wer","wo","wann","warum","ein","eine","einer","einem",
    "der","die","das","den","dem","des","und","oder","aber","für","von","mit",
    "an","in","auf","zu","bei","nach","über","unter","durch","aus","um","im",
    "am","beim","zur","zum","sich","auch","noch","schon","sehr","dann","wenn",
    "dass","dieser","diese","dieses","diesen","diesem","kann","wird","wurde",
    "sind","haben","hat","hatte","hatte","werden","sein","war","nach","vor",
    "the","is","a","an","of","in","on","at","to","for","and","or","that","it",
    "this","with","are","was","were","be","been","have","has","had","not","but",
    "from","by","as","which","they","their","its","about","into","through",
}

# ── Fragewort → Antwort-Muster ──
_Q_PATTERNS = {
    "hauptstadt":   r"Hauptstadt[^\.\n]*ist[^\.\n]*",
    "bevölkerung":  r"(?:Einwohner|Bevölkerung)[^\.\n]*\d[^\.\n]*",
    "geboren":      r"(?:geboren|Geburtstag|Geburtsort)[^\.\n]*",
    "gestorben":    r"(?:gestorben|Tod|starb)[^\.\n]*",
    "gründung":     r"(?:gegründet|Gründung|gegründet)[^\.\n]*",
    "fläche":       r"(?:Fläche|km²|Quadratkilometer)[^\.\n]*",
    "höhe":         r"(?:Höhe|hoch|Meter|m ü)[^\.\n]*",
}

# ── Suchmodus ──
_WIKI_KW  = {"was","wer","wie","wo","wann","warum","welche","welcher","welches",
             "ist","war","bedeutet","heißt","erkläre","erklär","definition",
             "bedeutung","geschichte","hauptstadt","hauptstädte","erfunden",
             "gegründet","geboren","gestorben","entdeckt","entwickelt","land",
             "kontinent","ozean","planet","tier","pflanze","krankheit"}
_NEWS_KW  = {"aktuell","heute","neueste","neu","nachrichten","news","gerade",
             "jetzt","letzte","neuigkeit","aktuelles"}
_PRICE_KW = {"kurs","preis","kosten","kostet","wert","bitcoin","ethereum",
             "euro","dollar","aktie","crypto","rendite"}


# ────────────────────────────────────────
#  QUERY OPTIMIERUNG
# ────────────────────────────────────────
_REMOVE_PREFIXES = [
    "bitte erkläre mir genau ","bitte erkläre mir ","erkläre mir genau ",
    "erkläre mir ","bitte erklär mir ","erklär mir ","kannst du mir erklären ",
    "kannst du mir sagen ","kannst du mir erklären wie ",
    "ich möchte wissen ","ich würde gerne wissen ","ich will wissen ",
    "sag mir bitte ","sag mir ","zeig mir bitte ","zeig mir ","zeige mir ",
    "was genau ist ","was ist eigentlich ","was ist denn ",
    "wer genau ist ","wer ist eigentlich ","wer ist denn ",
    "wie genau funktioniert ","wie funktioniert eigentlich ",
    "wo genau liegt ","wo genau ist ","wo liegt eigentlich ",
    "definiere ","definition von ","bedeutung von ","erklärung zu ",
    "bitte ","mal kurz ",
]

def optimize_query(frage: str) -> tuple:
    """Query bereinigen + Such-Modus erkennen."""
    q = frage.strip()
    ql = q.lower()

    # Modus erkennen
    words = set(re.sub(r"[^\w\s]", "", ql).split())
    modus = "general"
    if words & _PRICE_KW:  modus = "price"
    elif words & _NEWS_KW: modus = "news"
    elif words & _WIKI_KW: modus = "wiki"

    # Füllwörter entfernen
    for p in _REMOVE_PREFIXES:
        if ql.startswith(p):
            q = q[len(p):].strip()
            ql = q.lower()
            break

    return q.rstrip("?!., "), modus


# ────────────────────────────────────────
#  INTENT-ERKENNUNG  (was will der Nutzer wirklich?)
# ────────────────────────────────────────

_INTENT_PATTERNS = [
    # (Intent-Name, Regex-Muster, Suchmodus)
    ("kaufen",     r"\b(kaufen|bestellen|preis|kosten|wo bekomme?|günstig|angebot|shop)\b", "shopping"),
    ("news",       r"\b(news|nachrichten|aktuell|heute|neu|2024|2025|gerade|jetzt)\b",      "news"),
    ("how_to",     r"\b(wie (kann|muss|soll|geht|funktioniert)|tutorial|anleitung|schritt|howto)\b", "how_to"),
    ("person",     r"\b(wer ist|wer war|biographie|geboren|gestorben|alter|beruf)\b",       "person"),
    ("ort",        r"\b(wo liegt|hauptstadt|land|stadt|kontinent|koordinaten|einwohner)\b", "place"),
    ("rezept",     r"\b(rezept|zutaten|kochen|backen|zubereiten|gericht|essen machen)\b",   "recipe"),
    ("wetter",     r"\b(wetter|temperatur|°c|regen|schnee|wind|klima)\b",                   "weather"),
    ("definition", r"\b(was ist|was sind|bedeutung|definition|erkläre?|erklärung)\b",       "definition"),
    ("vergleich",  r"\b(unterschied|vs\.|vergleich|besser|oder|welche?s? ist)\b",           "comparison"),
    ("sport",      r"\b(ergebnis|score|tabelle|bundesliga|premier league|champions league|nfl|nba)\b", "sports"),
    ("film_serie", r"\b(film|serie|movie|netflix|kino|schauspieler|staffel|folge)\b",       "entertainment"),
    ("calc",       r"^[\d\s\+\-\*\/\(\)\.]+$",                                              "calc"),
]

def detect_intent(query: str) -> str:
    """Erkennt die Suchintention für zielgerichtete Suche."""
    ql = query.lower()
    for name, pattern, _ in _INTENT_PATTERNS:
        if re.search(pattern, ql):
            return name
    return "general"


def build_search_queries(original: str, intent: str) -> list:
    """
    Baut mehrere optimierte Suchqueries für verschiedene Aspekte.
    Gibt Liste von (query, sprache) zurück.
    """
    q = original.strip().rstrip("?!.,")
    ql = q.lower()
    queries = [q]  # Hauptquery immer zuerst

    # Intent-spezifische Zusatz-Queries
    if intent == "kaufen":
        queries.append(f"{q} kaufen Preis")
        queries.append(f"{q} günstig bestellen")
    elif intent == "news":
        queries.append(f"{q} 2025")
        queries.append(f"{q} aktuell")
    elif intent == "how_to":
        queries.append(f"{q} Anleitung")
        queries.append(f"how to {q}")
    elif intent == "person":
        queries.append(f"{q} Biographie")
    elif intent == "rezept":
        queries.append(f"{q} Rezept Zutaten")
        queries.append(f"{q} einfach schnell")
    elif intent == "definition":
        queries.append(f"{q} einfach erklärt")
    elif intent == "vergleich":
        queries.append(f"{q} Unterschied Vergleich")
    elif intent == "sport":
        queries.append(f"{q} aktuell 2025")
    elif intent == "film_serie":
        queries.append(f"{q} Handlung Bewertung")

    return queries[:3]  # max 3 Queries


# ────────────────────────────────────────
#  TEXT-EXTRAKTION  (deutlich verbessert)
# ────────────────────────────────────────

def _clean_html_text(html: str) -> str:
    """Extrahiert sauberen Plaintext aus HTML."""
    # Störende Blöcke komplett entfernen
    for pat in [
        r"(?s)<script[^>]*>.*?</script>",
        r"(?s)<style[^>]*>.*?</style>",
        r"(?s)<nav[^>]*>.*?</nav>",
        r"(?s)<header[^>]*>.*?</header>",
        r"(?s)<footer[^>]*>.*?</footer>",
        r"(?s)<aside[^>]*>.*?</aside>",
        r"(?s)<form[^>]*>.*?</form>",
        r"(?s)<noscript[^>]*>.*?</noscript>",
        r"(?s)<!--.*?-->",
        r"(?s)<figure[^>]*>.*?</figure>",
        r"(?s)<iframe[^>]*>.*?</iframe>",
    ]:
        html = re.sub(pat, " ", html)

    # Wichtige Block-Tags → Zeilenumbruch
    html = re.sub(r"<(?:p|div|li|h[1-6]|br|tr)[^>]*>", "\n", html, flags=re.IGNORECASE)
    text = unescape(re.sub(r"<[^>]+>", " ", html))
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def _extract_main_content(html: str) -> str:
    """Findet den Haupt-Content-Bereich einer Seite."""
    # Versuche bekannte Content-Container zu finden
    patterns = [
        r"(?s)<article[^>]*>(.*?)</article>",
        r'(?s)<div[^>]+(?:class|id)="[^"]*(?:article-body|post-content|entry-content|main-content|article-content|content-body|post-body|story-body)[^"]*"[^>]*>(.*?)</div>',
        r"(?s)<main[^>]*>(.*?)</main>",
        r'(?s)<div[^>]+(?:class|id)="[^"]*(?:content|main|body)[^"]*"[^>]*>(.*?)</div>',
    ]
    for pat in patterns:
        m = re.search(pat, html)
        if m and len(m.group(1)) > 300:
            return m.group(1)
    return html


def fetch_page_text(url: str, max_chars: int = 4000) -> str:
    """Lädt und extrahiert Seitentext intelligent."""
    if not REQ_OK or not url: return ""

    # Wikipedia via API (schneller & sauberer)
    if "wikipedia.org/wiki/" in url:
        title = url.split("/wiki/")[-1]
        lang  = re.search(r"//([a-z]+)\.wikipedia", url)
        lang  = lang.group(1) if lang else "de"
        try:
            r = requests.get(
                f"https://{lang}.wikipedia.org/w/api.php",
                params={"action":"query","prop":"extracts","exsentences":20,
                        "titles":title,"format":"json","explaintext":True},
                headers={"User-Agent":"Mozilla/5.0"}, timeout=7)
            pages = r.json().get("query",{}).get("pages",{})
            for p in pages.values():
                ext = p.get("extract","").strip()
                if ext: return ext[:max_chars]
        except Exception: pass
        return ""

    try:
        r = requests.get(url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0",
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate",
            },
            timeout=10, allow_redirects=True)
        if r.status_code != 200: return ""

        content = _extract_main_content(r.text)
        text = _clean_html_text(content)

        # Gute Absätze filtern (mind. 80 Zeichen, keine Navigation/Cookie-Texte)
        paragraphs = []
        for para in text.split("\n\n"):
            para = para.strip()
            if len(para) < 60: continue
            if re.search(r"(Cookie|Datenschutz|Impressum|Newsletter|©|AGB|Anmeld|Login|Registrier)", para): continue
            if para.count("|") > 4 or para.count("•") > 6: continue
            paragraphs.append(para)

        if paragraphs:
            return "\n\n".join(paragraphs[:10])[:max_chars]
        return text[:max_chars]
    except Exception:
        return ""


# ────────────────────────────────────────
#  TF-IDF SCORING  (verbessert)
# ────────────────────────────────────────

def _tokenize(text: str) -> list:
    return [w for w in re.sub(r"[^\w\s]", "", text.lower()).split()
            if w not in _SW and len(w) > 2]


def _tfidf_scores(query: str, docs: list) -> list:
    q_terms = _tokenize(query)
    if not q_terms: return []

    # Sätze aus allen Docs sammeln
    all_sents = []
    for doc_idx, (doc_text, doc_url) in enumerate(docs):
        if not doc_text: continue
        # Sätze splitten (DE+EN)
        sents = re.split(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ\"\'\(0-9])", doc_text)
        for sent_idx, s in enumerate(sents):
            s = s.strip()
            if len(s) < 35 or len(s) > 600: continue
            if s.count("|") > 3 or s.count("·") > 3: continue
            if re.search(r"(Cookie|Datenschutz|Impressum|©|AGB)", s): continue
            all_sents.append((s, doc_url, doc_idx, sent_idx))

    if not all_sents: return []

    N = len(all_sents)
    idf = {}
    for term in set(q_terms):
        df = sum(1 for s, _, _, _ in all_sents if term in s.lower())
        idf[term] = math.log((N + 1) / (df + 1)) + 1 if df else 2.5

    results = []
    for i, (sent, url, doc_idx, sent_idx) in enumerate(all_sents):
        tokens = _tokenize(sent)
        if not tokens: continue
        tf = {t: tokens.count(t) / len(tokens) for t in set(q_terms)}
        base_score = sum(tf.get(t, 0) * idf.get(t, 0) for t in q_terms)
        # Bonus: früh im Dokument = informativer
        pos_bonus = 1.0 / (math.log(sent_idx + 2) * 0.5 + 1)
        # Bonus: alle Query-Terme enthalten
        coverage = sum(1 for t in q_terms if t in sent.lower()) / len(q_terms)
        # Bonus: Query-Phrase direkt enthalten
        phrase_bonus = 1.4 if query.lower()[:20] in sent.lower() else 1.0
        final = base_score * (1 + pos_bonus * 0.4) * (1 + coverage * 0.6) * phrase_bonus
        if final > 0:
            results.append((final, sent, url))

    results.sort(key=lambda x: -x[0])
    return results


def _build_coherent_answer(query: str, scored: list, n: int = 8) -> str:
    """Baut eine kohärente Antwort aus den besten Sätzen."""
    seen = set()
    chosen = []
    for score, sent, url in scored:
        fp = re.sub(r"\s+", "", sent[:60].lower())
        if fp in seen: continue
        # Zu ähnliche Sätze überspringen
        skip = False
        for _, cs, _ in chosen:
            common = sum(1 for w in sent.split() if w in cs)
            if len(sent.split()) > 0 and common / len(sent.split()) > 0.7:
                skip = True; break
        if skip: continue
        seen.add(fp)
        chosen.append((score, sent, url))
        if len(chosen) >= n: break

    if not chosen: return ""
    # Beste zuerst
    chosen.sort(key=lambda x: -x[0])
    return " ".join(s for _, s, _ in chosen)


def extract_direct_answer(query: str, text: str) -> str:
    ql = query.lower()
    for kw, pattern in _Q_PATTERNS.items():
        if kw in ql:
            m = re.search(pattern, text, re.IGNORECASE)
            if m: return m.group(0).strip()
    return ""


# ────────────────────────────────────────
#  WIKIPEDIA
# ────────────────────────────────────────

def wikipedia_suche(query: str, lang: str = "de") -> dict | None:
    if not REQ_OK: return None
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
               "Accept-Language": f"{lang},{lang}-DE;q=0.9"}

    def _get_summary(title: str) -> dict | None:
        try:
            r = requests.get(
                f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote_plus(title)}",
                headers=headers, timeout=7)
            if r.status_code == 200:
                d = r.json()
                ext = d.get("extract", "").strip()
                if ext and len(ext) > 80:
                    return {"title": d.get("title",""), "extract": ext,
                            "url": d.get("content_urls",{}).get("desktop",{}).get("page","")}
        except Exception: pass
        return None

    # Direkt versuchen
    result = _get_summary(query)
    if result: return result

    # Suche
    try:
        rs = requests.get(
            f"https://{lang}.wikipedia.org/w/api.php",
            params={"action":"query","list":"search","srsearch":query,
                    "format":"json","srlimit":5,"srprop":"snippet"},
            headers=headers, timeout=7)
        for hit in rs.json().get("query",{}).get("search",[]):
            r2 = _get_summary(hit["title"])
            if r2: return r2
    except Exception: pass

    # Englisch-Fallback
    if lang == "de":
        return wikipedia_suche(query, lang="en")
    return None


def wikipedia_full_text(query: str, lang: str = "de") -> str:
    """Mehr Wikipedia-Text via Parse-API."""
    if not REQ_OK: return ""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        rs = requests.get(
            f"https://{lang}.wikipedia.org/w/api.php",
            params={"action":"query","list":"search","srsearch":query,
                    "format":"json","srlimit":1},
            headers=headers, timeout=6)
        hits = rs.json().get("query",{}).get("search",[])
        if not hits: return ""
        title = hits[0]["title"]
        rp = requests.get(
            f"https://{lang}.wikipedia.org/w/api.php",
            params={"action":"query","prop":"extracts","exintro":False,
                    "exsentences":25,"titles":title,"format":"json","explaintext":True},
            headers=headers, timeout=8)
        for page in rp.json().get("query",{}).get("pages",{}).values():
            ext = page.get("extract","").strip()
            if ext: return ext[:4000]
    except Exception: pass
    return ""


# ────────────────────────────────────────
#  WIKIDATA
# ────────────────────────────────────────

def wikidata_fact(query: str) -> str:
    if not REQ_OK: return ""
    ql = query.lower()
    headers = {"User-Agent": "JARVIS/5.0", "Accept": "application/sparql-results+json"}
    if any(w in ql for w in ["hauptstadt", "capital"]):
        m = re.search(r"(?:hauptstadt(?:\s+von)?|capital(?:\s+of)?)\s+([A-ZÄÖÜa-zäöü\s]+)",
                      query, re.IGNORECASE)
        if m:
            country = m.group(1).strip().rstrip("?")
            sparql = f"""
SELECT ?capitalLabel WHERE {{
  ?country wikibase:label {{ bd:serviceParam wikibase:language "de,en". }}
  ?country ?label "{country}"@de .
  ?country wdt:P36 ?capital .
  ?capital rdfs:label ?capitalLabel .
  FILTER(LANG(?capitalLabel) = "de")
}} LIMIT 1"""
            try:
                r = requests.get("https://query.wikidata.org/sparql",
                    params={"query":sparql,"format":"json"}, headers=headers, timeout=8)
                if r.status_code == 200:
                    bindings = r.json().get("results",{}).get("bindings",[])
                    if bindings:
                        cap = bindings[0].get("capitalLabel",{}).get("value","")
                        if cap: return f"Die Hauptstadt von {country} ist {cap}."
            except Exception: pass
    return ""


# ────────────────────────────────────────
#  DDG SUCHE
# ────────────────────────────────────────

def _ddg_instant(query: str) -> dict:
    if not REQ_OK: return {}
    try:
        r = requests.get("https://api.duckduckgo.com/",
            params={"q":query,"format":"json","no_html":"1","skip_disambig":"1"},
            headers={"User-Agent":"Mozilla/5.0"}, timeout=6)
        d = r.json()
        if d.get("Answer"):
            return {"answer": d["Answer"], "type": "instant"}
        elif d.get("AbstractText"):
            return {"answer": d["AbstractText"],
                    "source": d.get("AbstractSource",""),
                    "src_url": d.get("AbstractURL",""), "type": "abstract"}
    except Exception: pass
    return {}


def _ddg_suche(query: str, lang: str = "de-de", max_results: int = 12) -> list:
    if not DDG_OK: return []
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with DDGS() as ddgs:
                texts = (list(ddgs.text(query, region=lang, max_results=max_results))
                         or list(ddgs.text(query, max_results=max_results)))
        return [{"title": t.get("title","")[:120],
                 "body":  t.get("body","")[:1200],
                 "url":   t.get("href","")} for t in texts if t]
    except Exception: return []


def _html_fallback(query: str, max_results: int = 8) -> list:
    if not REQ_OK: return []
    try:
        r = requests.get("https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            timeout=8)
        parts = re.split(r"(?s)<div[^>]+result__body[^>]*>", r.text)[1:]
        out = []
        for part in parts:
            if len(out) >= max_results: break
            lm = re.search(r'<a[^>]+class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', part)
            if not lm: continue
            url = unescape(lm.group(1))
            if url.startswith("//"): url = "https:" + url
            sm = re.search(r'<a[^>]+class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>', part)
            out.append({
                "title": unescape(re.sub(r"<[^>]+>","",lm.group(2))).strip(),
                "body":  unescape(re.sub(r"<[^>]+>","",sm.group(1))).strip() if sm else "",
                "url":   url})
        return out
    except Exception: return []


# ────────────────────────────────────────
#  HAUPT-SUCHFUNKTION  (komplett neu)
# ────────────────────────────────────────

def web_suche(frage: str, lang: str = "de-de") -> dict:
    """
    Intent-gesteuerte Mehrstufige Suche.
    Sucht gezielt nach dem, was der Nutzer wirklich will.
    """
    if not REQ_OK:
        return {"type":"error","answer":"❌ pip install requests",
                "results":[],"wiki":None,"all_texts":[],"query_used":frage,"intent":"error"}

    cache_key = frage.lower().strip()
    if cache_key in _search_cache:
        return _search_cache[cache_key]

    # Intent & Query optimieren
    intent   = detect_intent(frage)
    query, modus = optimize_query(frage)
    queries  = build_search_queries(query, intent)
    wiki_lang = "de" if "de" in lang else "en"

    result: dict = {
        "type":       "web",
        "answer":     "",
        "source":     "",
        "src_url":    f"https://duckduckgo.com/?q={quote_plus(query)}",
        "wiki":       None,
        "results":    [],
        "all_texts":  [],
        "query_used": query,
        "intent":     intent,
    }

    # ── A: Wikidata (strukturierte Fakten) ────────────────────
    wd = wikidata_fact(frage)
    if wd:
        result["answer"] = wd
        result["source"] = "Wikidata"
        result["type"]   = "instant"
        result["all_texts"].append((wd, "https://wikidata.org"))

    # ── B: Wikipedia (bei Wissens-Fragen) ────────────────────
    use_wiki = intent in ("definition","person","ort","general","wiki") or modus in ("wiki","general")
    if use_wiki:
        wiki = wikipedia_suche(query, lang=wiki_lang)
        if wiki:
            result["wiki"]    = wiki
            result["type"]    = "wiki"
            result["source"]  = "Wikipedia"
            result["src_url"] = wiki.get("url", "")
            result["all_texts"].append((wiki["extract"], wiki.get("url","")))
            # Mehr Wiki-Text holen
            full = wikipedia_full_text(query, lang=wiki_lang)
            if full and full != wiki.get("extract",""):
                result["all_texts"].append((full, wiki.get("url","")))
            if not result["answer"]:
                result["answer"] = wiki["extract"]

    # ── C: DDG Instant Answer ─────────────────────────────────
    instant = _ddg_instant(query)
    if instant.get("answer") and not result["answer"]:
        result.update({"answer":instant["answer"],
                       "source":instant.get("source","DuckDuckGo"),
                       "src_url":instant.get("src_url",result["src_url"]),
                       "type":instant.get("type","instant")})
        result["all_texts"].append((instant["answer"], result["src_url"]))

    # ── D: Websuche mit allen optimierten Queries ─────────────
    all_ddg_results = []
    seen_urls = set()
    for q_variant in queries:
        ddg = _ddg_suche(q_variant, lang=lang, max_results=10)
        if not ddg and q_variant == queries[0]:
            ddg = _html_fallback(q_variant)
        for item in ddg:
            url = item.get("url","")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_ddg_results.append(item)

    result["results"] = all_ddg_results[:15]

    # DDG-Snippets als Texte sammeln
    for r in all_ddg_results:
        body = r.get("body","")
        if body and len(body) > 50:
            result["all_texts"].append((body, r.get("url","")))

    # ── E: Seitentext der Top-Treffer laden (parallel) ────────
    # Intent-gesteuert: wie viele Seiten wirklich öffnen?
    n_fetch = 5 if intent in ("kaufen","how_to","rezept","comparison") else 3
    urls_to_fetch = [r["url"] for r in all_ddg_results[:n_fetch] if r.get("url")
                     and "youtube.com" not in r.get("url","")
                     and "reddit.com" not in r.get("url","")][:n_fetch]

    if urls_to_fetch:
        import concurrent.futures as _cf
        with _cf.ThreadPoolExecutor(max_workers=4) as ex:
            page_texts = list(ex.map(lambda u: (fetch_page_text(u, 4000), u), urls_to_fetch))
        for pt, pu in page_texts:
            if pt and len(pt) > 100:
                result["all_texts"].append((pt, pu))
                if not result.get("page_text"):
                    result["page_text"] = pt

    # ── F: Fallback auf erstes DDG-Snippet ───────────────────
    if not result["answer"] and all_ddg_results:
        best = all_ddg_results[0]
        result.update({"answer": best.get("body",""),
                       "source": best.get("title",""),
                       "src_url": best.get("url",""),
                       "type": "web"})

    _search_cache[cache_key] = result
    return result


# ────────────────────────────────────────
#  ANTWORT-AUFBEREITUNG  (komplett neu)
# ────────────────────────────────────────

def humanize_search_response(query: str, result: dict) -> str:
    """
    Baut eine strukturierte, vollständige Antwort.
    Zeigt IMMER echte Inhalte, nicht nur Definitionen.
    """
    lines     = []
    intent    = result.get("intent", "general")
    all_texts = result.get("all_texts", [])
    qused     = result.get("query_used", query)

    # ── 1. Wikidata Direkt-Antwort (Fakten) ──────────────────
    if result.get("type") == "instant" and result.get("source") == "Wikidata":
        lines.append("⚡ " + result["answer"])
        lines.append("")

    # ── 2. Wikipedia (bei Wissens-Fragen) ────────────────────
    wiki = result.get("wiki")
    if wiki and wiki.get("extract"):
        lines.append(f"📖 {wiki['title']}")
        lines.append("─" * 40)
        # Ersten Absatz vollständig zeigen
        paras = wiki["extract"].split("\n\n")
        lines.append(paras[0])
        if len(paras) > 1:
            lines.append(paras[1][:400] + ("..." if len(paras[1]) > 400 else ""))
        if wiki.get("url"):
            lines.append(f"\n🔗 {wiki['url']}")
        lines.append("")

    # ── 3. TF-IDF aus allen gesammelten Texten ───────────────
    if all_texts:
        scored = _tfidf_scores(qused, all_texts)
        combined = " ".join(t for t, _ in all_texts[:5])
        direct   = extract_direct_answer(qused, combined)

        if not wiki and scored:
            answer_text = _build_coherent_answer(qused, scored, n=7)
            if answer_text and len(answer_text) > 80:
                if direct and direct not in answer_text:
                    lines.append(f"⚡ {direct}\n")
                lines.append("🌐 Aus dem Web:")
                lines.append("─" * 40)
                lines.append(answer_text)
                lines.append("")
        elif wiki and direct and direct not in wiki.get("extract",""):
            lines.append(f"⚡ Zusatz: {direct}")
            lines.append("")

    # ── 4. Intent-spezifische Treffer-Liste ──────────────────
    results = result.get("results", [])
    if results:
        # Für Shopping, News, How-To immer Treffer anzeigen
        show_results = (
            intent in ("kaufen","news","how_to","rezept","sport","film_serie","vergleich")
            or not lines
            or (not wiki and not result.get("answer"))
        )
        if show_results:
            if intent == "kaufen":
                lines.append("🛒 Angebote & Preise:")
            elif intent == "news":
                lines.append("📰 Aktuelle Meldungen:")
            elif intent == "how_to":
                lines.append("📋 Anleitungen:")
            elif intent == "rezept":
                lines.append("🍳 Rezepte:")
            else:
                lines.append("🔍 Top-Treffer:")
            lines.append("─" * 40)

            shown = 0
            for res in results[:6]:
                body = res.get("body","").strip()
                if not body or len(body) < 30: continue
                title = res.get("title","")
                url   = res.get("url","")
                lines.append(f"• {title}")
                lines.append(f"  {body[:350]}")
                if url: lines.append(f"  🔗 {url}")
                lines.append("")
                shown += 1
                if shown >= 4: break

    # ── 5. Weitere Quellen (wenn Wikipedia Hauptantwort) ─────
    if wiki and results:
        extras = [r for r in results[:5]
                  if r.get("body","") and len(r.get("body","")) > 80
                  and "wikipedia" not in r.get("url","").lower()][:3]
        if extras:
            lines.append("📌 Weitere Quellen:")
            for res in extras:
                lines.append(f"  • {res['title']}")
                lines.append(f"    {res['body'][:220]}")
                if res.get("url"): lines.append(f"    🔗 {res['url']}")
                lines.append("")

    if not lines:
        # Absoluter Fallback
        if results:
            lines.append("🔍 Gefundene Ergebnisse:")
            for res in results[:3]:
                if res.get("body"):
                    lines.append(f"• {res['title']}")
                    lines.append(f"  {res['body'][:300]}")
                    if res.get("url"): lines.append(f"  🔗 {res['url']}")
                    lines.append("")
        else:
            return f'Leider nichts zu "{qused}" gefunden. Versuche andere Stichwörter.'

    return "\n".join(lines).strip()


def extractive_answer(query: str, texts: list, n_sentences: int = 6) -> str:
    normalized = []
    for t in texts:
        if isinstance(t, tuple): normalized.append(t)
        elif isinstance(t, str) and t: normalized.append((t, ""))
    scored = _tfidf_scores(query, normalized)
    return _build_coherent_answer(query, scored, n=n_sentences)

# ══════════════════════════════════════════════════════════════
#  INTELLIGENZ-ENGINE  (Claude API + Gedächtnis + Web-Kontext)
# ══════════════════════════════════════════════════════════════

# Konversations-Gedächtnis (bleibt während der Session)
_conversation_memory: list = []   # [{"role":"user/assistant","content":"..."}]
_MAX_MEMORY = 20                   # letzte N Nachrichten merken


def _memory_add(role: str, content: str):
    _conversation_memory.append({"role": role, "content": content})
    # Über Limit → älteste (aber nie die erste System-Msg) kürzen
    while len(_conversation_memory) > _MAX_MEMORY:
        _conversation_memory.pop(0)


def _memory_clear():
    _conversation_memory.clear()


def _build_system_prompt() -> str:
    """Baut den System-Prompt mit aktuellem PC-Kontext."""
    now = datetime.datetime.now().strftime("%A, %d. %B %Y, %H:%M Uhr")
    name = get_user_name()
    try:
        i = sysinfo()
        pc_info = (f"CPU: {i['cpu']}%, RAM: {i['ram']}% "
                   f"({i['ram_used']}/{i['ram_total']} MB), "
                   f"Disk: {i['disk']}%")
        if i['akku']:
            pc_info += f", Akku: {i['akku'][0]}% {'(lädt)' if i['akku'][1] else ''}"
    except Exception:
        pc_info = "nicht verfügbar"

    return f"""Du bist J.A.R.V.I.S, ein smarter, persönlicher Windows-Assistent für {name}.

AKTUELLER KONTEXT:
- Zeit: {now}
- PC-Status: {pc_info}
- Nutzer: {name}

DEIN CHARAKTER:
- Intelligent, präzise, freundlich und direkt
- Du redest den Nutzer mit seinem Namen an wenn es passt
- Du antwortest auf Deutsch, kurz und klar
- Bei Fragen beantwortest du direkt und vollständig
- Du erinnerst dich an den bisherigen Gesprächsverlauf dieser Session
- Bei Rechenaufgaben, Logik, Code gibst du präzise Antworten
- Bei Wissensfragen kombinierst du dein Wissen mit den bereitgestellten Web-Infos
- Du schwärmst nicht übermäßig und bist nicht übertrieben höflich

WICHTIG:
- Wenn Web-Suchergebnisse beigefügt sind, nutze sie als primäre Informationsquelle
- Antworte immer auf Deutsch außer der Nutzer schreibt auf Englisch
- Halte Antworten prägnant – max 3-4 Sätze für einfache Fragen, mehr nur wenn nötig"""


def ask_claude(user_text: str, web_context: str = "") -> str:
    """
    Sendet Anfrage an Claude API mit Gedächtnis und optionalem Web-Kontext.
    Gibt Antwort-String zurück oder "" bei Fehler.
    """
    api_key = config.get("anthropic_api_key", "").strip()
    if not api_key or not REQ_OK:
        return ""

    # Nachricht aufbauen – Web-Kontext direkt in die User-Message
    if web_context:
        message_content = (f"{user_text}\n\n"
                           f"[Web-Recherche dazu]:\n{web_context[:3000]}")
    else:
        message_content = user_text

    # Gedächtnis + neue Nachricht
    messages = list(_conversation_memory) + [
        {"role": "user", "content": message_content}
    ]

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         api_key,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":      "claude-haiku-4-5-20251001",
                "max_tokens": 1024,
                "system":     _build_system_prompt(),
                "messages":   messages,
            },
            timeout=20,
        )
        if resp.status_code == 200:
            data = resp.json()
            answer = data["content"][0]["text"].strip()
            # Ins Gedächtnis aufnehmen
            _memory_add("user",      user_text)
            _memory_add("assistant", answer)
            return answer
        elif resp.status_code == 401:
            return "⚠️ Ungültiger API-Key. Bitte in den Einstellungen prüfen."
        elif resp.status_code == 429:
            return "⚠️ API-Limit erreicht. Bitte kurz warten."
        else:
            return ""
    except requests.Timeout:
        return ""
    except Exception:
        return ""




LOKAL = {
    "hallo":         "Hallo! Was kann ich für dich tun?",
    "hi":            "Hi! Wie kann ich helfen?",
    "hey":           "Hey! Was brauchst du?",
    "wer bist du":   "Ich bin J.A.R.V.I.S – dein smarter Windows-Assistent.",
    "danke":         "Gern geschehen! 😊",
    "danke schön":   "Sehr gerne!",
    "wie geht es":   "Mir geht's bestens! Dir?",
    "hilfe":         'Sage "alle Befehle" für eine vollständige Liste.',
}


def ki_antwort(text: str):
    """
    Haupt-KI-Logik:
    1. Konversation (Grüßen, Small Talk)
    2. Lokale Sofort-Antworten
    3. Claude API (mit Web-Kontext falls nötig)
    4. Fallback: lokale Web-Suche
    """
    t = text.lower().strip()

    # Gedächtnis löschen auf Befehl
    if any(w in t for w in ["vergiss alles","neues gespräch","konversation zurücksetzen","memory clear"]):
        _memory_clear()
        return "🧹 Gedächtnis geleert. Wir fangen frisch an!", None

    # Konversations-Antworten (Grüßen etc.)
    conv = conversation_response(text)
    if conv: return conv

    # Lokale Sofort-Antworten
    for key, antwort in LOKAL.items():
        if key in t: return antwort, None

    # ── Claude API verfügbar? ─────────────────────────────────
    api_key = config.get("anthropic_api_key", "").strip()

    if api_key and REQ_OK:
        # Entscheide ob Web-Suche nötig ist
        intent   = detect_intent(text)
        need_web = intent in ("news","kaufen","sport","film_serie") or \
                   any(w in t for w in ["aktuell","heute","neueste","preis","kosten",
                                        "wer hat gewonnen","ergebnis","wetter"])

        web_ctx = ""
        search_result = None

        if need_web:
            # Web-Suche parallel für Kontext
            search_result = web_suche(text, config.get("search_lang","de-de"))
            # Kompakten Kontext aus Suchergebnissen bauen
            ctx_parts = []
            if search_result.get("wiki"):
                ctx_parts.append(search_result["wiki"]["extract"][:800])
            for r in search_result.get("results", [])[:4]:
                if r.get("body"): ctx_parts.append(f"{r['title']}: {r['body'][:300]}")
            web_ctx = "\n\n".join(ctx_parts)

        answer = ask_claude(text, web_ctx)

        if answer and not answer.startswith("⚠️"):
            return answer, search_result

        # Bei API-Fehler: Fehlermeldung nur bei echtem Auth-Fehler zeigen
        if answer.startswith("⚠️"):
            return answer, None

    # ── Fallback: Lokale Web-Suche ────────────────────────────
    search_result = web_suche(text, config.get("search_lang","de-de"))
    return humanize_search_response(text, search_result), search_result



# ══════════════════════════════════════════
#  APPS
# ══════════════════════════════════════════
APPS = {
    "Chrome":         (r"C:\Program Files\Google\Chrome\Application\chrome.exe",       "🌐"),
    "Firefox":        (r"C:\Program Files\Mozilla Firefox\firefox.exe",                "🦊"),
    "Edge":           (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe","🌐"),
    "Opera":          (r"C:\Program Files\Opera\launcher.exe",                         "🌐"),
    "Notepad":        ("notepad.exe",                                                   "📝"),
    "Notepad++":      (r"C:\Program Files\Notepad++\notepad++.exe",                    "📝"),
    "Rechner":        ("calc.exe",                                                      "🧮"),
    "Explorer":       ("explorer.exe",                                                  "📁"),
    "CMD":            ("cmd.exe",                                                       "⬛"),
    "PowerShell":     ("powershell.exe",                                                "🔵"),
    "Paint":          ("mspaint.exe",                                                   "🎨"),
    "Task-Manager":   ("taskmgr.exe",                                                   "📊"),
    "Einstellungen":  ("ms-settings:",                                                  "⚙️"),
    "Systemsteuerung":("control.exe",                                                   "🖥️"),
    "Word":           (r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",  "📄"),
    "Excel":          (r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",    "📊"),
    "PowerPoint":     (r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE","📊"),
    "Outlook":        (r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE", "📧"),
    "VS Code":        (str(Path.home()/"AppData/Local/Programs/Microsoft VS Code/Code.exe"), "💻"),
    "VSCode":         (str(Path.home()/"AppData/Local/Programs/Microsoft VS Code/Code.exe"), "💻"),
    "PyCharm":        (r"C:\Program Files\JetBrains\PyCharm\bin\pycharm64.exe",         "🐍"),
    "VLC":            (r"C:\Program Files\VideoLAN\VLC\vlc.exe",                       "▶️"),
}
WEBS = {
    "youtube":"https://youtube.com","google":"https://google.com",
    "github":"https://github.com","twitch":"https://twitch.tv",
    "netflix":"https://netflix.com","amazon":"https://amazon.de",
    "reddit":"https://reddit.com","whatsapp":"https://web.whatsapp.com",
    "gmail":"https://gmail.com","chatgpt":"https://chat.openai.com",
    "wikipedia":"https://de.wikipedia.org","ebay":"https://ebay.de",
    "instagram":"https://instagram.com","twitter":"https://twitter.com",
    "tiktok":"https://tiktok.com",
}

def normalize_label(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())

def start_app(pfad):
    try:
        if pfad.startswith("ms-"): os.startfile(pfad)
        elif os.path.exists(pfad): subprocess.Popen([pfad])
        else:
            result = subprocess.run([pfad], capture_output=True, text=True, timeout=10)
            if result.returncode != 0: return False
        return True
    except Exception as e:
        print(f"Fehler beim Starten von {pfad}: {e}")
        return False


# ══════════════════════════════════════════
#  SYSTEM
# ══════════════════════════════════════════
def sysinfo():
    cpu = psutil.cpu_percent(interval=0.3)
    r   = psutil.virtual_memory()
    d   = psutil.disk_usage("/")
    b   = psutil.sensors_battery()
    net = psutil.net_io_counters()
    return {
        "cpu":cpu,"ram":r.percent,"disk":d.percent,
        "ram_used":r.used//(1024**2),"ram_total":r.total//(1024**2),
        "disk_free":d.free//(1024**3),"disk_total":d.total//(1024**3),
        "akku":(int(b.percent),b.power_plugged) if b else None,
        "proz":len(psutil.pids()),
        "net_up":net.bytes_sent//(1024**2),
        "net_dn":net.bytes_recv//(1024**2),
    }

def get_procs(n=50):
    procs = []
    for p in psutil.process_iter(["pid","name","cpu_percent","memory_percent","status"]):
        try: procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess): pass
    return sorted(procs, key=lambda x: x.get("memory_percent") or 0, reverse=True)[:n]

def set_vol(pct):
    pct = max(0, min(100, pct))
    sc = (f"$w=New-Object -ComObject WScript.Shell;"
          f"1..50|%{{$w.SendKeys([char]174)}};"
          f"1..{pct//2}|%{{$w.SendKeys([char]175)}}")
    threading.Thread(
        target=lambda: subprocess.run(["powershell","-Command",sc], capture_output=True),
        daemon=True).start()

def get_weather(city):
    if not REQ_OK: return None
    try:
        r = requests.get(f"https://wttr.in/{quote_plus(city)}?format=j1", timeout=5)
        d = r.json(); c = d["current_condition"][0]
        forecast = []
        for day in d.get("weather",[])[:3]:
            forecast.append({"date":day.get("date",""),"max":day["maxtempC"]+"°C",
                              "min":day["mintempC"]+"°C",
                              "desc":day["hourly"][4]["weatherDesc"][0]["value"]})
        return {"temp":c["temp_C"]+"°C","feel":c["FeelsLikeC"]+"°C",
                "desc":c["weatherDesc"][0]["value"],"humid":c["humidity"]+"%",
                "wind":c["windspeedKmph"]+" km/h","uv":c.get("uvIndex","?"),
                "forecast":forecast}
    except Exception: return None

def gen_pw(length=16, sym=True, nums=True, upper=True):
    chars = string.ascii_lowercase
    if upper: chars += string.ascii_uppercase
    if nums:  chars += string.digits
    if sym:   chars += "!@#$%&*-_=+?."
    return "".join(random.SystemRandom().choice(chars) for _ in range(length))

def pw_strength(pw):
    s = 0
    if len(pw) >= 12: s += 1
    if len(pw) >= 20: s += 1
    if re.search(r"[A-Z]", pw): s += 1
    if re.search(r"\d",   pw): s += 1
    if re.search(r"[^a-zA-Z0-9]", pw): s += 1
    labels = ["","Schwach","Mäßig","Gut","Stark","Sehr stark"]
    colors = [DIM2, RED, AMBER, CYAN, GREEN, GREEN]
    return labels[s], colors[s]


# ══════════════════════════════════════════
#  BEFEHLS-ROUTER   (FIX 3: app_state statt global)
# ══════════════════════════════════════════
# ══════════════════════════════════════════════════════════════
#  NLU-HELFER & PC-STEUERUNGS-FUNKTIONEN
# ══════════════════════════════════════════════════════════════

_FILLER_WORDS = [
    "bitte","kannst du","könntest du","würdest du","magst du",
    "kannst du mir","ich möchte dass du","ich will dass du",
    "ich brauche","ich hätte gerne","ich möchte","ich will",
    "mal kurz","mal eben","kurz","eben","doch","einfach",
    "für mich","sofort","jetzt","bitte mal","doch mal",
    "mach bitte","tu bitte","tu mal","kannst du bitte",
]

_NUM_MAP = {
    "null":0,"ein":1,"eine":1,"eins":1,"zwei":2,"drei":3,"vier":4,
    "fünf":5,"sechs":6,"sieben":7,"acht":8,"neun":9,"zehn":10,
    "elf":11,"zwölf":12,"dreizehn":13,"vierzehn":14,"fünfzehn":15,
    "sechzehn":16,"siebzehn":17,"achtzehn":18,"neunzehn":19,
    "zwanzig":20,"dreißig":30,"vierzig":40,"fünfzig":50,
    "sechzig":60,"siebzig":70,"achtzig":80,"neunzig":90,"hundert":100,
    "one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,
    "eight":8,"nine":9,"ten":10,"twenty":20,"thirty":30,"fifty":50,
}

KNOWN_FOLDERS = {
    "desktop":    str(Path.home()/"Desktop"),
    "downloads":  str(Path.home()/"Downloads"),
    "download":   str(Path.home()/"Downloads"),
    "dokumente":  str(Path.home()/"Documents"),
    "documents":  str(Path.home()/"Documents"),
    "bilder":     str(Path.home()/"Pictures"),
    "pictures":   str(Path.home()/"Pictures"),
    "fotos":      str(Path.home()/"Pictures"),
    "musik":      str(Path.home()/"Music"),
    "music":      str(Path.home()/"Music"),
    "videos":     str(Path.home()/"Videos"),
    "appdata":    str(Path.home()/"AppData"),
    "eigene dateien": str(Path.home()/"Documents"),
    "temp":       os.environ.get("TEMP","C:/Windows/Temp"),
}

SETTINGS_PAGES = {
    "display":"display","anzeige":"display","monitor":"display",
    "bluetooth":"bluetooth",
    "wlan":"network-wifi","wifi":"network-wifi","netzwerk":"network",
    "update":"windowsupdate","windows update":"windowsupdate",
    "energie":"powersleep","strom":"powersleep","akku einst":"powersleep",
    "sound":"sound","ton einst":"sound","audio":"sound",
    "konto":"accounts","benutzer einst":"accounts",
    "sprache einst":"regionlanguage","datenschutz":"privacy",
    "defender":"windowsdefender","firewall":"windowsdefender","virenschutz":"windowsdefender",
    "apps einst":"appsfeatures","speicher einst":"storagesense",
    "taskleiste":"taskbar","gaming einst":"gaming-gamebar",
    "drucker":"printers","maus einst":"mousetouchpad","tastatur einst":"keyboard",
    "zeitzone":"dateandtime","bildschirm":"display",
    "hintergrund":"personalization-background","sperrbildschirm":"lockscreen",
    "benachrichtigung einst":"notifications",
}

SYSTEM_TOOLS = {
    "snipping tool":       "SnippingTool.exe",
    "bildschirmtastatur":  "osk.exe",
    "lupe":                "magnify.exe",
    "narrator":            "narrator.exe",
    "registrierungseditor":"regedit.exe",
    "gerätemanager":       "devmgmt.msc",
    "datenträgerverwaltung":"diskmgmt.msc",
    "dienste":             "services.msc",
    "ereignisanzeige":     "eventvwr.msc",
    "systemeigenschaften": "sysdm.cpl",
    "netzwerkverbindungen":"ncpa.cpl",
}

_APP_ALIAS = {
    "browser":"Chrome","internet":"Chrome","web browser":"Chrome",
    "musikplayer":"VLC","mediaplayer":"VLC","videoplayer":"VLC",
    "texteditor":"Notepad","notizblock":"Notepad","editor":"Notepad",
    "terminal":"CMD","konsole":"CMD","eingabeaufforderung":"CMD",
    "dateiexplorer":"Explorer","dateiverwaltung":"Explorer",
    "taschenrechner":"Rechner","kalkulator":"Rechner",
    "malen":"Paint","zeichnen":"Paint",
    "vscode":"VS Code","visual studio code":"VS Code",
}

ALLE_BEFEHLE = """📋 J.A.R.V.I.S – ALLE BEFEHLE

⏰ ZEIT        "Uhrzeit" / "Datum" / "Welcher Tag"
🚀 APPS        "Öffne Chrome" / "Mach YouTube auf" / "Chrome öffnen"
📁 ORDNER      "Öffne Downloads" / "Desktop öffnen" / "Bilder anzeigen"
🔊 LAUTSTÄRKE  "Lautstärke auf 60" / "Lauter" / "Leiser" / "Lautlos"
🎵 MEDIEN      "Play" / "Pause" / "Nächster Song" / "Vorheriger"
💡 HELLIGKEIT  "Helligkeit auf 80" / "Heller" / "Dunkler"
🌙 DESIGN      "Dunkelmodus an/aus"
🔒 POWER       "PC sperren" / "Schlafmodus" / "Herunterfahren"
               "Neustart" / "Abmelden" / "Shutdown abbrechen"
🌐 NETZWERK    "Meine IP" / "Öffentliche IP" / "WLAN an/aus"
               "Ping google.com" / "DNS leeren" / "Internet testen"
🪟 FENSTER     "Fenster schließen/minimieren/maximieren"
               "Fenster links/rechts einrasten" / "Alle minimieren"
               "Fenster wechseln" / "Task-Ansicht" / "Alle Fenster"
               "Neues Desktop" / "Desktop links/rechts"
📸 SCREENSHOT  "Screenshot" / "Snipping Tool"
⌨️ EINGABE     "Tippe Hallo Welt" / "Enter/Escape/Tab drücken"
               "Kopieren/Einfügen/Rückgängig/Alles markieren"
               "Speichern" / "Drucken" / "Neues Tab" / "Neu laden"
               "Zoom rein/raus" / "Emoji-Tastatur" / "Ausführen"
🖱️ MAUS        "Linksklick" / "Rechtsklick" / "Doppelklick"
               "Scrollen oben/unten [N]"
📋 CLIPBOARD   "Zwischenablage anzeigen" / "Clipboard leeren"
               "Clipboard Verlauf" (Win+V)
🔧 SYSTEM      "Systeminfo" / "Prozesse anzeigen" / "Disk-Info"
               "Batteriebericht" / "Offene Fenster"
               "Prozess beenden [Name]" / "Temp leeren"
               "Papierkorb leeren" / "Gerätemanager"
📦 WINGET      "Installiere [App]" / "Deinstalliere [App]"
               "Suche App [Name]"
⚙️ EINST       "Display-Einstellungen" / "Bluetooth-Einstellungen"
               "Update-Einstellungen" / "Energie-Einstellungen"
🔍 BROWSER     "Suche nach [Begriff]" / "Google [Begriff]"
⏱ TIMER       "Timer 10 Minuten" / "Timer 30 Sekunden"
💬 CHAT        Alles andere → KI + Websuche

💡 Sprich natürlich: "Kannst du Chrome aufmachen?",
   "Mach bitte den PC leiser", "Ich will YouTube schauen" – alles OK!"""


def normalize_cmd(text: str) -> str:
    """Lowercase + Füllwörter entfernen + Zahlwörter → Ziffern."""
    t = text.lower().strip()
    t = re.sub(r"[?!,\.;:\"]","",t)
    for fw in sorted(_FILLER_WORDS, key=len, reverse=True):
        t = re.sub(rf"\b{re.escape(fw)}\b"," ",t)
    for word, digit in sorted(_NUM_MAP.items(), key=lambda x: -len(x[0])):
        t = re.sub(rf"\b{word}\b", str(digit), t, flags=re.IGNORECASE)
    return re.sub(r"\s+"," ",t).strip()


def has_kw(text: str, *keywords) -> bool:
    """True wenn mindestens eines der Keywords im Text vorkommt."""
    return any(kw in text for kw in keywords)


def _extract_number(text: str):
    """Erste Zahl aus Text extrahieren (nach Normalisierung)."""
    m = re.search(r"\d+", text)
    return int(m.group()) if m else None


def ps_run(cmd: str, timeout: int = 10):
    """PowerShell-Befehl asynchron ausführen."""
    threading.Thread(
        target=lambda: subprocess.run(
            ["powershell","-NoProfile","-Command",cmd],
            capture_output=True, timeout=timeout),
        daemon=True).start()


def media_key(action: str):
    """Virtuelle Media-Taste senden."""
    vk = {"play_pause":0xB3,"next":0xB0,"prev":0xB1,"stop":0xB2,
          "vol_up":0xAF,"vol_dn":0xAE,"mute":0xAD}
    k = vk.get(action)
    if k:
        ctypes.windll.user32.keybd_event(k,0,0,0)
        ctypes.windll.user32.keybd_event(k,0,2,0)


def vol_step(up: bool, steps: int = 4):
    """Lautstärke schrittweise erhöhen/senken."""
    key = "vol_up" if up else "vol_dn"
    for _ in range(steps): media_key(key)


def set_brightness(level: int):
    """Bildschirmhelligkeit setzen (0–100)."""
    level = max(0, min(100, level))
    ps_run(f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods)"
           f".WmiSetBrightness(1,{level})")


def get_brightness() -> int:
    """Aktuelle Helligkeit auslesen."""
    try:
        r = subprocess.run(
            ["powershell","-NoProfile","-Command",
             "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"],
            capture_output=True, text=True, timeout=5)
        return int(r.stdout.strip())
    except Exception: return -1


def brightness_step(up: bool) -> int:
    """Helligkeit um 20% erhöhen oder senken."""
    br   = get_brightness()
    base = br if br >= 0 else 60
    new  = min(100, base + 20) if up else max(0, base - 20)
    set_brightness(new)
    return new


def dark_mode_set(on: bool):
    """Windows Dark/Light Mode umschalten."""
    val = 0 if on else 1
    ps_run(f'Set-ItemProperty -Path '
           f'"HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" '
           f'-Name "AppsUseLightTheme" -Value {val};'
           f'Set-ItemProperty -Path '
           f'"HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" '
           f'-Name "SystemUsesLightTheme" -Value {val}')


def lock_screen():
    ctypes.windll.user32.LockWorkStation()


def sleep_pc():
    ps_run("Add-Type -Assembly System.Windows.Forms;"
           "[System.Windows.Forms.Application]::SetSuspendState('Suspend',$false,$false)")


def hibernate_pc():
    subprocess.run(["shutdown","/h"], capture_output=True)


def logoff_pc():
    subprocess.run(["shutdown","/l"], capture_output=True)


def shutdown_pc(delay: int = 10):
    subprocess.run(["shutdown","/s","/t",str(delay)], capture_output=True)


def restart_pc(delay: int = 10):
    subprocess.run(["shutdown","/r","/t",str(delay)], capture_output=True)


def cancel_shutdown():
    subprocess.run(["shutdown","/a"], capture_output=True)


def get_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80)); ip = s.getsockname()[0]; s.close()
        return ip
    except Exception: return "Nicht ermittelbar"


def get_public_ip() -> str:
    if not REQ_OK: return "requests nicht installiert"
    try: return requests.get("https://api.ipify.org", timeout=5).text.strip()
    except Exception: return "Nicht abrufbar"


def check_internet() -> bool:
    try: socket.create_connection(("8.8.8.8",53), timeout=3); return True
    except Exception: return False


def get_network_info() -> str:
    try:
        r = subprocess.run(["ipconfig"], capture_output=True, text=True,
                           encoding="cp850", timeout=5)
        lines = [l for l in r.stdout.splitlines()
                 if any(k in l for k in ["IPv4","IPv6","Standard","DNS","Subnetz","Adapter"])]
        return "\n".join(lines[:14]) or "Keine Infos"
    except Exception: return "Fehler"


def wifi_set(on: bool):
    state = "Enable" if on else "Disable"
    ps_run(f'Get-NetAdapter | Where-Object {{$_.Name -match "Wi-Fi|WLAN|Wireless"}} | '
           f'ForEach-Object {{ {state}-NetAdapter -Name $_.Name -Confirm:$false }}')


def flush_dns() -> str:
    try:
        subprocess.run(["ipconfig","/flushdns"], capture_output=True, timeout=5)
        return "✓ DNS-Cache geleert."
    except Exception: return "Fehler beim DNS-Flush."


def ping_host(host: str) -> str:
    try:
        r = subprocess.run(["ping","-n","3",host],
                           capture_output=True, text=True, encoding="cp850", timeout=12)
        lines = [l for l in r.stdout.splitlines() if l.strip()]
        return "\n".join(lines[-4:])
    except Exception: return f"Ping zu {host} fehlgeschlagen."


def kill_by_name(name: str) -> str:
    killed = 0
    for p in psutil.process_iter(["pid","name"]):
        try:
            if name.lower() in p.info["name"].lower():
                p.terminate(); killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied): pass
    return (f"✓ {killed} Prozess(e) '{name}' beendet." if killed
            else f"Kein Prozess '{name}' gefunden.")


def winget_install(app: str) -> str:
    def _do():
        subprocess.run(["winget","install","--accept-source-agreements",
                        "--accept-package-agreements","-e","--id",app],
                       capture_output=True)
    threading.Thread(target=_do, daemon=True).start()
    return f"⬇ Installiere '{app}' via winget..."


def winget_uninstall(app: str) -> str:
    def _do():
        subprocess.run(["winget","uninstall","-e","--id",app], capture_output=True)
    threading.Thread(target=_do, daemon=True).start()
    return f"🗑 Deinstalliere '{app}'..."


def winget_search(query: str) -> str:
    try:
        r = subprocess.run(["winget","search",query],
                           capture_output=True, text=True, encoding="utf-8", timeout=15)
        lines = r.stdout.strip().splitlines()
        return "\n".join(lines[:20]) or "Keine Ergebnisse."
    except Exception: return "winget nicht verfügbar."


def empty_recycle_bin() -> str:
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None,None,1)
        return "🗑 Papierkorb geleert."
    except Exception: return "Fehler."


def clear_temp() -> str:
    count = 0
    temp  = Path(os.environ.get("TEMP","C:/Windows/Temp"))
    for f in temp.iterdir():
        try:
            if f.is_file(): f.unlink(); count += 1
            elif f.is_dir(): shutil.rmtree(f, ignore_errors=True); count += 1
        except Exception: pass
    return f"🗑 {count} Temp-Einträge gelöscht."


def find_files(name: str) -> list:
    results = []
    try:
        for p in Path.home().rglob(f"*{name}*"):
            results.append(str(p))
            if len(results) >= 10: break
    except Exception: pass
    return results


def create_textfile(fname: str) -> str:
    if not fname.endswith(".txt"): fname += ".txt"
    p = Path.home()/"Desktop"/fname.replace(" ","_")
    p.write_text("", encoding="utf-8")
    return str(p)


def disk_info() -> str:
    lines = []
    for part in psutil.disk_partitions():
        try:
            u   = psutil.disk_usage(part.mountpoint)
            bar = "█"*(u.percent//10) + "░"*(10-u.percent//10)
            lines.append(f"  {part.device:<6} [{bar}] {u.percent}%  "
                         f"{u.used//(1024**3)}/{u.total//(1024**3)} GB")
        except Exception: pass
    return "\n".join(lines) or "Keine Disk-Infos"


def battery_report() -> str:
    try:
        p = str(Path.home()/"Desktop"/"battery-report.html")
        subprocess.run(["powercfg","/batteryreport","/output",p],
                       capture_output=True, timeout=8)
        os.startfile(p)
        return f"🔋 Batterie-Bericht erstellt:\n  {p}"
    except Exception: return "Batterie-Bericht fehlgeschlagen."


def windows_list_str() -> str:
    try:
        r = subprocess.run(
            ["powershell","-NoProfile","-Command",
             "Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | "
             "Select-Object -ExpandProperty MainWindowTitle"],
            capture_output=True, text=True, timeout=5)
        lines = [l.strip() for l in r.stdout.strip().splitlines() if l.strip()]
        return "\n".join(f"  • {l}" for l in lines[:15]) or "Keine Fenster."
    except Exception: return "Fehler."


def snap_window(side: str):
    m = {"links":"left","rechts":"right","oben":"up","unten":"down"}
    k = m.get(side)
    if k: pyautogui.hotkey("win",k)


def taskview():
    pyautogui.hotkey("win","tab")


def new_vdesktop():
    pyautogui.hotkey("win","ctrl","d")


def switch_vdesktop(direction: str):
    pyautogui.hotkey("win","ctrl","right" if direction=="rechts" else "left")


def close_vdesktop():
    pyautogui.hotkey("win","ctrl","f4")


def mouse_click(btn: str = "left", double: bool = False):
    if double: pyautogui.doubleClick()
    elif btn == "right": pyautogui.rightClick()
    else: pyautogui.click()


def scroll_page(direction: str, amount: int = 5):
    pyautogui.scroll(amount if direction=="oben" else -amount)


def type_text(text: str):
    """Text via Clipboard in aktives Fenster tippen (Sonderzeichen-sicher)."""
    time.sleep(0.4)
    if CLIP_OK:
        old = ""
        try: old = __import__("pyperclip").paste()
        except Exception: pass
        __import__("pyperclip").copy(text)
        pyautogui.hotkey("ctrl","v")
        time.sleep(0.2)
        try: __import__("pyperclip").copy(old)
        except Exception: pass
    else:
        pyautogui.typewrite(text, interval=0.04)


def clip_get() -> str:
    if CLIP_OK:
        try: return __import__("pyperclip").paste()
        except Exception: pass
    return ""


def clip_set(text: str):
    if CLIP_OK:
        try: __import__("pyperclip").copy(text)
        except Exception: pass


def toast_notify(title: str, msg: str):
    """Windows-Toast-Benachrichtigung."""
    t = title.replace("'","''"); m = msg.replace("'","''")
    ps_run(f"""try {{
  [Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime] | Out-Null
  $xml = [Windows.Data.Xml.Dom.XmlDocument,Windows.Data.Xml.Dom.XmlDocument,ContentType=WindowsRuntime]::New()
  $xml.LoadXml('<toast><visual><binding template="ToastText02"><text id="1">{t}</text><text id="2">{m}</text></binding></visual></toast>')
  $toast = [Windows.UI.Notifications.ToastNotification,Windows.UI.Notifications,ContentType=WindowsRuntime]::New($xml)
  [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('JARVIS').Show($toast)
}} catch {{}}""")


def open_settings(page: str):
    """Windows-Einstellungs-Seite via ms-settings: URI öffnen."""
    mapping = {
        "display":"ms-settings:display","anzeige":"ms-settings:display",
        "bluetooth":"ms-settings:bluetooth",
        "network-wifi":"ms-settings:network-wifi","network":"ms-settings:network",
        "windowsupdate":"ms-settings:windowsupdate","update":"ms-settings:windowsupdate",
        "powersleep":"ms-settings:powersleep","energie":"ms-settings:powersleep",
        "sound":"ms-settings:sound","ton":"ms-settings:sound",
        "accounts":"ms-settings:accounts","regionlanguage":"ms-settings:regionlanguage",
        "privacy":"ms-settings:privacy","windowsdefender":"ms-settings:windowsdefender",
        "appsfeatures":"ms-settings:appsfeatures","storagesense":"ms-settings:storagesense",
        "taskbar":"ms-settings:taskbar","gaming-gamebar":"ms-settings:gaming-gamebar",
        "printers":"ms-settings:printers","mousetouchpad":"ms-settings:mousetouchpad",
        "keyboard":"ms-settings:keyboard","dateandtime":"ms-settings:dateandtime",
        "personalization-background":"ms-settings:personalization-background",
        "lockscreen":"ms-settings:lockscreen","notifications":"ms-settings:notifications",
    }
    uri = mapping.get(page, f"ms-settings:{page}")
    try: os.startfile(uri)
    except Exception: pass


def open_folder(path: str):
    try: subprocess.Popen(["explorer", path])
    except Exception: pass


# ══════════════════════════════════════════════════════════════
def route(text, on_search_result=None):
    raw = text.strip()
    b   = normalize_cmd(raw)   # normalisiert + Füllwörter weg
    def ok(t): return True, t, None

    # ── 0. Hilfe ──────────────────────────────────────────────
    if has_kw(b,"was kannst du","alle befehle","befehlsliste","hilfe befehle"):
        return ok(ALLE_BEFEHLE)

    # ── 1. Zeit & Datum ───────────────────────────────────────
    if has_kw(b,"uhrzeit","wie spät","welche uhrzeit","wie viel uhr","wieviel uhr"):
        return ok(datetime.datetime.now().strftime("Es ist %H:%M:%S Uhr."))
    if has_kw(b,"datum","welcher tag","welches datum","was für ein tag","was ist heute"):
        return ok(datetime.datetime.now().strftime("Heute ist %A, %d. %B %Y."))
    if has_kw(b,"uptime","wie lange läuft","laufzeit des systems"):
        boot = datetime.datetime.fromtimestamp(psutil.boot_time())
        up   = datetime.datetime.now() - boot
        h,r  = divmod(int(up.total_seconds()),3600); m=r//60
        return ok(f"⏱ System läuft seit {h}h {m}min")

    # ── 2. Apps & Webseiten öffnen ────────────────────────────
    _OPEN_VERBS = r"^(?:öffne|starte|start|open|launch|mach auf|zeig|zeige|ruf auf|geh auf|gehe auf|geh zu|gehe zu)\s+(?:den |die |das |mir )?"
    _AUF_PAT    = re.compile(r"^mach\s+(?:den |die |das )?(.+?)\s+(?:auf|offen)$")
    _END_PAT    = re.compile(r"^(?:den |die |das )?(.+?)\s+(?:öffnen|starten|aufmachen|aufrufen|anzeigen)$")
    _MAIN_PAT   = re.compile(_OPEN_VERBS + r"(.+)$")

    def _try_open(rest):
        rest = rest.strip().rstrip(".,!?")
        rn   = normalize_label(rest)
        # Ordner
        for fname, fpath in KNOWN_FOLDERS.items():
            if fname in rn:
                open_folder(fpath); return ok(f"📁 {fname.title()}")
        # Einstellungen
        for kw, page in SETTINGS_PAGES.items():
            if normalize_label(kw) in rn:
                open_settings(page); return ok(f"⚙️ {kw}-Einstellungen")
        # System-Tools
        for name, cmd in SYSTEM_TOOLS.items():
            if normalize_label(name) in rn:
                try: os.startfile(cmd) if cmd.endswith(':') else subprocess.Popen([cmd])
                except Exception: pass
                return ok(f"🔧 {name} geöffnet.")
        # Webseiten
        for s,u in WEBS.items():
            if s in rn: webbrowser.open(u); return ok(f"✓ Öffne {s}.")
        # App-Aliase
        for alias, real in _APP_ALIAS.items():
            if normalize_label(alias) in rn and real in APPS:
                start_app(APPS[real][0]); return ok(f"✓ Starte {real}.")
        # Apps direkt
        for name,(pfad,_) in APPS.items():
            if normalize_label(name) in rn:
                start_app(pfad); return ok(f"✓ Starte {name}.")
        # Custom Apps
        for name,pfad in config.get("custom_apps",{}).items():
            if normalize_label(name) in rn:
                start_app(pfad); return ok(f"✓ Starte {name}.")
        # URL direkt
        if rest.startswith("http"):
            webbrowser.open(rest); return ok(f"✓ Öffne {rest}")
        # Existierender Pfad
        if os.path.exists(rest):
            os.startfile(rest); return ok(f"✓ Öffne {rest}")
        # Shell-Fallback
        try: subprocess.Popen(rest, shell=True); return ok(f"✓ Starte '{rest}'")
        except Exception: return None

    for pat in [_AUF_PAT, _END_PAT, _MAIN_PAT]:
        m = pat.match(b)
        if m:
            res = _try_open(m.group(1))
            if res: return res

    # ── 3. App schließen ──────────────────────────────────────
    m = re.match(r"(?:schließ|beende|mach zu|kill|close)\s+(?:den |die |das )?(.+?)(?:\s+zu)?$", b)
    if m:
        name = m.group(1).strip()
        if has_kw(name,"fenster","aktiv","aktuelle"):
            pyautogui.hotkey("alt","f4"); return ok("🪟 Fenster geschlossen.")
        res = kill_by_name(name)
        if "0 Prozess" not in res and "Kein Prozess" not in res:
            return ok(res)

    # ── 4. Screenshot ─────────────────────────────────────────
    if has_kw(b,"screenshot","bildschirmfoto","screen shot"):
        if has_kw(b,"bereich","ausschnitt","snip","region"):
            subprocess.Popen(["SnippingTool.exe"]); return ok("✂️ Snipping Tool geöffnet.")
        p = str(Path.home()/"Desktop"/f"Screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        pyautogui.screenshot(p); return ok(f"📸 Screenshot:\n{p}")

    # ── 5. System-Info ────────────────────────────────────────
    if has_kw(b,"systeminfo","system info","system status","auslastung"):
        i = sysinfo()
        akku = f"\n🔋 {i['akku'][0]}% {'🔌' if i['akku'][1] else ''}" if i['akku'] else ""
        return ok(f"🖥️ System:\n  CPU:  {i['cpu']}%\n  RAM:  {i['ram']}% ({i['ram_used']}/{i['ram_total']}MB)\n  Disk: {i['disk']}% ({i['disk_free']}/{i['disk_total']}GB frei)\n  Proz: {i['proz']}{akku}")
    if re.fullmatch(r"cpu|ram|akku|batterie", b):
        i = sysinfo()
        if b=="cpu":   return ok(f"CPU: {i['cpu']}%")
        if b=="ram":   return ok(f"RAM: {i['ram']}% ({i['ram_used']}/{i['ram_total']}MB)")
        return ok(f"🔋 {i['akku'][0]}% {'🔌' if i['akku'][1] else '🔋'}" if i['akku'] else "Kein Akku.")
    if has_kw(b,"disk info","festplatten","laufwerke","disk"):
        return ok("💾 Festplatten:\n" + disk_info())
    if has_kw(b,"prozesse anzeigen","laufende prozesse","top prozesse"):
        procs = get_procs(12)
        lines = [f"  {p['name'][:28]:<29} RAM:{p.get('memory_percent',0):.1f}%" for p in procs]
        return ok("🔧 Prozesse:\n" + "\n".join(lines))
    if has_kw(b,"auflösung","bildschirmauflösung"):
        w,h = pyautogui.size(); return ok(f"🖥️ Auflösung: {w}×{h} px")
    if has_kw(b,"batteriebericht","battery report"):
        return ok(battery_report())
    if has_kw(b,"offene fenster","fenster liste","welche fenster"):
        return ok("🪟 Offene Fenster:\n" + windows_list_str())

    # ── 6. Lautstärke ─────────────────────────────────────────
    m = re.search(r"(?:lautstärke|volume)\s*(?:auf|auf:)?\s*(\d+)", b)
    if m: set_vol(int(m.group(1))); return ok(f"🔊 Lautstärke: {m.group(1)}%.")
    if has_kw(b,"lautlos","stumm","mute","stummschalten"):
        set_vol(0); return ok("🔇 Lautlos.")
    if has_kw(b,"volle lautstärke","maximale lautstärke","ganz laut"):
        set_vol(100); return ok("🔊 Maximum.")
    if has_kw(b,"lauter","lautstärke erhöhen","lautstärke rauf","volume up"):
        vol_step(True,4); return ok("🔊 Lauter.")
    if has_kw(b,"leiser","lautstärke senken","lautstärke runter","volume down"):
        vol_step(False,4); return ok("🔉 Leiser.")

    # ── 7. Medien ─────────────────────────────────────────────
    if has_kw(b,"play","wiedergabe starten","musik play","abspielen","song starten"):
        media_key("play_pause"); return ok("▶️ Play.")
    if has_kw(b,"pause","pausieren","musik pausieren") and not has_kw(b,"prozess"):
        media_key("play_pause"); return ok("⏸️ Pause.")
    if has_kw(b,"nächster song","nächstes lied","skip","next song","überspringen"):
        media_key("next"); return ok("⏭️ Nächster.")
    if has_kw(b,"vorheriger song","vorheriges lied","back","previous") and not has_kw(b,"fenster"):
        media_key("prev"); return ok("⏮️ Vorheriger.")
    if has_kw(b,"musik stopp","stop musik","wiedergabe stopp"):
        media_key("stop"); return ok("⏹️ Stop.")

    # ── 8. Helligkeit ─────────────────────────────────────────
    m = re.search(r"helligkeit\s*(?:auf|auf:)?\s*(\d+)", b)
    if m: set_brightness(int(m.group(1))); return ok(f"💡 Helligkeit: {m.group(1)}%.")
    if has_kw(b,"heller","helligkeit erhöhen","helligkeit rauf"):
        new = brightness_step(True); return ok(f"💡 Heller ({new}%).")
    if has_kw(b,"dunkler","helligkeit senken","helligkeit runter") and not has_kw(b,"modus"):
        new = brightness_step(False); return ok(f"💡 Dunkler ({new}%).")
    if has_kw(b,"helligkeit anzeigen","wie hell"):
        br = get_brightness()
        return ok(f"💡 Helligkeit: {br}%" if br>=0 else "Nur für Laptop-Bildschirme.")

    # ── 9. Dark/Night-Mode ────────────────────────────────────
    if has_kw(b,"dunkelmodus an","dark mode an","darkmode an","nachtmodus an"):
        dark_mode_set(True); return ok("🌙 Dunkelmodus an.")
    if has_kw(b,"dunkelmodus aus","dark mode aus","darkmode aus","nachtmodus aus","hellmodus"):
        dark_mode_set(False); return ok("☀️ Hellmodus an.")

    # ── 10. Power ─────────────────────────────────────────────
    if has_kw(b,"pc sperren","bildschirm sperren","sperren","lock pc","lock screen"):
        lock_screen(); return ok("🔒 PC gesperrt.")
    if has_kw(b,"schlafmodus","sleep mode","schlafen legen","suspend"):
        sleep_pc(); return ok("😴 Schlafmodus...")
    if has_kw(b,"ruhezustand","hibernate"):
        hibernate_pc(); return ok("💤 Ruhezustand...")
    if has_kw(b,"abmelden","ausloggen","logoff","sign out"):
        logoff_pc(); return ok("👋 Abmelden...")
    if has_kw(b,"herunterfahren","ausschalten","shutdown","pc aus","computer aus"):
        t2 = _extract_number(b) or 10
        shutdown_pc(t2); return ok(f"⬇ PC fährt in {t2}s herunter.")
    if has_kw(b,"neustart","neu starten","restart","reboot"):
        t2 = _extract_number(b) or 10
        restart_pc(t2); return ok(f"🔁 Neustart in {t2}s.")
    if has_kw(b,"shutdown abbrechen","herunterfahren abbrechen","neustart abbrechen"):
        cancel_shutdown(); return ok("✓ Herunterfahren abgebrochen.")

    # ── 11. Netzwerk ──────────────────────────────────────────
    if has_kw(b,"meine ip","ip adresse","lokale ip","local ip"):
        return ok(f"🌐 Lokale IP: {get_ip()}")
    if has_kw(b,"öffentliche ip","public ip","externe ip","was ist meine ip"):
        return ok(f"🌐 Öffentliche IP: {get_public_ip()}")
    if has_kw(b,"internet testen","internetverbindung","bin ich online","verbindung testen"):
        ok2 = check_internet()
        return ok("✅ Internet OK." if ok2 else "❌ Kein Internet.")
    if has_kw(b,"netzwerkinfo","netzwerk info","ipconfig","netzwerk status"):
        return ok("🌐 Netzwerk:\n" + get_network_info())
    if has_kw(b,"wlan an","wifi an","wlan einschalten","wifi einschalten"):
        wifi_set(True); return ok("📶 WLAN ein...")
    if has_kw(b,"wlan aus","wifi aus","wlan ausschalten","wifi ausschalten"):
        wifi_set(False); return ok("📵 WLAN aus...")
    if has_kw(b,"dns leeren","dns flush","flushdns"):
        return ok(flush_dns())
    m = re.search(r"ping\s+([\w\.\-]+)", b)
    if m: return ok(f"📡 Ping {m.group(1)}:\n{ping_host(m.group(1))}")

    # ── 12. Fenster ───────────────────────────────────────────
    if has_kw(b,"fenster schließen","schließ fenster","schließe das fenster","fenster zu","mach fenster zu"):
        pyautogui.hotkey("alt","f4"); return ok("🪟 Fenster geschlossen.")
    if has_kw(b,"fenster minimieren","minimiere fenster","fenster klein","mach fenster klein"):
        pyautogui.hotkey("win","down"); return ok("🪟 Minimiert.")
    if has_kw(b,"fenster maximieren","maximiere fenster","vollbild","fullscreen"):
        pyautogui.hotkey("win","up"); return ok("🪟 Maximiert.")
    if has_kw(b,"fenster links","links einrasten","snap links"):
        snap_window("links"); return ok("🪟 Links.")
    if has_kw(b,"fenster rechts","rechts einrasten","snap rechts"):
        snap_window("rechts"); return ok("🪟 Rechts.")
    if has_kw(b,"fenster wechseln","alt tab","nächstes fenster"):
        pyautogui.hotkey("alt","tab"); return ok("🔄 Fenster wechseln.")
    if has_kw(b,"task ansicht","taskansicht","alle fenster","übersicht"):
        taskview(); return ok("🗂️ Task-Ansicht.")
    if has_kw(b,"alle minimieren","alle fenster minimieren"):
        pyautogui.hotkey("win","m"); return ok("🪟 Alle minimiert.")
    if has_kw(b,"alle wiederherstellen","alle fenster wiederherstellen"):
        pyautogui.hotkey("win","shift","m"); return ok("🪟 Alle wiederhergestellt.")
    if has_kw(b,"neues desktop","neuer desktop","virtuelles desktop"):
        new_vdesktop(); return ok("➕ Neues Desktop.")
    if has_kw(b,"desktop rechts","nächstes desktop"):
        switch_vdesktop("rechts"); return ok("➡️ Desktop ►")
    if has_kw(b,"desktop links","vorheriges desktop"):
        switch_vdesktop("links"); return ok("⬅️ Desktop ◄")
    if has_kw(b,"virtuelles desktop schließen","desktop schließen"):
        close_vdesktop(); return ok("❌ Desktop geschlossen.")
    if has_kw(b,"desktop anzeigen","zeige desktop","zeig desktop","show desktop"):
        pyautogui.hotkey("win","d"); return ok("🖥️ Desktop.")

    # ── 13. Dateien ───────────────────────────────────────────
    if has_kw(b,"papierkorb leeren","papierkorb","mülleimer leeren"):
        return ok(empty_recycle_bin())
    if has_kw(b,"temp leeren","temp dateien","temporäre dateien"):
        return ok(clear_temp())
    m = re.search(r"(?:datei suchen|suche datei|finde datei)\s+(.+)", b)
    if m:
        res2 = find_files(m.group(1).strip())
        return ok("🔍 Gefunden:\n" + "\n".join(f"  {r}" for r in res2) if res2
                  else f"Keine Datei '{m.group(1)}' gefunden.")
    m = re.search(r"(?:erstelle textdatei|neue textdatei|textdatei)\s*(.+)?", b)
    if m:
        p2 = create_textfile((m.group(1) or "Neue_Datei").strip())
        os.startfile(p2); return ok(f"📄 Erstellt:\n{p2}")

    # ── 14. Prozess beenden ───────────────────────────────────
    m = re.search(r"(?:prozess beenden|beende prozess|kill|töte)\s+(.+)", b)
    if m: return ok(kill_by_name(m.group(1).strip()))

    # ── 15. Clipboard ─────────────────────────────────────────
    if has_kw(b,"zwischenablage anzeigen","clipboard anzeigen","was ist in der zwischenablage"):
        clip = clip_get()
        return ok(f"📋 Clipboard:\n{clip[:600]}" if clip else "📋 Clipboard leer.")
    if has_kw(b,"zwischenablage leeren","clipboard leeren"):
        clip_set(""); return ok("📋 Clipboard geleert.")
    if has_kw(b,"clipboard verlauf","zwischenablage verlauf"):
        pyautogui.hotkey("win","v"); return ok("📋 Clipboard-Verlauf.")
    m = re.search(r"(?:in zwischenablage|clipboard setzen|kopiere in clipboard)\s+(.+)", b)
    if m: clip_set(m.group(1).strip()); return ok("📋 Kopiert.")

    # ── 16. Text tippen ───────────────────────────────────────
    m = re.match(r"^(?:tippe|schreibe|eingabe|type)\s+(.+)$", b)
    if m: type_text(m.group(1).strip()); return ok(f"⌨️ Getippt.")

    # ── 17. Tastatur-Shortcuts ────────────────────────────────
    _shortcuts = [
        (["enter drücken","drücke enter"],         lambda: pyautogui.press("enter"),          "↩️ Enter."),
        (["escape drücken","drücke escape","esc"],  lambda: pyautogui.press("escape"),         "⎋ Escape."),
        (["tab drücken","drücke tab"],              lambda: pyautogui.press("tab"),            "↹ Tab."),
        (["kopieren","copy"],                       lambda: pyautogui.hotkey("ctrl","c"),      "📋 Kopiert."),
        (["einfügen","paste"],                      lambda: pyautogui.hotkey("ctrl","v"),      "📋 Eingefügt."),
        (["ausschneiden","cut"],                    lambda: pyautogui.hotkey("ctrl","x"),      "✂️ Ausgeschnitten."),
        (["rückgängig","undo"],                     lambda: pyautogui.hotkey("ctrl","z"),      "↶ Rückgängig."),
        (["wiederholen","redo"],                    lambda: pyautogui.hotkey("ctrl","y"),      "↷ Wiederholt."),
        (["alles markieren","alles auswählen","select all"], lambda: pyautogui.hotkey("ctrl","a"), "☑️ Alles markiert."),
        (["speichern","save"],                      lambda: pyautogui.hotkey("ctrl","s"),      "💾 Gespeichert."),
        (["drucken","print"],                       lambda: pyautogui.hotkey("ctrl","p"),      "🖨️ Drucken."),
        (["neues tab","new tab"],                   lambda: pyautogui.hotkey("ctrl","t"),      "🗂️ Neues Tab."),
        (["tab schließen","close tab"],             lambda: pyautogui.hotkey("ctrl","w"),      "❌ Tab zu."),
        (["neu laden","refresh","reload"],          lambda: pyautogui.press("f5"),             "🔄 Reload."),
        (["neues fenster","new window"],            lambda: pyautogui.hotkey("ctrl","n"),      "🪟 Neues Fenster."),
        (["windows suche","suche öffnen"],          lambda: pyautogui.hotkey("win","s"),       "🔍 Suche."),
        (["ausführen","run dialog"],                lambda: pyautogui.hotkey("win","r"),       "▶️ Ausführen."),
        (["aktionscenter","action center"],         lambda: pyautogui.hotkey("win","a"),       "🔔 Aktionscenter."),
        (["emoji picker","emoji tastatur"],         lambda: pyautogui.hotkey("win","."),       "😊 Emoji-Picker."),
        (["zoom rein","zoom in","hineinzoomen"],    lambda: pyautogui.hotkey("ctrl","+"),      "🔍 Zoom +"),
        (["zoom raus","zoom out","herauszoomen"],   lambda: pyautogui.hotkey("ctrl","-"),      "🔎 Zoom -"),
        (["zoom reset","standard zoom"],            lambda: pyautogui.hotkey("ctrl","0"),      "🔍 Zoom reset."),
    ]
    for keywords, action, msg in _shortcuts:
        if has_kw(b, *keywords) and not has_kw(b,"einstellungen","zwischenablage","song"):
            action(); return ok(msg)

    # ── 18. Maus ──────────────────────────────────────────────
    if has_kw(b,"linksklick","left click","mausklick","klicken"):
        mouse_click("left"); return ok("🖱️ Klick.")
    if has_kw(b,"rechtsklick","right click","kontextmenü"):
        mouse_click("right"); return ok("🖱️ Rechtsklick.")
    if has_kw(b,"doppelklick","double click"):
        mouse_click("left", double=True); return ok("🖱️ Doppelklick.")
    m = re.search(r"scroll\s*(oben|hoch|rauf|up)", b)
    if m:
        scroll_page("oben", _extract_number(b) or 5); return ok("↑ Gescrollt.")
    m = re.search(r"scroll\s*(unten|runter|down)", b)
    if m:
        scroll_page("unten", _extract_number(b) or 5); return ok("↓ Gescrollt.")

    # ── 19. Einstellungen direkt ──────────────────────────────
    for kw, page in SETTINGS_PAGES.items():
        if f"{kw} einstellungen" in b or f"einstellungen {kw}" in b:
            open_settings(page); return ok(f"⚙️ {kw}-Einstellungen.")

    # ── 20. winget ────────────────────────────────────────────
    m = re.search(r"(?:installiere|install)\s+(.+)", b)
    if m: return ok(winget_install(m.group(1).strip()))
    m = re.search(r"(?:deinstalliere|uninstall|entferne)\s+(.+)", b)
    if m: return ok(winget_uninstall(m.group(1).strip()))
    m = re.search(r"(?:suche app|app suchen|winget suche)\s+(.+)", b)
    if m: return ok(winget_search(m.group(1).strip()))

    # ── 21. Browser-Suche ─────────────────────────────────────
    m = re.match(r"^(?:suche|google|bing|such nach|suche nach)\s+(?:nach\s+)?(.+)$", b)
    if m:
        q2 = m.group(1).strip()
        webbrowser.open(f"https://www.google.com/search?q={quote_plus(q2)}")
        return ok(f"🔍 Google: {q2}")

    # ── 22. Timer ─────────────────────────────────────────────
    m = re.search(r"timer\s+(?:für\s+|auf\s+|von\s+)?(\d+)\s*(sek\w*|min\w*|std\w*|stund\w*|h\b)?", b)
    if m:
        v  = int(m.group(1))
        e  = (m.group(2) or "sek").lower()
        s2 = v*(60 if "min" in e else 3600 if any(x in e for x in ["std","stund","h"]) else 1)
        def _timer_fn():
            time.sleep(s2)
            toast_notify("⏱ JARVIS", f"Timer {v} {e} abgelaufen!")
            subprocess.run(["powershell","-Command",
                'Add-Type -AN System.Windows.Forms;'
                '[System.Windows.Forms.MessageBox]::Show("Timer abgelaufen!","JARVIS ⏱")'],
                capture_output=True)
        threading.Thread(target=_timer_fn, daemon=True).start()
        return ok(f"⏱ Timer {v} {e} gestellt!")

    # ── 23. Benachrichtigung ──────────────────────────────────
    m = re.search(r"(?:benachrichtigung|notification|toast)\s+(.+)", b)
    if m: toast_notify("JARVIS", m.group(1)); return ok(f"🔔 {m.group(1)}")

    # ── 24. Letzte Antwort ────────────────────────────────────
    if has_kw(b,"sag das nochmal","wiederhole","nochmal","noch einmal"):
        last = app_state.get_response()
        return ok(last) if last else ok("Nichts zum Wiederholen.")

    # ── 25. Beenden ───────────────────────────────────────────
    if has_kw(b,"jarvis beenden","jarvis schließen","tschüss jarvis","auf wiedersehen","exit jarvis","bye jarvis"):
        return ok("__EXIT__")

    return False, "", None


# ══════════════════════════════════════════
#  UI-HELFER
# ══════════════════════════════════════════
def sep(parent, color=BORDER, pad=0):
    tk.Frame(parent, bg=color, height=1).pack(fill="x", padx=pad)

def card(parent, **kw):
    kw.pop('bg', None)
    return tk.Frame(parent, bg=BG3, bd=0, highlightthickness=1,
                    highlightbackground=BG4, highlightcolor=BG4, **kw)

def icon_btn(parent, text, cmd, bg=BG3, fg=TEXT2, hover_bg=BG4, hover_fg=CYAN,
             font=F_SMALL, padx=10, pady=5):
    b = tk.Label(parent, text=text, font=font, bg=bg, fg=fg,
                 cursor="hand2", padx=padx, pady=pady)
    b.bind("<Button-1>", lambda e: cmd())
    b.bind("<Enter>", lambda e: b.config(bg=hover_bg, fg=hover_fg))
    b.bind("<Leave>", lambda e: b.config(bg=bg, fg=fg))
    return b


# ══════════════════════════════════════════
#  CHAT MANAGER
# ══════════════════════════════════════════
class ChatManager:
    def __init__(self, parent_jarvis):
        self.jarvis      = parent_jarvis
        self._chat       = None
        self._res_frame  = None
        self._res_text   = None
        self._res_count  = None
        self._inp        = None
        self._inp_var    = None
        self._search_lbl = None
        # Kreis-Animation
        self._orb_canvas  = None
        self._orb_speaking = False
        self._orb_phase    = 0.0
        self._orb_rings    = []   # (canvas_id, radius, speed, color)

    def build(self, panel):
        split = tk.Frame(panel, bg=BG0); split.pack(fill="both", expand=True)

        # ── LINKS: Stimm-Kreis (Orb) ──────────────────────────────
        self._orb_col = tk.Frame(split, bg=BG0)
        self._orb_col.place(relx=0, rely=0, relheight=1, width=280)

        self._orb_canvas = tk.Canvas(self._orb_col, bg=BG0, highlightthickness=0)
        self._orb_canvas.pack(fill="both", expand=True)

        self._orb_label = tk.Label(self._orb_col, text="BEREIT", font=(FN,9,"bold"),
                                   bg=BG0, fg=DIM2)
        self._orb_label.pack(pady=(0,12))

        self._orb_canvas.bind("<Configure>", lambda e: self._orb_draw_idle())
        self._orb_loop()

        # ── DIVIDER (ziehbar) ─────────────────────────────────────
        self._divider_x = 280          # aktuelle Trennlinie in px
        self._divider   = tk.Frame(split, bg=BORDER, width=6, cursor="sb_h_double_arrow")
        self._divider.place(x=280, rely=0, relheight=1, width=6)

        self._divider.bind("<ButtonPress-1>",   self._div_start)
        self._divider.bind("<B1-Motion>",        self._div_drag)
        self._divider.bind("<ButtonRelease-1>",  self._div_end)
        self._divider.bind("<Enter>", lambda e: self._divider.config(bg=CYAN))
        self._divider.bind("<Leave>", lambda e: self._divider.config(bg=BORDER))

        # ── RECHTS: Chat-Text ──────────────────────────────────────
        self._chat_col = card(split, bg=BG1)
        self._chat_col.place(x=286, rely=0, relwidth=1, relheight=1)
        split.bind("<Configure>", lambda e: self._div_relayout(e.width))

        chat_col = self._chat_col

        chat_area = tk.Frame(chat_col, bg=BG1)
        chat_area.pack(fill="both", expand=True, padx=12, pady=12)
        csb = ttk.Scrollbar(chat_area); csb.pack(side="right", fill="y")
        self._chat = tk.Text(
            chat_area, font=(FN,10), bg=BG1, fg=TEXT,
            relief="flat", bd=0, padx=16, pady=12, wrap="word",
            state="disabled", yscrollcommand=csb.set, spacing1=2, spacing3=4,
        )
        self._chat.pack(fill="both", expand=True); csb.config(command=self._chat.yview)

        self._chat.tag_configure("u_name", foreground=BLUE,   font=(FN,10,"bold"))
        self._chat.tag_configure("u_body", foreground="#a8d5ff", background="#0a1628",
                                           lmargin1=24, lmargin2=24, spacing3=8, spacing1=2)
        self._chat.tag_configure("j_name", foreground=CYAN,   font=(FN,10,"bold"))
        self._chat.tag_configure("j_body", foreground=TEXT,    background=BG2,
                                           lmargin1=24, lmargin2=24, spacing3=8, spacing1=2)
        self._chat.tag_configure("code",   foreground=GREEN,   background="#050e05",
                                           lmargin1=24, lmargin2=24, font=(FC,10), spacing3=6)
        self._chat.tag_configure("sys",    foreground=DIM2,    font=(FN,9,"italic"), spacing3=4)
        self._chat.tag_configure("warn",   foreground=AMBER,   font=(FN,10,"bold"), spacing3=4)
        self._chat.tag_configure("link",   foreground=BLUE,    underline=True)

        self._res_frame = None
        self._res_text  = None
        self._res_count = None

        sep(panel)
        inp_f = card(panel, bg=BG2)
        inp_f.pack(fill="x", padx=14, pady=12)

        self._inp_var = tk.StringVar()
        self._inp = tk.Entry(inp_f, textvariable=self._inp_var,
                             font=(FN,12), bg=BG3, fg=CYAN,
                             relief="flat", insertbackground=CYAN,
                             highlightthickness=2,
                             highlightbackground=BORDER, highlightcolor=CYAN)
        self._inp.pack(side="left", fill="x", expand=True, ipady=10, padx=(0,10))
        self._inp.bind("<Return>",   lambda e: self.jarvis._send())
        # FIX 1: ↑↓ direkt im ChatManager behandeln
        self._inp.bind("<Up>",   self.hist_up)
        self._inp.bind("<Down>", self.hist_dn)
        self._inp.bind("<FocusIn>",  lambda e: self._inp.config(highlightbackground=CYAN))
        self._inp.bind("<FocusOut>", lambda e: self._inp.config(highlightbackground=BORDER))

        for ico, cmd, bg, fg in [
            ("▶", self.jarvis._send, CYAN, BG0),
            ("🎤", self.jarvis._mic_click, BG3, TEXT2),
            ("🗑", self.clear, BG3, DIM2),
        ]:
            b = tk.Button(inp_f, text=ico, font=(FN,14), bg=bg, fg=fg,
                          relief="flat", cursor="hand2", width=3,
                          activebackground=CYAN2 if ico=="▶" else BG4,
                          command=cmd)
            b.pack(side="right", padx=3, ipady=8)

        self._search_lbl = tk.Label(panel, text="", font=F_TINY, bg=BG0, fg=AMBER)
        self._search_lbl.pack(anchor="w", padx=14)

    # ── Öffentliche Methoden ─────────────
    def set_input(self, text):
        self.jarvis._nav("chat")
        self._inp_var.set(text)
        self._inp.focus(); self._inp.icursor("end")

    def set_search_text(self, text):
        # FIX 2: zentralisiert hier
        if self._search_lbl: self._search_lbl.config(text=text)

    def say(self, role, text, search_result=None):
        now = datetime.datetime.now().strftime('%H:%M')
        self._chat.config(state="normal")
        if role == "user":
            self._chat.insert("end", f"\n  ► Du   {now}\n", "u_name")
            self._insert_rich(text, "u_body")
        elif role == "bot":
            self._chat.insert("end", f"\n  ◈ J.A.R.V.I.S   {now}\n", "j_name")
            self._insert_rich(text, "j_body")
            if search_result:
                self.show_results(search_result)
            spreche(text)
        elif role == "warn":
            self._chat.insert("end", f"\n  {text}\n", "warn")
        else:
            self._chat.insert("end", f"\n  {text}\n", "sys")
        self._chat.config(state="disabled")
        self._chat.see("end")

    def _insert_rich(self, text, tag):
        for p in re.split(r"(```[\s\S]*?```)", text):
            if p.startswith("```"):
                code = re.sub(r"^```\w*\n?","",p).rstrip("`").strip()
                self._chat.insert("end", f"\n{code}\n\n", "code")
            else:
                self._chat.insert("end", f"  {p}\n", tag)

    def show_results(self, r):
        pass  # Suchergebnisse-Leiste entfernt

    def clear(self):
        self._chat.config(state="normal"); self._chat.delete("1.0","end")
        self._chat.config(state="disabled")

    # FIX 1: hist_up/dn leben hier, nicht auf Jarvis
    # ══════════════════════════════════════
    #  ORB – Sprachkreis Animation
    # ══════════════════════════════════════
    def _orb_draw_idle(self):
        """Zeichnet den ruhenden Orb."""
        if not self._orb_canvas: return
        cv = self._orb_canvas
        cv.delete("all")
        w = cv.winfo_width()  or 280
        h = cv.winfo_height() or 400
        cx, cy = w // 2, h // 2
        r = min(w, h) // 4

        # Äußere Glow-Ringe (statisch)
        for i, (rad_fac, alpha) in enumerate([(2.4, "#0a1a2a"), (2.0, "#0c2035"),
                                               (1.7, "#0e2840"), (1.45, "#102e4a")]):
            cv.create_oval(cx - r*rad_fac, cy - r*rad_fac,
                           cx + r*rad_fac, cy + r*rad_fac,
                           fill=alpha, outline="")

        # Haupt-Kreis
        cv.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#071830", outline=CYAN, width=2)

        # Inneres Symbol
        cv.create_text(cx, cy, text="◈", font=(FN, int(r*0.7), "bold"),
                       fill=CYAN)
        cv.create_text(cx, cy + r + 18, text="JARVIS", font=(FN, 9, "bold"),
                       fill=DIM2)

    def _orb_loop(self):
        """Animations-Loop – läuft permanent."""
        if not self._orb_canvas: return
        try:
            cv = self._orb_canvas
            w  = cv.winfo_width()  or 280
            h  = cv.winfo_height() or 400
        except Exception:
            return

        cx, cy = w // 2, h // 2
        r_base = min(w, h) // 4
        cv.delete("all")

        import math as _m
        t = self._orb_phase

        if self._orb_speaking:
            # ── SPRECHEN: pulsierende Wellen ──
            # Hintergrund-Glow
            for i in range(5):
                fac   = 2.6 - i * 0.25
                pulse = _m.sin(t * 3 + i * 0.8) * 0.12
                rad   = r_base * (fac + pulse)
                # Farbe von dunkel nach cyan
                intensity = int(max(0, min(255, 20 + i * 15 + _m.sin(t*2+i)*10)))
                color = f"#{intensity:02x}{intensity+20:02x}{min(255,intensity+60):02x}"
                cv.create_oval(cx-rad, cy-rad, cx+rad, cy+rad,
                               fill=color, outline="")

            # Haupt-Kreis pulsierend
            pulse_r = r_base * (1.0 + _m.sin(t * 4) * 0.08)
            glow_col = CYAN if _m.sin(t*3) > 0 else CYAN2
            cv.create_oval(cx-pulse_r-4, cy-pulse_r-4, cx+pulse_r+4, cy+pulse_r+4,
                           fill="", outline=glow_col, width=3)
            cv.create_oval(cx-pulse_r, cy-pulse_r, cx+pulse_r, cy+pulse_r,
                           fill="#071830", outline=CYAN, width=2)

            # Wellen-Ringe die nach außen wandern
            for i in range(3):
                wave_phase = (t * 1.5 + i * 0.7) % (2 * _m.pi)
                wave_r     = r_base * (1.2 + wave_phase * 0.4)
                alpha_val  = max(0, int(180 * (1 - wave_phase / (2*_m.pi))))
                if wave_r < r_base * 2.8 and alpha_val > 20:
                    # Simuliere Transparenz durch Farbmischung
                    mix = alpha_val / 255
                    r_c = int(mix * 0  + (1-mix) * 7)
                    g_c = int(mix * 217 + (1-mix) * 24)
                    b_c = int(mix * 255 + (1-mix) * 48)
                    ring_col = f"#{r_c:02x}{g_c:02x}{b_c:02x}"
                    cv.create_oval(cx-wave_r, cy-wave_r, cx+wave_r, cy+wave_r,
                                   fill="", outline=ring_col, width=2)

            # Inneres Symbol pulsierend
            sym_size = int(r_base * (0.65 + _m.sin(t*5)*0.05))
            cv.create_text(cx, cy, text="◈",
                           font=(FN, sym_size, "bold"), fill=CYAN)

            # Schallwellen-Balken links/rechts
            bars = 5
            for i in range(bars):
                bar_h = int(r_base * 0.3 * abs(_m.sin(t * (3+i) + i)))
                x_off = r_base * 1.4 + i * 8
                for sign in (1, -1):
                    x = cx + sign * x_off
                    cv.create_rectangle(x-3, cy-bar_h, x+3, cy+bar_h,
                                        fill=CYAN2, outline="")

            cv.create_text(cx, cy + r_base + 20,
                           text="SPRICHT...", font=(FN, 9, "bold"), fill=CYAN)
            self._orb_label.config(text="", fg=CYAN)

        else:
            # ── IDLE: ruhiger Glow ──
            for i, (fac, col) in enumerate([
                (2.4, "#070f1a"), (1.9, "#09162a"), (1.5, "#0c1e38")
            ]):
                # Leichter Atem-Effekt
                breath = _m.sin(t * 0.8) * 0.04
                rad    = r_base * (fac + breath)
                cv.create_oval(cx-rad, cy-rad, cx+rad, cy+rad, fill=col, outline="")

            cv.create_oval(cx-r_base, cy-r_base, cx+r_base, cy+r_base,
                           fill="#071830", outline=DIM, width=1)
            cv.create_text(cx, cy, text="◈",
                           font=(FN, int(r_base*0.65), "bold"), fill=DIM2)
            cv.create_text(cx, cy + r_base + 20,
                           text="JARVIS", font=(FN, 9, "bold"), fill=DIM2)
            self._orb_label.config(text="", fg=DIM2)

        self._orb_phase += 0.08
        # 40ms ≈ 25fps
        self._orb_canvas.after(40, self._orb_loop)

    def orb_start_speaking(self):
        """Aktiviert den Sprech-Effekt."""
        self._orb_speaking = True
        if self._orb_label:
            self._orb_label.config(fg=CYAN)

    def orb_stop_speaking(self):
        """Deaktiviert den Sprech-Effekt."""
        self._orb_speaking = False
        if self._orb_label:
            self._orb_label.config(fg=DIM2)

    def set_search_text(self, text):
        if self._search_lbl:
            self._search_lbl.config(text=text)


    # ── Divider-Logik ──────────────────────────────────────────
    def _div_start(self, e):
        self._drag_start_x   = e.x_root
        self._drag_start_div = self._divider_x

    def _div_drag(self, e):
        split_w = (self._orb_col.winfo_width()
                   + 6
                   + self._chat_col.winfo_width())
        delta = e.x_root - self._drag_start_x
        new_x = max(120, min(self._drag_start_div + delta, split_w - 200))
        self._divider_x = new_x
        self._orb_col.place(width=new_x)
        self._divider.place(x=new_x)
        self._chat_col.place(x=new_x + 6)

    def _div_end(self, e):
        self._divider.config(bg=BORDER)

    def _div_relayout(self, total_w):
        dx = self._divider_x
        self._orb_col.place(width=dx)
        self._divider.place(x=dx)
        self._chat_col.place(x=dx + 6)

    def hist_up(self, e):
        entries = [h["text"] for h in history]
        if not entries: return
        self.jarvis.hist_idx = min(self.jarvis.hist_idx+1, len(entries)-1)
        self._inp_var.set(entries[-(self.jarvis.hist_idx+1)])
        self._inp.icursor("end")

    def hist_dn(self, e):
        if self.jarvis.hist_idx <= 0:
            self.jarvis.hist_idx = -1; self._inp_var.set(""); return
        self.jarvis.hist_idx -= 1
        entries = [h["text"] for h in history]
        self._inp_var.set(entries[-(self.jarvis.hist_idx+1)])
        self._inp.icursor("end")


# ══════════════════════════════════════════
#  TOOLS MANAGER
# ══════════════════════════════════════════
class ToolsManager:
    def __init__(self, parent_jarvis):
        self.jarvis = parent_jarvis
        self._calc_expr = ""
        self._calc_var = None
        self._timer_run = False
        self._timer_end = None
        self._th = self._tm = self._ts = None
        self._timer_disp = None
        self._rem_txt = self._rem_time = self._rem_list = None
        self._note_lb = self._note_title = self._note_body = None
        self._cur_note = None
        self._clip_box = None
        self._pw_len = self._pw_sym = self._pw_num = self._pw_up = None
        self._pw_var = self._pw_str_lbl = None
        self._txt_ed = self._txt_stats = None
        self._weather_city = self._weather_f = None
        self._hist_box = None

    def build(self, panel):
        nb = ttk.Notebook(panel); nb.pack(fill="both", expand=True)
        for lbl, fn in [
            ("📝 Notizen",   self._tab_notes),
            ("📋 Clipboard", self._tab_clip),
            ("⏱ Timer",     self._tab_timer),
            ("🧮 Rechner",   self._tab_calc),
            ("🔑 Passwort",  self._tab_pw),
            ("✏️ Texttools", self._tab_text),
            ("🌤 Wetter",    self._tab_weather),
            ("📜 Verlauf",   self._tab_hist),
        ]:
            f = tk.Frame(nb, bg=BG1); nb.add(f, text=lbl); fn(f)

    # ── Notizen ─────────────────────────
    def _tab_notes(self, p):
        top = tk.Frame(p, bg=BG1); top.pack(fill="x")
        tk.Label(top, text="📝  Notizen", font=F_TITLE, bg=BG1, fg=WHITE).pack(side="left", padx=12, pady=8)
        for ico, lbl, cmd in [("+","Neu",self._note_new),("💾","Speichern",self._note_save),("🗑","Löschen",self._note_del)]:
            tk.Button(top, text=f"{ico} {lbl}", font=F_SMALL, bg=BG3, fg=TEXT2, relief="flat",
                      cursor="hand2", activebackground=BG4, activeforeground=CYAN,
                      command=cmd).pack(side="right", padx=3, pady=8, ipady=4)
        sep(p); row = tk.Frame(p, bg=BG1); row.pack(fill="both", expand=True)
        lf = tk.Frame(row, bg=BG2, width=230); lf.pack(side="left", fill="y"); lf.pack_propagate(False)
        ysb = ttk.Scrollbar(lf); ysb.pack(side="right", fill="y")
        self._note_lb = tk.Listbox(lf, font=F_SMALL, bg=BG2, fg=TEXT, relief="flat", bd=0,
                                   selectbackground=BLUE, selectforeground=WHITE,
                                   yscrollcommand=ysb.set, activestyle="none")
        self._note_lb.pack(fill="both", expand=True); ysb.config(command=self._note_lb.yview)
        self._note_lb.bind("<<ListboxSelect>>", self._note_sel)
        self._note_refresh()
        ef = tk.Frame(row, bg=BG1); ef.pack(side="left", fill="both", expand=True)
        self._note_title = tk.StringVar()
        tk.Entry(ef, textvariable=self._note_title, font=(FN,13,"bold"), bg=BG1, fg=WHITE,
                 relief="flat", insertbackground=CYAN, highlightthickness=0).pack(fill="x", padx=12, pady=(10,4), ipady=6)
        sep(ef, pad=12)
        self._note_body = tk.Text(ef, font=(FN,10), bg=BG1, fg=TEXT, relief="flat", bd=0,
                                  padx=14, pady=10, wrap="word", insertbackground=CYAN)
        self._note_body.pack(fill="both", expand=True, padx=4)

    def _note_refresh(self):
        self._note_lb.delete(0,"end")
        for n in all_notes: self._note_lb.insert("end","  "+(n.get("title","?"))[:30])

    def _note_new(self):
        all_notes.append({"title":"Neue Notiz","body":"","created":str(datetime.datetime.now())})
        notes_save(all_notes); self._note_refresh()
        self._note_lb.selection_clear(0,"end"); self._note_lb.selection_set(len(all_notes)-1)
        self._note_sel(None)

    def _note_sel(self, e):
        sel = self._note_lb.curselection()
        if not sel: return
        i = sel[0]; self._cur_note = i; n = all_notes[i]
        self._note_title.set(n.get("title",""))
        self._note_body.delete("1.0","end"); self._note_body.insert("1.0",n.get("body",""))

    def _note_save(self):
        if self._cur_note is None: return
        all_notes[self._cur_note]["title"] = self._note_title.get()
        all_notes[self._cur_note]["body"]  = self._note_body.get("1.0","end").strip()
        notes_save(all_notes); self._note_refresh(); self._note_lb.selection_set(self._cur_note)

    def _note_del(self):
        if self._cur_note is None: return
        if messagebox.askyesno("Löschen","Notiz löschen?"):
            all_notes.pop(self._cur_note); notes_save(all_notes); self._note_refresh()
            self._note_title.set(""); self._note_body.delete("1.0","end"); self._cur_note = None

    # ── Clipboard ───────────────────────
    def _tab_clip(self, p):
        top = tk.Frame(p, bg=BG1); top.pack(fill="x")
        tk.Label(top, text="📋  Clipboard-Verlauf", font=F_TITLE, bg=BG1, fg=WHITE).pack(side="left", padx=12, pady=8)
        tk.Button(top, text="🔄 Refresh", font=F_SMALL, bg=BG3, fg=TEXT2, relief="flat",
                  cursor="hand2", command=self._clip_refresh).pack(side="right", padx=8, pady=8, ipady=4)
        tk.Button(top, text="🗑 Leeren", font=F_SMALL, bg=BG3, fg=TEXT2, relief="flat",
                  cursor="hand2", command=lambda:(self.jarvis.clip_hist.clear(),self._clip_refresh())).pack(
                  side="right", padx=4, pady=8, ipady=4)
        sep(p)
        sb = ttk.Scrollbar(p); sb.pack(side="right", fill="y")
        self._clip_box = tk.Text(p, font=F_MONO_S, bg=BG1, fg=TEXT, relief="flat", bd=0,
                                 padx=14, pady=10, yscrollcommand=sb.set, state="disabled")
        self._clip_box.pack(fill="both", expand=True); sb.config(command=self._clip_box.yview)
        self._clip_box.tag_configure("idx", foreground=CYAN, font=F_MONO_B)
        self._clip_box.tag_configure("sep", foreground=DIM)
        self._clip_refresh()

    def _clip_refresh(self):
        try:
            if CLIP_OK:
                curr = __import__("pyperclip").paste()
                if curr and (not self.jarvis.clip_hist or self.jarvis.clip_hist[-1] != curr):
                    self.jarvis.clip_hist.append(curr)
        except Exception: pass
        self._clip_box.config(state="normal"); self._clip_box.delete("1.0","end")
        for i, t in enumerate(reversed(list(self.jarvis.clip_hist))):
            self._clip_box.insert("end",f"[{i+1}] ","idx")
            self._clip_box.insert("end",f"{t[:300]}\n")
            self._clip_box.insert("end","─"*60+"\n","sep")
        self._clip_box.config(state="disabled")

    # ── Timer ────────────────────────────
    def _tab_timer(self, p):
        f = tk.Frame(p, bg=BG1); f.pack(fill="both", expand=True, padx=24, pady=16)
        tk.Label(f, text="⏱  Timer", font=F_TITLE, bg=BG1, fg=WHITE).pack(anchor="w", pady=(0,12))
        irow = card(f); irow.pack(fill="x", pady=4, ipady=8)
        tk.Label(irow, text="Timer:", font=F_HEAD, bg=BG3, fg=TEXT, width=7, anchor="w").grid(row=0,column=0,padx=12,pady=8,sticky="w")
        self._th = tk.Spinbox(irow,from_=0,to=23,width=4,font=F_MONO,bg=BG4,fg=CYAN,relief="flat",buttonbackground=BG4,insertbackground=CYAN)
        self._th.grid(row=0,column=1,padx=4); tk.Label(irow,text="h",font=F_SMALL,bg=BG3,fg=DIM2).grid(row=0,column=2)
        self._tm = tk.Spinbox(irow,from_=0,to=59,width=4,font=F_MONO,bg=BG4,fg=CYAN,relief="flat",buttonbackground=BG4,insertbackground=CYAN)
        self._tm.grid(row=0,column=3,padx=4); tk.Label(irow,text="min",font=F_SMALL,bg=BG3,fg=DIM2).grid(row=0,column=4)
        self._ts = tk.Spinbox(irow,from_=0,to=59,width=4,font=F_MONO,bg=BG4,fg=CYAN,relief="flat",buttonbackground=BG4,insertbackground=CYAN)
        self._ts.grid(row=0,column=5,padx=4); tk.Label(irow,text="sek",font=F_SMALL,bg=BG3,fg=DIM2).grid(row=0,column=6)
        tk.Button(irow,text="▶ Start",font=F_HEAD,bg=CYAN,fg=BG0,relief="flat",cursor="hand2",
                  command=self.timer_start).grid(row=0,column=7,padx=12,pady=8,ipady=4)
        tk.Button(irow,text="⏹ Stop",font=F_HEAD,bg=BG4,fg=TEXT2,relief="flat",cursor="hand2",
                  command=self.timer_stop).grid(row=0,column=8,padx=4,pady=8,ipady=4)
        self._timer_disp = tk.Label(f, text="00:00:00", font=(FN,42,"bold"), bg=BG1, fg=CYAN)
        self._timer_disp.pack(pady=12)
        sep(f); sep_rem = tk.Frame(f, bg=BG1); sep_rem.pack(fill="x", pady=(12,6))
        tk.Label(sep_rem,text="🔔  Erinnerungen",font=F_TITLE,bg=BG1,fg=WHITE).pack(anchor="w")
        rrow = card(f); rrow.pack(fill="x",ipady=6,pady=4)
        self._rem_txt = tk.Entry(rrow,font=F_BODY,bg=BG4,fg=TEXT,relief="flat",
                                 insertbackground=CYAN,width=32,
                                 highlightthickness=1,highlightbackground=BORDER)
        self._rem_txt.pack(side="left",padx=12,pady=8,ipady=5,fill="x",expand=True)
        self._rem_txt.insert(0,"Text...")
        self._rem_time = tk.Entry(rrow,font=F_MONO,bg=BG4,fg=CYAN,relief="flat",
                                  insertbackground=CYAN,width=7,
                                  highlightthickness=1,highlightbackground=BORDER)
        self._rem_time.pack(side="left",padx=4,pady=8,ipady=5); self._rem_time.insert(0,"HH:MM")
        tk.Button(rrow,text="+ Setzen",font=F_HEAD,bg=PURPLE,fg=WHITE,relief="flat",
                  cursor="hand2",command=self._reminder_add).pack(side="right",padx=12,pady=8,ipady=4)
        self._rem_list = tk.Frame(f,bg=BG1); self._rem_list.pack(fill="x",pady=4)
        self._reminder_refresh()

    def timer_start(self):
        h=int(self._th.get() or 0); m=int(self._tm.get() or 0); s=int(self._ts.get() or 0)
        total = h*3600+m*60+s
        if total<=0: return
        self._timer_run=True; self._timer_end=time.time()+total; self._timer_tick()

    def timer_stop(self):
        self._timer_run = False

    def _timer_tick(self):
        if not self._timer_run:
            self._timer_disp.config(text="00:00:00",fg=CYAN); return
        rem = max(0,int(self._timer_end-time.time()))
        hh,r=divmod(rem,3600); mm,ss=divmod(r,60)
        self._timer_disp.config(text=f"{hh:02d}:{mm:02d}:{ss:02d}",
                                 fg=RED if rem<10 else AMBER if rem<30 else CYAN)
        if rem<=0:
            self._timer_run=False; self._timer_disp.config(text="✓ FERTIG!",fg=GREEN)
            spreche("Timer abgelaufen!"); messagebox.showinfo("⏱ JARVIS","Timer abgelaufen!")
        else: self.jarvis.root.after(1000,self._timer_tick)

    # FIX 5: _reminder_add speichert nur – kein neuer Thread pro Eintrag
    def _reminder_add(self):
        text = self._rem_txt.get().strip()
        t    = self._rem_time.get().strip()
        if not text or text=="Text..." or not re.match(r"\d{2}:\d{2}",t): return
        app_state.config.setdefault("reminders",[]).append(
            {"text":text,"time":t,"done":False})
        cfg_save(config)
        self._rem_txt.delete(0,"end"); self._rem_time.delete(0,"end")
        self._reminder_refresh()

    def _reminder_refresh(self):
        for w in self._rem_list.winfo_children(): w.destroy()
        for r in app_state.config.get("reminders",[])[-8:]:
            rf=tk.Frame(self._rem_list,bg=BG2); rf.pack(fill="x",pady=1)
            done=r.get("done",False)
            tk.Label(rf,text=f"  🔔  {r['time']}   {r['text']}",font=F_SMALL,
                     bg=BG2,fg=DIM2 if done else TEXT).pack(side="left",padx=6,pady=3)
            if done: tk.Label(rf,text="✓",font=F_SMALL,bg=BG2,fg=GREEN).pack(side="right",padx=8)

    # ── Rechner ──────────────────────────
    def _tab_calc(self, p):
        f = tk.Frame(p,bg=BG1); f.pack(expand=True)
        tk.Label(f,text="🧮  Rechner",font=F_TITLE,bg=BG1,fg=WHITE).pack(pady=(16,8))
        self._calc_var = tk.StringVar(value="0")
        self._calc_hist_lbl = tk.Label(f,text="",font=F_TINY,bg=BG1,fg=DIM2)
        self._calc_hist_lbl.pack(anchor="e",padx=48)
        tk.Label(f,textvariable=self._calc_var,font=(FN,28,"bold"),
                 bg=BG3,fg=CYAN,anchor="e",padx=16,width=14).pack(fill="x",padx=44,pady=(2,6))
        bf=tk.Frame(f,bg=BG1); bf.pack(padx=44)
        for row in [
            [("C",RED),("±",BG4),("%",BG4),("÷",PURPLE)],
            [("7",BG3),("8",BG3),("9",BG3),("×",PURPLE)],
            [("4",BG3),("5",BG3),("6",BG3),("−",PURPLE)],
            [("1",BG3),("2",BG3),("3",BG3),("+",PURPLE)],
            [("0",BG3),(".",BG3),("⌫",BG4),("=",CYAN)],
        ]:
            rf=tk.Frame(bf,bg=BG1); rf.pack()
            for lbl,color in row:
                tk.Button(rf,text=lbl,font=(FN,13,"bold"),bg=color,
                          fg=BG0 if lbl=="=" else WHITE,
                          relief="flat",cursor="hand2",width=4,
                          activebackground=BG4 if lbl!="=" else CYAN2,
                          command=lambda l=lbl: self.calc(l)).pack(side="left",padx=2,pady=2,ipady=10)

    def calc(self, btn):
        if btn=="C": self._calc_expr=""; self._calc_var.set("0"); self._calc_hist_lbl.config(text="")
        elif btn=="⌫": self._calc_expr=self._calc_expr[:-1]; self._calc_var.set(self._calc_expr or "0")
        elif btn=="=":
            try:
                expr=self._calc_expr.replace("÷","/").replace("×","*").replace("−","-")
                self._calc_hist_lbl.config(text=self._calc_expr+" =")
                r=safe_eval_math(expr); self._calc_var.set(str(round(r,10))); self._calc_expr=str(r)
            except (ValueError,ZeroDivisionError): self._calc_var.set("Fehler"); self._calc_expr=""
        elif btn=="±":
            try: self._calc_expr=str(-float(self._calc_expr)); self._calc_var.set(self._calc_expr)
            except ValueError: pass
        elif btn=="%":
            try: self._calc_expr=str(float(self._calc_expr)/100); self._calc_var.set(self._calc_expr)
            except ValueError: pass
        else: self._calc_expr+=btn; self._calc_var.set(self._calc_expr)

    # ── Passwort ─────────────────────────
    def _tab_pw(self, p):
        f=tk.Frame(p,bg=BG1); f.pack(fill="both",expand=True,padx=24,pady=16)
        tk.Label(f,text="🔑  Passwort-Generator",font=F_TITLE,bg=BG1,fg=WHITE).pack(anchor="w",pady=(0,12))
        opts=card(f); opts.pack(fill="x",pady=4,ipady=10)
        tk.Label(opts,text="Länge:",font=F_HEAD,bg=BG3,fg=TEXT).grid(row=0,column=0,padx=12,pady=8,sticky="w")
        self._pw_len=tk.IntVar(value=16)
        tk.Scale(opts,from_=8,to=64,variable=self._pw_len,orient="horizontal",
                 bg=BG3,fg=CYAN,troughcolor=BG4,highlightthickness=0,length=200,sliderlength=14,
                 command=lambda v:self._pw_gen()).grid(row=0,column=1,padx=8)
        tk.Label(opts,textvariable=self._pw_len,font=F_MONO_B,bg=BG3,fg=CYAN,width=3).grid(row=0,column=2)
        self._pw_sym=tk.BooleanVar(value=True); self._pw_num=tk.BooleanVar(value=True); self._pw_up=tk.BooleanVar(value=True)
        for col,(var,lbl) in enumerate([(self._pw_sym,"Sonderzeichen"),(self._pw_num,"Zahlen"),(self._pw_up,"Großbuchstaben")]):
            tk.Checkbutton(opts,text=lbl,variable=var,bg=BG3,fg=TEXT,selectcolor=BG4,
                           activebackground=BG3,command=self._pw_gen).grid(row=1,column=col,padx=12,sticky="w")
        self._pw_var=tk.StringVar()
        tk.Entry(f,textvariable=self._pw_var,font=(FC,14),bg=BG2,fg=GREEN,
                 relief="flat",state="readonly",readonlybackground=BG2,
                 highlightthickness=1,highlightbackground=BORDER).pack(fill="x",pady=12,ipady=10)
        br=tk.Frame(f,bg=BG1); br.pack(fill="x")
        tk.Button(br,text="🔄 Neu",font=F_HEAD,bg=CYAN,fg=BG0,relief="flat",cursor="hand2",
                  command=self._pw_gen,activebackground=CYAN2).pack(side="left",padx=(0,8),ipady=6,ipadx=16)
        tk.Button(br,text="📋 Kopieren",font=F_HEAD,bg=BG3,fg=TEXT2,relief="flat",cursor="hand2",
                  command=self._pw_copy).pack(side="left",ipady=6,ipadx=10)
        self._pw_str_lbl=tk.Label(f,text="",font=F_SMALL,bg=BG1,fg=DIM2)
        self._pw_str_lbl.pack(anchor="w",pady=(8,0))
        self._pw_gen()

    def _pw_gen(self,*_):
        pw=gen_pw(self._pw_len.get(),self._pw_sym.get(),self._pw_num.get(),self._pw_up.get())
        self._pw_var.set(pw); lbl,col=pw_strength(pw)
        self._pw_str_lbl.config(text=f"Stärke: {lbl}",fg=col)

    def _pw_copy(self):
        pw=self._pw_var.get()
        if pw and CLIP_OK: __import__("pyperclip").copy(pw); self.jarvis._say("system","📋 Passwort kopiert.")

    # ── Text-Tools ───────────────────────
    def _tab_text(self, p):
        f=tk.Frame(p,bg=BG1); f.pack(fill="both",expand=True)
        top=tk.Frame(f,bg=BG1); top.pack(fill="x",padx=12,pady=(8,4))
        tk.Label(top,text="✏️  Text-Werkzeuge",font=F_TITLE,bg=BG1,fg=WHITE).pack(side="left")
        br=tk.Frame(f,bg=BG1); br.pack(fill="x",padx=12,pady=(0,4))
        for lbl,cmd in [
            ("GROSS",     lambda:self._txt_do(str.upper)),
            ("klein",     lambda:self._txt_do(str.lower)),
            ("Titel",     lambda:self._txt_do(str.title)),
            ("Umkehren",  lambda:self._txt_do(lambda s:s[::-1])),
            ("Leerzeichen",lambda:self._txt_do(lambda s:re.sub(r" +"," ",s))),
            ("📋 Kopieren",self._txt_copy),
            ("🌐 Suchen",  self._txt_search),
        ]:
            tk.Button(br,text=lbl,font=F_SMALL,bg=BG3,fg=TEXT2,relief="flat",cursor="hand2",padx=8,
                      activebackground=BG4,activeforeground=CYAN,command=cmd).pack(side="left",padx=2,pady=4,ipady=4)
        sb=ttk.Scrollbar(f); sb.pack(side="right",fill="y",padx=(0,4))
        self._txt_ed=tk.Text(f,font=F_MONO,bg=BG2,fg=TEXT,relief="flat",bd=0,padx=12,pady=10,
                             wrap="word",insertbackground=CYAN,yscrollcommand=sb.set)
        self._txt_ed.pack(fill="both",expand=True,padx=(12,0)); sb.config(command=self._txt_ed.yview)
        self._txt_ed.insert("1.0","Text hier eingeben...")
        self._txt_stats=tk.Label(f,text="",font=F_TINY,bg=BG1,fg=DIM2)
        self._txt_stats.pack(anchor="w",padx=12,pady=4)
        self._txt_ed.bind("<KeyRelease>",lambda e:self._txt_update())
        self._txt_update()

    def _txt_do(self,fn):
        t=self._txt_ed.get("1.0","end-1c"); self._txt_ed.delete("1.0","end")
        self._txt_ed.insert("1.0",fn(t)); self._txt_update()

    def _txt_update(self):
        t=self._txt_ed.get("1.0","end-1c")
        w=len(t.split()) if t.strip() else 0
        self._txt_stats.config(text=f"  Wörter: {w}  ·  Zeichen: {len(t)}  ·  Zeilen: {t.count(chr(10))+1}")

    def _txt_copy(self):
        if CLIP_OK: __import__("pyperclip").copy(self._txt_ed.get("1.0","end-1c")); self.jarvis._say("system","📋 Text kopiert.")

    def _txt_search(self):
        t=self._txt_ed.get("1.0","end-1c").strip()[:300]
        if t: self.jarvis._nav("chat"); self.jarvis.chat_manager.set_input(t)

    # ── Wetter ───────────────────────────
    def _tab_weather(self, p):
        f=tk.Frame(p,bg=BG1); f.pack(fill="both",expand=True,padx=24,pady=16)
        top=tk.Frame(f,bg=BG1); top.pack(fill="x",pady=(0,12))
        tk.Label(top,text="🌤  Wetter",font=F_TITLE,bg=BG1,fg=WHITE).pack(side="left")
        self._weather_city=tk.StringVar(value=config.get("weather_city","Berlin"))
        tk.Entry(top,textvariable=self._weather_city,font=F_MONO,bg=BG3,fg=TEXT,
                 relief="flat",insertbackground=CYAN,width=18,
                 highlightthickness=1,highlightbackground=BORDER,highlightcolor=CYAN).pack(side="right",padx=(8,0),ipady=5)
        tk.Button(top,text="🔄 Laden",font=F_SMALL,bg=CYAN,fg=BG0,relief="flat",
                  cursor="hand2",command=self._weather_load).pack(side="right",ipady=5,ipadx=10)
        self._weather_f=tk.Frame(f,bg=BG1); self._weather_f.pack(fill="both",expand=True)
        tk.Label(self._weather_f,text="Klicke '🔄 Laden' für Wetterdaten.",font=F_BODY,bg=BG1,fg=DIM2).pack(pady=40)

    def _weather_load(self):
        city=self._weather_city.get()
        app_state.set("weather_city",city)
        for w in self._weather_f.winfo_children(): w.destroy()
        tk.Label(self._weather_f,text="Lade...",font=F_BODY,bg=BG1,fg=DIM2).pack(pady=40)
        def _go():
            w=get_weather(city)
            def _show():
                for x in self._weather_f.winfo_children(): x.destroy()
                if not w:
                    tk.Label(self._weather_f,text="Wetterdaten konnten nicht geladen werden.",
                             font=F_BODY,bg=BG1,fg=AMBER).pack(pady=40); return
                cur=card(self._weather_f); cur.pack(fill="x",pady=4,ipady=10)
                tk.Label(cur,text=city,font=(FN,14,"bold"),bg=BG3,fg=CYAN).pack(pady=(8,2))
                tk.Label(cur,text=w["temp"],font=(FN,36,"bold"),bg=BG3,fg=WHITE).pack()
                tk.Label(cur,text=w["desc"],font=F_BODY,bg=BG3,fg=TEXT2).pack()
                dr=tk.Frame(cur,bg=BG3); dr.pack(pady=8)
                for ico,lbl,val in [("🌡","Gefühlt",w["feel"]),("💧","Luftf.",w["humid"]),
                                    ("💨","Wind",w["wind"]),("☀️","UV",w.get("uv","?"))]:
                    df=tk.Frame(dr,bg=BG4); df.pack(side="left",padx=6,ipadx=10,ipady=6)
                    tk.Label(df,text=f"{ico} {lbl}",font=F_TINY,bg=BG4,fg=DIM2).pack()
                    tk.Label(df,text=val,font=F_HEAD,bg=BG4,fg=TEXT).pack()
                if w.get("forecast"):
                    tk.Label(self._weather_f,text="3-Tage-Vorschau",font=F_HEAD,bg=BG1,fg=DIM2).pack(anchor="w",pady=(10,4))
                    fr=tk.Frame(self._weather_f,bg=BG1); fr.pack(fill="x")
                    for day in w["forecast"]:
                        dc=card(fr); dc.pack(side="left",fill="x",expand=True,padx=4,ipady=8)
                        tk.Label(dc,text=day.get("date",""),font=F_TINY,bg=BG3,fg=DIM2).pack()
                        tk.Label(dc,text=f"{day['max']} / {day['min']}",font=F_HEAD,bg=BG3,fg=WHITE).pack(pady=2)
                        tk.Label(dc,text=day["desc"][:20],font=F_TINY,bg=BG3,fg=TEXT2,wraplength=90).pack()
            self.jarvis.root.after(0,_show)
        threading.Thread(target=_go,daemon=True).start()

    # ── Verlauf ──────────────────────────
    def _tab_hist(self, p):
        top=tk.Frame(p,bg=BG1); top.pack(fill="x")
        tk.Label(top,text="📜  Verlauf",font=F_TITLE,bg=BG1,fg=WHITE).pack(side="left",padx=12,pady=8)
        tk.Button(top,text="🗑 Leeren",font=F_SMALL,bg=BG3,fg=TEXT2,relief="flat",cursor="hand2",
                  command=lambda:(app_state.clear_history(),self._hist_refresh())).pack(side="right",padx=8,pady=8,ipady=4)
        sep(p)
        sb=ttk.Scrollbar(p); sb.pack(side="right",fill="y")
        self._hist_box=tk.Text(p,font=F_MONO_S,bg=BG1,fg=TEXT,relief="flat",bd=0,
                               padx=14,pady=10,yscrollcommand=sb.set,state="disabled")
        self._hist_box.pack(fill="both",expand=True); sb.config(command=self._hist_box.yview)
        self._hist_box.tag_configure("time",foreground=DIM2,font=F_TINY)
        self._hist_box.tag_configure("txt",foreground=TEXT)
        self._hist_box.tag_configure("sep",foreground=DIM)
        self._hist_refresh()

    def _hist_refresh(self):
        self._hist_box.config(state="normal"); self._hist_box.delete("1.0","end")
        for h in reversed(history[-100:]):
            self._hist_box.insert("end",f"  {h.get('time','')[:16]}\n","time")
            self._hist_box.insert("end",f"  {h.get('text','')}\n","txt")
            self._hist_box.insert("end","─"*60+"\n","sep")
        self._hist_box.config(state="disabled")


# ══════════════════════════════════════════
#  FILE MANAGER
# ══════════════════════════════════════════
class FileManager:
    def __init__(self, parent_jarvis):
        self.jarvis = parent_jarvis
        self._path_var = self._ftree = self._finfo = self._cur_path = None

    def build(self, panel):
        tb=tk.Frame(panel,bg=BG1); tb.pack(fill="x")
        tk.Label(tb,text="📁  Datei-Manager",font=F_TITLE,bg=BG1,fg=WHITE).pack(side="left",padx=14,pady=8)
        for ico,lbl,cmd in [
            ("🏠","Home",   lambda:self.nav(Path.home())),
            ("🖥️","Desktop",lambda:self.nav(Path.home()/"Desktop")),
            ("📥","Downs",  lambda:self.nav(Path.home()/"Downloads")),
            ("📄","Docs",   lambda:self.nav(Path.home()/"Documents")),
            ("↑","Hoch",   self.up),
        ]:
            tk.Button(tb,text=f"{ico} {lbl}",font=F_SMALL,bg=BG3,fg=TEXT2,
                      relief="flat",cursor="hand2",padx=6,
                      activebackground=BG4,activeforeground=CYAN,
                      command=cmd).pack(side="right",padx=2,pady=8,ipady=4)
        self._path_var=tk.StringVar(value=str(Path.home()))
        pe=tk.Entry(tb,textvariable=self._path_var,font=F_SMALL,bg=BG2,fg=TEXT,
                    relief="flat",insertbackground=CYAN,width=40,
                    highlightthickness=1,highlightbackground=BORDER,highlightcolor=CYAN)
        pe.pack(side="left",padx=8,ipady=4,fill="x",expand=True)
        pe.bind("<Return>",lambda e:self.nav(Path(self._path_var.get())))
        sep(panel)
        tf=tk.Frame(panel,bg=BG0); tf.pack(fill="both",expand=True)
        xsb=ttk.Scrollbar(tf,orient="horizontal"); xsb.pack(side="bottom",fill="x")
        ysb=ttk.Scrollbar(tf); ysb.pack(side="right",fill="y")
        self._ftree=ttk.Treeview(tf,columns=("name","typ","groesse","geaendert"),
                                  show="headings",yscrollcommand=ysb.set,xscrollcommand=xsb.set)
        self._ftree.pack(fill="both",expand=True)
        ysb.config(command=self._ftree.yview); xsb.config(command=self._ftree.xview)
        for col,w,h in [("name",360,"📄 Name"),("typ",90,"Typ"),("groesse",100,"Größe"),("geaendert",160,"Geändert")]:
            self._ftree.heading(col,text=h); self._ftree.column(col,width=w,minwidth=50)
        self._ftree.bind("<Double-1>",self.dbl_click)
        self._ftree.bind("<Button-3>",self.ctx_menu)
        bot=tk.Frame(panel,bg=BG1); bot.pack(fill="x")
        self._finfo=tk.Label(bot,text="",font=F_TINY,bg=BG1,fg=DIM2)
        self._finfo.pack(side="left",padx=12,pady=5)
        tk.Button(bot,text="📁 Neuer Ordner",font=F_SMALL,bg=BG3,fg=TEXT2,
                  relief="flat",cursor="hand2",command=self.mkdir).pack(side="right",padx=8,pady=5,ipady=3)

    def nav(self, path):
        try: items=list(Path(path).iterdir())
        except PermissionError: messagebox.showwarning("Zugriff verweigert","Kein Zugriff."); return
        self._path_var.set(str(path)); self._cur_path=Path(path)
        self._ftree.delete(*self._ftree.get_children())
        dirs,files=[],[]
        for it in items:
            try:
                st=it.stat(); mod=datetime.datetime.fromtimestamp(st.st_mtime).strftime("%d.%m.%Y %H:%M")
                if it.is_dir(): dirs.append(("📁 "+it.name,"Ordner","—",mod,str(it)))
                else:
                    sz=st.st_size
                    szs=(f"{sz//(1024**2)} MB" if sz>1024**2 else f"{sz//1024} KB" if sz>1024 else f"{sz} B")
                    files.append(("📄 "+it.name,it.suffix or "—",szs,mod,str(it)))
            except Exception: pass
        for d in sorted(dirs,key=lambda x:x[0]):
            self._ftree.insert("","end",values=d[:4],tags=("dir",),iid=d[4])
        for f in sorted(files,key=lambda x:x[0]):
            self._ftree.insert("","end",values=f[:4],tags=("file",),iid=f[4])
        self._ftree.tag_configure("dir",foreground=CYAN)
        self._finfo.config(text=f"  {len(dirs)} Ordner · {len(files)} Dateien  |  {path}")

    def up(self):
        if self._cur_path: self.nav(self._cur_path.parent)

    def dbl_click(self, event):
        sel=self._ftree.selection()
        if not sel: return
        p=Path(sel[0])
        if p.is_dir(): self.nav(p)
        else:
            try: os.startfile(str(p))
            except Exception: pass

    def ctx_menu(self, event):
        sel=self._ftree.identify_row(event.y)
        if not sel: return
        self._ftree.selection_set(sel); p=Path(sel)
        m=tk.Menu(self.jarvis.root,tearoff=0,bg=BG3,fg=TEXT,
                  activebackground=BLUE,activeforeground=WHITE,font=F_SMALL)
        m.add_command(label="  📂 Öffnen",
                      command=lambda:os.startfile(str(p)) if not p.is_dir() else self.nav(p))
        m.add_command(label="  📋 Pfad kopieren",
                      command=lambda:(CLIP_OK and __import__("pyperclip").copy(str(p)),
                                      self.jarvis._say("system","Pfad kopiert.")))
        m.add_separator()
        m.add_command(label="  ✏️  Umbenennen",command=lambda:self.rename(p))
        m.add_command(label="  🗑  Löschen",   command=lambda:self.delete(p))
        try: m.tk_popup(event.x_root,event.y_root)
        finally: m.grab_release()

    def rename(self, p):
        new=simpledialog.askstring("Umbenennen","Neuer Name:",initialvalue=p.name,parent=self.jarvis.root)
        if new:
            try: p.rename(p.parent/new); self.nav(self._cur_path)
            except Exception as ex: messagebox.showerror("Fehler",str(ex))

    def delete(self, p):
        if messagebox.askyesno("Löschen",f"'{p.name}' löschen?"):
            try:
                shutil.rmtree(p) if p.is_dir() else p.unlink()
                self.nav(self._cur_path)
            except Exception as ex: messagebox.showerror("Fehler",str(ex))

    def mkdir(self):
        if not self._cur_path: return
        name=simpledialog.askstring("Neuer Ordner","Name:",parent=self.jarvis.root)
        if name:
            try: (self._cur_path/name).mkdir(); self.nav(self._cur_path)
            except Exception as ex: messagebox.showerror("Fehler",str(ex))


# ══════════════════════════════════════════
#  HAUPT-APP
# ══════════════════════════════════════════
class Jarvis:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S  v5.0  [Fixed]")
        self.root.geometry("1380x840")
        self.root.minsize(1100,700)
        self.root.configure(bg=BG0)

        self.cpu_hist  = deque([0]*80, maxlen=80)
        self.ram_hist  = deque([0]*80, maxlen=80)
        self.clip_hist = deque(maxlen=60)
        self.hist_idx  = -1
        self.listening = False
        self.wakeword  = False
        self.cur_tab   = None

        self.chat_manager  = ChatManager(self)
        self.tools_manager = ToolsManager(self)
        self.file_manager  = FileManager(self)

        self._style()
        self._build()
        self._start_loops()

        self._say("system", f"J.A.R.V.I.S v5.0 — {datetime.datetime.now().strftime('%H:%M:%S')}")
        if mic_ok and config.get("wakeword_enabled",True):
            self._say("system", f"Wakeword '{config['wakeword']}' ist aktiv.")
        if not DDG_OK:
            self._say("warn","⚠  duckduckgo-search nicht gefunden → eingeschränkte Suche.")
        if not mic_ok:
            self._say("warn","⚠  Kein Mikrofon erkannt.")
        self.root.protocol("WM_DELETE_WINDOW",self._exit)
        self._nav("chat")

    # ── Style ────────────────────────────
    def _style(self):
        s=ttk.Style(); s.theme_use("clam")
        s.configure("TNotebook",       background=BG1,borderwidth=0)
        s.configure("TNotebook.Tab",   background=BG2,foreground=DIM2,padding=[16,9],font=(FN,10,"bold"))
        s.map("TNotebook.Tab",
              background=[("selected",BG4),("active",BG3)],
              foreground=[("selected",CYAN),("active",TEXT)])
        s.configure("Treeview",        background=BG3,foreground=TEXT,
                                        fieldbackground=BG3,rowheight=26,font=F_SMALL,borderwidth=0)
        s.configure("Treeview.Heading",background=BG4,foreground=CYAN,font=(FN,9,"bold"),borderwidth=0)
        s.map("Treeview",background=[("selected",BLUE)])
        s.configure("TScrollbar",      background=BG3,troughcolor=BG1,borderwidth=0,arrowsize=10,width=10)
        s.configure("TProgressbar",    background=CYAN,troughcolor=BG3,borderwidth=0,thickness=6)

    # ── Layout ───────────────────────────
    def _build(self):
        top=tk.Frame(self.root,bg=BG1,height=60); top.pack(fill="x"); top.pack_propagate(False)
        tk.Frame(top,bg=CYAN,width=4).pack(side="left",fill="y")
        logo=tk.Frame(top,bg=BG1); logo.pack(side="left",padx=(16,24),pady=6)
        tk.Label(logo,text="◈",font=(FN,20,"bold"),bg=BG1,fg=CYAN).pack(side="left",padx=(0,8))
        tk.Label(logo,text="J.A.R.V.I.S",font=(FN,16,"bold"),bg=BG1,fg=WHITE).pack(side="left")
        tk.Label(logo,text=" v5.0",font=(FN,9),bg=BG1,fg=DIM2).pack(side="left",padx=(6,0))
        status=tk.Frame(top,bg=BG1); status.pack(side="left",padx=(0,12),pady=10)
        self._status_dot=tk.Label(status,text="●",font=(FN,10),bg=BG1,fg=GREEN); self._status_dot.pack(side="left",padx=(0,6))
        self._status_var=tk.StringVar(value="BEREIT")
        tk.Label(status,textvariable=self._status_var,font=(FN,9),bg=BG1,fg=DIM2).pack(side="left")
        self._mode_var=tk.StringVar(value=self._get_mode_text())
        tk.Label(status,textvariable=self._mode_var,font=(FN,9),bg=BG1,fg=TEXT2).pack(side="left",padx=(12,0))
        self._time_lbl=tk.Label(top,text="",font=(FC,9),bg=BG1,fg=DIM2); self._time_lbl.pack(side="right",padx=16)
        self._mic_btn=tk.Button(top,text="🎤  Mikrofon",font=(FN,10,"bold"),bg=BG3,fg=TEXT2,
                                 relief="flat",cursor="hand2",padx=14,
                                 activebackground=RED,activeforeground=WHITE,
                                 command=self._mic_click,
                                 state="normal" if mic_ok else "disabled")
        self._mic_btn.pack(side="right",padx=(0,8),pady=10,ipady=6)
        sep(top)

        body=tk.Frame(self.root,bg=BG0); body.pack(fill="both",expand=True)
        sb=tk.Frame(body,bg=BG1,width=88); sb.pack(side="left",fill="y"); sb.pack_propagate(False)
        tk.Frame(sb,bg=BORDER,width=1).pack(side="right",fill="y")
        self._nav_btns={}
        for tid,ico,lbl in [("chat","💬","Chat"),("apps","⚡","Apps"),("files","📁","Dateien"),
                              ("tools","🔧","Tools"),("system","🖥️","System"),("settings","⚙️","Einst.")]:
            b=tk.Button(sb,text=f"{ico}\n{lbl}",font=(FN,9,"bold"),bg=BG2,fg=TEXT2,relief="flat",
                         wraplength=70,justify="center",cursor="hand2",
                         activebackground=BG4,activeforeground=CYAN,bd=0,highlightthickness=0,
                         command=lambda t=tid:self._nav(t))
            b.pack(fill="x",padx=8,pady=6,ipady=8); self._nav_btns[tid]=b

        self.content=tk.Frame(body,bg=BG0); self.content.pack(fill="both",expand=True)
        self.panels={}
        for tid in self._nav_btns:
            f=tk.Frame(self.content,bg=BG0)
            f.place(relx=0,rely=0,relwidth=1,relheight=1)
            self.panels[tid]=f

        self.chat_manager.build(self.panels["chat"])
        self._build_apps(self.panels["apps"])
        self.file_manager.build(self.panels["files"])
        self.tools_manager.build(self.panels["tools"])
        self._build_system(self.panels["system"])
        self._build_settings(self.panels["settings"])

    def _nav(self, tid):
        self.cur_tab=tid
        for k,b in self._nav_btns.items():
            b.config(bg=BG4 if k==tid else BG2, fg=CYAN if k==tid else TEXT2)
        for k,p in self.panels.items():
            (p.lower if k!=tid else p.lift)()
        if tid=="system": self._sys_refresh()
        if tid=="files" and not hasattr(self,"_files_init"):
            self.file_manager.nav(Path.home()); self._files_init=True

    # ── Öffentliche Shortcuts ────────────
    def _say(self, role, text, search_result=None):
        return self.chat_manager.say(role, text, search_result)

    def _set_inp(self, text):
        return self.chat_manager.set_input(text)

    # ── Senden ───────────────────────────
    def _send(self):
        text = self.chat_manager._inp_var.get().strip()
        if not text: return
        self.chat_manager._inp_var.set(""); self.hist_idx=-1
        app_state.add_history({"text":text,"time":str(datetime.datetime.now())})
        self._say("user", text)
        self._set_status("DENKT...", AMBER)
        self.chat_manager.set_search_text("")

        def _run():
            handled, antwort, _ = route(text)
            if antwort == "__EXIT__":
                self.root.after(0, lambda: self._say("bot","Auf Wiedersehen!"))
                spreche("Auf Wiedersehen!")
                self.root.after(1500, self._exit); return
            if handled:
                # FIX 3: app_state.set_response
                app_state.set_response(antwort)
                self.root.after(0, lambda a=antwort:(
                    self._say("bot",a), self._set_status("BEREIT",GREEN)))
            else:
                self.root.after(0, lambda:(
                    self._set_status("SUCHE...",AMBER),
                    # FIX 2: über chat_manager, nicht self._search_lbl
                    self.chat_manager.set_search_text("🌐 Suche im Internet...")))
                ki_txt, sr = ki_antwort(text)
                # FIX 3
                app_state.set_response(ki_txt)
                self.root.after(0, lambda t=ki_txt,r=sr:(
                    self._say("bot",t,r),
                    self._set_status("BEREIT",GREEN),
                    self.chat_manager.set_search_text("")))

        threading.Thread(target=_run, daemon=True).start()

    # ── Mikrofon ─────────────────────────
    def _mic_click(self):
        if self.listening: return
        self.listening=True; self._mic_btn.config(bg=RED,fg=WHITE)
        self._set_status("🎤 LAUSCHE",RED); self._nav("chat")
        threading.Thread(target=self._aufnehmen,daemon=True).start()

    def _aufnehmen(self):
        t=lausche()
        self.listening=False
        self.root.after(0,lambda:self._mic_btn.config(bg=BG3,fg=TEXT2))
        if t:
            self.root.after(0,lambda tx=t:(
                self._say("user",f"🎤 {tx}"),
                self._do_send(tx)))
        else: self._set_status("BEREIT",GREEN)

    def _do_send(self, text):
        self._set_status("DENKT...",AMBER)
        def _run():
            handled,antwort,_=route(text)
            if antwort=="__EXIT__":
                self.root.after(0,lambda:self._say("bot","Auf Wiedersehen!"))
                spreche("Auf Wiedersehen!"); self.root.after(1500,self._exit); return
            if handled:
                app_state.set_response(antwort)  # FIX 3
                self.root.after(0,lambda a=antwort:(self._say("bot",a),self._set_status("BEREIT",GREEN)))
            else:
                # FIX 2: chat_manager.set_search_text statt self._search_lbl
                self.root.after(0,lambda:self.chat_manager.set_search_text("🌐 Suche im Internet..."))
                ki_txt,sr=ki_antwort(text)
                app_state.set_response(ki_txt)   # FIX 3
                self.root.after(0,lambda t=ki_txt,r=sr:(
                    self._say("bot",t,r),self._set_status("BEREIT",GREEN),
                    self.chat_manager.set_search_text("")))
        threading.Thread(target=_run,daemon=True).start()

    # FIX 7: Wakeword-Loop prüft wakeword_enabled laufend
    def _ww_loop(self):
        while self.wakeword:
            if not config.get("wakeword_enabled", True):
                time.sleep(2); continue
            t=lausche(timeout=10,limit=4)
            if t and config.get("wakeword","jarvis") in t:
                self._set_status("AKTIVIERT!",GREEN); spreche("Ja?"); time.sleep(0.3)
                cmd=lausche(timeout=8,limit=15)
                if cmd:
                    self.root.after(0,lambda c=cmd:(
                        self._nav("chat"),self._say("user",f"🎤 {c}"),self._do_send(c)))

    # ── System-Panel ─────────────────────
    def _build_apps(self, p):
        hdr=tk.Frame(p,bg=BG1); hdr.pack(fill="x")
        tk.Label(hdr,text="⚡  App-Starter",font=F_TITLE,bg=BG1,fg=WHITE).pack(side="left",padx=14,pady=10)
        sv=tk.StringVar(); sv.trace("w",lambda *a:self._app_filter(sv.get()))
        se=tk.Entry(hdr,textvariable=sv,font=F_SMALL,bg=BG3,fg=TEXT,relief="flat",
                    insertbackground=CYAN,width=22,highlightthickness=1,
                    highlightbackground=BORDER,highlightcolor=CYAN)
        se.pack(side="right",padx=8,pady=10,ipady=5)
        se.insert(0,"🔍 Suchen...")
        se.bind("<FocusIn>",lambda e:se.delete(0,"end") if se.get().startswith("🔍") else None)
        tk.Button(hdr,text="+ Hinzufügen",font=F_SMALL,bg=BG3,fg=TEXT2,relief="flat",
                  cursor="hand2",activebackground=BG4,activeforeground=CYAN,
                  command=self._app_add).pack(side="right",padx=4,pady=10,ipady=4)
        sep(p)
        sf=tk.Frame(p,bg=BG0); sf.pack(fill="both",expand=True)
        sb=ttk.Scrollbar(sf); sb.pack(side="right",fill="y")
        self._app_cv=tk.Canvas(sf,bg=BG0,highlightthickness=0,yscrollcommand=sb.set)
        self._app_cv.pack(fill="both",expand=True); sb.config(command=self._app_cv.yview)
        self.app_grid=tk.Frame(self._app_cv,bg=BG0)
        self._app_win=self._app_cv.create_window(0,0,anchor="nw",window=self.app_grid)
        self.app_grid.bind("<Configure>",lambda e:(
            self._app_cv.configure(scrollregion=self._app_cv.bbox("all")),
            self._app_cv.itemconfig(self._app_win,width=self._app_cv.winfo_width())))
        self._app_cv.bind("<Configure>",lambda e:self._app_cv.itemconfig(self._app_win,width=e.width))
        self._app_cv.bind("<MouseWheel>",lambda e:self._app_cv.yview_scroll(-1*(e.delta//120),"units"))
        self._app_render(APPS)

    def _app_render(self, apps):
        if not hasattr(self,"app_grid"): return
        for w in self.app_grid.winfo_children(): w.destroy()
        all_apps=dict(apps)
        all_apps.update({k:(v,"📌") for k,v in config.get("custom_apps",{}).items()})
        cols=6
        for i,(name,(pfad,ico)) in enumerate(all_apps.items()):
            r,c=divmod(i,cols)
            fr=tk.Frame(self.app_grid,bg=BG3,highlightthickness=1,highlightbackground=BORDER)
            fr.grid(row=r,column=c,padx=6,pady=6,sticky="nsew",ipadx=2,ipady=4)
            self.app_grid.columnconfigure(c,weight=1)
            tk.Label(fr,text=ico,font=("Segoe UI Emoji",22),bg=BG3).pack(pady=(10,2))
            tk.Label(fr,text=name,font=(FN,8),bg=BG3,fg=TEXT2,wraplength=95,justify="center").pack(pady=(0,8))
            for w in [fr]+fr.winfo_children():
                w.bind("<Button-1>",lambda e,pf=pfad,n=name:self._launch(pf,n))
                w.bind("<Enter>",lambda e,f=fr:f.config(bg=BG4,highlightbackground=CYAN))
                w.bind("<Leave>",lambda e,f=fr:f.config(bg=BG3,highlightbackground=BORDER))

    def _app_filter(self, q):
        if not hasattr(self,"app_grid"): return
        q=q.lower().strip()
        if not q or q.startswith("🔍"): self._app_render(APPS); return
        f={k:v for k,v in APPS.items() if q in k.lower()}
        f.update({k:(v,"📌") for k,v in config.get("custom_apps",{}).items() if q in k.lower()})
        self._app_render(f)

    def _launch(self, pfad, name):
        if start_app(pfad): self._say("system",f"✓ {name} gestartet.")
        else: messagebox.showerror("Fehler",f"'{name}' konnte nicht gestartet werden.")

    def _app_add(self):
        name=simpledialog.askstring("App hinzufügen","Name:",parent=self.root)
        if not name: return
        pfad=filedialog.askopenfilename(filetypes=[("Programme","*.exe"),("Alle","*.*")])
        if pfad:
            config.setdefault("custom_apps",{})[name]=pfad
            cfg_save(config); self._app_render(APPS)

    def _build_system(self, p):
        hdr=tk.Frame(p,bg=BG1); hdr.pack(fill="x")
        tk.Label(hdr,text="🖥️  System-Monitor",font=F_TITLE,bg=BG1,fg=WHITE).pack(side="left",padx=14,pady=10)
        for lbl,cmd in [
            ("🔄 Refresh",self._sys_refresh),
            ("⬇ Herunterfahren",lambda:(subprocess.run(["shutdown","/s","/t","30"]),messagebox.showinfo("Herunterfahren","In 30s."))),
            ("🔁 Neustart",     lambda:(subprocess.run(["shutdown","/r","/t","30"]),messagebox.showinfo("Neustart","In 30s."))),
            ("❌ Abbrechen",    lambda:subprocess.run(["shutdown","/a"])),
        ]:
            tk.Button(hdr,text=lbl,font=F_SMALL,bg=BG3,fg=TEXT2,relief="flat",cursor="hand2",padx=8,
                      activebackground=BG4,activeforeground=CYAN,command=cmd).pack(side="right",padx=2,pady=10,ipady=4)
        sep(p)
        body=tk.Frame(p,bg=BG0); body.pack(fill="both",expand=True)
        lf=tk.Frame(body,bg=BG1,width=310); lf.pack(side="left",fill="y"); lf.pack_propagate(False)
        tk.Frame(lf,bg=BORDER,width=1).pack(side="right",fill="y")
        tk.Label(lf,text="  AUSLASTUNG",font=F_TINY,bg=BG1,fg=DIM2).pack(anchor="w",padx=12,pady=(12,4))
        self._sbars={}
        for name,lbl in [("cpu","CPU"),("ram","RAM"),("disk","DISK")]:
            fr=tk.Frame(lf,bg=BG1); fr.pack(fill="x",padx=12,pady=4)
            tk.Label(fr,text=f"{lbl}:",font=(FN,9,"bold"),bg=BG1,fg=TEXT2,width=5,anchor="w").pack(side="left")
            pb=ttk.Progressbar(fr,length=160,mode="determinate"); pb.pack(side="left",padx=6)
            lbl2=tk.Label(fr,text="0%",font=F_TINY,bg=BG1,fg=CYAN,width=5); lbl2.pack(side="right")
            self._sbars[name]=(pb,lbl2)
        tk.Label(lf,text="  CPU-VERLAUF",font=F_TINY,bg=BG1,fg=DIM2).pack(anchor="w",padx=12,pady=(12,4))
        self._cpu_cv=tk.Canvas(lf,height=70,bg=BG2,highlightthickness=1,highlightbackground=BORDER); self._cpu_cv.pack(fill="x",padx=12)
        tk.Label(lf,text="  RAM-VERLAUF",font=F_TINY,bg=BG1,fg=DIM2).pack(anchor="w",padx=12,pady=(10,4))
        self._ram_cv=tk.Canvas(lf,height=70,bg=BG2,highlightthickness=1,highlightbackground=BORDER); self._ram_cv.pack(fill="x",padx=12)
        tk.Label(lf,text="  LAUTSTÄRKE",font=F_TINY,bg=BG1,fg=DIM2).pack(anchor="w",padx=12,pady=(10,4))
        self._vol=tk.IntVar(value=50)
        tk.Scale(lf,from_=0,to=100,variable=self._vol,orient="horizontal",bg=BG1,fg=CYAN,
                  troughcolor=BG3,highlightthickness=0,length=240,sliderlength=14,
                  command=lambda v:set_vol(int(v))).pack(padx=12,anchor="w")
        self._sysdet=tk.Label(lf,text="",font=F_TINY,bg=BG1,fg=DIM2,justify="left")
        self._sysdet.pack(anchor="w",padx=14,pady=8)
        rf=tk.Frame(body,bg=BG0); rf.pack(side="left",fill="both",expand=True)
        tk.Label(rf,text="  PROZESSE",font=F_TINY,bg=BG0,fg=DIM2).pack(anchor="w",padx=12,pady=(12,4))
        ysb=ttk.Scrollbar(rf); ysb.pack(side="right",fill="y",padx=(0,4))
        self._ptree=ttk.Treeview(rf,columns=("pid","name","cpu","mem","status"),
                                   show="headings",yscrollcommand=ysb.set)
        self._ptree.pack(fill="both",expand=True,padx=(12,0)); ysb.config(command=self._ptree.yview)
        for col,w,h in [("pid",60,"PID"),("name",220,"Prozess"),("cpu",80,"CPU%"),("mem",90,"RAM%"),("status",90,"Status")]:
            self._ptree.heading(col,text=h); self._ptree.column(col,width=w,minwidth=40)
        bot=tk.Frame(rf,bg=BG0); bot.pack(fill="x",padx=12,pady=8)
        tk.Button(bot,text="⚠ Beenden",font=F_HEAD,bg=RED,fg=WHITE,relief="flat",cursor="hand2",
                  command=self._kill_proc).pack(side="left",ipady=5,ipadx=14)
        tk.Button(bot,text="🔄 Refresh",font=F_SMALL,bg=BG3,fg=TEXT2,relief="flat",cursor="hand2",
                  command=self._sys_refresh).pack(side="left",padx=8,ipady=5)

    def _sys_refresh(self):
        try:
            i=sysinfo()
            self.cpu_hist.append(i["cpu"]); self.ram_hist.append(i["ram"])
            for name,val in [("cpu",i["cpu"]),("ram",i["ram"]),("disk",i["disk"])]:
                pb,lbl=self._sbars[name]; pb["value"]=val
                lbl.config(text=f"{int(val)}%",fg=GREEN if val<60 else AMBER if val<85 else RED)
            self._draw_chart(self._cpu_cv,list(self.cpu_hist),CYAN)
            self._draw_chart(self._ram_cv,list(self.ram_hist),PURPLE)
            bat=i["akku"]
            bat_s=f"Akku: {bat[0]}% {'🔌' if bat[1] else '🔋'}\n" if bat else ""
            self._sysdet.config(text=(f"{bat_s}RAM: {i['ram_used']} / {i['ram_total']} MB\n"
                                       f"Disk: {i['disk_free']} / {i['disk_total']} GB frei\n"
                                       f"Prozesse: {i['proz']}\n"
                                       f"Netz ↑{i['net_up']}MB ↓{i['net_dn']}MB"))
            self._ptree.delete(*self._ptree.get_children())
            for proc in get_procs():
                self._ptree.insert("","end",iid=str(proc.get("pid","")),
                    values=(proc.get("pid",""),proc.get("name","")[:28],
                            f"{proc.get('cpu_percent',0):.1f}",
                            f"{proc.get('memory_percent',0):.1f}",proc.get("status","")))
        except Exception: pass

    def _draw_chart(self, cv, data, color):
        cv.delete("all"); w=cv.winfo_width() or 270; h=70
        if len(data)<2: return
        for yg in [17,35,53]: cv.create_line(0,yg,w,yg,fill=BORDER,width=1)
        coords=[]
        for ix,v in enumerate(data): coords+=[int(ix*w/(len(data)-1)),int(h-(v/100)*h)]
        cv.create_line(*coords,fill=color,width=1,smooth=True)
        cv.create_polygon([0,h]+coords+[w,h],fill=color,outline="",stipple="gray25")

    def _kill_proc(self):
        sel=self._ptree.selection()
        if not sel: return
        pid=int(sel[0])
        if messagebox.askyesno("Beenden",f"PID {pid} beenden?"):
            try: psutil.Process(pid).terminate(); self._sys_refresh()
            except Exception as ex: messagebox.showerror("Fehler",str(ex))

    def _build_settings(self, p):
        # ── scrollbare Hauptfläche ──
        sf = tk.Frame(p, bg=BG0); sf.pack(fill="both", expand=True)
        sb = ttk.Scrollbar(sf); sb.pack(side="right", fill="y")
        cv = tk.Canvas(sf, bg=BG0, highlightthickness=0, yscrollcommand=sb.set)
        cv.pack(fill="both", expand=True); sb.config(command=cv.yview)
        f  = tk.Frame(cv, bg=BG0); cv.create_window(0, 0, anchor="nw", window=f)
        f.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<MouseWheel>", lambda e: cv.yview_scroll(-1*(e.delta//120), "units"))

        # ── Variablen ──
        self._sv                  = {}
        self._wakeword_enabled_var= tk.BooleanVar(value=config.get("wakeword_enabled", True))
        self._speech_input_var    = tk.BooleanVar(value=config.get("speech_input_enabled", True))
        self._speak_var           = tk.BooleanVar(value=config.get("speak_answers", True))
        self._set_rate            = tk.IntVar(value=config.get("tts_rate", 150))
        self._dark_mode_var       = tk.BooleanVar(value=config.get("dark_mode", True))
        self._search_lang_var     = tk.StringVar(value=config.get("search_lang", "de-de"))
        self._user_name_var       = tk.StringVar(value=config.get("user_name", USER_DEFAULT_NAME))

        # ═══════════════════════════
        #  HEADER
        # ═══════════════════════════
        hdr = tk.Frame(f, bg=BG1); hdr.pack(fill="x", padx=0, pady=0)
        tk.Label(hdr, text="⚙  Einstellungen", font=(FN, 18, "bold"),
                 bg=BG1, fg=WHITE).pack(side="left", padx=24, pady=18)
        # Sofort-Speichern Button
        tk.Button(hdr, text="💾  Speichern",
                  font=(FN, 11, "bold"), bg=CYAN, fg=BG0,
                  relief="flat", cursor="hand2",
                  activebackground=CYAN2,
                  command=self._save_settings).pack(side="right", padx=24, pady=14, ipadx=20, ipady=8)
        # Reset Button
        tk.Button(hdr, text="↺  Zurücksetzen",
                  font=F_SMALL, bg=BG3, fg=DIM2,
                  relief="flat", cursor="hand2",
                  activebackground=BG4, activeforeground=TEXT,
                  command=self._reset_settings).pack(side="right", padx=4, pady=14, ipadx=10, ipady=8)
        sep(f)

        # ── Hilfsfunktion: Abschnitt-Header ──
        def section(title, icon):
            fr = tk.Frame(f, bg=BG0); fr.pack(fill="x", padx=24, pady=(20, 6))
            tk.Label(fr, text=icon, font=("Segoe UI Emoji", 14),
                     bg=BG0, fg=CYAN).pack(side="left", padx=(0, 8))
            tk.Label(fr, text=title, font=(FN, 12, "bold"),
                     bg=BG0, fg=CYAN).pack(side="left")
            c = card(f); c.pack(fill="x", padx=24, pady=(0, 4))
            return c

        # ── Hilfsfunktion: Zeile mit Label + Widget ──
        def row(parent, label, hint=""):
            r = tk.Frame(parent, bg=BG3); r.pack(fill="x", padx=2, pady=1)
            lf = tk.Frame(r, bg=BG3, width=200); lf.pack(side="left", fill="y")
            lf.pack_propagate(False)
            tk.Label(lf, text=label, font=F_HEAD, bg=BG3,
                     fg=TEXT, anchor="w").pack(side="left", padx=12, pady=10)
            wf = tk.Frame(r, bg=BG3); wf.pack(side="left", fill="x", expand=True, padx=(0, 12), pady=8)
            if hint:
                tk.Label(r, text=hint, font=F_TINY, bg=BG3,
                         fg=DIM2, wraplength=180, justify="right").pack(side="right", padx=12)
            return wf

        def toggle(parent, var, on_text="AN", off_text="AUS"):
            """Moderner Toggle statt hässlicher Checkbox."""
            fr = tk.Frame(parent, bg=BG3, cursor="hand2"); fr.pack(side="left")
            lbl = tk.Label(fr, font=(FN, 9, "bold"), padx=10, pady=3,
                           relief="flat", cursor="hand2")
            def _refresh(*_):
                if var.get():
                    lbl.config(text=on_text, bg=GREEN, fg=BG0)
                else:
                    lbl.config(text=off_text, bg=DIM, fg=TEXT2)
            _refresh()
            var.trace_add("write", _refresh)
            lbl.bind("<Button-1>", lambda e: (var.set(not var.get()), self._save_settings()))
            lbl.pack()
            return lbl

        def entry(parent, var, width=28, show=""):
            e = tk.Entry(parent, textvariable=var, font=F_MONO,
                         bg=BG4, fg=CYAN, relief="flat", show=show,
                         insertbackground=CYAN, width=width,
                         highlightthickness=1,
                         highlightbackground=BORDER, highlightcolor=CYAN)
            e.pack(side="left", ipady=5)
            e.bind("<FocusOut>", lambda _: self._save_settings())
            return e

        # ═══════════════════════════
        #  1. NUTZER
        # ═══════════════════════════
        c = section("Nutzer", "👤")
        wf = row(c, "Dein Name", "Wie JARVIS dich anspricht")
        entry(wf, self._user_name_var)

        c = section("Sprache & Suche", "🎙️")

        # Wakeword
        ww_var = tk.StringVar(value=config.get("wakeword", "jarvis"))
        self._sv["wakeword"] = ww_var
        wf = row(c, "Wakeword", "Aktivierungswort für Mikrofon")
        entry(wf, ww_var, width=16)

        # Wakeword aktiv
        wf = row(c, "Wakeword aktiv", "Lauscht im Hintergrund")
        toggle(wf, self._wakeword_enabled_var)

        # Spracheingabe
        wf = row(c, "Spracheingabe", "Mikrofon-Button aktiv")
        toggle(wf, self._speech_input_var)

        # Erkennungssprache
        speech_lang_var = tk.StringVar(value=config.get("speech_lang", "de-DE"))
        self._sv["speech_lang"] = speech_lang_var
        wf = row(c, "Erkennungssprache", "z.B. de-DE oder en-US")
        lang_cb = ttk.Combobox(wf, textvariable=speech_lang_var,
                               values=["de-DE","en-US","en-GB","fr-FR","es-ES","it-IT","nl-NL"],
                               font=F_SMALL, width=12, state="readonly")
        lang_cb.pack(side="left")
        lang_cb.bind("<<ComboboxSelected>>", lambda _: self._save_settings())

        # Suchsprache
        search_lang_var = tk.StringVar(value=config.get("search_lang", "de-de"))
        self._sv["search_lang"] = search_lang_var
        wf = row(c, "Suchsprache", "DDG Suchregion")
        sl_cb = ttk.Combobox(wf, textvariable=search_lang_var,
                             values=["de-de","en-us","en-gb","fr-fr","es-es","it-it"],
                             font=F_SMALL, width=12, state="readonly")
        sl_cb.pack(side="left")
        sl_cb.bind("<<ComboboxSelected>>", lambda _: self._save_settings())

        # ═══════════════════════════
        #  3. SPRACHAUSGABE
        # ═══════════════════════════
        c = section("Sprachausgabe (TTS)", "🔊")

        # Vorlesen AN/AUS
        wf = row(c, "Antworten vorlesen", "Spricht Antworten laut")
        toggle(wf, self._speak_var)

        # Geschwindigkeit
        wf = row(c, "Geschwindigkeit", f"Aktuell: {self._set_rate.get()}")
        rate_lbl = tk.Label(wf, text=str(self._set_rate.get()),
                            font=F_MONO_B, bg=BG3, fg=CYAN, width=4)
        rate_lbl.pack(side="right", padx=(4, 0))
        rate_scale = tk.Scale(wf, from_=80, to=300, variable=self._set_rate,
                              orient="horizontal", bg=BG3, fg=CYAN,
                              troughcolor=BG4, highlightthickness=0,
                              length=240, sliderlength=16, showvalue=False,
                              command=lambda v: (rate_lbl.config(text=str(int(float(v)))),
                                                 self._save_settings()))
        rate_scale.pack(side="left")

        # Stimme
        wf = row(c, "Stimme", "Installierte TTS-Stimmen")
        self._set_voice = ttk.Combobox(wf, values=[v.name for v in all_voices],
                                        font=F_SMALL, state="readonly", width=40)
        if all_voices:
            idx = config.get("voice", 0)
            if not isinstance(idx, int) or not (0 <= idx < len(all_voices)):
                idx = 0
            self._set_voice.set(all_voices[idx].name)
        self._set_voice.pack(side="left")
        self._set_voice.bind("<<ComboboxSelected>>", lambda _: self._save_settings())

        # Test-Button
        tk.Button(wf, text="▶ Test", font=F_SMALL, bg=BG4, fg=TEXT2,
                  relief="flat", cursor="hand2",
                  activebackground=BG4, activeforeground=CYAN,
                  command=lambda: spreche(f"Hallo {get_user_name()}, ich bin JARVIS!")
                  ).pack(side="left", padx=8, ipady=3, ipadx=6)

        # ═══════════════════════════
        #  4. WETTER
        # ═══════════════════════════
        c = section("Wetter", "🌤")
        city_var = tk.StringVar(value=config.get("weather_city", "Berlin"))
        self._sv["weather_city"] = city_var
        wf = row(c, "Heimatstadt", "Für Wetteranzeige")
        entry(wf, city_var, width=20)

        # ═══════════════════════════
        #  5. SYSTEM-INFOS
        # ═══════════════════════════
        c = section("Status & Pakete", "📦")
        pkg_frame = tk.Frame(c, bg=BG3); pkg_frame.pack(fill="x", padx=12, pady=8)
        for pkg, ok, install in [
            ("duckduckgo-search",  DDG_OK,  "pip install duckduckgo-search"),
            ("requests",           REQ_OK,  "pip install requests"),
            ("pyperclip",          CLIP_OK, "pip install pyperclip"),
            ("keyboard",           KB_OK,   "pip install keyboard"),
        ]:
            pr = tk.Frame(pkg_frame, bg=BG3); pr.pack(fill="x", pady=2)
            dot = tk.Label(pr, text="●", font=(FN, 10), bg=BG3,
                           fg=GREEN if ok else RED); dot.pack(side="left", padx=(8, 6))
            tk.Label(pr, text=pkg, font=F_MONO_S, bg=BG3,
                     fg=TEXT if ok else TEXT2, width=24, anchor="w").pack(side="left")
            if not ok:
                tk.Label(pr, text=install, font=F_TINY, bg=BG3,
                         fg=AMBER).pack(side="left", padx=8)
            else:
                tk.Label(pr, text="installiert", font=F_TINY,
                         bg=BG3, fg=DIM2).pack(side="left", padx=8)

        # Python-Version
        import sys as _sys
        info_row = tk.Frame(c, bg=BG3); info_row.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(info_row, text=f"Python {_sys.version.split()[0]}   |   Mikrofon: {'✓' if mic_ok else '✗'}",
                 font=F_TINY, bg=BG3, fg=DIM2).pack(side="left", padx=8)

        # ═══════════════════════════
        #  6. GEFÄHRLICHE AKTIONEN
        # ═══════════════════════════
        c = section("Daten", "🗂")
        danger_row = tk.Frame(c, bg=BG3); danger_row.pack(fill="x", padx=12, pady=8)
        tk.Button(danger_row, text="🗑  Verlauf löschen", font=F_SMALL,
                  bg=BG4, fg=TEXT2, relief="flat", cursor="hand2",
                  activebackground=RED, activeforeground=WHITE,
                  command=self._clear_history_confirm
                  ).pack(side="left", padx=(0, 8), ipady=5, ipadx=10)
        tk.Button(danger_row, text="🗑  Notizen löschen", font=F_SMALL,
                  bg=BG4, fg=TEXT2, relief="flat", cursor="hand2",
                  activebackground=RED, activeforeground=WHITE,
                  command=self._clear_notes_confirm
                  ).pack(side="left", padx=4, ipady=5, ipadx=10)
        tk.Button(danger_row, text="↺  Config zurücksetzen", font=F_SMALL,
                  bg=BG4, fg=TEXT2, relief="flat", cursor="hand2",
                  activebackground=RED, activeforeground=WHITE,
                  command=self._reset_settings
                  ).pack(side="left", padx=4, ipady=5, ipadx=10)

        # ═══════════════════════════
        #  6. FARBEN
        # ═══════════════════════════
        c = section("Farben & Theme", "🎨")

        # Theme-Schnellauswahl
        wf = row(c, "Schnell-Theme", "Vordefinierte Farbschemata")
        theme_var = tk.StringVar(value="Eigene Farben")
        theme_cb  = ttk.Combobox(wf, textvariable=theme_var,
                                  values=list(COLOR_THEMES.keys()),
                                  font=F_SMALL, width=28, state="readonly")
        theme_cb.pack(side="left")
        def apply_theme(e=None):
            name = theme_var.get()
            if name in COLOR_THEMES:
                t = COLOR_THEMES[name]
                for key, cvar in self._color_vars.items():
                    if key in t: cvar.set(t[key])
                self._save_colors()   # speichert + wendet live an
        theme_cb.bind("<<ComboboxSelected>>", apply_theme)

        # Einzelne Farben bearbeiten
        self._color_vars: dict = {}
        color_groups = [
            ("Hintergrund",   ["BG0","BG1","BG2","BG3","BG4","BORDER","DIM","DIM2"]),
            ("Akzente",       ["CYAN","CYAN2","AMBER","AMBER2","GREEN","GREEN2","RED","PURPLE","BLUE"]),
            ("Text",          ["TEXT","TEXT2","WHITE"]),
        ]
        for grp_name, keys in color_groups:
            grp = tk.Frame(c, bg=BG3); grp.pack(fill="x", padx=2, pady=(6,0))
            tk.Label(grp, text=f"  {grp_name}", font=F_TINY,
                     bg=BG3, fg=DIM2).pack(anchor="w", padx=8, pady=(4,0))
            grid = tk.Frame(grp, bg=BG3); grid.pack(fill="x", padx=8, pady=(0,6))
            for col_idx, key in enumerate(keys):
                cell = tk.Frame(grid, bg=BG3); cell.grid(row=0, column=col_idx, padx=4, pady=3)
                current = config.get("colors", {}).get(key, _COLOR_DEFAULTS.get(key, "#ffffff"))
                cvar = tk.StringVar(value=current)
                self._color_vars[key] = cvar
                # Farbvorschau-Button
                preview = tk.Label(cell, text="  ", bg=current, width=3,
                                   relief="flat", cursor="hand2",
                                   highlightthickness=2, highlightbackground=BORDER)
                preview.pack()
                tk.Label(cell, text=key, font=(FN,7), bg=BG3, fg=DIM2).pack()

                def _pick(k=key, cv=cvar, pv=preview):
                    from tkinter import colorchooser
                    chosen = colorchooser.askcolor(
                        color=cv.get(),
                        title=f"Farbe wählen: {k}")[1]
                    if chosen:
                        cv.set(chosen)
                        pv.config(bg=chosen, highlightbackground=chosen)
                        self._save_colors()
                preview.bind("<Button-1>", lambda e, fn=_pick: fn())
                # Hover-Effekt
                preview.bind("<Enter>", lambda e, w=preview: w.config(highlightbackground=CYAN))
                preview.bind("<Leave>", lambda e, w=preview, k=key:
                             w.config(highlightbackground=BORDER))

        # Reset-Button
        reset_row = tk.Frame(c, bg=BG3); reset_row.pack(fill="x", padx=12, pady=8)
        tk.Button(reset_row, text="↺  Farben zurücksetzen", font=F_SMALL,
                  bg=BG4, fg=TEXT2, relief="flat", cursor="hand2",
                  activebackground=BG4, activeforeground=RED,
                  command=self._reset_colors).pack(side="left", ipady=4, ipadx=10)
        tk.Label(reset_row, text="Neustart erforderlich um Farben anzuwenden",
                 font=F_TINY, bg=BG3, fg=DIM2).pack(side="left", padx=12)

        # Spacer am Ende
        tk.Frame(f, bg=BG0, height=30).pack()
    def _save_colors(self):
        """Farben speichern UND sofort live auf alle Widgets anwenden."""
        new_colors = {key: var.get() for key, var in self._color_vars.items()}
        config.setdefault("colors", {}).update(new_colors)
        cfg_save(config)
        self._apply_colors_live(new_colors)
        self._set_status("✓ Farben angewendet", GREEN)

    def _reset_colors(self):
        if messagebox.askyesno("Farben zurücksetzen",
                               "Alle Farben auf Standard zurücksetzen?"):
            config.pop("colors", None)
            cfg_save(config)
            for key, var in self._color_vars.items():
                var.set(_COLOR_DEFAULTS.get(key, "#ffffff"))
            self._apply_colors_live(_COLOR_DEFAULTS)
            self._set_status("✓ Farben zurückgesetzt", GREEN)

    def _apply_colors_live(self, colors: dict):
        """Wendet neue Farben sofort auf ALLE Widgets an – kein Neustart nötig."""
        # Globale Farbvariablen aktualisieren
        import sys
        mod = sys.modules[__name__]
        color_map = {
            "BG0":BG0,"BG1":BG1,"BG2":BG2,"BG3":BG3,"BG4":BG4,
            "BORDER":BORDER,"DIM":DIM,"DIM2":DIM2,
            "CYAN":CYAN,"CYAN2":CYAN2,"AMBER":AMBER,"AMBER2":AMBER2,
            "GREEN":GREEN,"GREEN2":GREEN2,"RED":RED,"PURPLE":PURPLE,
            "BLUE":BLUE,"TEXT":TEXT,"TEXT2":TEXT2,"WHITE":WHITE,
        }
        # Neue Werte in globale Variablen schreiben
        for key, val in colors.items():
            if hasattr(mod, key):
                setattr(mod, key, val)

        new_bg0  = colors.get("BG0",  BG0)
        new_bg1  = colors.get("BG1",  BG1)
        new_bg2  = colors.get("BG2",  BG2)
        new_bg3  = colors.get("BG3",  BG3)
        new_bg4  = colors.get("BG4",  BG4)
        new_cyan = colors.get("CYAN", CYAN)
        new_text = colors.get("TEXT", TEXT)
        new_text2= colors.get("TEXT2",TEXT2)
        new_border=colors.get("BORDER",BORDER)
        new_dim2 = colors.get("DIM2", DIM2)
        new_green= colors.get("GREEN",GREEN)
        new_amber= colors.get("AMBER",AMBER)
        new_red  = colors.get("RED",  RED)
        new_white= colors.get("WHITE",WHITE)

        # Mapping: alte Farbe → neue Farbe
        remap = {
            BG0:new_bg0, BG1:new_bg1, BG2:new_bg2, BG3:new_bg3, BG4:new_bg4,
            CYAN:new_cyan, TEXT:new_text, TEXT2:new_text2, BORDER:new_border,
            DIM2:new_dim2, GREEN:new_green, AMBER:new_amber, RED:new_red,
            WHITE:new_white,
        }

        def recolor(widget):
            """Rekursiv alle Widgets neu einfärben."""
            try:
                # bg / background
                try:
                    cur_bg = widget.cget("bg")
                    if cur_bg in remap:
                        widget.config(bg=remap[cur_bg])
                except Exception: pass
                # fg / foreground
                try:
                    cur_fg = widget.cget("fg")
                    if cur_fg in remap:
                        widget.config(fg=remap[cur_fg])
                except Exception: pass
                # highlightbackground
                try:
                    cur_hb = widget.cget("highlightbackground")
                    if cur_hb in remap:
                        widget.config(highlightbackground=remap[cur_hb])
                except Exception: pass
                # insertbackground (Cursor)
                try:
                    cur_ib = widget.cget("insertbackground")
                    if cur_ib in remap:
                        widget.config(insertbackground=remap[cur_ib])
                except Exception: pass
            except Exception: pass
            # Kinder rekursiv
            try:
                for child in widget.winfo_children():
                    recolor(child)
            except Exception: pass

        self.root.config(bg=new_bg0)
        recolor(self.root)

        # Chat-Tags neu setzen
        try:
            cm = self.chat_manager
            if cm and cm._chat:
                cm._chat.config(bg=new_bg1, fg=new_text)
                cm._chat.tag_configure("u_body", background=new_bg2, foreground=new_text)
                cm._chat.tag_configure("j_body", background=new_bg2, foreground=new_text)
                cm._chat.tag_configure("j_name", foreground=new_cyan)
                cm._chat.tag_configure("u_name", foreground=colors.get("BLUE", BLUE))
                cm._chat.tag_configure("sys",    foreground=new_dim2)
                cm._chat.tag_configure("warn",   foreground=new_amber)
        except Exception: pass

        # Orb neu zeichnen
        try:
            if self.chat_manager._orb_canvas:
                self.chat_manager._orb_draw_idle()
        except Exception: pass

        # TTK-Style neu setzen
        try:
            s = ttk.Style()
            s.configure("TNotebook",       background=new_bg1)
            s.configure("TNotebook.Tab",   background=new_bg2, foreground=new_dim2)
            s.map("TNotebook.Tab",
                  background=[("selected",new_bg4),("active",new_bg3)],
                  foreground=[("selected",new_cyan),("active",new_text)])
            s.configure("Treeview",
                        background=new_bg3, foreground=new_text,
                        fieldbackground=new_bg3)
            s.configure("TScrollbar",      background=new_bg3, troughcolor=new_bg1)
            s.configure("TProgressbar",    background=new_cyan, troughcolor=new_bg3)
        except Exception: pass

        self.root.update_idletasks()



    def _save_settings(self):
        updates = {key: var.get() for key, var in self._sv.items()}
        updates["wakeword_enabled"]      = self._wakeword_enabled_var.get()
        updates["speech_input_enabled"]  = self._speech_input_var.get()
        updates["speak_answers"]         = self._speak_var.get()
        updates["tts_rate"]              = self._set_rate.get()
        updates["user_name"]             = self._user_name_var.get().strip().title() or USER_DEFAULT_NAME
        vname = self._set_voice.get()
        for i, v in enumerate(all_voices):
            if v.name == vname:
                updates["voice"] = i; break
        app_state.update_config(updates)
        self._update_mode_text()
        self._set_status("✓ Gespeichert", GREEN)

    def _reset_settings(self):
        if messagebox.askyesno("Config zurücksetzen",
                               "Alle Einstellungen auf Standard zurücksetzen?"):
            CFG_FILE.unlink(missing_ok=True)
            messagebox.showinfo("Neustart erforderlich",
                                "Bitte JARVIS neu starten um die Standardwerte zu laden.")

    def _clear_history_confirm(self):
        if messagebox.askyesno("Verlauf löschen", "Kompletten Verlauf löschen?"):
            app_state.clear_history()
            self._say("system", "🗑 Verlauf gelöscht.")

    def _clear_notes_confirm(self):
        if messagebox.askyesno("Notizen löschen",
                               "Alle Notizen unwiderruflich löschen?"):
            app_state.all_notes.clear()
            notes_save(app_state.all_notes)
            self._say("system", "🗑 Alle Notizen gelöscht.")


    # ── Status & Hintergrund ─────────────
    def _set_status(self, text, color=GREEN):
        self.root.after(0, lambda: (self._status_var.set(text), self._status_dot.config(fg=color)))

    def _get_mode_text(self):
        return (f"Vorlesen: {'AN' if config.get('speak_answers',True) else 'AUS'} | "
                f"Wakeword: {'AN' if config.get('wakeword_enabled',True) else 'AUS'} | "
                f"Spracheingabe: {'AN' if config.get('speech_input_enabled',True) else 'AUS'}")

    def _update_mode_text(self):
        if hasattr(self,"_mode_var"): self._mode_var.set(self._get_mode_text())

    # FIX 5: zentraler Reminder-Watcher – ein Thread für alle
    def _reminder_watcher(self):
        while True:
            now = datetime.datetime.now().strftime("%H:%M")
            for r in app_state.config.get("reminders",[]):
                if not r.get("done") and r.get("time") == now:
                    r["done"] = True
                    cfg_save(config)
                    spreche(f"Erinnerung: {r['text']}")
                    self.root.after(0, lambda tx=r["text"]: messagebox.showinfo("🔔 Erinnerung", tx))
            time.sleep(30)

    def _start_loops(self):
        self._time_loop()
        self._bg_stats_loop()
        self._clip_loop()
        # FIX 5: ein zentraler Reminder-Thread
        threading.Thread(target=self._reminder_watcher, daemon=True).start()
        # FIX 7: Wakeword nur starten wenn mic vorhanden UND wakeword konfiguriert
        if mic_ok and config.get("wakeword"):
            self.wakeword = True
            threading.Thread(target=self._ww_loop, daemon=True).start()

    def _time_loop(self):
        self._time_lbl.config(text=datetime.datetime.now().strftime("  %A  %d. %B %Y    %H:%M:%S"))
        self.root.after(1000, self._time_loop)

    def _bg_stats_loop(self):
        if self.cur_tab=="system": self._sys_refresh()
        else:
            try: i=sysinfo(); self.cpu_hist.append(i["cpu"]); self.ram_hist.append(i["ram"])
            except Exception: pass
        self.root.after(2500, self._bg_stats_loop)

    def _clip_loop(self):
        try:
            if CLIP_OK:
                curr=__import__("pyperclip").paste()
                if curr and (not self.clip_hist or self.clip_hist[-1]!=curr):
                    self.clip_hist.append(curr)
        except Exception: pass
        self.root.after(3000, self._clip_loop)

    def _exit(self):
        cfg_save(config); notes_save(all_notes); hist_save(history)
        self.root.destroy()

    def run(self):
        self._set_status("BEREIT", GREEN)
        self.root.mainloop()


# ══════════════════════════════════════════
if __name__ == "__main__":
    print("Starte J.A.R.V.I.S v5.0 [Fixed]...")
    Jarvis().run()