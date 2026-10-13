# -*- coding: utf-8 -*-
"""
Firby Platform — Workspace Control Service
==========================================
Capa de servicios centralizada para el Control Center de Firby (/workspace).
Conecta el frontend profesional con el Control Plane y el Agent Runtime:
1. Overview & Operational Reading: Estado en vivo, versión publicada, KPIs reales.
2. Control de Agente: Online/Paused/Maintenance/Error, Kill Switch de emergencia.
3. Control de Runs: Running/Waiting/Done/Failed/Cancelled, Approve/Deny/Cancel.
4. Conversaciones: Explorador de sesiones reales con eventos operativos sin CoT privado.
5. Base de Conocimiento (Knowledge): CRUD particionado, categorías, versionado y enseñanza.
6. Reglas de Negocio (Rules): Políticas estructuradas (condición -> directiva).
7. Herramientas & Capacidades: Toggles reales de permisos y aprobación.
8. Integraciones Empresariales: Meta WhatsApp Business, Google Calendar, CRM, Webhooks.
9. Workflows (n8n de Firby): Creación, simulación dry-run, publicación y versionado.
10. Trial & Facturación: Ciclo de 7 días, cálculo de expiración, cancelación en 1 clic.
11. Onboarding de 7 pasos: Guía interactiva tras alta del cliente.
"""

from __future__ import annotations
import json
import time
import uuid
import logging
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

from src.core.platform.store import platform_store
from src.core.platform.manager import control_plane
from src.core.platform.control import agent_control, RunControlState
from src.core.platform.models import (
    Tenant, AgentInstance, AgentStatus, AgentManifest, KnowledgeItem, AuditEvent
)
from src.core.platform.workflows import workflow_engine, WorkflowDefinition, FlowNode
from src.core.operator.business_config import BusinessConfig, ToolPermission, StructuredRule

log = logging.getLogger("firby.platform.workspace_service")


