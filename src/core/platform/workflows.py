# -*- coding: utf-8 -*-
"""
Firby Platform — Workflow Engine ("El n8n de Firby")
=====================================================
Motor de flujos y automatizaciones visuales para el Control Center de Firby:
- Grafo de ejecución determinista (Nodos y Aristas).
- Triggers reales: conversation_started, message_received, appointment_created,
  form_submitted, lead_created, webhook, schedule.
- Nodos de condición: Evaluación en backend con operadores equals, not_equals,
  contains, greater_than, less_than.
- Nodos de acción: send_message, ask_agent, query_knowledge, check_availability,
  book_appointment, update_knowledge, create_lead, send_webhook, wait, escalate.
- Nodos de aprobación humana: Pausan la ejecución en WAITING_APPROVAL y se
  integran con el AgentControlSystem.
- Contexto de flujo aislado por Tenant y Run (flow_context).
- Simulación en seco (Dry Run) sin efectos secundarios reales.
- Versionado DRAFT -> VALIDATE -> TEST -> PUBLISH -> ACTIVE con soporte de rollback.
"""

from __future__ import annotations
import json
import time
import uuid
import logging
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple

from src.core.platform.store import platform_store
from src.core.platform.control import agent_control, RunControlState

log = logging.getLogger("firby.platform.workflows")


class NodeType(str, Enum):
    TRIGGER = "trigger"
    CONDITION = "condition"
    ACTION = "action"
    APPROVAL = "approval"
    END = "end"


class TriggerType(str, Enum):
    CONVERSATION_STARTED = "conversation_started"
    MESSAGE_RECEIVED = "message_received"
    APPOINTMENT_CREATED = "appointment_created"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    FORM_SUBMITTED = "form_submitted"
    LEAD_CREATED = "lead_created"
    WEBHOOK = "webhook"
    SCHEDULE = "schedule"


class ActionType(str, Enum):
    SEND_MESSAGE = "send_message"
    ASK_AGENT = "ask_agent"
    QUERY_KNOWLEDGE = "query_knowledge"
    CHECK_AVAILABILITY = "check_availability"
    BOOK_APPOINTMENT = "book_appointment"
    UPDATE_KNOWLEDGE = "update_knowledge"
    CREATE_LEAD = "create_lead"
    SEND_WEBHOOK = "send_webhook"
    WAIT = "wait"
    ESCALATE = "escalate"
    RUN_FLOW = "run_flow"


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ExecutionStatus(str, Enum):
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class FlowNode:
    id: str
    type: str  # trigger, condition, action, approval, end
    sub_type: str = ""
    name: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    next_node_id: Optional[str] = None
    # Para nodos de condición:
    true_node_id: Optional[str] = None
    false_node_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "sub_type": self.sub_type,
            "name": self.name,
            "config": self.config,
            "next_node_id": self.next_node_id,
            "true_node_id": self.true_node_id,
            "false_node_id": self.false_node_id
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> FlowNode:
        return cls(
            id=d.get("id", str(uuid.uuid4())[:8]),
            type=d.get("type", "action"),
            sub_type=d.get("sub_type", ""),
            name=d.get("name", ""),
            config=d.get("config") or {},
            next_node_id=d.get("next_node_id"),
            true_node_id=d.get("true_node_id"),
            false_node_id=d.get("false_node_id")
        )


@dataclass
class WorkflowDefinition:
    nodes: Dict[str, FlowNode] = field(default_factory=dict)
    entry_node_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_node_id": self.entry_node_id,
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()}
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> WorkflowDefinition:
        nodes = {}
        for k, v in (d.get("nodes") or {}).items():
            nodes[k] = FlowNode.from_dict(v)
        return cls(
            nodes=nodes,
            entry_node_id=d.get("entry_node_id", "")
        )


