# -*- coding: utf-8 -*-
"""
Firby AI — Standardized Tool Contracts & Runtime Interfaces (Bloque 3)
=====================================================================
Definición formal de tipos, schemas JSON, niveles de riesgo, modos de ejecución,
llamadas estructuradas y resultados para la capa de herramientas del Agent Runtime.
Inspirado en OpenAI Agents SDK, PydanticAI y Temporal.
"""

from __future__ import annotations

import time
import uuid
import json
import logging
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Callable, Tuple, Union

from src.core.operator.models import UIAction

log = logging.getLogger("firby.operator.tool_contracts")


class ToolRiskLevel(str, Enum):
    """Nivel de riesgo e impacto operativo de una herramienta."""
    READ_ONLY = "read_only"       # Consulta sin efectos secundarios (búsqueda, disponibilidad, lectura)
    MUTATING = "mutating"         # Modifica estado persistente (agendar cita, ticket, registro)
    CRITICAL = "critical"         # Alto riesgo o irreversible (pago, cancelación masiva, cambio de credenciales)


class ToolExecutionMode(str, Enum):
    """Modo y ubicación de ejecución de la herramienta."""
    SERVER_SYNC = "server_sync"         # Ejecución inmediata síncrona en el backend
    SERVER_ASYNC = "server_async"       # Tarea en background / worker
    CLIENT_UI = "client_ui"             # Ejecución en el frontend (navegación, spotlight, apertura de modal)
    HUMAN_APPROVAL = "human_approval"   # Pausada a la espera de autorización por WhatsApp del dueño


class ToolStatus(str, Enum):
    """Estado unificado y exhaustivo del resultado de una herramienta."""
    SUCCESS = "success"
    VALIDATION_ERROR = "validation_error"
    PERMISSION_DENIED = "permission_denied"
    NOT_FOUND = "not_found"
    TIMEOUT = "timeout"
    EXECUTION_ERROR = "execution_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    CANCELLED = "cancelled"


@dataclass
class ToolCall:
    """Invocación estructurada a una herramienta generada por el Agent Runtime."""
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str = field(default_factory=lambda: f"call_{uuid.uuid4().hex[:8]}")
    run_id: str = ""
    task_id: str = ""
    step_id: int = 1
    idempotency_key: Optional[str] = None
    requested_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_id": self.call_id,
            "run_id": self.run_id,
            "task_id": self.task_id,
            "step_id": self.step_id,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "idempotency_key": self.idempotency_key,
            "requested_at": self.requested_at
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ToolCall:
        return cls(
            tool_name=str(d.get("tool_name") or ""),
            arguments=d.get("arguments") or {},
            call_id=str(d.get("call_id") or f"call_{uuid.uuid4().hex[:8]}"),
            run_id=str(d.get("run_id") or ""),
            task_id=str(d.get("task_id") or ""),
            step_id=int(d.get("step_id") or 1),
            idempotency_key=d.get("idempotency_key"),
            requested_at=float(d.get("requested_at") or time.time())
        )


@dataclass
class ToolResult:
    """Resultado formal y estructurado de la ejecución de una herramienta."""
    tool_name: str
    status: ToolStatus
    success: bool
    call_id: str = ""
    run_id: str = ""
    task_id: str = ""
    step_id: int = 1
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    observations: str = ""
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    completed_at: float = field(default_factory=time.time)
    ui_action: Optional[UIAction] = None
    missing_fields: List[str] = field(default_factory=list)
    verified: bool = False

    @property
    def data(self) -> Dict[str, Any]:
        """Compatibilidad con interfaces legacy que leen .data."""
        return self.result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_id": self.call_id,
            "run_id": self.run_id,
            "task_id": self.task_id,
            "step_id": self.step_id,
            "tool_name": self.tool_name,
            "status": self.status.value if isinstance(self.status, ToolStatus) else str(self.status),
            "success": self.success,
            "result": self.result,
            "data": self.result,  # Legacy alias
            "error": self.error,
            "observations": self.observations,
            "warnings": self.warnings,
            "metadata": self.metadata,
            "duration_ms": round(self.duration_ms, 2),
            "completed_at": self.completed_at,
            "ui_action": self.ui_action.to_dict() if self.ui_action else None,
            "missing_fields": self.missing_fields,
            "verified": self.verified
        }


class ToolDefinition:
    """
    Contrato formal de una capacidad en la plataforma Firby.
    Define validación estricta de schema JSON, modo de ejecución y riesgo.
    """

    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        required_params: Optional[List[str]] = None,
        risk_level: ToolRiskLevel = ToolRiskLevel.READ_ONLY,
        execution_mode: ToolExecutionMode = ToolExecutionMode.SERVER_SYNC,
        timeout_sec: float = 10.0,
        idempotent: bool = False,
        handler: Optional[Callable[..., ToolResult]] = None
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.required_params = required_params or []
        self.risk_level = risk_level
        self.execution_mode = execution_mode
        self.timeout_sec = timeout_sec
        self.idempotent = idempotent
        self.handler = handler

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """Alias para compatibilidad con código que espera parameters_schema."""
        return self.input_schema

    def validate_arguments(self, args: Dict[str, Any]) -> Tuple[bool, Optional[str], List[str]]:
        """
        Valida tipos, campos requeridos y restricciones del schema JSON.
        Retorna (is_valid, error_message, missing_fields).
        """
        if not isinstance(args, dict):
            return False, f"Los argumentos deben ser un objeto JSON/diccionario, recibido: {type(args).__name__}", []

        # 1. Validar campos requeridos
        missing = []
        for req in self.required_params:
            val = args.get(req)
            if val is None or (isinstance(val, str) and not val.strip()):
                missing.append(req)

        if missing:
            return False, f"Faltan parámetros requeridos: {', '.join(missing)}", missing

        # 2. Validar tipos de acuerdo al schema de propiedades
        properties = self.input_schema.get("properties", {})
        for param_name, param_spec in properties.items():
            if param_name in args:
                val = args[param_name]
                expected_type = param_spec.get("type")
                if expected_type and val is not None:
                    if expected_type == "string" and not isinstance(val, str):
                        return False, f"Parámetro '{param_name}' debe ser string, recibido: {type(val).__name__}", []
                    elif expected_type == "integer" and (not isinstance(val, int) or isinstance(val, bool)):
                        return False, f"Parámetro '{param_name}' debe ser integer, recibido: {type(val).__name__}", []
                    elif expected_type == "number" and not isinstance(val, (int, float)):
                        return False, f"Parámetro '{param_name}' debe ser number, recibido: {type(val).__name__}", []
                    elif expected_type == "boolean" and not isinstance(val, bool):
                        return False, f"Parámetro '{param_name}' debe ser boolean, recibido: {type(val).__name__}", []
                    elif expected_type == "array" and not isinstance(val, list):
                        return False, f"Parámetro '{param_name}' debe ser array, recibido: {type(val).__name__}", []
                    elif expected_type == "object" and not isinstance(val, dict):
                        return False, f"Parámetro '{param_name}' debe ser object, recibido: {type(val).__name__}", []

        return True, None, []

    def to_function_declaration(self) -> Dict[str, Any]:
        """Convierte la definición a estándar OpenAPI / Gemini Function Declaration."""
        properties = {}
        for p_name, p_spec in self.input_schema.get("properties", {}).items():
            properties[p_name] = {
                "type": p_spec.get("type", "string"),
                "description": p_spec.get("description", "")
            }

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": self.required_params
            }
        }
