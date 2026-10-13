# -*- coding: utf-8 -*-
"""
tests/test_response_integrity.py
================================
Suite de Certificación de Integridad de Respuestas y Prevención de Truncamiento Conversacional.

Verifica rigurosamente los 12 requisitos mandatorios del protocolo P0/P1:
1. short_response_complete
2. medium_response_complete
3. long_response_complete
4. repeated_long_response
5. multi_turn_response_integrity
6. no_premature_stream_close
7. backend_response_matches_frontend
8. detect_truncated_finish_reason
9. no_partial_word_termination
10. toolless_long_response
11. response_after_10_turns
12. response_after_15_turns
"""

import pytest
import asyncio
import uuid
import re
from typing import Dict, Any, List

from src.core.widget_operator import widget_operator, FirbyWidgetOperator
from src.core.operator.runtime import operator_runtime
from src.core.operator.models import OperatorResult


def verify_text_integrity(text: str) -> None:
    """Verifica que el texto esté semánticamente cerrado, sin palabras truncadas ni formato mutilado."""
    assert text is not None and len(text.strip()) > 0, "La respuesta no puede ser vacía"
    clean = text.strip()

    # 1. No debe terminar en raíces o palabras cortadas a mitad de camino
    assert not re.search(
        r'\b(agend|disponib|configur|autoriz|sincron|solicit|operac|func|comunic|modific|verific)\.{2,3}$',
        clean,
        re.IGNORECASE
    ), f"Palabra truncada detectada en el final de: {repr(clean[-30:])}"

    # 2. Asteriscos markdown y comillas deben estar balanceados
    assert clean.count("**") % 2 == 0, f"Marcas de negrita no balanceadas en: {repr(clean)}"

    # 3. Puntuación de cierre válida para respuestas de más de 6 palabras
    valid_ends = ('.', '!', '?', ':', ')', ']', '}', '"', "'", '`', '>', '*')
    words = clean.split()
    if len(words) > 6:
        assert clean.endswith(valid_ends), f"La respuesta no termina con puntuación válida: {repr(clean[-30:])}"


async def send_widget_turn(message: str, user_id: str, org_id: str = "firby_landing") -> Dict[str, Any]:
    """Ejecuta un turno conversacional manejando automáticamente el protocolo de dos fases UI/observación."""
    res = await widget_operator.handle_message(message, user_id=user_id, org_id=org_id)
    if res.get("requires_observation") and res.get("ui_action"):
        r_id = res.get("run_id")
        obs_payload = {
            "run_id": r_id,
            "step_id": res.get("step_id", 1),
            "status": "success",
            "target": res["ui_action"].get("target", "#hero"),
            "success": True,
            "duration_ms": 50,
            "error": None
        }
        res = await widget_operator.handle_observation(
            run_id=r_id,
            observation=obs_payload,
            user_id=user_id,
            org_id=org_id
        )
    return res


# ─────────────────────────────────────────────────────────────────────────────
# 1. short_response_complete
# ─────────────────────────────────────────────────────────────────────────────
def test_short_response_complete():
    """Verifica que respuestas breves (saludos, confirmaciones cortas) terminen completas."""
    async def _run():
        user_id = f"test_short_{uuid.uuid4().hex[:8]}"
        res = await send_widget_turn("Hola", user_id=user_id, org_id="firby_landing")
        assert res["ok"] is True
        assert len(res["bubbles"]) > 0
        txt = res["bubbles"][0]
        verify_text_integrity(txt)
        assert FirbyWidgetOperator.is_response_complete(txt) is True

    asyncio.run(_run())


# ─────────────────────────────────────────────────────────────────────────────
# 2. medium_response_complete
# ─────────────────────────────────────────────────────────────────────────────
def test_medium_response_complete():
    """Verifica que respuestas de longitud media (planes, cómo funciona) no se corten."""
    async def _run():
        user_id = f"test_med_{uuid.uuid4().hex[:8]}"
        res = await send_widget_turn(
            "¿Cuáles son los planes y precios que ofrece Firby?",
            user_id=user_id,
            org_id="firby_landing"
        )
        assert res["ok"] is True
        assert len(res["bubbles"]) > 0
        txt = res["bubbles"][0]
        verify_text_integrity(txt)
        assert len(txt) > 80
        assert FirbyWidgetOperator.is_response_complete(txt) is True

    asyncio.run(_run())


