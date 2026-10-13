# -*- coding: utf-8 -*-
"""
Firby AI — Bloque 1 Test Suite
==============================
Sincronización Estricta de Eventos y Eliminación de Navegación/Acciones Prematuras
(Frontera Agent Runtime <-> Agent Surface)

Pruebas obligatorias:
- TEST 1: 'Muéstrame los planes.' -> thinking (página NO se mueve) -> decision -> action_requested -> navigation -> observation -> verification -> response.
- TEST 2: '¿Cuánto cuesta Pro?' -> direct response, NO navigation.
- TEST 3: 'Explícame los planes pero no me lleves a ninguna parte.' -> explanation response, NO navigation (negative constraint obeyed).
- TEST 4: '3x3' -> 9, NO navigation, NO promotion, NO artificial CTA.
- TEST 5: 'Quiero agendar una cita.' -> asks for missing slots or explains policy, does not invent action.
- TEST 6: Tool/action fails -> ACTION_FAILED -> OBSERVATION -> runtime replans, NOT marked DONE just because requested.
- TEST 7: Ciclo HTTP completo vía /api/widget/chat y /api/widget/observe.
"""

import pytest
import asyncio
from src.core.operator.models import (
    WebContext, UIAction, UIActionType, OperatorResult,
    AgentRunState, AgentEventType, AgentEvent, ActionObservation
)
from src.core.operator.intent_classifier import IntentClassifier, UserIntentType
from src.core.operator.runtime import DigitalWebOperatorRuntime
from src.core.widget_operator import widget_operator
from starlette.testclient import TestClient
from src.interfaces.web.app import app


@pytest.fixture
def runtime():
    return DigitalWebOperatorRuntime()


# ═══════════════════════════════════════════════════════════════════════════
# TEST 1: "Muéstrame los planes."
# ═══════════════════════════════════════════════════════════════════════════
def test_1_explicit_navigation_flow(runtime):
    """
    TEST 1:
    Usuario: 'Muéstrame los planes.'
    - Runtime emite ACTION_REQUESTED con target #planes y requires_observation=True.
    - La respuesta textual se retiene (bubbles vacío) para no hablar antes de actuar.
    - Frontend ejecuta la acción en la UI y envía la observación.
    - Runtime verifica la observación y entrega la respuesta final contextual (DONE).
    """
    async def _run():
        user_query = "Muéstrame los planes."
        user_id = "test_user_t1"
        run_id = "run_test_1"

        # Fase 1: Solicitud inicial
        res_phase1 = await runtime.process_turn(
            message=user_query,
            user_id=user_id,
            org_id="firby_landing",
            run_id=run_id
        )

        # Verificaciones de fase 1
        assert res_phase1.ok is True
        assert res_phase1.run_id == run_id
        assert res_phase1.state == AgentRunState.ACTION_REQUESTED.value
        assert res_phase1.requires_observation is True
        assert res_phase1.action is not None
        assert res_phase1.action.get("target") == "#planes"
        # La respuesta en texto no se muestra antes de verificar la navegación
        assert res_phase1.response == ""
        assert len(res_phase1.bubbles) == 0

        # Eventos emitidos en fase 1
        event_names = [e["event"] for e in res_phase1.events]
        assert AgentEventType.MESSAGE_RECEIVED.value in event_names
        assert AgentEventType.THINKING_STARTED.value in event_names
        assert AgentEventType.DECISION_CREATED.value in event_names
        assert AgentEventType.ACTION_REQUESTED.value in event_names

        # Fase 2: Simulación de ejecución en UI y reporte de observación
        observation = {
            "run_id": run_id,
            "step_id": 1,
            "status": "section_reached",
            "target": "#planes",
            "success": True
        }

        res_phase2 = await runtime.process_observation(
            run_id=run_id,
            observation_dict=observation,
            user_id=user_id,
            org_id="firby_landing"
        )

        # Verificaciones de fase 2
        assert res_phase2.ok is True
        assert res_phase2.run_id == run_id
        assert res_phase2.state == AgentRunState.DONE.value
        assert res_phase2.requires_observation is False
        assert len(res_phase2.bubbles) > 0
        assert "Planes y Precios" in res_phase2.response
        assert "Starter" in res_phase2.response
        assert "Pro" in res_phase2.response
        assert "Equipos" in res_phase2.response

        # Eventos de verificación
        event_names_p2 = [e["event"] for e in res_phase2.events]
        assert AgentEventType.OBSERVATION_CREATED.value in event_names_p2
        assert AgentEventType.VERIFICATION_STARTED.value in event_names_p2
        assert AgentEventType.VERIFICATION_COMPLETED.value in event_names_p2
        assert AgentEventType.RUN_COMPLETED.value in event_names_p2

    asyncio.run(_run())


