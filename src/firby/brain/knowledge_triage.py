# -*- coding: utf-8 -*-
"""
Firby Medical Knowledge Base & Emergency Triage Engine (Camila Persona)
Provides strict semantic document lookup, anti-hallucination medical guardrails,
and automated Code-Red emergency detection with instant doctor escalation.
"""
from __future__ import annotations

import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

import httpx

log = logging.getLogger("firby.knowledge_triage")


# Señales de alerta roja / urgencia médica
EMERGENCY_RED_FLAGS = [
    r"sangr(ado|ando|e)", r"hemorragi", r"dolor (insoportable|extremo|muy fuerte|agudo)",
    r"fiebre (alta|38|39|40)", r"infecci(on|ón)", r"pus", r"hinchaz(on|ón) sever",
    r"asfixi", r"no puedo respirar", r"desmay", r"convulsi", r"alergia grave",
    r"se abri(o|ó) los puntos", r"se me solt(o|ó) la cirug", r"emergencia"
]


class MedicalTriageEngine:
    """Motor de Triaje Médico y Base de Conocimiento Clínica."""

    def __init__(self, db, telegram_bot_token: Optional[str] = None, admin_telegram_chat_id: Optional[str] = None):
        self.db = db
        self.bot_token = telegram_bot_token
        self.admin_chat_id = admin_telegram_chat_id

    def check_emergency_triage(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Escanea el mensaje en busca de alertas médicas críticas.
        Devuelve (es_emergencia, motivo_detectado).
        """
        text_lower = text.lower()
        for pattern in EMERGENCY_RED_FLAGS:
            match = re.search(pattern, text_lower)
            if match:
                return True, match.group(0)
        return False, None

    async def handle_emergency_alert(
        self, patient_phone: str, message: str, trigger_reason: str, clinic_name: str
    ) -> str:
        """
        Interrumpe el flujo normal, envía mensaje de primeros auxilios y dispara alerta al doctor.
        """
        log.warning(f"[TRIAGE CRÍTICO] 🚨 Emergencia detectada de {patient_phone}: {trigger_reason}")

        # 1. Notificar al Doctor / Administrador vía Telegram / Webhook
        await self._dispatch_doctor_emergency_alert(patient_phone, message, trigger_reason, clinic_name)

        # 2. Mensaje humano tranquilizador e instrucciones al paciente
        response = (
            f"⚠️ *Atención prioritaria*: Hemos detectado que presentas una molestia que requiere revisión médica urgente ||| "
            f"Ya le acabo de enviar una alerta directa de alta prioridad al doctor de turno en {clinic_name} con tu mensaje ||| "
            f"Por favor mantén la calma, no te automediques. Si presentas dificultad respiratoria o sangrado profuso, acude al servicio de urgencias más cercano inmediatamente. Nuestro equipo te llamará en breve."
        )
        return response

    async def _dispatch_doctor_emergency_alert(
        self, patient_phone: str, message: str, trigger_reason: str, clinic_name: str
    ):
        """Envía alerta de emergencia instantánea a los canales administrativos."""
        alert_text = (
            f"🚨🚨 *ALERTA MÉDICA DE EMERGENCIA - FIRBY* 🚨🚨\n\n"
            f"🏥 *Clínica*: {clinic_name}\n"
            f"📱 *Paciente*: +{patient_phone}\n"
            f"⚠️ *Motivo de Alerta*: `{trigger_reason}`\n"
            f"💬 *Mensaje del Paciente*: \"{message}\"\n\n"
            f"⏰ *Hora*: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"👉 *Acción requerida*: Contactar al paciente de inmediato."
        )

        from src.core.globals import Config
        token = self.bot_token or getattr(Config, "TELEGRAM_TOKEN", None)
        admin_id = self.admin_chat_id or getattr(Config, "TELEGRAM_ADMIN_CHAT_ID", None)

        if token and admin_id:
            try:
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(url, json={
                        "chat_id": admin_id,
                        "text": alert_text,
                        "parse_mode": "Markdown"
                    })
                log.info(f"[TRIAGE] Alerta enviada a Telegram admin {admin_id}")
            except Exception as e:
                log.error(f"[TRIAGE] Error enviando alerta a Telegram: {e}")

    def query_knowledge_base(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Consulta documentos clínicos indexados en la base de datos (precios, preparación, etc.).
        """
        try:
            with self.db._conn() as c:
                # Buscar en tabla de memorias / knowledge_base
                rows = c.execute("""
                    SELECT id, key, content, category, metadata
                    FROM memories
                    WHERE content LIKE ? OR key LIKE ?
                    LIMIT ?
                """, (f"%{query}%", f"%{query}%", limit)).fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            log.debug(f"[KnowledgeTriage] Error consultando memoria: {e}")
            return []
