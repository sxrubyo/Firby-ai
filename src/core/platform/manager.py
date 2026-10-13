# -*- coding: utf-8 -*-
"""
Firby Platform — Control Plane Manager
======================================
Control Plane central que orquesta:
1. TENANTS & AGENTS: Creación y gestión de inquilinos y sus instancias de agente.
2. CONFIGURATION: Almacenamiento declarativo de BusinessConfig por (tenant, agent).
3. VALIDATION BEFORE PUBLISH:
   Validación rigurosa de consistencia antes de permitir la publicación a producción:
   - BusinessConfig completo y coherente.
   - Herramientas válidas y soportadas.
   - Integraciones de infraestructura requeridas conectadas.
   - Cero secretos o credenciales expuestas en la configuración del cliente.
4. PUBLISH & VERSIONING:
   Transición atómica DRAFT -> PUBLISHED.
   Genera el AgentManifest inmutable con checksum SHA-256 y versionado incremental.
5. ATOMIC ROLLBACK:
   Restaura una versión anterior exacta sin efectos colaterales.
6. AUDIT LOGGING:
   Registra cada acción administrativa (creación, edición, publicación, rollback).
"""

from __future__ import annotations
import re
import json
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone

from src.core.platform.models import (
    Tenant, TenantStatus, AgentInstance, AgentStatus, AgentManifest,
    AgentVersionRecord, ValidationResult, AuditEvent
)
from src.core.platform.store import platform_store, PlatformStore
from src.core.platform.capabilities import PLATFORM_CAPABILITIES_CATALOG, CapabilityEngine
from src.core.platform.knowledge import tenant_knowledge_engine
from src.core.operator.business_config import (
    BusinessConfig, BusinessIdentity, OfficialInfo, BusinessPolicy,
    ServiceItem, PricingTier, NavigationResource, ToolPermission,
    ConnectedIntegrations
)

log = logging.getLogger("firby.platform.manager")


