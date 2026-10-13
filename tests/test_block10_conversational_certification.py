# -*- coding: utf-8 -*-
"""
BLOQUE 10 — CERTIFICACIÓN CONVERSACIONAL Y PARIDAD DEV -> PROD
Suite Exhaustiva de Verificación de Fluidez, Orden Temporal, Postura Comercial y Límites Cognitivos.

Cubre los 16 requisitos obligatorios del Bloque 10:
1. Multi-turn 10+ turns
2. Multi-turn 15+ turns
3. Cambio de tema
4. Retorno a tema anterior
5. "ese" (referencia anafórica)
6. "el anterior" (referencia relativa de plan)
7. "Vale." + siguiente pregunta funcional sin cierre prematuro
8. Negación comercial ("No quiero comprar todavía", "Solo estoy mirando")
9. Cambio posterior a intención comercial ("Ok, me interesa")
10. Pregunta funcional dentro de conversación comercial (sin desvío agresivo)
11. Respuesta desconocida sin invención (Honest boundary)
12. Orden estricto de respuestas y asociación de turn_id
13. Concurrencia de turnos y serialización FIFO
14. Respuestas stale / prevención de cruce de mensajes
15. Ausencia de CTAs comerciales tras declarar exploración
16. Navegación únicamente ante intención válida y respeto a "no me lleves"
"""

import pytest
import asyncio
import uuid
import time
from typing import List, Dict, Any

from src.core.operator.runtime import operator_runtime
from src.core.operator.models import OperatorResult
from src.core.operator.intent_classifier import IntentClassifier, UserIntentType
from src.core.operator.memory import TaskState
from src.core.widget_operator import widget_operator


# ==============================================================================
# 1. ORDEN TEMPORAL Y SERIALIZACIÓN DE TURNOS CONCURRENTES (FASE A / REQ 12, 13)
# ==============================================================================

def test_1_temporal_order_and_concurrent_turns():
    """
    REQ 12 & 13: Verifica que turnos simultáneos o solapados mantengan orden estricto
    y asociación unívoca de turn_id mediante SessionLockManager.
    """
    async def _run():
        user_id = f"test_b10_fifo_{uuid.uuid4().hex[:8]}"

        # Lanzar T1 ("¿Cómo controla el operador lo que puede hacer?") y T2 ("¿Y cuánto cuesta?")
        t1_fut = widget_operator.handle_message("¿Cómo controla el operador lo que puede hacer?", user_id=user_id, org_id="firby_landing")
        t2_fut = widget_operator.handle_message("¿Y cuánto cuesta?", user_id=user_id, org_id="firby_landing")

        res1, res2 = await asyncio.gather(t1_fut, t2_fut)

        assert res1["ok"] is True
        assert res2["ok"] is True
        assert res1["turn_id"] == 1, f"Expected turn_id 1, got {res1.get('turn_id')}"
        assert res2["turn_id"] == 2, f"Expected turn_id 2, got {res2.get('turn_id')}"
        assert res1["intent"] == "capability_query"
        assert res2["intent"] == "business_pricing"

        # Comprobar que res1 no contiene precio y res2 responde pricing / navega a #planes
        assert "reglas" in res1["response"].lower() or "políticas" in res1["response"].lower() or "whatsapp" in res1["response"].lower()
        if res2.get("requires_observation") and res2.get("ui_action"):
            assert res2["ui_action"]["target"] == "#planes"
            obs_res = await widget_operator.handle_observation(
                run_id=res2["run_id"],
                observation={"success": True, "target": "#planes", "current_section": "#planes"},
                user_id=user_id,
                org_id="firby_landing"
            )
            assert any(w in obs_res["response"].lower() for w in ["starter", "pro", "equipos", "cop", "mes"])
        else:
            assert any(w in res2["response"].lower() for w in ["starter", "pro", "equipos", "cop", "mes"])

    asyncio.run(_run())


# ==============================================================================
# 2. REFERENCIAS RELATIVAS Y MEMORIA DE PRECIOS ("ese", "el anterior") (REQ 5, 6)
# ==============================================================================

def test_2_relative_pronoun_ese():
    """REQ 5: '¿Cuál tiene más autonomía?' -> Pro, seguido de '¿Y ese cuánto cuesta?' -> Pro."""
    state = TaskState(task_id="test_ese")
    
    c1 = IntentClassifier.classify("¿Cuál tiene más autonomía?", task_state=state)
    assert c1.target_plan == "pro"
    state.set_focus_entity("plan", "pro", "Plan Pro")

    c2 = IntentClassifier.classify("¿Y ese cuánto cuesta?", task_state=state)
    assert c2.target_plan == "pro"
    assert c2.intent == UserIntentType.BUSINESS_PRICING


