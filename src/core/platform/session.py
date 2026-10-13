# -*- coding: utf-8 -*-
"""
Firby Platform — Secure Widget Session & Pinning Manager
========================================================
Resuelve de raíz los hallazgos de seguridad de la auditoría:
1. IDENTIFICADOR SEGURO NO SENSIBLE:
   Genera tokens de sesión criptográficos `fws_<64_hex_chars>`.
2. VINCULACIÓN INQUEBRANTABLE (TENANT & AGENT PINNING):
   Cada sesión queda registrada en el servidor con:
   (session_token) -> (tenant_id, agent_id, conversation_id, expires_at)
3. IMPOSIBILIDAD DE SUPLANTACIÓN (ANTI-SPOOFING):
   Si el cliente intenta modificar el parámetro 'tenant_id' o 'org_id' en el payload HTTP,
   el backend ignora el valor enviado y fuerza la identidad vinculada a la sesión.
4. EXPIRACIÓN Y RENOVACIÓN:
   Expiración a 30 días con actualización de 'last_seen_at' en cada interacción válida.
"""

from __future__ import annotations
import time
import secrets
import logging
from typing import Dict, Any, Optional, Tuple

from src.core.platform.models import WidgetSession
from src.core.platform.store import platform_store, PlatformStore

log = logging.getLogger("firby.platform.session")


class WidgetSessionManager:
    """Administrador de sesiones públicas para el Widget de Firby."""

    def __init__(self, store: Optional[PlatformStore] = None):
        self.store = store or platform_store

    def generate_token(self) -> str:
        """Genera un token seguro e impredecible para la sesión del widget."""
        return f"fws_{secrets.token_hex(32)}"

    def create_session(
        self,
        public_id: str,
        tenant_id: str,
        agent_id: str,
        conversation_id: Optional[str] = None,
        client_metadata: Optional[Dict[str, Any]] = None
    ) -> WidgetSession:
        """Crea y persiste una nueva sesión vinculada exclusivamente a un tenant y agente."""
        token = self.generate_token()
        conv_id = conversation_id or f"conv_{secrets.token_hex(12)}"
        now = time.time()
        session = WidgetSession(
            session_token=token,
            public_id=public_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            conversation_id=conv_id,
            created_at=now,
            expires_at=now + (30 * 86400),  # 30 días
            last_seen_at=now,
            client_metadata=client_metadata or {}
        )
        self.store.save_widget_session(session)
        log.info(f"[WidgetSessionManager] Creada sesión {token[:12]}... para tenant={tenant_id}, agent={agent_id}")
        return session

    def resolve_session(self, session_token: str) -> Optional[WidgetSession]:
        """Recupera la sesión verificando que no haya expirado."""
        if not session_token or not isinstance(session_token, str):
            return None
        session = self.store.get_widget_session(session_token.strip())
        if session and not session.is_expired():
            session.last_seen_at = time.time()
            self.store.save_widget_session(session)
            return session
        return None

    def validate_and_bind(
        self,
        session_token: Optional[str],
        public_id: Optional[str],
        fallback_tenant_id: str = "firby_landing",
        fallback_agent_id: str = "firby-demo",
        client_metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str, str, str]:
        """
        Valida o crea una sesión y devuelve la tupla inmutable:
        (session_token, tenant_id, agent_id, conversation_id).
        
        Garantía de Aislamiento:
        El servidor es la ÚNICA autoridad sobre a qué tenant y agente pertenece la sesión.
        """
        # 1. Intentar validar sesión existente si el token fue provisto
        if session_token:
            clean_token = session_token.strip()
            existing = self.resolve_session(clean_token)
            if existing:
                return (
                    existing.session_token,
                    existing.tenant_id,
                    existing.agent_id,
                    existing.conversation_id
                )

        # 2. Si no existe o expiró, resolver tenant_id y agent_id a partir de public_id
        resolved_tenant = fallback_tenant_id
        resolved_agent = fallback_agent_id
        pub_id = public_id or "agt_firby_demo"

        if public_id:
            agent = self.store.get_agent_by_public_id(public_id.strip())
            if agent:
                resolved_tenant = agent.tenant_id
                resolved_agent = agent.agent_id

        # 3. Crear una nueva sesión vinculada
        new_session = self.create_session(
            public_id=pub_id,
            tenant_id=resolved_tenant,
            agent_id=resolved_agent,
            client_metadata=client_metadata
        )
        return (
            new_session.session_token,
            new_session.tenant_id,
            new_session.agent_id,
            new_session.conversation_id
        )


widget_session_manager = WidgetSessionManager()