# ═══════════════════════════════════════════════════════════════════════════
# TEST 2: "¿Cuánto cuesta Pro?"
# ═══════════════════════════════════════════════════════════════════════════
def test_2_pricing_inquiry_no_navigation(runtime):
    """
    TEST 2:
    Usuario: '¿Cuánto cuesta Pro?'
    - El agente responde directamente el precio del Plan Pro ($490.000 COP/mes).
    - CERO navegación o salto de pantalla (action=None, ui_action=None).
    - Estado directo: DONE.
    """
    async def _run():
        user_query = "¿Cuánto cuesta Pro?"
        user_id = "test_user_t2"

        res = await runtime.process_turn(
            message=user_query,
            user_id=user_id,
            org_id="firby_landing"
        )

        assert res.ok is True
        assert res.state == AgentRunState.DONE.value
        assert res.requires_observation is False
        assert res.action is None
        assert res.ui_action is None
        assert len(res.ui_actions) == 0

        # Contenido de la respuesta
        assert "490.000" in res.response
        assert "Plan Pro" in res.response

        # Eventos emitidos
        event_names = [e["event"] for e in res.events]
        assert AgentEventType.ACTION_REQUESTED.value not in event_names
        assert AgentEventType.RUN_COMPLETED.value in event_names

    asyncio.run(_run())


# ═══════════════════════════════════════════════════════════════════════════
# TEST 3: "Explícame los planes pero no me lleves a ninguna parte."
# ═══════════════════════════════════════════════════════════════════════════
def test_3_negative_navigation_constraint(runtime):
    """
    TEST 3:
    Usuario: 'Explícame los planes pero no me lleves a ninguna parte.'
    - Obedece la restricción negativa del usuario ('no me lleves').
    - El clasificador detecta has_negative_navigation_constraint=True.
    - CERO navegación o scroll (action=None, ui_action=None).
    - Explica los planes directamente en texto sobrio.
    """
    async def _run():
        user_query = "Explícame los planes pero no me lleves a ninguna parte."
        user_id = "test_user_t3"

        # Clasificador cognitivo
        classification = IntentClassifier.classify(user_query)
        assert classification.has_negative_navigation_constraint is True
        assert classification.intent == UserIntentType.BUSINESS_PRICING
        assert classification.target_navigation is None

        # Ejecución del runtime
        res = await runtime.process_turn(
            message=user_query,
            user_id=user_id,
            org_id="firby_landing"
        )

        assert res.ok is True
        assert res.state == AgentRunState.DONE.value
        assert res.requires_observation is False
        assert res.action is None
        assert res.ui_action is None
        assert len(res.ui_actions) == 0
        assert "Starter" in res.response
        assert "Pro" in res.response
        assert "Equipos" in res.response

        event_names = [e["event"] for e in res.events]
        assert AgentEventType.ACTION_REQUESTED.value not in event_names

    asyncio.run(_run())


# ═══════════════════════════════════════════════════════════════════════════
# TEST 4: "3x3"
# ═══════════════════════════════════════════════════════════════════════════
def test_4_pure_math_calculation(runtime):
    """
    TEST 4:
    Usuario: '3x3'
    - Responde únicamente '9.'
    - CERO navegación.
    - CERO promoción comercial de Firby ni llamadas a la acción artificiales.
    - Chips vacíos.
    """
    async def _run():
        user_query = "3x3"
        user_id = "test_user_t4"

        res = await runtime.process_turn(
            message=user_query,
            user_id=user_id,
            org_id="firby_landing"
        )

        assert res.ok is True
        assert res.state == AgentRunState.DONE.value
        assert res.requires_observation is False
        assert res.action is None
        assert res.ui_action is None
        assert res.response.strip() == "9."
        assert len(res.chips) == 0
        assert len(res.action_chips) == 0
        assert "firby" not in res.response.lower()
        assert "plan" not in res.response.lower()

    asyncio.run(_run())