def test_3_relative_pronoun_el_anterior():
    """REQ 6: De Pro a '¿Y el anterior?' resuelve a Starter; de Equipos a '¿Y el anterior?' resuelve a Pro."""
    state = TaskState(task_id="test_anterior")
    state.set_focus_entity("plan", "pro", "Plan Pro")

    c1 = IntentClassifier.classify("¿Y el anterior?", task_state=state)
    assert c1.target_plan == "starter"

    state.set_focus_entity("plan", "equipos", "Plan Equipos")
    c2 = IntentClassifier.classify("¿Y el anterior?", task_state=state)
    assert c2.target_plan == "pro"


# ==============================================================================
# 3. NEGACIÓN COMERCIAL Y EXPLORACIÓN (REQ 8, 14, 15)
# ==============================================================================

def test_4_commercial_negation_strictly_inhibits_sales_and_signup():
    """
    REQ 8 & 14: Frases de negación comercial no inician navegación a /sign-up
    ni devuelven CTAs de venta en consultas posteriores.
    """
    async def _run():
        negations = [
            "No quiero comprar todavía.",
            "Solo estoy mirando.",
            "Solo estoy investigando.",
            "No quiero contratar aún.",
            "Todavía no."
        ]

        for text in negations:
            user_id = f"test_b10_neg_{uuid.uuid4().hex[:6]}"
            res = await operator_runtime.process_turn(text, user_id=user_id, org_id="firby_landing")
            assert res.ok is True
            assert res.intent == "commercial_negation"
            assert res.action is None
            assert res.ui_action is None

            # Verificar que no contiene llamadas a la acción de registro
            for chip in res.action_chips:
                target = chip.get("action_target") or ""
                assert "/sign-up" not in target
                assert "/free-trial" not in target

            # Turno posterior de capacidad técnica
            res_sub = await operator_runtime.process_turn("¿Cómo funciona con WhatsApp?", user_id=user_id, org_id="firby_landing")
            assert res_sub.ok is True
            assert res_sub.intent == "capability_query"
            for chip in res_sub.action_chips:
                target = chip.get("action_target") or ""
                assert "/sign-up" not in target
                assert "/free-trial" not in target
                assert "#planes" not in target

    asyncio.run(_run())


# ==============================================================================
# 4. REACTIVACIÓN A ACCIÓN COMERCIAL LEGÍTIMA (REQ 9)
# ==============================================================================

def test_5_reactivation_from_negation_to_commercial_action():
    """
    REQ 9: Tras declarar exploración, una intención explícita posterior
    como 'Ok, me interesa. ¿Cómo me registro?' reactiva el flujo comercial.
    """
    async def _run():
        user_id = f"test_b10_react_{uuid.uuid4().hex[:8]}"

        # Turno 1: Negación
        r1 = await operator_runtime.process_turn("No quiero comprar todavía, solo estoy mirando", user_id=user_id, org_id="firby_landing")
        assert r1.intent == "commercial_negation"
        state1 = operator_runtime.memory.load_task_state(user_id, "firby_landing")
        assert state1.is_commercial_inhibited() is True

        # Turno 2: Reactivación explícita
        r2 = await operator_runtime.process_turn("Ok, me interesa. ¿Cómo me registro?", user_id=user_id, org_id="firby_landing")
        assert r2.ok is True
        assert r2.intent == "commercial_action"
        state2 = operator_runtime.memory.load_task_state(user_id, "firby_landing")
        assert state2.is_commercial_inhibited() is False

        # Verifica que ofrece chips para registrarse y ver planes
        chip_targets = [c.get("action_target") for c in r2.action_chips]
        assert any(t in ["/sign-up", "/free-trial"] for t in chip_targets if t)

    asyncio.run(_run())


# ==============================================================================
# 5. MENSAJES CORTOS Y CONTINUIDAD ("Vale.", "Ok.") (REQ 7)
# ==============================================================================

