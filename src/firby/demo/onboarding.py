# -*- coding: utf-8 -*-
"""
DemoOnboardingService — Módulo especializado en descubrimiento de negocio, scraping, e interceptación de credenciales.
"""
from __future__ import annotations
import re
import logging
from typing import Optional, List, Dict, Any, Tuple

log = logging.getLogger("firby.demo.onboarding")

class DemoOnboardingService:
    """Maneja el interceptor de tokens de integración y la lógica de clasificación de negocios."""

    def __init__(self, db_manager: Any = None):
        self.db = db_manager

    async def intercept_credentials(self, text: str) -> Optional[List[str]]:
        """
        Intercepta automáticamente tokens de Notion (`ntn_`) o ElevenLabs (`sk_`)
        enviados por el prospecto/admin durante la demo.
        """
        # Interceptor de Notion
        notion_match = re.search(r"\b(ntn_[a-zA-Z0-9_-]{15,})\b", text)
        if notion_match:
            token = notion_match.group(1)
            try:
                from src.firby.channels.onboarding import validate_notion_token
                notion_info = await validate_notion_token(token)
                if notion_info:
                    if self.db and hasattr(self.db, "add_linked_channel"):
                        try:
                            self.db.add_linked_channel(
                                platform="notion",
                                channel_identity=notion_info.get("workspace_name", "Notion"),
                                config_json={
                                    "token": token,
                                    "workspace_name": notion_info.get("workspace_name", "Notion"),
                                    "bot_name": notion_info.get("bot_name", "Firby Bot"),
                                }
                            )
                        except Exception as e:
                            log.warning(f"[demo_onboarding] add_linked_channel notion error: {e}")
                    return [
                        f"¡Excelente! Conectado a Notion {notion_info.get('workspace_name', 'Notion')}.",
                        "Ahora puedo sincronizarme con tus bases de datos de manera automática."
                    ]
            except Exception as ne:
                log.warning(f"[demo_onboarding] validate_notion_token error: {ne}")

        # Comando de Sincronización de Notion cuando no está vinculado
        if "sincronizar notion" in text.lower():
            linked = []
            if self.db and hasattr(self.db, "get_linked_channels"):
                try: linked = self.db.get_linked_channels(platform="notion")
                except Exception: pass
            if not linked:
                return [
                    "Notion no está conectado aún en esta instancia.",
                    "Pásame tu clave de integración de Notion (comienza con `ntn_`) para vincular tu espacio de trabajo de manera automática."
                ]

        # Interceptor de ElevenLabs
        elevenlabs_match = re.search(r"\b(sk_[a-zA-Z0-9_-]{15,})\b", text)
        if elevenlabs_match:
            token = elevenlabs_match.group(1)
            if self.db and hasattr(self.db, "add_linked_channel"):
                try:
                    self.db.add_linked_channel(
                        platform="elevenlabs",
                        channel_identity="ElevenLabs Voice Engine",
                        config_json={"token": token}
                    )
                except Exception as ee:
                    log.warning(f"[demo_onboarding] add_linked_channel elevenlabs error: {ee}")
            return [
                "¡Super! Configuré tu token de ElevenLabs para las notas de voz de tu bot.",
                "Ahora puedes pedirme audios o notas de voz en cualquier momento."
            ]

        return None