# ═══════════════════════════════════════════════════════════════════════════
# TEST 5: "Quiero agendar una cita."
# ═══════════════════════════════════════════════════════════════════════════
def test_5_booking_request_policy_and_missing_slots(runtime):
    """
    TEST 5:
    Usuario: 'Quiero agendar una cita.'
    - Para la landing de Firby, explica la política oficial (activación autoservicio 7 días o WhatsApp directivo).
    - CERO invención de acciones o citas falsas.
    - No se crea una cita sin slots (nombre, teléfono, horario).
    """
    async def _run():
        user_query = "Quiero agendar una cita."
        user_id = "test_user_t5"

        res = await runtime.process_turn(
            message=user_query,
            user_id=user_id,
            org_id="firby_landing"
        )

        assert res.ok is True
        assert res.state == AgentRunState.DONE.value
        assert res.requires_observation is False
        assert res.action is None
        assert res.ui_action is None
        # No inventa reservas confirmadas ficticias
        assert "APT-" not in res.response
        # Explica política real de Firby
        assert "prueba gratis" in res.response.lower() or "whatsapp" in res.response.lower()

    asyncio.run(_run())


# ═══════════════════════════════════════════════════════════════════════════
# TEST 6: Tool/action fails -> runtime replans
# ═══════════════════════════════════════════════════════════════════════════
def test_6_action_failed_observation_replanning(runtime):
    """
    TEST 6:
    Fallo de acción de interfaz (ej. sección no encontrada en el DOM).
    - Usuario pide ver los planes -> ACTION_REQUESTED emitido.
    - Frontend intenta navegar y falla (target missing).
    - Frontend reporta observación con status='section_target_missing', success=False.
    - Runtime verifica la falla, emite ACTION_FAILED y replanifica con una alternativa directa.
    - NO se marca como DONE sin replanificar.
    """
    async def _run():
        user_query = "Muéstrame los planes."
        user_id = "test_user_t6"
        run_id = "run_test_6_fail"

        # Fase 1: Acción solicitada
        res_phase1 = await runtime.process_turn(
            message=user_query,
            user_id=user_id,
            org_id="firby_landing",
            run_id=run_id
        )
        assert res_phase1.state == AgentRunState.ACTION_REQUESTED.value

        # Fase 2: Reporte de falla desde frontend
        fail_observation = {
            "run_id": run_id,
            "step_id": 1,
            "status": "section_target_missing",
            "target": "#planes",
            "success": False,
            "error": "Element #planes not found in DOM"
        }

        res_phase2 = await runtime.process_observation(
            run_id=run_id,
            observation_dict=fail_observation,
            user_id=user_id,
            org_id="firby_landing"
        )

        assert res_phase2.ok is True
        assert res_phase2.state == AgentRunState.DONE.value

        # Verificación de que el runtime replanificó
        event_names = [e["event"] for e in res_phase2.events]
        assert AgentEventType.ACTION_FAILED.value in event_names
        assert AgentEventType.VERIFICATION_COMPLETED.value in event_names

        # El evento de verificación completada registra status='failed' y replanned=True
        verify_events = [e for e in res_phase2.events if e["event"] == AgentEventType.VERIFICATION_COMPLETED.value]
        assert len(verify_events) > 0
        assert verify_events[0].get("data", {}).get("replanned") is True

        # El texto final ofrece el contenido en texto alternativo directamente
        assert "Starter" in res_phase2.response
        assert "Pro" in res_phase2.response

    asyncio.run(_run())


# ═══════════════════════════════════════════════════════════════════════════
# TEST 7: Integración HTTP completa (/api/widget/chat y /api/widget/observe)
# ═══════════════════════════════════════════════════════════════════════════
def test_7_http_api_two_phase_cycle():
    """
    TEST 7:
    Valida el ciclo completo de dos fases a través de los endpoints HTTP FastAPI.
    """
    client = TestClient(app)
    run_id = "http_run_123"

    # 1. Enviar mensaje de navegación
    r1 = client.post("/api/widget/chat", json={
        "message": "Muéstrame los planes",
        "user_id": "http_user_1",
        "run_id": run_id
    })
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["ok"] is True
    assert d1["state"] == "ACTION_REQUESTED"
    assert d1["action"]["target"] == "#planes"
    assert d1["requires_observation"] is True

    # 2. Reportar observación al endpoint /api/widget/observe
    r2 = client.post("/api/widget/observe", json={
        "run_id": run_id,
        "step_id": 1,
        "user_id": "http_user_1",
        "observation": {
            "status": "section_reached",
            "target": "#planes",
            "success": True
        }
    })
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["ok"] is True
    assert d2["state"] == "DONE"
    assert len(d2["bubbles"]) > 0
    assert "Starter" in d2["response"]

    # 3. Consulta directa sin navegación vía /api/widget/chat
    r3 = client.post("/api/widget/chat", json={
        "message": "3x3",
        "user_id": "http_user_2"
    })
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3["ok"] is True
    assert d3["state"] == "DONE"
    assert d3["action"] is None
    assert d3["response"].strip() == "9."