def test_6_acknowledgement_followed_by_immediate_query():
    """
    REQ 7: 'Vale.' no dispara cierre de despedida ('Quedo a tu disposición...').
    El turno siguiente se responde con total normalidad.
    """
    async def _run():
        user_id = f"test_b10_ack_{uuid.uuid4().hex[:8]}"

        r1 = await operator_runtime.process_turn("Vale.", user_id=user_id, org_id="firby_landing")
        assert r1.ok is True
        assert r1.intent == "acknowledgement"
        assert "quedo a tu disposición si necesitas algo más" not in r1.response.lower()
        assert "hasta luego" not in r1.response.lower()

        r2 = await operator_runtime.process_turn("Antes de eso, ¿puede pedir autorización antes de reservar?", user_id=user_id, org_id="firby_landing")
        assert r2.ok is True
        assert r2.intent == "capability_query"
        assert any(w in r2.response.lower() for w in ["autorización", "visto bueno", "whatsapp", "dueño", "política", "politica"])

    asyncio.run(_run())


# ==============================================================================
# 6. CONSULTAS DE CAPACIDAD TÉCNICA SIN DESVÍO COMERCIAL (REQ 10)
# ==============================================================================

def test_7_capability_query_inside_commercial_conversation():
    """
    REQ 10: '¿Puede agendar citas?' explica Google Calendar de forma funcional
    sin empujar agresivamente la prueba ni forzar registro en /sign-up.
    """
    async def _run():
        user_id = f"test_b10_cap_{uuid.uuid4().hex[:8]}"

        # Paso 1: Pregunta de precio
        await operator_runtime.process_turn("¿Cuánto cuesta el Starter?", user_id=user_id, org_id="firby_landing")

        # Paso 2: Pregunta funcional de capacidad
        r2 = await operator_runtime.process_turn("¿Puede agendar citas?", user_id=user_id, org_id="firby_landing")
        assert r2.ok is True
        assert r2.intent == "capability_query"
        assert "google calendar" in r2.response.lower() or "agenda" in r2.response.lower()
        # No debe redirigir la navegación
        assert r2.action is None
        assert r2.ui_action is None

    asyncio.run(_run())


# ==============================================================================
# 7. HONEST BOUNDARY: PREGUNTAS DESCONOCIDAS O INTERNAS (REQ 11)
# ==============================================================================

def test_8_honest_boundary_unknown_facts():
    """
    REQ 11: Consultas sobre hechos desconocidos o equipo interno orientan a /sobre-nosotros
    sin alucinar nombres inventados de personas.
    """
    async def _run():
        user_id = f"test_b10_honest_{uuid.uuid4().hex[:8]}"

        r = await operator_runtime.process_turn("¿Quién es el CEO de Firby?", user_id=user_id, org_id="firby_landing")
        assert r.ok is True
        assert r.intent in ["business_about", "honest_boundary"]
        assert any(w in r.response.lower() for w in ["no dispongo", "registros oficiales", "sobre-nosotros", "medellín"])

    asyncio.run(_run())


# ==============================================================================
# 8. CAMBIO DE TEMA Y RETORNO CONTEXTUAL (REQ 3, 4)
# ==============================================================================

def test_9_topic_shift_and_contextual_return():
    """
    REQ 3 & 4: Cambio drástico de tema (cálculo matemático) seguido de regreso a precios.
    Detecta ambigüedad o responde limpiamente sin mezclar contextos.
    """
    async def _run():
        user_id = f"test_b10_shift_{uuid.uuid4().hex[:8]}"

        # T1: Precio Pro
        r1 = await operator_runtime.process_turn("¿Cuánto cuesta el Plan Pro?", user_id=user_id, org_id="firby_landing")
        assert r1.intent == "business_pricing"

        # T2: Cambio de tema (matemática pura)
        r2 = await operator_runtime.process_turn("¿Cuánto es 25 por 4?", user_id=user_id, org_id="firby_landing")
        assert r2.intent == "calculation_or_fact"
        assert "100" in r2.response or any(w in r2.response.lower() for w in ["enfocado", "cálculos", "sitio web", "operaciones", "matemáticos", "procesos"])

        # T3: Regreso a precios
        r3 = await operator_runtime.process_turn("Volviendo a los planes, ¿cuánto cuesta el Starter?", user_id=user_id, org_id="firby_landing")
        assert r3.intent == "business_pricing"
        assert "starter" in r3.response.lower()
        assert "290.000" in r3.response

    asyncio.run(_run())


# ==============================================================================
# 9. RESTRICCIÓN NEGATIVA DE NAVEGACIÓN ("no me lleves") (REQ 16)
# ==============================================================================

