# -*- coding: utf-8 -*-
"""Adaptador de canal para Slack Web API y Events API."""
from __future__ import annotations
import logging
import httpx
from typing import Dict, Any, Optional, List
from src.firby.channels.base import ChannelAdapterBase, NormalizedMessage

log = logging.getLogger("firby.channels.slack")

class SlackAdapter(ChannelAdapterBase):
    """Adaptador para interactuar con la API de Slack."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.token = config.get("token")
        self.signing_secret = config.get("signing_secret")
        if not self.token:
            raise ValueError("Token de Slack no configurado en los parámetros del adaptador.")

    async def send_message(self, recipient_id: str, text: str, attachments: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Envía un mensaje a un canal o usuario de Slack."""
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "channel": recipient_id,
            "text": text
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                result = response.json()
                if response.status_code == 200 and result.get("ok"):
                    return True
                log.error(f"[slack] Falló envío: {response.status_code} - {result.get('error')} - {result}")
        except Exception as e:
            log.error(f"[slack] Excepción al enviar mensaje a {recipient_id}: {e}")
        return False

    async def handle_webhook(self, data: Dict[str, Any]) -> Optional[NormalizedMessage]:
        """Procesa y normaliza eventos recibidos desde el Events API de Slack."""
        # 1. Manejo del reto de verificación de URL de Slack
        if data.get("type") == "url_verification":
            return NormalizedMessage(
                platform="slack",
                sender_id="slack_system",
                text=data.get("challenge", ""),
                channel_id="url_verification",
                raw_data=data
            )

        event = data.get("event")
        if not event:
            return None

        # 2. Filtrado de mensajes e incidencias
        # Solo procesamos eventos de tipo 'message'
        if event.get("type") != "message":
            return None

        # Ignorar mensajes del propio bot (evita bucles infinitos)
        if event.get("bot_id") or event.get("subtype") in ["bot_message", "message_changed", "message_deleted"]:
            return None

        text = event.get("text") or ""
        channel_id = event.get("channel")
        sender_id = event.get("user")

        if not channel_id or not sender_id:
            return None

        return NormalizedMessage(
            platform="slack",
            sender_id=sender_id,
            text=text,
            channel_id=channel_id,
            raw_data=data
        )
