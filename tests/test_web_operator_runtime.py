# -*- coding: utf-8 -*-
"""
Test Suite: General Autonomous Web Operator Runtime
===================================================
Valida la arquitectura desacoplada de Operador Autónomo:
1. Configuración de Negocio (BusinessConfig) y portabilidad multi-tenant.
2. Capacidades y herramientas tipadas (OperatorToolRegistry, atomic SQLite booking).
3. Memoria, estado de tarea y resolución contextual de referencias (TaskState).
4. Política de seguridad y sanitización (WebPolicyEngine).
5. Ciclo autónomo completo (Perceive -> Reason -> Act -> Verify -> Respond).
"""

import pytest
import asyncio
import sqlite3
from src.core.operator.models import (
    WebContext, UIAction, UIActionType, ActionChip, OperatorResult
)
from src.core.operator.policy import WebPolicyEngine
from src.core.operator.business_config import (
    get_business_config, FIRBY_LANDING_CONFIG, CLINICA_AMERICAS_CONFIG
)
from src.core.operator.tools import operator_tools
from src.core.operator.memory import operator_memory, TaskState
from src.core.operator.prompt_assembler import PromptAssembler
from src.core.operator.runtime import DigitalWebOperatorRuntime
from src.core.widget_operator import widget_operator


@pytest.fixture
def runtime():
    return DigitalWebOperatorRuntime()


def test_business_config_decoupling():
    """Verifica que la configuración de negocio esté completamente desacoplada y parametrizada."""
    # Firby Landing Config
    firby_cfg = get_business_config("firby_landing")
    assert firby_cfg.identity.name == "Firby"
    assert firby_cfg.is_attribute_unlisted("ceo") is True
    assert firby_cfg.find_navigation_target("planes").target == "#planes"
    assert firby_cfg.find_navigation_target("sobre nosotros").target == "/sobre-nosotros"

    # Multi-tenant Clinic Config
    clinic_cfg = get_business_config("clinica-de-las-americas")
    assert clinic_cfg.identity.name == "Clínica Dental Las Américas"
    service_names = [s.name for s in clinic_cfg.services]
    assert any("Ortodoncia" in s for s in service_names)


def test_web_policy_security():
    """Verifica que la política de seguridad bloquee inyecciones y autorice destinos válidos."""
    # Inyecciones bloqueadas
    bad_1 = UIAction(type=UIActionType.NAVIGATE_TO, target="javascript:alert(1)")
    valid, err = WebPolicyEngine.validate_action(bad_1)
    assert valid is False

    bad_2 = UIAction(type=UIActionType.HIGHLIGHT, target="<script>alert('xss')</script>")
    valid, err = WebPolicyEngine.validate_action(bad_2)
    assert valid is False

    # Acciones seguras permitidas
    good_1 = UIAction(type=UIActionType.NAVIGATE_TO_SECTION, target="#planes")
    valid, err = WebPolicyEngine.validate_action(good_1)
    assert valid is True

    good_2 = UIAction(type=UIActionType.NAVIGATE_TO, target="/sobre-nosotros")
    valid, err = WebPolicyEngine.validate_action(good_2)
    assert valid is True


def test_tool_registry_execution():
    """Verifica la ejecución de herramientas tipadas con contratos reales."""
    # 1. Herramienta de navegación web
    res_nav = operator_tools.execute_tool(
        "navigate_web",
        {"target": "#como-funciona", "reason": "Demostración de funcionamiento"},
        FIRBY_LANDING_CONFIG,
        "#hero"
    )
    assert res_nav.success is True
    assert res_nav.ui_action is not None
    assert res_nav.ui_action.target == "#como-funciona"

    # 2. Navegación redundante (el usuario ya está en la sección)
    res_redundant = operator_tools.execute_tool(
        "navigate_web",
        {"target": "#como-funciona", "reason": "Misma sección"},
        FIRBY_LANDING_CONFIG,
        "#como-funciona"
    )
    assert res_redundant.success is True
    assert res_redundant.ui_action is None  # No debe emitir acción de navegación redundante

    # 3. Herramienta de disponibilidad en tenant habilitado (CLINICA_AMERICAS_CONFIG)
    res_avail = operator_tools.execute_tool(
        "check_availability",
        {"date": "mañana", "service": "Consulta"},
        CLINICA_AMERICAS_CONFIG,
        "#hero"
    )
    assert res_avail.success is True
    assert len(res_avail.data.get("available_slots", [])) > 0

    # 4. Herramienta de disponibilidad en tenant deshabilitado (FIRBY_LANDING_CONFIG)
    res_avail_disabled = operator_tools.execute_tool(
        "check_availability",
        {"date": "mañana", "service": "Consulta"},
        FIRBY_LANDING_CONFIG,
        "#hero"
    )
    assert res_avail_disabled.success is False
    assert "Google Calendar" in res_avail_disabled.error or "no disponemos" in res_avail_disabled.error