def test_10_negative_navigation_constraint_absolute():
    """
    REQ 16: 'Quiero ver los precios pero no me muevas la página' informa precios
    directamente en texto con ui_action = None.
    """
    async def _run():
        user_id = f"test_b10_nomic_{uuid.uuid4().hex[:8]}"

        r = await operator_runtime.process_turn("Quiero ver los precios pero no me lleves a ninguna parte ni muevas la página", user_id=user_id, org_id="firby_landing")
        assert r.ok is True
        assert r.intent == "business_pricing"
        assert r.action is None
        assert r.ui_action is None
        assert any(w in r.response.lower() for w in ["starter", "pro", "equipos"])

    asyncio.run(_run())


# ==============================================================================
# 10. PREVENCIÓN DE RESPUESTAS STALE EN RÁFAGA (REQ 14)
# ==============================================================================

def test_11_no_stale_responses_on_rapid_fire():
    """
    REQ 14: Cuatro mensajes rápidos consecutivos sobre la misma sesión.
    Cada uno debe recibir su respuesta con turn_id estrictamente incremental (1, 2, 3, 4).
    """
    async def _run():
        user_id = f"test_b10_rapid_{uuid.uuid4().hex[:8]}"
        msgs = ["Hola", "¿Qué planes hay?", "¿Y el Pro?", "Vale."]

        results = []
        for msg in msgs:
            res = await widget_operator.handle_message(msg, user_id=user_id, org_id="firby_landing")
            results.append(res)

        turn_ids = [r["turn_id"] for r in results]
        assert turn_ids == [1, 2, 3, 4], f"Expected turn_ids [1, 2, 3, 4], got {turn_ids}"

    asyncio.run(_run())


# ==============================================================================
# 11. CONVERSACIÓN DE 10 TURNOS (REQ 1)
# ==============================================================================

def test_12_multi_turn_10_turns_complete_suite():
    """REQ 1: Conversación lineal y coherente de 10 turnos consecutivos."""
    async def _run():
        user_id = f"test_b10_10t_{uuid.uuid4().hex[:8]}"
        conversation = [
            ("Hola", "casual_greeting"),
            ("¿Qué es Firby?", "what_is_firby"),
            ("¿Cuáles son los planes?", "business_pricing"),
            ("¿Y ese Pro qué incluye?", "business_pricing"),
            ("¿Y el anterior?", "business_pricing"),
            ("No quiero contratar aún, solo estoy revisando", "commercial_negation"),
            ("¿Puede agendar citas?", "capability_query"),
            ("¿Cómo se integra con WhatsApp?", "capability_query"),
            ("Vale.", "acknowledgement"),
            ("Ok, me interesa. ¿Cómo me registro?", "commercial_action")
        ]

        for idx, (prompt, expected_intent) in enumerate(conversation, start=1):
            res = await operator_runtime.process_turn(prompt, user_id=user_id, org_id="firby_landing")
            assert res.ok is True, f"Turn {idx} failed"
            assert res.turn_id == idx, f"Turn {idx} expected turn_id {idx}, got {res.turn_id}"
            assert res.intent == expected_intent, f"Turn {idx} ('{prompt}') expected intent '{expected_intent}', got '{res.intent}'"

    asyncio.run(_run())


# ==============================================================================
# 12. CONVERSACIÓN PROFUNDA DE 15 TURNOS (REQ 2, FASE C)
# ==============================================================================

