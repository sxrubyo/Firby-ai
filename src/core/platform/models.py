# -*- coding: utf-8 -*-
"""
Firby Platform — Core Multi-Tenant Domain Models
================================================
Define los contratos de datos fundamentales del Control Plane y Data Plane:
- Tenant: Unidad fundamental de aislamiento organizativo.
- AgentInstance: Instancia de agente perteneciente a un tenant.
- AgentManifest: Contrato inmutable que documenta la composición exacta de una versión.
- AgentVersionRecord: Registro histórico para versionado y rollback atómico.
- KnowledgeItem: Contenido de conocimiento particionado por tenant y agente.
- AuditEvent: Registro de auditoría administrativa y de decisiones de runtime.
- WidgetSession: Sesión pública segura y vinculada (pinned) a un tenant/agente.
"""

from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional


class TenantStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class AgentStatus(str, Enum):
    DRAFT = "draft"
    VALIDATING = "validating"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class Tenant:
    """Entidad principal de Tenant (Inquilino / Organización)."""
    tenant_id: str
    name: str
    status: TenantStatus = TenantStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "name": self.name,
            "status": self.status.value if isinstance(self.status, TenantStatus) else str(self.status),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Tenant:
        return cls(
            tenant_id=d.get("tenant_id", ""),
            name=d.get("name", ""),
            status=TenantStatus(d.get("status", "active")),
            created_at=d.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=d.get("updated_at", datetime.now(timezone.utc).isoformat()),
            metadata=d.get("metadata") or {}
        )


@dataclass
class AgentInstance:
    """Instancia de Agente perteneciente a un Tenant (1 Tenant -> 1..N Agents)."""
    agent_id: str
    tenant_id: str
    name: str
    status: AgentStatus = AgentStatus.DRAFT
    runtime_version: str = "1.0.0"
    published_version: Optional[int] = None
    public_id: str = ""
    allowed_channels: List[str] = field(default_factory=lambda: ["web"])
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "status": self.status.value if isinstance(self.status, AgentStatus) else str(self.status),
            "runtime_version": self.runtime_version,
            "published_version": self.published_version,
            "public_id": self.public_id,
            "allowed_channels": self.allowed_channels,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> AgentInstance:
        return cls(
            agent_id=d.get("agent_id", ""),
            tenant_id=d.get("tenant_id", ""),
            name=d.get("name", ""),
            status=AgentStatus(d.get("status", "draft")),
            runtime_version=d.get("runtime_version", "1.0.0"),
            published_version=d.get("published_version"),
            public_id=d.get("public_id", ""),
            allowed_channels=d.get("allowed_channels") or ["web"],
            created_at=d.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=d.get("updated_at", datetime.now(timezone.utc).isoformat()),
            metadata=d.get("metadata") or {}
        )


@dataclass
class AgentManifest:
    """Contrato auditado que describe exactamente la composición técnica de un agente publicado."""
    agent_id: str
    tenant_id: str
    version: int
    runtime_version: str = "1.0.0"
    config_version: int = 1
    knowledge_version: int = 1
    toolset_version: int = 1
    policy_version: int = 1
    memory_policy_version: int = 1
    ui_version: int = 1
    published_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    published_by: str = "system"
    checksum: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    business_name: str = ""
    business_summary: str = ""
    website_url: str = ""
    enabled_capabilities: List[str] = field(default_factory=list)

    def compute_checksum(self, payload: Dict[str, Any]) -> str:
        """Calcula un hash SHA-256 inmutable de la configuración publicada."""
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "tenant_id": self.tenant_id,
            "version": self.version,
            "runtime_version": self.runtime_version,
            "config_version": self.config_version,
            "knowledge_version": self.knowledge_version,
            "toolset_version": self.toolset_version,
            "policy_version": self.policy_version,
            "memory_policy_version": self.memory_policy_version,
            "ui_version": self.ui_version,
            "published_at": self.published_at,
            "published_by": self.published_by,
            "checksum": self.checksum,
            "metadata": self.metadata,
            "business_name": self.business_name,
            "business_summary": self.business_summary,
            "website_url": self.website_url,
            "enabled_capabilities": self.enabled_capabilities
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> AgentManifest:
        return cls(
            agent_id=d.get("agent_id", ""),
            tenant_id=d.get("tenant_id", ""),
            version=d.get("version", 1),
            runtime_version=d.get("runtime_version", "1.0.0"),
            config_version=d.get("config_version", 1),
            knowledge_version=d.get("knowledge_version", 1),
            toolset_version=d.get("toolset_version", 1),
            policy_version=d.get("policy_version", 1),
            memory_policy_version=d.get("memory_policy_version", 1),
            ui_version=d.get("ui_version", 1),
            published_at=d.get("published_at", datetime.now(timezone.utc).isoformat()),
            published_by=d.get("published_by", "system"),
            checksum=d.get("checksum", ""),
            metadata=d.get("metadata") or {},
            business_name=d.get("business_name", ""),
            business_summary=d.get("business_summary", ""),
            website_url=d.get("website_url", ""),
            enabled_capabilities=d.get("enabled_capabilities") or []
        )


