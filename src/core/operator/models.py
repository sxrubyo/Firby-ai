# -*- coding: utf-8 -*-
"""
Firby AI — Web Operator Models
==============================
Modelos de datos y esquemas para la capa de control web, navegación del sitio,
acciones de interfaz y contexto en tiempo real del visitante.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class UIActionType(str, Enum):
    NAVIGATE_TO = "navigate_to"
    NAVIGATE_TO_SECTION = "navigate_to_section"
    SCROLL_TO = "scroll_to"
    HIGHLIGHT = "highlight"
    OPEN_MODAL = "open_modal"
    OPEN_FORM = "open_form"
    FOCUS_ELEMENT = "focus_element"


import time

class AgentRunState(str, Enum):
    IDLE = "IDLE"
    MESSAGE_RECEIVED = "MESSAGE_RECEIVED"
    THINKING = "THINKING"
    DECIDING = "DECIDING"
    ACTION_REQUESTED = "ACTION_REQUESTED"
    ACTION_STARTED = "ACTION_STARTED"
    ACTION_COMPLETED = "ACTION_COMPLETED"
    ACTION_FAILED = "ACTION_FAILED"
    VERIFYING = "VERIFYING"
    RESPONDING = "RESPONDING"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    REPLANNING = "REPLANNING"
    TIMED_OUT = "TIMED_OUT"
    CANCELLED = "CANCELLED"
    DONE = "DONE"
    ERROR = "ERROR"


class AgentEventType(str, Enum):
    MESSAGE_RECEIVED = "agent.message.received"
    THINKING_STARTED = "agent.thinking.started"
    DECISION_CREATED = "agent.decision.created"
    ACTION_REQUESTED = "agent.action.requested"
    ACTION_STARTED = "agent.action.started"
    ACTION_COMPLETED = "agent.action.completed"
    ACTION_FAILED = "agent.action.failed"
    TOOL_CALL_REQUESTED = "agent.tool.call_requested"
    TOOL_PERMISSION_CHECKED = "agent.tool.permission_checked"
    TOOL_VALIDATION_CHECKED = "agent.tool.validation_checked"
    TOOL_EXECUTION_STARTED = "agent.tool.execution_started"
    TOOL_EXECUTION_COMPLETED = "agent.tool.execution_completed"
    TOOL_EXECUTION_FAILED = "agent.tool.execution_failed"
    OBSERVATION_CREATED = "agent.observation.created"
    VERIFICATION_STARTED = "agent.verification.started"
    VERIFICATION_COMPLETED = "agent.verification.completed"
    RESPONSE_CREATED = "agent.response.created"
    RUN_COMPLETED = "agent.run.completed"
    RUN_FAILED = "agent.run.failed"


class UserIntentCategory(str, Enum):
    FACTUAL_QUERY = "factual_query"
    UNKNOWN_BOUNDARY = "unknown_boundary"
    NAVIGATION_REQUEST = "navigation_request"
    HOW_IT_WORKS = "how_it_works"
    PRICING_INQUIRY = "pricing_inquiry"
    SETUP_INQUIRY = "setup_inquiry"
    TEAM_INQUIRY = "team_inquiry"
    BOOKING_REQUEST = "booking_request"
    GREETING = "greeting"
    GENERAL = "general"


@dataclass
class WebContext:
    """Contexto en tiempo real de la página donde se encuentra el usuario."""
    current_url: str = "/"
    current_section: str = "#hero"
    page_title: str = "Firby"
    available_sections: List[str] = field(default_factory=lambda: [
        "#hero", "#problema", "#como-funciona", "#sobre-nosotros",
        "#equipo-digital", "#canales", "#seguridad-cumplimiento", "#planes", "#contacto"
    ])
    interactive_elements: List[str] = field(default_factory=list)
    last_navigation_event: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> WebContext:
        if not data or not isinstance(data, dict):
            return cls()
        return cls(
            current_url=str(data.get("current_url") or "/"),
            current_section=str(data.get("current_section") or "#hero"),
            page_title=str(data.get("page_title") or "Firby"),
            available_sections=data.get("available_sections") or [
                "#hero", "#problema", "#como-funciona", "#sobre-nosotros",
                "#equipo-digital", "#canales", "#seguridad-cumplimiento", "#planes", "#contacto"
            ],
            interactive_elements=data.get("interactive_elements") or [],
            last_navigation_event=data.get("last_navigation_event")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_url": self.current_url,
            "current_section": self.current_section,
            "page_title": self.page_title,
            "available_sections": self.available_sections,
            "interactive_elements": self.interactive_elements,
            "last_navigation_event": self.last_navigation_event
        }


@dataclass
class UIAction:
    """Acción estructurada sobre la interfaz web del usuario."""
    type: UIActionType
    target: str
    params: Dict[str, Any] = field(default_factory=dict)
    label: str = ""
    requires_confirmation: bool = False
    confirmation_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "type": self.type.value if isinstance(self.type, UIActionType) else str(self.type),
            "target": self.target,
            "route": self.target,  # compatibilidad con frontend legacy
            "params": self.params,
            "label": self.label,
            "requires_confirmation": self.requires_confirmation,
            "confirmation_text": self.confirmation_text
        }
        if self.params:
            for k, v in self.params.items():
                if k not in res:
                    res[k] = v
        return res


@dataclass
class ActionChip:
    """Chip interactivo que combina respuesta visual con acción ejecutable."""
    label: str
    action_type: Optional[str] = None
    action_target: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "action_type": self.action_type,
            "action_target": self.action_target,
            "payload": self.payload
        }


@dataclass
class AgentEvent:
    """Evento estructurado emitido durante el ciclo de vida de un run."""
    event: AgentEventType
    run_id: str
    task_id: str
    tenant_id: str
    conversation_id: str
    step_id: int
    state: AgentRunState
    timestamp: float = field(default_factory=lambda: __import__('time').time())
    action: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    requires_verification: bool = False
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": self.event.value if isinstance(self.event, AgentEventType) else str(self.event),
            "run_id": self.run_id,
            "task_id": self.task_id,
            "tenant_id": self.tenant_id,
            "conversation_id": self.conversation_id,
            "step_id": self.step_id,
            "state": self.state.value if isinstance(self.state, AgentRunState) else str(self.state),
            "timestamp": self.timestamp,
            "action": self.action,
            "reason": self.reason,
            "requires_verification": self.requires_verification,
            "data": self.data
        }


@dataclass
class ActionObservation:
    """Observación reportada por la superficie (frontend o tool executor) tras ejecutar una acción."""
    run_id: str = ""
    step_id: int = 1
    status: str = "executed"
    action_id: Optional[str] = None
    target: Optional[str] = None
    success: bool = True
    error: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: Optional[Dict[str, Any]]) -> ActionObservation:
        if not d or not isinstance(d, dict):
            return cls(run_id="", step_id=0, status="unknown", success=False, error="invalid observation payload")
        return cls(
            run_id=str(d.get("run_id") or ""),
            step_id=int(d.get("step_id") or 0),
            status=str(d.get("status") or "executed"),
            action_id=d.get("action_id"),
            target=d.get("target"),
            success=bool(d.get("success", True) if d.get("status") != "section_target_missing" and not d.get("error") else False),
            error=d.get("error"),
            data=d.get("data") or {}
        )

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "run_id": self.run_id,
            "step_id": self.step_id,
            "status": self.status,
            "target": self.target,
            "success": self.success,
            "error": self.error,
            "data": self.data
        }
        if self.action_id:
            res["action_id"] = self.action_id
        return res


@dataclass
class OperatorResult:
    """Resultado unificado del Digital Web Operator."""
    ok: bool = True
    response: str = ""
    bubbles: List[str] = field(default_factory=list)
    chips: List[str] = field(default_factory=list)
    action_chips: List[Dict[str, Any]] = field(default_factory=list)
    ui_action: Optional[Dict[str, Any]] = None
    ui_actions: List[Dict[str, Any]] = field(default_factory=list)
    action: Optional[Dict[str, Any]] = None
    action_card: Optional[Dict[str, Any]] = None
    active_agent: str = "landing.concierge"
    intent: str = "general"
    web_context: Dict[str, Any] = field(default_factory=dict)
    handoff_history: List[str] = field(default_factory=list)
    inter_agent_messages: List[Dict[str, Any]] = field(default_factory=list)
    run_id: str = ""
    task_id: str = ""
    step_id: int = 0
    state: str = "DONE"
    requires_observation: bool = False
    turn_id: int = 0
    events: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "response": self.response,
            "bubbles": self.bubbles,
            "chips": self.chips,
            "action_chips": self.action_chips,
            "ui_action": self.ui_action,
            "ui_actions": self.ui_actions,
            "action": self.action or self.ui_action,
            "action_card": self.action_card,
            "active_agent": self.active_agent,
            "intent": self.intent,
            "web_context": self.web_context,
            "handoff_history": self.handoff_history,
            "inter_agent_messages": self.inter_agent_messages,
            "run_id": self.run_id,
            "task_id": self.task_id,
            "step_id": self.step_id,
            "turn_id": self.turn_id,
            "state": self.state,
            "status": "COMPLETED" if self.state == "DONE" else ("ACTION_REQUESTED" if self.requires_observation else self.state),
            "is_complete": self.state == "DONE",
            "requires_observation": self.requires_observation,
            "events": self.events
        }


@dataclass
class AgentStep:
    """Paso cognitivo o de acción individual dentro de una tarea."""
    step_id: int
    task_id: str
    run_id: str = ""
    state: AgentRunState = AgentRunState.THINKING
    thought: str = ""
    decision: str = ""
    tool_call: Optional[Dict[str, Any]] = None
    tool_result: Optional[Dict[str, Any]] = None
    observation: Optional[Dict[str, Any]] = None
    verification: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "task_id": self.task_id,
            "run_id": self.run_id,
            "state": self.state.value if isinstance(self.state, AgentRunState) else str(self.state),
            "thought": self.thought,
            "decision": self.decision,
            "tool_call": self.tool_call,
            "tool_result": self.tool_result,
            "observation": self.observation,
            "verification": self.verification,
            "error": self.error,
            "timestamp": self.timestamp
        }


@dataclass
class AgentTask:
    """Meta u objetivo en ejecución asignado al agente."""
    task_id: str
    run_id: str
    goal: str
    state: AgentRunState = AgentRunState.THINKING
    steps: List[AgentStep] = field(default_factory=list)
    slots: Dict[str, Any] = field(default_factory=dict)
    missing_slots: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "run_id": self.run_id,
            "goal": self.goal,
            "state": self.state.value if isinstance(self.state, AgentRunState) else str(self.state),
            "steps": [s.to_dict() for s in self.steps],
            "slots": self.slots,
            "missing_slots": self.missing_slots,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


@dataclass
class AgentRun:
    """Ejecución completa de un ciclo multi-turno para una conversación y tenant."""
    run_id: str
    conversation_id: str
    tenant_id: str = "firby_landing"
    state: AgentRunState = AgentRunState.IDLE
    tasks: List[AgentTask] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "conversation_id": self.conversation_id,
            "tenant_id": self.tenant_id,
            "state": self.state.value if isinstance(self.state, AgentRunState) else str(self.state),
            "tasks": [t.to_dict() for t in self.tasks],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

