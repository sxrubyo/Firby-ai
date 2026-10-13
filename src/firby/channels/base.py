# -*- coding: utf-8 -*-
"""Clases base y utilidades para adaptadores de canales omnicanal."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

@dataclass
class NormalizedMessage:
    """Mensaje entrante normalizado desde cualquier plataforma."""
    platform: str
    sender_id: str
    text: str
    channel_id: Optional[str] = None
    is_admin: bool = False
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)

class ChannelAdapterBase(ABC):
    """Interfaz base para adaptadores de mensajería (WhatsApp, Telegram, Slack, etc.)."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def send_message(self, recipient_id: str, text: str, attachments: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Envía un mensaje al destinatario a través de la plataforma.
        
        Args:
            recipient_id: Identificador único del destinatario en la plataforma.
            text: Texto del mensaje.
            attachments: Archivos adjuntos opcionales.
            
        Returns:
            True si el envío fue exitoso, False en caso contrario.
        """
        pass

    @abstractmethod
    async def handle_webhook(self, data: Dict[str, Any]) -> Optional[NormalizedMessage]:
        """
        Procesa el payload crudo del webhook y lo normaliza.
        
        Args:
            data: Payload del webhook en formato de diccionario.
            
        Returns:
            Instancia de NormalizedMessage o None si el mensaje debe ser ignorado (ej. bucles, eco).
        """
        pass
