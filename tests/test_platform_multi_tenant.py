# -*- coding: utf-8 -*-
"""
Test Suite: Firby Multi-Tenant Platform Architecture
====================================================
Valida exhaustivamente los requerimientos de Bloque 6:
1. TENANT ISOLATION: Aislamiento estricto entre organizaciones en backend y persistencia.
2. AGENT SCOPING: Instancias independientes compartiendo el mismo runtime.
3. KNOWLEDGE SCOPING: Recuperación de conocimiento estrictamente particionada.
4. MEMORY SCOPING: Memoria de trabajo y estado de tareas sin contaminación cruzada.
5. TOOL & PERMISSIONS: Distinción entre capacidad de plataforma, capacidad habilitada y precondiciones.
6. VERSIONING & ROLLBACK: Snapshot inmutable, manifiestos auditables y rollback atómico.
7. WIDGET BOOTSTRAP & PINNING: Identificador público seguro, sin secretos, sesión vinculada anti-suplantación.
8. SAME RUNTIME PATH: Demo y clientes utilizan exactamente las mismas capas del runtime.
"""

import pytest
import asyncio
from typing import Dict, Any

from src.core.platform.models import (
    Tenant, TenantStatus, AgentInstance, AgentStatus, AgentManifest
)
from src.core.platform.store import platform_store
from src.core.platform.manager import control_plane
from src.core.platform.knowledge import tenant_knowledge_engine
from src.core.platform.capabilities import capability_engine, CapabilityEngine, PermissionLevel
from src.core.platform.session import widget_session_manager
from src.core.platform.bootstrap import public_bootstrap_service
from src.core.platform.migration import resolve_tenant_agent_pair
from src.core.operator.memory import operator_memory, TaskState
from src.core.operator.runtime import operator_runtime
from src.core.operator.business_config import (
    BusinessConfig, BusinessIdentity, OfficialInfo, BusinessPolicy,
    ToolPermission, ConnectedIntegrations
)


def test_tenant_creation_and_scoping():
    """Valida la creación de Tenants y su scoping server-side."""
    t_a = control_plane.create_tenant("tenant_alpha", "Organización Alpha")
    t_b = control_plane.create_tenant("tenant_beta", "Organización Beta")

    assert t_a.tenant_id == "tenant_alpha"
    assert t_b.tenant_id == "tenant_beta"

    retrieved_a = control_plane.get_tenant("tenant_alpha")
    assert retrieved_a is not None
    assert retrieved_a.name == "Organización Alpha"

    # Verificar que los agentes de A no aparezcan en B
    control_plane.create_agent("tenant_alpha", "agent_a1", "Agente Alpha 1")
    control_plane.create_agent("tenant_beta", "agent_b1", "Agente Beta 1")

    agents_a = control_plane.list_agents("tenant_alpha")
    agents_b = control_plane.list_agents("tenant_beta")

    assert len(agents_a) == 1
    assert agents_a[0].agent_id == "agent_a1"

    assert len(agents_b) == 1
    assert agents_b[0].agent_id == "agent_b1"

    # Aislamiento: B no puede recuperar el agente de A
    assert platform_store.get_agent_instance("tenant_beta", "agent_a1") is None


def test_knowledge_scoping_and_isolation():
    """Demuestra que Tenant A NUNCA puede recuperar conocimiento de Tenant B."""
    tenant_knowledge_engine.add_document(
        tenant_id="tenant_alpha",
        agent_id="agent_a1",
        title="Protocolo Alpha",
        content="Contenido confidencial de Alpha sobre precios preferenciales.",
        scope="public",
        priority=10
    )

    tenant_knowledge_engine.add_document(
        tenant_id="tenant_beta",
        agent_id="agent_b1",
        title="Tratamiento Odontológico Beta",
        content="Procedimiento clínico de Beta con tecnología láser 3D.",
        scope="public",
        priority=10
    )

    # Consulta desde Tenant Alpha
    results_alpha = tenant_knowledge_engine.query_knowledge(
        tenant_id="tenant_alpha",
        agent_id="agent_a1",
        query_text="precios protocolo"
    )
    assert len(results_alpha) >= 1
    assert any("Alpha" in r.title for r in results_alpha)
    assert not any("Beta" in r.title for r in results_alpha)
    assert not any("láser" in r.content for r in results_alpha)

    # Consulta desde Tenant Beta
    results_beta = tenant_knowledge_engine.query_knowledge(
        tenant_id="tenant_beta",
        agent_id="agent_b1",
        query_text="láser tratamiento"
    )
    assert len(results_beta) >= 1
    assert any("Beta" in r.title for r in results_beta)
    assert not any("Alpha" in r.title for r in results_beta)
    assert not any("precios preferenciales" in r.content for r in results_beta)


