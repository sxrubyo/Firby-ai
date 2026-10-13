"""firby_demo_voice.py — Voice cascade with ElevenLabs for demo mode."""
from __future__ import annotations

import asyncio
import logging
import os
import random
import re
import tempfile
from typing import List, Optional, Tuple

import httpx

import hashlib
import shutil

from firby_mirroring import get_muletillas, DEFAULT_REGION, profile_cache, SocialProfile

log = logging.getLogger("firby.demo_voice")

CACHE_DIR = "/tmp/firby_voice_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Cascade of ElevenLabs API keys — try key1 → key2 → key3
FFMPEG_WARMTH = True  # post-processing for audio warmth

API_KEYS = [k for k in [
    os.getenv("ELEVENLABS_API_KEY"),
    os.getenv("ELEVENLABS_API_KEY_2"),
    os.getenv("ELEVENLABS_API_KEY_3"),
] if k]

# Female voices ranked by how natural/warm they sound in Spanish
VOICE_CASCADE: List[Tuple[str, str]] = [
    ("cgSgspJ2msm6clMCkdW9", "Jessica"),   # Playful, Bright, Warm — young (best for Colombian)
    ("EXAVITQu4vr4xnSDxMaL", "Sarah"),     # Mature, Confident — young (backup)
    ("FGY2WhTYpPnrIDTdsKH5", "Laura"),      # Enthusiast, quirky — young (energetic)
    ("hpp4J3VqNfWAUOO0d1Us", "Bella"),      # Professional, Warm — middle_aged (formal fallback)
]

DEFAULT_VOICE = VOICE_CASCADE[0][0]

# Muletillas obtenidas dinamicamente de firby_mirroring segun perfil regional
# Fallback: colombiano (default para Latam)


_HAS_LAUGHTER_CACHE = {}


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

