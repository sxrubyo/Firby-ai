# -*- coding: utf-8 -*-
"""
Firby Platform — Bloque P1 Test Suite: Estabilización del Orquestador Conversacional
==================================================================================
Valida:
TEST 1: Turnos concurrentes sobre la misma sesión se procesan en orden FIFO sin carreras.
TEST 2: 'No quiero comprar todavía' responde sin navegar a /sign-up y sin chips de venta.
TEST 3: 'solo estoy mirando' no empuja la prueba gratis.
TEST 4: '¿Puede agendar citas?' responde sobre agendamiento sin CTA de registro ni trial.
TEST 5: '¿Cómo controla el operador lo que puede hacer?' explica control y políticas sin desvío comercial.
TEST 6: 'Vale.' después de una explicación responde acuse continuo sin despedida ('Quedo a tu disposición...').
TEST 7: La memoria de precios y pronombres relativos se preserva:
        '¿Cuál tiene más autonomía?' -> Pro
        '¿Y ese cuánto cuesta?' -> Pro
        '¿Y el anterior?' -> Starter
        '¿Y ese era el Pro?' -> Pro
TEST 8: Turno posterior a negación comercial respeta postura exploratoria (sin chips comerciales forzados).
STRESS TEST: Conversación completa de 10 turnos de extremo a extremo.
"""

import asyncio
import pytest
import uuid

from src.core.operator.intent_classifier import IntentClassifier, UserIntentType
from src.core.operator.memory import TaskState
from src.core.operator.runtime import operator_runtime
from src.core.widget_operator import widget_operator


def test_1_concurrent_turns_fifo_serialization():
    """TEST 1: Turnos concurrentes sobre la misma sesión se serializan y procesan en orden."""
    async def _run():
        user_id = f"test_user_fifo_{uuid.uuid4().hex[:8]}"
        
        # Lanzamos 3 mensajes concurrentes sobre la misma sesión
        results = await asyncio.gather(
            widget_operator.handle_message("Hola", user_id=user_id),
            widget_operator.handle_message("¿Cómo funciona Firby?", user_id=user_id),
            widget_operator.handle_message("Vale.", user_id=user_id)
        )

        assert len(results) == 3
        for r in results:
            assert r.get("ok") is True
            assert "response" in r or "bubbles" in r

        # Verificar que en memoria el turn_sequence avanzó correctamente sin corromperse
        state = operator_runtime.memory.load_task_state(user_id, "firby_landing")
        assert state.turn_sequence == 3
    asyncio.run(_run())


def test_2_commercial_negation_no_navigation_no_sales():
    """TEST 2: 'No quiero comprar todavía' responde sin navegar a /sign-up y sin chips de venta."""
    async def _run():
        user_id = f"test_user_neg_{uuid.uuid4().hex[:8]}"
        res = await operator_runtime.process_turn(
            message="No quiero comprar todavía",
            user_id=user_id,
            org_id="firby_landing"
        )

        assert res.ok is True
        assert res.intent == "commercial_negation"
        assert res.action is None
        assert res.ui_action is None

        # Verificar postura inhibida en memoria
        state = operator_runtime.memory.load_task_state(user_id, "firby_landing")
        assert state.is_commercial_inhibited() is True

        # Verificar chips: ninguno debe navegar a /sign-up ni /free-trial
        for chip in res.action_chips:
            target = chip.get("action_target") or ""
            assert "/sign-up" not in target
            assert "/free-trial" not in target
    asyncio.run(_run())


def test_3_exploration_mode_solo_estoy_mirando():
    """TEST 3: 'solo estoy mirando' activa exploración y no empuja la prueba gratis."""
    async def _run():
        user_id = f"test_user_look_{uuid.uuid4().hex[:8]}"
        res = await operator_runtime.process_turn(
            message="solo estoy mirando",
            user_id=user_id,
            org_id="firby_landing"
        )

        assert res.ok is True
        assert res.intent == "commercial_negation"
        assert "prueba gratuita" not in res.response.lower()
        assert "regístrate" not in res.response.lower()
        assert "registrate" not in res.response.lower()

        state = operator_runtime.memory.load_task_state(user_id, "firby_landing")
        assert state.is_commercial_inhibited() is True
    asyncio.run(_run())


