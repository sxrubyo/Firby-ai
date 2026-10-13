# -*- coding: utf-8 -*-
"""
Firby Platform — Agent & Tenant Migration Engine
================================================
Migra el agente y configuraciones actuales de Firby a la arquitectura multi-tenant:
1. MIGRACIÓN DEL AGENTE DEMO DE FIRBY:
   tenant_id: 'tenant_demo'
   agent_id: 'agent_firby_demo'
   public_id: 'agt_firby_demo'
   published_version: 1
   -> Pasa de ser una excepción arquitectónica a ser un Tenant y Agente formal
      con su propio AgentManifest, historial de versiones y base de conocimiento.
2. MIGRACIÓN DE SEGUNDO TENANT (CLÍNICA ODONTOLÓGICA):
   tenant_id: 'tenant_clinica'
   agent_id: 'agent_clinica'
   public_id: 'agt_clinica_americas'
   published_version: 1
   -> Demuestra y verifica el aislamiento multi-tenant con Google Calendar habilitado.
3. MAPEO DE COMPATIBILIDAD HACIA ATRÁS:
   Permite que requests históricos con 'firby_landing' o 'firby-demo' se resuelvan
   de forma transparente a 'tenant_demo' / 'agent_firby_demo'.
"""

from __future__ import annotations
import logging
from typing import Dict, Any, Tuple

from src.core.platform.models import Tenant, TenantStatus, AgentInstance, AgentStatus, AgentManifest, AgentVersionRecord
from src.core.platform.store import platform_store, PlatformStore
from src.core.platform.manager import control_plane, ControlPlaneManager
from src.core.platform.knowledge import tenant_knowledge_engine
from src.core.operator.business_config import FIRBY_LANDING_CONFIG, CLINICA_AMERICAS_CONFIG

log = logging.getLogger("firby.platform.migration")

# Mapeos de compatibilidad hacia atrás
LEGACY_TENANT_ALIASES: Dict[str, Tuple[str, str]] = {
    "firby_landing": ("tenant_demo", "agent_firby_demo"),
    "firby_default": ("tenant_demo", "agent_firby_demo"),
    "firby": ("tenant_demo", "agent_firby_demo"),
    "demo": ("tenant_demo", "agent_firby_demo"),
    "base": ("tenant_demo", "agent_firby_demo"),
    "tenant_demo": ("tenant_demo", "agent_firby_demo"),
    "clinica-de-las-americas": ("tenant_clinica", "agent_clinica"),
    "clinica": ("tenant_clinica", "agent_clinica"),
    "tenant_clinica": ("tenant_clinica", "agent_clinica")
}


def resolve_tenant_agent_pair(raw_id: str) -> Tuple[str, str]:
    """Resuelve identificadores legacy o nuevos a la tupla canónica (tenant_id, agent_id)."""
    clean = (raw_id or "").strip().lower()
    if clean in LEGACY_TENANT_ALIASES:
        return LEGACY_TENANT_ALIASES[clean]
    if ":" in clean:
        parts = clean.split(":", 1)
        return parts[0].strip(), parts[1].strip()
    return clean or "tenant_demo", f"agent_{clean}" if clean else "agent_firby_demo"


