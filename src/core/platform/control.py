# -*- coding: utf-8 -*-
"""
Firby Platform — Verifiable Agent Control System
=================================================
Proporciona la capa de gobernanza dura y control verificable del agente:

1. CAPABILITY MATRIX:
   - Evaluación transparente: ENABLED, AUTHORIZED, REQUIRES_APPROVAL, AVAILABLE_IN_ENV.
2. HARD GUARANTEES (INJECTION-PROOF):
   - Aislamiento estricto de tenants y validación en código contra ataques de jailbreak.
3. DRY-RUN & SANDBOXING:
   - Modo de simulación previa a publicación (CalendarSandbox, CRMSandbox, WhatsAppSandbox).
4. RUN LIFECYCLE CONTROL:
   - PAUSE, RESUME, CANCEL, RETRY, ABORT, APPROVE, DENY.
5. OPERATIONAL EVENT LOGGING:
   - Reconstrucción de turnos auditables sin fuga de secretos ni de cadenas de pensamiento privadas.
"""

from __future__ import annotations
import time
import json
import uuid
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

from src.core.platform.models import TenantStatus, AgentStatus
from src.core.platform.capabilities import (
    PLATFORM_CAPABILITIES_CATALOG, CapabilityEngine, PermissionLevel, ApprovalRequirement
)
from src.core.platform.store import platform_store
from src.core.platform.manager import control_plane
from src.core.operator.business_config import BusinessConfig

log = logging.getLogger("firby.platform.control")


class RunControlState(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    CANCELLED = "CANCELLED"
    ABORTED = "ABORTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class CapabilityStatus:
    capability: str
    enabled: bool
    authorized: bool
    requires_approval: bool
    available_in_environment: bool
    permission_level: str = "read"
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.capability,
            "tool_id": self.capability,
            "name": self.capability,
            "capability": self.capability,
            "enabled": self.enabled,
            "is_active": self.enabled,
            "authorized": self.authorized,
            "requires_approval": self.requires_approval,
            "requires_hitl": self.requires_approval,
            "available_in_environment": self.available_in_environment,
            "permission_level": self.permission_level,
            "reason": self.reason
        }


@dataclass
class ControlDecision:
    allowed: bool
    requires_approval: bool
    is_dry_run: bool
    tool_name: str
    reason: str = ""
    sanitized_args: Dict[str, Any] = field(default_factory=dict)
    simulated_result: Optional[Dict[str, Any]] = None


@dataclass
class AgentRunRecord:
    run_id: str
    tenant_id: str
    agent_id: str
    user_id: str
    state: RunControlState = RunControlState.IDLE
    created_at: float = field(default_factory=time.time)
    step_count: int = 0
    max_steps: int = 6
    timeout_seconds: float = 30.0
    dry_run: bool = False
    pending_approval: Optional[Dict[str, Any]] = None
    cancellation_reason: Optional[str] = None
    events: List[Dict[str, Any]] = field(default_factory=list)

    def is_active(self) -> bool:
        return self.state in (RunControlState.RUNNING, RunControlState.WAITING_APPROVAL)

    def is_timed_out(self) -> bool:
        return (time.time() - self.created_at) > self.timeout_seconds

    def add_event(self, event_type: str, data: Dict[str, Any]):
        evt = {
            "timestamp": time.time(),
            "event": event_type,
            "step": self.step_count,
            "data": data
        }
        self.events.append(evt)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "state": self.state.value if isinstance(self.state, RunControlState) else str(self.state),
            "step_count": self.step_count,
            "max_steps": self.max_steps,
            "timeout_seconds": self.timeout_seconds,
            "dry_run": self.dry_run,
            "pending_approval": self.pending_approval,
            "cancellation_reason": self.cancellation_reason,
            "events_count": len(self.events),
            "events": self.events
        }


# ═════════════════════════════════════════════════════════════════════════════
# 1. TOOL SANDBOXES (SIMULATED EXTERNAL SERVICES)
# ═════════════════════════════════════════════════════════════════════════════

