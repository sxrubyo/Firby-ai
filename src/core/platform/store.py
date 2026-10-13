# -*- coding: utf-8 -*-
"""
Firby Platform — Multi-Tenant Storage Layer
===========================================
Garantiza persistencia segura y aislada en SQLite (firby_ultra.db) para:
- Tenants y metadatos de negocio.
- Instancias de agentes y permisos asociados.
- Historial de versiones y manifiestos de publicación para rollback atómico.
- Base de conocimiento estructurada y particionada por Tenant y Agente.
- Credenciales server-side e integraciones de infraestructura.
- Sesiones de widget seguras vinculadas inequívocamente al tenant.
- Registro de auditoría (Audit Trail) de acciones administrativas y runtime.

Regla inquebrantable de seguridad:
Toda consulta a recursos persistentes aplica filtrado estricto por tenant_id.
"""

from __future__ import annotations
import json
import sqlite3
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from src.core.platform.models import (
    Tenant, TenantStatus, AgentInstance, AgentStatus, AgentManifest,
    AgentVersionRecord, KnowledgeItem, AuditEvent, WidgetSession
)

log = logging.getLogger("firby.platform.store")


class PlatformStore:
    """Almacén central persistente y multi-tenant de la plataforma Firby."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            import os
            db_path = os.getenv("PLATFORM_DB_PATH") or os.getenv("FIRBY_ULTRA_DB") or "firby_ultra.db"
        self.db_path = db_path
        self._init_tables()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_tables(self):
        """Inicializa las tablas del Control Plane multi-tenant si no existen."""
        try:
            with self._get_connection() as conn:
                cur = conn.cursor()

                # 1. Tenants
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS platform_tenants (
                        tenant_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'active',
                        metadata_json TEXT DEFAULT '{}',
                        created_at TEXT,
                        updated_at TEXT
                    )
                """)

                # 2. Agent Instances
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS platform_agent_instances (
                        agent_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'draft',
                        runtime_version TEXT NOT NULL DEFAULT '1.0.0',
                        published_version INTEGER,
                        public_id TEXT UNIQUE,
                        allowed_channels_json TEXT DEFAULT '["web"]',
                        metadata_json TEXT DEFAULT '{}',
                        created_at TEXT,
                        updated_at TEXT,
                        FOREIGN KEY (tenant_id) REFERENCES platform_tenants(tenant_id) ON DELETE CASCADE
                    )
                """)

                # 3. Agent Versions (Snapshots para Rollback)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS platform_agent_versions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        agent_id TEXT NOT NULL,
                        tenant_id TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        manifest_json TEXT NOT NULL,
                        config_json TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'published',
                        created_at TEXT,
                        UNIQUE(agent_id, version),
                        FOREIGN KEY (agent_id) REFERENCES platform_agent_instances(agent_id) ON DELETE CASCADE
                    )
                """)

                # 4. Partitioned Knowledge Items
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS platform_agent_knowledge (
                        doc_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        agent_id TEXT NOT NULL DEFAULT '*',
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        source TEXT DEFAULT 'manual',
                        version INTEGER DEFAULT 1,
                        scope TEXT DEFAULT 'public',
                        priority INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'active',
                        metadata_json TEXT DEFAULT '{}',
                        created_at TEXT,
                        updated_at TEXT,
                        FOREIGN KEY (tenant_id) REFERENCES platform_tenants(tenant_id) ON DELETE CASCADE
                    )
                """)

                # 5. Integrations (Server-Side Isolated Credentials)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS platform_agent_integrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tenant_id TEXT NOT NULL,
                        integration_name TEXT NOT NULL,
                        is_connected INTEGER DEFAULT 0,
                        credentials_json TEXT DEFAULT '{}',
                        updated_at TEXT,
                        UNIQUE(tenant_id, integration_name),
                        FOREIGN KEY (tenant_id) REFERENCES platform_tenants(tenant_id) ON DELETE CASCADE
                    )
                """)

                # 6. Widget Sessions (Pinned to Tenant and Agent)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS platform_widget_sessions (
                        session_token TEXT PRIMARY KEY,
                        public_id TEXT NOT NULL,
                        tenant_id TEXT NOT NULL,
                        agent_id TEXT NOT NULL,
                        conversation_id TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        expires_at REAL NOT NULL,
                        last_seen_at REAL NOT NULL,
                        client_metadata_json TEXT DEFAULT '{}'
                    )
                """)

                # 7. Audit Events
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS platform_audit_events (
                        event_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        agent_id TEXT NOT NULL,
                        action TEXT NOT NULL,
                        actor TEXT NOT NULL,
                        details_json TEXT DEFAULT '{}',
                        timestamp TEXT
                    )
                """)

                # Índices de alto rendimiento para Scoping y Lookup
                cur.execute("CREATE INDEX IF NOT EXISTS idx_agents_tenant ON platform_agent_instances(tenant_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_agents_public_id ON platform_agent_instances(public_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_lookup ON platform_agent_knowledge(tenant_id, agent_id, status)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_versions_agent ON platform_agent_versions(agent_id, version)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_tenant ON platform_audit_events(tenant_id, agent_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON platform_widget_sessions(session_token)")

                conn.commit()
                log.info("[PlatformStore] Esquema multi-tenant inicializado correctamente.")
        except Exception as e:
            log.error(f"[PlatformStore] Error inicializando esquema multi-tenant: {e}", exc_info=True)

    # ─────────────────────────────────────────────────────────────────────────
    # TENANTS
    # ─────────────────────────────────────────────────────────────────────────

    def save_tenant(self, tenant: Tenant):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO platform_tenants (tenant_id, name, status, metadata_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(tenant_id) DO UPDATE SET
                    name = excluded.name,
                    status = excluded.status,
                    metadata_json = excluded.metadata_json,
                    updated_at = excluded.updated_at
            """, (
                tenant.tenant_id,
                tenant.name,
                tenant.status.value if isinstance(tenant.status, TenantStatus) else str(tenant.status),
                json.dumps(tenant.metadata, ensure_ascii=False),
                tenant.created_at,
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM platform_tenants WHERE tenant_id = ?", (tenant_id,))
            row = cur.fetchone()
            if row:
                return Tenant(
                    tenant_id=row["tenant_id"],
                    name=row["name"],
                    status=TenantStatus(row["status"]),
                    metadata=json.loads(row["metadata_json"] or "{}"),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
        return None

    def list_tenants(self) -> List[Tenant]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM platform_tenants ORDER BY created_at ASC")
            rows = cur.fetchall()
            return [
                Tenant(
                    tenant_id=r["tenant_id"],
                    name=r["name"],
                    status=TenantStatus(r["status"]),
                    metadata=json.loads(r["metadata_json"] or "{}"),
                    created_at=r["created_at"],
                    updated_at=r["updated_at"]
                ) for r in rows
            ]

    # ─────────────────────────────────────────────────────────────────────────
    # AGENT INSTANCES
    # ─────────────────────────────────────────────────────────────────────────

    def save_agent_instance(self, agent: AgentInstance):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO platform_agent_instances (
                    agent_id, tenant_id, name, status, runtime_version,
                    published_version, public_id, allowed_channels_json,
                    metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(agent_id) DO UPDATE SET
                    tenant_id = excluded.tenant_id,
                    name = excluded.name,
                    status = excluded.status,
                    runtime_version = excluded.runtime_version,
                    published_version = excluded.published_version,
                    public_id = excluded.public_id,
                    allowed_channels_json = excluded.allowed_channels_json,
                    metadata_json = excluded.metadata_json,
                    updated_at = excluded.updated_at
            """, (
                agent.agent_id,
                agent.tenant_id,
                agent.name,
                agent.status.value if isinstance(agent.status, AgentStatus) else str(agent.status),
                agent.runtime_version,
                agent.published_version,
                agent.public_id,
                json.dumps(agent.allowed_channels, ensure_ascii=False),
                json.dumps(agent.metadata, ensure_ascii=False),
                agent.created_at,
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()

    def get_agent_instance(self, tenant_id: str, agent_id: str) -> Optional[AgentInstance]:
        """Recupera un agente garantizando scoping estricto por tenant_id."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM platform_agent_instances WHERE tenant_id = ? AND agent_id = ?",
                (tenant_id, agent_id)
            )
            row = cur.fetchone()
            if row:
                return self._row_to_agent_instance(row)
        return None

    def get_agent_by_id(self, agent_id: str) -> Optional[AgentInstance]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM platform_agent_instances WHERE agent_id = ?", (agent_id,))
            row = cur.fetchone()
            if row:
                return self._row_to_agent_instance(row)
        return None

    def get_agent_by_public_id(self, public_id: str) -> Optional[AgentInstance]:
        """Resuelve una instancia pública para el widget embed."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM platform_agent_instances WHERE public_id = ?", (public_id,))
            row = cur.fetchone()
            if row:
                return self._row_to_agent_instance(row)
        return None

    def list_agents(self, tenant_id: str) -> List[AgentInstance]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM platform_agent_instances WHERE tenant_id = ? ORDER BY created_at ASC", (tenant_id,))
            rows = cur.fetchall()
            return [self._row_to_agent_instance(r) for r in rows]

    def _row_to_agent_instance(self, row: sqlite3.Row) -> AgentInstance:
        return AgentInstance(
            agent_id=row["agent_id"],
            tenant_id=row["tenant_id"],
            name=row["name"],
            status=AgentStatus(row["status"]),
            runtime_version=row["runtime_version"],
            published_version=row["published_version"],
            public_id=row["public_id"] or "",
            allowed_channels=json.loads(row["allowed_channels_json"] or '["web"]'),
            metadata=json.loads(row["metadata_json"] or "{}"),
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    # ─────────────────────────────────────────────────────────────────────────
    # AGENT VERSIONS & MANIFESTS (ROLLBACK ATÓMICO)
    # ─────────────────────────────────────────────────────────────────────────

    def save_agent_version(self, record: AgentVersionRecord) -> int:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO platform_agent_versions (
                    agent_id, tenant_id, version, manifest_json, config_json, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(agent_id, version) DO UPDATE SET
                    manifest_json = excluded.manifest_json,
                    config_json = excluded.config_json,
                    status = excluded.status
            """, (
                record.agent_id,
                record.tenant_id,
                record.version,
                json.dumps(record.manifest_dict, ensure_ascii=False),
                json.dumps(record.config_dict, ensure_ascii=False),
                record.status,
                record.created_at
            ))
            conn.commit()
            return cur.lastrowid or 0

    def get_agent_version(self, tenant_id: str, agent_id: str, version: int) -> Optional[AgentVersionRecord]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM platform_agent_versions
                WHERE tenant_id = ? AND agent_id = ? AND version = ?
            """, (tenant_id, agent_id, version))
            row = cur.fetchone()
            if row:
                return AgentVersionRecord(
                    id=row["id"],
                    agent_id=row["agent_id"],
                    tenant_id=row["tenant_id"],
                    version=row["version"],
                    manifest_dict=json.loads(row["manifest_json"]),
                    config_dict=json.loads(row["config_json"]),
                    status=row["status"],
                    created_at=row["created_at"]
                )
        return None

    def list_agent_versions(self, tenant_id: str, agent_id: str) -> List[AgentVersionRecord]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM platform_agent_versions
                WHERE tenant_id = ? AND agent_id = ?
                ORDER BY version DESC
            """, (tenant_id, agent_id))
            rows = cur.fetchall()
            return [
                AgentVersionRecord(
                    id=r["id"],
                    agent_id=r["agent_id"],
                    tenant_id=r["tenant_id"],
                    version=r["version"],
                    manifest_dict=json.loads(r["manifest_json"]),
                    config_dict=json.loads(r["config_json"]),
                    status=r["status"],
                    created_at=r["created_at"]
                ) for r in rows
            ]

    # ─────────────────────────────────────────────────────────────────────────
    # PARTITIONED KNOWLEDGE (TENANT & AGENT SCOPED)
    # ─────────────────────────────────────────────────────────────────────────

    def save_knowledge_item(self, item: KnowledgeItem):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO platform_agent_knowledge (
                    doc_id, tenant_id, agent_id, title, content, source,
                    version, scope, priority, status, metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(doc_id) DO UPDATE SET
                    title = excluded.title,
                    content = excluded.content,
                    version = excluded.version,
                    scope = excluded.scope,
                    priority = excluded.priority,
                    status = excluded.status,
                    metadata_json = excluded.metadata_json,
                    updated_at = excluded.updated_at
            """, (
                item.doc_id,
                item.tenant_id,
                item.agent_id,
                item.title,
                item.content,
                item.source,
                item.version,
                item.scope,
                item.priority,
                item.status,
                json.dumps(item.metadata, ensure_ascii=False),
                item.created_at,
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()

    def get_knowledge_items(
        self,
        tenant_id: str,
        agent_id: str = "*",
        scope: str = "public",
        status: str = "active"
    ) -> List[KnowledgeItem]:
        """
        Recupera el conocimientoScoped estrictamente por tenant_id.
        El agente A de Tenant 1 jamás puede recibir conocimiento de Tenant 2.
        """
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM platform_agent_knowledge
                WHERE tenant_id = ?
                  AND (agent_id = ? OR agent_id = '*')
                  AND (scope = ? OR scope = 'public')
                  AND status = ?
                ORDER BY priority DESC, created_at ASC
            """, (tenant_id, agent_id, scope, status))
            rows = cur.fetchall()
            return [
                KnowledgeItem(
                    doc_id=r["doc_id"],
                    tenant_id=r["tenant_id"],
                    agent_id=r["agent_id"],
                    title=r["title"],
                    content=r["content"],
                    source=r["source"],
                    version=r["version"],
                    scope=r["scope"],
                    priority=r["priority"],
                    status=r["status"],
                    metadata=json.loads(r["metadata_json"] or "{}"),
                    created_at=r["created_at"],
                    updated_at=r["updated_at"]
                ) for r in rows
            ]

    # ─────────────────────────────────────────────────────────────────────────
    # SERVER-SIDE INTEGRATIONS
    # ─────────────────────────────────────────────────────────────────────────

    def save_integration(
        self,
        tenant_id: str,
        integration_name: str,
        is_connected: bool,
        credentials: Dict[str, Any]
    ):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO platform_agent_integrations (
                    tenant_id, integration_name, is_connected, credentials_json, updated_at
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(tenant_id, integration_name) DO UPDATE SET
                    is_connected = excluded.is_connected,
                    credentials_json = excluded.credentials_json,
                    updated_at = excluded.updated_at
            """, (
                tenant_id,
                integration_name,
                1 if is_connected else 0,
                json.dumps(credentials, ensure_ascii=False),
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()

    def get_integration(self, tenant_id: str, integration_name: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM platform_agent_integrations
                WHERE tenant_id = ? AND integration_name = ?
            """, (tenant_id, integration_name))
            row = cur.fetchone()
            if row:
                return {
                    "tenant_id": row["tenant_id"],
                    "integration_name": row["integration_name"],
                    "is_connected": bool(row["is_connected"]),
                    "credentials": json.loads(row["credentials_json"] or "{}"),
                    "updated_at": row["updated_at"]
                }
        return None

    # ─────────────────────────────────────────────────────────────────────────
    # WIDGET SESSIONS (PINNED & EXPIRES)
    # ─────────────────────────────────────────────────────────────────────────

    def save_widget_session(self, session: WidgetSession):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO platform_widget_sessions (
                    session_token, public_id, tenant_id, agent_id,
                    conversation_id, created_at, expires_at, last_seen_at,
                    client_metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_token) DO UPDATE SET
                    last_seen_at = excluded.last_seen_at,
                    client_metadata_json = excluded.client_metadata_json
            """, (
                session.session_token,
                session.public_id,
                session.tenant_id,
                session.agent_id,
                session.conversation_id,
                session.created_at,
                session.expires_at,
                session.last_seen_at,
                json.dumps(session.client_metadata, ensure_ascii=False)
            ))
            conn.commit()

    def get_widget_session(self, session_token: str) -> Optional[WidgetSession]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM platform_widget_sessions WHERE session_token = ?", (session_token,))
            row = cur.fetchone()
            if row:
                sess = WidgetSession(
                    session_token=row["session_token"],
                    public_id=row["public_id"],
                    tenant_id=row["tenant_id"],
                    agent_id=row["agent_id"],
                    conversation_id=row["conversation_id"],
                    created_at=row["created_at"],
                    expires_at=row["expires_at"],
                    last_seen_at=row["last_seen_at"],
                    client_metadata=json.loads(row["client_metadata_json"] or "{}")
                )
                if not sess.is_expired():
                    return sess
        return None

    # ─────────────────────────────────────────────────────────────────────────
    # AUDIT TRAIL
    # ─────────────────────────────────────────────────────────────────────────

    def record_audit_event(
        self,
        tenant_id: str,
        agent_id: str,
        action: str,
        actor: str = "admin",
        details: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        import uuid
        event = AuditEvent(
            event_id=f"aud_{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            agent_id=agent_id,
            action=action,
            actor=actor,
            details=details or {}
        )
        self.save_audit_event(event)
        return event

    def save_audit_event(self, event: AuditEvent):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO platform_audit_events (
                    event_id, tenant_id, agent_id, action, actor, details_json, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.tenant_id,
                event.agent_id,
                event.action,
                event.actor,
                json.dumps(event.details, ensure_ascii=False),
                event.timestamp
            ))
            conn.commit()

    def get_audit_events(
        self,
        tenant_id: str,
        agent_id: Optional[str] = None,
        limit: int = 50
    ) -> List[AuditEvent]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            if agent_id:
                cur.execute("""
                    SELECT * FROM platform_audit_events
                    WHERE tenant_id = ? AND agent_id = ?
                    ORDER BY timestamp DESC LIMIT ?
                """, (tenant_id, agent_id, limit))
            else:
                cur.execute("""
                    SELECT * FROM platform_audit_events
                    WHERE tenant_id = ?
                    ORDER BY timestamp DESC LIMIT ?
                """, (tenant_id, limit))
            rows = cur.fetchall()
            return [
                AuditEvent(
                    event_id=r["event_id"],
                    tenant_id=r["tenant_id"],
                    agent_id=r["agent_id"],
                    action=r["action"],
                    actor=r["actor"],
                    details=json.loads(r["details_json"] or "{}"),
                    timestamp=r["timestamp"]
                ) for r in rows
            ]


platform_store = PlatformStore()
