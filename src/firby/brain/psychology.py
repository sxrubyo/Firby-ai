"""Conversational Psychology Engine for LatAm & Colombia.

Implements emotional mirroring, anti-robot phrasing, natural micro-pauses,
and human receptionist cadence.
"""

import re
import logging
from typing import Dict, Any

log = logging.getLogger("firby.brain.psychology")


ROBOTIC_PHRASES = [
    "como modelo de lenguaje",
    "soy un asistente virtual",
    "soy una inteligencia artificial",
    "¿en qué más te puedo asistir el día de hoy?",
    "¿en qué te puedo ayudar hoy?",
    "es un placer atenderte hoy",
    "no dude en contactarnos",
    "estoy programado para",
    "soy firby de",
]

LATAM_WARM_CONNECTORS = [
    "Con todo gusto",
    "Claro que sí",
    "Regálame un segundo",
    "Entiendo perfectamente",
    "Con gusto te colaboro",
    "Excelente",
]

CASUAL_GREETINGS = ["ey", "yoo", "yo", "buenas", "hola", "qué tal", "buenas noches", "buenas tardes", "buenos días"]


class LatAmPsychologyEngine:
    """Motor de Psicología Conversacional y Espejo Emocional LatAm."""

    def __init__(self, region: str = "Colombia"):
        self.region = region

    def detect_sentiment(self, text: str) -> str:
        """Determina el estado emocional del usuario: urgente, ansioso, formal, amigable."""
        text_low = text.lower().strip()
        if any(w in text_low for w in ["urgente", "emergencia", "grave", "duele mucho", "ayuda por favor"]):
            return "urgent"
        elif any(w in text_low for w in ["precio", "cuánto vale", "costo", "valor", "tarifa"]):
            return "commercial_direct"
        elif text_low in CASUAL_GREETINGS or any(text_low.startswith(g) for g in ["ey", "yoo", "hola"]):
            return "casual_human"
        elif any(w in text_low for w in ["gracias", "buen día", "hola", "cordial saludo"]):
            return "warm_friendly"
        return "neutral"

    def humanize_greeting_turn(self, user_msg: str, bot_response: str, business_name: str = "Clínica Las Américas") -> str:
        """Transforma aperturas rígidas ("Soy Firby de X...") en respuestas cálidas y humanas de recepcionista real."""
        user_low = user_msg.lower().strip()
        bot_low = bot_response.lower()

        # Si el usuario hace una apertura informal como "Ey" o "Yoo what's up"
        if user_low in ["ey", "yoo", "yoo what's up", "yo", "eyyy"]:
            return f"¡Hola! 👋 ¿Cómo estás? Cuéntame, ¿en qué te puedo colaborar hoy en {business_name}?"

        # Si la respuesta del bot cayó en la muletilla rígida "Soy Firby de X, ¿en qué te puedo ayudar hoy?"
        if "soy firby" in bot_low and ("ayudar hoy" in bot_low or "asistir" in bot_low):
            return f"¡Hola! 👋 Claro que sí, bienvenido a {business_name}. Cuéntame, ¿qué consulta o cita necesitas revisar?"

        return bot_response

    def sanitize_bot_phrases(self, response: str) -> str:
        """Elimina muletillas de robot y formalismos sintéticos."""
        clean = response
        for phrase in ROBOTIC_PHRASES:
            clean = re.sub(re.escape(phrase), "", clean, flags=re.IGNORECASE).strip()

        # Limpiar dobles espacios o signos huérfanos
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    def apply_emotional_mirror(self, response: str, sentiment: str) -> str:
        """Ajusta el tono de la respuesta según el sentimiento detectado."""
        clean = self.sanitize_bot_phrases(response)

        if sentiment == "urgent":
            # Tono prioritario, sereno y directo
            if not clean.lower().startswith(("tranquil", "entiendo", "claro")):
                clean = f"Entiendo la urgencia. {clean}"
        elif sentiment == "commercial_direct":
            # Tono ágil y directo sin rodeos
            pass
        elif sentiment == "warm_friendly":
            # Tono cálido LatAm / Colombia
            if not any(c.lower() in clean.lower() for c in LATAM_WARM_CONNECTORS):
                clean = f"Con gusto. {clean}"

        return clean