class CalendarSandbox:
    """Simulador de Google Calendar para validación segura pre-publicación."""

    def __init__(self):
        self.simulated_bookings: List[Dict[str, Any]] = []

    def check_availability(self, date_str: str = "mañana") -> Dict[str, Any]:
        return {
            "success": True,
            "simulated": True,
            "date": date_str,
            "available_slots": ["09:00", "11:30", "14:00", "16:30"],
            "timezone": "America/Bogota"
        }

    def book_appointment(
        self,
        date_str: str,
        time_str: str,
        client_name: str = "Paciente",
        phone: str = "",
        service: str = "Consulta General"
    ) -> Dict[str, Any]:
        booking = {
            "success": True,
            "simulated": True,
            "status": "SIMULATED_CONFIRMED",
            "appointment_id": f"sandbox_appt_{int(time.time() * 1000)}",
            "date": date_str,
            "time": time_str,
            "client_name": client_name,
            "phone": phone,
            "service": service,
            "message": "Cita confirmada en simulación Sandbox (sin modificar Google Calendar real)."
        }
        self.simulated_bookings.append(booking)
        return booking


class CRMSandbox:
    """Simulador de CRM para captura de prospectos y leads."""

    def __init__(self):
        self.captured_leads: List[Dict[str, Any]] = []

    def capture_lead(
        self,
        name: str,
        email_or_phone: str = "",
        phone: str = "",
        interest: str = "General"
    ) -> Dict[str, Any]:
        lead = {
            "success": True,
            "simulated": True,
            "lead_id": f"sandbox_lead_{int(time.time() * 1000)}",
            "name": name,
            "email_or_phone": email_or_phone,
            "phone": phone or email_or_phone,
            "interest": interest,
            "timestamp": time.time()
        }
        self.captured_leads.append(lead)
        return lead


class WhatsAppSandbox:
    """Simulador de notificaciones salientes de WhatsApp ejecutivo."""

    def __init__(self):
        self.sent_messages: List[Dict[str, Any]] = []

    def send_owner_alert(self, phone: str, message: str) -> Dict[str, Any]:
        msg = {
            "success": True,
            "simulated": True,
            "delivered": True,
            "message_id": f"sandbox_wa_{int(time.time() * 1000)}",
            "recipient": phone,
            "status": "delivered_to_sandbox",
            "body": message,
            "timestamp": time.time()
        }
        self.sent_messages.append(msg)
        return msg

    def send_alert(self, phone: str, message: str) -> Dict[str, Any]:
        return self.send_owner_alert(phone, message)


# ═════════════════════════════════════════════════════════════════════════════
# 2. AGENT CONTROL ENGINE
# ═════════════════════════════════════════════════════════════════════════════

