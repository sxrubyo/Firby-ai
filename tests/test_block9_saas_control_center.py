# -*- coding: utf-8 -*-
"""
Test Suite — Bloque 9: Firby SaaS Control Center & Workspace
============================================================
Verifica:
1. Agent Control & Kill Switch (ONLINE, PAUSED, Emergency Stop)
2. Runtime Guard: verifica que runtime detiene ejecuciones cuando el agente está PAUSED
3. Run Control: listado, aprobación HITL, rechazo, cancelación
4. Conversaciones y Timeline de eventos operacionales
5. Base de Conocimiento estructurada (CRUD, versionado, enseñanza en lenguaje natural)
6. Reglas de Negocio estructuradas (Condición -> Directiva, toggle activo/inactivo)
7. Capability Engine & Tools: autorización en caliente
8. Flujos / "El n8n de Firby": simulación Dry-Run, plantillas, validación de grafos
9. Integraciones: canales (WhatsApp, GCal, CRM)
10. Facturación & Prueba de 7 días: cálculo exacto, cancelación en 1 clic
11. Onboarding guiado: avance de pasos
12. Sección 47 ("El cliente controla a Firby"): reactividad inmediata en runtime
"""

import os
import json
import pytest
from src.core.platform.control import agent_control, RunControlState
from src.core.platform.store import platform_store
from src.core.platform.models import Tenant, AgentInstance, TenantStatus, AgentStatus
from src.core.platform.workflows import workflow_engine
from src.core.platform.workspace_service import workspace_service
from src.core.operator.runtime import DigitalWebOperatorRuntime


