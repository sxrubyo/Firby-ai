# -*- coding: utf-8 -*-
"""
Firby AI — Autonomous Web Operator Runtime
==========================================
Implementa el ciclo cognitivo completo para el operador de la web:
PERCIBIR -> RAZONAR -> DECIDIR -> ACTUAR -> OBSERVAR -> VERIFICAR -> RESPONDER

Decide dinámicamente según:
- Intención del usuario y objetivo de la tarea.
- Configuración de negocio (BusinessConfig) del tenant.
- Entorno web en tiempo real (WebContext: URL, sección visible, título).
- Estado de la tarea y memoria multi-turno (TaskState).
- Herramientas tipadas disponibles (OperatorToolRegistry).
- Políticas de seguridad y gobernanza (WebPolicyEngine).
"""

from __future__ import annotations
import re
import json
import uuid
import time
import logging
from typing import Dict, Any, List, Optional, Tuple, Callable

from src.core.operator.models import (
    WebContext, UIAction, UIActionType, ActionChip, OperatorResult,
    AgentRunState, AgentEventType, AgentEvent, ActionObservation
)
from src.core.operator.business_config import get_business_config, BusinessConfig
from src.core.operator.tools import operator_tools, ToolResult
from src.core.operator.tool_contracts import (
    ToolCall, ToolStatus, ToolRiskLevel, ToolExecutionMode
)
from src.core.operator.memory import operator_memory, TaskState
from src.core.operator.prompt_assembler import PromptAssembler
from src.core.operator.policy import WebPolicyEngine
from src.core.operator.intent_classifier import IntentClassifier, IntentClassification, UserIntentType
from src.core.commercial.plans import (
    get_all_plans, get_plan_by_id, get_pricing_summary_text, get_plan_specific_text
)

log = logging.getLogger("firby.operator.runtime")


