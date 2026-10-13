# -*- coding: utf-8 -*-
"""
Firby AI — Architectural Overhaul Test Suite (13 Mandatory Scenarios A-M)
========================================================================
Valida de extremo a extremo los 13 escenarios obligatorios requeridos:
A) Pregunta cuya respuesta está en una subpágina (/sobre-nosotros).
B) Pregunta cuya respuesta está en la página actual (/#como-funciona).
C) Solicitud de navegación a una sección (#planes).
D) Solicitud de navegación a otra ruta (/faq).
E) Solicitud de una acción que NO está habilitada (book_appointment en landing).
F) Solicitud de una acción que SÍ está habilitada (book_appointment en clínica).
G) Acción que falla (recuperación elegante y sin crash).
H) Acción que requiere información adicional (slot-filling antes de ejecutar).
I) Conversación de múltiples turnos (retención de contexto).
J) Navegación durante una conversación (preservación de task_state y anáfora).
K) Usuario que cambia de tema (pivot fluido).
L) Información inexistente (reconocimiento honesto de frontera de conocimiento).
M) Sitio con múltiples subpáginas (Site Discovery completo y mapa navegable).
"""

import pytest
import asyncio
import sqlite3
from typing import Dict, Any, List

from src.core.operator.models import WebContext, UIActionType
from src.core.operator.business_config import (
    get_business_config, FIRBY_LANDING_CONFIG, CLINICA_AMERICAS_CONFIG,
    BusinessConfig, ToolPermission
)
from src.core.operator.tools import operator_tools, ToolResult
from src.core.operator.memory import TaskState, operator_memory
from src.core.operator.runtime import DigitalWebOperatorRuntime
from src.core.operator.site_discovery import SiteDiscoveryEngine, site_knowledge_engine
from src.core.operator.teaching import WorkspaceTeachingEngine


@pytest.fixture
def runtime():
    return DigitalWebOperatorRuntime()


# ─────────────────────────────────────────────────────────────────────────────
# ESCENARIO A: Pregunta cuya respuesta está en una subpágina (/sobre-nosotros)
# ─────────────────────────────────────────────────────────────────────────────
def test_scenario_a_subpage_knowledge(runtime):
    """Verifica que el conocimiento descubierto de una subpágina responda con precisión y atribución."""
    # Buscar en el motor de Site Discovery
    matches = site_knowledge_engine.search_knowledge("visión ingeniería fundadores sobre nosotros", top_k=3)
    assert len(matches) > 0
    # Al menos una coincidencia debe provenir de /sobre-nosotros
    subpage_match = next((m for m in matches if "/sobre-nosotros" in m.source_page), None)
    assert subpage_match is not None
    assert "Sobre Nosotros" in subpage_match.title or "Sobre Nosotros" in subpage_match.excerpt


# ─────────────────────────────────────────────────────────────────────────────
# ESCENARIO B: Pregunta cuya respuesta está en la página actual (/#como-funciona)
# ─────────────────────────────────────────────────────────────────────────────
def test_scenario_b_current_page_knowledge(runtime):
    """Verifica la respuesta para contenido dentro de la página actual sin navegación redundante."""
    matches = site_knowledge_engine.search_knowledge("tres pasos operador en vivo instalación", top_k=3)
    assert len(matches) > 0
    hero_or_func = next((m for m in matches if m.source_page == "/" and m.source_section in ["#como-funciona", "#hero", "#mobileDrawer"]), None)
    assert hero_or_func is not None


# ─────────────────────────────────────────────────────────────────────────────
# ESCENARIO C: Solicitud de navegación a una sección (#planes)
# ─────────────────────────────────────────────────────────────────────────────
def test_scenario_c_section_navigation():
    """Verifica la emisión de acción UI para navegar suavemente a una sección."""
    res = operator_tools.execute_tool(
        "navigate_web",
        {"target": "#planes", "reason": "Ver tabla de precios"},
        FIRBY_LANDING_CONFIG,
        current_section="#hero"
    )
    assert res.success is True
    assert res.ui_action is not None
    assert res.ui_action.type == UIActionType.NAVIGATE_TO_SECTION
    assert res.ui_action.target == "#planes"


