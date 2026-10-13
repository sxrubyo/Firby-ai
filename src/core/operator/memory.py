# -*- coding: utf-8 -*-
"""
Firby AI — Operator Memory & Task State Management
==================================================
Distingue formalmente entre:
- Conversation Context: Historial de mensajes entre usuario y agente.
- Working State: Intención activa y resolución de referencias ("ese", "el primero", "allá").
- Task State: Estado de la tarea en curso (slots rellenados, última consulta de disponibilidad, cita en proceso).
- Verified Actions: Registro de acciones completadas y verificadas con éxito.
"""

from __future__ import annotations
import re
import json
import sqlite3
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

log = logging.getLogger("firby.operator.memory")


@dataclass
class TaskState:
    """Estado de la tarea activa y memoria de trabajo (Working Memory) del operador."""
    task_id: str = ""
    active_goal: str = ""
    status: str = "PENDING"
    slots: Dict[str, Any] = field(default_factory=dict)
    missing_slots: List[str] = field(default_factory=list)
    active_topic: Optional[str] = None
    previous_topic: Optional[str] = None
    focus_entity: Optional[Dict[str, Any]] = None
    entity_staleness: int = 0
    context_shift_detected: bool = False
    last_tool_name: Optional[str] = None
    last_tool_args: Dict[str, Any] = field(default_factory=dict)
    last_tool_result: Dict[str, Any] = field(default_factory=dict)
    verified_actions: List[Dict[str, Any]] = field(default_factory=list)
    pending_slot_confirmation: Optional[str] = None
    commercial_posture: str = "neutral"  # "neutral", "exploring", "negative", "interested"
    turn_sequence: int = 0
    terms_accepted: bool = False
    consent_pending: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "active_goal": self.active_goal,
            "status": self.status,
            "slots": self.slots,
            "missing_slots": self.missing_slots,
            "active_topic": self.active_topic,
            "previous_topic": self.previous_topic,
            "focus_entity": self.focus_entity,
            "entity_staleness": self.entity_staleness,
            "context_shift_detected": self.context_shift_detected,
            "last_tool_name": self.last_tool_name,
            "last_tool_args": self.last_tool_args,
            "last_tool_result": self.last_tool_result,
            "verified_actions": self.verified_actions,
            "pending_slot_confirmation": self.pending_slot_confirmation,
            "commercial_posture": self.commercial_posture,
            "turn_sequence": self.turn_sequence,
            "terms_accepted": self.terms_accepted,
            "consent_pending": self.consent_pending
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> TaskState:
        if not data:
            return cls()
        return cls(
            task_id=data.get("task_id", ""),
            active_goal=data.get("active_goal", ""),
            status=data.get("status", "PENDING"),
            slots=data.get("slots", {}),
            missing_slots=data.get("missing_slots", []),
            active_topic=data.get("active_topic"),
            previous_topic=data.get("previous_topic"),
            focus_entity=data.get("focus_entity"),
            entity_staleness=int(data.get("entity_staleness", 0)),
            context_shift_detected=bool(data.get("context_shift_detected", False)),
            last_tool_name=data.get("last_tool_name"),
            last_tool_args=data.get("last_tool_args", {}),
            last_tool_result=data.get("last_tool_result", {}),
            verified_actions=data.get("verified_actions", []),
            pending_slot_confirmation=data.get("pending_slot_confirmation"),
            commercial_posture=str(data.get("commercial_posture", "neutral")),
            turn_sequence=int(data.get("turn_sequence", 0)),
            terms_accepted=bool(data.get("terms_accepted", False)),
            consent_pending=bool(data.get("consent_pending", True))
        )

    def set_commercial_posture(self, posture: str):
        """Actualiza la postura comercial (ej: 'exploring', 'negative', 'interested', 'neutral')."""
        self.commercial_posture = posture
        log.info(f"[TaskState] Postura comercial actualizada a: {posture}")

    def is_commercial_inhibited(self) -> bool:
        """Determina si las llamadas a la acción comerciales deben estar inhibidas."""
        return self.commercial_posture in ("negative", "exploring", "inhibited")

    def set_focus_entity(self, entity_type: str, entity_id: str, label: str = ""):
        """Establece la entidad activa en el foco de atención (Working Memory)."""
        self.focus_entity = {
            "type": entity_type,
            "id": entity_id,
            "label": label or entity_id
        }
        self.entity_staleness = 0
        log.info(f"[TaskState] Foco establecido en {entity_type}:{entity_id}")

    def clear_focus_entity(self):
        """Limpia la entidad en foco."""
        self.focus_entity = None
        self.entity_staleness = 0

    def track_topic(self, new_topic: str, is_business: bool = True):
        """Registra la transición temática y detecta cambios bruscos de contexto."""
        if not self.active_topic:
            self.active_topic = new_topic
            self.context_shift_detected = False
            return

        if new_topic != self.active_topic:
            self.previous_topic = self.active_topic
            self.active_topic = new_topic
            # Si se pasa de un tema a otro no relacionado (ej: cálculo general vs negocio)
            if not is_business or self.previous_topic == "calculation_or_fact":
                self.context_shift_detected = True
                self.entity_staleness += 1
                log.info(f"[TaskState] Cambio de contexto detectado: '{self.previous_topic}' -> '{new_topic}'. Staleness={self.entity_staleness}")
            else:
                self.context_shift_detected = False
        else:
            self.context_shift_detected = False

    def detect_ambiguity_on_context_shift(self, user_text: str, current_intent: str) -> Tuple[bool, Optional[str]]:
        """
        Detecta si una pregunta contiene un referente ambiguo tras un cambio de contexto.
        Retorna (is_ambiguous, reason).
        """
        t = user_text.lower().strip()
        is_pronoun_or_short = any(p in t for p in [
            "cuánto cuesta", "cuanto cuesta", "cuánto vale", "cuanto vale",
            "y ese", "y esa", "qué incluye", "que incluye", "precios", "el precio"
        ])

        # Si hubo un cambio de contexto previo (ej. cálculo matemático '3x3') y el usuario pregunta un pronombre/costo desnudo:
        if is_pronoun_or_short and (self.context_shift_detected or self.previous_topic == "calculation_or_fact"):
            # Si el usuario menciona explícitamente el nombre de un plan o entidad, NO es ambiguo:
            if any(p in t for p in ["pro", "starter", "equipos", "plan pro", "plan starter", "plan equipos"]):
                return False, None
            if self.focus_entity:
                return True, f"referent_ambiguous_after_context_shift:{self.focus_entity.get('id')}"
            return True, "referent_ambiguous_no_focus"

        return False, None

    def update_slot(self, key: str, value: Any):
        """Actualiza un slot en el estado de la tarea."""
        self.slots[key] = value

    def get_slot(self, key: str, default: Any = None) -> Any:
        """Obtiene un slot del estado de la tarea."""
        return self.slots.get(key, default)

    def record_tool_execution(self, name: str, args: Optional[Dict[str, Any]] = None, result: Optional[Dict[str, Any]] = None):
        """Registra la ejecución y resultado de una herramienta para uso en turnos posteriores."""
        self.last_tool_name = name
        self.last_tool_args = args or {}
        self.last_tool_result = result or {}
        if result and result.get("success"):
            self.verified_actions.append({
                "tool": name,
                "data": result.get("data", {}),
                "timestamp": result.get("timestamp")
            })

    def resolve_reference(self, user_text: str) -> Dict[str, Any]:
        """
        Resuelve referencias contextuales como 'ese', 'el primero', 'a esa hora', 'en ese horario',
        o preguntas implícitas sobre un plan activo en el foco de atención.
        """
        t = user_text.lower()
        resolved = {}

        # 1. Resolución de planes en memoria si no hubo cambio de contexto
        plan_order = ["starter", "pro", "equipos"]
        if self.focus_entity and self.focus_entity.get("type") == "plan" and not self.context_shift_detected:
            curr_id = self.focus_entity.get("id")
            if any(k in t for k in ["el anterior", "y el anterior", "plan anterior", "el de antes"]):
                if curr_id in plan_order:
                    curr_idx = plan_order.index(curr_id)
                    prev_idx = max(0, curr_idx - 1)
                    resolved["target_plan"] = plan_order[prev_idx]
                    self.set_focus_entity("plan", resolved["target_plan"], f"Plan {resolved['target_plan'].title()}")
                    log.info(f"[TaskState] Referencia 'el anterior' resuelta de {curr_id} a: {resolved['target_plan']}")
            elif any(k in t for k in ["el siguiente", "y el siguiente", "el que le sigue", "el superior"]):
                if curr_id in plan_order:
                    curr_idx = plan_order.index(curr_id)
                    next_idx = min(len(plan_order) - 1, curr_idx + 1)
                    resolved["target_plan"] = plan_order[next_idx]
                    self.set_focus_entity("plan", resolved["target_plan"], f"Plan {resolved['target_plan'].title()}")
                    log.info(f"[TaskState] Referencia 'el siguiente' resuelta de {curr_id} a: {resolved['target_plan']}")
            elif any(k in t for k in ["el otro", "y el otro", "el otro plan"]):
                alt = "starter" if curr_id == "pro" else ("pro" if curr_id == "starter" else "pro")
                resolved["target_plan"] = alt
                self.set_focus_entity("plan", alt, f"Plan {alt.title()}")
                log.info(f"[TaskState] Referencia 'el otro' resuelta de {curr_id} a: {alt}")
            elif any(k in t for k in ["cuánto cuesta", "cuanto cuesta", "cuánto vale", "cuanto vale", "y ese", "ese", "qué incluye", "el precio"]):
                resolved["target_plan"] = curr_id
                log.info(f"[TaskState] Referencia resuelta al plan activo en Working Memory: {resolved['target_plan']}")

        # 2. Si el usuario hace referencia a un horario consultado previamente
        if self.last_tool_name == "check_availability" and self.last_tool_result:
            slots = self.last_tool_result.get("data", {}).get("available_slots", [])
            date_ref = self.last_tool_result.get("data", {}).get("date", "mañana")
            service_ref = self.last_tool_result.get("data", {}).get("service", "")

            if service_ref and not self.slots.get("service"):
                self.slots["service"] = service_ref
                resolved["service"] = service_ref

            if any(k in t for k in ["ese", "el primero", "la primera opción", "el de la mañana", "a esa hora", "ese horario", "reserva ese"]):
                if slots:
                    chosen_slot = slots[0]
                    full_datetime = f"{date_ref} {chosen_slot}"
                    self.slots["datetime_slot"] = full_datetime
                    resolved["datetime_slot"] = full_datetime
                    log.info(f"[TaskState] Referencia de horario '{user_text}' resuelta a: {full_datetime}")

        return resolved