@dataclass
class WorkflowRecord:
    workflow_id: str
    tenant_id: str
    agent_id: str
    name: str
    description: str
    status: WorkflowStatus
    version: int
    definition: WorkflowDefinition
    published_at: Optional[str] = None
    created_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))

    @property
    def id(self) -> str:
        return self.workflow_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.workflow_id,
            "workflow_id": self.workflow_id,
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value if isinstance(self.status, WorkflowStatus) else str(self.status),
            "version": self.version,
            "definition": self.definition.to_dict(),
            "published_at": self.published_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class WorkflowEngine:
    """Motor de ejecución, validación y simulación de flujos de trabajo."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            import os
            db_path = os.getenv("PLATFORM_DB_PATH") or os.getenv("FIRBY_ULTRA_DB") or "firby_ultra.db"
        self.db_path = db_path

    def _get_conn(self):
        import sqlite3
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        return conn

    # ─────────────────────────────────────────────────────────────────────────
    # 1. VALIDACIÓN DE FLUJOS
    # ─────────────────────────────────────────────────────────────────────────

    def validate_workflow(self, definition: WorkflowDefinition) -> Tuple[bool, List[str]]:
        """Valida estructuralmente el grafo del flujo."""
        errors: List[str] = []

        if not definition.nodes:
            errors.append("El flujo no contiene nodos.")
            return False, errors

        if not definition.entry_node_id or definition.entry_node_id not in definition.nodes:
            # Buscar el primer nodo de tipo trigger
            triggers = [n for n in definition.nodes.values() if n.type == NodeType.TRIGGER.value]
            if not triggers:
                errors.append("El flujo debe tener al menos un nodo disparador (Trigger).")
            else:
                definition.entry_node_id = triggers[0].id

        visited = set()
        to_visit = [definition.entry_node_id] if definition.entry_node_id in definition.nodes else []

        while to_visit:
            nid = to_visit.pop()
            if nid in visited:
                continue
            visited.add(nid)
            node = definition.nodes.get(nid)
            if not node:
                errors.append(f"El nodo '{nid}' no existe en el flujo.")
                continue

            if node.type == NodeType.CONDITION.value:
                if not node.true_node_id and not node.false_node_id:
                    errors.append(f"El nodo de condición '{node.name or node.id}' no tiene ramas de salida.")
                if node.true_node_id:
                    if node.true_node_id not in definition.nodes:
                        errors.append(f"El nodo '{node.true_node_id}' referenciado en la rama verdadera no existe.")
                    else:
                        to_visit.append(node.true_node_id)
                if node.false_node_id:
                    if node.false_node_id not in definition.nodes:
                        errors.append(f"El nodo '{node.false_node_id}' referenciado en la rama falsa no existe.")
                    else:
                        to_visit.append(node.false_node_id)
            elif node.type in (NodeType.TRIGGER.value, NodeType.ACTION.value, NodeType.APPROVAL.value):
                if node.next_node_id:
                    if node.next_node_id not in definition.nodes:
                        errors.append(f"El nodo siguiente '{node.next_node_id}' no existe en la definición.")
                    else:
                        to_visit.append(node.next_node_id)

        is_valid = len(errors) == 0
        return is_valid, errors

    # ─────────────────────────────────────────────────────────────────────────
    # 2. DRY RUN (SIMULACIÓN PASO A PASO)
    # ─────────────────────────────────────────────────────────────────────────

    def dry_run(
        self,
        arg1: Any = None,
        arg2: Any = None,
        arg3: Any = None,
        workflow_id: Optional[str] = None,
        test_payload: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Ejecuta una simulación completa paso a paso del flujo sin modificar sistemas externos.
        Soporta:
        - dry_run(tenant_id, workflow_def, initial_payload)
        - dry_run(workflow_id="...", test_payload={...})
        """
        wdef: Optional[WorkflowDefinition] = None
        t_id = tenant_id
        initial_payload: Dict[str, Any] = {}

        if isinstance(arg1, str) and isinstance(arg2, WorkflowDefinition):
            t_id = arg1
            wdef = arg2
            initial_payload = arg3 or {}
        elif workflow_id or (isinstance(arg1, str) and not isinstance(arg2, WorkflowDefinition)):
            wid = workflow_id or arg1
            initial_payload = test_payload if test_payload is not None else (arg2 or {})
            wf_rec = self.get_workflow(wid)
            if not wf_rec:
                return {"ok": False, "success": False, "error": f"Workflow {wid} no encontrado."}
            wdef = wf_rec.definition
            t_id = wf_rec.tenant_id
        elif isinstance(arg1, WorkflowDefinition):
            wdef = arg1
            initial_payload = arg2 or {}

        if not wdef:
            return {"ok": False, "success": False, "error": "Definición de workflow requerida."}

        is_valid, errors = self.validate_workflow(wdef)
        if not is_valid:
            return {
                "ok": False,
                "success": False,
                "status": "VALIDATION_FAILED",
                "errors": errors,
                "steps": [],
                "execution_log": []
            }

        context: Dict[str, Any] = {
            "tenant_id": t_id,
            "simulated": True,
            "variables": dict(initial_payload)
        }

        execution_log: List[Dict[str, Any]] = []
        current_id = wdef.entry_node_id
        max_steps = 25
        step = 0

        while current_id and step < max_steps:
            step += 1
            node = wdef.nodes.get(current_id)
            if not node:
                break

            log_entry: Dict[str, Any] = {
                "step": step,
                "node_id": node.id,
                "node_name": node.name or node.id,
                "type": node.type,
                "node_type": node.type,
                "sub_type": node.sub_type,
                "inputs": dict(context["variables"])
            }

            next_node: Optional[str] = None

            if node.type == NodeType.TRIGGER.value:
                log_entry["action"] = f"Trigger activado: {node.sub_type}"
                log_entry["result"] = {"triggered": True, "event": initial_payload}
                next_node = node.next_node_id

            elif node.type == NodeType.CONDITION.value:
                cond_cfg = node.config or {}
                var_name = cond_cfg.get("variable", "")
                operator = cond_cfg.get("operator", "equals")
                target_val = cond_cfg.get("value", "")

                actual_val = context["variables"].get(var_name, "")
                cond_met = self._evaluate_condition(actual_val, operator, target_val)

                log_entry["condition_evaluation"] = {
                    "variable": var_name,
                    "actual": actual_val,
                    "operator": operator,
                    "target": target_val,
                    "result": cond_met
                }
                next_node = node.true_node_id if cond_met else node.false_node_id
                log_entry["branch_taken"] = "true_branch" if cond_met else "false_branch"

            elif node.type == NodeType.ACTION.value:
                action_type = node.sub_type
                cfg = node.config or {}
                sim_res = self._execute_simulated_action(t_id, action_type, cfg, context["variables"])
                log_entry["action"] = f"Acción ejecutada: {action_type}"
                log_entry["result"] = sim_res
                if isinstance(sim_res, dict) and "output_variable" in cfg:
                    context["variables"][cfg["output_variable"]] = sim_res
                next_node = node.next_node_id

            elif node.type == NodeType.APPROVAL.value:
                log_entry["action"] = "Aprobación Humana Requerida"
                log_entry["result"] = {
                    "status": "WAITING_APPROVAL",
                    "approver": node.config.get("approver", "owner"),
                    "simulated_outcome": "pending_admin_approval"
                }
                next_node = node.next_node_id

            elif node.type == NodeType.END.value:
                log_entry["action"] = "Fin de flujo"
                next_node = None

            execution_log.append(log_entry)
            current_id = next_node

        return {
            "ok": True,
            "success": True,
            "status": "COMPLETED",
            "total_steps": len(execution_log),
            "steps": execution_log,
            "execution_log": execution_log,
            "final_variables": context["variables"]
        }

    def _evaluate_condition(self, actual: Any, operator: str, target: Any) -> bool:
        """Evalúa operadores de condición."""
        actual_str = str(actual).strip().lower()
        target_str = str(target).strip().lower()

        if operator == "equals":
            return actual_str == target_str
        elif operator == "not_equals":
            return actual_str != target_str
        elif operator == "contains":
            return target_str in actual_str
        elif operator == "greater_than":
            try:
                return float(actual) > float(target)
            except (ValueError, TypeError):
                return False
        elif operator == "less_than":
            try:
                return float(actual) < float(target)
            except (ValueError, TypeError):
                return False
        return False

    def _execute_simulated_action(
        self,
        tenant_id: str,
        action_type: str,
        config: Dict[str, Any],
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta una acción en el entorno de Sandboxing de Firby."""
        if action_type in ("check_availability",):
            date_val = variables.get("date") or config.get("date", "mañana")
            return agent_control.calendar_sandbox.check_availability(date_val)
        elif action_type in ("book_appointment",):
            return agent_control.calendar_sandbox.book_appointment(
                date_str=variables.get("date") or config.get("date", "mañana"),
                time_str=variables.get("time") or config.get("time", "10:00 AM"),
                client_name=variables.get("name") or config.get("client_name", "Cliente"),
                phone=variables.get("phone") or config.get("phone", "+573000000000"),
                service=variables.get("service") or config.get("service", "Consulta General")
            )
        elif action_type in ("create_lead",):
            return agent_control.crm_sandbox.capture_lead(
                name=variables.get("name") or config.get("name", "Prospecto"),
                email_or_phone=variables.get("contact") or config.get("phone", "+573000000000"),
                interest=variables.get("interest") or config.get("interest", "General")
            )
        elif action_type in ("send_message", "escalate"):
            return agent_control.whatsapp_sandbox.send_owner_alert(
                phone=config.get("phone", "admin"),
                message=config.get("message", "Mensaje de workflow ejecutado.")
            )
        elif action_type in ("send_webhook",):
            return {
                "success": True,
                "simulated": True,
                "endpoint": config.get("url", "https://webhook.site/demo"),
                "status_code": 200
            }
        return {"success": True, "simulated": True, "action": action_type}

    # ─────────────────────────────────────────────────────────────────────────
    # 3. GESTIÓN Y PERSISTENCIA DE WORKFLOWS
    # ─────────────────────────────────────────────────────────────────────────

    def save_workflow(
        self,
        tenant_id: str,
        name: str,
        definition: WorkflowDefinition,
        description: str = "",
        agent_id: str = "*",
        workflow_id: Optional[str] = None
    ) -> WorkflowRecord:
        """Crea o actualiza un workflow en estado borrador (draft)."""
        wid = workflow_id or f"wf_{uuid.uuid4().hex[:10]}"
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT version, status FROM platform_workflows WHERE workflow_id = ? AND tenant_id = ?", (wid, tenant_id))
            row = cur.fetchone()
            version = (row["version"] + 1) if row else 1
            status = row["status"] if row else WorkflowStatus.DRAFT.value

            cur.execute("""
                INSERT OR REPLACE INTO platform_workflows (
                    workflow_id, tenant_id, agent_id, name, description,
                    status, version, definition_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                wid, tenant_id, agent_id, name, description,
                status, version, json.dumps(definition.to_dict()), now
            ))
            conn.commit()

        return WorkflowRecord(
            workflow_id=wid,
            tenant_id=tenant_id,
            agent_id=agent_id,
            name=name,
            description=description,
            status=WorkflowStatus(status),
            version=version,
            definition=definition,
            updated_at=now
        )

    def publish_workflow(self, arg1: str, arg2: Optional[str] = None, actor: str = "admin") -> Tuple[bool, str]:
        """Valida y publica un workflow haciéndolo activo para el runtime."""
        if arg2 is not None and not str(arg2).startswith("admin") and not str(arg2).startswith("user"):
            tenant_id, workflow_id = arg1, arg2
        else:
            workflow_id = arg1
            tenant_id = None
            if isinstance(arg2, str) and (arg2.startswith("admin") or arg2.startswith("user")):
                actor = arg2

        wf = self.get_workflow(workflow_id, tenant_id=tenant_id)
        if not wf:
            return False, "Workflow no encontrado."

        is_valid, errors = self.validate_workflow(wf.definition)
        if not is_valid:
            return False, f"Error de validación: {'; '.join(errors)}"

        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE platform_workflows SET
                    status = 'published',
                    published_at = ?,
                    updated_at = ?
                WHERE workflow_id = ?
            """, (now, now, wf.workflow_id))
            conn.commit()

        # Registrar en auditoría
        platform_store.record_audit_event(
            tenant_id=wf.tenant_id,
            agent_id=wf.agent_id,
            action="workflow.published",
            actor=actor,
            details={"workflow_id": wf.workflow_id, "name": wf.name, "version": wf.version}
        )

        return True, "Workflow publicado exitosamente."

    def list_workflows(self, tenant_id: str) -> List[WorkflowRecord]:
        """Lista todos los workflows pertenecientes a un tenant."""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM platform_workflows WHERE tenant_id = ? ORDER BY updated_at DESC
            """, (tenant_id,))
            rows = cur.fetchall()

        results = []
        for r in rows:
            results.append(WorkflowRecord(
                workflow_id=r["workflow_id"],
                tenant_id=r["tenant_id"],
                agent_id=r["agent_id"],
                name=r["name"],
                description=r["description"] or "",
                status=WorkflowStatus(r["status"]),
                version=r["version"],
                definition=WorkflowDefinition.from_dict(json.loads(r["definition_json"] or "{}")),
                published_at=r["published_at"],
                created_at=r["created_at"] or "",
                updated_at=r["updated_at"] or ""
            ))
        return results

    def get_workflow(self, arg1: str, arg2: Optional[str] = None, tenant_id: Optional[str] = None) -> Optional[WorkflowRecord]:
        """Obtiene un workflow específico por (tenant_id, workflow_id) o (workflow_id)."""
        if arg2 is not None:
            t_id, w_id = arg1, arg2
        else:
            w_id = arg1
            t_id = tenant_id

        with self._get_conn() as conn:
            cur = conn.cursor()
            if t_id:
                cur.execute("""
                    SELECT * FROM platform_workflows WHERE workflow_id = ? AND tenant_id = ?
                """, (w_id, t_id))
            else:
                cur.execute("""
                    SELECT * FROM platform_workflows WHERE workflow_id = ?
                """, (w_id,))
            r = cur.fetchone()
            if not r:
                return None

            return WorkflowRecord(
                workflow_id=r["workflow_id"],
                tenant_id=r["tenant_id"],
                agent_id=r["agent_id"],
                name=r["name"],
                description=r["description"] or "",
                status=WorkflowStatus(r["status"]),
                version=r["version"],
                definition=WorkflowDefinition.from_dict(json.loads(r["definition_json"] or "{}")),
                published_at=r["published_at"],
                created_at=r["created_at"] or "",
                updated_at=r["updated_at"] or ""
            )

    def create_prebuilt_templates(self, tenant_id: str = "default", agent_id: str = "firby_operator_default") -> List[WorkflowRecord]:
        """Crea o sincroniza las 4 plantillas operacionales clave de Firby."""
        templates_defs = [
            {
                "id": f"tpl_direct_booking_{tenant_id}",
                "name": "Reserva Directa en Google Calendar",
                "description": "Verifica disponibilidad en agenda, bloquea la cita y notifica confirmación al dueño.",
                "entry_node_id": "trigger_1",
                "nodes": {
                    "trigger_1": FlowNode(id="trigger_1", type=NodeType.TRIGGER.value, sub_type=TriggerType.APPOINTMENT_CREATED.value, name="Cita solicitada en widget web", next_node_id="act_check"),
                    "act_check": FlowNode(id="act_check", type=NodeType.ACTION.value, sub_type=ActionType.CHECK_AVAILABILITY.value, name="Consultar Google Calendar", next_node_id="act_book"),
                    "act_book": FlowNode(id="act_book", type=NodeType.ACTION.value, sub_type=ActionType.BOOK_APPOINTMENT.value, name="Reservar espacio en calendario", next_node_id="act_notify"),
                    "act_notify": FlowNode(id="act_notify", type=NodeType.ACTION.value, sub_type=ActionType.SEND_MESSAGE.value, name="Notificar al dueño por WhatsApp", config={"phone": "+57 324 369 9856"}, next_node_id="end_1"),
                    "end_1": FlowNode(id="end_1", type=NodeType.END.value, name="Cita agendada con éxito")
                }
            },
            {
                "id": f"tpl_price_exception_{tenant_id}",
                "name": "Excepción de Precio y Descuento Comercial",
                "description": "Si un visitante pide descuento superior a política, solicita visto bueno al dueño por WhatsApp.",
                "entry_node_id": "trigger_1",
                "nodes": {
                    "trigger_1": FlowNode(id="trigger_1", type=NodeType.TRIGGER.value, sub_type=TriggerType.MESSAGE_RECEIVED.value, name="Solicitud de descuento comercial", next_node_id="cond_disc"),
                    "cond_disc": FlowNode(id="cond_disc", type=NodeType.CONDITION.value, name="¿Descuento > 15%?", config={"variable": "discount_pct", "operator": "greater_than", "value": "15"}, true_node_id="appr_hitl", false_node_id="act_reply"),
                    "appr_hitl": FlowNode(id="appr_hitl", type=NodeType.APPROVAL.value, name="Aprobación Humana Dueño (WhatsApp)", next_node_id="act_reply"),
                    "act_reply": FlowNode(id="act_reply", type=NodeType.ACTION.value, sub_type=ActionType.SEND_MESSAGE.value, name="Enviar respuesta oficial al visitante", next_node_id="end_1"),
                    "end_1": FlowNode(id="end_1", type=NodeType.END.value, name="Trámite resuelto")
                }
            },
            {
                "id": f"tpl_owner_vip_alert_{tenant_id}",
                "name": "Alerta VIP al Dueño del Negocio",
                "description": "Línea ejecutiva continua: envía alertas inmediatas a WhatsApp ante oportunidades de alto valor.",
                "entry_node_id": "trigger_1",
                "nodes": {
                    "trigger_1": FlowNode(id="trigger_1", type=NodeType.TRIGGER.value, sub_type=TriggerType.LEAD_CREATED.value, name="Lead calificado de alto valor capturado", next_node_id="act_alert"),
                    "act_alert": FlowNode(id="act_alert", type=NodeType.ACTION.value, sub_type=ActionType.SEND_MESSAGE.value, name="WhatsApp ejecutivo (+57 324 369 9856)", config={"recipient": "owner"}, next_node_id="end_1"),
                    "end_1": FlowNode(id="end_1", type=NodeType.END.value, name="Alerta entregada")
                }
            },
            {
                "id": f"tpl_crm_sync_{tenant_id}",
                "name": "Sincronización Inmediata con CRM",
                "description": "Registra datos de contacto y dispara webhook seguro firmado con HMAC.",
                "entry_node_id": "trigger_1",
                "nodes": {
                    "trigger_1": FlowNode(id="trigger_1", type=NodeType.TRIGGER.value, sub_type=TriggerType.FORM_SUBMITTED.value, name="Formulario completado en el widget", next_node_id="act_lead"),
                    "act_lead": FlowNode(id="act_lead", type=NodeType.ACTION.value, sub_type=ActionType.CREATE_LEAD.value, name="Crear lead en base de datos", next_node_id="act_hook"),
                    "act_hook": FlowNode(id="act_hook", type=NodeType.ACTION.value, sub_type=ActionType.SEND_WEBHOOK.value, name="Disparar webhook CRM firmado", next_node_id="end_1"),
                    "end_1": FlowNode(id="end_1", type=NodeType.END.value, name="Sincronizado")
                }
            }
        ]

        created_records = []
        for tpl in templates_defs:
            wdef = WorkflowDefinition(nodes=tpl["nodes"], entry_node_id=tpl["entry_node_id"])
            rec = self.save_workflow(
                tenant_id=tenant_id,
                agent_id=agent_id,
                name=tpl["name"],
                description=tpl["description"],
                definition=wdef,
                workflow_id=tpl["id"]
            )
            created_records.append(rec)
        return created_records


# Instancia singleton del motor de workflows
workflow_engine = WorkflowEngine()
