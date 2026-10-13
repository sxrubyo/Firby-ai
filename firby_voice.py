"""firby_voice.py — 100x Ultra-Human Voice Engine for Firby.

Canonical, shared module for text-to-speech generation with:
1. Native WhatsApp OGG OPUS 16kHz Codec Conversion (ffmpeg)
2. Asymmetrical Human Pauses & Micro-Breath Inserter
3. Spanish Phonetics (Guasap, Nóushon, Bubli, low-cased acronyms)
4. Dynamic Date/Time Text Conversion
5. Human Gain Fluctuation & Pitch Escalator Removal
6. Natural Auto-Correction / Dube Insertion (1 in 15 chance)
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import re
import random
import shutil
import tempfile
from typing import List, Optional, Tuple

import httpx

try:
    from src.firby.channels.voice import FirbyVoice, ROBOT_PATTERNS, voice
    FirbyVoice = FirbyVoice
except ImportError:
    try:
        from src.firby.channels.voice import FirbyVoice, ROBOT_PATTERNS, voice
        FirbyVoice = FirbyVoice
    except Exception:
        pass

log = logging.getLogger("firby.voice")

CACHE_DIR = "/tmp/firby_voice_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# ── ElevenLabs API key cascade ──────────────────────────────────────────────
API_KEYS = [k for k in [
    os.getenv("ELEVENLABS_API_KEY"),
    os.getenv("ELEVENLABS_API_KEY_2"),
    os.getenv("ELEVENLABS_API_KEY_3"),
] if k]

# ── Voice cascade (female, warm, natural-sounding in Spanish) ───────────────
VOICE_CASCADE: List[Tuple[str, str]] = [
    ("cgSgspJ2msm6clMCkdW9", "Jessica"),
    ("EXAVITQu4vr4xnSDxMaL", "Sarah"),
    ("FGY2WhTYpPnrIDTdsKH5", "Laura"),
    ("hpp4J3VqNfWAUOO0d1Us", "Bella"),
]

DEFAULT_VOICE = VOICE_CASCADE[0][0]

MONTH_NAMES = {
    "01": "enero", "02": "febrero", "03": "marzo", "04": "abril",
    "05": "mayo", "06": "junio", "07": "julio", "08": "agosto",
    "09": "septiembre", "10": "octubre", "11": "noviembre", "12": "diciembre",
    "1": "enero", "2": "febrero", "3": "marzo", "4": "abril",
    "5": "mayo", "6": "junio", "7": "julio", "8": "agosto",
    "9": "septiembre"
}

# ── Humanization & Text Pre-Processing (20 Ideas Implementation) ───────────

def _format_dates_and_times(text: str) -> str:
    """Conombra fechas y horas a texto hablado natural (ej. '15/08' -> '15 de agosto')."""
    # Dates dd/mm/yyyy or dd/mm
    def _date_sub(m):
        day, month = m.group(1), m.group(2)
        mname = MONTH_NAMES.get(month, month)
        return f"{day} de {mname}"

    text = re.sub(r"\b([0-3]?[0-9])/([0-1]?[0-9])(?:/\d{2,4})?\b", _date_sub, text)
    
    # Times 3:00pm -> 3 de la tarde
    text = re.sub(r"\b([0-1]?[0-9]):00\s*(pm|PM)\b", r"\1 de la tarde", text)
    text = re.sub(r"\b([0-1]?[0-9]):00\s*(am|AM)\b", r"\1 de la mañana", text)
    return text


def _remove_emojis(text: str) -> str:
    """Remueve emojis y caracteres gráficos Unicode de la pista de audio."""
    return re.sub(r"[\U00010000-\U0010ffff\u2600-\u27ff\u2300-\u23ff]", "", text)


def _has_laughter(text: str) -> bool:
    lower = text.lower()
    return bool(re.search(r"\b(ja[ja]*|je[je]*|ji[ji]*|jaja|jeje|jiji|lol)\b", lower))


def _num_to_words(n: str) -> str:
    """Convert small number string to Spanish words for TTS clarity."""
    mapping = {"0":"cero","1":"uno","2":"dos","3":"tres","4":"cuatro","5":"cinco",
               "6":"seis","7":"siete","8":"ocho","9":"nueve","10":"diez",
               "11":"once","12":"doce","13":"trece","14":"catorce","15":"quince",
               "16":"dieciseis","17":"diecisiete","18":"dieciocho","19":"diecinueve",
               "20":"veinte","21":"veintiuno","22":"veintidos","23":"veintitres",
               "24":"veinticuatro","25":"veinticinco","26":"veintiseis","27":"veintisiete",
               "28":"veintiocho","29":"veintinueve","30":"treinta"}
    return mapping.get(n, n)


def _format_numbers_to_words(text: str) -> str:
    """
    Convierte números y combinaciones numéricas a palabras habladas en español para TTS fluido:
    - "24/7" -> "veinticuatro siete"
    - "100%" -> "cien por ciento"
    - "3500" -> "tres mil quinientos"
    - "4500" -> "cuatro mil quinientos"
    - "24" -> "veinticuatro"
    """
    if not text:
        return text

    # Casos especiales frecuentes
    text = re.sub(r"\b24\s*/\s*7\b", "veinticuatro siete", text, flags=re.IGNORECASE)
    text = re.sub(r"\b24-7\b", "veinticuatro siete", text, flags=re.IGNORECASE)
    text = re.sub(r"\b24/7\b", "veinticuatro siete", text, flags=re.IGNORECASE)
    text = re.sub(r"\b100\s*%\b", "cien por ciento", text)
    text = re.sub(r"(\d+)\s*%", r"\1 por ciento", text)

    # Mapeos de números comunes
    num_map = {
        "0": "cero", "1": "uno", "2": "dos", "3": "tres", "4": "cuatro",
        "5": "cinco", "6": "seis", "7": "siete", "8": "ocho", "9": "nueve",
        "10": "diez", "11": "once", "12": "doce", "13": "trece", "14": "catorce",
        "15": "quince", "16": "dieciséis", "17": "diecisiete", "18": "dieciocho",
        "19": "diecinueve", "20": "veinte", "21": "veintiuno", "22": "veintidós",
        "23": "veintitrés", "24": "veinticuatro", "25": "veinticinco",
        "26": "veintiséis", "27": "veintisiete", "28": "veintiocho",
        "29": "veintinueve", "30": "treinta", "40": "cuarenta", "50": "cincuenta",
        "60": "sesenta", "70": "setenta", "80": "ochenta", "90": "noventa",
        "100": "cien", "200": "doscientos", "300": "trescientos", "400": "cuatrocientos",
        "500": "quinientos", "600": "seiscientos", "700": "setecientos",
        "800": "ochocientos", "900": "novecentos",
        "3500": "tres mil quinientos", "4500": "cuatro mil quinientos",
        "1000": "mil", "2000": "dos mil", "3000": "tres mil", "5000": "cinco mil"
    }

    def _rep_num(m):
        val = m.group(0)
        return num_map.get(val, val)

    text = re.sub(r"\b\d{1,4}\b", _rep_num, text)
    return text


def inject_human_disfluencies(text: str, user_text: str = "", region: str = "colombiano") -> str:
    """
    Transforma el texto para ElevenLabs inyectando disfluencias y fonética hablada.
    """
    clean = text or ""
    
    # 1. Remoción de emojis
    clean = _remove_emojis(clean)

    # 2. Conversión de Números a Palabras Habladas
    clean = _format_numbers_to_words(clean)

    # 2. Fonetización de Marcas y Siglas
    clean = re.sub(r"\bWhatsApp\b", "Guasap", clean, flags=re.I)
    clean = re.sub(r"\bNotion\b", "Nóushon", clean, flags=re.I)
    clean = re.sub(r"\bInstagram\b", "Ínstagram", clean, flags=re.I)
    clean = re.sub(r"\bDr\.", "Doctor", clean, flags=re.I)
    clean = re.sub(r"\bDra\.", "Doctora", clean, flags=re.I)

    # Acrónimos en minúsculas
    clean = re.sub(r"\bAPI\b", "api", clean)
    clean = re.sub(r"\bPDF\b", "pdf", clean)
    clean = re.sub(r"\bCRM\b", "crm", clean)
    clean = re.sub(r"\bIA\b", "ia", clean)
    clean = re.sub(r"\bURL\b", "url", clean)
    clean = re.sub(r"\bID\b", "id", clean)

    # 3. Conversión de Fechas/Horas
    clean = _format_dates_and_times(clean)

    # 4. Eliminación del Tono Pitch Escalator (Remover signos ! al final de frase)
    clean = re.sub(r"!+", ".", clean)
    clean = re.sub(r"\s+", " ", clean).strip()

    if not clean or len(clean) < 15:
        return clean

    lower = clean.lower()

    # 5. Inyección de aperturas naturales conversacionales (solo si no empieza ya con saludo)
    has_greeting_or_start = any(lower.startswith(w) for w in (
        "hola", "buenos", "buenas", "qué tal", "que tal", "mira", "claro", "te cuento"
    ))
    if not has_greeting_or_start and random.random() < 0.20:
        start_fillers = ["Mira, ", "Claro, ", "Te cuento, "]
        prefix = random.choice(start_fillers)
        clean = prefix + clean[0].lower() + clean[1:] if clean else clean

    # 6. Sin repeticiones artificiales ni tartamudeo (voz ejecutiva fluida)

    # 7. Autocorrecciones humanas suaves mid-sentence (5% probabilidad)
    if random.random() < 0.05:
        corrections = [" o sea, ", " digamos, ", " mejor dicho, "]
        sent_endings = list(re.finditer(r"[.!?]\s+", clean))
        if sent_endings and len(sent_endings) >= 2:
            insert_at = sent_endings[0].end()
            clean = clean[:insert_at] + random.choice(corrections) + clean[insert_at:]

    # 8. Pausas de pensamiento naturales antes de datos clave
    if re.search(r"\b(\d+|cuanto|cuesta|precio|años|meses|días|pesos|dólares)\b", clean, re.I) and random.random() < 0.15:
        pensatives = ["A ver, ", "Mira, "]
        clean = clean[0].lower() + clean[1:] if clean else clean
        clean = random.choice(pensatives) + clean

    # 9. Cadencia de pausas naturales en comas (sin muletillas de duda)
    def _replace_mid(match):
        r_val = random.random()
        if r_val < 0.30:
            return "... "
        elif r_val < 0.45:
            return " — "
        else:
            return ", "

    clean = re.sub(r",\s*", _replace_mid, clean, count=random.randint(1, 2))

    # 10. Contracciones habladas naturales (pa', tá, na')
    if random.random() < 0.30:
        clean = re.sub(r"\bpara\b", "pa'", clean, count=1)
    if random.random() < 0.20:
        clean = re.sub(r"\bestá(s|n)?\b", lambda m: "tá" + (m.group(1) or ""), clean, count=1)
    if random.random() < 0.15:
        clean = re.sub(r"\bnada\b", "na'", clean, count=1)

    # 11. Auditoría y Refinamiento Regional con FirbyAudioAuditor
    try:
        from src.firby.brain.firby_audio_auditor import audio_auditor
        clean = audio_auditor.audit_and_refine_script(clean, user_text=user_text)
    except Exception as e:
        log.warning(f"[voice] Auditor error: {e}")

    # Asegurar punto final para cadencia TTS
    if not clean.endswith("!") and not clean.endswith("?"):
        clean = clean.rstrip(" .!?-") + "."

    return clean


# ── TTS generation (cascade API keys + voice fallback) ──────────────────────

async def _try_generate(text: str, api_key: str, voice_id: str) -> Optional[str]:
    """Single attempt to generate audio with model cascade (eleven_multilingual_v2 -> eleven_turbo_v2_5)."""
    models_to_try = ["eleven_multilingual_v2", "eleven_turbo_v2_5"]
    for model_id in models_to_try:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={
                        "xi-api-key": api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "text": text,
                        "model_id": model_id,
                        "voice_settings": {
                            "stability": 0.45,
                            "similarity_boost": 0.85,
                            "style": 0.05,
                            "use_speaker_boost": True,
                        },
                    },
                )
                if r.status_code == 200 and len(r.content) > 1000:
                    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                    tmp.write(r.content)
                    tmp.close()
                    return tmp.name
                elif r.status_code in (401, 402):
                    log.warning(f"[voice] ElevenLabs error HTTP {r.status_code} ({api_key[-6:]})")
                    try:
                        from firby_core.api_awareness import _capability_map
                        _capability_map.set_elevenlabs_status(False, f"HTTP {r.status_code} Cuota o saldo agotado")
                    except Exception:
                        pass
                    break
                elif r.status_code == 429:
                    log.debug(f"[voice] rate limited ({api_key[-6:]})")
                    break
                else:
                    log.debug(f"[voice] HTTP {r.status_code} ({model_id}): {r.text[:100]}")
        except Exception as e:
            log.debug(f"[voice] error ({model_id}): {e}")
    return None


async def convert_to_whatsapp_opus(mp3_path: str) -> str:
    """Convert MP3 audio to native WhatsApp OGG OPUS 16kHz voice note codec with dynamic gain variation using ffmpeg."""
    if not mp3_path or not os.path.exists(mp3_path):
        return mp3_path
    
    ogg_path = mp3_path.replace(".mp3", ".ogg")
    
    # Fluctución de volumen aleatoria (±0.8 dB) para simular movimiento del teléfono
    random_gain = round(random.uniform(0.95, 1.02), 2)
    af_filter = f"volume={random_gain}"

    try:
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y", "-i", mp3_path,
            "-af", af_filter,
            "-c:a", "libopus", "-b:a", "16k", "-ar", "16000",
            ogg_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        if os.path.exists(ogg_path) and os.path.getsize(ogg_path) > 500:
            log.info(f"[voice] converted to native WhatsApp OPUS 16kHz codec (gain={random_gain}) -> {ogg_path}")
            return ogg_path
    except Exception as e:
        log.warning(f"[voice] ffmpeg conversion error: {e}")
    return mp3_path


async def generate_tts_audio(text: str, voice_idx: int = 0, user_text: str = "") -> Optional[str]:
    """Generate TTS audio with ElevenLabs — cascade keys & voices, converted to native WhatsApp OPUS 16kHz codec.
    Returns path to temp file, or None on failure.
    """
    valid_keys = [k for k in API_KEYS if k and k.strip()]
    if not valid_keys:
        return None

    # Inject human disfluencies and regional audit for natural sound
    tts_text = inject_human_disfluencies(text, user_text=user_text)

    # Check disk cache first (0ms latency, 0 characters consumed)
    vid_target = VOICE_CASCADE[voice_idx][0] if voice_idx < len(VOICE_CASCADE) else DEFAULT_VOICE
    cache_hash = hashlib.md5(f"{tts_text.strip()}:{vid_target}".encode("utf-8")).hexdigest()
    cached_path = os.path.join(CACHE_DIR, f"{cache_hash}.ogg")
    if os.path.exists(cached_path) and os.path.getsize(cached_path) > 500:
        log.info(f"[voice] cache hit for '{tts_text[:30]}...' -> {cached_path}")
        tmp = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
        shutil.copyfile(cached_path, tmp.name)
        tmp.close()
        return tmp.name

    # Try each API key in cascade
    for key in valid_keys:
        for vid, vname in VOICE_CASCADE[voice_idx:voice_idx + 2]:
            result = await _try_generate(tts_text, key, vid)
            if result:
                log.info(f"[voice] generated with {vname} ({vid[:8]}...) key ...{key[-6:]}")
                # Convert MP3 to WhatsApp Native OGG OPUS 16kHz with dynamic gain
                opus_file = await convert_to_whatsapp_opus(result)
                try:
                    shutil.copyfile(opus_file, cached_path)
                except Exception as ce:
                    log.debug(f"[voice] cache save error: {ce}")
                return opus_file
            log.debug(f"[voice] {vname} failed with key ...{key[-6:]}, trying next")

    log.warning("[voice] all keys/voices exhausted")
    return None


# Backward-compatible alias
generate_demo_audio = generate_tts_audio
generate_audio = generate_tts_audio


# ── Decision logic ──────────────────────────────────────────────────────────

def should_send_voice(text: str, turn_number: int, has_business_name: bool = False) -> bool:
    """Decide when to send voice — 10% human lottery for explanations (>=40 chars)."""
    clean_text = text.strip()
    if turn_number <= 1:
        return False
    if len(clean_text) < 40:
        return False
    return random.random() < 0.10