def test_13_multi_turn_15_turns_deep_master_flow():
    """
    REQ 2 & SECCIÓN 12: Conversación profunda de 15 turnos simulando el flujo completo:
    - Saludo
    - Consulta de producto
    - Precios y memoria
    - Referencias anafóricas ("ese", "el anterior")
    - Cambio de tema (matemática pura)
    - Regreso a negocio
    - Objeción comercial ("No quiero comprar todavía")
    - Pregunta funcional de citas (sin venta forzada)
    - Consulta de WhatsApp (dos canales)
    - Consulta honest boundary (CEO / Medellín)
    - Mensaje corto "Vale." (sin cierre de despedida)
    - Reactivación comercial explícita
    - Cierre cordial.
    """
    async def _run():
        user_id = f"test_b10_15t_{uuid.uuid4().hex[:8]}"

        flow = [
            # T1: Saludo inicial
            ("Hola", "casual_greeting", lambda r: "ayudarte" in r.response.lower() or "hola" in r.response.lower()),
            # T2: Producto
            ("¿Qué hace Firby exactamente?", "capability_query", lambda r: "operador" in r.response.lower() or "web" in r.response.lower()),
            # T3: Precios generales
            ("¿Cuánto cuestan los planes?", "business_pricing", lambda r: "starter" in r.response.lower() and "pro" in r.response.lower()),
            # T4: Referencia anafórica a Pro
            ("¿Cuál tiene más autonomía?", "business_pricing", lambda r: "pro" in r.response.lower() and "490.000" in r.response),
            # T5: Referencia anafórica "ese"
            ("¿Y ese qué incluye?", "business_pricing", lambda r: "autonomía" in r.response.lower() or "otp" in r.response.lower() or "whatsapp" in r.response.lower()),
            # T6: Referencia relativa "el anterior"
            ("¿Y el anterior?", "business_pricing", lambda r: "starter" in r.response.lower() and "290.000" in r.response),
            # T7: Desvío drástico de tema
            ("¿Cuánto es 12 por 5?", "calculation_or_fact", lambda r: "60" in r.response or any(w in r.response.lower() for w in ["enfocado", "cálculos", "sitio web", "operaciones", "matemáticos", "procesos"])),
            # T8: Asentimiento corto sin cierre
            ("Vale.", "acknowledgement", lambda r: "hasta luego" not in r.response.lower() and "quedo a tu disposición" not in r.response.lower()),
            # T9: Retorno a negocio
            ("Volviendo a Firby, ¿cuánto cuesta el plan Equipos?", "business_pricing", lambda r: "equipos" in r.response.lower() and "890.000" in r.response),
            # T10: Negación comercial
            ("No quiero comprar todavía, solo estoy mirando", "commercial_negation", lambda r: r.action is None and not any("/sign-up" in (c.get("action_target") or "") for c in r.action_chips)),
            # T11: Pregunta de capacidad técnica (sin desvío a ventas)
            ("¿Puede agendar citas?", "capability_query", lambda r: "google calendar" in r.response.lower() or "agenda" in r.response.lower()),
            # T12: Pregunta de dos canales / WhatsApp
            ("¿Cómo funciona con WhatsApp?", "capability_query", lambda r: any(w in r.response.lower() for w in ["dueño", "ejecutiva", "excepciones", "dos canales"])),
            # T13: Honest boundary
            ("¿Quién es el CEO de Firby?", "honest_boundary", lambda r: any(w in r.response.lower() for w in ["no dispongo", "registros oficiales", "sobre-nosotros", "medellín"])),
            # T14: Reactivación comercial explícita
            ("Ok, me interesa. ¿Cómo me registro?", "commercial_action", lambda r: any(t in ["/sign-up", "/free-trial"] for t in [c.get("action_target") for c in r.action_chips])),
            # T15: Cierre cordial
            ("Muchas gracias", "casual_greeting", lambda r: "gusto" in r.response.lower())
        ]

        for step, (message, expected_intent, validator) in enumerate(flow, start=1):
            res = await operator_runtime.process_turn(message, user_id=user_id, org_id="firby_landing")
            assert res.ok is True, f"Step {step} failed: ok is False"
            assert res.turn_id == step, f"Step {step} turn_id mismatch: expected {step}, got {res.turn_id}"
            assert res.intent == expected_intent, f"Step {step} ('{message}') expected intent '{expected_intent}', got '{res.intent}'"
            assert validator(res), f"Step {step} validator failed on response: {res.response}"

    asyncio.run(_run())


# ==============================================================================
# 13. AUSENCIA TOTAL DE CTA TRAS DECLARAR EXPLORACIÓN (REQ 15)
# ==============================================================================

def test_14_no_cta_after_exploration_mode():
    """REQ 15: Comprueba que una consulta posterior a 'solo estoy mirando' no contiene chips comerciales."""
    async def _run():
        user_id = f"test_b10_nocta_{uuid.uuid4().hex[:8]}"

        # Paso 1: Exploración declarada
        r1 = await operator_runtime.process_turn("Solo estoy mirando por ahora", user_id=user_id, org_id="firby_landing")
        assert r1.intent == "commercial_negation"

        # Paso 2: Preguntas posteriores diversas
        for query in ["¿Qué hace Firby?", "¿Cómo funciona con WhatsApp?", "¿Puede agendar citas?"]:
            r = await operator_runtime.process_turn(query, user_id=user_id, org_id="firby_landing")
            for chip in r.action_chips:
                target = (chip.get("action_target") or "").lower()
                assert "/sign-up" not in target
                assert "/free-trial" not in target
                assert "#planes" not in target
                assert "prueba" not in chip.get("label", "").lower()
                assert "contratar" not in chip.get("label", "").lower()

    asyncio.run(_run())