def inject_human_disfluencies(text: str, region: str = DEFAULT_REGION, user_text: str = "") -> str:
    """Transform text for ElevenLabs TTS by injecting natural filler words,
    breath pauses, micro-hesitations, repetitions, self-corrections, and audio tags (v4).
    Supports Spanish ('ehh...', 'mira...', 'pues...') and English ('well...', 'uh...').
    This does NOT alter the text sent in WhatsApp chat — only the audio track.
    """
    clean = text or ""

    # Normalize numbers/symbols for better TTS pronunciation
    clean = re.sub(r"\b24\s*/\s*7\b", "veinticuatro siete", clean, flags=re.I)
    clean = re.sub(r"\b24-7\b", "veinticuatro siete", clean, flags=re.I)
    clean = re.sub(r"\b24/7\b", "veinticuatro siete", clean, flags=re.I)
    clean = re.sub(r"(\d+)/(\d+)", lambda m: _num_to_words(m.group(1)) + "/" + m.group(2) if m.group(1).isdecimal() and len(m.group(1)) <= 2 else m.group(0), clean)
    clean = re.sub(r"(\d+)%", lambda m: _num_to_words(m.group(1)) + " por ciento" if m.group(1).isdecimal() and len(m.group(1)) <= 2 else m.group(0), clean)

    # Phonetic fix for ElevenLabs: "Firby"/"Boobly" -> "Bubli"
    clean = re.sub(r"\bFirby\b", "Bubli", clean, flags=re.I)
    clean = re.sub(r"\bBoobly\b", "Bubli", clean, flags=re.I)

    # Strip Tip: prefixes so TTS doesn't read them literally
    clean = re.sub(r"(^|[.!?]\s+)(\*\*)?(\U0001f4a1\s*)?Tip:\s*", r"\1", clean, flags=re.I).strip()
    if clean and not clean[0].isupper():
        clean = clean[0].upper() + clean[1:] if len(clean) > 1 else clean

    # Purge any meta promises, demo script leftovers, and generic AI intro phrases
    meta_patterns = [
        r"en un segundito te mando un audio[^.!?]*",
        r"en un segundito te envio un audio[^.!?]*",
        r"te mando un audio contandote[^.!?]*",
        r"ya te envio el audio[^.!?]*",
        r"para que el audio sea mas personalizado[^.!?]*",
        r"cual es el nombre de tu negocio[^.!?]*",
        r"cuál es el nombre de tu negocio[^.!?]*",
        r"soy boobly[^.!?]*",
        r"soy firby,?\s*o sea,?\s*la ia recepcionista[^.!?]*",
        r"ia recepcionista 24/7[^.!?]*",
    ]
    for mp in meta_patterns:
        clean = re.sub(mp, "", clean, flags=re.I)
    clean = re.sub(r"\s+", " ", clean).strip()

    if not clean or len(clean) < 15:
        return clean

    lower = clean.lower()

    # Detect English response text
    is_english = any(w in lower for w in ("of course", "sure", "i can", "business", "client", "clients", "hello", "the ", "with ")) and not any(w in lower for w in ("hola", "claro", "que ", "para ", "como ", "con "))

    if is_english:
        if any(lower.startswith(h) for h in ("well", "uh", "um", "like", "sure,")):
            return clean
        openings = ["Well... ", "Uh... ", "Sure... ", "Like... ", "Well, sure... "]
        prefix = random.choice(openings) if random.random() < 0.70 else ""

        def _replace_pause_en(match):
            r_val = random.random()
            if r_val < 0.20:
                return "... like, "
            elif r_val < 0.40:
                return "... uh, "
            elif r_val < 0.55:
                return "... you know, "
            elif r_val < 0.70:
                return " --- "
            else:
                return "... "
        processed = re.sub(r",\s*", _replace_pause_en, clean, count=2)
        result = prefix + processed
        return result

    # --- Spanish / regional ---
    # Executive fluid Spanish — NO excessive 'ehh' and NO stuttering
    mid_fillers = [m for m in mid_fillers if "ehh" not in m] or ["... ", ", "]

    # If already starts with a filler, don't add another
    if not any(lower.startswith(fw.rstrip("... ").lower()) for fw in start_fillers):
        if random.random() < 0.20:
            prefix = random.choice(start_fillers)
            clean = prefix + clean[0].lower() + clean[1:] if clean else clean

    # Sin repeticiones artificiales ni tartamudeo (voz ejecutiva y natural)

    # --- Self-corrections mid-sentence ---
    if random.random() < 0.10:
        corrections = [
            " bueno, mejor dicho, ",
            " o sea, ",
            " digamos, ",
            " mejor dicho, ",
        ]
        sent_endings = re.finditer(r"[.!?]\s+", clean)
        positions = [m.end() for m in sent_endings]
        if positions and len(positions) >= 2:
            insert_at = positions[0]
            clean = clean[:insert_at] + random.choice(corrections) + clean[insert_at:]

    # --- Pensative pause before factual answers ---
    if re.search(r"\b(\d+|cuanto|cuesta|precio|años|meses|días|pesos|dólares)\b", clean, re.I) and random.random() < 0.25:
        pensatives = ["Déjame pensar... ", "Déjame ver... ", "A ver... "]
        clean = clean[0].lower() + clean[1:] if clean else clean
        clean = random.choice(pensatives) + clean

    # Replace some commas with thinking/mid-sentence fillers
    def _replace_mid(match):
        r_val = random.random()
        if r_val < 0.38:
            return random.choice(mid_fillers)
        elif r_val < 0.50:
            return " --- "
        elif r_val < 0.65:
            return "... "
        else:
            return ", "


    clean = re.sub(r",\s*", _replace_mid, clean, count=random.randint(2, 4))

    # --- Contractions for casual spoken Spanish ---
    if random.random() < 0.30:
        clean = re.sub(r"\bpara\b", "pa'", clean, count=1)
    if random.random() < 0.20:
        clean = re.sub(r"\bestá(s|n)?\b", lambda m: "tá" + (m.group(1) or ""), clean, count=1)
    if random.random() < 0.15:
        clean = re.sub(r"\bnada\b", "na'", clean, count=1)

    # Inject [laughs] audio tag if text has laughter
    if _has_laughter(clean) and random.random() < 0.20:
        sentences = re.split(r"(?<=[.!?])\s+", clean)
        for i, sent in enumerate(sentences):
            if re.search(r"\b(ja[ja]*|je[je]*|ji[ji]*|jaja|jeje|jiji|lol)\b", sent, re.I):
                sentences[i] = sent.rstrip(".!?") + " [laughs]."
                break
        clean = " ".join(sentences)

    # Ensure final period so TTS cadence sounds complete — preserve ? and !
    if not clean.endswith("!") and not clean.endswith("?"):
        clean = clean.rstrip(" .!?-") + "."

    return clean

