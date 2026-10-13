# -*- coding: utf-8 -*-
"""
Firby AI — Web Operator Policy & Permissions Engine
===================================================
Control de permisos, validación de acciones de UI y auditoría.
Garantiza que el agente NO pueda ejecutar JavaScript arbitrario sobre la página
y que toda acción de navegación o interfaz sea estrictamente validada.
"""

from __future__ import annotations
import re
from typing import Tuple, Optional, Set
from src.core.operator.models import UIAction, UIActionType

# Rutas permitidas para navegación interna
ALLOWED_INTERNAL_ROUTES: Set[str] = {
    "/",
    "/sobre-nosotros",
    "/about-us",
    "/faq",
    "/preguntas-frecuentes",
    "/terminos",
    "/terms",
    "/politica-de-privacidad",
    "/privacy",
    "/privacidad",
    "/data-agreement",
    "/sign-in",
    "/sign-up",
    "/free-trial",
    "/workspace"
}

# Secciones oficiales y anclajes permitidos en la landing
ALLOWED_SECTIONS: Set[str] = {
    "#hero",
    "#problema",
    "#sub-costo-oculto",
    "#como-funciona",
    "#sobre-nosotros",
    "#equipo-digital",
    "#canales",
    "#seguridad-cumplimiento",
    "#planes",
    "#experiencia-conversacional",
    "#contacto"
}

# Selectores permitidos para highlight y scroll
ALLOWED_HIGHLIGHT_SELECTORS: Set[str] = {
    "#planes",
    ".pricing-card",
    ".pricing-card.popular",
    "#como-funciona",
    ".step-card",
    "#sobre-nosotros",
    "#equipo-digital",
    ".team-card",
    "#seguridad-cumplimiento",
    ".channel-preview-widget",
    "#canales",
    "#problema",
    "#hero",
    "#contacto"
}


class WebPolicyEngine:
    """Valida y audita acciones de interfaz emitidas por el runtime del agente."""

    @staticmethod
    def is_safe_target(target: str) -> bool:
        """Verifica que el target no contenga inyecciones ni código malicioso."""
        if not target or len(target) > 200:
            return False
        # Bloquear javascript:, data:, event handlers, etc.
        lowered = target.lower().strip()
        if any(bad in lowered for bad in ["javascript:", "data:", "<script", "eval(", "onload", "onclick", "onerror"]):
            return False
        return True

    @classmethod
    def validate_action(cls, action: UIAction) -> Tuple[bool, Optional[str]]:
        """
        Valida que la acción estructurada cumpla las políticas de seguridad.
        Retorna (es_valida, error_o_motivo).
        """
        if not cls.is_safe_target(action.target):
            return False, "Target de acción inseguro o no permitido"

        action_type = action.type if isinstance(action.type, UIActionType) else UIActionType(action.type)

        if action_type == UIActionType.NAVIGATE_TO:
            # Debe ser una ruta interna permitida
            clean_route = action.target.split("?")[0].split("#")[0]
            if clean_route not in ALLOWED_INTERNAL_ROUTES and not clean_route.startswith("/"):
                return False, f"Ruta de navegación no autorizada: {clean_route}"
            return True, None

        elif action_type == UIActionType.NAVIGATE_TO_SECTION or action_type == UIActionType.SCROLL_TO:
            # Debe ser una sección ancla válida
            sec = action.target if action.target.startswith("#") else f"#{action.target}"
            if sec not in ALLOWED_SECTIONS:
                # Si no está en la lista estricta pero es un selector ID seguro alfanumérico
                if re.match(r'^#[a-zA-Z0-9_\-]+$', sec):
                    return True, None
                return False, f"Sección objetivo no reconocida: {sec}"
            return True, None

        elif action_type == UIActionType.HIGHLIGHT:
            # Debe ser un selector válido de la whitelist o un id de sección permitido
            if action.target in ALLOWED_HIGHLIGHT_SELECTORS or action.target in ALLOWED_SECTIONS:
                return True, None
            if re.match(r'^[#\.][a-zA-Z0-9_\-]+$', action.target):
                return True, None
            return False, f"Selector de destaque no permitido: {action.target}"

        elif action_type in (UIActionType.OPEN_MODAL, UIActionType.OPEN_FORM, UIActionType.FOCUS_ELEMENT):
            if re.match(r'^[a-zA-Z0-9_\-]+$', action.target) or re.match(r'^[#\.][a-zA-Z0-9_\-]+$', action.target):
                return True, None
            return False, f"Identificador de elemento no permitido: {action.target}"

        return False, "Tipo de acción desconocido"

    @classmethod
    def resolve_section_target(cls, text: str) -> Optional[str]:
        """Infiere la sección de la landing más adecuada según la intención del texto."""
        t = text.lower()
        if any(k in t for k in ["plan", "precio", "cuanto cuesta", "cuánto cuesta", "costo", "tarifa", "mensualidad", "starter", "pro", "equipos", "prueba gratis", "descuento", "precio especial", "cobran", "suscrib", "suscripci", "contrat"]):
            return "#planes"
        if any(k in t for k in ["como funciona", "cómo funciona", "paso a paso", "funcionamiento", "que hace", "qué hace", "instalacion", "instalación", "integracion", "integración"]):
            return "#como-funciona"
        if any(k in t for k in ["seguridad", "privacidad", "cumplimiento", "bancaria", "datos", "otp", "cifrado"]):
            return "#seguridad-cumplimiento"
        if any(k in t for k in ["canal", "canales", "whatsapp", "dos canales"]):
            return "#canales"
        if any(k in t for k in ["equipo digital", "roles", "perfil", "perfiles", "operador digital", "asistentes", "especialistas"]):
            return "#equipo-digital"
        if any(k in t for k in ["quienes crearon", "quiénes crearon", "creadores", "sobre nosotros"]):
            return "#sobre-nosotros"
        if any(k in t for k in ["problema", "dolor", "costo oculto"]):
            return "#problema"
        if any(k in t for k in ["contacto", "hablar con alguien", "asesor", "demo", "demostracion", "demostración", "agendar", "cita", "reunion", "reunión"]):
            return "#contacto"
        return None