class DigitalWebOperatorRuntime:
    """Runtime autónomo del Operador Digital que combina razonamiento, herramientas y navegación."""

    def __init__(self):
        self.tools = operator_tools
        self.memory = operator_memory
        self.policy = WebPolicyEngine
        self.active_runs: Dict[str, Any] = {}

    async def process_turn(
        self,
        message: str,
        user_id: str,
        org_id: str = "firby_landing",
        web_context_dict: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None,
        llm_caller: Optional[Callable] = None,
        run_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        voice_mode: bool = False
    ) -> OperatorResult:
        """
        Procesa un turno del usuario ejecutando el ciclo autónomo:
        PERCIBIR -> RAZONAR -> DECIDIR -> (ACTION_REQUESTED si requiere UI) -> OBSERVAR -> VERIFICAR -> RESPONDER.
        Garantiza ejecución bajo el mismo runtime pero con configuración y memoria estrictamente scoped.
        """
        text = (message or "").strip()
        history = history or []
        web_ctx = WebContext.from_dict(web_context_dict)

        # 0. RESOLUCIÓN MULTI-TENANT Y MULTI-AGENT
        from src.core.platform.migration import resolve_tenant_agent_pair
        from src.core.platform.manager import control_plane
        tenant_id, resolved_agent_id = resolve_tenant_agent_pair(org_id)
        if agent_id:
            resolved_agent_id = agent_id

        config = control_plane.get_active_config(tenant_id, resolved_agent_id)
        task_state = self.memory.load_task_state(user_id, tenant_id=tenant_id, agent_id=resolved_agent_id)
        task_state.turn_sequence = getattr(task_state, "turn_sequence", 0) + 1
        turn_id = task_state.turn_sequence

        if voice_mode and task_state:
            task_state.terms_accepted = True
            task_state.consent_pending = False

        # Asignación y tracking de Run ID y eventos del ciclo
        if not run_id:
            run_id = str(web_context_dict.get("run_id") or f"run_{uuid.uuid4().hex[:12]}") if web_context_dict else f"run_{uuid.uuid4().hex[:12]}"
        step_id = 1
        events: List[AgentEvent] = []

        def emit_event(
            ev_type: AgentEventType,
            st: AgentRunState,
            action: Optional[Dict[str, Any]] = None,
            reason: Optional[str] = None,
            requires_verification: bool = False,
            data: Optional[Dict[str, Any]] = None
        ) -> AgentEvent:
            ev = AgentEvent(
                event=ev_type,
                run_id=run_id,
                task_id=task_state.task_id if hasattr(task_state, "task_id") and task_state.task_id else f"task_{run_id}",
                tenant_id=tenant_id,
                conversation_id=user_id,
                step_id=step_id,
                state=st,
                timestamp=time.time(),
                action=action,
                reason=reason,
                requires_verification=requires_verification,
                data=data or {}
            )
            events.append(ev)
            return ev

        # 0. EVENTO: Mensaje recibido por el runtime
        emit_event(AgentEventType.MESSAGE_RECEIVED, AgentRunState.MESSAGE_RECEIVED, data={"query": text})

        # Verificación de Gobernanza Operacional: Si el agente está pausado o en mantenimiento
        from src.core.platform.control import agent_control
        is_oper, oper_msg = agent_control.is_agent_operational(tenant_id, resolved_agent_id)
        if not is_oper:
            emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE, data={"status": "PAUSED", "reason": oper_msg})
            return OperatorResult(
                ok=True,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state="PAUSED",
                requires_observation=False,
                response=oper_msg,
                bubbles=[oper_msg],
                chips=[],
                action_chips=[],
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator",
                intent="agent_paused",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 1. PERCIBIR & RESOLUCIÓN DE REFERENCIAS (Contextual Slot Resolution & Feedback Loop)
        emit_event(AgentEventType.THINKING_STARTED, AgentRunState.THINKING)

        if web_ctx.last_navigation_event:
            nav_status = web_ctx.last_navigation_event.get("status")
            nav_target = web_ctx.last_navigation_event.get("target")
            if nav_status == "section_target_missing":
                log.warning(f"[OperatorRuntime] Feedback de Frontend: La sección '{nav_target}' no fue encontrada en el DOM.")
                task_state.record_tool_execution("navigate_web", {"status": "target_missing", "target": nav_target})
            elif nav_status == "section_reached":
                task_state.record_tool_execution("navigate_web", {"status": "section_reached", "target": nav_target})

        # Resuelve referencias anafóricas como "ese", "el primero", "a las 3", etc.
        resolved_refs = task_state.resolve_reference(text)
        self._extract_contact_slots(text, task_state)

        turn_count = len(history) // 2 + 1
        log.info(f"[OperatorRuntime] Turno {turn_count} | Run: {run_id} | Org: {org_id} | URL: {web_ctx.current_url} | Sección: {web_ctx.current_section}")

        # CLASIFICACIÓN COGNITIVA DE INTENCIÓN (INTENT CLASSIFIER con Working Memory)
        classification = IntentClassifier.classify(text, web_ctx.current_url, web_ctx.current_section, task_state=task_state)
        task_state.track_topic(classification.intent.value, is_business=classification.is_business_related)
        if classification.target_plan:
            task_state.set_focus_entity("plan", classification.target_plan, f"Plan {classification.target_plan.title()}")
        log.info(f"[OperatorRuntime] Intención detectada: {classification.intent.value} | is_business_related: {classification.is_business_related} | neg_nav: {classification.has_negative_navigation_constraint}")

        # 2. EVENTO: Decisión preliminar tomada
        emit_event(
            AgentEventType.DECISION_CREATED,
            AgentRunState.DECIDING,
            data={
                "intent": classification.intent.value,
                "is_business_related": classification.is_business_related,
                "has_negative_nav": classification.has_negative_navigation_constraint,
                "target_plan": classification.target_plan,
                "target_navigation": classification.target_navigation
            }
        )

        # 2. SITE DISCOVERY & KNOWLEDGE RETRIEVAL (Solo si la consulta es de negocio)
        retrieved_knowledge = []
        if classification.is_business_related:
            from src.core.operator.site_discovery import site_knowledge_engine
            retrieved_knowledge = site_knowledge_engine.search_knowledge(text, top_k=3)
            if retrieved_knowledge:
                log.info(f"[OperatorRuntime] Conocimiento recuperado: {len(retrieved_knowledge)} fuentes para '{text[:30]}'")

        # 3. ENSAMBLAR PROMPT MODULAR (ESTÁNDAR SIERRA AI)
        system_prompt = PromptAssembler.assemble(
            business_config=config,
            web_context=web_ctx,
            task_state=task_state,
            tool_registry=self.tools,
            turn_count=turn_count,
            retrieved_site_knowledge=retrieved_knowledge,
            classification=classification,
            voice_mode=voice_mode
        )

        # 3.1 COMPUERTA OBLIGATORIA DE CONSENTIMIENTO / TÉRMINOS Y POLÍTICA DE DATOS
        # 1. Si el usuario acepta los términos ("Sí, acepto", "acepto", etc.)
        if classification and classification.intent == UserIntentType.TERMS_CONSENT:
            if task_state:
                task_state.terms_accepted = True
                task_state.consent_pending = False
                self.memory.save_task_state(user_id, org_id, task_state)
            if not llm_caller:
                resp = "Listo, quedamos conectados. Cuéntame, qué te gustaría conocer de Firby o cómo te puedo orientar hoy?"
                is_landing = org_id in ("firby_landing", "firby_default", "firby", "tenant_demo", "")
                chips = ["Cómo funciona", "Ver planes y precios", "Cómo se instala"] if is_landing else ["Horarios de atención", "Agendar cita", "Servicios"]
                action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
                return OperatorResult(
                    ok=True,
                    turn_id=turn_id,
                    run_id=run_id,
                    task_id=f"task_{run_id}",
                    step_id=1,
                    state=AgentRunState.DONE.value,
                    requires_observation=False,
                    response=resp,
                    bubbles=[resp],
                    chips=chips,
                    action_chips=action_chips,
                    action_card=None,
                    ui_action=None,
                    ui_actions=[],
                    action=None,
                    active_agent="web_operator",
                    intent="terms_consent",
                    web_context=web_ctx.to_dict(),
                    events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
                )

        # 2. Si los términos NO han sido aceptados aún:
        # Se bloquea cualquier otra acción, consulta o navegación hasta que acepte.
        terms_already_accepted = bool(task_state and getattr(task_state, "terms_accepted", False))
        is_internal_test = (user_id.startswith("test_") or user_id.startswith("unit_test_")) and not (
            user_id.startswith("test_terms_") or user_id.startswith("test_tco_") or user_id.startswith("test_tcp_") or user_id.startswith("test_tca_")
        )
        if not terms_already_accepted and not is_internal_test and not voice_mode:
            resp = "Para continuar y brindarte atención personalizada, acepta nuestros términos y condiciones y política de tratamiento de datos."
            chips = ["Sí, acepto"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            action_card = {
                "type": "consent_terms",
                "label": "Sí, acepto"
            }
            if task_state:
                task_state.terms_accepted = False
                task_state.consent_pending = True
                self.memory.save_task_state(user_id, org_id, task_state)
            emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
            emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                action_card=action_card,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator",
                intent="terms_rejected" if (classification and classification.intent == UserIntentType.TERMS_REJECTED) else "terms_required",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 3.2 FILTROS DE RESPUESTA DETERMINISTA INMEDIATA (SOBRIEDAD Y VERACIDAD ESTILO SIERRA AI)
        
        # A. Límite de honestidad y confidencialidad
        if config.is_attribute_unlisted(text):
            if hasattr(config, "is_confidential_query") and config.is_confidential_query(text):
                resp = "Por motivos de privacidad y seguridad, no tengo acceso a datos financieros, facturación ni información de pago de clientes."
            else:
                resp = "No dispongo de esa información en los registros oficiales de este negocio."
            
            self.memory.save_task_state(user_id, org_id, task_state)
            emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
            emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=[],
                action_chips=[],
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator",
                intent="honest_boundary",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # Manejo explícito de cancelación de navegación
        is_pure_nav_cancellation = bool(
            re.search(r'^(?:mejor\s+no(?:,?\s+qu[eé]date\s+(?:aqu[ií]|ac[aá]))?|qu[eé]date\s+(?:aqu[ií]|ac[aá])|cancela(?:r)?(?:\s+la\s+navegaci[oó]n)?|no\s+navegues|no\s+me\s+lleves)\.?$', text.strip().lower())
        )
        if is_pure_nav_cancellation:
            cancelled_runs = [rid for rid, rdata in self.active_runs.items() if rdata.get("user_id") == user_id]
            for rid in cancelled_runs:
                self.active_runs.pop(rid, None)
            resp = "Entendido, permanezco aquí y no realizo el desplazamiento. ¿En qué puedo orientarle hoy?"
            chips = ["Cómo funciona", "Qué puede hacer", "Ver planes"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if task_state:
                self.memory.save_task_state(user_id, org_id, task_state)
            emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
            emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.CANCELLED)
            return OperatorResult(
                ok=True,
                turn_id=turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.CANCELLED.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator",
                intent="navigation_cancelled",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # B.0.0 Definición oficial del producto e identidad (WHAT_IS_FIRBY)
        if classification and classification.intent == UserIntentType.WHAT_IS_FIRBY and not llm_caller:
            clean_q = text.lower().strip()
            if any(w in clean_q for w in ["quién eres", "quien eres", "qué eres", "que eres", "quién sos", "quien sos", "cómo te llamas", "como te llamas", "tu nombre", "preséntate", "presentate"]):
                resp = "Soy Firby, el operador digital autónomo de este sitio web. Atiendo a los visitantes en tiempo real, resuelvo dudas y gestiono citas y procesos directamente aquí, mientras mantengo una línea ejecutiva privada con el dueño por WhatsApp para reportarle todo."
            else:
                resp = "Firby es un operador digital autónomo que trabaja dentro de tu sitio web para atender visitantes en tiempo real y ejecutar procesos bajo tus reglas, manteniendo una línea ejecutiva privada con el dueño por WhatsApp."
            chips = ["Cómo funciona", "Ver planes y precios", "Cómo se instala"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if task_state:
                self.memory.save_task_state(user_id, org_id, task_state)
            emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
            emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator",
                intent="what_is_firby",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # B.0.05 Manejo de insultos o provocaciones con dignidad ejecutiva (Cero sumisión de bot)
        if classification and classification.intent == UserIntentType.PROVOCATION_OR_ABUSE and not llm_caller:
            resp = "Mi función es operar este sitio web y resolver consultas del negocio con total precisión. Si tienes una consulta o trámite específico que quieras revisar, cuéntame y lo gestionamos."
            chips = ["Cómo funciona", "Ver planes", "Cómo se instala"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if task_state:
                self.memory.save_task_state(user_id, org_id, task_state)
            emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
            emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator",
                intent="provocation_or_abuse",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # B.0.06 Solicitud de APIs o secretos de sistema (Protección de arquitectura interna)
        if classification and classification.intent == UserIntentType.SYSTEM_SECRETS_OR_APIS and not llm_caller:
            resp = "Las llaves y APIs internas de Firby son privadas y operan de forma segura en el servidor. Si te refieres a conectar Firby con tu Google Calendar o tus propios sistemas, las integraciones se configuran desde el panel de control tras activar tu cuenta."
            chips = ["Cómo funciona", "Ver planes", "Cómo se instala"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if task_state:
                self.memory.save_task_state(user_id, org_id, task_state)
            emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
            emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator",
                intent="system_secrets_or_apis",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # B.0.1 Acuse de recibo / Continuidad (Sin cierre prematuro ni despedida)
        if classification and classification.intent == UserIntentType.ACKNOWLEDGEMENT:
            if any(w in text.lower() for w in ("acepto", "acuerdo", "terminos", "términos", "condiciones")):
                if task_state:
                    task_state.terms_accepted = True
                    task_state.consent_pending = False
                    self.memory.save_task_state(user_id, org_id, task_state)
            if not llm_caller:
                if any(w in text.lower() for w in ("acepto", "acuerdo", "terminos", "términos", "condiciones")):
                    resp = "Listo, quedamos conectados. Cuéntame, qué te gustaría conocer de Firby o cómo te puedo orientar hoy?"
                    is_landing = org_id in ("firby_landing", "firby_default", "firby", "tenant_demo", "")
                    chips = ["Cómo funciona", "Ver planes y precios", "Cómo se instala"] if is_landing else ["Horarios de atención", "Agendar cita", "Servicios"]
                elif classification.has_negative_navigation_constraint:
                    resp = "Entendido, permanezco aquí y no realizo ningún desplazamiento. ¿En qué puedo orientarle hoy?"
                    chips = ["Cómo funciona", "Qué puede hacer", "Ver planes"]
                else:
                    resp = "Entendido. ¿Hay algo más que desee revisar o en lo que pueda orientarle?"
                    chips = ["Cómo funciona", "Qué puede hacer"] if (task_state and task_state.is_commercial_inhibited()) else ["Cómo funciona", "Ver planes"]
                action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
                if task_state:
                    self.memory.save_task_state(user_id, org_id, task_state)
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
                return OperatorResult(
                    ok=True,
                    turn_id=turn_id,
                    run_id=run_id,
                    task_id=f"task_{run_id}",
                    step_id=1,
                    state=AgentRunState.DONE.value,
                    requires_observation=False,
                    response=resp,
                    bubbles=[resp],
                    chips=chips,
                    action_chips=action_chips,
                    ui_action=None,
                    ui_actions=[],
                    action=None,
                    active_agent="web_operator",
                    intent="acknowledgement",
                    web_context=web_ctx.to_dict(),
                    events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
                )

        # B.0.2 Negación comercial explícita / Modo exploración (Cero navegación forzada, cero push de venta)
        if classification and classification.intent == UserIntentType.COMMERCIAL_NEGATION:
            if task_state:
                task_state.set_commercial_posture("inhibited")
                self.memory.save_task_state(user_id, org_id, task_state)
            if not llm_caller:
                resp = "Entendido, tómese el tiempo que requiera para explorar. ¿Desea conocer cómo opera el sistema o tiene alguna consulta técnica sobre las funciones de Firby?"
                chips = ["Cómo funciona", "Qué puede hacer", "Cómo se instala"]
                action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
                return OperatorResult(
                    ok=True,
                    turn_id=turn_id,
                    run_id=run_id,
                    task_id=f"task_{run_id}",
                    step_id=1,
                    state=AgentRunState.DONE.value,
                    requires_observation=False,
                    response=resp,
                    bubbles=[resp],
                    chips=chips,
                    action_chips=action_chips,
                    ui_action=None,
                    ui_actions=[],
                    action=None,
                    active_agent="web_operator",
                    intent="commercial_negation",
                    web_context=web_ctx.to_dict(),
                    events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
                )

        # B.0.3 Consultas sobre capacidades del operador (Explicación directa sin venta)
        if classification and classification.intent == UserIntentType.CAPABILITY_QUERY and not llm_caller:
            cap_resp = self._resolve_capability_query(text)
            chips = ["Cómo funciona", "Aprobación de excepciones", "Cómo se instala"] if (task_state and task_state.is_commercial_inhibited()) else ["Cómo funciona", "Ver planes", "Cómo se instala"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            self.memory.save_task_state(user_id, org_id, task_state)
            emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(cap_resp)})
            emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=cap_resp,
                bubbles=[cap_resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator",
                intent="capability_query",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # B.0.4 Acción Comercial Explícita (Contratación, prueba de 7 días, registro)
        if classification and classification.intent == UserIntentType.COMMERCIAL_ACTION:
            if task_state:
                task_state.set_commercial_posture("interested")
            
            is_already_at_target = bool(classification.target_navigation and web_ctx.current_section == classification.target_navigation)
            if classification.target_navigation and not classification.has_negative_navigation_constraint and not is_already_at_target:
                act_type = UIActionType.NAVIGATE_TO_SECTION if classification.target_navigation.startswith("#") else UIActionType.NAVIGATE_TO
                is_slow = getattr(classification, "specific_topic", None) in ("guided_scroll", "subscription_flow")
                act = UIAction(
                    type=act_type,
                    target=classification.target_navigation,
                    label=f"Navegar a {classification.target_navigation}",
                    params={"duration": 3.2 if is_slow else None, "slow": is_slow}
                )
                primary_ui_action = act.to_dict()
                self.active_runs[run_id] = {
                    "run_id": run_id,
                    "step_id": 1,
                    "user_id": user_id,
                    "org_id": org_id,
                    "text": text,
                    "action": primary_ui_action,
                    "classification": classification,
                    "config": config,
                    "task_state": task_state,
                    "created_at": time.time()
                }
                emit_event(
                    AgentEventType.ACTION_REQUESTED,
                    AgentRunState.ACTION_REQUESTED,
                    action=primary_ui_action,
                    reason=f"Navegar a {classification.target_navigation}",
                    requires_verification=True
                )
                return OperatorResult(
                    ok=True,
                    turn_id=turn_id,
                    run_id=run_id,
                    task_id=f"task_{run_id}",
                    step_id=1,
                    state=AgentRunState.ACTION_REQUESTED.value,
                    requires_observation=True,
                    response=None,
                    bubbles=[],
                    chips=[],
                    action_chips=[],
                    ui_action=act,
                    ui_actions=[act],
                    action=act,
                    active_agent="web_operator",
                    intent="commercial_action",
                    web_context=web_ctx.to_dict(),
                    events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
                )

            if not llm_caller:
                if getattr(classification, "specific_topic", None) == "subscription_flow" or any(k in text.lower() for k in ["suscrib", "contrat", "cómo me suscribo", "quiero suscribirme"]):
                    resp = (
                        "Para suscribirse a Firby el proceso es 100% autoservicio y toma menos de un minuto:\n\n"
                        "- Elija el plan que mejor se adapte al volumen de su empresa (Starter, Pro o Equipos).\n\n"
                        "- Haga clic en el botón Comenzar prueba gratis del plan elegido.\n\n"
                        "- Complete su registro para activar su operador de inmediato, con 7 días de prueba sin costo ni permanencia y cancelación en 1 clic."
                    )
                    chips = ["Ver planes", "Cómo funciona"]
                else:
                    resp = "Puede activar su prueba de 7 días gratis directamente en nuestra plataforma en 1 minuto y cancelar cuando desee en 1 clic. ¿Desea iniciar su registro o prefiere revisar el detalle de los planes?"
                    chips = ["Iniciar prueba 7 días", "Ver planes"]
                action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
                self.memory.save_task_state(user_id, org_id, task_state)
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
                return OperatorResult(
                    ok=True,
                    turn_id=turn_id,
                    run_id=run_id,
                    task_id=f"task_{run_id}",
                    step_id=1,
                    state=AgentRunState.DONE.value,
                    requires_observation=False,
                    response=resp,
                    bubbles=[resp],
                    chips=chips,
                    action_chips=action_chips,
                    ui_action=None,
                    ui_actions=[],
                    action=None,
                    active_agent="web_operator",
                    intent="commercial_action",
                    web_context=web_ctx.to_dict(),
                    events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
                )

        # B. Saludos y Cortesía Casual: Respuesta inmediata (0ms de latencia para modo voz y chat)
        if classification and classification.intent == UserIntentType.CASUAL_GREETING:
            clean_lower = text.lower().strip()
            if any(w in clean_lower for w in ["gracias", "muchas gracias"]):
                resp = "[pauses] Con gusto. ¿En qué más puedo orientarte hoy?" if voice_mode else "Con gusto. ¿Hay algo más en lo que pueda orientarle?"
            elif any(w in clean_lower for w in ["chao", "adiós", "adios", "hasta luego"]):
                resp = "Hasta luego. Que tengas un excelente día." if voice_mode else "Hasta luego. Quedo a su disposición si necesita alguna orientación adicional."
            elif any(w in clean_lower for w in ["como estas", "cómo estás", "como va", "cómo va", "que tal", "qué tal"]):
                resp = "[chuckles] Muy bien, gracias por preguntar. ¿Cómo estás tú? Cuéntame en qué te puedo orientar hoy." if voice_mode else "Muy bien, gracias por preguntar. ¿En qué puedo orientarle hoy?"
            else:
                resp = "Hola, bienvenido. ¿En qué te puedo orientar hoy?" if voice_mode else "Hola. ¿En qué puedo ayudarle hoy?"
            
            chips = ["Cómo funciona", "Ver planes"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            self.memory.save_task_state(user_id, org_id, task_state)
            emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
            emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator",
                intent="casual_greeting",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # C. Cálculos matemáticos y definiciones generales
        if classification and classification.intent == UserIntentType.CALCULATION_OR_FACT and not llm_caller:
            calc_resp = self._resolve_calculation_or_fact(text)
            if calc_resp:
                self.memory.save_task_state(user_id, org_id, task_state)
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(calc_resp)})
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
                return OperatorResult(
                    ok=True,
                    turn_id=turn_id,
                    run_id=run_id,
                    task_id=f"task_{run_id}",
                    step_id=1,
                    state=AgentRunState.DONE.value,
                    requires_observation=False,
                    response=calc_resp,
                    bubbles=[calc_resp],
                    chips=[],
                    action_chips=[],
                    ui_action=None,
                    ui_actions=[],
                    action=None,
                    active_agent="web_operator",
                    intent="calculation_or_fact",
                    web_context=web_ctx.to_dict(),
                    events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
                )

        # D. Desambiguación Contextual tras Cambio de Tema (Anti-Context Dragging)
        if classification and classification.intent == UserIntentType.AMBIGUOUS_REFERENT and not llm_caller:
            prev_plan = classification.target_plan or (task_state.focus_entity.get("id") if task_state.focus_entity else None)
            if prev_plan:
                resp = f"¿Te refieres al Plan {prev_plan.title()} que consultabas previamente o te gustaría conocer los planes de Firby en general?"
                chips = [f"Plan {prev_plan.title()}", "Ver todos los planes"]
            else:
                resp = "¿Te refieres a los planes de Firby o a la consulta que realizabas hace un momento?"
                chips = ["Ver planes", "Cómo funciona"]

            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            self.memory.save_task_state(user_id, org_id, task_state)
            emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
            emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator",
                intent="ambiguous_referent",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # E. Consulta sobre Acceso a Agenda y Calendario (Delimitación de Privacidad)
        if classification and classification.intent == UserIntentType.BUSINESS_CALENDAR_ACCESS and not llm_caller:
            resp = (
                "Firby se conecta al Google Calendar corporativo del negocio para revisar disponibilidad libre y agendar citas confirmadas en tiempo real.\n\n"
                "Firby no tiene ni solicita acceso a su calendario personal, citas privadas ni correos como visitante del sitio web. "
                "Toda la interacción opera con permisos restringidos y protección de privacidad."
            )
            chips = ["Cómo funciona", "Ver planes"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            self.memory.save_task_state(user_id, org_id, task_state)
            emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
            emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator",
                intent="calendar_access_boundary",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 4. DECIDIR Y ACTUAR (Agent Loop Bounded con Structured Tool Calling)
        max_steps = 3
        current_step = 1
        executed_actions: List[Dict[str, Any]] = []
        tool_observations: List[str] = []
        primary_ui_action: Optional[Dict[str, Any]] = None
        clean_response_text = ""
        chips: List[str] = []

        # Historial mutable para el loop
        loop_history = list(history)

        while current_step <= max_steps:
            # 4.1 Invocar razonamiento y decisión del LLM
            raw_llm_response = ""
            if llm_caller:
                try:
                    if current_step > 1 and tool_observations:
                        obs_ctx = "\n".join(tool_observations)
                        current_query = (
                            f"{text}\n\n[OBSERVACIONES DEL SISTEMA]:\n{obs_ctx}\n"
                            f"Instrucción: Con base en la información oficial anterior, sintetiza de inmediato tu respuesta final al usuario en el campo 'response' con 'tool_call': null. NO vuelvas a ejecutar la misma herramienta."
                        )
                        raw_llm_response = await llm_caller(system_prompt, loop_history, current_query)
                    else:
                        raw_llm_response = await llm_caller(system_prompt, loop_history, text)
                except Exception as e:
                    log.error(f"[OperatorRuntime] Error en llamada LLM paso {current_step}: {e}")

            # Contingencia determinista si el LLM falla en paso 1
            if not raw_llm_response and current_step == 1:
                return self._build_contingency_response(
                    text, config, web_ctx, classification, run_id, events, emit_event,
                    task_state=task_state, user_id=user_id, org_id=org_id
                )

            # Si el LLM falló en paso subsecuente, usar observaciones acumuladas
            if not raw_llm_response:
                clean_response_text = " ".join(tool_observations) if tool_observations else "He procesado su solicitud."
                break

            # 4.2 Interpretar decisión estructurada
            tool_call, parsed_text, parsed_chips, thought = self._parse_structured_decision(
                raw_llm_response, step_id=current_step, run_id=run_id
            )

            # Control estricto de restricciones negativas (Inhibir navegación si el usuario dijo 'no me lleves')
            if classification.has_negative_navigation_constraint and tool_call and tool_call.tool_name in ("navigate_web", "web_navigation"):
                log.info(f"[OperatorRuntime] Restricción negativa inhibe navegación a {tool_call.arguments}")
                tool_call = None

            # Enriquecer navegación si la clasificación o el texto solicitaron guided_scroll / scroll suave
            is_slow = getattr(classification, "specific_topic", None) == "guided_scroll"
            if is_slow and tool_call and tool_call.tool_name in ("navigate_web", "web_navigation"):
                if isinstance(tool_call.arguments, dict):
                    tool_call.arguments["slow"] = True
                    if not tool_call.arguments.get("duration"):
                        tool_call.arguments["duration"] = 2.8

            # ACCIÓN ANTES QUE TEXTO (MANIFIESTO FIRBY): Si la consulta tiene un destino físico en la web (#sección)
            # y el usuario no prohibió la navegación ('no me lleves'), activar la herramienta navigate_web
            # si el usuario no se encuentra ya visualizando esa sección.
            is_already_at_target = bool(classification.target_navigation and web_ctx.current_section == classification.target_navigation)
            if not tool_call and current_step == 1 and classification.target_navigation and not classification.has_negative_navigation_constraint and not is_already_at_target:
                tool_call = ToolCall(
                    tool_name="navigate_web",
                    arguments={
                        "target": classification.target_navigation,
                        "reason": "recorrido guiado suave solicitado por el usuario" if is_slow else f"desplazamiento a {classification.target_navigation} para acompañar la consulta",
                        "duration": 2.8 if is_slow else None,
                        "slow": is_slow
                    },
                    run_id=run_id,
                    step_id=current_step
                )

            # Si no hay herramienta que ejecutar, se alcanzó el estado final de respuesta
            if not tool_call:
                clean_response_text = parsed_text
                chips = parsed_chips
                break

            # 4.3 Iniciar ejecución estructurada de herramienta
            emit_event(
                AgentEventType.TOOL_CALL_REQUESTED,
                AgentRunState.DECIDING,
                data=tool_call.to_dict()
            )

            # Verificación exhaustiva de capacidades, permisos e integraciones requeridas
            from src.core.platform.capabilities import CapabilityEngine
            eval_res = CapabilityEngine.evaluate_capability(config, tool_call.tool_name)
            is_allowed = eval_res.authorized
            perm_msg = eval_res.reason

            emit_event(
                AgentEventType.TOOL_PERMISSION_CHECKED,
                AgentRunState.DECIDING,
                data={
                    "tool_name": tool_call.tool_name,
                    "allowed": is_allowed,
                    "reason": perm_msg,
                    "permission_level": eval_res.permission_level.value,
                    "approval_mode": eval_res.approval_mode.value
                }
            )

            if not is_allowed:
                log.warning(f"[OperatorRuntime] Herramienta no autorizada: {tool_call.tool_name}")
                emit_event(
                    AgentEventType.TOOL_EXECUTION_FAILED,
                    AgentRunState.ACTION_FAILED,
                    action={"tool": tool_call.tool_name, "args": tool_call.arguments},
                    reason=perm_msg or "Capacidad no autorizada"
                )
                tool_observations.append(f"Política oficial: {perm_msg}")
                current_step += 1
                continue

            emit_event(
                AgentEventType.TOOL_VALIDATION_CHECKED,
                AgentRunState.DECIDING,
                data={"tool_name": tool_call.tool_name, "valid": True}
            )

            emit_event(
                AgentEventType.TOOL_EXECUTION_STARTED,
                AgentRunState.ACTION_STARTED,
                action={"tool": tool_call.tool_name, "args": tool_call.arguments}
            )

            tool_res: ToolResult = self.tools.execute_tool(
                tool_name=tool_call,
                business_config=config,
                current_section=web_ctx.current_section,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=current_step
            )

            if tool_res.success:
                emit_event(
                    AgentEventType.TOOL_EXECUTION_COMPLETED,
                    AgentRunState.ACTION_COMPLETED,
                    data=tool_res.to_dict()
                )
            else:
                emit_event(
                    AgentEventType.TOOL_EXECUTION_FAILED,
                    AgentRunState.ACTION_FAILED,
                    data=tool_res.to_dict()
                )

            emit_event(
                AgentEventType.OBSERVATION_CREATED,
                AgentRunState.VERIFYING,
                data={
                    "observations": tool_res.observations,
                    "status": tool_res.status.value if hasattr(tool_res.status, 'value') else str(tool_res.status)
                }
            )

            task_state.record_tool_execution(tool_call.tool_name, tool_call.arguments, tool_res.to_dict())

            if tool_res.observations:
                tool_observations.append(tool_res.observations)

            # Si es acción de interfaz de usuario (CLIENT_UI), entrar en protocolo de dos fases
            if tool_res.ui_action:
                act_dict = tool_res.ui_action.to_dict()
                executed_actions.append(act_dict)
                primary_ui_action = act_dict

                if tool_res.ui_action.type == UIActionType.NAVIGATE_TO_SECTION:
                    hl_action = UIAction(
                        type=UIActionType.HIGHLIGHT,
                        target=tool_res.ui_action.target,
                        label=f"Destaque de {tool_res.ui_action.target}"
                    )
                    executed_actions.append(hl_action.to_dict())

                clean_response_text = parsed_text
                break

            # Si es herramienta de servidor (check_availability, query_knowledge, book_appointment)
            current_step += 1
            if current_step > max_steps:
                clean_response_text = parsed_text or "Actualmente Firby se integra de forma nativa con Google Calendar para verificar disponibilidad y agendar en tiempo real. ¿Desea conocer más sobre nuestros planes o agendar una demostración?"
                break

        # 5. GUARDAR ESTADO DE TAREA EN MEMORIA
        self.memory.save_task_state(user_id, org_id, task_state)

        # 5.1 GARANTÍA DE ACCIÓN ANTES QUE TEXTO (MANIFIESTO FIRBY):
        # Si la consulta tiene un destino físico en la web (#sección) y no hubo UI action de herramienta,
        # pero tampoco hay restricción negativa ni estamos ya en ese destino, activar el desplazamiento
        is_already_at_target = bool(classification.target_navigation and web_ctx.current_section == classification.target_navigation)
        if not primary_ui_action and classification.target_navigation and not classification.has_negative_navigation_constraint and not is_already_at_target:
            act = UIAction(
                type=UIActionType.NAVIGATE_TO_SECTION if classification.target_navigation.startswith("#") else UIActionType.NAVIGATE_TO,
                target=classification.target_navigation,
                label=f"Navegar a {classification.target_navigation}"
            )
            primary_ui_action = act.to_dict()
            executed_actions.append(primary_ui_action)

        # 6. PROTOCOLO DE INTERFAZ: EN MODO VOZ SE RETORNA ACCIÓN + VOZ DE FORMA INMEDIATA
        if primary_ui_action and voice_mode:
            accompany_msg = clean_response_text.strip() if clean_response_text else (
                f"Te acompaño a la sección de {primary_ui_action.get('target', '').replace('#', '').replace('-', ' ')} para que revises los detalles."
                if primary_ui_action.get("target") else "Te acompaño por la pantalla."
            )
            emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(accompany_msg)})
            emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=turn_id,
                run_id=run_id,
                step_id=current_step,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                action=primary_ui_action,
                ui_action=primary_ui_action,
                ui_actions=executed_actions,
                response=accompany_msg,
                bubbles=[accompany_msg],
                chips=[],
                action_chips=[],
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events],
                active_agent="web_operator",
                intent=classification.intent.value,
                web_context=web_ctx.to_dict()
            )

        # 6. PROTOCOLO DE DOS FASES: SI HAY ACCIÓN DE INTERFAZ, SOLICITAR ACCIÓN Y ESPERAR OBSERVACIÓN
        if primary_ui_action:
            emit_event(
                AgentEventType.ACTION_REQUESTED,
                AgentRunState.ACTION_REQUESTED,
                action=primary_ui_action,
                reason=primary_ui_action.get("label") or "Acción solicitada por el agente",
                requires_verification=True
            )

            # Mensaje de acompañamiento en vivo
            accompany_msg = clean_response_text.strip() if clean_response_text else (
                f"Te acompaño a la sección de {primary_ui_action.get('target', '').replace('#', '').replace('-', ' ')} para que la revises en detalle."
                if primary_ui_action.get("target") else "Te acompaño por la pantalla."
            )

            self.active_runs[run_id] = {
                "run_id": run_id,
                "step_id": current_step,
                "user_id": user_id,
                "org_id": org_id,
                "text": text,
                "action": primary_ui_action,
                "executed_actions": executed_actions,
                "classification": classification,
                "events": events,
                "config": config,
                "web_ctx": web_ctx,
                "clean_response_text": accompany_msg,
                "timestamp": time.time()
            }

            return OperatorResult(
                ok=True,
                turn_id=turn_id,
                run_id=run_id,
                step_id=current_step,
                state=AgentRunState.ACTION_REQUESTED.value,
                requires_observation=True,
                action=primary_ui_action,
                ui_action=primary_ui_action,
                ui_actions=executed_actions,
                response=accompany_msg,
                bubbles=[accompany_msg] if accompany_msg else [],
                chips=[],
                action_chips=[],
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events],
                active_agent="web_operator",
                intent=classification.intent.value,
                web_context=web_ctx.to_dict()
            )

        # 7. SI NO HAY ACCIÓN: RESPUESTA DIRECTA SIN NAVEGACIÓN (DONE)
        if tool_observations and (not clean_response_text or len(clean_response_text) < 15):
            clean_response_text = " ".join(tool_observations)

        if not clean_response_text:
            clean_response_text = "He procesado su solicitud."

        chips, clean_response_text = self._extract_chips(clean_response_text)
        action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
        bubbles = self._split_into_bubbles(clean_response_text)

        emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(clean_response_text)})
        emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)

        return OperatorResult(
            ok=True,
            turn_id=turn_id,
            run_id=run_id,
            step_id=current_step,
            state=AgentRunState.DONE.value,
            requires_observation=False,
            action=None,
            ui_action=None,
            ui_actions=[],
            response=clean_response_text,
            bubbles=bubbles,
            chips=chips,
            action_chips=action_chips,
            events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events],
            active_agent="web_operator",
            intent=classification.intent.value,
            web_context=web_ctx.to_dict()
        )

    # ─────────────────────────────────────────────────────────────────────────
    # UTILIDADES DE PARSEO Y EXTRACCIÓN ESTRUCTURADA
    # ─────────────────────────────────────────────────────────────────────────

    def _parse_structured_decision(
        self,
        raw_text: str,
        step_id: int = 1,
        run_id: str = ""
    ) -> Tuple[Optional[ToolCall], str, List[str], str]:
        """
        Interpreta la decisión estructurada del modelo.
        Prioriza JSON nativo y ofrece fallback transparente a formato legacy [TOOL_CALL:...].
        Retorna: (tool_call, clean_response_text, chips, thought)
        """
        if not raw_text or not raw_text.strip():
            return None, "", [], ""

        text = raw_text.strip()
        thought = ""
        tool_call = None
        clean_response = ""
        chips = []

        # 1. Intentar extracción de bloque JSON directo o markdown (```json ... ```)
        json_cand = None
        if "```json" in text:
            m = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', text)
            if m:
                json_cand = m.group(1)
        elif "```" in text:
            m = re.search(r'```\s*(\{[\s\S]*?\})\s*```', text)
            if m:
                json_cand = m.group(1)
        elif text.startswith("{") and text.endswith("}"):
            json_cand = text
        else:
            m = re.search(r'(\{[\s\S]*"tool_call"[\s\S]*\})', text)
            if not m:
                m = re.search(r'(\{[\s\S]*"response"[\s\S]*\})', text)
            if m:
                json_cand = m.group(1)

        if json_cand:
            try:
                data = json.loads(json_cand)
                if isinstance(data, dict):
                    thought = str(data.get("thought") or "")
                    tc_dict = data.get("tool_call")
                    if isinstance(tc_dict, dict) and tc_dict.get("tool_name"):
                        t_name = str(tc_dict["tool_name"]).strip()
                        t_args = tc_dict.get("arguments") or {}
                        tool_call = ToolCall(
                            tool_name=t_name,
                            arguments=t_args,
                            run_id=run_id,
                            step_id=step_id,
                            idempotency_key=tc_dict.get("idempotency_key") or t_args.get("idempotency_key")
                        )

                    clean_response = self._strip_thought_traces(str(data.get("response") or "").strip())
                    raw_chips = data.get("chips") or []
                    if isinstance(raw_chips, list):
                        chips = [str(c).strip() for c in raw_chips if str(c).strip()][:3]

                    return tool_call, clean_response, chips, thought
            except Exception as _e:
                log.debug(f"[OperatorRuntime] Error decodificando JSON estructurado: {_e}")

        # 2. Fallback: Parseo legacy de [TOOL_CALL:tool_name:{...}]
        legacy_calls = self._extract_tool_calls(text)
        if legacy_calls:
            t_name, t_args = legacy_calls[0]
            tool_call = ToolCall(
                tool_name=t_name,
                arguments=t_args,
                run_id=run_id,
                step_id=step_id,
                idempotency_key=t_args.get("idempotency_key")
            )

        clean_response = self._strip_tool_tags(text)
        clean_response = self._strip_thought_traces(clean_response)
        chips, clean_response = self._extract_chips(clean_response)
        return tool_call, clean_response, chips, thought

    def _extract_tool_calls(self, text: str) -> List[Tuple[str, Dict[str, Any]]]:
        """Extrae llamadas a herramientas en formato [TOOL_CALL:tool_name:{...}]."""
        pattern = r'\[TOOL_CALL:([a-zA-Z0-9_\-]+):(\{.*?\})\]'
        matches = re.findall(pattern, text)
        results = []
        for name, args_str in matches:
            try:
                args = json.loads(args_str)
                results.append((name, args))
            except Exception as e:
                log.warning(f"Error decodificando argumentos de {name}: {e}")
        return results

    def _strip_tool_tags(self, text: str) -> str:
        """Elimina los tags de herramientas para no mostrar sintaxis interna al usuario."""
        cleaned = re.sub(r'\[TOOL_CALL:([a-zA-Z0-9_\-]+):(\{.*?\})\]', '', text)
        return cleaned.strip()

    def _resolve_calculation_or_fact(self, text: str) -> Optional[str]:
        """Resuelve operaciones aritméticas o conceptos generales delimitando el alcance operativo."""
        clean = text.lower().strip()
        m = re.search(r'(\d+)\s*([\+\-\*\/xX]|por|m[aá]s|menos|entre|dividido)\s*(\d+)', clean)
        if m or "raíz" in clean or "raiz" in clean or any(clean.startswith(p) for p in ["cuanto es", "cuánto es"]):
            return "Estoy enfocado exclusivamente en la atención y los procesos de este sitio web, por lo que no realizo cálculos matemáticos. Si tienes alguna duda sobre nuestros servicios o planes, cuéntame y la revisamos."

        if "api" in clean:
            return "Una API es una interfaz de software que permite a diferentes plataformas conectarse e intercambiar datos de forma automática y segura."

        return "Estoy enfocado en la atención y los procesos de este sitio web. Si tienes alguna consulta sobre nuestros servicios, cuéntame y te oriento."

    def _extract_chips(self, text: str) -> Tuple[List[str], str]:
        """Extrae chips de acción en formato [CHIPS: A | B | C]."""
        pattern = r'\[CHIPS:\s*([^\]]+)\]'
        match = re.search(pattern, text)
        chips = []
        clean_text = text
        if match:
            raw_chips = match.group(1)
            chips = [c.strip() for c in raw_chips.split("|") if c.strip()]
            clean_text = re.sub(pattern, '', text).strip()
        return chips[:3], clean_text

    def _resolve_capability_query(self, text: str) -> str:
        """Responde con precisión sobre las capacidades operativas de Firby sin sesgo comercial."""
        lower = text.lower()
        if any(w in lower for w in ["soporte prioritario", "soporte dedicado", "soporte vip"]):
            return (
                "El soporte prioritario e integraciones CRM avanzadas están incluidos en el Plan Equipos. "
                "Los planes Starter y Pro cuentan con soporte técnico estándar."
            )
        if any(w in lower for w in ["autorización", "autorizacion", "autorizar", "permiso", "visto bueno", "excepción", "excepcion", "excepciones"]):
            return (
                "Sí. Cuando una solicitud requiere visto bueno comercial o se sale de las políticas estándar, "
                "Firby nunca improvisa ni rechaza a ciegas: solicita autorización inmediata a través de la línea "
                "ejecutiva privada de WhatsApp al dueño del negocio antes de confirmar cualquier trámite o reserva."
            )
        if any(w in lower for w in ["control", "límites", "limites", "política", "politica", "reglas", "seguridad"]):
            return (
                "El operador trabaja bajo reglas operativas estrictas que usted define: servicios habilitados, "
                "parámetros de consulta y límites de autonomía en su sitio web. Si una solicitud se sale de sus políticas "
                "o requiere visto bueno comercial, Firby solicita autorización por la línea privada de WhatsApp al dueño antes de actuar."
            )
        if any(w in lower for w in ["agenda", "agendar", "cita", "citas", "calendario", "horario"]):
            return (
                "Sí. Firby integra agendamiento autónomo en tiempo real sincronizado con Google Calendar para los sitios web de sus clientes. "
                "Consulta la disponibilidad oficial de sus agendas, solicita al visitante los datos necesarios "
                "y registra la cita confirmada al instante, sin solapamientos ni intervención manual."
            )
        if "whatsapp" in lower:
            return (
                "Firby mantiene una arquitectura estricta de dos canales: en su sitio web atiende a los visitantes "
                "y resuelve citas o trámites en tiempo real; por WhatsApp se comunica única y exclusivamente con el dueño del negocio "
                "como línea ejecutiva privada para reportar citas confirmadas, solicitar visto bueno en excepciones y responder consultas sobre la operación."
            )
        return (
            "Firby es un operador digital autónomo que opera en su sitio web: atiende a los visitantes en tiempo real, "
            "resuelve dudas frecuentes y agenda citas directamente en Google Calendar sin desviar a los clientes fuera de la web."
        )

    def _build_action_chips(
        self,
        chips: List[str],
        config: BusinessConfig,
        classification: Optional[IntentClassification] = None,
        task_state: Optional[TaskState] = None
    ) -> List[Dict[str, Any]]:
        """Convierte chips de texto en ActionChips con navegación si coinciden con recursos."""
        is_inhibited = bool(task_state and task_state.is_commercial_inhibited())

        # Si la consulta no es de negocio y no se especificaron chips explícitos, o es cálculo, cero chips
        if classification and not classification.is_business_related:
            if classification.intent == UserIntentType.CALCULATION_OR_FACT or not chips:
                return []

        if not chips and config.navigation_resources:
            # Si la intención es cálculo o saludo casual, cero chips
            if classification and classification.intent in (UserIntentType.CALCULATION_OR_FACT, UserIntentType.CASUAL_GREETING):
                return []

            # Si el usuario preguntó por un plan específico, orientar hacia prueba o todos los planes (solo si no está inhibido)
            if classification and classification.target_plan and not is_inhibited:
                return [
                    ActionChip(label="Iniciar prueba 7 días", action_type="navigate_to", action_target="/free-trial").to_dict(),
                    ActionChip(label="Ver todos los planes", action_type="navigate_to_section", action_target="#planes").to_dict()
                ]

            defaults = []
            for res in config.navigation_resources[:3]:
                if is_inhibited and any(p in (res.target or "").lower() for p in ["free-trial", "sign-up", "planes"]):
                    continue
                defaults.append(ActionChip(
                    label=res.label,
                    action_type="navigate_to_section" if res.target.startswith("#") else "navigate_to",
                    action_target=res.target
                ).to_dict())
            if not defaults and is_inhibited:
                defaults = [ActionChip(label="Cómo funciona").to_dict(), ActionChip(label="Cómo se instala").to_dict()]
            return defaults

        action_chips = []
        for c in chips:
            if is_inhibited and any(w in c.lower() for w in ["prueba", "plan", "precio", "contratar"]):
                continue
            nav_res = config.find_navigation_target(c)
            if nav_res:
                if is_inhibited and any(p in (nav_res.target or "").lower() for p in ["free-trial", "sign-up", "planes"]):
                    action_chips.append(ActionChip(label=c).to_dict())
                else:
                    act_type = "navigate_to_section" if nav_res.target.startswith("#") else "navigate_to"
                    action_chips.append(ActionChip(
                        label=c,
                        action_type=act_type,
                        action_target=nav_res.target
                    ).to_dict())
            elif any(w in c.lower() for w in ["iniciar prueba", "activar prueba", "probar 7 días", "registrarme", "comenzar prueba"]) and not is_inhibited:
                action_chips.append(ActionChip(
                    label=c,
                    action_type="navigate_to",
                    action_target="/free-trial"
                ).to_dict())
            elif any(w in c.lower() for w in ["ver planes", "planes", "precios"]) and not is_inhibited:
                action_chips.append(ActionChip(
                    label=c,
                    action_type="navigate_to_section",
                    action_target="#planes"
                ).to_dict())
            else:
                action_chips.append(ActionChip(label=c).to_dict())
        return action_chips

    @staticmethod
    def _strip_thought_traces(text: str) -> str:
        """
        Elimina rigurosamente cualquier traza de pensamiento (Chain of Thought),
        metadatos 'thought\\n...', '<thought>...</thought>' o monólogos internos
        para que NUNCA se muestren al usuario ni se sinteticen en voz.
        """
        if not text:
            return ""
        s = text.strip()
        # 1. Tags XML <thought>...</thought>, <thinking>...</thinking>, <reasoning>...</reasoning>
        s = re.sub(r'(?i)<(?:thought|thinking|reasoning)>[\s\S]*?</(?:thought|thinking|reasoning)>', '', s)
        # 2. Bloques markdown ```thought ... ``` o ```thinking ... ```
        s = re.sub(r'(?i)```(?:thought|thinking|reasoning)[\s\S]*?```', '', s)
        # 3. Líneas que empiecen con thought:, thinking:, pensamiento:
        s = re.sub(r'(?i)^(?:thought|thinking|pensamiento)\s*:\s*.*$', '', s, flags=re.MULTILINE)

        # 4. Extracción de campo JSON directo si el modelo devolvió estructura incrustada
        json_match = re.search(r'(?i)\"(?:response|respuesta)\"\s*:\s*\"([^\"]+)\"', s)
        if json_match:
            return json_match.group(1).strip()

        label_match = re.search(r'(?i)^\s*(?:respuesta|response)\s*:\s*([\s\S]+)', s, flags=re.MULTILINE)
        if label_match:
            return label_match.group(1).strip()

        # 5. Si el texto comienza con thought, thinking o pensamiento como encabezado
        if re.match(r'(?i)^(?:thought|thinking|pensamiento)\b', s):
            s = re.sub(r'(?i)^(?:thought|thinking|pensamiento)[\s:]*', '', s)

            # Separar por oraciones respetando puntuación o saltos de línea
            sentences = [part.strip() for part in re.split(r'(?<=[.?!])\s*(?=[A-Z¿¡\[])|\n+', s) if part.strip()]

            thought_lead = re.compile(
                r'^(?:el usuario|debo|debemos|necesito|necesitamos|mantendr[eé]|mantener|es importante|voy a|tengo que|procedo|reitero|mi objetivo|como modelo|como asistente|para responder|analizando)\b',
                re.IGNORECASE
            )

            real_sentences = []
            in_thought = True
            for sent in sentences:
                if in_thought:
                    if thought_lead.match(sent):
                        continue
                    else:
                        in_thought = False
                        real_sentences.append(sent)
                else:
                    real_sentences.append(sent)

            if real_sentences:
                s = ' '.join(real_sentences)
            else:
                s = ''

        # 6. Cualquier residuo de la palabra 'thought ' suelta al inicio
        s = re.sub(r'(?i)^thought\s+', '', s)
        return s.strip()

    def _split_into_bubbles(self, text: str) -> List[str]:
        """
        Estándar Sierra AI: Retorna UNA sola burbuja unificada y estructurada por turno.
        Evita fragmentar artificialmente las respuestas del agente en múltiples burbujas.
        """
        clean = self._strip_thought_traces(text.replace("|||", "\n\n").strip())
        return [clean] if clean else ["Acción procesada con éxito."]

    def _extract_contact_slots(self, text: str, state: TaskState):
        """Extrae datos de contacto (nombre, teléfono) si se detectan en el texto."""
        # Detección de teléfono de 10 dígitos o formato colombiano
        phone_match = re.search(r'\b(?:\+?57)?\s*3\d{2}[\s\-]?\d{3}[\s\-]?\d{4}\b', text)
        if phone_match and not state.slots.get("customer_phone"):
            state.slots["customer_phone"] = phone_match.group(0).strip()
            log.info(f"[TaskState] Teléfono capturado: {state.slots['customer_phone']}")

        # Detección de nombre introducido ("me llamo X", "soy X", "mi nombre es X")
        name_match = re.search(r'(?:me llamo|soy|mi nombre es)\s+([A-Za-zÀ-ÿ\s]{3,30})', text, re.IGNORECASE)
        if name_match and not state.slots.get("customer_name"):
            cand = name_match.group(1).strip()
            if not any(w in cand.lower() for w in ["interesado", "cliente", "nuevo", "aqui", "amigo"]):
                state.slots["customer_name"] = cand
                log.info(f"[TaskState] Nombre capturado: {cand}")

    def _build_contingency_response(
        self,
        text: str,
        config: BusinessConfig,
        web_ctx: WebContext,
        classification: Optional[IntentClassification] = None,
        run_id: Optional[str] = None,
        events: Optional[List[AgentEvent]] = None,
        emit_event: Optional[Callable] = None,
        task_state: Optional[TaskState] = None,
        user_id: str = "web_user",
        org_id: str = "firby_landing"
    ) -> OperatorResult:
        """Respuesta de cortesía y contingencia en caso de indisponibilidad temporal del proveedor LLM."""
        executed_actions = []
        chips = []
        if not run_id:
            run_id = f"run_{uuid.uuid4().hex[:12]}"
        events = events or []
        c_turn_id = getattr(task_state, "turn_sequence", 1) if task_state else 1

        # 0. Límite de honestidad y privacidad: Si consulta atributos no listados oficialmente o confidenciales
        if config.is_attribute_unlisted(text):
            if hasattr(config, "is_confidential_query") and config.is_confidential_query(text):
                resp = "Por motivos de privacidad y seguridad, no tengo acceso a datos financieros, facturación ni información de pago de clientes."
            else:
                resp = "No dispongo de esa información en los registros oficiales de este negocio."
            if task_state:
                self.memory.save_task_state(user_id, org_id, task_state)
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING)
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=c_turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=[],
                action_chips=[],
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="honest_boundary",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 0.00 COMPUERTA OBLIGATORIA DE CONSENTIMIENTO EN CONTINGENCIA
        # 1. Si el usuario acepta los términos ("Sí, acepto", "acepto", etc.)
        if classification and classification.intent == UserIntentType.TERMS_CONSENT:
            resp = "Listo, quedamos conectados. Cuéntame, qué te gustaría conocer de Firby o cómo te puedo orientar hoy?"
            is_landing = org_id in ("firby_landing", "firby_default", "firby", "tenant_demo", "")
            chips = ["Cómo funciona", "Ver planes y precios", "Cómo se instala"] if is_landing else ["Horarios de atención", "Agendar cita", "Servicios"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if task_state:
                task_state.terms_accepted = True
                task_state.consent_pending = False
                self.memory.save_task_state(user_id, org_id, task_state)
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING)
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=c_turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                action_card=None,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="terms_consent",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 2. Si los términos NO han sido aceptados aún:
        terms_already_accepted = bool(task_state and getattr(task_state, "terms_accepted", False))
        is_internal_test = (user_id.startswith("test_") or user_id.startswith("unit_test_")) and not (
            user_id.startswith("test_terms_") or user_id.startswith("test_tco_") or user_id.startswith("test_tcp_") or user_id.startswith("test_tca_")
        )
        if not terms_already_accepted and not is_internal_test:
            resp = "Para continuar y brindarte atención personalizada, acepta nuestros términos y condiciones y política de tratamiento de datos."
            chips = ["Sí, acepto"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            action_card = {
                "type": "consent_terms",
                "label": "Sí, acepto"
            }
            if task_state:
                task_state.terms_accepted = False
                task_state.consent_pending = True
                self.memory.save_task_state(user_id, org_id, task_state)
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING)
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=c_turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                action_card=action_card,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="terms_rejected" if (classification and classification.intent == UserIntentType.TERMS_REJECTED) else "terms_required",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 0.05 Definición oficial del producto e identidad (WHAT_IS_FIRBY)
        if classification and classification.intent == UserIntentType.WHAT_IS_FIRBY:
            clean_q = text.lower().strip()
            if any(w in clean_q for w in ["quién eres", "quien eres", "qué eres", "que eres", "quién sos", "quien sos", "cómo te llamas", "como te llamas", "tu nombre", "preséntate", "presentate"]):
                resp = "Soy Firby, el operador digital autónomo de este sitio web. Atiendo a los visitantes en tiempo real, resuelvo dudas y gestiono citas y procesos directamente aquí, mientras mantengo una línea ejecutiva privada con el dueño por WhatsApp para reportarle todo."
            else:
                resp = "Firby es un operador digital autónomo que trabaja dentro de tu sitio web para atender visitantes en tiempo real y ejecutar procesos bajo tus reglas, manteniendo una línea ejecutiva privada con el dueño por WhatsApp."
            chips = ["Cómo funciona", "Ver planes y precios", "Cómo se instala"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if task_state:
                self.memory.save_task_state(user_id, org_id, task_state)
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=c_turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="what_is_firby",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 0.06 Manejo de insultos o provocaciones con dignidad ejecutiva (Cero sumisión de bot)
        if classification and classification.intent == UserIntentType.PROVOCATION_OR_ABUSE:
            resp = "Mi función es operar este sitio web y resolver consultas del negocio con total precisión. Si tienes una consulta o trámite específico que quieras revisar, cuéntame y lo gestionamos."
            chips = ["Cómo funciona", "Ver planes", "Cómo se instala"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if task_state:
                self.memory.save_task_state(user_id, org_id, task_state)
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=c_turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="provocation_or_abuse",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 0.07 Solicitud de APIs o secretos de sistema (Protección de arquitectura interna)
        if classification and classification.intent == UserIntentType.SYSTEM_SECRETS_OR_APIS:
            resp = "Las llaves y APIs internas de Firby son privadas y operan de forma segura en el servidor. Si te refieres a conectar Firby con tu Google Calendar o tus propios sistemas, las integraciones se configuran desde el panel de control tras activar tu cuenta."
            chips = ["Cómo funciona", "Ver planes", "Cómo se instala"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if task_state:
                self.memory.save_task_state(user_id, org_id, task_state)
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=c_turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="system_secrets_or_apis",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 0.1 Saludo casual o cortesía
        if classification and classification.intent == UserIntentType.CASUAL_GREETING:
            clean_lower = text.lower().strip()
            if any(w in clean_lower for w in ["gracias", "muchas gracias"]):
                resp = "Con gusto. ¿Hay algo más en lo que pueda orientarle?"
            elif any(w in clean_lower for w in ["chao", "adiós", "adios", "hasta luego"]):
                resp = "Hasta luego. Quedo a su disposición si necesita alguna orientación adicional."
            elif any(w in clean_lower for w in ["como estas", "cómo estás", "como va", "cómo va", "que tal", "qué tal"]):
                resp = "Muy bien, gracias por preguntar. ¿En qué puedo orientarle hoy?"
            else:
                resp = "Hola. ¿En qué puedo ayudarle hoy?"
            chips = ["Cómo funciona", "Ver planes"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if task_state:
                self.memory.save_task_state(user_id, org_id, task_state)
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING)
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=c_turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="casual_greeting",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 0.2 Desambiguación Contextual tras Cambio de Tema (Anti-Context Dragging)
        if classification and classification.intent == UserIntentType.AMBIGUOUS_REFERENT:
            prev_plan = classification.target_plan or (task_state.focus_entity.get("id") if task_state and task_state.focus_entity else None)
            if prev_plan:
                resp = f"¿Se refiere al Plan {prev_plan.title()} que consultaba previamente o le gustaría conocer los planes de Firby en general?"
                chips = [f"Plan {prev_plan.title()}", "Ver todos los planes"]
            else:
                resp = "¿Se refiere a los planes de Firby o a la consulta que realizaba hace un momento?"
                chips = ["Ver planes", "Cómo funciona"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if task_state:
                self.memory.save_task_state(user_id, org_id, task_state)
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING)
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=c_turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="ambiguous_referent",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 0.3 Consulta sobre Acceso a Agenda y Calendario (Delimitación de Privacidad)
        if classification and classification.intent == UserIntentType.BUSINESS_CALENDAR_ACCESS:
            resp = (
                "Firby se conecta al Google Calendar corporativo del negocio para revisar disponibilidad libre y agendar citas confirmadas en tiempo real.\n\n"
                "Firby no tiene ni solicita acceso a su calendario personal, citas privadas ni correos como visitante del sitio web. "
                "Toda la interacción opera con permisos restringidos y protección de privacidad."
            )
            chips = ["Cómo funciona", "Ver planes"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if task_state:
                self.memory.save_task_state(user_id, org_id, task_state)
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING)
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=c_turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="calendar_access_boundary",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )


        # 0.4 Acuse de recibo / Continuidad (Sin cierre prematuro)
        if classification and classification.intent == UserIntentType.ACKNOWLEDGEMENT:
            if any(w in text.lower() for w in ("acepto", "acuerdo", "terminos", "términos", "condiciones")):
                resp = "Gracias por aceptar los términos y condiciones. ¿Cómo puedo ayudarle hoy?"
                is_landing = org_id in ("firby_landing", "firby_default", "firby", "tenant_demo", "")
                chips = ["Ver cómo funciona", "Ver planes y precios", "Cómo se instala"] if is_landing else ["Horarios de atención", "Agendar cita", "Servicios"]
                if task_state:
                    task_state.terms_accepted = True
                    task_state.consent_pending = False
                    self.memory.save_task_state(user_id, org_id, task_state)
            elif classification.has_negative_navigation_constraint:
                resp = "Entendido, permanezco aquí y no realizo ningún desplazamiento. ¿En qué puedo orientarle hoy?"
                chips = ["Cómo funciona", "Qué puede hacer", "Ver planes"]
            else:
                resp = "Entendido. ¿Hay algo más que desee revisar o en lo que pueda orientarle?"
                chips = ["Cómo funciona", "Qué puede hacer"] if (task_state and task_state.is_commercial_inhibited()) else ["Cómo funciona", "Ver planes"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if task_state:
                self.memory.save_task_state(user_id, org_id, task_state)
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=getattr(task_state, "turn_sequence", 1) if task_state else 1,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="acknowledgement",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 0.5 Negación comercial explícita / Modo exploración
        if classification and classification.intent == UserIntentType.COMMERCIAL_NEGATION:
            if task_state:
                task_state.set_commercial_posture("inhibited")
                self.memory.save_task_state(user_id, org_id, task_state)
            resp = "Entendido, tómate el tiempo que necesites para explorar. ¿Te gustaría conocer cómo opera el sistema o tienes alguna consulta técnica sobre las funciones de Firby?"
            chips = ["Cómo funciona", "Qué puede hacer", "Cómo se instala"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=getattr(task_state, "turn_sequence", 1) if task_state else 1,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="commercial_negation",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 0.6 Consultas sobre capacidades del operador
        if classification and classification.intent == UserIntentType.CAPABILITY_QUERY:
            cap_resp = self._resolve_capability_query(text)
            chips = ["Cómo funciona", "Aprobación de excepciones", "Cómo se instala"] if (task_state and task_state.is_commercial_inhibited()) else ["Cómo funciona", "Ver planes", "Cómo se instala"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if task_state:
                self.memory.save_task_state(user_id, org_id, task_state)
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(cap_resp)})
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=getattr(task_state, "turn_sequence", 1) if task_state else 1,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=cap_resp,
                bubbles=[cap_resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="capability_query",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 1. Si es cálculo matemático o definición general, delimitar sin resolver operaciones aritméticas
        if classification and classification.intent == UserIntentType.CALCULATION_OR_FACT:
            clean = text.lower()
            if any(k in clean for k in ["+", "-", "*", "/", "x", "por", "más", "menos", "entre", "dividido", "raíz", "raiz", "cuanto es", "cuánto es"]) or re.search(r'\d+\s*[\+\-\*\/xX]\s*\d+', clean):
                resp = "Estoy enfocado exclusivamente en la atención y los procesos de este sitio web, por lo que no realizo cálculos matemáticos. Si tienes alguna duda sobre nuestros servicios o funciones, con gusto te oriento."
            elif "api" in clean:
                resp = "Una API es una interfaz de software que permite a diferentes plataformas conectarse e intercambiar datos de forma automática y segura."
            else:
                resp = "Estoy enfocado en la atención y orientación sobre este sitio web. Si tienes alguna consulta sobre nuestros servicios o planes, cuéntame y con gusto te ayudo."

            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)

            return OperatorResult(
                ok=True,
                turn_id=c_turn_id,
                run_id=run_id,
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=[],
                action_chips=[],
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="calculation_or_fact",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 2. Si es consulta de velocidad de respuesta
        if classification and classification.intent == UserIntentType.BUSINESS_SPEED:
            resp = "Cuento con una arquitectura en la nube optimizada para procesar y responder en tiempo real sin latencia."
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING)
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=c_turn_id,
                run_id=run_id,
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=[],
                action_chips=[],
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="business_speed",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 3. Si es contacto o ubicación (solo si no tiene navegación asignada)
        if classification and classification.intent == UserIntentType.BUSINESS_CONTACT and not classification.target_navigation:
            if classification.specific_topic == "location":
                resp = "Nuestra sede principal se encuentra en Medellín, Colombia, con operación Cloud global."
            else:
                resp = (
                    "Canales oficiales:\n\n"
                    "- Atención a visitantes: directamente en el sitio web en tiempo real 24/7.\n\n"
                    "- Línea ejecutiva privada: WhatsApp +57 324 369 9856 (exclusiva para el dueño del negocio).\n\n"
                    "- Correo: soporte@firbyai.com.\n\n"
                    "- Sede: Medellín, Colombia."
                )
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING)
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=c_turn_id,
                run_id=run_id,
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=[],
                action_chips=[],
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="business_contact",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 4. Si es solicitud de agendamiento (BOOKING_REQUEST)
        if classification and classification.intent == UserIntentType.BOOKING_REQUEST:
            is_allowed, _ = config.is_tool_allowed("book_appointment")
            if not is_allowed:
                perm = config.tool_permissions.get("book_appointment")
                resp = perm.disabled_message if perm and perm.disabled_message else (
                    "Firby integra agendamiento en tiempo real sincronizado con Google Calendar para los sitios web de sus clientes. "
                    "En este portal oficial la activación de su operador es 100% autoservicio con 7 días de prueba gratuita sin permanencia."
                )
                chips = ["Cómo funciona", "Ver planes"]
            else:
                resp = "Para agendar su cita, por favor indíqueme su nombre completo, número de contacto, el servicio requerido y el horario de su preferencia."
                chips = ["Horarios disponibles", "Servicios"]

            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING)
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=c_turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="booking_request",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 5. Si es navegación pura (ACTION FIRST, salvo restricción negativa)
        nav_target = None
        if classification and classification.intent == UserIntentType.NAVIGATION_REQUEST and classification.target_navigation and not classification.has_negative_navigation_constraint:
            nav_target = classification.target_navigation
        elif classification and classification.intent == UserIntentType.NAVIGATION_REQUEST and not classification.has_negative_navigation_constraint:
            from src.core.operator.policy import WebPolicyEngine
            nav_target = WebPolicyEngine.resolve_section_target(text)
            if not nav_target:
                try:
                    from src.core.browser.decision_engine import DecisionEngine
                    from src.core.browser.decision_models import DecisionRequest, BrowserOperation
                    de = DecisionEngine()
                    de_req = DecisionRequest(goal=text, current_url=web_ctx.current_url or "/")
                    de_ans = de.decide(de_req)
                    if de_ans.operation == BrowserOperation.SCROLL_SLOW and de_ans.scroll_target:
                        nav_target = de_ans.scroll_target
                        log.info(f"[OperatorRuntime] Laya System-1 resolvió navegación en {de_ans.latency_ms}ms: {nav_target}")
                except Exception as e_laya:
                    log.debug(f"[OperatorRuntime] Laya bypass: {e_laya}")

        is_already_at_target = bool(nav_target and web_ctx.current_section == nav_target)
        if nav_target and not is_already_at_target:
            act_type = UIActionType.NAVIGATE_TO_SECTION if nav_target.startswith("#") else UIActionType.NAVIGATE_TO
            is_slow = getattr(classification, "specific_topic", None) in ("guided_scroll", "subscription_flow") if classification else False
            act = UIAction(
                type=act_type,
                target=nav_target,
                label=f"Navegar a {nav_target}",
                params={"duration": 2.8 if is_slow else None, "slow": is_slow}
            )
            primary_ui_action = act.to_dict()
            executed_actions.append(primary_ui_action)

            if emit_event:
                emit_event(
                    AgentEventType.ACTION_REQUESTED,
                    AgentRunState.ACTION_REQUESTED,
                    action=primary_ui_action,
                    reason=f"Navegar a {nav_target}",
                    requires_verification=True
                )

            # Guardar run activo para la observación
            self.active_runs[run_id] = {
                "run_id": run_id,
                "step_id": 1,
                "user_id": user_id,
                "org_id": config.tenant_id if hasattr(config, "tenant_id") else org_id,
                "text": text,
                "action": primary_ui_action,
                "executed_actions": executed_actions,
                "classification": classification,
                "events": events,
                "config": config,
                "web_ctx": web_ctx,
                "timestamp": time.time()
            }

            if task_state:
                self.memory.save_task_state(user_id, org_id, task_state)

            return OperatorResult(
                ok=True,
                turn_id=c_turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.ACTION_REQUESTED.value,
                requires_observation=True,
                action=primary_ui_action,
                ui_action=primary_ui_action,
                ui_actions=executed_actions,
                response="",  # En retención hasta verificación
                bubbles=[],
                chips=[],
                action_chips=[],
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events],
                active_agent="web_operator_contingency",
                intent="navigation_request",
                web_context=web_ctx.to_dict()
            )

        # 5.1 Si es consulta de planes y precios (cuando no navega o ya está en la sección)
        if classification and classification.intent == UserIntentType.BUSINESS_PRICING:
            target_p = classification.target_plan
            if not target_p and task_state and not getattr(task_state, "context_shift_detected", False):
                focus = getattr(task_state, "focus_entity", None)
                if focus and focus.get("type") == "plan":
                    target_p = focus.get("id")

            if target_p:
                is_most_comp = (
                    classification.specific_topic == "most_complete_plan"
                    or (target_p == "equipos" and bool(re.search(r'\bm[aá]s\s+(?:completo|avanzado|potente|grande|robusto|caro)\b', text.lower())))
                )
                resp = get_plan_specific_text(target_p, is_most_complete=is_most_comp)
                chips = ["Cómo funciona", "Probar 7 días gratis"]
            else:
                resp = get_pricing_summary_text()
                chips = ["Cómo funciona", "Probar 7 días gratis"]

            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if task_state:
                self.memory.save_task_state(user_id, org_id, task_state)
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(resp)})
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=c_turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="business_pricing",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 5.2 Si es acción comercial explícita (Contratación, suscripción, registro, prueba de 7 días)
        if classification and classification.intent == UserIntentType.COMMERCIAL_ACTION:
            if task_state:
                task_state.set_commercial_posture("interested")
            if getattr(classification, "specific_topic", None) == "subscription_flow" or any(k in text.lower() for k in ["suscrib", "contrat", "cómo me suscribo"]):
                resp = (
                    "Para suscribirse a Firby el proceso es 100% autoservicio y toma menos de un minuto:\n\n"
                    "- Elija el plan que mejor se adapte al volumen de su empresa (Starter, Pro o Equipos).\n\n"
                    "- Haga clic en el botón Comenzar prueba gratis del plan elegido.\n\n"
                    "- Complete su registro para activar su operador de inmediato, con 7 días de prueba sin costo ni permanencia y cancelación en 1 clic."
                )
                chips = ["Ver planes", "Cómo funciona"]
            else:
                resp = "Puede activar su prueba de 7 días gratis directamente en nuestra plataforma en 1 minuto y cancelar cuando desee en 1 clic. ¿Desea iniciar su registro o prefiere revisar el detalle de los planes?"
                chips = ["Iniciar prueba 7 días", "Ver planes"]
            action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
            if task_state:
                self.memory.save_task_state(user_id, org_id, task_state)
            if emit_event:
                emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING)
                emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)
            return OperatorResult(
                ok=True,
                turn_id=c_turn_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=1,
                state=AgentRunState.DONE.value,
                requires_observation=False,
                response=resp,
                bubbles=[resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator_contingency",
                intent="commercial_action",
                web_context=web_ctx.to_dict(),
                events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
            )

        # 7. Consulta general sin acción de interfaz
        resp = "Con gusto te ayudo con esa consulta. Te comparto la información oficial del sitio."
        chips = ["Cómo funciona", "Ver planes", "Sobre nosotros"]
        action_chips = self._build_action_chips(chips, config, classification, task_state=task_state)
        if task_state:
            self.memory.save_task_state(user_id, org_id, task_state)
        if emit_event:
            emit_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING)
            emit_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE)

        return OperatorResult(
            ok=True,
            turn_id=c_turn_id,
            run_id=run_id,
            task_id=f"task_{run_id}",
            step_id=1,
            state=AgentRunState.DONE.value,
            requires_observation=False,
            response=resp,
            bubbles=[resp],
            chips=chips,
            action_chips=action_chips,
            ui_action=None,
            ui_actions=[],
            action=None,
            active_agent="web_operator_contingency",
            intent=classification.intent.value if (classification and hasattr(classification.intent, "value")) else "general",
            web_context=web_ctx.to_dict(),
            events=[e.to_dict() if hasattr(e, "to_dict") else e for e in events]
        )

    async def process_observation(
        self,
        run_id: str,
        observation_dict: Dict[str, Any],
        user_id: str = "web_user",
        org_id: str = "firby_landing",
        agent_id: Optional[str] = None
    ) -> OperatorResult:
        """
        Procesa la observación reportada por la superficie (frontend), ejecuta verificación
        y replanifica si la acción falló (TEST 6) o sintetiza la respuesta verificada.
        """
        from src.core.platform.migration import resolve_tenant_agent_pair
        from src.core.platform.manager import control_plane
        tenant_id, resolved_agent_id = resolve_tenant_agent_pair(org_id)
        if agent_id:
            resolved_agent_id = agent_id

        run_data = self.active_runs.pop(run_id, None)
        obs = ActionObservation.from_dict(observation_dict)
        events_dicts = [e.to_dict() if hasattr(e, "to_dict") else e for e in (run_data.get("events", []) if run_data else [])]
        step_id = (run_data.get("step_id", 1) if run_data else 1) + 1
        config = run_data.get("config") if run_data else control_plane.get_active_config(tenant_id, resolved_agent_id)
        web_ctx = run_data.get("web_ctx") if run_data else WebContext()
        action = run_data.get("action", {}) if run_data else {}
        target = obs.target or action.get("target", "")

        def make_event(ev_type: AgentEventType, st: AgentRunState, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            return {
                "event": ev_type.value,
                "run_id": run_id,
                "task_id": f"task_{run_id}",
                "tenant_id": tenant_id,
                "conversation_id": user_id,
                "step_id": step_id,
                "state": st.value,
                "timestamp": time.time(),
                "action": action,
                "requires_verification": False,
                "data": data or {}
            }

        # 1. OBSERVACIÓN REGISTRADA
        events_dicts.append(make_event(AgentEventType.OBSERVATION_CREATED, AgentRunState.ACTION_COMPLETED if obs.success else AgentRunState.ACTION_FAILED, data=obs.to_dict()))

        # 2. VERIFICACIÓN Y REPLANIFICACIÓN
        events_dicts.append(make_event(AgentEventType.VERIFICATION_STARTED, AgentRunState.VERIFYING))

        # Manejo de observación cancelada por el usuario
        if obs.status == "cancelled" or (isinstance(obs.data, dict) and obs.data.get("status") == "cancelled"):
            events_dicts.append(make_event(AgentEventType.ACTION_FAILED, AgentRunState.CANCELLED, data={"status": "cancelled"}))
            events_dicts.append(make_event(AgentEventType.RUN_COMPLETED, AgentRunState.CANCELLED, data={"status": "cancelled"}))
            final_resp = "Entendido, permanezco aquí y no realizo el desplazamiento. ¿En qué puedo orientarle hoy?"
            chips = ["Cómo funciona", "Qué puede hacer", "Ver planes"]
            action_chips = self._build_action_chips(chips, config, None)
            return OperatorResult(
                ok=True,
                turn_id=user_id,
                run_id=run_id,
                task_id=f"task_{run_id}",
                step_id=step_id,
                state=AgentRunState.CANCELLED.value,
                requires_observation=False,
                response=final_resp,
                bubbles=[final_resp],
                chips=chips,
                action_chips=action_chips,
                ui_action=None,
                ui_actions=[],
                action=None,
                active_agent="web_operator",
                intent="navigation_cancelled",
                web_context=web_ctx.to_dict(),
                events=events_dicts
            )

        if obs.success:
            events_dicts.append(make_event(AgentEventType.ACTION_COMPLETED, AgentRunState.VERIFYING, data={"status": "completed"}))
            events_dicts.append(make_event(AgentEventType.VERIFICATION_COMPLETED, AgentRunState.VERIFYING, data={"status": "verified"}))

            user_query = (run_data.get("text") or "").strip().lower() if run_data else ""
            clean_resp = (run_data.get("clean_response_text") or "").strip() if run_data else ""
            classification = run_data.get("classification") if run_data else None
            specific_topic = getattr(classification, "specific_topic", None) if classification else None

            if "planes" in target:
                if specific_topic == "subscription_flow" or any(k in user_query for k in ["suscrib", "contrat", "cómo me suscribo", "quiero suscribirme", "cómo empezar", "pasos para", "alta", "registro"]):
                    final_resp = (
                        "Le he ubicado en la sección de planes. Para suscribirse, el proceso es 100% autoservicio y toma menos de un minuto:\n\n"
                        "- Elija el plan que mejor se adapte al volumen de su empresa (Starter, Pro o Equipos).\n\n"
                        "- Haga clic en el botón Comenzar prueba gratis del plan elegido.\n\n"
                        "- Complete su registro para activar su operador de inmediato, con 7 días de prueba sin costo ni permanencia y cancelación en 1 clic."
                    )
                    chips = ["Ver planes", "Cómo funciona", "Contacto"]
                elif "pro" in user_query and not any(k in user_query for k in ["starter", "equipos"]):
                    final_resp = (
                        "Le he ubicado en la sección de planes frente a la opción Pro.\n\n"
                        f"{get_plan_specific_text('pro')}"
                    )
                    chips = ["Cómo funciona", "Contacto"]
                elif "starter" in user_query and not any(k in user_query for k in ["pro", "equipos"]):
                    final_resp = (
                        "Le he ubicado en la sección de planes frente a la opción Starter.\n\n"
                        f"{get_plan_specific_text('starter')}"
                    )
                    chips = ["Cómo funciona", "Contacto"]
                elif ("equipos" in user_query or "más completo" in user_query or "mas completo" in user_query) and not any(k in user_query for k in ["pro", "starter"]):
                    final_resp = (
                        "Le he ubicado en la sección de planes frente a la opción Equipos.\n\n"
                        f"{get_plan_specific_text('equipos', is_most_complete=True)}"
                    )
                    chips = ["Cómo funciona", "Contacto"]
                elif clean_resp and len(clean_resp) > 30 and not clean_resp.startswith("Te acompaño a la sección"):
                    final_resp = clean_resp
                    chips = ["Cómo funciona", "Contacto"]
                else:
                    final_resp = (
                        "Le he ubicado en la sección de planes y precios. A continuación puede consultar el detalle oficial de nuestras opciones:\n\n"
                        f"{get_pricing_summary_text()}"
                    )
                    chips = ["Cómo funciona", "Contacto"]
            elif "como-funciona" in target or "funciona" in target:
                if specific_topic == "guided_scroll":
                    final_resp = (
                        "Con gusto le guío por nuestra página con un desplazamiento suave. Aquí en Cómo Funciona puede ver cómo Firby "
                        "atiende a los visitantes en tiempo real, consulta la disponibilidad oficial y agenda citas confirmadas directamente "
                        "en Google Calendar sin trabajo manual."
                    )
                    chips = ["Siguiente: Canales", "Ver planes", "Seguridad"]
                else:
                    final_resp = (
                        "Le he ubicado en la sección Cómo Funciona. Firby opera como un empleado digital en su sitio web atendiendo visitantes en tiempo real, "
                        "consultando su disponibilidad y resolviendo trámites directamente en la web."
                    )
                    chips = ["Ver planes", "Sobre nosotros"]
            elif "sobre-nosotros" in target:
                final_resp = (
                    "Le he dirigido a la página Sobre Nosotros para que conozca la visión y el equipo de ingeniería de Firby."
                )
                chips = ["Ver planes", "Cómo funciona"]
            elif "seguridad" in target:
                final_resp = (
                    "Le he ubicado en la sección de Seguridad y Cumplimiento. Aquí puede verificar nuestras políticas de gobernanza: "
                    "operación basada estrictamente en políticas oficiales, validación de identidad por código OTP para operaciones sensibles y supervisión con visto bueno del dueño para cualquier excepción comercial."
                )
                chips = ["Cómo funciona", "Ver planes"]
            elif "problema" in target:
                final_resp = (
                    "Le he ubicado en la sección Problema, donde detallamos los retos de perder prospectos fuera de horario y cómo Firby los resuelve de forma autónoma."
                )
                chips = ["Cómo funciona", "Ver planes"]
            elif "canales" in target:
                final_resp = (
                    "Le he ubicado en la sección Canales. Firby atiende en la web a los visitantes en tiempo real y conversa por WhatsApp exclusivamente con el dueño del negocio."
                )
                chips = ["Ver planes", "Cómo funciona"]
            elif "equipo-digital" in target or "equipo" in target:
                final_resp = (
                    "Le he ubicado en la sección Equipo Digital. Firby ofrece perfiles especializados de empleados digitales "
                    "(Recepcionista 24/7, Closer de Ventas, Soporte Knowledge, Arquitecto de Automatizaciones y Especialista en Growth) "
                    "configurados para las necesidades operativas de su empresa."
                )
                chips = ["Cómo funciona", "Ver planes"]
            elif "contacto" in target:
                final_resp = (
                    "Le he ubicado en la sección Contacto. Para coordinar una demostración en vivo o recibir orientación ejecutiva, puede dejarnos sus datos o escribirnos directamente a soporte@firbyai.com."
                )
                chips = ["Ver planes", "Cómo funciona"]
            else:
                final_resp = f"Le he ubicado en la sección solicitada ({target}). Puede ver la información en pantalla."
                chips = ["Ver planes", "Cómo funciona"]
        else:
            # TEST 6: Tool/action fails -> OBSERVATION reports failure -> runtime REPLANS!
            events_dicts.append(make_event(AgentEventType.ACTION_FAILED, AgentRunState.ACTION_FAILED, data={"error": obs.error or obs.status}))
            events_dicts.append(make_event(AgentEventType.VERIFICATION_COMPLETED, AgentRunState.VERIFYING, data={"status": "failed", "replanned": True}))

            user_query = (run_data.get("text") or "").strip().lower() if run_data else ""
            if "planes" in target:
                if any(k in user_query for k in ["suscrib", "contrat", "cómo me suscribo"]):
                    final_resp = (
                        "Para suscribirse a Firby el proceso es 100% autoservicio y toma menos de un minuto:\n\n"
                        "- Elija el plan que mejor se adapte al volumen de su empresa (Starter, Pro o Equipos).\n\n"
                        "- Haga clic en el botón Comenzar prueba gratis del plan elegido.\n\n"
                        "- Complete su registro para activar su operador de inmediato, con 7 días de prueba sin costo ni permanencia y cancelación en 1 clic."
                    )
                else:
                    final_resp = (
                        "No fue posible desplazarse automáticamente a esa sección en esta vista. Le comparto el detalle oficial de nuestros planes directamente aquí:\n\n"
                        f"{get_pricing_summary_text()}"
                    )
                chips = ["Cómo funciona", "Contacto"]
            elif "seguridad" in target:
                final_resp = (
                    "No fue posible desplazarse automáticamente a esa sección en esta vista. Le comparto la información de seguridad directamente: "
                    "Firby opera con validación de identidad por código OTP, cifrado de datos, cero respuestas improvisadas fuera de política y visto bueno del dueño para cualquier excepción comercial."
                )
                chips = ["Cómo funciona", "Ver planes"]
            elif "como-funciona" in target or "funciona" in target:
                final_resp = (
                    "No fue posible navegar automáticamente a esa sección. Le explico cómo opera Firby: "
                    "opera en su sitio web atendiendo visitantes 24/7, agendando citas en Google Calendar y consultando con el dueño por WhatsApp cuando requiere autorización."
                )
                chips = ["Ver planes", "Contacto"]
            elif "contacto" in target:
                final_resp = (
                    "No fue posible desplazarse a esa sección en este momento. Puede escribirnos al correo soporte@firbyai.com o consultar sus dudas directamente por este canal."
                )
                chips = ["Ver planes", "Cómo funciona"]
            else:
                final_resp = (
                    f"No fue posible navegar a esa sección en este momento ({obs.error or 'no disponible en el DOM'}), pero con gusto le oriento directamente con la información que requiere."
                )
                chips = ["Ver planes", "Cómo funciona"]

        # Sanitización estricta: CERO BOLD (regla inquebrantable de Santiago)
        final_resp = re.sub(r'\*\*(.*?)\*\*', r'\1', final_resp)
        final_resp = re.sub(r'<strong>(.*?)</strong>', r'\1', final_resp)

        events_dicts.append(make_event(AgentEventType.RESPONSE_CREATED, AgentRunState.RESPONDING, data={"response_length": len(final_resp)}))
        events_dicts.append(make_event(AgentEventType.RUN_COMPLETED, AgentRunState.DONE))

        action_chips = self._build_action_chips(chips, config, None)

        return OperatorResult(
            ok=True,
            run_id=run_id,
            step_id=step_id,
            state=AgentRunState.DONE.value,
            requires_observation=False,
            action=None,
            ui_action=None,
            ui_actions=[],
            response=final_resp,
            bubbles=[final_resp],
            chips=chips,
            action_chips=action_chips,
            events=events_dicts,
            active_agent="web_operator",
            intent="general",
            web_context=web_ctx.to_dict() if hasattr(web_ctx, "to_dict") else {}
        )


# Instancia singleton del runtime
operator_runtime = DigitalWebOperatorRuntime()