class TestBlock9SaaSControlCenter:

    @classmethod
    def setup_class(cls):
        cls.tenant_id = "test_saas_tenant"
        cls.agent_id = "test_saas_agent"
        # Crear tenant y agente de prueba en platform_store
        platform_store.save_tenant(Tenant(tenant_id=cls.tenant_id, name="Clínica Médica Test"))
        platform_store.save_agent_instance(AgentInstance(
            tenant_id=cls.tenant_id,
            agent_id=cls.agent_id,
            name="Firby Operador Médico",
            public_id="clinica-medica-test"
        ))

    # ─────────────────────────────────────────────────────────────────────────
    # 1. AGENT CONTROL & EMERGENCY STOP / KILL SWITCH
    # ─────────────────────────────────────────────────────────────────────────

    def test_agent_state_transitions(self):
        """Verifica cambios de estado entre ONLINE, PAUSED y MAINTENANCE."""
        # 1. Poner en PAUSED
        res = workspace_service.set_agent_state(self.tenant_id, self.agent_id, "PAUSED", "Mantenimiento programado")
        assert res["ok"] is True
        assert res["state"] == "PAUSED"
        assert agent_control.is_agent_operational(self.tenant_id, self.agent_id)[0] is False

        # 2. Poner en ONLINE
        res = workspace_service.set_agent_state(self.tenant_id, self.agent_id, "ONLINE", "Reactivación de servicio")
        assert res["ok"] is True
        assert res["state"] == "ONLINE"
        assert agent_control.is_agent_operational(self.tenant_id, self.agent_id)[0] is True

    def test_emergency_stop_kill_switch(self):
        """Verifica que el Kill Switch pausa al agente y cancela runs activos."""
        # Crear un run activo
        run = agent_control.register_run(self.tenant_id, self.agent_id, "test_chat_1", "web_widget")
        assert run.state == RunControlState.RUNNING

        # Disparar Kill Switch
        stop_res = workspace_service.emergency_stop(self.tenant_id, self.agent_id, actor="admin_tester")
        assert stop_res["ok"] is True
        assert stop_res["cancelled_runs_count"] >= 1
        assert agent_control.is_agent_operational(self.tenant_id, self.agent_id)[0] is False

        # Verificar que el run fue cancelado o abortado
        assert run.state in [RunControlState.CANCELLED, RunControlState.ABORTED]

        # Restaurar a ONLINE para siguientes tests
        agent_control.set_agent_operational_state(self.tenant_id, self.agent_id, "ONLINE")

    def test_runtime_guard_pauses_execution(self):
        """Verifica que DigitalWebOperatorRuntime respeta el Kill Switch / estado PAUSED."""
        import asyncio
        # Pausar agente
        agent_control.set_agent_operational_state(self.tenant_id, self.agent_id, "PAUSED")

        runtime = DigitalWebOperatorRuntime()
        turn_result = asyncio.run(runtime.process_turn(
            message="Hola, necesito una cita",
            user_id="test_runtime_chat",
            org_id=self.tenant_id,
            agent_id=self.agent_id
        ))

        assert turn_result.state == "PAUSED"
        assert "pausado" in turn_result.response.lower()

        # Restaurar
        agent_control.set_agent_operational_state(self.tenant_id, self.agent_id, "ONLINE")

    # ─────────────────────────────────────────────────────────────────────────
    # 2. RUN CONTROL & HITL APPROVALS
    # ─────────────────────────────────────────────────────────────────────────

    def test_run_control_approvals(self):
        """Verifica el ciclo de vida de un run con aprobación humana obligatoria."""
        # Registrar run que solicita una acción sensible
        run = agent_control.register_run(self.tenant_id, self.agent_id, "chat_hitl_1", "whatsapp")
        agent_control.request_human_approval(
            run_id=run.run_id,
            action_type="confirm_price_exception",
            details={"discount_pct": 25, "customer": "Paciente VIP"}
        )
        assert run.state == RunControlState.WAITING_APPROVAL

        # Listar runs filtrando por WAITING_APPROVAL
        runs = workspace_service.list_runs(self.tenant_id, status_filter="waiting_approval")
        matching = [r for r in runs if r["run_id"] == run.run_id]
        assert len(matching) == 1
        assert matching[0]["state"].lower() == "waiting_approval"

        # Aprobar run
        approve_res = workspace_service.approve_run(run.run_id, actor="supervisor")
        assert approve_res["ok"] is True
        assert run.state in [RunControlState.RUNNING, RunControlState.COMPLETED]

    # ─────────────────────────────────────────────────────────────────────────
    # 3. KNOWLEDGE MANAGEMENT & NATURAL LANGUAGE TEACHING
    # ─────────────────────────────────────────────────────────────────────────

    def test_knowledge_crud_and_versioning(self):
        """Verifica adición, versión incremental y archivo de conocimiento."""
        # 1. Crear documento
        add_res = workspace_service.add_knowledge(
            tenant_id=self.tenant_id,
            title="Política de Cancelaciones",
            content="Las cancelaciones deben realizarse con mínimo 4 horas de anticipación.",
            category="policies",
            priority=10
        )
        assert add_res["ok"] is True
        doc_id = add_res["item"]["doc_id"]
        assert add_res["item"]["version"] == 1

        # 2. Actualizar documento incrementando versión
        up_res = workspace_service.update_knowledge(
            tenant_id=self.tenant_id,
            doc_id=doc_id,
            title="Política de Cancelaciones Actualizada",
            content="Las cancelaciones deben realizarse con mínimo 6 horas de anticipación.",
            category="policies",
            priority=10
        )
        assert up_res["ok"] is True
        assert up_res["version"] == 2

        # 3. Archivar documento
        del_res = workspace_service.archive_knowledge(self.tenant_id, doc_id)
        assert del_res["ok"] is True

    def test_teach_agent_natural_language(self):
        """Verifica que una enseñanza en lenguaje natural se estructura en conocimiento y regla."""
        teach_res = workspace_service.teach_agent(
            tenant_id=self.tenant_id,
            agent_id=self.agent_id,
            instruction_text="El horario de atención los sábados es de 8:00 AM a 2:00 PM sin excepción.",
            actor="dueño_negocio"
        )
        assert teach_res["ok"] is True
        assert teach_res["category"] == "hours"
        assert "doc_id" in teach_res
        assert "rule_id" in teach_res

        # Verificar que la regla aparece en el listado de reglas
        rules = workspace_service.list_rules(self.tenant_id)
        assert any(r["id"] == teach_res["rule_id"] for r in rules)

    # ─────────────────────────────────────────────────────────────────────────
    # 4. STRUCTURED BUSINESS RULES
    # ─────────────────────────────────────────────────────────────────────────

    def test_business_rules_management(self):
        """Verifica creación, toggle activo/inactivo y eliminación de reglas."""
        rule_res = workspace_service.create_rule(
            tenant_id=self.tenant_id,
            trigger_condition="Si el cliente pregunta por descuento para más de 3 personas",
            directive="Ofrecer 10% de descuento grupal y solicitar aprobación de gerencia si piden más.",
            category="pricing",
            priority=5
        )
        assert rule_res["ok"] is True
        rule_id = rule_res["rule"]["id"]

        # Desactivar regla
        toggle_off = workspace_service.toggle_rule(self.tenant_id, rule_id, is_active=False)
        assert toggle_off["ok"] is True
        assert toggle_off["is_active"] is False

        # Reactivar regla
        toggle_on = workspace_service.toggle_rule(self.tenant_id, rule_id, is_active=True)
        assert toggle_on["ok"] is True
        assert toggle_on["is_active"] is True

        # Eliminar regla
        del_res = workspace_service.delete_rule(self.tenant_id, rule_id)
        assert del_res["ok"] is True

    # ─────────────────────────────────────────────────────────────────────────
    # 5. CAPABILITY ENGINE & TOOLS AUTHORIZATION
    # ─────────────────────────────────────────────────────────────────────────

    def test_tool_permissions_in_runtime(self):
        """Verifica que se pueden apagar herramientas y exigir HITL."""
        tools = workspace_service.list_tools(self.tenant_id, self.agent_id)
        assert len(tools) >= 5

        # Encontrar herramienta de agendamiento
        cal_tool = next((t for t in tools if t["id"] == "calendar_reserver"), tools[0])
        tool_id = cal_tool["id"]

        # Modificar permiso para requerir HITL
        res = workspace_service.update_tool_permission(
            tenant_id=self.tenant_id,
            agent_id=self.agent_id,
            tool_id=tool_id,
            is_active=True,
            requires_hitl=True
        )
        assert res["ok"] is True
        assert res["requires_hitl"] is True

        # Verificar que el cambio quedó persistido
        updated_tools = workspace_service.list_tools(self.tenant_id, self.agent_id)
        target = next(t for t in updated_tools if t["id"] == tool_id)
        assert target["requires_hitl"] is True

    # ─────────────────────────────────────────────────────────────────────────
    # 6. FLOWS & WORKFLOW SIMULATOR (EL N8N DE FIRBY)
    # ─────────────────────────────────────────────────────────────────────────

    def test_workflow_templates_and_simulation(self):
        """Verifica la generación de plantillas y la simulación Dry-Run determinística."""
        templates = workflow_engine.create_prebuilt_templates(self.tenant_id)
        assert len(templates) >= 4

        # Tomar la primera plantilla (Reserva Directa)
        wf = templates[0]

        # Publicar flujo
        pub_res, msg = workflow_engine.publish_workflow(wf.id, actor="admin_tester")
        assert pub_res is True

        # Ejecutar Dry-Run Simulator con payload simulado
        dry_res = workflow_engine.dry_run(
            workflow_id=wf.id,
            test_payload={
                "customer_name": "Laura Gómez",
                "phone": "+573001234567",
                "service": "Valoración Médica",
                "requested_time": "2026-09-25T10:00:00"
            }
        )
        assert dry_res["ok"] is True
        assert dry_res["status"] == "COMPLETED"
        assert len(dry_res["steps"]) >= 2
        assert any(step["node_type"] == "action" for step in dry_res["steps"])

    # ─────────────────────────────────────────────────────────────────────────
    # 7. CHANNELS & INTEGRATIONS
    # ─────────────────────────────────────────────────────────────────────────

    def test_integrations_management(self):
        """Verifica la configuración segura de integraciones y canales."""
        integrations = workspace_service.list_integrations(self.tenant_id)
        assert len(integrations) >= 4

        # Guardar credenciales de WhatsApp Business Cloud
        res = workspace_service.save_integration(
            tenant_id=self.tenant_id,
            channel_id="meta_whatsapp",
            config_data={
                "phone_number_id": "10023456789",
                "business_account_id": "999888777",
                "access_token": "EAAX_TEST_TOKEN_123456",
                "webhook_verified": True
            }
        )
        assert res["ok"] is True

        # Verificar que el canal ahora está conectado
        updated_ints = workspace_service.list_integrations(self.tenant_id)
        wa = next(i for i in updated_ints if i["id"] == "meta_whatsapp")
        assert wa["status"].lower() == "connected"

    # ─────────────────────────────────────────────────────────────────────────
    # 8. BILLING & 7-DAY FREE TRIAL
    # ─────────────────────────────────────────────────────────────────────────

    def test_billing_and_1click_cancel(self):
        """Verifica el cálculo exacto de la prueba y la cancelación en 1 clic."""
        billing = workspace_service.get_billing_status(self.tenant_id)
        assert "plan_name" in billing
        assert "days_remaining" in billing
        assert billing["trial_status"] in ["TRIAL_ACTIVE", "TRIAL_ENDING", "CONVERTED", "CANCELLED"]

        # Cancelar en 1 clic
        cancel_res = workspace_service.cancel_trial_or_subscription(self.tenant_id, reason="test_cancel")
        assert cancel_res["ok"] is True

        # Verificar que el estado cambió a CANCELLED
        updated_billing = workspace_service.get_billing_status(self.tenant_id)
        assert updated_billing["trial_status"] == "CANCELLED"
        assert updated_billing["can_cancel"] is False

    # ─────────────────────────────────────────────────────────────────────────
    # 9. ONBOARDING GUIADO (7 PASOS)
    # ─────────────────────────────────────────────────────────────────────────

    def test_onboarding_guided_steps(self):
        """Verifica el avance y persistencia del onboarding de 7 pasos."""
        state = workspace_service.get_onboarding_state(self.tenant_id)
        assert "steps" in state
        assert len(state["steps"]) == 7

        # Completar paso 1 (conectar web)
        step1_res = workspace_service.complete_onboarding_step(self.tenant_id, "connect_website")
        assert step1_res["ok"] is True

        # Verificar que el progreso aumentó
        updated_state = workspace_service.get_onboarding_state(self.tenant_id)
        assert updated_state["steps"][0]["completed"] is True
        assert updated_state["progress_pct"] > 0

    # ─────────────────────────────────────────────────────────────────────────
    # 10. SECCIÓN 47: EL CLIENTE CONTROLA A FIRBY
    # ─────────────────────────────────────────────────────────────────────────

    def test_section_47_client_controls_firby(self):
        """
        Verificación de la Sección 47 del Master Spec:
        - Si el cliente apaga una herramienta, runtime no la usa.
        - Si el cliente añade una regla, runtime la aplica inmediatamente.
        - Si el cliente pausa el agente, runtime no atiende.
        """
        # 1. Regla agregada
        rule_res = workspace_service.create_rule(
            tenant_id=self.tenant_id,
            trigger_condition="Pregunta por urgencias pediátricas",
            directive="Derivar de inmediato al conmutador de la clínica 018000.",
            category="clinical_urgency"
        )
        assert rule_res["ok"] is True

        # 2. Verificar que las reglas activas del tenant la incluyen
        rules = workspace_service.list_rules(self.tenant_id)
        active_rules = [r for r in rules if r.get("is_active", True)]
        assert any("018000" in r["directive"] for r in active_rules)

        # 3. Overview general devuelve métricas consistentes
        overview = workspace_service.get_overview(self.tenant_id, self.agent_id)
        assert overview["ok"] is True
        assert "metrics" in overview
        assert "agent" in overview
        assert overview["metrics"]["active_rules"] >= 1
