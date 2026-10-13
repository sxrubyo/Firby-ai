"""Omnichannel Outreach Router for Firby V10.

Handles message dispatching, channel normalization, and response interceptors.
"""

import logging
from typing import Dict, Any, Optional
from src.firby.admin.outreach import AdminOutreachEngine
from src.firby.brain.psychology import LatAmPsychologyEngine

log = logging.getLogger("firby.channels.outreach_router")


class OmnichannelOutreachRouter:
    """Enrutador de Salida Omnicanal para el Admin y Ovni."""

    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self.engine = AdminOutreachEngine(tenant_id)
        self.psychology = LatAmPsychologyEngine()

    async def dispatch_admin_outreach(
        self,
        raw_recipient: str,
        message: str,
        send_fn: Any,
        preferred_channel: str = "whatsapp",
        admin_id: str = "admin",
    ) -> Dict[str, Any]:
        """Procesa y despacha un mensaje proactivo del admin a un destinatario."""
        recipient_info = self.engine.normalize_recipient(raw_recipient, preferred_channel)
        
        # Aplicar saneamiento anti-robot y tono de recepcionista si aplica
        clean_msg = self.psychology.sanitize_bot_phrases(message)

        # Registrar sesión de seguimiento
        session = self.engine.register_outreach_session(recipient_info, clean_msg, admin_id)

        # Invocar función de envío omnicanal (WhatsApp/Telegram API)
        success = False
        try:
            if callable(send_fn):
                await send_fn(recipient_info["chat_id"], clean_msg)
                success = True
            log.info(f"[OutreachRouter] Dispatched outreach to {recipient_info['chat_id']} ({recipient_info['channel']})")
        except Exception as e:
            log.error(f"[OutreachRouter] Failed to dispatch to {recipient_info['chat_id']}: {e}")
            session["status"] = "failed"
            session["error"] = str(e)

        return {
            "success": success,
            "session": session,
            "formatted_message": clean_msg,
        }