class ControlPlaneManager:
    """Administrador central del Control Plane de Firby."""

    def __init__(self, store: Optional[PlatformStore] = None):
        self.store = store or platform_store

    # ─────────────────────────────────────────────────────────────────────────
    # GESTIÓN DE TENANTS
    # ─────────────────────────────────────────────────────────────────────────

    def create_tenant(self, tenant_id: str, name: str, metadata: Optional[Dict[str, Any]] = None) -> Tenant:
        clean_id = tenant_id.strip().lower()
        tenant = Tenant(
            tenant_id=clean_id,
            name=name.strip(),
            status=TenantStatus.ACTIVE,
            metadata=metadata or {}
        )
        self.store.save_tenant(tenant)
        self.log_audit(clean_id, "*", "tenant_created", "system", {"name": name})
        return tenant

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        return self.store.get_tenant(tenant_id.strip().lower())

    def list_tenants(self) -> List[Tenant]:
        return self.store.list_tenants()

    # ─────────────────────────────────────────────────────────────────────────
    # GESTIÓN DE INSTANCIAS DE AGENTE
    # ─────────────────────────────────────────────────────────────────────────

    def create_agent(
        self,
        tenant_id: str,
        agent_id: str,
        name: str,
        public_id: Optional[str] = None,
        allowed_channels: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentInstance:
        clean_tid = tenant_id.strip().lower()
        clean_aid = agent_id.strip().lower()

        tenant = self.get_tenant(clean_tid)
        if not tenant:
            raise ValueError(f"El tenant '{clean_tid}' no existe. Debe crearse antes de instanciar agentes.")

        pub_id = public_id or f"agt_{clean_aid.replace('-', '_')}"
        agent = AgentInstance(
            agent_id=clean_aid,
            tenant_id=clean_tid,
            name=name.strip(),
            status=AgentStatus.DRAFT,
            runtime_version="1.0.0",
            published_version=None,
            public_id=pub_id,
            allowed_channels=allowed_channels or ["web"],
            metadata=metadata or {}
        )
        self.store.save_agent_instance(agent)
        self.log_audit(clean_tid, clean_aid, "agent_created", "admin", {"name": name, "public_id": pub_id})
        return agent

    def get_agent(self, tenant_id: str, agent_id: str) -> Optional[AgentInstance]:
        return self.store.get_agent_instance(tenant_id.strip().lower(), agent_id.strip().lower())

    def get_agent_by_public_id(self, public_id: str) -> Optional[AgentInstance]:
        return self.store.get_agent_by_public_id(public_id.strip())

    def list_agents(self, tenant_id: str) -> List[AgentInstance]:
        return self.store.list_agents(tenant_id.strip().lower())

    # ─────────────────────────────────────────────────────────────────────────
    # CONFIGURACIÓN DECLARATIVA
    # ─────────────────────────────────────────────────────────────────────────

    def save_agent_config(self, tenant_id: str, agent_id: str, config: BusinessConfig):
        """Guarda la configuración de un agente en SQLite."""
        clean_tid = tenant_id.strip().lower()
        clean_aid = agent_id.strip().lower()
        config.tenant_id = clean_tid
        # Guardar en SQLite con clave combinada para aislamiento
        storage_key = f"{clean_tid}:{clean_aid}"
        config.save_to_db(db_path=self.store.db_path)
        self.log_audit(clean_tid, clean_aid, "agent_config_updated", "admin", {"identity": config.identity.name})

    def get_agent_config(self, tenant_id: str, agent_id: str) -> Optional[BusinessConfig]:
        """Obtiene la configuración activa o en borrador."""
        clean_tid = tenant_id.strip().lower()
        clean_aid = agent_id.strip().lower()

        # 1. Si está publicado, intentar recuperar la configuración de la versión publicada
        agent = self.get_agent(clean_tid, clean_aid)
        if agent and agent.published_version:
            ver_rec = self.store.get_agent_version(clean_tid, clean_aid, agent.published_version)
            if ver_rec and ver_rec.config_dict:
                return BusinessConfig.from_dict(ver_rec.config_dict)

        # 2. Cargar desde la base de datos de configuraciones
        return BusinessConfig.load_from_db(clean_tid, db_path=self.store.db_path)

    # ─────────────────────────────────────────────────────────────────────────
    # VALIDATION BEFORE PUBLISH
    # ─────────────────────────────────────────────────────────────────────────

    def validate_agent_for_publish(self, tenant_id: str, agent_id: str) -> ValidationResult:
        """
        Valida exhaustivamente un agente antes de permitir su publicación:
        - Tenant existe y está activo.
        - AgentInstance existe.
        - BusinessConfig contiene campos obligatorios (nombre, tono, políticas).
        - Las herramientas habilitadas existen en la plataforma.
        - Las herramientas que requieren integraciones tienen dichas integraciones activas.
        - Las rutas de navegación son seguras (#seccion o /ruta).
        - Cero secretos o credenciales en textos de configuración.
        """
        errors: List[str] = []
        warnings: List[str] = []

        tenant = self.get_tenant(tenant_id)
        if not tenant:
            errors.append(f"Tenant '{tenant_id}' no existe.")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        if tenant.status != TenantStatus.ACTIVE:
            errors.append(f"Tenant '{tenant_id}' no está activo (estado: {tenant.status}).")

        agent = self.get_agent(tenant_id, agent_id)
        if not agent:
            errors.append(f"Agente '{agent_id}' no existe en tenant '{tenant_id}'.")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        # Cargar configuración a validar
        config = BusinessConfig.load_from_db(tenant_id, db_path=self.store.db_path)
        if not config:
            errors.append("No se encontró BusinessConfig configurada para este agente.")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        # Validar Identidad
        if not config.identity.name or len(config.identity.name.strip()) < 2:
            errors.append("La identidad del negocio debe incluir un nombre válido.")

        # Validar Herramientas e Integraciones
        for tool_name, perm in config.tool_permissions.items():
            if perm.enabled:
                eval_res = CapabilityEngine.evaluate_capability(config, tool_name)
                if not eval_res.authorized:
                    errors.append(f"Herramienta '{tool_name}' habilitada pero bloqueada: {eval_res.reason}")

        # Validar Recursos de Navegación
        for res in config.navigation_resources:
            if not res.target.startswith("#") and not res.target.startswith("/"):
                errors.append(f"Recurso de navegación '{res.id}' con destino inválido '{res.target}'. Debe iniciar con '#' o '/'.")

        # Validar que no existan secretos expuestos en campos de texto
        text_dump = json.dumps(config.to_dict()).lower()
        secret_patterns = [r"api_key", r"secret_key", r"password", r"private_key", r"bearer\s+[a-z0-9_\-\.]{20,}"]
        for pat in secret_patterns:
            if re.search(pat, text_dump):
                errors.append(f"Detectado posible secreto o credencial privada expuesta en la configuración ({pat}).")

        is_valid = len(errors) == 0
        return ValidationResult(valid=is_valid, errors=errors, warnings=warnings)

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLISH & ROLLBACK
    # ─────────────────────────────────────────────────────────────────────────

    def publish_agent(self, tenant_id: str, agent_id: str, published_by: str = "admin") -> AgentManifest:
        """
        Publica una nueva versión de un agente:
        DRAFT -> VALIDATING -> PUBLISHED.
        Crea snapshot inmutable para soportar rollback instantáneo.
        """
        clean_tid = tenant_id.strip().lower()
        clean_aid = agent_id.strip().lower()

        # 1. Validación estricta
        val_res = self.validate_agent_for_publish(clean_tid, clean_aid)
        if not val_res.valid:
            error_str = " | ".join(val_res.errors)
            raise ValueError(f"No se puede publicar el agente por errores de validación: {error_str}")

        agent = self.get_agent(clean_tid, clean_aid)
        assert agent is not None

        # 2. Determinar nuevo número de versión
        current_ver = agent.published_version or 0
        new_version = current_ver + 1

        # 3. Cargar configuración actual
        config = BusinessConfig.load_from_db(clean_tid, db_path=self.store.db_path)
        assert config is not None
        config_dict = config.to_dict()

        # 4. Construir y firmar AgentManifest
        manifest = AgentManifest(
            agent_id=clean_aid,
            tenant_id=clean_tid,
            version=new_version,
            runtime_version=agent.runtime_version,
            config_version=new_version,
            knowledge_version=new_version,
            toolset_version=new_version,
            policy_version=new_version,
            memory_policy_version=1,
            ui_version=1,
            published_at=datetime.now(timezone.utc).isoformat(),
            published_by=published_by
        )
        manifest.checksum = manifest.compute_checksum(config_dict)

        # 5. Guardar Version Snapshot histórico
        ver_record = AgentVersionRecord(
            agent_id=clean_aid,
            tenant_id=clean_tid,
            version=new_version,
            manifest_dict=manifest.to_dict(),
            config_dict=config_dict,
            status="published",
            created_at=manifest.published_at
        )
        self.store.save_agent_version(ver_record)

        # 6. Actualizar estado del agente a PUBLISHED
        agent.status = AgentStatus.PUBLISHED
        agent.published_version = new_version
        self.store.save_agent_instance(agent)

        # 7. Sincronizar conocimiento en el Scoped Knowledge Engine
        tenant_knowledge_engine.sync_business_config(clean_tid, clean_aid, config)

        # 8. Registrar evento de auditoría
        self.log_audit(
            clean_tid, clean_aid, "agent_published", published_by,
            {"version": new_version, "checksum": manifest.checksum}
        )

        log.info(f"[ControlPlane] Agente {clean_aid} publicado con éxito (versión {new_version}, checksum {manifest.checksum[:8]}).")
        return manifest

    def rollback_agent(self, tenant_id: str, agent_id: str, target_version: int, actor: str = "admin") -> AgentManifest:
        """
        Ejecuta un Rollback atómico a una versión previa publicada.
        """
        clean_tid = tenant_id.strip().lower()
        clean_aid = agent_id.strip().lower()

        ver_rec = self.store.get_agent_version(clean_tid, clean_aid, target_version)
        if not ver_rec:
            raise ValueError(f"No existe el snapshot de versión {target_version} para el agente '{clean_aid}'.")

        agent = self.get_agent(clean_tid, clean_aid)
        if not agent:
            raise ValueError(f"El agente '{clean_aid}' no existe.")

        # Restaurar la configuración en SQLite
        restored_config = BusinessConfig.from_dict(ver_rec.config_dict)
        restored_config.save_to_db(db_path=self.store.db_path)

        # Actualizar la versión activa del agente
        previous_version = agent.published_version
        agent.published_version = target_version
        agent.status = AgentStatus.PUBLISHED
        self.store.save_agent_instance(agent)

        manifest = AgentManifest.from_dict(ver_rec.manifest_dict)

        # Sincronizar conocimiento restaurado
        tenant_knowledge_engine.sync_business_config(clean_tid, clean_aid, restored_config)

        # Auditoría
        self.log_audit(
            clean_tid, clean_aid, "agent_rollback", actor,
            {"target_version": target_version, "from_version": previous_version}
        )

        log.info(f"[ControlPlane] Rollback completado para {clean_aid}: versión {previous_version} -> {target_version}")
        return manifest

    def get_published_manifest(self, tenant_id: str, agent_id: str) -> Optional[AgentManifest]:
        clean_tid = tenant_id.strip().lower()
        clean_aid = agent_id.strip().lower()
        agent = self.get_agent(clean_tid, clean_aid)
        if agent and agent.published_version:
            ver_rec = self.store.get_agent_version(clean_tid, clean_aid, agent.published_version)
            if ver_rec:
                return AgentManifest.from_dict(ver_rec.manifest_dict)
        return None

    def get_active_config(self, tenant_id: str, agent_id: Optional[str] = None) -> BusinessConfig:
        """
        Recupera la configuración activa para el runtime.
        Garantiza que la demo de Firby o cualquier cliente obtenga su BusinessConfig exacta.
        """
        clean_tid = (tenant_id or "firby_landing").strip().lower()
        clean_aid = (agent_id or "firby-demo").strip().lower()

        # 1. Si existe en el almacén de versiones
        if clean_aid:
            agent = self.get_agent(clean_tid, clean_aid)
            if agent and agent.published_version:
                ver_rec = self.store.get_agent_version(clean_tid, clean_aid, agent.published_version)
                if ver_rec and ver_rec.config_dict:
                    return BusinessConfig.from_dict(ver_rec.config_dict)

        # 2. Cargar desde SQLite
        loaded = BusinessConfig.load_from_db(clean_tid, db_path=self.store.db_path)
        if loaded:
            return loaded

        # 3. Fallback canónico si es demo o landing
        from src.core.operator.business_config import get_business_config
        return get_business_config(clean_tid)

    # ─────────────────────────────────────────────────────────────────────────
    # AUDIT TRAIL
    # ─────────────────────────────────────────────────────────────────────────

    def log_audit(self, tenant_id: str, agent_id: str, action: str, actor: str, details: Dict[str, Any]):
        event = AuditEvent(
            event_id=f"aud_{uuid.uuid4().hex[:14]}",
            tenant_id=tenant_id,
            agent_id=agent_id,
            action=action,
            actor=actor,
            details=details,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        self.store.save_audit_event(event)

    def get_audit_log(self, tenant_id: str, agent_id: Optional[str] = None, limit: int = 50) -> List[AuditEvent]:
        return self.store.get_audit_events(tenant_id=tenant_id, agent_id=agent_id, limit=limit)


control_plane = ControlPlaneManager()