def test_memory_scoping_and_isolation():
    """Valida que dos conversaciones con el mismo session_id en diferentes tenants no se contaminen."""
    shared_session_id = "test_user_shared_123"

    state_alpha = TaskState(task_id="task_alpha")
    state_alpha.set_focus_entity("plan", "plan_enterprise", "Plan Enterprise Alpha")
    operator_memory.save_task_state(shared_session_id, "tenant_alpha", state_alpha, agent_id="agent_a1")

    state_beta = TaskState(task_id="task_beta")
    state_beta.set_focus_entity("service", "implante_dental", "Implante Titanio Beta")
    operator_memory.save_task_state(shared_session_id, "tenant_beta", state_beta, agent_id="agent_b1")

    # Recuperación con scoping
    loaded_alpha = operator_memory.load_task_state(shared_session_id, tenant_id="tenant_alpha", agent_id="agent_a1")
    loaded_beta = operator_memory.load_task_state(shared_session_id, tenant_id="tenant_beta", agent_id="agent_b1")

    assert loaded_alpha.focus_entity["id"] == "plan_enterprise"
    assert loaded_beta.focus_entity["id"] == "implante_dental"
    assert loaded_alpha.task_id == "task_alpha"
    assert loaded_beta.task_id == "task_beta"


def test_capabilities_enabled_vs_preconditions():
    """Valida la diferencia entre capacidad de plataforma, habilitación y precondiciones."""
    # Configuración donde book_appointment está habilitado pero Google Calendar no está conectado
    unconnected_config = BusinessConfig(
        tenant_id="tenant_test_calendar",
        identity=BusinessIdentity(
            name="Negocio Prueba", legal_name="Negocio", industry="Tech",
            description="Test", website_url="https://test.com"
        ),
        official_info=OfficialInfo(),
        connected_integrations=ConnectedIntegrations(google_calendar=False),
        tool_permissions={
            "book_appointment": ToolPermission(name="book_appointment", enabled=True)
        }
    )

    # Aunque esté habilitada en tool_permissions, falla por precondición de infraestructura
    eval_unconnected = CapabilityEngine.evaluate_capability(unconnected_config, "book_appointment")
    assert eval_unconnected.authorized is False
    assert "Google Calendar" in eval_unconnected.reason

    # Cuando la integración se activa, la herramienta queda autorizada
    unconnected_config.connected_integrations.google_calendar = True
    eval_connected = CapabilityEngine.evaluate_capability(unconnected_config, "book_appointment")
    assert eval_connected.authorized is True
    assert eval_connected.permission_level == PermissionLevel.WRITE


def test_publish_validation_and_atomic_rollback():
    """Valida el ciclo DRAFT -> VALIDATING -> PUBLISHED y el Rollback a versión previa."""
    t_id = "tenant_version_test"
    a_id = "agent_version_test"

    control_plane.create_tenant(t_id, "Versioned Org")
    agent = control_plane.create_agent(t_id, a_id, "Versioned Agent")

    # 1. Configuración v1
    config_v1 = BusinessConfig(
        tenant_id=t_id,
        identity=BusinessIdentity(
            name="Negocio Version 1", legal_name="Negocio V1", industry="Consultoria",
            description="Consultoria v1", website_url="https://v1.com"
        ),
        official_info=OfficialInfo(operating_hours="9am a 5pm"),
        tool_permissions={"navigate_web": ToolPermission(name="navigate_web", enabled=True)}
    )
    control_plane.save_agent_config(t_id, a_id, config_v1)

    # Publicar v1
    manifest_v1 = control_plane.publish_agent(t_id, a_id, published_by="admin_test")
    assert manifest_v1.version == 1
    assert manifest_v1.checksum != ""

    agent_ref = control_plane.get_agent(t_id, a_id)
    assert agent_ref.status == AgentStatus.PUBLISHED
    assert agent_ref.published_version == 1

    # 2. Configuración v2 (actualizar nombre)
    config_v2 = BusinessConfig(
        tenant_id=t_id,
        identity=BusinessIdentity(
            name="Negocio Version 2 Renombrado", legal_name="Negocio V2", industry="Consultoria",
            description="Consultoria v2 mejorada", website_url="https://v2.com"
        ),
        official_info=OfficialInfo(operating_hours="8am a 8pm"),
        tool_permissions={"navigate_web": ToolPermission(name="navigate_web", enabled=True)}
    )
    control_plane.save_agent_config(t_id, a_id, config_v2)

    # Publicar v2
    manifest_v2 = control_plane.publish_agent(t_id, a_id, published_by="admin_test")
    assert manifest_v2.version == 2

    active_cfg = control_plane.get_active_config(t_id, a_id)
    assert active_cfg.identity.name == "Negocio Version 2 Renombrado"

    # 3. ROLLBACK atómico a v1
    manifest_restored = control_plane.rollback_agent(t_id, a_id, target_version=1, actor="security_admin")
    assert manifest_restored.version == 1

    # Verificar que la configuración activa ahora sea de nuevo la v1
    restored_cfg = control_plane.get_active_config(t_id, a_id)
    assert restored_cfg.identity.name == "Negocio Version 1"

    # Verificar auditoría
    audit_events = control_plane.get_audit_log(t_id, a_id)
    actions = [e.action for e in audit_events]
    assert "agent_published" in actions
    assert "agent_rollback" in actions


