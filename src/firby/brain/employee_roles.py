# -*- coding: utf-8 -*-
"""
Firby Digital Employees & Roles System
Manages the 5 specialized autonomous agents per business/tenant.
"""
from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from enum import Enum

log = logging.getLogger("firby.employee_roles")


class EmployeeRole(str, Enum):
    RECEPCIONISTA = "recepcionista"
    CLOSER_VENTAS = "closer_ventas"
    SOPORTE_KNOWLEDGE = "soporte_knowledge"
    AUTOMATIZADOR = "automatizador"
    GROWTH_CAMPAIGNS = "growth_campaigns"


EMPLOYEE_PROFILES = {
    EmployeeRole.RECEPCIONISTA: {
        "title": "Recepcionista & Front-Desk",
        "default_name": "Firby",
        "description": "Atención 24/7, agendamiento de citas en Google Calendar y llamadas telefónicas en vivo con voz humana.",
        "skills": ["agendar_cita", "consultar_disponibilidad", "enviar_recordatorios", "llamadas_voz"]
    },
    EmployeeRole.CLOSER_VENTAS: {
        "title": "Closer de Ventas & Pagos",
        "default_name": "Santiago",
        "description": "Califica leads, maneja objeciones de precios y genera links de pago/depósito por WhatsApp.",
        "skills": ["generar_link_pago", "calificar_lead", "recuperar_cotizacion", "confirmar_deposito"]
    },
    EmployeeRole.SOPORTE_KNOWLEDGE: {
        "title": "Soporte & Base de Conocimiento",
        "default_name": "Camila",
        "description": "Responde dudas complejas basadas en PDFs de la clínica y escala urgencias médicas de inmediato al doctor.",
        "skills": ["consultar_pdf", "triaje_urgencias", "escalar_doctor", "instrucciones_post_consulta"]
    },
    EmployeeRole.AUTOMATIZADOR: {
        "title": "Arquitecto de Automatizaciones",
        "default_name": "Nova",
        "description": "Crea flujos automáticos en n8n a partir de lo que el dueño le pida en lenguaje natural.",
        "skills": ["crear_automatizacion", "conectar_google_sheets", "enviar_alertas_telegram", "disparar_webhooks"]
    },
    EmployeeRole.GROWTH_CAMPAIGNS: {
        "title": "Especialista en Growth & Reactivación",
        "default_name": "Mateo",
        "description": "Detecta pacientes inactivos y envía mensajes hiperpersonalizados para llenar la agenda.",
        "skills": ["segmentar_inactivos", "campana_reactivacion", "promociones_personalizadas"]
    }
}


class EmployeeManager:
    """Manages active employee personas and dynamic prompts for a clinic/tenant."""

    def __init__(self, db):
        self.db = db

    def get_active_roles(self) -> List[EmployeeRole]:
        """Returns the active employee roles enabled for this clinic."""
        try:
            clinic = self.db.get_clinic()
            enabled = clinic.get("active_roles") or ["recepcionista", "closer_ventas", "soporte_knowledge"]
            if isinstance(enabled, str):
                import json
                enabled = json.loads(enabled)
            return [EmployeeRole(r) for r in enabled if r in EmployeeRole._value2member_map_]
        except Exception:
            return [EmployeeRole.RECEPCIONISTA, EmployeeRole.CLOSER_VENTAS]

    def build_system_prompt_extension(self) -> str:
        """Injects capabilities of active digital employees into the main AI prompt."""
        active_roles = self.get_active_roles()
        
        prompt_parts = [
            "\n## CAPACIDADES MULTI-ROL DEL SISTEMA FIRBY:",
            "Cuentas con las siguientes especialidades operativas activadas para este negocio:"
        ]

        for role in active_roles:
            info = EMPLOYEE_PROFILES.get(role, {})
            prompt_parts.append(f"- **{info.get('title')}**: {info.get('description')}")

        prompt_parts.append(
            "\nSi el usuario pide crear una automatización, cobrar un depósito o consultar un procedimiento, "
            "actúa con la especialidad correspondiente de manera natural, humana y ejecutiva."
        )

        return "\n".join(prompt_parts)