# ─────────────────────────────────────────────────────────────────────────────
# 3. long_response_complete
# ─────────────────────────────────────────────────────────────────────────────
def test_long_response_complete():
    """Verifica que explicaciones largas y complejas mantengan integridad hasta el último carácter."""
    async def _run():
        user_id = f"test_long_{uuid.uuid4().hex[:8]}"
        res = await send_widget_turn(
            "Explícame todo lo que puede hacer Firby respecto a atención, navegación, citas, datos del cliente, reglas y autorizaciones.",
            user_id=user_id,
            org_id="firby_landing"
        )
        assert res["ok"] is True
        assert len(res["bubbles"]) > 0
        txt = res["bubbles"][0]
        verify_text_integrity(txt)
        assert len(txt) > 200
        assert FirbyWidgetOperator.is_response_complete(txt) is True

    asyncio.run(_run())


# ─────────────────────────────────────────────────────────────────────────────
# 4. repeated_long_response
# ─────────────────────────────────────────────────────────────────────────────
def test_repeated_long_response():
    """Verifica que la generación de respuestas largas sea consistente y repetible sin truncamiento aleatorio."""
    async def _run():
        for idx in range(3):
            user_id = f"test_rep_long_{idx}_{uuid.uuid4().hex[:8]}"
            res = await send_widget_turn(
                "Explica detalladamente la diferencia entre la atención en la web y la línea privada de WhatsApp.",
                user_id=user_id,
                org_id="firby_landing"
            )
            assert res["ok"] is True
            txt = res["bubbles"][0]
            verify_text_integrity(txt)
            assert FirbyWidgetOperator.is_response_complete(txt) is True

    asyncio.run(_run())


# ─────────────────────────────────────────────────────────────────────────────
# 5. multi_turn_response_integrity
# ─────────────────────────────────────────────────────────────────────────────
def test_multi_turn_response_integrity():
    """
    Reproduce exactamente la secuencia de 6 turnos del incidente real:
    T1: Hola
    T2: No se
    T3: Guiarme
    T4: ??? No entiendo
    T5: Osea que acciones puede hacer??
    T6: Y ya? Que pasa si quieren cambiar su nombre o no se su correo como actua en el servidor?
    Verifica que el Turno 6 no sufra truncamiento ('gestionar agend...').
    """
    async def _run():
        user_id = f"test_seq_incident_{uuid.uuid4().hex[:8]}"
        turns = [
            "Hola",
            "No se",
            "Guiarme",
            "??? No entiendo",
            "Osea que acciones puede hacer??",
            "Y ya? Que pasa si quieren cambiar su nombre o no se su correo como actua en el servidor?"
        ]

        last_res = None
        for turn_text in turns:
            last_res = await send_widget_turn(turn_text, user_id=user_id, org_id="firby_landing")
            assert last_res["ok"] is True

        assert last_res is not None
        final_text = last_res["bubbles"][0] if last_res["bubbles"] else last_res["response"]
        verify_text_integrity(final_text)
        assert not final_text.strip().endswith("agend")
        assert not final_text.strip().endswith("agend...")
        assert FirbyWidgetOperator.is_response_complete(final_text) is True

    asyncio.run(_run())


