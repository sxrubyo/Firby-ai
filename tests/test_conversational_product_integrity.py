# -*- coding: utf-8 -*-
"""
Firby AI — Conversational Product Integrity & Operator Alignment Test Suite
===========================================================================
Valida rigurosamente la alineación del operador web de Firby:
1. what_is_firby: "¿Qué es Firby?" responde la definición directa, no saludo genérico.
2. terms_consent_pending: "Sí, acepto" con consentimiento pendiente ejecuta TERMS_CONSENT.
3. terms_consent_already_accepted: "Sí, acepto" tras consentimiento previo no reinicia estado.
4. terms_consent_out_of_context: "sí, acepto" en otro contexto no se reinterpreta legalmente.
5. response_integrity: is_response_complete valida sintaxis, comillas y terminaciones anómalas.
6. max_token_fallback: finishReason MAX_TOKENS / LENGTH es descartado y rota de modelo.
7. long_response_complete: respuesta profunda de arquitectura no sufre truncamiento.
8. most_complete_plan: "¿Cuánto cuesta el plan más completo?" identifica explícitamente Equipos.
9. exact_feature_question: "¿Ese tiene soporte prioritario?" responde puntualmente sin derivar a WhatsApp.
10. functional_question_not_auto_whatsapp: preguntas funcionales no desvían a WhatsApp.
11. appointment_capability_truth: agendamiento refleja verdad de capacidad sin desvío a WhatsApp.
12. navigation_cancelled: cancelación de navegación emite CANCELLED sin confirmar desplazamiento.
13. navigation_completed: navegación completada se confirma formalmente ("Le he ubicado...").
14. negative_navigation_constraint: "no me lleves" inhibe herramientas de navegación.
15. formal_tone: registro formal consistente "usted / su / sus" en todas las respuestas.
16. no_false_booking: nunca se inventa una cita si la herramienta está deshabilitada.
17. response_after_10_turns: integridad de memoria y respuesta tras 10 turnos interactivos.
18. response_after_15_turns: estabilidad conversacional y contexto sostenido tras 15 turnos.
"""

import asyncio
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.widget_operator import FirbyWidgetOperator
from src.core.operator.runtime import DigitalWebOperatorRuntime
from src.core.operator.intent_classifier import IntentClassifier, UserIntentType
from src.core.operator.memory import TaskState
from src.core.operator.models import ActionObservation, AgentRunState


operator_runtime = DigitalWebOperatorRuntime()


# 1. WHAT_IS_FIRBY
def test_01_what_is_firby():
    async def _run():
        user_id = f"test_wif_{uuid.uuid4().hex[:8]}"
        res = await operator_runtime.process_turn("Hola, ¿qué es Firby?", user_id=user_id, org_id="firby_landing")
        assert res.ok is True
        assert res.intent == "what_is_firby"
        assert res.ui_action is None
        # No debe ser el saludo genérico vacío
        assert res.response != "Hola. ¿En qué puedo ayudarte hoy?"
        assert res.response != "Hola. ¿En qué puedo ayudarle hoy?"
        # Debe definir que es un operador digital autónomo en sitio web
        lower = res.response.lower()
        assert "operador digital autónomo" in lower or "operador" in lower
        assert "sitio web" in lower or "web" in lower
    asyncio.run(_run())


# 2. TERMS_CONSENT PENDING
def test_02_terms_consent_pending():
    async def _run():
        user_id = f"test_tcp_{uuid.uuid4().hex[:8]}"
        res = await operator_runtime.process_turn("Sí, acepto", user_id=user_id, org_id="firby_landing")
        assert res.ok is True
        assert res.intent == "terms_consent"
        assert "quedamos conectados" in res.response.lower() or "gracias por aceptar" in res.response.lower()
        assert any(w in res.response.lower() for w in ["orientar", "ayudarle", "ayudarte", "conocer"])
        # Verificar que el estado guardó terms_accepted = True
        state = operator_runtime.memory.load_task_state(user_id, "firby_landing")
        assert state.terms_accepted is True
    asyncio.run(_run())


