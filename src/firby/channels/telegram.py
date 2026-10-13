# -*- coding: utf-8 -*-
"""Adaptador de canal para Telegram Bot API."""
from __future__ import annotations
import logging
import httpx
from typing import Dict, Any, Optional, List
from src.firby.channels.base import ChannelAdapterBase, NormalizedMessage

log = logging.getLogger("firby.channels.telegram")

class TelegramAdapter(ChannelAdapterBase):
    """Adaptador para interactuar con la API de Telegram."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.token = config.get("token")
        if not self.token:
            raise ValueError("Token de Telegram no configurado en los parámetros del adaptador.")
        self.api_url = f"https://api.telegram.org/bot{self.token}"

    async def send_message(self, recipient_id: str, text: str, attachments: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Envía un mensaje de texto o con adjuntos a un chat_id de Telegram."""
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": recipient_id,
            "text": text,
            "parse_mode": "Markdown"  # Soporte básico para negritas/itálicas
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    return True
                log.error(f"[telegram] Falló envío: {response.status_code} - {response.text}")
        except Exception as e:
            log.error(f"[telegram] Excepción al enviar mensaje a {recipient_id}: {e}")
        return False

    async def handle_webhook(self, data: Dict[str, Any]) -> Optional[NormalizedMessage]:
        """Procesa y normaliza mensajes recibidos mediante webhook de Telegram."""
        message = data.get("message") or data.get("edited_message")
        if not message:
            return None

        chat = message.get("chat")
        sender = message.get("from")
        text = message.get("text") or ""
        
        if not chat or not sender:
            return None

        # Evitar responder a bots
        if sender.get("is_bot"):
            return None

        # Mapear chat_id y sender_id
        chat_id = str(chat.get("id"))
        sender_id = str(sender.get("id"))

        # Extraer adjuntos básicos (por ejemplo, fotos o documentos)
        attachments = []
        if "photo" in message:
            # Telegram envía múltiples tamaños de foto, tomamos la más grande (última de la lista)
            photo_sizes = message["photo"]
            if photo_sizes:
                attachments.append({
                    "type": "image",
                    "file_id": photo_sizes[-1].get("file_id"),
                    "file_unique_id": photo_sizes[-1].get("file_unique_id")
                })
        elif "document" in message:
            doc = message["document"]
            attachments.append({
                "type": "document",
                "file_id": doc.get("file_id"),
                "mime_type": doc.get("mime_type"),
                "file_name": doc.get("file_name")
            })

        return NormalizedMessage(
            platform="telegram",
            sender_id=sender_id,
            text=text,
            channel_id=chat_id,
            attachments=attachments,
            raw_data=data
        )