def test_4_capability_query_booking():
    """TEST 4: '¿Puede agendar citas?' responde sobre agendamiento sin CTA de registro ni trial."""
    async def _run():
        user_id = f"test_user_cap_{uuid.uuid4().hex[:8]}"
        res = await operator_runtime.process_turn(
            message="¿Puede agendar citas?",
            user_id=user_id,
            org_id="firby_landing"
        )

        assert res.ok is True
        assert res.intent == "capability_query"
        assert res.action is None
        # Debe explicar Google Calendar
        assert "google calendar" in res.response.lower() or "agenda" in res.response.lower()
        # No debe obligar a registrarse
        assert "/sign-up" not in str(res.action_chips)
    asyncio.run(_run())


def test_5_capability_query_controls_and_exceptions():
    """TEST 5: '¿Cómo controla el operador lo que puede hacer?' explica control y políticas sin desvío comercial."""
    async def _run():
        user_id = f"test_user_ctrl_{uuid.uuid4().hex[:8]}"
        res = await operator_runtime.process_turn(
            message="¿Cómo controla el operador lo que puede hacer?",
            user_id=user_id,
            org_id="firby_landing"
        )

        assert res.ok is True
        assert res.intent == "capability_query"
        assert any(term in res.response.lower() for term in ["reglas", "políticas", "politicas", "whatsapp", "autorización"])
        assert res.action is None
    asyncio.run(_run())


def test_6_acknowledgement_continuous_no_farewell():
    """TEST 6: 'Vale.' después de una explicación responde acuse continuo sin despedida ('Quedo a tu disposición...')."""
    async def _run():
        user_id = f"test_user_ack_{uuid.uuid4().hex[:8]}"
        res = await operator_runtime.process_turn(
            message="Vale.",
            user_id=user_id,
            org_id="firby_landing"
        )

        assert res.ok is True
        assert res.intent == "acknowledgement"
        # No debe sonar a despedida
        assert "quedo a tu disposición si necesitas algo más" not in res.response.lower()
        assert "hasta luego" not in res.response.lower()
        # Debe mantener la conversación abierta
        assert any(term in res.response.lower() for term in ["entendido", "revisar", "orientarte", "ayudarte"])
    asyncio.run(_run())


def test_7_pricing_sequence_and_pronouns():
    """
    TEST 7: La secuencia de memoria de precios y pronombres relativos se preserva:
    '¿Cuál tiene más autonomía?' -> Pro
    '¿Y ese cuánto cuesta?' -> Pro
    '¿Y el anterior?' -> Starter
    '¿Y ese era el Pro?' -> Pro
    """
    state = TaskState(task_id="test_pricing")
    
    # 1. "¿Cuál tiene más autonomía?"
    c1 = IntentClassifier.classify("¿Cuál tiene más autonomía?", task_state=state)
    assert c1.target_plan == "pro"
    state.set_focus_entity("plan", "pro", "Plan Pro")

    # 2. "¿Y ese cuánto cuesta?"
    c2 = IntentClassifier.classify("¿Y ese cuánto cuesta?", task_state=state)
    assert c2.target_plan == "pro"

    # 3. "¿Y el anterior?"
    c3 = IntentClassifier.classify("¿Y el anterior?", task_state=state)
    assert c3.target_plan == "starter"
    state.set_focus_entity("plan", "starter", "Plan Starter")

    # 4. "¿Y ese era el Pro?"
    c4 = IntentClassifier.classify("¿Y ese era el Pro?", task_state=state)
    assert c4.target_plan == "pro"


def test_8_turn_after_negation_preserves_exploratory_posture():
    """TEST 8: Turno posterior a negación comercial respeta postura exploratoria (sin chips comerciales forzados)."""
    async def _run():
        user_id = f"test_user_post_neg_{uuid.uuid4().hex[:8]}"
        
        # Paso 1: Negación
        res1 = await operator_runtime.process_turn(
            message="No quiero contratar aún",
            user_id=user_id,
            org_id="firby_landing"
        )
        assert res1.intent == "commercial_negation"

        # Paso 2: Consulta posterior
        res2 = await operator_runtime.process_turn(
            message="¿Cómo funciona con WhatsApp?",
            user_id=user_id,
            org_id="firby_landing"
        )
        assert res2.intent == "capability_query"
        # No debe tener chips para iniciar prueba o ver planes con target comercial
        for chip in res2.action_chips:
            target = chip.get("action_target") or ""
            assert "/sign-up" not in target
            assert "/free-trial" not in target
    asyncio.run(_run())


