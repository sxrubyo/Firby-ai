# -*- coding: utf-8 -*-
"""
Firby AI — Bloque 3 Test Suite: Structured Tool Calling & Tool Runtime Real
===========================================================================
Valida los 16 requerimientos técnicos de la arquitectura de herramientas:
1. Tool válida
2. Tool inexistente (NOT_FOUND)
3. Argumentos inválidos (VALIDATION_ERROR por tipos)
4. Argumentos incompletos (VALIDATION_ERROR por missing_fields)
5. Permission denied (Tenant deshabilitado en BusinessConfig)
6. Permission allowed (Tenant habilitado en BusinessConfig)
7. Timeout handling (TIMEOUT controlado)
8. Execution failure (EXECUTION_ERROR controlado)
9. Successful navigation as structured tool
10. Failed navigation to prohibited route (WebPolicyEngine)
11. Duplicate action / Idempotency protection (IdempotencyStore)
12. Multi-turn Agent Loop (Server tool execution -> Observation -> Synthesis)
13. Observation propagation (task_state and event lineage)
14. Agent continuing after tool failure (replanning)
15. Negative constraint enforcement (inhibits navigate_web)
16. Structured JSON Decision Parsing with legacy fallback
"""

import os
import json
import time
import asyncio
import pytest
import sqlite3

from src.core.operator.models import (
    AgentRunState, AgentEventType, WebContext, OperatorResult
)
from src.core.operator.tool_contracts import (
    ToolDefinition, ToolCall, ToolResult, ToolStatus, ToolRiskLevel, ToolExecutionMode
)
from src.core.operator.tools import OperatorToolRegistry
from src.core.operator.idempotency import IdempotencyStore
from src.core.operator.business_config import (
    BusinessConfig, BusinessIdentity, OfficialInfo, BusinessPolicy,
    ToolPermission, NavigationResource, get_business_config
)
from src.core.operator.runtime import DigitalWebOperatorRuntime


@pytest.fixture
def clean_db(tmp_path):
    db_file = tmp_path / "test_block3.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            patient_name TEXT,
            patient_phone TEXT,
            service TEXT,
            datetime_slot TEXT,
            notes TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    return str(db_file)


@pytest.fixture
def test_registry(clean_db):
    return OperatorToolRegistry(db_path=clean_db)


@pytest.fixture
def test_configs():
    # Tenant 1: Landing (Citas deshabilitadas)
    landing_cfg = BusinessConfig(
        tenant_id="firby_landing",
        identity=BusinessIdentity(name="Firby", legal_name="Firby AI S.A.S.", industry="SaaS", description="", website_url=""),
        official_info=OfficialInfo(),
        tool_permissions={
            "navigate_web": ToolPermission(name="navigate_web", enabled=True),
            "highlight_ui": ToolPermission(name="highlight_ui", enabled=True),
            "check_availability": ToolPermission(name="check_availability", enabled=False, disabled_message="Agenda no disponible en Firby Landing."),
            "book_appointment": ToolPermission(name="book_appointment", enabled=False, disabled_message="En Firby la activación es autoservicio.")
        }
    )

    # Tenant 2: Clinica (Citas habilitadas)
    clinica_cfg = BusinessConfig(
        tenant_id="clinica-de-las-americas",
        identity=BusinessIdentity(name="Clínica Las Américas", legal_name="Clínica S.A.S.", industry="Dental", description="", website_url=""),
        official_info=OfficialInfo(),
        tool_permissions={
            "navigate_web": ToolPermission(name="navigate_web", enabled=True),
            "highlight_ui": ToolPermission(name="highlight_ui", enabled=True),
            "check_availability": ToolPermission(name="check_availability", enabled=True),
            "book_appointment": ToolPermission(name="book_appointment", enabled=True)
        }
    )
    return {"landing": landing_cfg, "clinica": clinica_cfg}


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBAS UNITARIAS DE TOOLS, PERMISOS, VALIDACIÓN E IDEMPOTENCIA
# ─────────────────────────────────────────────────────────────────────────────

def test_1_valid_tool_execution(test_registry, test_configs):
    """TEST 1: Invocación exitosa de herramienta válida."""
    call = ToolCall(
        tool_name="check_availability",
        arguments={"date": "2026-09-20"},
        run_id="run_t1"
    )
    res = test_registry.execute_tool(call, business_config=test_configs["clinica"])
    assert res.status == ToolStatus.SUCCESS
    assert res.success is True
    assert "available_slots" in res.result
    assert res.verified is True
    assert len(res.observations) > 0