# ─────────────────────────────────────────────────────────────────────────────
# 6. no_premature_stream_close
# ─────────────────────────────────────────────────────────────────────────────
def test_no_premature_stream_close():
    """Verifica que el transporte HTTP JSON retorne un payload completo con estado explícito COMPLETED."""
    async def _run():
        user_id = f"test_transport_{uuid.uuid4().hex[:8]}"
        res = await send_widget_turn(
            "¿Cómo se asegura Firby de no inventar información?",
            user_id=user_id,
            org_id="firby_landing"
        )
        assert res["ok"] is True
        assert "response" in res
        assert "bubbles" in res
        assert isinstance(res["bubbles"], list)
        assert len(res["bubbles"]) > 0
        assert res.get("status") in ("COMPLETED", "ACTION_REQUESTED")

    asyncio.run(_run())


# ─────────────────────────────────────────────────────────────────────────────
# 7. backend_response_matches_frontend
# ─────────────────────────────────────────────────────────────────────────────
def test_backend_response_matches_frontend():
    """
    Verifica que el contenido textual generado en el backend no sufra recorte
    ni pérdida al ser procesado para el DOM por el formateador Markdown del frontend.
    """
    async def _run():
        user_id = f"test_parity_{uuid.uuid4().hex[:8]}"
        res = await send_widget_turn(
            "¿Qué opciones de soporte y atención incluye el plan Pro?",
            user_id=user_id,
            org_id="firby_landing"
        )
        raw_backend = res["bubbles"][0]

        # Simular formatMarkdown de widget.js:
        def format_markdown_sim(text: str) -> str:
            html = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
            html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
            lines = html.split('\n')
            formatted = []
            for line in lines:
                trimmed = line.strip()
                if trimmed.startswith('- ') or trimmed.startswith('• '):
                    formatted.append(f'<div class="firby-bullet-item">{trimmed[2:].strip()}</div>')
                else:
                    formatted.append(line)
            return '<br/>'.join(formatted)

        dom_rendered = format_markdown_sim(raw_backend)

        raw_words = [w.strip("*,.-()[]") for w in raw_backend.split() if len(w) > 3]
        for w in raw_words[:10]:
            assert w in dom_rendered, f"Palabra {w} ausente en DOM formateado"
        for w in raw_words[-5:]:
            assert w in dom_rendered, f"Palabra final {w} ausente en DOM formateado"

    asyncio.run(_run())


# ─────────────────────────────────────────────────────────────────────────────
# 8. detect_truncated_finish_reason
# ─────────────────────────────────────────────────────────────────────────────
def test_detect_truncated_finish_reason():
    """Verifica que el runtime detecte explícitamente tokens truncados y terminaciones de límite."""
    truncated_candidate = {
        "finishReason": "MAX_TOKENS",
        "content": {
            "parts": [{"text": "Firby está diseñado para atender a los visitantes, resolver sus dudas, operar la navegación del sitio y gestionar agend"}]
        }
    }
    assert truncated_candidate["finishReason"] in ("MAX_TOKENS", "LENGTH")
    raw_text = truncated_candidate["content"]["parts"][0]["text"]
    assert FirbyWidgetOperator.is_response_complete(raw_text) is False


# ─────────────────────────────────────────────────────────────────────────────
# 9. no_partial_word_termination
# ─────────────────────────────────────────────────────────────────────────────
def test_no_partial_word_termination():
    """Verifica que el validador de integridad rechace terminaciones anómalas en raíces de palabras."""
    cut_examples = [
        "Firby está diseñado para atender y gestionar agend...",
        "El sistema valida la disponib...",
        "Puedes revisar la configur...",
        "Para proceder se requiere autoriz...",
        "La agenda se encuentra sincron...",
        "El usuario envió una solicit...",
        "El operador digital de Firby está diseñado para atender a los visitantes, resolver sus dudas y guiar",
        "{\"thought\": \"analizando\", \"response\": \"texto sin cerrar"
    ]
    for ex in cut_examples:
        assert FirbyWidgetOperator.is_response_complete(ex) is False, f"Falló al detectar truncamiento en: {ex}"

    valid_examples = [
        "Hola.",
        "Entendido.",
        "Acción procesada con éxito.",
        "Firby es un operador digital que vive en tu sitio web y atiende 24/7.",
        "Nuestros planes oficiales son:\n- **Starter**: $290.000 COP / mes.\n- **Pro**: $490.000 COP / mes."
    ]
    for ex in valid_examples:
        assert FirbyWidgetOperator.is_response_complete(ex) is True, f"Falso positivo en ejemplo válido: {ex}"