@dataclass
class AgentVersionRecord:
    """Snapshot histórico persistente de una versión de agente (para rollback atómico)."""
    agent_id: str
    tenant_id: str
    version: int
    manifest_dict: Dict[str, Any]
    config_dict: Dict[str, Any]
    status: str = "published"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "tenant_id": self.tenant_id,
            "version": self.version,
            "manifest": self.manifest_dict,
            "config": self.config_dict,
            "status": self.status,
            "created_at": self.created_at
        }


@dataclass
class KnowledgeItem:
    """Documento de conocimiento con partición estricta por Tenant y Agente."""
    doc_id: str
    tenant_id: str
    agent_id: str  # Puede ser '*' para conocimiento global del tenant
    title: str
    content: str
    source: str = "manual"
    version: int = 1
    scope: str = "public"  # public, internal, private
    priority: int = 0
    status: str = "active"  # active, draft, archived
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "title": self.title,
            "content": self.content,
            "source": self.source,
            "version": self.version,
            "scope": self.scope,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> KnowledgeItem:
        return cls(
            doc_id=d.get("doc_id", ""),
            tenant_id=d.get("tenant_id", ""),
            agent_id=d.get("agent_id", "*"),
            title=d.get("title", ""),
            content=d.get("content", ""),
            source=d.get("source", "manual"),
            version=int(d.get("version", 1)),
            scope=d.get("scope", "public"),
            priority=int(d.get("priority", 0)),
            status=d.get("status", "active"),
            created_at=d.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=d.get("updated_at", datetime.now(timezone.utc).isoformat()),
            metadata=d.get("metadata") or {}
        )


@dataclass
class AuditEvent:
    """Registro inmutable de auditoría para trazabilidad de gobernanza."""
    event_id: str
    tenant_id: str
    agent_id: str
    action: str
    actor: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "action": self.action,
            "actor": self.actor,
            "details": self.details,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> AuditEvent:
        return cls(
            event_id=d.get("event_id", ""),
            tenant_id=d.get("tenant_id", ""),
            agent_id=d.get("agent_id", ""),
            action=d.get("action", ""),
            actor=d.get("actor", ""),
            details=d.get("details") or {},
            timestamp=d.get("timestamp", datetime.now(timezone.utc).isoformat())
        )


@dataclass
class WidgetSession:
    """Sesión pública de widget vinculada criptográficamente a un Tenant y Agente."""
    session_token: str
    public_id: str
    tenant_id: str
    agent_id: str
    conversation_id: str
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + (30 * 86400))  # 30 días
    last_seen_at: float = field(default_factory=time.time)
    client_metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_token": self.session_token,
            "public_id": self.public_id,
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "conversation_id": self.conversation_id,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "last_seen_at": self.last_seen_at,
            "client_metadata": self.client_metadata
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> WidgetSession:
        return cls(
            session_token=d.get("session_token", ""),
            public_id=d.get("public_id", ""),
            tenant_id=d.get("tenant_id", ""),
            agent_id=d.get("agent_id", ""),
            conversation_id=d.get("conversation_id", ""),
            created_at=float(d.get("created_at", time.time())),
            expires_at=float(d.get("expires_at", time.time() + (30 * 86400))),
            last_seen_at=float(d.get("last_seen_at", time.time())),
            client_metadata=d.get("client_metadata") or {}
        )


@dataclass
class ValidationResult:
    """Resultado de la validación previa a la publicación de un agente."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