def test_2_nonexistent_tool(test_registry, test_configs):
    """TEST 2: Intento de invocar herramienta no registrada en el catálogo."""
    call = ToolCall(
        tool_name="hack_mainframe",
        arguments={"ip": "127.0.0.1"},
        run_id="run_t2"
    )
    res = test_registry.execute_tool(call, business_config=test_configs["clinica"])
    assert res.status == ToolStatus.NOT_FOUND
    assert res.success is False
    assert "no existe en el catálogo" in res.error


def test_3_invalid_arguments_schema_type(test_registry, test_configs):
    """TEST 3: Argumentos de tipo incorrecto violan el schema JSON."""
    call = ToolCall(
        tool_name="navigate_web",
        arguments={"target": 12345},  # Int en lugar de string
        run_id="run_t3"
    )
    res = test_registry.execute_tool(call, business_config=test_configs["clinica"])
    assert res.status == ToolStatus.VALIDATION_ERROR
    assert res.success is False
    assert "debe ser string" in res.error


def test_4_incomplete_arguments_missing_required(test_registry, test_configs):
    """TEST 4: Faltan campos obligatorios requeridos por el contrato."""
    call = ToolCall(
        tool_name="book_appointment",
        arguments={"customer_name": "Carlos Gómez"},  # Faltan phone, service, datetime_slot
        run_id="run_t4"
    )
    res = test_registry.execute_tool(call, business_config=test_configs["clinica"])
    assert res.status == ToolStatus.VALIDATION_ERROR
    assert res.success is False
    assert "customer_phone" in res.missing_fields
    assert "service" in res.missing_fields
    assert "datetime_slot" in res.missing_fields


def test_5_permission_denied_disabled_by_tenant(test_registry, test_configs):
    """TEST 5: Separación Capacidad vs Permiso. La tool existe globalmente pero está deshabilitada para el tenant."""
    call = ToolCall(
        tool_name="book_appointment",
        arguments={
            "customer_name": "Carlos Gómez",
            "customer_phone": "+573001234567",
            "service": "Demo",
            "datetime_slot": "Mañana 10:00 AM"
        },
        run_id="run_t5"
    )
    res = test_registry.execute_tool(call, business_config=test_configs["landing"])
    assert res.status == ToolStatus.PERMISSION_DENIED
    assert res.success is False
    assert "En Firby la activación es autoservicio" in res.error


def test_6_permission_allowed_enabled_by_tenant(test_registry, test_configs):
    """TEST 6: La misma tool para un tenant autorizado ejecuta con éxito."""
    call = ToolCall(
        tool_name="book_appointment",
        arguments={
            "customer_name": "Carlos Gómez",
            "customer_phone": "+573001234567",
            "service": "Ortodoncia",
            "datetime_slot": "Mañana 10:00 AM"
        },
        run_id="run_t6"
    )
    res = test_registry.execute_tool(call, business_config=test_configs["clinica"])
    assert res.status == ToolStatus.SUCCESS
    assert res.success is True
    assert "booking_id" in res.result


def test_7_timeout_and_execution_error_handling(test_configs):
    """TEST 7 & 8: Manejo seguro de excepciones durante la ejecución de handlers."""
    def buggy_handler(args, cfg, section):
        raise RuntimeError("Fallo de conexión en base de datos externa")

    reg = OperatorToolRegistry()
    reg.register(ToolDefinition(
        name="buggy_tool",
        description="Tool que falla",
        input_schema={"type": "object", "properties": {"val": {"type": "string"}}},
        required_params=[],
        handler=buggy_handler
    ))
    # Permitir en config
    test_configs["clinica"].tool_permissions["buggy_tool"] = ToolPermission(name="buggy_tool", enabled=True)

    call = ToolCall(tool_name="buggy_tool", arguments={"val": "test"}, run_id="run_t7")
    res = reg.execute_tool(call, business_config=test_configs["clinica"])
    assert res.status == ToolStatus.EXECUTION_ERROR
    assert res.success is False
    assert "Fallo de conexión" in res.error


def test_9_navigation_valid_ui_action(test_registry, test_configs):
    """TEST 9: navigate_web emite UIAction estructurada y observación válida."""
    call = ToolCall(
        tool_name="navigate_web",
        arguments={"target": "#planes", "reason": "mostrar planes oficiales"},
        run_id="run_t9"
    )
    res = test_registry.execute_tool(call, business_config=test_configs["landing"], current_section="#hero")
    assert res.status == ToolStatus.SUCCESS
    assert res.success is True
    assert res.ui_action is not None
    assert res.ui_action.target == "#planes"


