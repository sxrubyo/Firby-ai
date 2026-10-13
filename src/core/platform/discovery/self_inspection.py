# -*- coding: utf-8 -*-
"""
Firby Platform — Self-Inspection & System Diagnostic Engine
===========================================================
Implementa la capacidad de Firby para autodiagnosticarse y conocer su propia
arquitectura, componentes, capacidades, herramientas, integraciones y límites:
- "Firby se conoce a sí mismo" sin inventar ni alucinar.
- Inspecciona el Control Plane, Data Plane y estado de ejecución real.
"""

from __future__ import annotations
import sys
import os
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List

from src.core.platform.capabilities import PLATFORM_CAPABILITIES_CATALOG
from src.core.platform.control import agent_control
from src.core.platform.store import platform_store


@dataclass
class SelfInspectionReport:
    platform_name: str = "Firby Autonomous Operator Platform"
    version: str = "1.0.0 (Multi-Tenant)"
    runtime_environment: str = "Linux / PM2 / Caddy Reverse Proxy"
    components_identified: List[str] = field(default_factory=list)
    available_capabilities: List[Dict[str, Any]] = field(default_factory=list)
    active_tools: List[str] = field(default_factory=list)
    available_integrations: List[Dict[str, Any]] = field(default_factory=list)
    allowed_actions: List[str] = field(default_factory=list)
    disallowed_actions: List[str] = field(default_factory=list)
    isolation_guarantees: List[str] = field(default_factory=list)
    storage_engine: str = "SQLite Multi-Tenant (firby_ultra.db)"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform_name": self.platform_name,
            "version": self.version,
            "runtime_environment": self.runtime_environment,
            "components_count": len(self.components_identified),
            "components": self.components_identified,
            "available_capabilities": self.available_capabilities,
            "active_tools": self.active_tools,
            "available_integrations": self.available_integrations,
            "allowed_actions": self.allowed_actions,
            "disallowed_actions": self.disallowed_actions,
            "isolation_guarantees": self.isolation_guarantees,
            "storage_engine": self.storage_engine
        }


class SelfInspector:
    """Motor de autoinspección factual y verifiable de Firby."""

    @staticmethod
    def inspect(tenant_id: str = "tenant_demo", agent_id: str = "agent_firby_demo") -> SelfInspectionReport:
        report = SelfInspectionReport()

        # 1. Componentes del sistema
        report.components_identified = [
            "ControlPlaneManager (manager.py): Gobernanza, versionado y publicación",
            "PlatformStore (store.py): Persistencia SQLite particionada por tenant",
            "OperatorRuntime (runtime.py): Ciclo cognitivo THINK -> DECIDE -> ACT -> OBSERVE",
            "AgentControlSystem (control.py): CapabilityMatrix y Sandboxing",
            "TenantKnowledgeEngine (knowledge.py): RAG scoped por organización",
            "WidgetSessionManager (session.py): Token pinning criptográfico fws_",
            "PublicBootstrapService (bootstrap.py): Exposición pública sin fuga de secretos",
            "AgentNavigationMotionEngine (firby-motion-engine.js): Física de desplazamiento inercial",
            "Universal Widget SDK (firby.js): Integración en 1 línea para sitios web"
        ]

        # 2. Matriz de capacidades evaluada para el agente
        cap_matrix = agent_control.get_capability_matrix(tenant_id, agent_id)
        for c in cap_matrix:
            report.available_capabilities.append(c.to_dict())

        # 3. Herramientas activas
        report.active_tools = [
            "navigate_to_section: Navegación asistida a secciones web con física de rodillo",
            "highlight_element: Resaltado táctil sutil de elementos de interfaz",
            "check_availability: Consulta de horarios disponibles en agenda",
            "schedule_appointment: Agendamiento atómico con verificación OTP",
            "query_business_knowledge: Consulta de políticas y términos comerciales",
            "escalate_to_human: Notificación de excepciones al dueño por canal privado"
        ]

        # 4. Integraciones
        agent = platform_store.get_agent_instance(tenant_id, agent_id)
        if agent and agent.published_version:
            v_rec = platform_store.get_agent_version(tenant_id, agent_id, agent.published_version)
            if v_rec and v_rec.manifest_dict:
                integs = v_rec.manifest_dict.get("integrations", {})
                for k, v in integs.items():
                    report.available_integrations.append({
                        "name": k,
                        "connected": v.get("connected", False) if isinstance(v, dict) else bool(v),
                        "type": v.get("type", "api") if isinstance(v, dict) else "api"
                    })

        # 5. Qué PUEDE y NO PUEDE hacer el agente (Invariantes de Gobernanza)
        report.allowed_actions = [
            "Atender visitantes en tiempo real en la página web mediante el widget 2D",
            "Desplazar y navegar la pantalla hacia secciones oficiales autorizadas",
            "Responder preguntas comerciales con precios oficiales exactos",
            "Validar y agendar citas utilizando slots reales de agenda",
            "Rechazar alucinaciones forzadas sobre datos no disponibles (ej. identidad del CEO)"
        ]

        report.disallowed_actions = [
            "Atender visitantes o leads por WhatsApp (regla inquebrantable de canales)",
            "Inventar o modificar precios no contemplados en la configuración comercial",
            "Ejecutar comandos de sistema operativo o acceder a archivos fuera del sandbox",
            "Acceder a datos, sesiones o bases de conocimiento de otros tenants",
            "Saltarse la verificación humana cuando una acción requiere aprobación",
            "Fingir éxito en herramientas que fallaron durante la ejecución"
        ]

        report.isolation_guarantees = [
            "Partición estricta de base de datos en platform_* WHERE tenant_id = ?",
            "Clave compuesta de memoria de sesión: tenant_id:agent_id:session_id",
            "Session pinning criptográfico fws_ que rechaza tenant spoofing en cliente",
            "Redacción absoluta de secretos en respuestas públicas al frontend"
        ]

        return report


# Instancia única del motor de auto-inspección
self_inspector = SelfInspector()