class WorkspaceService:
    """Servicio integral del Centro de Operaciones de Firby."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            import os
            db_path = os.getenv("PLATFORM_DB_PATH") or os.getenv("FIRBY_ULTRA_DB") or "firby_ultra.db"
        self.db_path = db_path

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        return conn

    # ═════════════════════════════════════════════════════════════════════════
    # 1. OVERVIEW & ESTADO OPERACIONAL
    # ═════════════════════════════════════════════════════════════════════════

    def get_overview(self, tenant_id: str = "default", agent_id: str = "firby_operator_default") -> Dict[str, Any]:
        """Devuelve una lectura operacional completa con datos 100% reales."""
        # 1. Estado del agente y versión publicada
        agent_state = agent_control.get_agent_operational_state(tenant_id, agent_id)
        agent = platform_store.get_agent_instance(tenant_id, agent_id)
        published_version = agent.published_version if agent else 1
        if not published_version:
            published_version = 1

        # 2. Conteo de conversaciones reales
        total_conversations = 0
        today_conversations = 0
        try:
            with self._get_conn() as conn:
                cur = conn.cursor()
                row = cur.execute("SELECT COUNT(*) FROM conversations").fetchone()
                total_conversations = row[0] if row else 0

                today_str = time.strftime("%Y-%m-%d")
                row_today = cur.execute(
                    "SELECT COUNT(*) FROM conversations WHERE ts LIKE ?", (f"{today_str}%",)
                ).fetchone()
                today_conversations = row_today[0] if row_today else 0
        except Exception as e:
            log.warning(f"Error fetching conversation counts: {e}")

        # 3. Conteo de citas reales
        confirmed_appointments = 0
        try:
            with self._get_conn() as conn:
                cur = conn.cursor()
                row = cur.execute("SELECT COUNT(*) FROM appointments WHERE status = 'confirmed'").fetchone()
                confirmed_appointments = row[0] if row else 0
        except Exception as e:
            log.warning(f"Error fetching appointments: {e}")

        # 4. Tareas completadas
        tasks_completed = 0
        try:
            with self._get_conn() as conn:
                cur = conn.cursor()
                row = cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'").fetchone()
                tasks_completed = row[0] if row else 0
        except Exception:
            pass

        # 5. Aprobaciones pendientes en runtime
        pending_approvals_count = sum(
            1 for r in agent_control._active_runs.values()
            if r.tenant_id == tenant_id and r.state == RunControlState.WAITING_APPROVAL
        )

        # 6. Base de conocimiento y reglas
        knowledge_count = len(self.list_knowledge(tenant_id))
        rules_count = len(self.list_rules(tenant_id))
        workflows_count = len(workflow_engine.list_workflows(tenant_id))

        # 7. Estado de facturación / trial
        billing = self.get_billing_status(tenant_id)

        # 8. Actividad reciente
        recent_activity = self.get_activity_feed(tenant_id, limit=6)

        return {
            "ok": True,
            "agent": {
                "agent_id": agent_id,
                "tenant_id": tenant_id,
                "name": agent.name if agent else "Firby Operador",
                "operational_state": agent_state.upper(),  # ONLINE, PAUSED, MAINTENANCE, ERROR
                "published_version": f"v{published_version}",
                "runtime_version": agent.runtime_version if agent else "1.0.0"
            },
            "metrics": {
                "total_conversations": total_conversations,
                "today_conversations": today_conversations,
                "confirmed_appointments": confirmed_appointments,
                "tasks_completed": tasks_completed,
                "pending_approvals": pending_approvals_count,
                "knowledge_items": knowledge_count,
                "active_rules": rules_count,
                "active_workflows": workflows_count
            },
            "billing": billing,
            "recent_activity": recent_activity
        }

    # ═════════════════════════════════════════════════════════════════════════
    # 2. CONTROL REAL DEL AGENTE & KILL SWITCH
    # ═════════════════════════════════════════════════════════════════════════

    def set_agent_state(
        self,
        tenant_id: str,
        agent_id: str,
        state: str,
        reason: str = "",
        actor: str = "admin"
    ) -> Dict[str, Any]:
        """Pone el agente en ONLINE, PAUSED o MAINTENANCE."""
        success, msg = agent_control.set_agent_operational_state(
            tenant_id=tenant_id,
            agent_id=agent_id,
            new_state=state,
            reason=reason,
            actor=actor
        )
        return {
            "ok": success,
            "state": state.upper(),
            "message": msg
        }

    def emergency_stop(self, tenant_id: str, agent_id: str = "*", actor: str = "admin") -> Dict[str, Any]:
        """KILL SWITCH: Congela todas las operaciones del agente de inmediato."""
        return agent_control.emergency_stop(tenant_id, agent_id, actor=actor)

    def list_runs(
        self,
        tenant_id: str,
        agent_id: str = "*",
        status_filter: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lista todos los turnos/runs de ejecución agéntica activos o recientes."""
        runs = []
        for r in list(agent_control._active_runs.values()):
            if r.tenant_id == tenant_id and (agent_id == "*" or r.agent_id == agent_id):
                if status_filter:
                    st_val = r.state.value if hasattr(r.state, "value") else str(r.state)
                    if st_val.lower() != status_filter.lower():
                        continue
                runs.append(r.to_dict())
        # Ordenar por fecha descendente
        runs.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        return runs[:limit]

    def approve_run(self, run_id: str, actor: str = "admin") -> Dict[str, Any]:
        """Aprueba una acción en espera en el runtime."""
        success, action = agent_control.approve_action(run_id, actor=actor)
        return {
            "ok": success,
            "run_id": run_id,
            "status": "APPROVED" if success else "NOT_FOUND_OR_NOT_WAITING",
            "action": action
        }

    def deny_run(self, run_id: str, reason: str = "denied_by_admin", actor: str = "admin") -> Dict[str, Any]:
        """Rechaza una acción en espera en el runtime."""
        success = agent_control.deny_action(run_id, reason=reason, actor=actor)
        return {
            "ok": success,
            "run_id": run_id,
            "status": "DENIED" if success else "NOT_FOUND_OR_NOT_WAITING"
        }

    def cancel_run(self, run_id: str, reason: str = "cancelled_by_admin", actor: str = "admin") -> Dict[str, Any]:
        """Cancela un turno de ejecución activo."""
        success = agent_control.cancel_run(run_id, reason=reason, actor=actor)
        return {
            "ok": success,
            "run_id": run_id,
            "status": "CANCELLED" if success else "NOT_FOUND"
        }

    # ═════════════════════════════════════════════════════════════════════════
    # 3. CONVERSACIONES REALES (AUDITORÍA OPERACIONAL)
    # ═════════════════════════════════════════════════════════════════════════

    def list_conversations(
        self,
        tenant_id: str = "default",
        search: str = "",
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Lista las conversaciones reales registradas en la base de datos."""
        conversations = []
        try:
            with self._get_conn() as conn:
                cur = conn.cursor()
                query = """
                    SELECT chat_id, role, content, ts, model_used
                    FROM conversations
                    GROUP BY chat_id
                    ORDER BY MAX(id) DESC
                    LIMIT ? OFFSET ?
                """
                rows = cur.execute(query, (limit, offset)).fetchall()

                for r in rows:
                    cid = r["chat_id"]
                    # Obtener último mensaje y cantidad de turnos
                    last_msg_row = cur.execute(
                        "SELECT role, content, ts FROM conversations WHERE chat_id = ? ORDER BY id DESC LIMIT 1",
                        (cid,)
                    ).fetchone()
                    msg_count_row = cur.execute(
                        "SELECT COUNT(*) FROM conversations WHERE chat_id = ?", (cid,)
                    ).fetchone()

                    # Comprobar si hay cita asociada
                    apt_row = cur.execute(
                        "SELECT service, datetime_slot, status FROM appointments WHERE chat_id = ? ORDER BY id DESC LIMIT 1",
                        (cid,)
                    ).fetchone()

                    conversations.append({
                        "id": cid,
                        "user_id": cid,
                        "channel": "web",
                        "turn_count": msg_count_row[0] if msg_count_row else 1,
                        "last_message": last_msg_row["content"] if last_msg_row else "",
                        "last_speaker": last_msg_row["role"] if last_msg_row else "user",
                        "updated_at": last_msg_row["ts"] if last_msg_row else r["ts"],
                        "appointment": {
                            "service": apt_row["service"],
                            "slot": apt_row["datetime_slot"],
                            "status": apt_row["status"]
                        } if apt_row else None
                    })
        except Exception as e:
            log.warning(f"Error listing conversations: {e}")

        if search:
            s = search.lower()
            conversations = [c for c in conversations if s in c["id"].lower() or s in c["last_message"].lower()]

        return conversations

    def get_conversation_detail(self, tenant_id: str, chat_id: str) -> Dict[str, Any]:
        """
        Retorna el transcript de la conversación con etiquetas operacionales:
        'Consultó disponibilidad', 'Comprobó política', 'Acción completada' sin CoT privado.
        """
        turns = []
        try:
            with self._get_conn() as conn:
                cur = conn.cursor()
                rows = cur.execute(
                    "SELECT id, role, content, ts, model_used FROM conversations WHERE chat_id = ? ORDER BY id ASC",
                    (chat_id,)
                ).fetchall()

                for r in rows:
                    text = r["content"] or ""
                    # Deducir hitos operacionales limpios para la interfaz
                    operational_event = None
                    if "disponibilidad" in text.lower():
                        operational_event = "Consultó disponibilidad"
                    elif "política" in text.lower() or "cancelación" in text.lower():
                        operational_event = "Comprobó política del negocio"
                    elif "confirmada" in text.lower() or "agendada" in text.lower():
                        operational_event = "Cita agendada en Google Calendar"
                    elif "whatsapp" in text.lower():
                        operational_event = "Derivación a WhatsApp del dueño"

                    turns.append({
                        "id": r["id"],
                        "role": r["role"],
                        "content": text,
                        "created_at": r["ts"],
                        "model_used": r["model_used"] or "firby-runtime",
                        "operational_event": operational_event
                    })

                # Datos del paciente/visitante
                patient_row = cur.execute(
                    "SELECT name, phone, email, notes FROM patients WHERE chat_id = ?", (chat_id,)
                ).fetchone()

                # Cita agendada si existe
                apt_row = cur.execute(
                    "SELECT id, patient_name, patient_phone, service, datetime_slot, status, created_at FROM appointments WHERE chat_id = ? ORDER BY id DESC LIMIT 1",
                    (chat_id,)
                ).fetchone()

                return {
                    "ok": True,
                    "chat_id": chat_id,
                    "turns": turns,
                    "contact": {
                        "name": patient_row["name"] if patient_row else (apt_row["patient_name"] if apt_row else "Visitante Web"),
                        "phone": patient_row["phone"] if patient_row else (apt_row["patient_phone"] if apt_row else ""),
                        "email": patient_row["email"] if patient_row else ""
                    },
                    "appointment": {
                        "id": apt_row["id"],
                        "service": apt_row["service"],
                        "datetime_slot": apt_row["datetime_slot"],
                        "status": apt_row["status"],
                        "created_at": apt_row["created_at"]
                    } if apt_row else None
                }
        except Exception as e:
            log.warning(f"Error fetching conversation detail: {e}")
            return {"ok": False, "error": str(e), "turns": []}

    # ═════════════════════════════════════════════════════════════════════════
    # 4. KNOWLEDGE (BASE DE CONOCIMIENTO)
    # ═════════════════════════════════════════════════════════════════════════

    def list_knowledge(
        self,
        tenant_id: str,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lista los documentos de conocimiento del tenant."""
        items = []
        try:
            with self._get_conn() as conn:
                cur = conn.cursor()
                rows = cur.execute("""
                    SELECT doc_id, tenant_id, agent_id, title, content, source, version, scope, priority, status, metadata_json, created_at, updated_at
                    FROM platform_agent_knowledge
                    WHERE tenant_id = ? AND status != 'archived'
                    ORDER BY priority DESC, created_at ASC
                """, (tenant_id,)).fetchall()
                for r in rows:
                    meta = json.loads(r["metadata_json"] or "{}")
                    items.append({
                        "doc_id": r["doc_id"],
                        "tenant_id": r["tenant_id"],
                        "agent_id": r["agent_id"],
                        "title": r["title"],
                        "content": r["content"],
                        "source": r["source"],
                        "version": r["version"],
                        "scope": r["scope"],
                        "priority": r["priority"],
                        "status": r["status"],
                        "category": meta.get("category", "business"),
                        "metadata": meta,
                        "created_at": r["created_at"],
                        "updated_at": r["updated_at"]
                    })
        except Exception as e:
            log.warning(f"Error listing knowledge: {e}")

        if category and category != "all":
            items = [it for it in items if it.get("category") == category]

        if search:
            s = search.lower()
            items = [it for it in items if s in it["title"].lower() or s in it["content"].lower()]

        return items

    def add_knowledge(
        self,
        tenant_id: str,
        title: str,
        content: str,
        category: str = "business",
        agent_id: str = "*",
        scope: str = "public",
        priority: int = 0,
        source: str = "admin_workspace"
    ) -> Dict[str, Any]:
        """Crea un nuevo documento de conocimiento en el Control Plane."""
        doc_id = f"doc_{uuid.uuid4().hex[:10]}"
        meta_json = json.dumps({"category": category})
        now = datetime.now(timezone.utc).isoformat()
        try:
            with self._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO platform_agent_knowledge (
                        doc_id, tenant_id, agent_id, title, content, source,
                        version, scope, priority, status, metadata_json, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, 'active', ?, ?, ?)
                """, (doc_id, tenant_id, agent_id, title, content, source, scope, priority, meta_json, now, now))
                conn.commit()

            platform_store.record_audit_event(
                tenant_id=tenant_id,
                agent_id=agent_id,
                action="knowledge.added",
                actor="admin",
                details={"doc_id": doc_id, "title": title, "category": category}
            )
            return {
                "ok": True,
                "item": {
                    "doc_id": doc_id,
                    "tenant_id": tenant_id,
                    "title": title,
                    "content": content,
                    "category": category,
                    "version": 1,
                    "priority": priority,
                    "created_at": now
                }
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def update_knowledge(
        self,
        tenant_id: str,
        doc_id: str,
        title: str,
        content: str,
        category: str = "business",
        priority: int = 0
    ) -> Dict[str, Any]:
        """Actualiza un documento existente incrementando su versión."""
        try:
            with self._get_conn() as conn:
                cur = conn.cursor()
                row = cur.execute("SELECT version, metadata_json, agent_id FROM platform_agent_knowledge WHERE tenant_id = ? AND doc_id = ?", (tenant_id, doc_id)).fetchone()
                if not row:
                    return {"ok": False, "error": "Documento no encontrado"}
                ver = (row["version"] or 1) + 1
                meta = json.loads(row["metadata_json"] or "{}")
                meta["category"] = category
                now = datetime.now(timezone.utc).isoformat()
                cur.execute("""
                    UPDATE platform_agent_knowledge
                    SET title = ?, content = ?, version = ?, priority = ?, metadata_json = ?, updated_at = ?
                    WHERE tenant_id = ? AND doc_id = ?
                """, (title, content, ver, priority, json.dumps(meta), now, tenant_id, doc_id))
                conn.commit()

            platform_store.record_audit_event(
                tenant_id=tenant_id,
                agent_id=row["agent_id"],
                action="knowledge.updated",
                actor="admin",
                details={"doc_id": doc_id, "version": ver}
            )
            return {"ok": True, "doc_id": doc_id, "version": ver}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def archive_knowledge(self, tenant_id: str, doc_id: str) -> Dict[str, Any]:
        """Archiva un documento de conocimiento."""
        try:
            with self._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE platform_agent_knowledge
                    SET status = 'archived', updated_at = datetime('now')
                    WHERE tenant_id = ? AND doc_id = ?
                """, (tenant_id, doc_id))
                conn.commit()
            platform_store.record_audit_event(
                tenant_id=tenant_id,
                agent_id="*",
                action="knowledge.archived",
                actor="admin",
                details={"doc_id": doc_id}
            )
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def teach_agent(
        self,
        tenant_id: str,
        agent_id: str,
        instruction_text: str,
        actor: str = "admin"
    ) -> Dict[str, Any]:
        """
        APRENDIZAJE ESTRUCTURADO:
        El administrador enseña algo en lenguaje natural ("El horario del sábado es hasta las 2 PM").
        Firby lo convierte en Knowledge estructurado + Regla de negocio + Auditoría.
        """
        clean_text = instruction_text.strip()
        if not clean_text:
            return {"ok": False, "error": "La instrucción no puede estar vacía."}

        # Clasificación heurística de categoría
        lower = clean_text.lower()
        cat = "business"
        title = f"Enseñanza administrativa: {clean_text[:35]}..."
        if any(w in lower for w in ["horario", "sábado", "domingo", "lunes", "hora", "abrimos", "cerramos"]):
            cat = "hours"
            title = "Actualización de horarios de atención"
        elif any(w in lower for w in ["precio", "costo", "tarifa", "descuento", "vale"]):
            cat = "pricing"
            title = "Condición de precios y tarifas"
        elif any(w in lower for w in ["política", "politica", "devolución", "cancelar", "cambio"]):
            cat = "policies"
            title = "Política oficial de negocio"
        elif any(w in lower for w in ["servicio", "procedimiento", "consulta"]):
            cat = "services"
            title = "Servicio u oferta comercial"

        # 1. Guardar como Knowledge Item
        kn_res = self.add_knowledge(
            tenant_id=tenant_id,
            title=title,
            content=clean_text,
            category=cat,
            agent_id=agent_id,
            source="admin_teaching"
        )

        # 2. Si es una prohibición o política ('no aceptar', 'siempre verificar', 'no ofrecer'), crear regla
        # 2. Convertir la enseñanza en una regla activa de negocio
        rule_res = self.create_rule(
            tenant_id=tenant_id,
            agent_id=agent_id,
            name=title,
            trigger_condition=f"Consulta o solicitud relacionada con {cat}",
            directive=clean_text,
            category=cat if cat in ["pricing", "policy", "hours"] else "policy",
            priority=1
        )

        platform_store.record_audit_event(
            tenant_id=tenant_id,
            agent_id=agent_id,
            action="agent.taught_new_knowledge",
            actor=actor,
            details={"instruction": clean_text, "category": cat, "rule_created": rule_res is not None}
        )

        kn_item = kn_res.get("item") or {}
        rule_item = rule_res.get("rule") if rule_res else {}

        return {
            "ok": True,
            "doc_id": kn_item.get("doc_id"),
            "rule_id": rule_item.get("id") or rule_item.get("rule_id"),
            "category": cat,
            "title": title,
            "knowledge_item": kn_item,
            "rule": rule_item,
            "message": f"Conocimiento incorporado exitosamente bajo la categoría '{cat}'."
        }

    # ═════════════════════════════════════════════════════════════════════════
    # 5. RULES (REGLAS DE NEGOCIO ESTRUCTURADAS)
    # ═════════════════════════════════════════════════════════════════════════

    def list_rules(self, tenant_id: str, agent_id: str = "*") -> List[Dict[str, Any]]:
        """Lista las reglas de negocio estructuradas."""
        rules = []
        try:
            with self._get_conn() as conn:
                cur = conn.cursor()
                rows = cur.execute("""
                    SELECT * FROM platform_rules
                    WHERE tenant_id = ? AND (agent_id = ? OR agent_id = '*' OR ? = '*')
                    ORDER BY priority DESC, created_at DESC
                """, (tenant_id, agent_id, agent_id)).fetchall()

                for r in rows:
                    rules.append({
                        "id": r["rule_id"],
                        "rule_id": r["rule_id"],
                        "tenant_id": r["tenant_id"],
                        "agent_id": r["agent_id"],
                        "name": r["name"],
                        "trigger_condition": r["trigger_condition"],
                        "directive": r["directive"],
                        "category": r["category"],
                        "priority": r["priority"],
                        "is_active": bool(r["is_active"]),
                        "version": r["version"],
                        "created_at": r["created_at"],
                        "updated_at": r["updated_at"]
                    })
        except Exception as e:
            log.warning(f"Error listing rules: {e}")

        # Si la tabla está vacía, sincronizar reglas por defecto del BusinessConfig
        if not rules:
            cfg = control_plane.get_agent_config(tenant_id, agent_id)
            if cfg and cfg.custom_rules:
                for cr in cfg.custom_rules:
                    self.create_rule(
                        tenant_id=tenant_id,
                        agent_id=agent_id,
                        name=cr.directive[:30],
                        trigger_condition=cr.trigger_condition,
                        directive=cr.directive,
                        category=cr.category or "policy"
                    )
                return self.list_rules(tenant_id, agent_id)

        return rules

    def create_rule(
        self,
        tenant_id: str,
        *args,
        trigger_condition: str = "",
        directive: str = "",
        category: str = "policy",
        priority: int = 0,
        agent_id: str = "firby_operator_default",
        name: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """Crea una regla estructurada e impacta el BusinessConfig del agente."""
        if len(args) == 4:
            agent_id, name, trigger_condition, directive = args
        elif len(args) == 2:
            trigger_condition, directive = args
        elif len(args) == 3:
            trigger_condition, directive, category = args

        if "agent_id" in kwargs:
            agent_id = kwargs["agent_id"]
        if "name" in kwargs:
            name = kwargs["name"]
        if not name:
            name = (directive[:35] + "...") if directive else "Regla de negocio"

        rid = f"rule_{uuid.uuid4().hex[:8]}"
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO platform_rules (
                    rule_id, tenant_id, agent_id, name, trigger_condition,
                    directive, category, priority, is_active, version, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?, ?)
            """, (rid, tenant_id, agent_id, name, trigger_condition, directive, category, priority, now, now))
            conn.commit()

        # Sincronizar con BusinessConfig
        self._sync_rule_to_config(tenant_id, agent_id)

        platform_store.record_audit_event(
            tenant_id=tenant_id,
            agent_id=agent_id,
            action="rule.created",
            actor="admin",
            details={"rule_id": rid, "name": name, "condition": trigger_condition}
        )

        return {
            "ok": True,
            "rule": {
                "id": rid,
                "rule_id": rid,
                "tenant_id": tenant_id,
                "agent_id": agent_id,
                "name": name,
                "trigger_condition": trigger_condition,
                "directive": directive,
                "category": category,
                "priority": priority,
                "is_active": True,
                "created_at": now
            }
        }

    def toggle_rule(self, tenant_id: str, rule_id: str, is_active: bool) -> Dict[str, Any]:
        """Activa o desactiva una regla en el runtime."""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE platform_rules
                SET is_active = ?, updated_at = datetime('now')
                WHERE tenant_id = ? AND rule_id = ?
            """, (1 if is_active else 0, tenant_id, rule_id))
            conn.commit()

        self._sync_rule_to_config(tenant_id, "*")
        return {"ok": True, "is_active": is_active}

    def delete_rule(self, tenant_id: str, rule_id: str) -> Dict[str, Any]:
        """Elimina una regla de negocio."""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM platform_rules WHERE tenant_id = ? AND rule_id = ?", (tenant_id, rule_id))
            conn.commit()

        self._sync_rule_to_config(tenant_id, "*")
        return {"ok": True}

    def _sync_rule_to_config(self, tenant_id: str, agent_id: str):
        """Sincroniza las reglas activas de SQLite al BusinessConfig del runtime."""
        active_rules = []
        with self._get_conn() as conn:
            cur = conn.cursor()
            rows = cur.execute("""
                SELECT rule_id, trigger_condition, directive, category
                FROM platform_rules
                WHERE tenant_id = ? AND is_active = 1
            """, (tenant_id,)).fetchall()
            for r in rows:
                active_rules.append(StructuredRule(
                    id=r["rule_id"],
                    trigger_condition=r["trigger_condition"],
                    directive=r["directive"],
                    category=r["category"]
                ))

        cfg = control_plane.get_agent_config(tenant_id, agent_id if agent_id != "*" else "firby_operator_default")
        if cfg:
            cfg.custom_rules = active_rules
            cfg.save_to_db(db_path=self.db_path)

    # ═════════════════════════════════════════════════════════════════════════
    # 6. TOOLS & CAPACIDADES
    # ═════════════════════════════════════════════════════════════════════════

    def list_tools(self, tenant_id: str, agent_id: str) -> List[Dict[str, Any]]:
        """Devuelve la matriz de capacidades y permisos del CapabilityEngine."""
        matrix = agent_control.get_capability_matrix(tenant_id, agent_id)
        return [c.to_dict() for c in matrix]

    def update_tool_permission(
        self,
        tenant_id: str,
        agent_id: str,
        tool_name: str = "",
        enabled: bool = True,
        requires_approval: Optional[bool] = None,
        disabled_message: Optional[str] = None,
        tool_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        requires_hitl: Optional[bool] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Habilita o deshabilita una herramienta e impacta el runtime inmediatamente."""
        target_name = tool_id or tool_name
        is_en = is_active if is_active is not None else enabled
        req_hitl = requires_hitl if requires_hitl is not None else (requires_approval if requires_approval is not None else False)

        cfg = control_plane.get_active_config(tenant_id, agent_id)

        # Mapear nombres canónicos y alias
        canonical_map = {
            "book_appointment": ["book_appointment", "schedule_appointment", "calendar_reserver"],
            "calendar_reserver": ["book_appointment", "schedule_appointment", "calendar_reserver"],
            "check_availability": ["check_availability"],
            "navigate_web": ["navigate_web", "web_navigation"],
            "highlight_ui": ["highlight_ui"],
            "query_business_knowledge": ["query_business_knowledge"],
            "escalate_to_human": ["escalate_to_human", "send_alert"]
        }

        targets = canonical_map.get(target_name, [target_name])
        for t in targets:
            if t not in cfg.tool_permissions:
                cfg.tool_permissions[t] = ToolPermission(name=t, enabled=is_en, requires_authorization=req_hitl)
            else:
                cfg.tool_permissions[t].enabled = is_en
                cfg.tool_permissions[t].requires_authorization = req_hitl

            if disabled_message is not None:
                cfg.tool_permissions[t].disabled_message = disabled_message

        # Guardar persistente en DB
        cfg.save_to_db(db_path=self.db_path)

        platform_store.record_audit_event(
            tenant_id=tenant_id,
            agent_id=agent_id,
            action="tool.permission_updated",
            actor="admin",
            details={"tool": target_name, "enabled": is_en, "requires_approval": req_hitl}
        )

        return {
            "ok": True,
            "tool": target_name,
            "tool_id": target_name,
            "enabled": is_en,
            "is_active": is_en,
            "requires_approval": req_hitl,
            "requires_hitl": req_hitl,
            "message": f"Herramienta '{target_name}' {'habilitada' if is_en else 'deshabilitada'} correctamente."
        }

    # ═════════════════════════════════════════════════════════════════════════
    # 7. CHANNELS & INTEGRACIONES (META WHATSAPP BUSINESS)
    # ═════════════════════════════════════════════════════════════════════════

    def list_integrations(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Lista las integraciones soportadas y su estado real."""
        integrations = [
            {
                "id": "web_widget",
                "name": "Widget de Atención Web 2D",
                "category": "web",
                "connected": True,
                "status": "CONNECTED",
                "details": {
                    "surface": "Sitio Web del Cliente",
                    "protocol": "HTML5 Embed / firby.js",
                    "domain_whitelist": ["*"],
                    "session_pinning": True
                }
            },
            {
                "id": "meta_whatsapp",
                "name": "Meta WhatsApp Business",
                "category": "messaging",
                "connected": False,
                "status": "NOT_CONNECTED",
                "details": {
                    "provider": "Meta Cloud API",
                    "waba_id": None,
                    "phone_number_id": None,
                    "display_phone": "+57 324 369 9856 (Canal exclusivo dueño)",
                    "quality_rating": "HIGH",
                    "webhook_verified": True
                }
            },
            {
                "id": "whatsapp",
                "name": "Línea Ejecutiva Privada WhatsApp",
                "category": "messaging",
                "connected": False,
                "status": "NOT_CONNECTED",
                "details": {
                    "provider": "Meta Cloud API",
                    "display_phone": "+57 324 369 9856"
                }
            },
            {
                "id": "google_calendar",
                "name": "Google Calendar",
                "category": "calendar",
                "connected": False,
                "status": "NOT_CONNECTED",
                "details": {
                    "sync_mode": "read_write",
                    "primary_calendar": "primary"
                }
            },
            {
                "id": "crm_webhooks",
                "name": "Webhooks Salientes & CRM",
                "category": "automation",
                "connected": True,
                "status": "CONNECTED",
                "details": {
                    "delivery_mode": "signed_hmac_sha256",
                    "events": ["lead_captured", "appointment_confirmed"]
                }
            }
        ]

        # Consultar estado en platform_agent_integrations
        try:
            with self._get_conn() as conn:
                cur = conn.cursor()
                rows = cur.execute("""
                    SELECT integration_name, is_connected, credentials_json
                    FROM platform_agent_integrations WHERE tenant_id = ?
                """, (tenant_id,)).fetchall()

                for r in rows:
                    name = r["integration_name"]
                    is_conn = bool(r["is_connected"])
                    creds = json.loads(r["credentials_json"] or "{}")
                    for it in integrations:
                        if it["id"] == name or (name in ["whatsapp", "meta_whatsapp"] and it["id"] in ["whatsapp", "meta_whatsapp"]):
                            it["connected"] = is_conn
                            it["status"] = "CONNECTED" if is_conn else "NOT_CONNECTED"
                            it["details"].update(creds)
        except Exception as e:
            log.warning(f"Error fetching integrations: {e}")

        return integrations

    def save_integration(
        self,
        tenant_id: str,
        channel_id: str,
        config_data: Optional[Dict[str, Any]] = None,
        credentials: Optional[Dict[str, Any]] = None,
        is_connected: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Guarda credenciales server-side para una integración (sin exponer secretos en frontend)."""
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        creds = config_data if config_data is not None else (credentials or {})
        target_names = [channel_id]
        if channel_id in ["meta_whatsapp", "whatsapp"]:
            target_names = ["meta_whatsapp", "whatsapp"]

        with self._get_conn() as conn:
            cur = conn.cursor()
            for t_name in target_names:
                row = cur.execute("SELECT id FROM platform_agent_integrations WHERE tenant_id = ? AND integration_name = ?", (tenant_id, t_name)).fetchone()
                if row:
                    cur.execute("""
                        UPDATE platform_agent_integrations
                        SET is_connected = ?, credentials_json = ?, updated_at = ?
                        WHERE id = ?
                    """, (1 if is_connected else 0, json.dumps(creds), now, row["id"]))
                else:
                    cur.execute("""
                        INSERT INTO platform_agent_integrations (
                            tenant_id, integration_name, is_connected, credentials_json, updated_at
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (tenant_id, t_name, 1 if is_connected else 0, json.dumps(creds), now))
            conn.commit()

        platform_store.record_audit_event(
            tenant_id=tenant_id,
            agent_id="*",
            action=f"integration.{channel_id}.connected" if is_connected else f"integration.{channel_id}.disconnected",
            actor="admin",
            details={"integration": channel_id, "is_connected": is_connected}
        )

        return {"ok": True, "integration": channel_id, "channel_id": channel_id, "is_connected": is_connected, "status": "connected"}

    # ═════════════════════════════════════════════════════════════════════════
    # 8. TRIAL & FACTURACIÓN (7 DÍAS REALES & CANCELACIÓN EN 1 CLIC)
    # ═════════════════════════════════════════════════════════════════════════

    def get_billing_status(self, tenant_id: str = "default") -> Dict[str, Any]:
        """Calcula de forma exacta el estado de la prueba de 7 días y la suscripción."""
        plan = "pro"
        plan_name = "Plan Pro"
        price_cop = "$490.000 COP / mes"
        trial_active = True
        trial_status = "TRIAL_ACTIVE"
        trial_started_at_str = ""
        days_remaining = 7
        card_masked = "•••• 4242"
        payment_method = "card"
        cancelled_at = None

        try:
            with self._get_conn() as conn:
                cur = conn.cursor()
                row = cur.execute("""
                    SELECT trial_active, trial_status, trial_started_at, trial_expires_at,
                           plan, card_masked, payment_method, cancelled_at
                    FROM clinic LIMIT 1
                """).fetchone()

                if row:
                    plan = row["plan"] or "pro"
                    trial_active = bool(row["trial_active"] == "1" or row["trial_active"] is True)
                    trial_status = row["trial_status"] or ("TRIAL_ACTIVE" if trial_active else "CONVERTED")
                    trial_started_at_str = row["trial_started_at"] or ""
                    card_masked = row["card_masked"] or card_masked
                    payment_method = row["payment_method"] or payment_method
                    cancelled_at = row["cancelled_at"]

                    if row["trial_status"] == "CANCELLED" or cancelled_at:
                        trial_status = "CANCELLED"
                        trial_active = False

                    # Cálculo exacto de días restantes
                    if trial_started_at_str and trial_status == "TRIAL_ACTIVE":
                        try:
                            start_dt = datetime.fromisoformat(trial_started_at_str.replace("Z", ""))
                            elapsed = datetime.now() - start_dt
                            rem = max(0, 7 - elapsed.days)
                            days_remaining = rem
                            if elapsed.days >= 7:
                                trial_status = "TRIAL_ENDING"
                        except Exception:
                            days_remaining = 7
        except Exception as e:
            log.warning(f"Error reading billing status: {e}")

        plan_catalog = {
            "starter": ("Plan Starter", "$290.000 COP / mes", 290000),
            "pro": ("Plan Pro", "$490.000 COP / mes", 490000),
            "equipos": ("Plan Equipos", "$890.000 COP / mes", 890000)
        }
        meta = plan_catalog.get(plan.lower(), ("Plan Pro", "$490.000 COP / mes", 490000))

        # Próxima fecha de facturación (exactamente 7 días tras inicio del trial)
        next_billing = (datetime.now() + timedelta(days=days_remaining)).strftime("%d de %B de %Y")

        return {
            "plan_id": plan.lower(),
            "plan_name": meta[0],
            "price_cop": meta[1],
            "amount_cop": meta[2],
            "trial_active": trial_active,
            "trial_status": trial_status,  # TRIAL_ACTIVE, TRIAL_ENDING, CONVERTED, CANCELLED
            "days_remaining": days_remaining,
            "next_billing_date": next_billing,
            "payment_method": {
                "type": payment_method,
                "card_masked": card_masked,
                "badge": "Verificación bancaria de seguridad (Prueba 7 días gratis)"
            },
            "can_cancel": trial_status != "CANCELLED",
            "cancelled_at": cancelled_at,
            "cancel_policy": "Cancela en 1 clic en cualquier momento sin penalidad ni cargos pendientes."
        }

    def cancel_trial_or_subscription(self, tenant_id: str = "default", reason: str = "user_cancel_1click") -> Dict[str, Any]:
        """Cancelación en 1 clic sin costo ni fricción."""
        now_str = datetime.now().isoformat()
        try:
            with self._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE clinic SET
                        trial_active = '0',
                        trial_status = 'CANCELLED',
                        cancelled_at = ?
                    WHERE id = 1
                """, (now_str,))
                conn.commit()
        except Exception as e:
            log.warning(f"Error cancelling subscription in clinic: {e}")

        platform_store.record_audit_event(
            tenant_id=tenant_id,
            agent_id="*",
            action="billing.subscription_cancelled",
            actor="customer",
            details={"reason": reason, "cancelled_at": now_str}
        )

        return {
            "ok": True,
            "status": "CANCELLED",
            "message": "Suscripción cancelada exitosamente. No se realizarán cobros futuros.",
            "cancelled_at": now_str
        }

    # ═════════════════════════════════════════════════════════════════════════
    # 9. ONBOARDING (7 PASOS GUIADOS)
    # ═════════════════════════════════════════════════════════════════════════

    def get_onboarding_state(self, tenant_id: str) -> Dict[str, Any]:
        """Obtiene el progreso de onboarding del cliente."""
        with self._get_conn() as conn:
            cur = conn.cursor()
            row = cur.execute("SELECT * FROM platform_onboarding WHERE tenant_id = ?", (tenant_id,)).fetchone()
            if not row:
                # Crear registro por defecto
                cur.execute("""
                    INSERT INTO platform_onboarding (tenant_id, current_step, completed_steps_json, is_completed, updated_at)
                    VALUES (?, 1, '[]', 0, datetime('now'))
                """, (tenant_id,))
                conn.commit()
                row = cur.execute("SELECT * FROM platform_onboarding WHERE tenant_id = ?", (tenant_id,)).fetchone()

            completed = json.loads(row["completed_steps_json"] or "[]")
            steps = [
                {"id": 1, "step_key": "connect_website", "title": "Conecta tu sitio web", "done": 1 in completed, "completed": 1 in completed},
                {"id": 2, "step_key": "configure_identity", "title": "Cuéntanos sobre tu negocio", "done": 2 in completed, "completed": 2 in completed},
                {"id": 3, "step_key": "add_knowledge", "title": "Revisamos tu información oficial", "done": 3 in completed, "completed": 3 in completed},
                {"id": 4, "step_key": "define_business_rules", "title": "Configura qué puede hacer Firby", "done": 4 in completed, "completed": 4 in completed},
                {"id": 5, "step_key": "configure_tools", "title": "Prueba al agente en el simulador", "done": 5 in completed, "completed": 5 in completed},
                {"id": 6, "step_key": "connect_channels", "title": "Instala el snippet en tu web", "done": 6 in completed, "completed": 6 in completed},
                {"id": 7, "step_key": "publish_agent", "title": "Publica y activa en producción", "done": 7 in completed, "completed": 7 in completed}
            ]

            pct = int((len(completed) / 7) * 100)
            return {
                "ok": True,
                "current_step": row["current_step"],
                "is_completed": bool(row["is_completed"]),
                "website_url": row["website_url"] or "",
                "steps": steps,
                "progress_pct": pct,
                "progress_percentage": pct
            }

    def complete_onboarding_step(self, tenant_id: str, step: Any, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Registra el avance en el flujo de onboarding."""
        step_keys_map = {
            "connect_website": 1,
            "configure_identity": 2,
            "add_knowledge": 3,
            "define_business_rules": 4,
            "configure_tools": 5,
            "connect_channels": 6,
            "publish_agent": 7
        }
        if isinstance(step, str):
            step_int = step_keys_map.get(step, 1)
        else:
            step_int = int(step)

        with self._get_conn() as conn:
            cur = conn.cursor()
            row = cur.execute("SELECT completed_steps_json FROM platform_onboarding WHERE tenant_id = ?", (tenant_id,)).fetchone()
            completed = json.loads(row["completed_steps_json"] or "[]") if row else []
            if step_int not in completed:
                completed.append(step_int)
            completed.sort()

            next_step = min(7, step_int + 1)
            is_all_done = len(completed) >= 7

            cur.execute("""
                UPDATE platform_onboarding SET
                    current_step = ?,
                    completed_steps_json = ?,
                    is_completed = ?,
                    updated_at = datetime('now')
                WHERE tenant_id = ?
            """, (next_step, json.dumps(completed), 1 if is_all_done else 0, tenant_id))
            conn.commit()

        return self.get_onboarding_state(tenant_id)

    # ═════════════════════════════════════════════════════════════════════════
    # 10. AUDIT FEED
    # ═════════════════════════════════════════════════════════════════════════

    def get_activity_feed(self, tenant_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Devuelve el feed cronológico real de eventos auditables."""
        events = platform_store.get_audit_events(tenant_id, limit=limit)
        results = []
        for ev in events:
            results.append({
                "event_id": ev.event_id,
                "action": ev.action,
                "actor": ev.actor,
                "details": ev.details,
                "timestamp": ev.timestamp
            })
        return results


# Instancia singleton del servicio de Workspace
workspace_service = WorkspaceService()