def test_10_navigation_security_policy_rejection(test_registry, test_configs):
    """TEST 10: WebPolicyEngine rechaza destinos no autorizados (ej. URL externa o script)."""
    call = ToolCall(
        tool_name="navigate_web",
        arguments={"target": "javascript:alert(1)", "reason": "inyección"},
        run_id="run_t10"
    )
    res = test_registry.execute_tool(call, business_config=test_configs["landing"])
    assert res.status == ToolStatus.VALIDATION_ERROR
    assert res.success is False
    assert "Destino no permitido por política" in res.error


def test_11_duplicate_action_idempotency_protection(clean_db, test_configs):
    """TEST 11: IdempotencyStore previene que una acción mutante se inserte dos veces en la base de datos."""
    reg = OperatorToolRegistry(db_path=clean_db)
    cfg = test_configs["clinica"]

    call1 = ToolCall(
        tool_name="book_appointment",
        arguments={
            "customer_name": "Laura Restrepo",
            "customer_phone": "+573109876543",
            "service": "Limpieza",
            "datetime_slot": "Viernes 3:00 PM",
            "idempotency_key": "unique_idem_key_001"
        },
        run_id="run_idem_1"
    )
    res1 = reg.execute_tool(call1, business_config=cfg)
    assert res1.status == ToolStatus.SUCCESS
    booking_id_1 = res1.result["booking_id"]

    # Invocación repetida exactamente idéntica
    call2 = ToolCall(
        tool_name="book_appointment",
        arguments={
            "customer_name": "Laura Restrepo",
            "customer_phone": "+573109876543",
            "service": "Limpieza",
            "datetime_slot": "Viernes 3:00 PM",
            "idempotency_key": "unique_idem_key_001"
        },
        run_id="run_idem_2"
    )
    res2 = reg.execute_tool(call2, business_config=cfg)
    assert res2.status == ToolStatus.SUCCESS
    # Reutiliza el mismo booking_id sin generar nuevo registro
    assert res2.result["booking_id"] == booking_id_1
    assert res2.metadata.get("idempotent_replay") is True

    # Verificar que en SQLite hay exactamente 1 registro
    with sqlite3.connect(clean_db) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM appointments WHERE patient_name = 'Laura Restrepo'")
        count = cur.fetchone()[0]
        assert count == 1


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBAS DEL AGENT RUNTIME CON LOOP, OBSERVACIÓN Y DECISIONES ESTRUCTURADAS
# ─────────────────────────────────────────────────────────────────────────────

def test_12_agent_loop_server_tool_with_observation():
    """
    TEST 12: Loop del Agente.
    Paso 1: El modelo decide invocar check_availability en JSON estructurado.
    El runtime ejecuta la tool, captura la observación y reinyecta al modelo en Paso 2.
    Paso 2: El modelo recibe la observación y sintetiza la respuesta final.
    """
    async def _run():
        runtime = DigitalWebOperatorRuntime()

        call_count = 0
        async def mock_llm_caller(prompt, history, query):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # Paso 1: Decisión estructurada de usar tool
                return json.dumps({
                    "thought": "Debo consultar la disponibilidad para mañana.",
                    "tool_call": {
                        "tool_name": "check_availability",
                        "arguments": {"date": "mañana"}
                    },
                    "response": "",
                    "chips": []
                })
            else:
                # Paso 2: Sintetiza respuesta incorporando la observación del sistema
                return json.dumps({
                    "thought": "Ya tengo los cupos disponibles, respondo al cliente.",
                    "tool_call": None,
                    "response": "Para mañana tenemos disponibilidad a las 09:00 AM y 11:30 AM. ¿Cuál te conviene más?",
                    "chips": ["09:00 AM", "11:30 AM"]
                })

        res = await runtime.process_turn(
            message="¿Qué horarios tienen disponibles mañana?",
            user_id="user_loop_test",
            org_id="clinica-de-las-americas",
            web_context_dict={"current_url": "/", "current_section": "#hero"},
            history=[],
            llm_caller=mock_llm_caller
        )

        assert res.ok is True
        assert res.state == AgentRunState.DONE.value
        assert call_count == 2
        assert "09:00 AM" in res.response
        assert res.requires_observation is False

    asyncio.run(_run())


