# -*- coding: utf-8 -*-
"""
Firby Platform — Multi-Tenant Multi-Agent Architecture
======================================================
"""

from src.core.platform.models import (
    Tenant, TenantStatus, AgentInstance, AgentStatus, AgentManifest,
    AgentVersionRecord, KnowledgeItem, AuditEvent, WidgetSession, ValidationResult
)
from src.core.platform.store import platform_store, PlatformStore
from src.core.platform.capabilities import capability_engine, CapabilityEngine, PLATFORM_CAPABILITIES_CATALOG
from src.core.platform.knowledge import tenant_knowledge_engine, TenantKnowledgeEngine
from src.core.platform.session import widget_session_manager, WidgetSessionManager
from src.core.platform.manager import control_plane, ControlPlaneManager
from src.core.platform.bootstrap import public_bootstrap_service, PublicBootstrapService
from src.core.platform.migration import resolve_tenant_agent_pair, run_platform_migrations
from src.core.platform.control import (
    agent_control, AgentControlSystem, RunControlState, CapabilityStatus,
    CalendarSandbox, CRMSandbox, WhatsAppSandbox
)
from src.core.platform.discovery import (
    onboarding_engine, self_inspector, ControlledSiteCrawler, CodebaseScanner
)

__all__ = [
    "Tenant",
    "TenantStatus",
    "AgentInstance",
    "AgentStatus",
    "AgentManifest",
    "AgentVersionRecord",
    "KnowledgeItem",
    "AuditEvent",
    "WidgetSession",
    "ValidationResult",
    "platform_store",
    "PlatformStore",
    "capability_engine",
    "CapabilityEngine",
    "PLATFORM_CAPABILITIES_CATALOG",
    "tenant_knowledge_engine",
    "TenantKnowledgeEngine",
    "widget_session_manager",
    "WidgetSessionManager",
    "control_plane",
    "ControlPlaneManager",
    "public_bootstrap_service",
    "PublicBootstrapService",
    "resolve_tenant_agent_pair",
    "run_platform_migrations",
    "agent_control",
    "AgentControlSystem",
    "RunControlState",
    "CapabilityStatus",
    "CalendarSandbox",
    "CRMSandbox",
    "WhatsAppSandbox",
    "onboarding_engine",
    "self_inspector",
    "ControlledSiteCrawler",
    "CodebaseScanner",
]