class OperatorMemoryManager:
    """Gestiona la memoria persistente en SQLite y la resolución contextual por sesión."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            import os
            db_path = os.getenv("PLATFORM_DB_PATH") or os.getenv("FIRBY_ULTRA_DB") or "firby_ultra.db"
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS operator_sessions (
                        session_id TEXT PRIMARY KEY,
                        org_id TEXT,
                        tenant_id TEXT DEFAULT 'tenant_demo',
                        agent_id TEXT DEFAULT 'agent_firby_demo',
                        task_state_json TEXT,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Migración no destructiva de columnas
                for col in ["tenant_id TEXT DEFAULT 'tenant_demo'", "agent_id TEXT DEFAULT 'agent_firby_demo'"]:
                    try:
                        cur.execute(f"ALTER TABLE operator_sessions ADD COLUMN {col}")
                    except Exception:
                        pass
                conn.commit()
        except Exception as e:
            log.warning(f"Error inicializando tabla operator_sessions: {e}")

    def load_task_state(
        self,
        session_id: str,
        tenant_id: str = "tenant_demo",
        agent_id: str = "agent_firby_demo"
    ) -> TaskState:
        """Recupera el estado de la tarea garantizando aislamiento por tenant_id y agent_id."""
        clean_tid = (tenant_id or "tenant_demo").strip().lower()
        clean_aid = (agent_id or "agent_firby_demo").strip().lower()
        try:
            from src.core.platform.migration import resolve_tenant_agent_pair
            canon_tid, canon_aid = resolve_tenant_agent_pair(clean_tid)
            clean_tid = canon_tid
            if clean_aid == "agent_firby_demo":
                clean_aid = canon_aid
        except Exception:
            pass

        scoped_key = f"{clean_tid}:{clean_aid}:{session_id}"
        try:
            with sqlite3.connect(self.db_path, timeout=3.0) as conn:
                cur = conn.cursor()
                # 1. Búsqueda por clave compuesta de aislamiento (tenant:agent:session)
                cur.execute("SELECT task_state_json FROM operator_sessions WHERE session_id = ?", (scoped_key,))
                row = cur.fetchone()
                if not row:
                    # 2. Búsqueda por columnas explícitas
                    cur.execute(
                        "SELECT task_state_json FROM operator_sessions WHERE session_id = ? AND tenant_id = ? AND agent_id = ?",
                        (session_id, clean_tid, clean_aid)
                    )
                    row = cur.fetchone()
                if not row:
                    # 3. Fallback de compatibilidad por session_id directo
                    cur.execute("SELECT task_state_json FROM operator_sessions WHERE session_id = ?", (session_id,))
                    row = cur.fetchone()

                if row and row[0]:
                    data = json.loads(row[0])
                    return TaskState.from_dict(data)
        except Exception as e:
            log.warning(f"Error cargando task state: {e}")
        return TaskState()

    def save_task_state(
        self,
        session_id: str,
        org_id_or_state: Any,
        state: Optional[TaskState] = None,
        agent_id: str = "agent_firby_demo"
    ):
        """Persiste el estado de la tarea en SQLite con clave compuesta y scoping por tenant_id y agent_id."""
        if isinstance(org_id_or_state, TaskState):
            actual_state = org_id_or_state
            actual_org_id = "tenant_demo"
        else:
            actual_org_id = str(org_id_or_state or "tenant_demo")
            actual_state = state or TaskState()

        clean_tid = actual_org_id.strip().lower()
        clean_aid = (agent_id or "agent_firby_demo").strip().lower()
        try:
            from src.core.platform.migration import resolve_tenant_agent_pair
            canon_tid, canon_aid = resolve_tenant_agent_pair(clean_tid)
            clean_tid = canon_tid
            if clean_aid == "agent_firby_demo":
                clean_aid = canon_aid
        except Exception:
            pass

        scoped_key = f"{clean_tid}:{clean_aid}:{session_id}"

        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                cur = conn.cursor()
                state_json = json.dumps(actual_state.to_dict())
                cur.execute("""
                    INSERT INTO operator_sessions (session_id, org_id, tenant_id, agent_id, task_state_json, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(session_id) DO UPDATE SET
                        org_id = excluded.org_id,
                        tenant_id = excluded.tenant_id,
                        agent_id = excluded.agent_id,
                        task_state_json = excluded.task_state_json,
                        updated_at = CURRENT_TIMESTAMP
                """, (scoped_key, clean_tid, clean_tid, clean_aid, state_json))
                conn.commit()
        except Exception as e:
            log.warning(f"Error guardando task state: {e}")


operator_memory = OperatorMemoryManager()