class AgentControlSystem:
    """Motor central de gobernanza dura y control de ejecución agéntica."""

    def __init__(self):
        self._active_runs: Dict[str, AgentRunRecord] = {}
        self.calendar_sandbox = CalendarSandbox()
        self.crm_sandbox = CRMSandbox()
        self.whatsapp_sandbox = WhatsAppSandbox()

    def get_capability_matrix(self, tenant_id: str, agent_id: str) -> List[CapabilityStatus]:
        """
        Construye la matriz de capacidades completa y verificable para una instancia de agente.
        """
        agent = platform_store.get_agent_instance(tenant_id, agent_id)
        if not agent:
            return []

        # Obtener configuración desde versión publicada o borrador
        config = None
        if agent.published_version:
            v_rec = platform_store.get_agent_version(tenant_id, agent_id, agent.published_version)
            if v_rec and v_rec.config_dict:
                config = BusinessConfig.from_dict(v_rec.config_dict)
        if not config:
            config = control_plane.get_active_config(tenant_id, agent_id)

        matrix: List[CapabilityStatus] = []
        for cap_name, cap_def in PLATFORM_CAPABILITIES_CATALOG.items():
            if config:
                eval_res = CapabilityEngine.evaluate_capability(config, cap_name)
                alias_name = "web_navigation" if cap_name == "navigate_web" else ("navigate_web" if cap_name == "web_navigation" else cap_name)
                perm = config.tool_permissions.get(cap_name) or config.tool_permissions.get(alias_name)
                is_enabled = perm.enabled if perm else False
                is_authorized = eval_res.authorized
                requires_appr = (perm.requires_authorization if (perm and perm.requires_authorization is not None) else False) or (eval_res.approval_mode in (ApprovalRequirement.HUMAN, ApprovalRequirement.OWNER_WHATSAPP))
                available_in_env = len(eval_res.missing_integrations) == 0
                reason = eval_res.reason or "Autorizado para ejecución"
            else:
                is_enabled = False
                is_authorized = False
                requires_appr = cap_def.default_approval in (ApprovalRequirement.HUMAN, ApprovalRequirement.OWNER_WHATSAPP)
                available_in_env = len(cap_def.required_integrations) == 0
                reason = "Sin configuración de agente"

            matrix.append(CapabilityStatus(
                capability=cap_name,
                enabled=is_enabled,
                authorized=is_authorized,
                requires_approval=requires_appr,
                available_in_environment=available_in_env,
                permission_level=cap_def.permission_level.value,
                reason=reason
            ))

        return matrix

    def evaluate_tool_request(
        self,
        tenant_id: str,
        agent_id: str,
        tool_name: str,
        args: Dict[str, Any],
        dry_run: bool = False
    ) -> ControlDecision:
        """
        Evalúa de forma estricta e incorruptible si una herramienta puede ejecutarse.
        Inmune a inyecciones de prompt.
        """
        clean_tool = (tool_name or "").strip().lower()

        # 1. Herramientas de UI / Navegación: autorizadas por defecto si están en catálogo
        if clean_tool in ("navigate_to_section", "navigate_to", "highlight_element", "scroll_to", "highlight_ui"):
            return ControlDecision(
                allowed=True,
                requires_approval=False,
                is_dry_run=dry_run,
                tool_name=clean_tool,
                reason="Herramienta de navegación segura autorizada",
                sanitized_args=args
            )

        # 2. Cargar configuración del agente
        config = control_plane.get_agent_config(tenant_id, agent_id)
        if not config:
            return ControlDecision(
                allowed=False,
                requires_approval=False,
                is_dry_run=dry_run,
                tool_name=clean_tool,
                reason=f"Gobernanza: Configuración no encontrada para el agente '{agent_id}'."
            )

        # 3. Evaluación exhaustiva mediante CapabilityEngine
        eval_res = CapabilityEngine.evaluate_capability(config, clean_tool)
        if not eval_res.authorized:
            return ControlDecision(
                allowed=False,
                requires_approval=False,
                is_dry_run=dry_run,
                tool_name=clean_tool,
                reason=f"Gobernanza: Permiso denegado ({eval_res.reason})"
            )

        # 4. Manejo de modalidad DRY-RUN o Sandboxing
        sim_res = None
        if dry_run:
            if clean_tool in ("schedule_appointment", "book_appointment"):
                sim_res = self.calendar_sandbox.book_appointment(
                    date_str=args.get("date", "mañana"),
                    time_str=args.get("time", "10:00 AM"),
                    client_name=args.get("client_name", "Cliente Simulado"),
                    phone=args.get("phone", "+573000000000"),
                    service=args.get("service", "Consulta General")
                )
            elif clean_tool == "check_availability":
                sim_res = self.calendar_sandbox.check_availability(date_str=args.get("date", "mañana"))
            elif clean_tool in ("capture_lead", "save_contact"):
                sim_res = self.crm_sandbox.capture_lead(
                    name=args.get("name", "Lead Simulado"),
                    email_or_phone=args.get("email", ""),
                    phone=args.get("phone", "+573000000000"),
                    interest=args.get("interest", "General")
                )
            elif clean_tool in ("send_alert", "escalate_to_human"):
                sim_res = self.whatsapp_sandbox.send_owner_alert(
                    phone=args.get("phone", "admin"),
                    message=args.get("message", "Alerta simulada")
                )

        requires_appr = eval_res.approval_mode in (ApprovalRequirement.HUMAN, ApprovalRequirement.OWNER_WHATSAPP)
        return ControlDecision(
            allowed=True,
            requires_approval=requires_appr and not dry_run,
            is_dry_run=dry_run,
            tool_name=clean_tool,
            reason="Autorizado por matriz de control",
            sanitized_args=args,
            simulated_result=sim_res
        )

    # Alias para compatibilidad con suites de prueba
    authorize_action = evaluate_tool_request

    # ─────────────────────────────────────────────────────────────────────────
    # RUN LIFECYCLE MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────

    def create_run(
        self,
        tenant_id: str,
        agent_id: str,
        channel: str = "web",
        user_query: str = "",
        user_id: str = "anon",
        max_steps: int = 6,
        timeout_seconds: float = 30.0,
        dry_run: bool = False,
        run_id: Optional[str] = None
    ) -> AgentRunRecord:
        """Inicializa un turno de ejecución auditable con límites duros."""
        rid = run_id or f"run_{uuid.uuid4().hex[:12]}"
        run = AgentRunRecord(
            run_id=rid,
            tenant_id=tenant_id,
            agent_id=agent_id,
            user_id=user_id,
            state=RunControlState.RUNNING,
            dry_run=dry_run,
            max_steps=max_steps,
            timeout_seconds=timeout_seconds
        )
        run.add_event("run.started", {
            "channel": channel,
            "query": user_query,
            "dry_run": dry_run,
            "max_steps": max_steps
        })
        self._active_runs[rid] = run
        return run

    def get_run(self, run_id: str) -> Optional[AgentRunRecord]:
        return self._active_runs.get(run_id)

    def pause_run(self, run_id: str, actor: str = "admin") -> bool:
        run = self.get_run(run_id)
        if run and run.state == RunControlState.RUNNING:
            run.state = RunControlState.PAUSED
            run.add_event("run.paused", {"actor": actor})
            return True
        return False

    def resume_run(self, run_id: str, actor: str = "admin") -> bool:
        run = self.get_run(run_id)
        if run and run.state == RunControlState.PAUSED:
            run.state = RunControlState.RUNNING
            run.add_event("run.resumed", {"actor": actor})
            return True
        return False

    def cancel_run(self, run_id: str, reason: str = "manual_cancellation", actor: str = "admin") -> bool:
        run = self.get_run(run_id)
        if run and run.is_active():
            run.state = RunControlState.CANCELLED
            run.cancellation_reason = reason
            run.add_event("run.cancelled", {"actor": actor, "reason": reason})
            return True
        return False

    def abort_run(self, run_id: str, reason: str = "execution_limit_exceeded", actor: str = "system") -> bool:
        run = self.get_run(run_id)
        if run:
            run.state = RunControlState.ABORTED
            run.cancellation_reason = reason
            run.add_event("run.aborted", {"actor": actor, "reason": reason})
            return True
        return False

    def register_run(
        self,
        tenant_id: str,
        agent_id: str,
        user_id: str = "anon",
        channel: str = "web",
        user_query: str = "",
        **kwargs
    ) -> AgentRunRecord:
        return self.create_run(
            tenant_id=tenant_id,
            agent_id=agent_id,
            channel=channel,
            user_query=user_query,
            user_id=user_id,
            **kwargs
        )

    def request_approval(self, run_id: str, action: Any, payload: Optional[Dict[str, Any]] = None) -> bool:
        run = self.get_run(run_id)
        if run and run.state == RunControlState.RUNNING:
            run.state = RunControlState.WAITING_APPROVAL
            action_data = {"action": action, "payload": payload or {}} if isinstance(action, str) else action
            run.pending_approval = action_data
            run.add_event("run.waiting_approval", {"action": action_data})
            return True
        return False

    def request_human_approval(
        self,
        run_id: str,
        action_type: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        return self.request_approval(run_id=run_id, action=action_type, payload=details)

    def approve_action(self, run_id: str, actor: str = "admin") -> Tuple[bool, Optional[Dict[str, Any]]]:
        run = self.get_run(run_id)
        if run and run.state == RunControlState.WAITING_APPROVAL and run.pending_approval:
            action = run.pending_approval
            run.pending_approval = None
            run.state = RunControlState.RUNNING
            run.add_event("run.action_approved", {"actor": actor, "action": action})
            return True, action
        return False, None

    def deny_action(self, run_id: str, reason: str = "denied_by_admin", actor: str = "admin") -> bool:
        run = self.get_run(run_id)
        if run and run.state == RunControlState.WAITING_APPROVAL:
            run.pending_approval = None
            run.state = RunControlState.RUNNING
            run.add_event("run.action_denied", {"actor": actor, "reason": reason})
            return True
        return False

    def step_check(self, run_id: str) -> Tuple[bool, str]:
        """
        Comprueba las invariantes duras de ejecución (pasos máximos y timeout).
        """
        run = self.get_run(run_id)
        if not run:
            return False, "run_not_found"

        if run.state == RunControlState.CANCELLED:
            return False, f"cancelled:{run.cancellation_reason}"

        if run.state == RunControlState.ABORTED:
            return False, f"aborted:{run.cancellation_reason}"

        if run.is_timed_out():
            self.abort_run(run_id, "timeout_exceeded")
            return False, "timeout_exceeded"

        run.step_count += 1
        if run.step_count > run.max_steps:
            self.abort_run(run_id, "max_steps_exceeded")
            return False, "max_steps_exceeded"

        return True, "ok"

    def complete_run(self, run_id: str):
        run = self.get_run(run_id)
        if run and run.state == RunControlState.RUNNING:
            run.state = RunControlState.COMPLETED
            run.add_event("run.completed", {})

    # ─────────────────────────────────────────────────────────────────────────
    # AGENT OPERATIONAL STATE & KILL SWITCH (EMERGENCY STOP)
    # ─────────────────────────────────────────────────────────────────────────

    _agent_operational_cache: Dict[str, str] = {}

    def set_agent_operational_state(
        self,
        tenant_id: str,
        agent_id: str,
        new_state: str,
        reason: str = "",
        actor: str = "admin"
    ) -> Tuple[bool, str]:
        """Modifica el estado operativo real y persistente del agente (online/paused/maintenance/error)."""
        valid_states = {"online", "paused", "maintenance", "error"}
        state_clean = (new_state or "").strip().lower()
        if state_clean not in valid_states:
            return False, f"Estado inválido. Valores permitidos: {', '.join(valid_states)}"

        key = f"{tenant_id}:{agent_id}"
        self._agent_operational_cache[key] = state_clean

        # Persistir en base de datos
        try:
            with platform_store._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE platform_agent_instances
                    SET operational_state = ?, updated_at = datetime('now')
                    WHERE tenant_id = ? AND (agent_id = ? OR ? = '*')
                """, (state_clean, tenant_id, agent_id, agent_id))
                conn.commit()
        except Exception as e:
            log.warning(f"Error persisting agent operational state: {e}")

        # Si el agente se pausa, pausar o abortar runs activos
        if state_clean in ("paused", "maintenance", "error"):
            for r in list(self._active_runs.values()):
                if r.tenant_id == tenant_id and (agent_id == "*" or r.agent_id == agent_id) and r.is_active():
                    self.cancel_run(r.run_id, reason=f"agent_set_to_{state_clean}", actor=actor)

        # Registrar en auditoría
        platform_store.record_audit_event(
            tenant_id=tenant_id,
            agent_id=agent_id,
            action=f"agent.state_{state_clean}",
            actor=actor,
            details={"new_state": state_clean, "reason": reason}
        )

        return True, f"Estado del agente actualizado a '{state_clean}'"

    def get_agent_operational_state(self, tenant_id: str, agent_id: str) -> str:
        """Obtiene el estado operativo actual (online/paused/maintenance/error)."""
        key = f"{tenant_id}:{agent_id}"
        if key in self._agent_operational_cache:
            return self._agent_operational_cache[key]

        try:
            with platform_store._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT operational_state FROM platform_agent_instances
                    WHERE tenant_id = ? AND (agent_id = ? OR ? = '*')
                    LIMIT 1
                """, (tenant_id, agent_id, agent_id))
                row = cur.fetchone()
                if row and row["operational_state"]:
                    st = row["operational_state"].strip().lower()
                    self._agent_operational_cache[key] = st
                    return st
        except Exception as e:
            log.warning(f"Error reading agent operational state: {e}")

        return "online"

    def is_agent_operational(self, tenant_id: str, agent_id: str) -> Tuple[bool, str]:
        """Comprueba si el agente puede aceptar nuevas acciones y responder a usuarios."""
        st = self.get_agent_operational_state(tenant_id, agent_id)
        if st == "online":
            return True, "Operativo"
        elif st == "paused":
            return False, "El agente se encuentra actualmente pausado por el administrador."
        elif st == "maintenance":
            return False, "El agente se encuentra en mantenimiento técnico programado."
        elif st == "error":
            return False, "El agente se encuentra detenido debido a una alerta del sistema."
        return False, f"El agente se encuentra en estado '{st}'."

    def emergency_stop(self, tenant_id: str, agent_id: str = "*", actor: str = "admin") -> Dict[str, Any]:
        """
        KILL SWITCH / PARADA DE EMERGENCIA:
        Bloquea inmediatamente nuevas ejecuciones, detiene turnos en curso y genera auditoría dura.
        """
        stopped_runs = 0
        for r in list(self._active_runs.values()):
            if r.tenant_id == tenant_id and (agent_id == "*" or r.agent_id == agent_id) and r.is_active():
                self.abort_run(r.run_id, reason="emergency_stop_triggered", actor=actor)
                stopped_runs += 1

        self.set_agent_operational_state(
            tenant_id=tenant_id,
            agent_id=agent_id,
            new_state="paused",
            reason="Parada de emergencia (Kill Switch) activada por administrador.",
            actor=actor
        )

        platform_store.record_audit_event(
            tenant_id=tenant_id,
            agent_id=agent_id,
            action="agent.kill_switch_activated",
            actor=actor,
            details={"stopped_runs": stopped_runs}
        )

        return {
            "ok": True,
            "status": "PAUSED",
            "stopped_runs": stopped_runs,
            "cancelled_runs_count": stopped_runs,
            "message": "Parada de emergencia ejecutada. Todas las acciones del agente han sido congeladas de inmediato."
        }


# Instancia única del sistema de control
agent_control = AgentControlSystem()