def test_widget_bootstrap_and_session_pinning():
    """Valida que el bootstrap público no exponga secretos y vincule la sesión al tenant."""
    bootstrap_res = public_bootstrap_service.bootstrap_agent("agt_firby_demo")

    assert bootstrap_res["ok"] is True
    assert bootstrap_res["agent"]["public_id"] == "agt_firby_demo"
    assert "branding" in bootstrap_res
    assert "welcome" in bootstrap_res

    # Verificación de Seguridad: Cero secretos en la respuesta pública
    json_str = str(bootstrap_res).lower()
    for forbidden in ["api_key", "password", "secret", "gemini_key", "bearer"]:
        assert forbidden not in json_str

    # Verificación de Tenant Pinning (Anti-Spoofing)
    token = bootstrap_res["session"]["session_token"]
    assert token.startswith("fws_")

    # Si un atacante intenta usar ese session_token pasando otro tenant_id
    validated_token, bound_tenant, bound_agent, conv_id = widget_session_manager.validate_and_bind(
        session_token=token,
        public_id="agt_malicious_override",
        fallback_tenant_id="tenant_malicious"
    )

    # El servidor ignora el tenant malicioso y fuerza el tenant vinculado en la base de datos
    assert bound_tenant == "tenant_demo"
    assert bound_agent == "agent_firby_demo"


def test_same_runtime_code_path():
    """Demuestra que el demo agent y un agente de cliente utilizan exactamente el mismo runtime."""
    async def _run():
        # 1. Turno de Demo Agent
        res_demo = await operator_runtime.process_turn(
            message="Quiero conocer los planes",
            user_id="user_test_runtime_1",
            org_id="tenant_demo",
            agent_id="agent_firby_demo"
        )
        assert res_demo.ok is True
        assert any("Starter" in b for b in res_demo.bubbles)

        # 2. Turno de Clínica Agent
        res_clinica = await operator_runtime.process_turn(
            message="¿Qué servicios prestan?",
            user_id="user_test_runtime_2",
            org_id="tenant_clinica",
            agent_id="agent_clinica"
        )
        assert res_clinica.ok is True
        # La clínica responde con sus servicios odontológicos, no con los planes de Firby
        assert not any("Starter" in b for b in res_clinica.bubbles)

    asyncio.run(_run())


