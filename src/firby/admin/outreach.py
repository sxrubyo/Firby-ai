"""Admin Proactive Outreach Subsystem for Firby V10.

Allows admins and Ovni to trigger proactive messages to any phone number/chat ID,
normalizes target channels (WhatsApp / Telegram), tracks session context,
and prepares the AI receptionist for seamless patient replies.
"""

import re
import time
import logging
from typing import Dict, Any, Optional

log = logging.getLogger("firby.admin.outreach")


class AdminOutreachEngine:
    """Motor de Proactivo Outreach para Administradores y Ovni."""

    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self._outreach_history: Dict[str, Dict[str, Any]] = {}

    def parse_escribir_command(self, raw_text: str) -> Optional[Dict[str, str]]:
        """Parses natural admin command formats:
        - /escribir <number> <message>
        - /hablale <number> <message>
        - /outbound <number> <message>
        - háblale a <number> <message>
        - escribele a <number> <message>
        """
        text = raw_text.strip()

        patterns = [
            r"^/(?:escribir|hablale|háblale|outbound|contactar)\s+([^\s]+)\s+(.+)$",
            r"^(?:háblale|hablale|escríbele|escribe|escribele|envíale|enviale)\s+(?:a\s+)?([^\s]+)\s+(.+)$",
        ]

        for pat in patterns:
            match = re.match(pat, text, re.DOTALL | re.IGNORECASE)
            if match:
                recipient = match.group(1).strip()
                message = match.group(2).strip()
                return {
                    "recipient": recipient,
                    "message": message,
                }

        return None

    def normalize_recipient(self, recipient: str, preferred_channel: str = "whatsapp") -> Dict[str, str]:
        """Convierte números crudos (ej. 3124348669, +573124348669) en JIDs/IDs de canal."""
        raw_clean = recipient.strip()
        clean_num = re.sub(r"[^\d]", "", raw_clean)

        # Si empieza con 3 (ej. 3124348669 de Colombia), agregar prefijo país 57
        if len(clean_num) == 10 and clean_num.startswith("3"):
            clean_num = "57" + clean_num

        if preferred_channel == "whatsapp":
            jid = recipient if "@" in recipient else f"{clean_num}@s.whatsapp.net"
            return {"chat_id": jid, "channel": "whatsapp", "raw": clean_num}
        else:
            return {"chat_id": clean_num, "channel": "telegram", "raw": clean_num}

    def register_outreach_session(self, recipient_info: Dict[str, str], message: str, admin_id: str = "admin") -> Dict[str, Any]:
        """Registra la sesión de outreach en memoria para que la IA sepa el contexto al responder el paciente."""
        chat_id = recipient_info["chat_id"]
        session_data = {
            "chat_id": chat_id,
            "tenant_id": self.tenant_id,
            "channel": recipient_info["channel"],
            "raw_recipient": recipient_info["raw"],
            "outbound_message": message,
            "admin_id": admin_id,
            "dispatched_at": time.time(),
            "status": "awaiting_patient_reply",
        }
        self._outreach_history[chat_id] = session_data
        log.info(f"[OutreachEngine] Registered outbound session for {chat_id} via {recipient_info['channel']}")
        return session_data

    def get_outreach_context(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Devuelve el contexto si la sesión fue iniciada por outreach del admin."""
        return self._outreach_history.get(chat_id)

    async def notify_admin_of_lead_booking(
        self,
        admin_chat_id: str,
        patient_name: str,
        patient_phone: str,
        requested_time: str,
        treatment: str = "Valoración médica",
        bridge_send_fn = None,
        llm_engine = None
    ) -> bool:
        """Notifica al Admin sobre una nueva cita con tono humano y natural de colega/empleada inteligente."""
        alert_msg = ""
        if llm_engine:
            try:
                system_prompt = (
                    "Eres la asistente comercial inteligente del negocio hablando con tu jefe/admin por WhatsApp. "
                    "Reporta con calidez, naturalidad y entusiasmo que un paciente acaba de agendar una cita. "
                    "Escribe en tono cercano de compañera de trabajo sin guiones ni cajas robóticas. "
                    "Menciónale que si quiere escribirle al cliente puede usar 'háblale a <número>'."
                )
                user_prompt = (
                    f"Reporta a tu jefe que agendaste a {patient_name} (teléfono: {patient_phone}) "
                    f"para {treatment} el {requested_time}."
                )
                r, _ = await llm_engine.complete(
                    [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                    model_tier="fast", temperature=0.7, max_tokens=150
                )
                if r and r.strip():
                    from firby_nuke_robot_phrases import humanize_whatsapp_punctuation
                    alert_msg = humanize_whatsapp_punctuation(r.strip())
            except Exception as e_llm:
                log.warning(f"[outreach] LLM alert generation failed: {e_llm}")

        if not alert_msg:
            alert_msg = (
                f"Hola! Te cuento que acabo de agendar a {patient_name} ({patient_phone}) para {treatment} "
                f"el {requested_time}! Quedó guardada provisionalmente en la agenda.\n\n"
                f"Si quieres enviarle algún mensaje desde aquí, solo dime o escribe 'háblale a {patient_phone}' y yo me encargo!"
            )

        log.info(f"[OutreachEngine] Sending natural booking notification for {patient_name} to admin {admin_chat_id}")
        if bridge_send_fn:
            try:
                await bridge_send_fn(admin_chat_id, alert_msg)
                return True
            except Exception as e:
                log.error(f"[outreach] Error sending admin alert: {e}")
        return False
