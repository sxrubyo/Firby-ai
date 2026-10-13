# -*- coding: utf-8 -*-
"""Anti-Robot Filters for response polishing."""
from __future__ import annotations

import logging
import re
from typing import List

from src.firby.core.proxy import GlobalProxy

log = logging.getLogger("firby.filters")

# Lazy imports/proxies for globals
_normalize_conv_text = GlobalProxy("_normalize_conv_text")


class AntiRobotFilter:
    """
    Filtra TODOS los patrones de bot antes de enviar al cliente.
    Nivel 1: solo frases obvias. Nivel 2: estricto. Nivel 3: agresivo.

    Esta es la razón por la que V7 se sentía incómodo y falso.
    Cada patrón aquí fue identificado en conversaciones reales que fracasaron.
    """

    # ══════════════════════════════════════════════════════════════════
    # ESTRATEGIA v11 — PROMPT-FIRST, FILTER-LAST
    # ══════════════════════════════════════════════════════════════════
    # El filtro ya NO mutila el texto generado por el LLM.
    # La defensa principal es el system prompt: le decimos al LLM qué
    # NO decir ANTES de que lo genere. El filtro solo actúa sobre
    # frases que son completamente autónomas (inicio/fin de texto) y
    # que NUNCA aparecen en contexto legítimo mid-sentence.
    #
    # FORBIDDEN_HARD    # v12: Eliminadas totalmente las palabras prohibidas y mutilación de texto a solicitud explícita del usuario
    FORBIDDEN_HARD = set()
    FORBIDDEN_SOFT = set()
    FORBIDDEN_EXACT = set()

    @classmethod
    def build_antibot_prompt_block(cls) -> str:
        return ""

    # Patrones regex que revelan bot (nivel 2+)
    # SOLO se aplican si la burbuja completa es la frase (match de inicio a fin)
    # o si el patrón está al comienzo/fin — NUNCA mid-sentence.
    FORBIDDEN_PATTERNS_L2 = [
        r"(?:la\s+)?asistente\s+virtual",
        r"¡(hola|buenas|bienvenid)!\s*¿en qué",
        r"^\s*¡",                                    # Apertura con ¡
        r"sería\s+(un\s+)?placer",
        r"será\s+(un\s+)?placer",
        r"espero\s+(haberte|haber)\s+ayudado",
        r"espero\s+que\s+(esta\s+)?información\s+(te\s+)?sea",
    ]

    # Patrones nivel 3 (muy agresivo — solo si admin lo activa)
    FORBIDDEN_PATTERNS_L3 = [
        r"^por\s+favor",
        r"cabe\s+(mencionar|destacar|resaltar)",
        r"es\s+(muy\s+)?importante\s+(mencionar|destacar)",
    ]

    # Correcciones de ortografía y puntuación que el LLM genera mal
    ORTOGRAPHY_FIXES = [
        # Signos dobles de apertura (nunca en WhatsApp informal)
        (r'¿([^?]{1,200}\?)', r'\1'),         # ¿pregunta? → pregunta?  (solo en informal)
        (r'¡([^!]{1,200}!)', r'\1'),           # ¡exclamación! → exclamación!
        # Triple puntuación
        (r'\.{4,}', '...'),
        (r'!{2,}', '!'),
        (r'\?{2,}', '?'),
        # Espacios antes de puntuación
        (r'\s+([,.:;!?])', r'\1'),
        # Punto + espacio + mayúscula al inicio de burbuja (ya manejado en split)
        # Em dash (guión largo) — nunca en WhatsApp
        (r'\s*—\s*', ', '),
        (r'\s*–\s*', ', '),
    ]

    def __init__(self, level: int = 2):
        self.level = level
        self._patterns_l2 = []
        self._patterns_l3 = []
        self._orth_patterns = [(re.compile(p), r) for p, r in getattr(self, 'ORTOGRAPHY_FIXES', [])]

    def process(self, text: str, archetype: str = "amigable") -> str:
        """Retorna el texto del LLM intacto sin mutilaciones."""
        if not text:
            return ""
        return text.strip()

    def _fix_ortography(self, text: str) -> str:
        return text

    def _remove_forbidden_exact(self, text: str) -> str:
        return text

    def _remove_forbidden_patterns(self, text: str, patterns: list) -> str:
        return text

    def _enforce_informal_archetype(self, text: str, archetype: str) -> str:
        """Ajusta formalidad según arquetipo."""
        if archetype in ("amigable", "juvenil", "energica", "directa"):
            # Remover signos de apertura en arquetipos informales
            text = re.sub(r'^¿', '', text)
            text = re.sub(r'^¡', '', text)
        return text

    def score_humanness(self, text: str) -> float:
        """
        Puntúa qué tan humana suena la respuesta (0.0 = robot, 1.0 = humano real).
        V8.1 — Scoring mejorado con investigación de WhatsApp Colombia real.
        """
        score = 1.0
        text_lower = text.lower()
        word_count = len(text.split())

        # ── Penalizaciones por frases de bot ─────────────────────────────────
        for phrase in self.FORBIDDEN_EXACT:
            if phrase in text_lower:
                score -= 0.18  # más agresivo que antes

        for pattern in self._patterns_l2:
            if pattern.search(text):
                score -= 0.12

        # ── Penalización por longitud ─────────────────────────────────────────
        # Una persona real en WhatsApp raramente escribe más de 40 palabras seguidas
        if word_count > 70:
            score -= 0.25
        elif word_count > 50:
            score -= 0.15
        elif word_count > 35:
            score -= 0.08

        # ── Penalización por estructura de lista (bullet hell) ────────────────
        bullet_count = len(re.findall(r'(?:^|\n)\s*[-•*]\s', text))
        if bullet_count >= 3:
            score -= 0.20  # listas largas = definitivamente robot
        elif bullet_count >= 2:
            score -= 0.10

        # ── Penalización por mayúsculas excesivas ─────────────────────────────
        upper_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if upper_ratio > 0.25:
            score -= 0.12

        # ── Penalización por emojis excesivos ─────────────────────────────────
        # v11: 1-2 emojis es natural en negocios colombianos — no penalizar
        emoji_count = len(re.findall(
            r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]',
            text
        ))
        if emoji_count > 4:
            score -= 0.20   # spam de emojis sí penaliza
        elif emoji_count > 2:
            score -= 0.05   # leve — 3 puede ser aceptable

        # ── Penalización por signos de apertura ───────────────────────────────
        if '¿' in text or '¡' in text:
            score -= 0.08

        # ── Penalización por múltiples preguntas en una burbuja ───────────────
        question_count = text.count('?')
        if question_count >= 3:
            score -= 0.15
        elif question_count >= 2:
            score -= 0.05

        # ── Penalización por punto final (WhatsApp real no lo usa) ────────────
        bubbles = [b.strip() for b in text.split('|||')]
        for bubble in bubbles:
            if bubble.endswith('.') and not bubble.endswith('...'):
                score -= 0.05

        # ── PREMIOS por marcadores de lenguaje humano colombiano ──────────────

        # Palabras de confirmación natural
        natural_affirmations = [
            "claro", "listo", "dale", "bacano", "chévere", "perfecto",
            "de una", "obvio", "eso", "sí claro", "sí señor"
        ]
        for w in natural_affirmations:
            if w in text_lower:
                score += 0.04
                break  # máximo 1 premio por categoría

        # Expresiones de empatía real (no fórmulas)
        real_empathy = ["ay qué pena", "ay no", "qué pena", "entiendo", "claro que sí pero"]
        for w in real_empathy:
            if w in text_lower:
                score += 0.03
                break

        # Conectores conversacionales naturales
        connectors = ["mira", "oye", "pues", "a ver", "eso sí", "eso es"]
        for w in connectors:
            if w in text_lower:
                score += 0.03
                break

        # Respuestas cortas (el sweet spot de WhatsApp: 5-25 palabras)
        if 5 <= word_count <= 15:
            score += 0.12
        elif 15 < word_count <= 25:
            score += 0.06

        # Uso natural de "|||" (burbujas separadas = muy humano)
        if "|||" in text and text.count("|||") <= 2:
            score += 0.08

        # Pregunta directa al final (cierre natural)
        clean_end = text.rstrip("| \n").lower()
        natural_closings = [
            "cuándo puedes", "te queda bien", "qué día", "esta semana",
            "cuéntame", "mándame", "qué tienes en mente", "cuándo puedes"
        ]
        for nc in natural_closings:
            if clean_end.endswith(nc) or nc in clean_end[-50:]:
                score += 0.06
                break

        return max(0.0, min(1.0, score))