def test_two_simulated_tenants_full_isolation():
    """
    Test Requerimiento 32: Dos tenants simulados (tenant_demo vs tenant_test).
    Demuestra fehacientemente que tenant_demo NO puede acceder a:
    - knowledge de tenant_test
    - memory de tenant_test
    - conversation de tenant_test
    - tools configuradas para tenant_test
    - integrations de tenant_test
    """
    # 1. Configuración de tenant_test (Negocio Restaurante Gourmet)
    t_test = control_plane.create_tenant("tenant_test", "Restaurante Gourmet Test")
    a_test = control_plane.create_agent("tenant_test", "agent_test", "Hostess Virtual Gourmet", public_id="agt_resto_test")

    cfg_test = BusinessConfig(
        tenant_id="tenant_test",
        identity=BusinessIdentity(
            name="Restaurante Cava & Fuego",
            legal_name="Gastronomía Cava S.A.S.",
            industry="Gastronomía y Restauración",
            description="Restaurante de autor con menú degustación y cata de vinos.",
            website_url="https://cavafuego.com"
        ),
        official_info=OfficialInfo(
            operating_hours="Martes a Sábado 12:00 PM a 11:00 PM",
            locations=["Zona Rosa, Medellín"]
        ),
        connected_integrations=ConnectedIntegrations(
            google_calendar=True,
            crm_system=True,
            whatsapp_owner=True
        ),
        tool_permissions={
            "book_appointment": ToolPermission(name="book_appointment", enabled=True),
            "check_availability": ToolPermission(name="check_availability", enabled=True),
            "navigate_web": ToolPermission(name="navigate_web", enabled=True)
        }
    )
    control_plane.save_agent_config("tenant_test", "agent_test", cfg_test)

    # Integración privada de tenant_test
    platform_store.save_integration("tenant_test", "table_reservation_engine", True, {"api_key": "resto_secret_9988"})

    # Knowledge exclusivo de tenant_test
    tenant_knowledge_engine.add_document(
        tenant_id="tenant_test",
        agent_id="agent_test",
        title="Menú Degustación 7 Tiempos",
        content="Menú exclusivo con maridaje de vino tinto y postre de chocolate amargo.",
        priority=10
    )

    # 2. Verificación de Aislamiento de Conocimiento
    kb_demo_search = tenant_knowledge_engine.query_knowledge("tenant_demo", "agent_firby_demo", "maridaje menú degustación")
    assert len(kb_demo_search) == 0, "tenant_demo NO debe ver el menú ni maridaje de tenant_test"

    kb_test_search = tenant_knowledge_engine.query_knowledge("tenant_test", "agent_test", "Starter Pro mensualidad")
    assert len(kb_test_search) == 0, "tenant_test NO debe ver los planes comerciales de tenant_demo"

    # 3. Verificación de Aislamiento de Memoria
    session_common = "shared_visitor_session_999"
    state_test = TaskState(task_id="task_reserva_mesa")
    state_test.slots["mesa"] = "Mesa 4 terraza para 2 personas"
    operator_memory.save_task_state(session_common, "tenant_test", state_test, agent_id="agent_test")

    demo_loaded_state = operator_memory.load_task_state(session_common, tenant_id="tenant_demo", agent_id="agent_firby_demo")
    assert "mesa" not in demo_loaded_state.slots, "tenant_demo no puede acceder a los slots de reserva de tenant_test"

    test_loaded_state = operator_memory.load_task_state(session_common, tenant_id="tenant_test", agent_id="agent_test")
    assert test_loaded_state.slots.get("mesa") == "Mesa 4 terraza para 2 personas"

    # 4. Verificación de Aislamiento de Tools y Precondiciones
    cfg_demo = control_plane.get_active_config("tenant_demo", "agent_firby_demo")
    eval_demo_book = CapabilityEngine.evaluate_capability(cfg_demo, "book_appointment")
    assert eval_demo_book.authorized is False, "En demo el agendamiento debe estar deshabilitado"

    eval_test_book = CapabilityEngine.evaluate_capability(cfg_test, "book_appointment")
    assert eval_test_book.authorized is True, "En tenant_test el agendamiento debe estar autorizado con Calendar conectado"

    # 5. Verificación de Aislamiento de Integraciones
    int_demo = platform_store.get_integration("tenant_demo", "table_reservation_engine")
    assert int_demo is None, "tenant_demo no tiene acceso a la integración table_reservation_engine de tenant_test"

    int_test = platform_store.get_integration("tenant_test", "table_reservation_engine")
    assert int_test is not None
    assert int_test["credentials"]["api_key"] == "resto_secret_9988"


def test_installation_sdk_file_exists():
    """Test Requerimiento 33: Valida que exista el SDK firby.js y el embed-test.html."""
    from pathlib import Path
    sdk_path = Path("/home/ubuntu/firby/src/interfaces/web/static/firby.js")
    html_path = Path("/home/ubuntu/firby/src/interfaces/web/static/embed-test.html")

    assert sdk_path.exists() is True
    assert html_path.exists() is True

    sdk_content = sdk_path.read_text(encoding="utf-8")
    assert "Firby.init" in sdk_content
    assert "/public/agents/" in sdk_content
    assert "bootstrap" in sdk_content

    html_content = html_path.read_text(encoding="utf-8")
    assert '<script src="/firby.js"></script>' in html_content
    assert 'Firby.init' in html_content

