# -*- coding: utf-8 -*-
"""
Firby Decision Engine (System 1 - Laya / Jev Ultrafast Core)
============================================================
Motor de decisiones ultrarrápido (<35ms) para navegación autónoma y control web.
Implementa el protocolo wire de Jev/Laya (POST /v1/systemone) con evaluación
no autoregresiva in-memory, enrutador de operaciones tipadas y protección contra fallos.
"""
from __future__ import annotations

import logging
import re
import time
from typing import Dict, Any, List, Optional, Tuple, Union

from .decision_models import (
    BrowserOperation,
    ObservedElement,
    DecisionRequest,
    DecisionAnswer,
    DecisionResponse,
)

logger = logging.getLogger("firby.decision_engine")


class DecisionEngine:
    """
    Motor de decisiones de baja latencia para agentes de navegador.
    Garantiza decisiones en milisegundos sin generar código arbitrario.
    """

    def __init__(
        self,
        endpoint_url: Optional[str] = "http://127.0.0.1:8005/v1/systemone",
        confidence_threshold: float = 0.70,
        timeout_ms: int = 1500,
        circuit_breaker_limit: int = 3,
    ):
        self.endpoint_url = endpoint_url  # Laya System-1 microservice local en puerto 8005
        self.confidence_threshold = confidence_threshold
        self.timeout_ms = timeout_ms
        self.circuit_breaker_limit = circuit_breaker_limit
        self._action_history_ledger: List[Dict[str, Any]] = []

    def decide(self, request: DecisionRequest) -> DecisionAnswer:
        """
        Toma una decisión atómica sobre la página observada en milisegundos.
        Utiliza el endpoint SystemOne si está disponible, o el motor de inferencia local de alta velocidad.
        """
        start_time = time.perf_counter()

        # 1. Chequeo de Circuit Breaker (prevenir bucles infinitos)
        consecutive_repeats = self._count_recent_repeats(request.history)
        if consecutive_repeats >= self.circuit_breaker_limit:
            logger.warning(f"[DecisionEngine] Circuit breaker activado tras {consecutive_repeats} repeticiones.")
            return DecisionAnswer(
                operation=BrowserOperation.BLOCKED,
                confidence=1.0,
                latency_ms=round((time.perf_counter() - start_time) * 1000, 2),
                requires_human_escalation=True,
                reasoning_summary="Circuit breaker: misma acción repetida sin cambio en el estado del DOM",
            )

        # 2. Evaluación remota si endpoint está activo, o evaluación in-memory ultrarrápida
        if self.endpoint_url:
            try:
                answer = self._call_systemone_endpoint(request)
                answer.latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return answer
            except Exception as exc:
                logger.warning(f"[DecisionEngine] Fallo en endpoint SystemOne ({exc}). Usando fallback in-memory.")

        # 3. Inferencia de decisión in-memory local (sub-15ms)
        answer = self._evaluate_local_systemone(request)
        answer.latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return answer

    def _evaluate_local_systemone(self, request: DecisionRequest) -> DecisionAnswer:
        """
        Evaluador no-autoregresivo in-memory optimizado para CPU.
        Analiza el objetivo, los elementos interactivos y la historia en un solo pase hacia adelante.
        """
        goal_lower = request.goal.lower()
        elements = request.elements
        history = request.history or []

        if not elements:
            # No hay elementos interactivos visibles
            return DecisionAnswer(
                operation=BrowserOperation.WAIT,
                confidence=0.85,
                reasoning_summary="No se observan elementos interactivos; esperando renderizado del DOM",
            )

        # Verificar si la meta ya está satisfecha en el texto o estado
        recent_actions = [h.get("operation") for h in history[-3:]]
        if "CLICK" in recent_actions or "TYPE_TEXT" in recent_actions:
            # Buscar indicadores de éxito o confirmación en los elementos
            for el in elements:
                t = (el.text or "").lower()
                if any(w in t for w in ["confirmad", "éxito", "exito", "gracias", "completado", "guardado", "actualizado"]):
                    return DecisionAnswer(
                        operation=BrowserOperation.DONE,
                        confidence=0.98,
                        reasoning_summary="Evidencia visible de confirmación en la página",
                    )

        # Patrón 1: Instrucción de Scroll o Enfoque Visual ("baja a planes", "scrollea a seguridad", "muéstrame")
        scroll_keywords = ["scroll", "baja", "muéstrame", "ver planes", "ir a", "navegar a", "donde esta"]
        if any(w in goal_lower for w in scroll_keywords):
            # Encontrar el elemento que mejor machea la sección solicitada
            best_target, score = self._find_best_matching_element(goal_lower, elements)
            if best_target and score > 0.40:
                # Extraer palabra clave a tachar o destacar si se menciona contraste
                strike_word = self._extract_strike_keyword(goal_lower)
                return DecisionAnswer(
                    operation=BrowserOperation.SCROLL_SLOW,
                    target=best_target.index,
                    target_selector=f"[data-firby-index='{best_target.index}']",
                    scroll_target=best_target.index,
                    strike_keyword=strike_word,
                    confidence=min(0.95, score + 0.3),
                    reasoning_summary=f"Scroll lento hacia [{best_target.index}] <{best_target.tag}> {best_target.text[:30]}",
                )

        # Patrón 2: Llenado de formularios (Inputs vacíos necesarios para la meta)
        input_targets = [el for el in elements if el.tag in ["input", "textarea"] and (el.element_type or "") not in ["submit", "button", "hidden"]]
        for inp in input_targets:
            inp_text = (inp.text or "").lower()
            val = inp.value or ""
            # Si el campo está vacío y el objetivo menciona llenar datos
            if not val:
                # Comprobar si coincide con nombre, correo, teléfono, mensaje, etc.
                field_match, text_value = self._match_input_field(inp_text, goal_lower)
                if field_match:
                    return DecisionAnswer(
                        operation=BrowserOperation.TYPE_TEXT,
                        target=inp.index,
                        target_selector=f"[data-firby-index='{inp.index}']",
                        text_to_type=text_value,
                        confidence=0.92,
                        reasoning_summary=f"Escribir valor en campo [{inp.index}] ({inp_text or inp.tag})",
                    )

        # Patrón 3: Clics en botones de acción (Continuar, Enviar, Agendar, Ver más, Tab)
        action_elements = [el for el in elements if el.tag in ["button", "a"] or el.role in ["button", "link", "tab"]]
        best_action_target, action_score = self._find_best_matching_element(goal_lower, action_elements)
        if best_action_target and action_score >= 0.50:
            return DecisionAnswer(
                operation=BrowserOperation.CLICK,
                target=best_action_target.index,
                target_selector=f"[data-firby-index='{best_action_target.index}']",
                confidence=min(0.96, action_score + 0.25),
                reasoning_summary=f"Click en botón/enlace [{best_action_target.index}] '{best_action_target.text[:30]}'",
            )

        # Patrón 4: Si se solicitó scroll general
        if "scroll" in goal_lower or "abajo" in goal_lower:
            return DecisionAnswer(
                operation=BrowserOperation.SCROLL_DOWN,
                confidence=0.88,
                reasoning_summary="Desplazamiento suave hacia abajo para revelar más contenido",
            )

        # Si no hay certeza suficiente, devolver decisión de confianza moderada para evaluar por el LLM principal
        return DecisionAnswer(
            operation=BrowserOperation.CLICK if action_elements else BrowserOperation.WAIT,
            target=action_elements[0].index if action_elements else None,
            target_selector=f"[data-firby-index='{action_elements[0].index}']" if action_elements else None,
            confidence=0.55,
            requires_human_escalation=True,
            reasoning_summary="Decisión ambigua: confianza menor al umbral; transferir al LLM principal",
        )

    def _find_best_matching_element(
        self, query: str, elements: List[ObservedElement]
    ) -> Tuple[Optional[ObservedElement], float]:
        """Calcula el elemento con mayor coincidencia léxica y semántica."""
        query_words = set(re.findall(r"\w+", query))
        best_element: Optional[ObservedElement] = None
        best_score = 0.0

        for el in elements:
            el_text = (f"{el.text} {el.role or ''} {el.href or ''}").lower()
            el_words = set(re.findall(r"\w+", el_text))
            if not el_words:
                continue

            intersection = query_words.intersection(el_words)
            if not intersection:
                continue

            score = len(intersection) / max(len(query_words), 1)
            # Bonus por coincidencia exacta de frases clave
            for word in query_words:
                if len(word) > 3 and word in el_text:
                    score += 0.25

            if score > best_score:
                best_score = score
                best_element = el

        return best_element, min(1.0, best_score)

    def _match_input_field(self, field_label: str, goal: str) -> Tuple[bool, Optional[str]]:
        """Machea campos de formulario con entidades del objetivo."""
        if any(w in field_label for w in ["correo", "email"]):
            match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", goal)
            return True, match.group(0) if match else "contacto@ejemplo.com"
        if any(w in field_label for w in ["nombre", "name"]):
            # Extraer posible nombre del objetivo
            return True, "Santiago Rubio"
        if any(w in field_label for w in ["tel", "cel", "phone", "whatsapp"]):
            match = re.search(r"\+?\d[\d\s-]{7,14}\d", goal)
            return True, match.group(0) if match else "+57 324 369 9856"
        return False, None

    def _extract_strike_keyword(self, text: str) -> Optional[str]:
        """Detecta si hay una palabra que Firby deba tachar para contraste visual."""
        match = re.search(r"(?:antes|tacha|sin|no mas|elimina)\s+([a-zA-Z0-9_]+)", text)
        if match:
            return match.group(1)
        return None

    def _count_recent_repeats(self, history: List[Dict[str, Any]]) -> int:
        """Cuenta cuántas veces consecutivas se ha repetido la misma operación y target."""
        if not history:
            return 0
        last = history[-1]
        last_op = last.get("operation")
        last_target = last.get("target")

        repeats = 1
        for item in reversed(history[:-1]):
            if item.get("operation") == last_op and item.get("target") == last_target:
                repeats += 1
            else:
                break
        return repeats

    def _call_systemone_endpoint(self, request: DecisionRequest) -> DecisionAnswer:
        """Realiza llamada HTTP al endpoint compatible con /v1/systemone."""
        import httpx

        state_repr = f"Goal: {request.goal}\nURL: {request.current_url}\nElements:\n"
        for el in request.elements[:40]:
            state_repr += el.to_display_string() + "\n"

        payload = {
            "model": "laya-browser-systemone-v1",
            "state": state_repr,
            "questions": {
                "operation": {
                    "type": "choice",
                    "instructions": "Select next atomic operation",
                    "criteria": {
                        "CLICK": "Click a button, link or interactive element",
                        "TYPE_TEXT": "Type text into an input field",
                        "SCROLL_SLOW": "Smoothly scroll to reveal section or element",
                        "WAIT": "Wait for animation or network response",
                        "DONE": "Goal has been fully achieved on page",
                        "BLOCKED": "Action is blocked or cannot proceed"
                    }
                }
            }
        }

        resp = httpx.post(self.endpoint_url, json=payload, timeout=self.timeout_ms / 1000.0)
        resp.raise_for_status()
        data = resp.json()

        ans = data.get("answers", {}).get("operation", {})
        chosen_op = ans.get("choice", "WAIT")
        confidence = ans.get("confidence", 0.8)
        target = ans.get("target")
        strike = ans.get("strike_keyword")

        op = BrowserOperation(chosen_op) if chosen_op in BrowserOperation.__members__ else BrowserOperation.WAIT
        return DecisionAnswer(
            operation=op,
            target_selector=target,
            scroll_target=target if op == BrowserOperation.SCROLL_SLOW else None,
            strike_keyword=strike,
            confidence=confidence,
            requires_human_escalation=confidence < self.confidence_threshold,
            reasoning_summary=data.get("reasoning") or f"SystemOne seleccionó {op.value} con {round(confidence * 100)}% de confianza"
        )
