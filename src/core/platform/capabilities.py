# -*- coding: utf-8 -*-
"""
Firby Platform — Capabilities & Permissions Enforcement Engine
==============================================================
Separa formalmente:
1. PLATFORM CAPABILITIES: Capacidades técnicas soportadas globalmente por Firby.
2. AGENT ENABLED CAPABILITIES: Qué capacidades están habilitadas para un agente específico.
3. PERMISSION MODEL:
   - Tool Permission: Habilitado o deshabilitado en configuración.
   - Read Permission: Acceso a datos y navegación (solo lectura).
   - Write Permission: Mutación de base de datos o creación de citas.
   - External Action: Llamadas a servicios externos (WhatsApp, Webhooks).
   - Approval Requirement: 'none' (autónomo) vs 'human' (requiere visto bueno del dueño).
4. PRECONDITION EVALUATION:
   - Una herramienta habilitada NO es ejecutable si no cumple requisitos de infraestructura
     (ejemplo: book_appointment requiere integración activa con Google Calendar).
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple

from src.core.operator.business_config import BusinessConfig, PlatformCapability

log = logging.getLogger("firby.platform.capabilities")


class PermissionLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    EXTERNAL_ACTION = "external_action"
    ADMIN = "admin"


class ApprovalRequirement(str, Enum):
    NONE = "none"
    HUMAN = "human"
    OWNER_WHATSAPP = "owner_whatsapp"


@dataclass
class CapabilityMetadata:
    """Definición estática de una capacidad de la plataforma."""
    name: str
    description: str
    permission_level: PermissionLevel
    default_approval: ApprovalRequirement
    required_integrations: List[str] = field(default_factory=list)


# Registro canónico de capacidades que la plataforma Firby ofrece
PLATFORM_CAPABILITIES_CATALOG: Dict[str, CapabilityMetadata] = {
    "navigate_web": CapabilityMetadata(
        name="navigate_web",
        description="Navega la pantalla del usuario a una sección o ruta del sitio web",
        permission_level=PermissionLevel.READ,
        default_approval=ApprovalRequirement.NONE,
        required_integrations=[]
    ),
    "web_navigation": CapabilityMetadata(
        name="web_navigation",
        description="Alias canónico de navegación web",
        permission_level=PermissionLevel.READ,
        default_approval=ApprovalRequirement.NONE,
        required_integrations=[]
    ),
    "highlight_ui": CapabilityMetadata(
        name="highlight_ui",
        description="Resalta visualmente un elemento o tarjeta en el frontend",
        permission_level=PermissionLevel.READ,
        default_approval=ApprovalRequirement.NONE,
        required_integrations=[]
    ),
    "query_business_knowledge": CapabilityMetadata(
        name="query_business_knowledge",
        description="Consulta la base de conocimiento oficial del negocio",
        permission_level=PermissionLevel.READ,
        default_approval=ApprovalRequirement.NONE,
        required_integrations=[]
    ),
    "check_availability": CapabilityMetadata(
        name="check_availability",
        description="Revisa horarios disponibles en el calendario del negocio",
        permission_level=PermissionLevel.READ,
        default_approval=ApprovalRequirement.NONE,
        required_integrations=["google_calendar"]
    ),
    "book_appointment": CapabilityMetadata(
        name="book_appointment",
        description="Registra una cita confirmada en la agenda del negocio",
        permission_level=PermissionLevel.WRITE,
        default_approval=ApprovalRequirement.NONE,
        required_integrations=["google_calendar"]
    ),
    "capture_lead": CapabilityMetadata(
        name="capture_lead",
        description="Captura los datos de contacto y requerimiento de un visitante",
        permission_level=PermissionLevel.WRITE,
        default_approval=ApprovalRequirement.NONE,
        required_integrations=[]
    ),
    "escalate_to_human": CapabilityMetadata(
        name="escalate_to_human",
        description="Notifica al dueño del negocio por WhatsApp para visto bueno o excepción",
        permission_level=PermissionLevel.EXTERNAL_ACTION,
        default_approval=ApprovalRequirement.NONE,
        required_integrations=["whatsapp_owner"]
    )
}


@dataclass
class CapabilityEvaluationResult:
    """Resultado de evaluar si una herramienta puede ser ejecutada por un agente."""
    authorized: bool
    capability_name: str
    permission_level: PermissionLevel
    approval_mode: ApprovalRequirement
    reason: Optional[str] = None
    missing_integrations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "authorized": self.authorized,
            "capability_name": self.capability_name,
            "permission_level": self.permission_level.value,
            "approval_mode": self.approval_mode.value,
            "reason": self.reason,
            "missing_integrations": self.missing_integrations
        }


class CapabilityEngine:
    """Motor de autorización y evaluación de capacidades del runtime."""

    @classmethod
    def evaluate_capability(
        cls,
        config: BusinessConfig,
        tool_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> CapabilityEvaluationResult:
        """
        Evalúa de forma exhaustiva y server-side si el agente tiene permitido ejecutar una tool.
        Revisa:
        1. Existencia en el catálogo de capacidades de la plataforma.
        2. Estado 'enabled' en la configuración del agente.
        3. Integraciones de infraestructura requeridas (e.g. Google Calendar conectado).
        4. Nivel de permiso y requerimiento de aprobación humana.
        """
        canonical_name = "navigate_web" if tool_name == "web_navigation" else tool_name
        catalog_meta = PLATFORM_CAPABILITIES_CATALOG.get(canonical_name) or PLATFORM_CAPABILITIES_CATALOG.get(tool_name)

        if not catalog_meta:
            return CapabilityEvaluationResult(
                authorized=False,
                capability_name=tool_name,
                permission_level=PermissionLevel.READ,
                approval_mode=ApprovalRequirement.NONE,
                reason=f"La herramienta '{tool_name}' no existe en las capacidades de la plataforma Firby."
            )

        # 1. Comprobar si está habilitada en la configuración del agente
        is_allowed, disabled_msg = config.is_tool_authorized(canonical_name)
        if not is_allowed:
            return CapabilityEvaluationResult(
                authorized=False,
                capability_name=canonical_name,
                permission_level=catalog_meta.permission_level,
                approval_mode=catalog_meta.default_approval,
                reason=disabled_msg or f"La herramienta '{canonical_name}' está deshabilitada para este agente."
            )

        # 2. Comprobar integraciones requeridas (Preconditions)
        missing_integrations = []
        for req in catalog_meta.required_integrations:
            connected = getattr(config.connected_integrations, req, False)
            if not connected:
                missing_integrations.append(req)

        if missing_integrations:
            human_reqs = ", ".join(missing_integrations).replace("google_calendar", "Google Calendar").replace("whatsapp_owner", "WhatsApp del Propietario")
            return CapabilityEvaluationResult(
                authorized=False,
                capability_name=canonical_name,
                permission_level=catalog_meta.permission_level,
                approval_mode=catalog_meta.default_approval,
                missing_integrations=missing_integrations,
                reason=f"La herramienta '{canonical_name}' requiere la integración [{human_reqs}] conectada en el negocio."
            )

        # 3. Comprobar permisos especiales
        perm = config.tool_permissions.get(canonical_name) or config.tool_permissions.get(tool_name)
        requires_approval = ApprovalRequirement.HUMAN if (perm and perm.requires_authorization) else catalog_meta.default_approval

        return CapabilityEvaluationResult(
            authorized=True,
            capability_name=canonical_name,
            permission_level=catalog_meta.permission_level,
            approval_mode=requires_approval,
            reason=None
        )


capability_engine = CapabilityEngine
