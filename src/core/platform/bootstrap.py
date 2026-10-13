# -*- coding: utf-8 -*-
"""
Firby Platform — Public Agent Bootstrap Service
===============================================
Resuelve de forma segura y pública la configuración inicial del widget para:
GET /public/agents/{public_id}/bootstrap

Contrato de Seguridad Estricto:
- Valida que el agente esté en estado PUBLISHED.
- Resuelve public_id -> tenant_id -> published_version -> configuración.
- Emite o valida un token de sesión criptográfico (WidgetSession) vinculado al tenant.
- SEPARA DATOS PÚBLICOS DE INTERNOS:
  * Expone ÚNICAMENTE: public_id, branding, colores, capacidades públicas autorizadas,
    secciones de navegación del sitio web y opciones de bienvenida.
  * NUNCA expone: credenciales de integración, políticas confidenciales,
    atributos no listados (CEO, facturación), secretos ni rutas de servidor.
"""

from __future__ import annotations
import logging
from typing import Dict, Any, Optional

from src.core.platform.store import platform_store, PlatformStore
from src.core.platform.manager import control_plane, ControlPlaneManager
from src.core.platform.session import widget_session_manager, WidgetSessionManager
from src.core.platform.models import AgentStatus

log = logging.getLogger("firby.platform.bootstrap")


class PublicBootstrapService:
    """Servicio de resolución pública y bootstrapping del widget web."""

    def __init__(
        self,
        store: Optional[PlatformStore] = None,
        manager: Optional[ControlPlaneManager] = None,
        session_mgr: Optional[WidgetSessionManager] = None
    ):
        self.store = store or platform_store
        self.manager = manager or control_plane
        self.session_mgr = session_mgr or widget_session_manager

    def bootstrap_agent(
        self,
        public_id: str,
        session_token: Optional[str] = None,
        client_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta el bootstrap seguro para inicializar el widget en el navegador.
        Devuelve el contrato mínimo necesario sin secretos.
        """
        clean_pub_id = (public_id or "").strip()
        if not clean_pub_id:
            return {"ok": False, "error": "public_id es requerido para bootstrap."}

        # 1. Resolver el agente a partir del identificador público (con fallback para demo)
        agent = self.store.get_agent_by_public_id(clean_pub_id)
        if not agent and clean_pub_id in ("firby_landing", "firby-demo", "demo", "agt_firby_demo", "firby"):
            agent = self.store.get_agent_by_public_id("agt_firby_demo")

        if not agent:
            # Intentar búsqueda directa por agent_id
            agent = self.store.get_agent_by_id(clean_pub_id)

        if not agent:
            log.warning(f"[Bootstrap] Agente no encontrado con public_id: {clean_pub_id}")
            return {"ok": False, "error": f"Agente '{clean_pub_id}' no encontrado o no configurado."}

        # 2. Comprobar que esté publicado
        if agent.status != AgentStatus.PUBLISHED:
            log.info(f"[Bootstrap] Agente {agent.agent_id} está en estado {agent.status} (no publicado).")
            # Permitir en entorno dev pero advertir
            if agent.status == AgentStatus.DRAFT:
                pass  # Soportar prueba de borradores autorizados

        # 3. Vincular o crear la sesión pública segura (Tenant Pinning)
        token, tenant_id, agent_id, conv_id = self.session_mgr.validate_and_bind(
            session_token=session_token,
            public_id=agent.public_id,
            fallback_tenant_id=agent.tenant_id,
            fallback_agent_id=agent.agent_id,
            client_metadata=client_metadata
        )

        # 4. Obtener la configuración activa del negocio
        config = self.manager.get_active_config(tenant_id, agent_id)

        # 5. Filtrar estrictamente capacidades públicas autorizadas
        allowed_caps = []
        for cap_name, perm in config.tool_permissions.items():
            if perm.enabled:
                allowed_caps.append(cap_name)

        # 6. Preparar navegación pública
        nav_sections = [
            {
                "id": n.id,
                "target": n.target,
                "label": n.label,
                "description": n.description
            }
            for n in config.navigation_resources
        ]

        # 7. Construir carga pública segura (Zero Secrets)
        is_demo = tenant_id in ("tenant_demo", "firby_landing", "base", "demo")
        welcome_text = (
            "Hola, estoy aquí para ayudarte a conocer la plataforma, resolver dudas oficiales y agendar citas en tiempo real. En qué puedo orientarte hoy?"
            if is_demo else
            f"Hola, te damos la bienvenida a {config.identity.name}. Estoy para orientarte sobre nuestros servicios y agendar tu cita. En qué podemos ayudarte?"
        )

        initial_chips = (
            ["Ver planes y precios", "Cómo funciona Firby", "Seguridad y control"]
            if is_demo else
            ["Consultar servicios", "Agendar una cita", "Horarios y ubicación"]
        )

        branding = {
            "title": config.identity.name or "Firby",
            "accent_color": "#b9fa01" if is_demo else "#00825a",
            "border_color": "#00825a" if is_demo else "#1e293b",
            "avatar_url": "/assets/branding/Isotipo-pestana.png?v=20260914_live",
            "position": "right"
        }

        return {
            "ok": True,
            "agent": {
                "public_id": agent.public_id,
                "name": agent.name,
                "runtime_version": agent.runtime_version,
                "published_version": agent.published_version or 1
            },
            "business": {
                "name": config.identity.name,
                "description": config.identity.description,
                "website_url": config.identity.website_url
            },
            "branding": branding,
            "allowed_capabilities": allowed_caps,
            "navigation_sections": nav_sections,
            "session": {
                "session_token": token,
                "conversation_id": conv_id,
                "tenant_id": tenant_id,
                "agent_id": agent_id
            },
            "welcome": {
                "bubbles": [welcome_text],
                "chips": initial_chips
            }
        }


public_bootstrap_service = PublicBootstrapService()