def test_9_stress_test_10_turns_complete_flow():
    """
    STRESS TEST CONVERSACIONAL DE 10 TURNOS:
    T1: 'Hola'
    T2: '¿Cuál tiene más autonomía?'
    T3: '¿Y ese cuánto cuesta?'
    T4: '¿Y el anterior?'
    T5: 'No quiero comprar todavía, solo estoy mirando'
    T6: '¿Puede agendar citas?'
    T7: '¿Cómo controla el operador lo que puede hacer?'
    T8: 'Vale.'
    T9: '¿Cómo funciona con WhatsApp?'
    T10: 'Ok, me interesa. ¿Cómo me registro?'
    """
    async def _run():
        user_id = f"stress_test_user_{uuid.uuid4().hex[:8]}"
        
        # Turno 1: Saludo
        t1 = await operator_runtime.process_turn("Hola", user_id=user_id, org_id="firby_landing")
        assert t1.ok is True
        assert t1.turn_id == 1
        assert t1.intent == "casual_greeting"

        # Turno 2: "¿Cuál tiene más autonomía?"
        t2 = await operator_runtime.process_turn("¿Cuál tiene más autonomía?", user_id=user_id, org_id="firby_landing")
        assert t2.ok is True
        assert t2.turn_id == 2
        state2 = operator_runtime.memory.load_task_state(user_id, "firby_landing")
        assert state2.focus_entity.get("id") == "pro"

        # Turno 3: "¿Y ese cuánto cuesta?"
        t3 = await operator_runtime.process_turn("¿Y ese cuánto cuesta?", user_id=user_id, org_id="firby_landing")
        assert t3.ok is True
        assert t3.turn_id == 3

        # Turno 4: "¿Y el anterior?"
        t4 = await operator_runtime.process_turn("¿Y el anterior?", user_id=user_id, org_id="firby_landing")
        assert t4.ok is True
        assert t4.turn_id == 4
        state4 = operator_runtime.memory.load_task_state(user_id, "firby_landing")
        assert state4.focus_entity.get("id") == "starter"

        # Turno 5: "No quiero comprar todavía, solo estoy mirando"
        t5 = await operator_runtime.process_turn("No quiero comprar todavía, solo estoy mirando", user_id=user_id, org_id="firby_landing")
        assert t5.ok is True
        assert t5.turn_id == 5
        assert t5.intent == "commercial_negation"
        state5 = operator_runtime.memory.load_task_state(user_id, "firby_landing")
        assert state5.is_commercial_inhibited() is True

        # Turno 6: "¿Puede agendar citas?" (Inhibido comercialmente)
        t6 = await operator_runtime.process_turn("¿Puede agendar citas?", user_id=user_id, org_id="firby_landing")
        assert t6.ok is True
        assert t6.turn_id == 6
        assert t6.intent == "capability_query"
        assert t6.action is None
        for c in t6.action_chips:
            assert "/sign-up" not in (c.get("action_target") or "")

        # Turno 7: "¿Cómo controla el operador lo que puede hacer?"
        t7 = await operator_runtime.process_turn("¿Cómo controla el operador lo que puede hacer?", user_id=user_id, org_id="firby_landing")
        assert t7.ok is True
        assert t7.turn_id == 7
        assert t7.intent == "capability_query"
        assert t7.action is None

        # Turno 8: "Vale." (Acuse de recibo, no despedida)
        t8 = await operator_runtime.process_turn("Vale.", user_id=user_id, org_id="firby_landing")
        assert t8.ok is True
        assert t8.turn_id == 8
        assert t8.intent == "acknowledgement"
        assert "quedo a tu disposición si necesitas algo más" not in t8.response.lower()
        assert "hasta luego" not in t8.response.lower()

        # Turno 9: "¿Cómo funciona con WhatsApp?"
        t9 = await operator_runtime.process_turn("¿Cómo funciona con WhatsApp?", user_id=user_id, org_id="firby_landing")
        assert t9.ok is True
        assert t9.turn_id == 9
        assert t9.intent == "capability_query"
        assert any(w in t9.response.lower() for w in ["dueño", "ejecutiva", "excepciones", "dos canales"])

        # Turno 10: "Ok, me interesa. ¿Cómo me registro?" (Reactivación positiva explícita)
        t10 = await operator_runtime.process_turn("Ok, me interesa. ¿Cómo me registro?", user_id=user_id, org_id="firby_landing")
        assert t10.ok is True
        assert t10.turn_id == 10
        assert t10.intent == "commercial_action"
        state10 = operator_runtime.memory.load_task_state(user_id, "firby_landing")
        assert state10.is_commercial_inhibited() is False
    asyncio.run(_run())