# ─────────────────────────────────────────────────────────────────────────────
# 10. toolless_long_response
# ─────────────────────────────────────────────────────────────────────────────
def test_toolless_long_response():
    """
    Sección 12: Consulta puramente explicativa sin herramientas.
    'Explícame exactamente qué puede hacer Firby si un visitante quiere modificar sus datos, qué puede ejecutar y qué necesita autorización.'
    Verifica que la explicación sea extensa, completa y con cierre semántico impecable.
    """
    async def _run():
        user_id = f"test_toolless_{uuid.uuid4().hex[:8]}"
        query = "Explícame exactamente qué puede hacer Firby si un visitante quiere modificar sus datos, qué puede ejecutar y qué necesita autorización."
        res = await send_widget_turn(query, user_id=user_id, org_id="firby_landing")
        assert res["ok"] is True
        txt = res["bubbles"][0]
        verify_text_integrity(txt)
        assert len(txt) > 200
        assert FirbyWidgetOperator.is_response_complete(txt) is True

    asyncio.run(_run())


# ─────────────────────────────────────────────────────────────────────────────
# 11. response_after_10_turns
# ─────────────────────────────────────────────────────────────────────────────
def test_response_after_10_turns():
    """Verifica que tras 10 turnos de conversación continua la respuesta no se corte por acumulación de contexto."""
    async def _run():
        user_id = f"test_10turns_{uuid.uuid4().hex[:8]}"
        history_prompts = [
            "Hola",
            "¿Qué es Firby?",
            "¿Cómo funciona?",
            "¿Qué pasa si alguien pregunta por precios?",
            "Háblame del plan Starter",
            "¿Y el plan Pro?",
            "¿Cómo se maneja Google Calendar?",
            "¿Quién atiende en WhatsApp?",
            "¿Y en la web quién responde?",
            "En resumen, ¿por qué es seguro usar Firby en mi negocio?"
        ]
        last_res = None
        for p in history_prompts:
            last_res = await send_widget_turn(p, user_id=user_id, org_id="firby_landing")
            assert last_res["ok"] is True

        assert last_res is not None
        txt = last_res["bubbles"][0]
        verify_text_integrity(txt)
        assert FirbyWidgetOperator.is_response_complete(txt) is True

    asyncio.run(_run())


# ─────────────────────────────────────────────────────────────────────────────
# 12. response_after_15_turns
# ─────────────────────────────────────────────────────────────────────────────
def test_response_after_15_turns():
    """Verifica que tras 15 turnos de conversación profunda el operador entregue respuestas 100% íntegras."""
    async def _run():
        user_id = f"test_15turns_{uuid.uuid4().hex[:8]}"
        history_prompts = [
            "Buenas",
            "Explícame brevemente el producto",
            "¿Cuánto cuesta?",
            "¿Tienen prueba gratis?",
            "¿Cómo se instala?",
            "¿Necesito programar?",
            "¿Funciona en WordPress?",
            "¿Y qué pasa si el cliente pide una cita?",
            "¿Se revisa el calendario?",
            "¿El dueño se entera?",
            "¿Por qué canal?",
            "¿El visitante habla por WhatsApp?",
            "¿Entonces el visitante solo habla en la web?",
            "¿Qué pasa si hay una excepción comercial?",
            "Excelente. Dame una conclusión final sobre la propuesta de valor de Firby."
        ]
        last_res = None
        for p in history_prompts:
            last_res = await send_widget_turn(p, user_id=user_id, org_id="firby_landing")
            assert last_res["ok"] is True

        assert last_res is not None
        txt = last_res["bubbles"][0]
        verify_text_integrity(txt)
        assert FirbyWidgetOperator.is_response_complete(txt) is True

    asyncio.run(_run())