def _post_process_audio(input_path: str) -> Optional[str]:
    """Apply FFmpeg post-processing for audio warmth: compression + EQ + light reverb.
    Returns path to processed file, or original path on failure."""
    import subprocess
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-af",
        "compression=threshold=0.2:ratio=3:makeup=4, "
        "equalizer=f=200:t=q:w=1:g=2,"
        "equalizer=f=3000:t=q:w=1:g=1.5,"
        "equalizer=f=8000:t=q:w=1:g=-1,"
        "aecho=0.8:0.7:20:0.25",
        "-b:a", "128k",
        tmp.name,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if r.returncode == 0 and os.path.getsize(tmp.name) > 1000:
            log.info(f"[demo_voice] post-processed audio: {input_path} -> {tmp.name}")
            return tmp.name
        log.debug(f"[demo_voice] post-process failed: {r.stderr[:200]}")
    except Exception as e:
        log.debug(f"[demo_voice] post-process exception: {e}")
    os.unlink(tmp.name)
    return input_path


async def generate_demo_audio(text: str, voice_idx: int = 0, region: str = DEFAULT_REGION) -> Optional[str]:
    """Generate audio with cascade & cache: try key1 -- key2, voice1 -- voice2."""

    valid_keys = [k for k in API_KEYS if k and k.strip()]
    if not valid_keys:
        return None

    # Inject natural Spanish fillers & breath pauses into the TTS track
    tts_text = inject_human_disfluencies(text, region)

    # Check disk cache first (0ms latency, 0 characters consumed)
    vid_target = VOICE_CASCADE[voice_idx][0] if voice_idx < len(VOICE_CASCADE) else DEFAULT_VOICE
    cache_hash = hashlib.md5(f"{tts_text.strip()}:{vid_target}".encode("utf-8")).hexdigest()
    cached_path = os.path.join(CACHE_DIR, f"{cache_hash}.mp3")
    if os.path.exists(cached_path) and os.path.getsize(cached_path) > 1000:
        log.info(f"[demo_voice] cache hit for '{tts_text[:30]}...' -> {cached_path}")
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        shutil.copyfile(cached_path, tmp.name)
        tmp.close()
        return tmp.name

    # Try each API key in cascade
    for key in valid_keys:
        for vid, vname in VOICE_CASCADE[voice_idx:voice_idx + 2]:
            result = await _try_generate(tts_text, key, vid)
            if result:
                log.info(f"[demo_voice] generated with {vname} ({vid[:8]}...) key ...{key[-6:]}")
                try:
                    shutil.copyfile(result, cached_path)
                except Exception as ce:
                    log.debug(f"[demo_voice] cache save error: {ce}")
                if FFMPEG_WARMTH:
                    processed = _post_process_audio(result)
                    if processed != result:
                        result = processed
                return result
            log.debug(f"[demo_voice] {vname} failed with key ...{key[-6:]}, trying next")

    # Fallback 100% Gratuito: Edge-TTS (Microsoft Neural)
    edge_res = await _try_generate_edge_tts(tts_text, region)
    if edge_res:
        log.info(f"[demo_voice] generated with Edge-TTS free fallback")
        return edge_res

    log.warning("[demo_voice] all keys/voices exhausted")
    return None