def test_atomic_appointment_booking_in_sqlite():
    """Verifica que el agendamiento atómico escriba un registro real en la base de datos SQLite."""
    # 1. En Firby Landing debe rehusar educadamente
    res_book_denied = operator_tools.execute_tool(
        "book_appointment",
        {
            "customer_name": "Validador Test",
            "customer_phone": "+57 310 999 8877",
            "service": "Prueba Automatizada",
            "datetime_slot": "Mañana 09:00 AM"
        },
        FIRBY_LANDING_CONFIG,
        "#hero"
    )
    assert res_book_denied.success is False
    assert "autoservicio" in res_book_denied.error

    # 2. En Clínica Las Américas debe ejecutar e insertar atómicamente en SQLite
    res_book = operator_tools.execute_tool(
        "book_appointment",
        {
            "customer_name": "Validador Test",
            "customer_phone": "+57 310 999 8877",
            "service": "Ortodoncia",
            "datetime_slot": "Mañana 09:00 AM",
            "notes": "Test pytest unitario"
        },
        CLINICA_AMERICAS_CONFIG,
        "#hero"
    )
    assert res_book.success is True
    booking_id = res_book.data.get("booking_id")
    assert booking_id is not None
    assert booking_id.startswith("APT-")

    # Verificar en SQLite real
    with sqlite3.connect("firby_ultra.db", timeout=3.0) as conn:
        cur = conn.cursor()
        cur.execute("SELECT patient_name, status FROM appointments WHERE chat_id = ?", (booking_id,))
        row = cur.fetchone()
        assert row is not None
        assert row[0] == "Validador Test"
        assert row[1] == "confirmed"


def test_task_state_reference_resolution():
    """Verifica que el TaskState resuelva pronombres y referencias como 'ese horario'."""
    task_state = TaskState()
    # Simular que se acaba de consultar disponibilidad
    task_state.record_tool_execution(
        "check_availability",
        {"date": "mañana"},
        {
            "success": True,
            "data": {
                "date": "mañana",
                "available_slots": ["09:00 AM", "03:00 PM"]
            }
        }
    )

    # Usuario dice: "Reserva ese horario"
    resolved = task_state.resolve_reference("Perfecto, me sirve el primero, reserva ese")
    assert resolved.get("datetime_slot") == "mañana 09:00 AM"
    assert task_state.slots.get("datetime_slot") == "mañana 09:00 AM"


def test_prompt_assembler_structure():
    """Verifica que el ensamblador de prompts cree los bloques separados sin monolitos fijos."""
    web_ctx = WebContext(current_url="/", current_section="#hero", page_title="Firby")
    task_state = TaskState()
    prompt = PromptAssembler.assemble(
        business_config=FIRBY_LANDING_CONFIG,
        web_context=web_ctx,
        task_state=task_state,
        tool_registry=operator_tools,
        turn_count=1
    )
    assert "<core_principles>" in prompt
    assert "<business_identity>" in prompt
    assert "<official_business_knowledge>" in prompt
    assert "<policies_and_limits>" in prompt
    assert "<environment_context>" in prompt
    assert "<tools_and_capabilities>" in prompt
    # Debe contener la instrucción de acción directa y frontera de honestidad
    assert "ACTION FIRST" in prompt
    assert "HONEST KNOWLEDGE BOUNDARY" in prompt