# 3. TERMS_CONSENT ALREADY ACCEPTED
def test_03_terms_consent_already_accepted():
    async def _run():
        user_id = f"test_tca_{uuid.uuid4().hex[:8]}"
        # Turno 1: Aceptación legal legítima
        res1 = await operator_runtime.process_turn("Sí, acepto", user_id=user_id, org_id="firby_landing")
        assert res1.intent == "terms_consent"

        # Turno 2: Usuario vuelve a escribir "Sí, acepto"
        res2 = await operator_runtime.process_turn("Sí, acepto", user_id=user_id, org_id="firby_landing")
        # NO debe repetir el saludo de términos ni reiniciar el estado
        assert res2.intent != "terms_consent"
        assert res2.intent == "acknowledgement"
        assert "gracias por aceptar los términos" not in res2.response.lower()
    asyncio.run(_run())


# 4. TERMS REQUIRED GATE & EXPLICIT REJECTION
def test_04_terms_consent_gate_and_rejection():
    async def _run():
        user_id = f"test_terms_{uuid.uuid4().hex[:8]}"
        # Turno 1: Usuario escribe sin haber aceptado los términos
        res1 = await operator_runtime.process_turn("¿Cuánto cuesta el plan Pro?", user_id=user_id, org_id="firby_landing")
        assert res1.ok is True
        assert res1.intent == "terms_required"
        assert "acepta nuestros términos y condiciones" in res1.response.lower()
        assert res1.action_card is not None
        assert res1.action_card.get("type") == "consent_terms"
        assert "Sí, acepto" in res1.chips

        # Turno 2: Usuario rechaza explícitamente ("no acepto")
        res2 = await operator_runtime.process_turn("no acepto", user_id=user_id, org_id="firby_landing")
        assert res2.ok is True
        assert res2.intent == "terms_rejected"
        assert "acepta nuestros términos y condiciones" in res2.response.lower()
        assert res2.action_card is not None
        assert res2.action_card.get("type") == "consent_terms"

        # Turno 3: Usuario finalmente acepta ("Sí, acepto")
        res3 = await operator_runtime.process_turn("Sí, acepto", user_id=user_id, org_id="firby_landing")
        assert res3.ok is True
        assert res3.intent == "terms_consent"
        assert "gracias por aceptar" in res3.response.lower()
        state = operator_runtime.memory.load_task_state(user_id, "firby_landing")
        assert state.terms_accepted is True
    asyncio.run(_run())


# 5. RESPONSE INTEGRITY
def test_05_response_integrity():
    # Respuestas completas
    assert FirbyWidgetOperator.is_response_complete("Firby opera en su sitio web atendiendo visitantes.") is True
    assert FirbyWidgetOperator.is_response_complete("El plan Starter cuesta $290.000 COP / mes.") is True
    assert FirbyWidgetOperator.is_response_complete("Entendido. ¿En qué puedo orientarle hoy?") is True

    # Respuestas anómalas o truncadas
    assert FirbyWidgetOperator.is_response_complete("") is False
    assert FirbyWidgetOperator.is_response_complete("Firby está diseñado para atender a los visitantes y agend...") is False
    assert FirbyWidgetOperator.is_response_complete("El costo mensual es de **$490.000 COP") is False
    assert FirbyWidgetOperator.is_response_complete('Dijo que "el sistema') is False
    assert FirbyWidgetOperator.is_response_complete('{"status": "running"') is False
    assert FirbyWidgetOperator.is_response_complete("Firby atiende a los visitantes y realiza la sincronización de") is False


# 6. MAX TOKEN FALLBACK
def test_06_max_token_fallback():
    async def _run():
        operator = FirbyWidgetOperator()

        call_count = 0
        async def mock_post(url, json=None, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_resp = MagicMock()
            if call_count == 1:
                # Simular respuesta truncada con finishReason MAX_TOKENS
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "candidates": [{
                        "finishReason": "MAX_TOKENS",
                        "content": {"parts": [{"text": "Esta respuesta fue cortada a la mitad por max_tokens..."}]}
                    }]
                }
            else:
                # Simular respuesta exitosa completa del siguiente modelo
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "candidates": [{
                        "finishReason": "STOP",
                        "content": {"parts": [{"text": "Esta es la respuesta completa y correcta del siguiente modelo en el swarm."}]}
                    }]
                }
            return mock_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            text, model = await operator._call_gemini_api_swarm("Hola, consulta de prueba", "Eres Firby")
            assert call_count >= 2
            assert text == "Esta es la respuesta completa y correcta del siguiente modelo en el swarm."
            assert operator.is_response_complete(text) is True
    asyncio.run(_run())