async def _try_generate_edge_tts(text: str, region: str = "colombia") -> Optional[str]:
    """Generación de voz gratuita vía Edge-TTS (sin API keys ni límites de tokens)."""
    try:
        import edge_tts
        voice_map = {
            "colombia": "es-CO-SalomeNeural",
            "mexico": "es-MX-DaliaNeural",
            "argentina": "es-AR-ElenaNeural",
            "espana": "es-ES-ElviraNeural",
        }
        chosen_voice = voice_map.get(region.lower(), "es-CO-SalomeNeural")
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp_path = tmp.name
        tmp.close()
        
        clean_text = re.sub(r"\[.*?\]", "", text).strip()
        communicate = edge_tts.Communicate(clean_text, chosen_voice, rate="+3%")
        await communicate.save(tmp_path)
        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 1000:
            log.info(f"[demo_voice] Edge-TTS generado exitosamente ({chosen_voice})")
            return tmp_path
    except Exception as e:
        log.warning(f"[demo_voice] Edge-TTS fallback error: {e}")
    return None


async def _try_generate(text: str, api_key: str, voice_id: str) -> Optional[str]:
    """Single attempt to generate audio with model cascade: multilingual_v2 -> v3 -> flash."""
    models_to_try = ["eleven_multilingual_v2", "eleven_v3", "eleven_flash_v2_5"]
    for model_id in models_to_try:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                payload = {
                    "text": text,
                    "model_id": model_id,
                    "voice_settings": {
                        "stability": 0.20,
                        "similarity_boost": 0.70,
                        "style": 0.55,
                        "use_speaker_boost": True,
                    },
                }
                # v3 has different optimal settings for expressiveness
                if model_id == "eleven_v3":
                    payload["voice_settings"] = {
                        "stability": 0.25,
                        "similarity_boost": 0.70,
                        "style": 0.55,
                        "use_speaker_boost": True,
                    }
                r = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={
                        "xi-api-key": api_key,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                if r.status_code == 200 and len(r.content) > 1000:
                    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                    tmp.write(r.content)
                    tmp.close()
                    return tmp.name
                elif r.status_code in (401, 402):
                    log.warning(f"[demo_voice] key unauthorized/payment required HTTP {r.status_code} ({api_key[-6:]})")
                    try:
                        from firby_core.api_awareness import _capability_map
                        _capability_map.set_elevenlabs_status(False, f"HTTP {r.status_code} Cuota o saldo agotado")
                    except Exception:
                        pass
                    break  # Key invalid or out of quota
                elif r.status_code == 429:
                    log.debug(f"[demo_voice] rate limited ({api_key[-6:]})")
                    break  # Key rate limited, try next key
                else:
                    log.debug(f"[demo_voice] HTTP {r.status_code} ({model_id}): {r.text[:100]}")
        except Exception as e:
            log.debug(f"[demo_voice] error ({model_id}): {e}")
    return None


def should_send_voice_in_demo(text: str, turn_number: int, has_business_name: bool) -> bool:
    """Decide when to send voice in demo --- 10% human lottery for long explanations (>=40 chars) after initial greeting."""
    import random
    clean_text = text.strip()
    # Saludos iniciales / primeros turnos: SOLO TEXTO
    if turn_number <= 1:
        return False
    if len(clean_text) < 40:
        return False
    # Para el resto de la conversacion, enviar audio ~10% de las veces como un humano real
    return random.random() < 0.10


# Conversion hooks for demo closing
DEMO_CLOSING_TRIGGERS = [
    "como activo", "como activo", "como lo contrato", "como contrato",
    "cuanto cuesta", "cuanto cuesta", "precio", "planes",
    "me interesa", "lo quiero", "activar", "contratar",
]


def detect_buying_intent(text: str) -> bool:
    """Detect if prospect wants to buy."""
    return any(t in text.lower() for t in DEMO_CLOSING_TRIGGERS)


def get_closing_response() -> str:
    """When prospect wants to buy, close with Santiago's contact."""
    return (
        "me alegra que te haya gustado la demo! |||"
        " para activarlo en tu negocio, Santiago te explica todo: 3124348669 |||"
        " la activacion es rapida, en menos de 5 minutos ya estoy respondiendo tu WhatsApp"
    )

generate_audio = generate_demo_audio  # alias
