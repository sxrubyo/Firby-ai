# -*- coding: utf-8 -*-
"""
Firby Audio Auditor & Script Refiner (V10 Ultra-Human Voice Engine)

Audita y refina guiones de audio antes de la síntesis TTS.
Evalúa la naturalidad del texto, adapta las muletillas al acento regional
solicitado (Argentino, Paisa, Mexicano, Español) y elimina cualquier rigidez sintética.
"""

from __future__ import annotations
import re
import random
import logging
from typing import Dict, Any, Tuple

log = logging.getLogger("firby.audio_auditor")

REGIONAL_FILLER_MAP = {
    "argentino": {
        "openings": ["Che, mirá... ", "Ah, mirá... ", "Viste que... ", "Che, te cuento... "],
        "pauses": ["... viste, ", "... che, ", " — "],
        "replacements": {"tu": "tu", "tienes": "tenés", "quieres": "querés", "puedes": "podés", "mira": "mirá"}
    },
    "paisa": {
        "openings": ["Vea, pues... ", "Ah, claro... ", "Hola, te cuento... "],
        "pauses": ["... pues, ", "... ", " — "],
        "replacements": {}
    },
    "mexicano": {
        "openings": ["Oye... ", "Ah, miren... ", "Claro que sí... "],
        "pauses": ["... osea, ", "... este, ", " — "],
        "replacements": {}
    },
    "general": {
        "openings": ["Ah, claro... ", "Mira... ", "Te cuento... "],
        "pauses": ["... ", ", ", " — "],
        "replacements": {}
    }
}


class FirbyAudioAuditor:
    """Auditor y refinador inteligente de guiones de notas de voz."""

    def detect_region_context(self, user_text: str, assistant_text: str) -> str:
        """Detecta la región o acento solicitado en el contexto de la conversación."""
        combined = f"{user_text} {assistant_text}".lower()
        if any(w in combined for w in ("argentino", "che", "tenés", "querés", "viste", "boludo", "buenos aires")):
            return "argentino"
        if any(w in combined for w in ("paisa", "medellín", "medellin", "parce", "vea pues")):
            return "paisa"
        if any(w in combined for w in ("mexicano", "wey", "padre", "órale", "mexico")):
            return "mexicano"
        return "general"

    def audit_and_refine_script(self, text: str, user_text: str = "") -> str:
        """
        Audita el texto generado y lo refina para que las muletillas y la cadencia
        suenen 100% naturales según el contexto regional y emocional.
        """
        if not text or len(text.strip()) < 10:
            return text

        region = self.detect_region_context(user_text, text)
        profile = REGIONAL_FILLER_MAP.get(region, REGIONAL_FILLER_MAP["general"])
        
        clean = text.strip()

        # 1. Aplicar reemplazos fonéticos de región si aplica
        for k, v in profile["replacements"].items():
            clean = re.sub(rf"\b{k}\b", v, clean, flags=re.I)

        # 2. Evitar acumulación o choque de muletillas (Anti-awkward fillers)
        # Si el texto ya empieza con una interjección natural, NO agregar otra
        lower = clean.lower()
        already_has_filler = any(lower.startswith(h) for h in ("che", "mirá", "mira", "ah claro", "vea", "oye", "ehh", "mm"))

        if not already_has_filler:
            # 25% probabilidad de apertura suave regional
            if random.random() < 0.25:
                prefix = random.choice(profile["openings"])
                clean = f"{prefix}{clean}"

        # 3. Formatear pausas naturales en comas de forma moderada
        def _sub_pause(match):
            return random.choice(profile["pauses"])

        # Solo reemplazar la primera coma larga para no sobrecargar el audio
        clean = re.sub(r",\s*", _sub_pause, clean, count=1)

        log.info(f"[audio_auditor] Refined script (region={region}) -> {clean[:50]}...")
        return clean


# Global Auditor Singleton
audio_auditor = FirbyAudioAuditor()