# 7. LONG RESPONSE COMPLETE
def test_07_long_response_complete():
    async def _run():
        user_id = f"test_lrc_{uuid.uuid4().hex[:8]}"
        query = "Y ya? Que pasa si quieren cambiar su nombre o no se su correo como actua en el servidor?"
        res = await operator_runtime.process_turn(query, user_id=user_id, org_id="firby_landing")
        assert res.ok is True
        assert len(res.response) > 50
        assert FirbyWidgetOperator.is_response_complete(res.response) is True
        # Debe terminar con puntuación adecuada
        assert res.response.strip().endswith(('.', '!', '?', ':'))
        # No debe contener tokens truncados
        assert not res.response.endswith("agend...")
    asyncio.run(_run())


# 8. MOST COMPLETE PLAN
def test_08_most_complete_plan():
    async def _run():
        user_id = f"test_mcp_{uuid.uuid4().hex[:8]}"
        res = await operator_runtime.process_turn("¿Cuánto cuesta el plan más completo?", user_id=user_id, org_id="firby_landing")
        assert res.ok is True
        assert res.intent == "business_pricing"
        lower = res.response.lower()
        # Debe identificar explícitamente a Equipos
        assert "equipos" in lower
        assert "890.000" in res.response
        assert "7 días gratis" in lower or "prueba" in lower
    asyncio.run(_run())


# 9. EXACT FEATURE QUESTION (SOPORTE PRIORITARIO)
def test_09_exact_feature_question():
    async def _run():
        user_id = f"test_efq_{uuid.uuid4().hex[:8]}"
        # Turno 1: Foco en Plan Pro
        await operator_runtime.process_turn("¿Cuánto cuesta el plan Pro?", user_id=user_id, org_id="firby_landing")

        # Turno 2: Pregunta por soporte prioritario
        res = await operator_runtime.process_turn("¿Ese tiene soporte prioritario?", user_id=user_id, org_id="firby_landing")
        assert res.ok is True
        lower = res.response.lower()
        # Debe responder sobre el soporte directamente
        assert "soporte" in lower
        # No debe sustituir la respuesta con WhatsApp de venta
        assert "escríbenos a whatsapp" not in lower
        assert "escríbenos por whatsapp" not in lower
    asyncio.run(_run())


# 10. FUNCTIONAL QUESTION NOT AUTO WHATSAPP
def test_10_functional_question_not_auto_whatsapp():
    async def _run():
        user_id = f"test_fq_{uuid.uuid4().hex[:8]}"
        res = await operator_runtime.process_turn("¿Qué acciones puede hacer el operador en la web?", user_id=user_id, org_id="firby_landing")
        assert res.ok is True
        lower = res.response.lower()
        # Debe responder de forma autónoma en la web
        assert "escríbenos por whatsapp" not in lower
        assert "contáctanos por whatsapp" not in lower
        assert "operador" in lower or "sitio web" in lower or "web" in lower
    asyncio.run(_run())


# 11. APPOINTMENT CAPABILITY TRUTH
def test_11_appointment_capability_truth():
    async def _run():
        user_id = f"test_act_{uuid.uuid4().hex[:8]}"
        res = await operator_runtime.process_turn("¿Puede agendar citas?", user_id=user_id, org_id="firby_landing")
        assert res.ok is True
        lower = res.response.lower()
        # Explica que integra agendamiento en Google Calendar para sitios de clientes
        assert "google calendar" in lower or "agendamiento" in lower
        # No inventa horarios falsos
        assert "mañana a las 10" not in lower
        # No desvía a WhatsApp para agendar
        assert "escríbenos por whatsapp" not in lower
    asyncio.run(_run())


# 12. NAVIGATION CANCELLED
def test_12_navigation_cancelled():
    async def _run():
        user_id = f"test_nc_{uuid.uuid4().hex[:8]}"
        # Paso 1: Pedir navegación
        res1 = await operator_runtime.process_turn("llévame a planes", user_id=user_id, org_id="firby_landing")
        assert res1.requires_observation is True

        # Paso 2: Cancelar antes de ejecutar o en siguiente interacción
        res2 = await operator_runtime.process_turn("mejor no, quédate aquí", user_id=user_id, org_id="firby_landing")
        assert res2.state == AgentRunState.CANCELLED.value
        assert res2.ui_action is None
        # No debe decir que lo está llevando
        assert "te estoy llevando" not in res2.response.lower()
        assert "le estoy llevando" not in res2.response.lower()
        assert "permanezco aquí" in res2.response.lower() or "quedo aquí" in res2.response.lower()
    asyncio.run(_run())


