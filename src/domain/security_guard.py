# -*- coding: utf-8 -*-
"""
Firby Security Guardrail & Injection Shield
===========================================
Protección de seguridad de nivel empresarial inspirada en Hermes ThreatPatterns y OpenClaw Guardrails.

Detecta y bloquea antes de enviar al LLM:
1. Inyección de Prompts / Jailbreaks (DAN, "Ignora instrucciones", "Modo desarrollador").
2. Intentos de extracción de System Prompt / Credenciales / API Keys.
3. Ataques de ejecución de código / Inyección SQL / Comandos de consola.
4. Spam / Inundación por tarifa de tasa (Rate Limiting per JID).
"""

from __future__ import annotations
import re
import time
import logging
from typing import Dict, Any, Tuple, Optional

log = logging.getLogger("firby.security")


class SecurityGuardEngine:
    """Escudo de seguridad para filtrar mensajes maliciosos y limitar tasa de peticiones."""

    def __init__(self):
        # Tracking de tasa por chat_id: chat_id -> list of timestamps
        self._user_rate_timestamps: Dict[str, list] = {}
        # Historial de amenazas bloqueadas
        self._blocked_threats_count: int = 0

        # Patrones de Inyección de Prompt y Jailbreak (en texto normalizado sin acentos)
        self._injection_patterns = [
            re.compile(r"ignore\s+(all\s+)?(previous\s+)?instructions", re.IGNORECASE),
            re.compile(r"ignora\s+(todas\s+las\s+)?(instrucciones|reglas)", re.IGNORECASE),
            re.compile(r"revela\s+(tu\s+)?(system\s+prompt|prompt\s+sistema|instrucciones)", re.IGNORECASE),
            re.compile(r"show\s+(me\s+)?(your\s+)?(system\s+prompt|instructions)", re.IGNORECASE),
            re.compile(r"dame\s+(la\s+)?(api\s*key|clave\s*api|password|contrasena)", re.IGNORECASE),
            re.compile(r"give\s+(me\s+)?(the\s+)?(api\s*key|password|secret)", re.IGNORECASE),
            re.compile(r"act\s+as\s+(dan|an\s+unfiltered|do\s+anything\s+now)", re.IGNORECASE),
            re.compile(r"actua\s+como\s+(dan|un\s+hacker|modo\s+desarrollador|sin\s+filtros)", re.IGNORECASE),
            re.compile(r"developer\s+mode\s+enabled", re.IGNORECASE),
            re.compile(r"repeat\s+everything\s+above", re.IGNORECASE),
            re.compile(r"repite\s+todo\s+lo\s+anterior", re.IGNORECASE),
        ]

        # Patrones de Inyección de Código / Comandos
        self._code_injection_patterns = [
            re.compile(r"<\s*script[^>]*>", re.IGNORECASE),
            re.compile(r"DROP\s+TABLE|DELETE\s+FROM|UNION\s+SELECT", re.IGNORECASE),
            re.compile(r"import\s+os|import\s+sys", re.IGNORECASE),
            re.compile(r"rm\s+-rf|eval\s*\(|exec\s*\(", re.IGNORECASE),
        ]

    def _normalize(self, s: str) -> str:
        s = s.lower().strip()
        accents = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u', 'ñ': 'n'}
        for k, v in accents.items():
            s = s.replace(k, v)
        return s

    def inspect_message(self, text: str, chat_id: str = "") -> Tuple[bool, Optional[str]]:
        """
        Inspecciona un mensaje entrante antes de procesarlo en el LLM.
        Devuelve: (is_safe: bool, rejection_response: str|None)
        """
        if not text or not isinstance(text, str):
            return True, None

        clean_text = self._normalize(text)

        # 1. Chequeo de Rate Limit (Máximo 15 mensajes por minuto por usuario)
        if chat_id:
            now = time.time()
            timestamps = self._user_rate_timestamps.get(chat_id, [])
            # Limpiar timestamps mayores a 60 segundos
            timestamps = [ts for ts in timestamps if now - ts < 60]
            timestamps.append(now)
            self._user_rate_timestamps[chat_id] = timestamps

            if len(timestamps) > 15:
                log.warning(f"[security] Rate limit excedido para {chat_id} ({len(timestamps)} msgs/min)")
                return False, "Vas un poco rápido 😅 ||| Dame un segundito y ya te respondo"

        # 2. Chequeo de Inyección de Prompt / Jailbreak
        for pattern in self._injection_patterns:
            if pattern.search(clean_text):
                self._blocked_threats_count += 1
                log.warning(f"[security] Ataque de Prompt Injection detectado de {chat_id}: '{clean_text[:60]}'")
                return False, "Jaja buen intento 😜 ||| Pero soy Firby y solo estoy programada para ayudarte con la atención de tu negocio en WhatsApp"

        # 3. Chequeo de Inyección de Código / SQL
        for pattern in self._code_injection_patterns:
            if pattern.search(clean_text):
                self._blocked_threats_count += 1
                log.warning(f"[security] Inyección de código detectada de {chat_id}: '{clean_text[:60]}'")
                return False, "Operación no permitida por seguridad 🛡️ ||| ¿En qué más puedo ayudarte con tu negocio?"

        return True, None


# Instancia global del guardia de seguridad
security_guard = SecurityGuardEngine()