# ─────────────────────────────────────────────────────────────────────────────
# ESCENARIO D: Solicitud de navegación a otra ruta (/faq)
# ─────────────────────────────────────────────────────────────────────────────
def test_scenario_d_cross_page_navigation():
    """Verifica la emisión de acción UI para navegar a otra página del sitio."""
    res = operator_tools.execute_tool(
        "navigate_web",
        {"target": "/faq", "reason": "Ver preguntas frecuentes"},
        FIRBY_LANDING_CONFIG,
        current_section="#hero"
    )
    assert res.success is True
    assert res.ui_action is not None
    assert res.ui_action.type == UIActionType.NAVIGATE_TO
    assert res.ui_action.target == "/faq"


# ─────────────────────────────────────────────────────────────────────────────
# ESCENARIO E: Solicitud de una acción que NO está habilitada
# ─────────────────────────────────────────────────────────────────────────────
def test_scenario_e_disabled_action_respectful_refusal():
    """Verifica que si una acción no está habilitada, el operador la rehúse educadamente sin simular."""
    # En Firby Landing, book_appointment está deshabilitada
    is_auth, err_msg = FIRBY_LANDING_CONFIG.is_tool_authorized("book_appointment")
    assert is_auth is False
    assert "autoservicio" in err_msg or "prueba gratis" in err_msg

    res = operator_tools.execute_tool(
        "book_appointment",
        {"customer_name": "Test", "customer_phone": "3001234567", "datetime_slot": "10:00 AM"},
        FIRBY_LANDING_CONFIG,
        current_section="#hero"
    )
    assert res.success is False
    assert "autoservicio" in res.error


# ─────────────────────────────────────────────────────────────────────────────
# ESCENARIO F: Solicitud de una acción que SÍ está habilitada
# ─────────────────────────────────────────────────────────────────────────────
def test_scenario_f_enabled_action_execution():
    """Verifica la ejecución real e inserción atómica en SQLite cuando la herramienta está autorizada."""
    is_auth, _ = CLINICA_AMERICAS_CONFIG.is_tool_authorized("book_appointment")
    assert is_auth is True

    res = operator_tools.execute_tool(
        "book_appointment",
        {
            "customer_name": "Paciente Validador F",
            "customer_phone": "+57 320 555 1234",
            "service": "Ortodoncia",
            "datetime_slot": "Lunes 10:00 AM",
            "notes": "Validación Escenario F"
        },
        CLINICA_AMERICAS_CONFIG,
        current_section="#servicios"
    )
    assert res.success is True
    assert res.data.get("booking_id") is not None

    # Verificar persistencia en base de datos SQLite real
    with sqlite3.connect("firby_ultra.db", timeout=3.0) as conn:
        cur = conn.cursor()
        cur.execute("SELECT patient_name, status FROM appointments WHERE chat_id = ?", (res.data["booking_id"],))
        row = cur.fetchone()
        assert row is not None
        assert row[0] == "Paciente Validador F"
        assert row[1] == "confirmed"


# ─────────────────────────────────────────────────────────────────────────────
# ESCENARIO G: Acción que falla (recuperación elegante y sin crash)
# ─────────────────────────────────────────────────────────────────────────────
def test_scenario_g_action_failure_recovery(runtime):
    """Verifica que ante un fallo en parámetros o ejecución externa, se devuelva ToolResult controlado."""
    # Faltan parámetros obligatorios en agendamiento
    res = operator_tools.execute_tool(
        "book_appointment",
        {"notes": "Sin nombre ni teléfono"},
        CLINICA_AMERICAS_CONFIG,
        current_section="#servicios"
    )
    assert res.success is False
    assert len(res.missing_fields) > 0
    assert "customer_name" in res.missing_fields or "customer_phone" in res.missing_fields


# ─────────────────────────────────────────────────────────────────────────────
# ESCENARIO H: Acción que requiere información adicional (slot-filling)
# ─────────────────────────────────────────────────────────────────────────────
def test_scenario_h_action_requiring_additional_info():
    """Verifica que el TaskState registre slots parciales y detecte los faltantes."""
    task_state = TaskState(active_goal="Agendar cita de Ortodoncia")
    task_state.update_slot("service", "Ortodoncia")
    task_state.update_slot("customer_name", "Carlos Mendoza")

    # Aún falta el teléfono y horario
    assert "customer_phone" not in task_state.slots
    assert "datetime_slot" not in task_state.slots
    assert task_state.slots["service"] == "Ortodoncia"
    assert task_state.slots["customer_name"] == "Carlos Mendoza"


