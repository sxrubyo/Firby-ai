"""
Firby V7.0 — Postprocessor Determinístico
=============================================
Humaniza la respuesta cruda del LLM sin llamar a ningún otro modelo.
Garantías: sin em dash, sin punto final, sin frases relleno, sin emojis.
"""

from __future__ import annotations
import re
import unicodedata
from typing import List


# ── Frases relleno que el LLM colea aunque el prompt las prohíba ──────────────
_STRIP_PHRASES = [
    "con mucho gusto", "encantada de conocerte", "encantado de conocerte",
    "es un placer", "fue un placer", "en qué más le puedo servir",
    "en qué más puedo ayudarte", "estoy aquí para ayudarte",
    "por supuesto,", "definitivamente,", "absolutamente,",
    "claro que sí,", "claro que si,", "con gusto te ayudo",
    "con gusto te cuento", "me alegra que preguntes",
    "perfecto, entiendo,", "te cuento que", "lo que pasa es que",
    "en ese sentido,", "de hecho,", "con todo gusto",
]

# ── Emojis ────────────────────────────────────────────────────────────────────
_EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002500-\U00002BEF"
    "\U00002702-\U000027B0"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FAFF"
    "\u2600-\u26FF"
    "\u2700-\u27BF"
    "]+",
    flags=re.UNICODE,
)


def postprocess(text: str, is_premium: bool = False) -> str:
    """
    Normalización suave para WhatsApp sin filtrar ni mutilar texto del LLM.
    """
    if not text:
        return text

    # Quitar signos invertidos de apertura
    text = text.replace("¿", "").replace("¡", "")

    # Quitar emojis estrictamente
    text = _EMOJI_RE.sub("", text)

    # Quitar formato markdown bold (* y **)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)

    # Normalizar separadores de burbuja (|| o |||)
    text = re.sub(r"\s*\|{2,3}\s*", " ||| ", text)

    # Normalizar espacios
    text = re.sub(r"[ \t]+", " ", text).strip()

    return text


def _per_bubble(s: str, is_premium: bool) -> str:
    s = s.strip()
    if not s:
        return s

    # Quitar residuo de pipes
    s = re.sub(r"^[\|\s]+|[\|\s]+$", "", s).strip()

    # Quitar punto final
    if s.endswith(".") and not s.endswith("..."):
        s = s[:-1].strip()

    # Quitar guión al inicio/fin (residuo post em-dash)
    s = re.sub(r"^\s*-\s+", "", s)
    s = re.sub(r"\s+-\s*$", "", s)
    s = s.strip()

    # Truncar si supera 125 chars (burbuja demasiado larga)
    if len(s) > 125:
        cut = max(s.rfind(". ", 0, 125), s.rfind(", ", 0, 125), s.rfind(" y ", 0, 125))
        if cut > 40:
            s = s[:cut].strip().rstrip(",").rstrip(".")

    # Mayúscula inicial solo para premium, minúscula para el resto
    if s:
        if is_premium:
            s = s[0].upper() + s[1:]
        else:
            first_word = s.split()[0] if s.split() else ""
            is_acronym = (len(first_word) <= 5
                          and first_word == first_word.upper()
                          and len(first_word) > 1)
            if not is_acronym:
                s = s[0].lower() + s[1:]

    return s


def split_bubbles(text: str, max_bubbles: int = 3) -> List[str]:
    """Divide el texto en burbujas y elimina residuos de pipes."""
    if not text:
        return []
    
    # Normalizar || o |||
    text = re.sub(r"\s*\|{2,3}\s*", " ||| ", text)
    
    if "|||" in text:
        parts = [b.strip() for b in text.split("|||") if b.strip()]
    elif "\n" in text:
        parts = [b.strip() for b in re.split(r"\n+", text) if b.strip()]
    else:
        parts = [text.strip()] if text.strip() else []
        
    cleaned = []
    for p in parts:
        p = re.sub(r"^[\|\s]+|[\|\s]+$", "", p).strip()
        p = re.sub(r"\s+\|+\s+", " ", p).strip()
        if p and len(p) > 1:
            cleaned.append(p)
            
    return cleaned[:max_bubbles]