# ==============================================================================
# 14. NAVEGACIÓN SOLAMENTE ANTE INTENCIÓN VÁLIDA (REQ 16)
# ==============================================================================

def test_15_navigation_only_on_valid_explicit_intent():
    """
    REQ 16: Comprueba que consultas informativas o de capacidad no disparan navegación de UI.
    La navegación se dispara ÚNICAMENTE ante solicitud explícita sin restricciones negativas.
    """
    async def _run():
        user_id = f"test_b10_nav_{uuid.uuid4().hex[:8]}"

        # Consultas sin navegación de UI
        non_nav_queries = [
            "¿Cómo funciona con WhatsApp?",
            "¿Puede agendar citas?",
            "¿Cuánto es 2 + 2?",
            "Hola",
            "Vale."
        ]
        for q in non_nav_queries:
            r = await operator_runtime.process_turn(q, user_id=user_id, org_id="firby_landing")
            assert r.action is None, f"Query '{q}' should not emit ui_action"
            assert r.ui_action is None, f"Query '{q}' should not emit ui_action"

        # Consulta con intención explícita de navegación a FAQ
        r_nav = await operator_runtime.process_turn("Llévame a las preguntas frecuentes", user_id=user_id, org_id="firby_landing")
        assert r_nav.intent == "navigation_request"
        assert r_nav.ui_action is not None
        assert r_nav.ui_action.get("target") in ["/faq", "#faq"]

    asyncio.run(_run())


# ==============================================================================
# 15. TÉRMINOS Y CONDICIONES (TERMS_CONSENT) (FASE D)
# ==============================================================================

def test_16_terms_consent_cordial_no_navigation():
    """
    FASE D / REQ 14: 'Sí, acepto' agradece cordialmente la aceptación y pregunta
    cómo ayudar hoy, con ui_action = None y sin navegar ni recitar planes.
    """
    async def _run():
        user_id = f"test_b10_tc_{uuid.uuid4().hex[:8]}"

        r = await operator_runtime.process_turn("Sí, acepto", user_id=user_id, org_id="firby_landing")
        assert r.ok is True
        assert r.intent == "terms_consent"
        assert r.action is None
        assert r.ui_action is None
        assert "quedamos conectados" in r.response.lower() or "gracias por aceptar" in r.response.lower() or "aceptar los términos" in r.response.lower()
        assert any(w in r.response.lower() for w in ["orientar", "ayudarle", "ayudarte", "conocer", "cómo puedo ayudarle"])

        # No debe recitar lista de precios
        assert "290.000" not in r.response
        assert "490.000" not in r.response

    asyncio.run(_run())


# ==============================================================================
# 16. RECORRIDO GUIADO CON DESPLAZAMIENTO SUAVE (GUIDED SCROLL)
# ==============================================================================

def test_17_guided_slow_scroll_flow():
    """
    Verifica que solicitudes de recorrido guiado con desplazamiento suave:
    1. Se clasifiquen como NAVIGATION_REQUEST con target #como-funciona y topic guided_scroll.
    2. En el paso 1 emitan una acción con slow=True y duration=2.8.
    3. Al reportar la observación del cliente, sinteticen el mensaje de acompañamiento y chips secuenciales.
    """
    async def _run():
        user_id = f"test_b10_guided_{uuid.uuid4().hex[:8]}"

        # Paso 1: Solicitud conversacional con saludo y petición de guiado suave
        r1 = await operator_runtime.process_turn(
            "holaa, guiame y ve scrolleando suavemente por mi",
            user_id=user_id,
            org_id="firby_landing"
        )
        assert r1.ok is True
        assert r1.intent == "navigation_request"
        assert r1.state == "ACTION_REQUESTED"
        assert r1.action is not None
        assert r1.action.get("target") == "#como-funciona"
        assert r1.action.get("slow") is True
        assert r1.action.get("duration") == 2.8

        # Paso 2: Observación de interfaz completada
        obs_payload = {
            "status": "scroll_completed",
            "target": "#como-funciona",
            "success": True,
            "scroll_completed": True,
            "section_id": "#como-funciona"
        }
        r2 = await operator_runtime.process_observation(
            run_id=r1.run_id,
            observation_dict=obs_payload,
            user_id=user_id,
            org_id="firby_landing"
        )
        assert r2.ok is True
        assert r2.state == "DONE"
        assert "desplazamiento suave" in r2.response.lower()
        assert "cómo funciona" in r2.response.lower()
        assert "Siguiente: Canales" in r2.chips

    asyncio.run(_run())