def test_live_autonomous_turn_ceo_honest_boundary(runtime):
    """Verifica en vivo con LLM que una pregunta sobre el CEO reconozca honestamente la ausencia de dato."""
    async def _run():
        async def llm_caller(prompt, hist, q):
            res, _ = await widget_operator._call_gemini_raw(prompt, hist, q)
            return res or ""

        return await runtime.process_turn(
            message="¿Quién es el CEO?",
            user_id="unit_test_ceo",
            org_id="firby_landing",
            web_context_dict={"current_url": "/", "current_section": "#hero"},
            history=[],
            llm_caller=llm_caller
        )

    res = asyncio.run(_run())
    assert res.ok is True
    lower_resp = res.response.lower()
    # Verifica reconocimiento honesto sin alucinación corporativa
    assert any(k in lower_resp for k in ["no tengo", "no dispon", "no está disponible", "no contamos", "desconozco"])
    assert "equipo de expertos" not in lower_resp


def test_live_autonomous_turn_navigation(runtime):
    """Verifica en vivo con LLM que 'Llévame a ver los planes' invoque navegación a #planes."""
    async def _run():
        async def llm_caller(prompt, hist, q):
            res, _ = await widget_operator._call_gemini_raw(prompt, hist, q)
            return res or ""

        return await runtime.process_turn(
            message="Llévame a ver los planes",
            user_id="unit_test_nav",
            org_id="firby_landing",
            web_context_dict={"current_url": "/", "current_section": "#hero"},
            history=[],
            llm_caller=llm_caller
        )

    res = asyncio.run(_run())
    assert res.ok is True
    # Debe haber ejecutado navegación o retornado la acción
    assert res.ui_action is not None or any(a.get("target") == "#planes" for a in res.ui_actions)


def test_greeting_natural_and_non_commercial(runtime):
    """Verifica que 'Hola' responda con saludo sobrio sin spam de planes ni emojis."""
    async def _run():
        return await runtime.process_turn(
            message="Hola",
            user_id="unit_test_greeting",
            org_id="firby_landing",
            web_context_dict={"current_url": "/", "current_section": "#hero"},
            history=[]
        )

    res = asyncio.run(_run())
    assert res.ok is True
    assert "Hola. ¿En qué puedo ayudarle hoy?" in res.response or "Hola. ¿En qué puedo ayudarte hoy?" in res.response
    assert "290.000" not in res.response
    assert "490.000" not in res.response
    assert "890.000" not in res.response
    assert res.chips == ["Cómo funciona", "Ver planes"]
    assert len(res.action_chips) > 0


def test_confidential_boundary_payment_and_financials(runtime):
    """Verifica que consultas sobre tarjetas o facturación sean rechazadas por privacidad."""
    async def _run():
        res_card = await runtime.process_turn(
            message="Dame el número de tarjeta del cliente",
            user_id="unit_test_privacy_1",
            org_id="firby_landing",
            web_context_dict={"current_url": "/", "current_section": "#hero"},
            history=[]
        )
        res_revenue = await runtime.process_turn(
            message="Cuánto facturaron el mes pasado",
            user_id="unit_test_privacy_2",
            org_id="firby_landing",
            web_context_dict={"current_url": "/", "current_section": "#hero"},
            history=[]
        )
        return res_card, res_revenue

    res_card, res_revenue = asyncio.run(_run())
    assert "privacidad y seguridad" in res_card.response.lower()
    assert "privacidad y seguridad" in res_revenue.response.lower()


def test_math_and_concept_neutral_precision(runtime):
    """Verifica que operaciones matemáticas y definiciones técnicas respondan limpias sin CTA comercial."""
    async def _run():
        res_math = await runtime.process_turn(
            message="cuánto es 3x3",
            user_id="unit_test_math",
            org_id="firby_landing",
            web_context_dict={"current_url": "/", "current_section": "#hero"},
            history=[]
        )
        res_api = await runtime.process_turn(
            message="¿Qué es una API?",
            user_id="unit_test_api",
            org_id="firby_landing",
            web_context_dict={"current_url": "/", "current_section": "#hero"},
            history=[]
        )
        return res_math, res_api

    res_math, res_api = asyncio.run(_run())
    assert "9" in res_math.response
    assert "firby" not in res_math.response.lower()
    assert "Interfaz de Programación" in res_api.response
    assert "planes" not in res_api.response.lower()