def run_platform_migrations(store: Optional[PlatformStore] = None):
    """Ejecuta la migración y población de datos iniciales en SQLite."""
    if isinstance(store, str):
        st = PlatformStore(db_path=store)
    else:
        st = store or platform_store

    # ─────────────────────────────────────────────────────────────────────────
    # 1. TENANT DEMO (FIRBY AI OFICIAL)
    # ─────────────────────────────────────────────────────────────────────────
    demo_tenant = st.get_tenant("tenant_demo")
    if not demo_tenant:
        demo_tenant = Tenant(
            tenant_id="tenant_demo",
            name="Firby AI",
            status=TenantStatus.ACTIVE,
            metadata={"domain": "firbyai.com", "plan": "enterprise"}
        )
        st.save_tenant(demo_tenant)
        log.info("[Migration] Creado tenant_demo")

    demo_agent = st.get_agent_instance("tenant_demo", "agent_firby_demo")
    if not demo_agent:
        demo_agent = AgentInstance(
            agent_id="agent_firby_demo",
            tenant_id="tenant_demo",
            name="Firby Web Concierge",
            status=AgentStatus.PUBLISHED,
            runtime_version="1.0.0",
            published_version=1,
            public_id="agt_firby_demo",
            allowed_channels=["web", "whatsapp"],
            metadata={"description": "Operador oficial del sitio firbyai.com"}
        )
        st.save_agent_instance(demo_agent)

        # Guardar configuración y manifiesto inicial
        FIRBY_LANDING_CONFIG.tenant_id = "tenant_demo"
        FIRBY_LANDING_CONFIG.save_to_db(db_path=st.db_path)

        manifest = AgentManifest(
            agent_id="agent_firby_demo",
            tenant_id="tenant_demo",
            version=1,
            runtime_version="1.0.0",
            config_version=1,
            knowledge_version=1,
            toolset_version=1,
            policy_version=1,
            published_by="system_migration"
        )
        manifest.checksum = manifest.compute_checksum(FIRBY_LANDING_CONFIG.to_dict())

        ver_rec = AgentVersionRecord(
            agent_id="agent_firby_demo",
            tenant_id="tenant_demo",
            version=1,
            manifest_dict=manifest.to_dict(),
            config_dict=FIRBY_LANDING_CONFIG.to_dict(),
            status="published"
        )
        st.save_agent_version(ver_rec)

        # Indexar conocimiento oficial de Firby
        tenant_knowledge_engine.sync_business_config("tenant_demo", "agent_firby_demo", FIRBY_LANDING_CONFIG)
        log.info("[Migration] Agente agent_firby_demo migrado y publicado (v1).")

    # ─────────────────────────────────────────────────────────────────────────
    # 2. TENANT CLÍNICA (CLÍNICA DENTAL LAS AMÉRICAS)
    # ─────────────────────────────────────────────────────────────────────────
    clinica_tenant = st.get_tenant("tenant_clinica")
    if not clinica_tenant:
        clinica_tenant = Tenant(
            tenant_id="tenant_clinica",
            name="Clínica Dental Las Américas",
            status=TenantStatus.ACTIVE,
            metadata={"sector": "salud", "city": "Medellín"}
        )
        st.save_tenant(clinica_tenant)
        log.info("[Migration] Creado tenant_clinica")

    clinica_agent = st.get_agent_instance("tenant_clinica", "agent_clinica")
    if not clinica_agent:
        clinica_agent = AgentInstance(
            agent_id="agent_clinica",
            tenant_id="tenant_clinica",
            name="Recepcionista Dental Las Américas",
            status=AgentStatus.PUBLISHED,
            runtime_version="1.0.0",
            published_version=1,
            public_id="agt_clinica_americas",
            allowed_channels=["web", "whatsapp"],
            metadata={"description": "Operador clínico con agenda 3D activa"}
        )
        st.save_agent_instance(clinica_agent)

        CLINICA_AMERICAS_CONFIG.tenant_id = "tenant_clinica"
        CLINICA_AMERICAS_CONFIG.save_to_db(db_path=st.db_path)

        manifest_clinica = AgentManifest(
            agent_id="agent_clinica",
            tenant_id="tenant_clinica",
            version=1,
            runtime_version="1.0.0",
            config_version=1,
            knowledge_version=1,
            toolset_version=1,
            policy_version=1,
            published_by="system_migration"
        )
        manifest_clinica.checksum = manifest_clinica.compute_checksum(CLINICA_AMERICAS_CONFIG.to_dict())

        ver_rec_clinica = AgentVersionRecord(
            agent_id="agent_clinica",
            tenant_id="tenant_clinica",
            version=1,
            manifest_dict=manifest_clinica.to_dict(),
            config_dict=CLINICA_AMERICAS_CONFIG.to_dict(),
            status="published"
        )
        st.save_agent_version(ver_rec_clinica)

        tenant_knowledge_engine.sync_business_config("tenant_clinica", "agent_clinica", CLINICA_AMERICAS_CONFIG)
        log.info("[Migration] Agente agent_clinica migrado y publicado (v1).")


# Inicializar automáticamente al importar
try:
    run_platform_migrations()
except Exception as _e:
    log.warning(f"[Migration] Error ejecutando migraciones iniciales: {_e}")