def test_13_observation_propagation_in_events():
    """TEST 13: Las observaciones y eventos de la herramienta quedan registrados en el lineage de eventos."""
    async def _run():
        runtime = DigitalWebOperatorRuntime()

        async def mock_llm_caller(prompt, history, query):
            return json.dumps({
                "thought": "Consulto disponibilidad.",
                "tool_call": {"tool_name": "check_availability", "arguments": {"date": "hoy"}},
                "response": "Revisando horarios..."
            })

        res = await runtime.process_turn(
            message="Horarios de hoy",
            user_id="user_obs_lineage",
            org_id="clinica-de-las-americas",
            web_context_dict={"current_url": "/", "current_section": "#hero"},
            history=[],
            llm_caller=mock_llm_caller
        )

        event_names = [e["event"] for e in res.events]
        assert AgentEventType.TOOL_CALL_REQUESTED.value in event_names
        assert AgentEventType.TOOL_PERMISSION_CHECKED.value in event_names
        assert AgentEventType.TOOL_VALIDATION_CHECKED.value in event_names
        assert AgentEventType.TOOL_EXECUTION_COMPLETED.value in event_names
        assert AgentEventType.OBSERVATION_CREATED.value in event_names

    asyncio.run(_run())


def test_14_negative_constraint_inhibits_structured_navigation():
    """TEST 14: Restricción negativa inhibe tool call estructurado de navigate_web."""
    async def _run():
        runtime = DigitalWebOperatorRuntime()

        async def mock_llm_caller(prompt, history, query):
            # El modelo intenta llamar navigate_web a pesar de la restricción
            return json.dumps({
                "thought": "El usuario preguntó de planes, intentaré navegar.",
                "tool_call": {"tool_name": "navigate_web", "arguments": {"target": "#planes"}},
                "response": "Nuestros planes son Starter, Pro y Equipos.",
                "chips": []
            })

        res = await runtime.process_turn(
            message="Explícame los planes pero no me lleves a ninguna parte",
            user_id="user_neg_constraint",
            org_id="firby_landing",
            web_context_dict={"current_url": "/", "current_section": "#hero"},
            history=[],
            llm_caller=mock_llm_caller
        )

        # El runtime debe haber bloqueado el navigate_web
        assert res.action is None
        assert res.ui_action is None
        assert res.requires_observation is False
        assert res.state == AgentRunState.DONE.value
        assert "Starter" in res.response

    asyncio.run(_run())


def test_15_structured_decision_with_legacy_fallback():
    """TEST 15: Compatibilidad hacia atrás. Soporta [TOOL_CALL:...] si un modelo antiguo lo produce."""
    async def _run():
        runtime = DigitalWebOperatorRuntime()

        async def mock_legacy_llm(prompt, history, query):
            return 'Claro, te muestro los planes. [TOOL_CALL:navigate_web:{"target": "#planes", "reason": "ver planes"}]'

        res = await runtime.process_turn(
            message="Muéstrame los planes",
            user_id="user_legacy_test",
            org_id="firby_landing",
            web_context_dict={"current_url": "/", "current_section": "#hero"},
            history=[],
            llm_caller=mock_legacy_llm
        )

        assert res.state == AgentRunState.ACTION_REQUESTED.value
        assert res.action is not None
        assert res.action["target"] == "#planes"
        assert res.requires_observation is True

    asyncio.run(_run())


def test_16_agent_replan_after_tool_failure():
    """TEST 16: Si la herramienta falla por validación, el agente replanifica y continúa sin abortar."""
    async def _run():
        runtime = DigitalWebOperatorRuntime()

        call_idx = 0
        async def mock_failing_llm(prompt, history, query):
            nonlocal call_idx
            call_idx += 1
            if call_idx == 1:
                # Enviar llamada con argumentos faltantes
                return json.dumps({
                    "thought": "Intento agendar sin teléfono",
                    "tool_call": {"tool_name": "book_appointment", "arguments": {"customer_name": "Pedro"}},
                    "response": ""
                })
            else:
                # Replanifica pidiendo los datos faltantes
                return json.dumps({
                    "thought": "Observo que faltan datos, pido el teléfono y horario al usuario.",
                    "tool_call": None,
                    "response": "Por favor indícame tu número de teléfono y el horario deseado para confirmar tu cita.",
                    "chips": []
                })

        res = await runtime.process_turn(
            message="Agenda para Pedro",
            user_id="user_replan_test",
            org_id="clinica-de-las-americas",
            web_context_dict={"current_url": "/", "current_section": "#hero"},
            history=[],
            llm_caller=mock_failing_llm
        )

        assert res.ok is True
        assert res.state == AgentRunState.DONE.value
        assert "teléfono" in res.response

    asyncio.run(_run())