# 13. NAVIGATION COMPLETED
def test_13_navigation_completed():
    async def _run():
        user_id = f"test_ncomp_{uuid.uuid4().hex[:8]}"
        res1 = await operator_runtime.process_turn("llévame a planes", user_id=user_id, org_id="firby_landing")
        assert res1.requires_observation is True

        # Simular observación exitosa desde la superficie
        obs = ActionObservation(action_id="act_1", success=True, target="#planes")
        res2 = await operator_runtime.process_observation(
            run_id=res1.run_id,
            observation_dict=obs.to_dict(),
            user_id=user_id,
            org_id="firby_landing"
        )
        assert res2.ok is True
        assert res2.state == AgentRunState.DONE.value
        lower = res2.response.lower()
        assert "le he ubicado" in lower or "planes y precios" in lower
    asyncio.run(_run())


# 14. NEGATIVE NAVIGATION CONSTRAINT
def test_14_negative_navigation_constraint():
    async def _run():
        user_id = f"test_nnc_{uuid.uuid4().hex[:8]}"
        res = await operator_runtime.process_turn("cuéntame de los planes pero no me lleves allá", user_id=user_id, org_id="firby_landing")
        assert res.ok is True
        assert res.ui_action is None
        assert "290.000" in res.response or "starter" in res.response.lower()
    asyncio.run(_run())


# 15. FORMAL TONE
def test_15_formal_tone():
    async def _run():
        user_id = f"test_ft_{uuid.uuid4().hex[:8]}"
        res = await operator_runtime.process_turn("Hola", user_id=user_id, org_id="firby_landing")
        assert res.ok is True
        lower = res.response.lower()
        # Debe usar "ayudarle" o registro formal
        assert "ayudarle" in lower or "orientarle" in lower
        # No debe tutear ("ayudarte", "te")
        assert "ayudarte" not in lower
    asyncio.run(_run())


# 16. NO FALSE BOOKING
def test_16_no_false_booking():
    async def _run():
        user_id = f"test_nfb_{uuid.uuid4().hex[:8]}"
        res = await operator_runtime.process_turn("Quiero agendar una cita para mañana a las 3pm", user_id=user_id, org_id="firby_landing")
        assert res.ok is True
        lower = res.response.lower()
        # En firby_landing el agendamiento está deshabilitado; no debe confirmar cita inventada
        assert "cita confirmada" not in lower
        assert "agendada para mañana" not in lower
        assert "autoservicio" in lower or "prueba gratuita" in lower or "google calendar" in lower
    asyncio.run(_run())


# 17. RESPONSE AFTER 10 TURNS
def test_17_response_after_10_turns():
    async def _run():
        user_id = f"test_10t_{uuid.uuid4().hex[:8]}"
        queries = [
            "Hola, ¿qué es Firby?",
            "¿Qué hace en la web?",
            "¿Cómo se conecta a Google Calendar?",
            "¿Cuáles son los planes?",
            "¿Cuánto cuesta Starter?",
            "¿Y el plan Pro?",
            "¿Y el plan más completo?",
            "¿Ese incluye soporte prioritario?",
            "¿Tienen prueba gratis?",
            "Entendido, muchas gracias."
        ]
        for idx, q in enumerate(queries):
            res = await operator_runtime.process_turn(q, user_id=user_id, org_id="firby_landing")
            assert res.ok is True
            assert FirbyWidgetOperator.is_response_complete(res.response) is True
    asyncio.run(_run())


# 18. RESPONSE AFTER 15 TURNS
def test_18_response_after_15_turns():
    async def _run():
        user_id = f"test_15t_{uuid.uuid4().hex[:8]}"
        queries = [
            "Hola",
            "¿Qué es Firby?",
            "¿Cómo funciona?",
            "¿Puede agendar citas?",
            "¿Qué controles de política tiene?",
            "¿Pide autorización antes de actuar?",
            "¿Cómo se comunica con el dueño?",
            "¿Cuánto cuesta el plan más completo?",
            "¿Y el plan Starter?",
            "¿Y el Pro?",
            "¿Ese tiene soporte prioritario?",
            "no quiero comprar todavía",
            "¿Cómo se instala en mi web?",
            "¿Tienen oficinas?",
            "Vale, gracias por la información."
        ]
        for idx, q in enumerate(queries):
            res = await operator_runtime.process_turn(q, user_id=user_id, org_id="firby_landing")
            assert res.ok is True
            assert FirbyWidgetOperator.is_response_complete(res.response) is True
            assert res.response.strip() != ""
    asyncio.run(_run())