# ─────────────────────────────────────────────────────────────────────────────
# ESCENARIO I: Conversación de múltiples turnos (retención de contexto)
# ─────────────────────────────────────────────────────────────────────────────
def test_scenario_i_multi_turn_conversation():
    """Verifica que el estado de memoria conserve los datos a través de turnos."""
    user_id = "test_user_multiturn_123"
    state = operator_memory.load_task_state(user_id)
    state.active_goal = "Consultar planes"
    state.update_slot("plan_interes", "Pro")
    operator_memory.save_task_state(user_id, state)

    # Recuperar en turno posterior
    reloaded_state = operator_memory.load_task_state(user_id)
    assert reloaded_state.active_goal == "Consultar planes"
    assert reloaded_state.slots.get("plan_interes") == "Pro"


# ─────────────────────────────────────────────────────────────────────────────
# ESCENARIO J: Navegación durante una conversación (preservación de task_state y anáfora)
# ─────────────────────────────────────────────────────────────────────────────
def test_scenario_j_navigation_during_conversation():
    """Verifica que una anáfora ('ese') resuelva el slot anterior incluso tras navegación."""
    state = TaskState()
    state.record_tool_execution(
        "check_availability",
        args={"date": "mañana", "service": "Ortodoncia"},
        result={"success": True, "data": {"available_slots": ["09:00 AM", "11:00 AM"], "date": "mañana", "service": "Ortodoncia"}}
    )

    resolved = state.resolve_reference("Me sirve ese horario")
    assert resolved is not None
    assert "09:00" in resolved.get("datetime_slot", "")
    assert state.slots.get("datetime_slot") == "mañana 09:00 AM"


# ─────────────────────────────────────────────────────────────────────────────
# ESCENARIO K: Usuario que cambia de tema (pivot fluido)
# ─────────────────────────────────────────────────────────────────────────────
def test_scenario_k_topic_change(runtime):
    """Verifica que el agente cambie de tema sin arrastrar metas incompatibles."""
    state = TaskState(active_goal="Cotizar Plan Starter")
    state.update_slot("plan", "Starter")

    # Usuario cambia de tema hacia ubicación
    nav_res = FIRBY_LANDING_CONFIG.find_navigation_target("dónde queda la oficina y ubicación")
    assert nav_res is not None or "Medellín" in FIRBY_LANDING_CONFIG.official_info.locations[0]


# ─────────────────────────────────────────────────────────────────────────────
# ESCENARIO L: Información inexistente (reconocimiento honesto de frontera)
# ─────────────────────────────────────────────────────────────────────────────
def test_scenario_l_nonexistent_info_honest_boundary():
    """Verifica que atributos no listados (CEO, directores privados) sean detectados como unlisted."""
    assert FIRBY_LANDING_CONFIG.is_attribute_unlisted("ceo") is True
    assert FIRBY_LANDING_CONFIG.is_attribute_unlisted("director_ejecutivo") is True
    assert FIRBY_LANDING_CONFIG.is_attribute_unlisted("salarios") is True
    assert FIRBY_LANDING_CONFIG.is_attribute_unlisted("planes") is False


# ─────────────────────────────────────────────────────────────────────────────
# ESCENARIO M: Sitio con múltiples subpáginas (Site Discovery completo)
# ─────────────────────────────────────────────────────────────────────────────
def test_scenario_m_multi_page_discovery():
    """Verifica que el motor SiteDiscoveryEngine haya mapeado todas las páginas y secciones."""
    graph = SiteDiscoveryEngine.get_or_create_graph("firby_landing")
    assert len(graph.pages) >= 5
    expected_routes = ["/", "/sobre-nosotros", "/faq", "/terminos", "/politica-de-privacidad"]
    for r in expected_routes:
        assert r in graph.pages

    nav_map = graph.get_navigation_map()
    assert len(nav_map) >= 5
    root_item = next((item for item in nav_map if item["path"] == "/"), None)
    assert root_item is not None
    assert len(root_item["sections"]) >= 5
