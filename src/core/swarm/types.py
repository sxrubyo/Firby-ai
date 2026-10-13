# -*- coding: utf-8 -*-
"""
Firby Multi-Agent Swarm Types & Protocols
=========================================
Define las estructuras de datos, enums y contratos para la red de agentes
escalable a cientos de agentes interactivos y workers.
"""

from __future__ import annotations
import uuid
import time
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field


class AgentDomain(str, Enum):
    SYSTEM = "system"
    CORE = "core"
    SALES = "sales"
    CLINICAL = "clinical"
    BILLING = "billing"
    OPERATIONS = "operations"
    TENANT = "tenant"
    WORKER = "worker"
    ESCALATION = "escalation"


class MessageType(str, Enum):
    HANDOFF = "handoff"                 # Transferencia de control en la conversación
    PEER_QUERY = "peer_query"           # Consulta síncrona entre agentes antes de responder
    PEER_RESPONSE = "peer_response"     # Respuesta de la consulta entre pares
    EVENT_PUBLISH = "event_publish"     # Publicación de eventos a la red (pub/sub)
    WORKER_TASK = "worker_task"         # Despacho de tarea no conversacional asíncrona


@dataclass
class AgentMessage:
    """Mensaje estructurado transmitido a través del SwarmMessageBus."""
    id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    sender_id: str = ""
    recipient_id: str = ""              # ID específico de agente o 'broadcast'
    conversation_id: str = ""
    org_id: str = ""
    message_type: MessageType = MessageType.HANDOFF
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "conversation_id": self.conversation_id,
            "org_id": self.org_id,
            "message_type": self.message_type.value if isinstance(self.message_type, MessageType) else str(self.message_type),
            "payload": self.payload,
            "created_at": self.created_at
        }


@dataclass
class AgentMetadata:
    """Descriptor de capacidades y enrutamiento para el registro de agentes."""
    id: str                             # Identificador único (ej: 'landing.concierge', 'tenant.clinica.dermatology')
    name: str                           # Nombre legible
    domain: AgentDomain = AgentDomain.CORE
    description: str = ""               # Descripción concisa para el switchboard semántico
    capabilities: List[str] = field(default_factory=list)  # Etiquetas para búsqueda rápida (ej: ['planes', 'precios'])
    system_prompt: str = ""             # Prompt maestro optimizado bajo estándares Anthropic/OpenAI
    tools: List[str] = field(default_factory=list)          # Herramientas permitidas para este agente
    allowed_handoffs: List[str] = field(default_factory=lambda: ["*"])  # A quiénes puede transferir
    is_conversational: bool = True      # Si es False, es un worker de fondo
    org_id: Optional[str] = None        # Si tiene org_id, pertenece exclusivamente a ese tenant

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain.value if isinstance(self.domain, AgentDomain) else str(self.domain),
            "description": self.description,
            "capabilities": self.capabilities,
            "tools": self.tools,
            "allowed_handoffs": self.allowed_handoffs,
            "is_conversational": self.is_conversational,
            "org_id": self.org_id
        }


@dataclass
class SwarmResult:
    """Resultado unificado del ciclo agéntico para la interfaz web/widget."""
    response: str
    bubbles: List[str]
    chips: List[str]
    ui_action: Optional[Dict[str, Any]] = None
    action_card: Optional[Dict[str, Any]] = None
    active_agent: str = ""
    handoff_history: List[str] = field(default_factory=list)
    inter_agent_messages: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "response": self.response,
            "bubbles": self.bubbles,
            "chips": self.chips,
            "ui_action": self.ui_action,
            "action_card": self.action_card,
            "active_agent": self.active_agent,
            "handoff_history": self.handoff_history,
            "inter_agent_messages": self.inter_agent_messages,
            "context": self.context
        }
