# -*- coding: utf-8 -*-
"""
Firby Enterprise Action & Tool Execution Engine
===============================================
Motor declarativo de herramientas y ejecución de acciones empresariales para Firby.
Implementa el estándar OpenAPI / JSON Schema de Function Calling, desacoplando la cognición
del LLM de la ejecución determinística en base de datos, servidores de clientes y WhatsApp.

Inspirado en la arquitectura de 'Supervised Action Graphs' de Sierra AI y Decagon AI.
"""

from __future__ import annotations
import json
import logging
import sqlite3
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Callable
import httpx

from src.core.webhook_dispatcher import webhook_dispatcher

log = logging.getLogger("firby.enterprise_tools")

DEFAULT_DB_PATH = "/home/ubuntu/firby/firby_ultra.db"
WHATSAPP_BRIDGE_URL = "http://localhost:8002/send"
OWNER_PHONE = "573124348669"


class EnterpriseToolRegistry:
    """Registro unificado de herramientas tipadas y auditadas."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable] = {}
        self._register_default_tools()

    def register(self, name: str, description: str, parameters: Dict[str, Any], handler: Callable):
        self._tools[name] = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            }
        }
        self._handlers[name] = handler
        log.info(f"[EnterpriseToolRegistry] Herramienta registrada: {name}")

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return list(self._tools.values())

    async def execute(self, name: str, args: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta validando parámetros y contexto de la organización."""
        if name not in self._handlers:
            return {"success": False, "error": f"Herramienta '{name}' no existe en el registro."}

        handler = self._handlers[name]
        try:
            res = await handler(args=args, context=context, db_path=self.db_path)
            return {"success": True, "result": res}
        except Exception as e:
            log.error(f"[EnterpriseToolRegistry] Error ejecutando '{name}': {e}", exc_info=True)
            return {"success": False, "error": f"Error interno ejecutando {name}: {str(e)}"}

    # ─────────────────────────────────────────────────────────────────────────
    # REGISTRO DE HERRAMIENTAS POR DEFECTO
    # ─────────────────────────────────────────────────────────────────────────

    def _register_default_tools(self):
        # 1. Agendar Cita Atómica
        self.register(
            name="book_appointment",
            description="Agenda una cita confirmada en el sistema, actualiza el perfil del paciente, notifica al dueño por WhatsApp y envía un webhook firmado al servidor del cliente.",
            parameters={
                "type": "object",
                "properties": {
                    "patient_name": {"type": "string", "description": "Nombre completo del paciente o cliente"},
                    "patient_phone": {"type": "string", "description": "Número de WhatsApp o teléfono"},
                    "service": {"type": "string", "description": "Servicio médico o procedimiento solicitado"},
                    "datetime_slot": {"type": "string", "description": "Fecha y hora deseada para la cita (ej. 'Mañana 3:00 PM', '2026-09-17 10:00')"},
                    "notes": {"type": "string", "description": "Observaciones adicionales o preferencias"}
                },
                "required": ["patient_name", "patient_phone", "service", "datetime_slot"]
            },
            handler=self._handle_book_appointment
        )

        # 2. Capturar Prospecto / Lead
        self.register(
            name="capture_lead",
            description="Registra un contacto o prospecto interesado que solicita información detallada sin agendar cita aún, disparando webhook al CRM del cliente.",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nombre del prospecto"},
                    "phone": {"type": "string", "description": "WhatsApp o teléfono de contacto"},
                    "interest": {"type": "string", "description": "Tratamiento o tema de interés"},
                    "notes": {"type": "string", "description": "Detalles o dudas específicas"}
                },
                "required": ["name", "phone"]
            },
            handler=self._handle_capture_lead
        )

        # 3. Solicitud de Visto Bueno al Dueño (Excepciones Comerciales / Políticas)
        self.register(
            name="request_owner_approval",
            description="Envía una consulta ejecutiva por WhatsApp privado al dueño del negocio para solicitar aprobación de excepciones fuera de política (descuentos especiales, sobrecupo, citas extraordinarias).",
            parameters={
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Nombre del cliente"},
                    "customer_phone": {"type": "string", "description": "Teléfono del cliente"},
                    "request_details": {"type": "string", "description": "Explicación exacta de la excepción solicitada"}
                },
                "required": ["customer_name", "request_details"]
            },
            handler=self._handle_request_owner_approval
        )

        # 4. Consultar Disponibilidad de Horarios
        self.register(
            name="check_availability",
            description="Verifica si un día u horario específico tiene citas ya programadas para evitar cruces.",
            parameters={
                "type": "object",
                "properties": {
                    "date_query": {"type": "string", "description": "Fecha a consultar (ej. '2026-09-16' o 'mañana')"}
                },
                "required": ["date_query"]
            },
            handler=self._handle_check_availability
        )

    # ─────────────────────────────────────────────────────────────────────────
    # IMPLEMENTACIONES DE LOS HANDLERS EMPRESARIALES
    # ─────────────────────────────────────────────────────────────────────────

    async def _handle_book_appointment(self, args: Dict[str, Any], context: Dict[str, Any], db_path: str) -> Dict[str, Any]:
        p_name = args.get("patient_name", "").strip()
        p_phone = args.get("patient_phone", "").strip()
        p_service = args.get("service", "").strip()
        p_date = args.get("datetime_slot", "").strip()
        p_notes = args.get("notes", "").strip()
        chat_id = context.get("chat_id", "web_visitor")
        org_id = context.get("org_id", "default")

        now_iso = datetime.now().isoformat()
        apt_id = None

        # 1. Inserción atómica en SQLite
        with sqlite3.connect(db_path, timeout=5.0) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO appointments (chat_id, patient_name, patient_phone, service, datetime_slot, duration_minutes, notes, status, created_at, confirmed_at)
                VALUES (?, ?, ?, ?, ?, 45, ?, 'confirmed', ?, ?)
            """, (chat_id, p_name, p_phone, p_service, p_date, p_notes, now_iso, now_iso))
            apt_id = cur.lastrowid

            # Upsert paciente
            cur.execute("""
                INSERT INTO patients (chat_id, name, phone, visits, last_service, first_seen, last_seen)
                VALUES (?, ?, ?, 1, ?, ?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                    name = CASE WHEN excluded.name != '' THEN excluded.name ELSE patients.name END,
                    phone = CASE WHEN excluded.phone != '' THEN excluded.phone ELSE patients.phone END,
                    visits = patients.visits + 1,
                    last_service = excluded.last_service,
                    last_seen = excluded.last_seen
            """, (chat_id, p_name, p_phone, p_service, now_iso, now_iso))
            conn.commit()

        # 2. Despacho de Webhook al Servidor del Cliente
        await webhook_dispatcher.dispatch(
            org_id=org_id,
            event="appointment.confirmed",
            data={
                "appointment_id": apt_id,
                "patient_name": p_name,
                "patient_phone": p_phone,
                "service": p_service,
                "datetime_slot": p_date,
                "notes": p_notes,
                "created_at": now_iso
            }
        )

        # 3. Notificación Ejecutiva por WhatsApp al Dueño
        try:
            alert_text = (
                f"Nueva cita agendada en la web (#{apt_id})\n\n"
                f"Paciente: {p_name}\n"
                f"Telefono: {p_phone}\n"
                f"Servicio: {p_service}\n"
                f"Horario: {p_date}\n"
                f"Notas: {p_notes if p_notes else 'Sin observaciones'}"
            )
            async with httpx.AsyncClient(timeout=4.0) as client:
                await client.post(WHATSAPP_BRIDGE_URL, json={"to": OWNER_PHONE, "message": alert_text})
                log.info(f"[EnterpriseTools] Alerta WhatsApp enviada para cita #{apt_id}")
        except Exception as e:
            log.warning(f"[EnterpriseTools] Error notificando por WhatsApp al dueño: {e}")

        return {
            "appointment_id": apt_id,
            "status": "confirmed",
            "message": f"Cita confirmada con id #{apt_id} para {p_name} el {p_date}"
        }

    async def _handle_capture_lead(self, args: Dict[str, Any], context: Dict[str, Any], db_path: str) -> Dict[str, Any]:
        name = args.get("name", "").strip()
        phone = args.get("phone", "").strip()
        interest = args.get("interest", "").strip()
        notes = args.get("notes", "").strip()
        chat_id = context.get("chat_id", "web_visitor")
        org_id = context.get("org_id", "default")
        now_iso = datetime.now().isoformat()

        # Guardar en patients
        with sqlite3.connect(db_path, timeout=5.0) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO patients (chat_id, name, phone, preferences, medical_notes, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                    name = excluded.name,
                    phone = excluded.phone,
                    preferences = excluded.preferences,
                    last_seen = excluded.last_seen
            """, (chat_id, name, phone, interest, notes, now_iso, now_iso))
            conn.commit()

        # Despachar webhook saliente
        await webhook_dispatcher.dispatch(
            org_id=org_id,
            event="lead.captured",
            data={
                "name": name,
                "phone": phone,
                "interest": interest,
                "notes": notes,
                "captured_at": now_iso
            }
        )

        return {"status": "success", "message": f"Prospecto {name} registrado correctamente"}

    async def _handle_request_owner_approval(self, args: Dict[str, Any], context: Dict[str, Any], db_path: str) -> Dict[str, Any]:
        customer_name = args.get("customer_name", "").strip()
        customer_phone = args.get("customer_phone", "").strip()
        details = args.get("request_details", "").strip()
        chat_id = context.get("chat_id", "web_visitor")
        org_id = context.get("org_id", "default")

        alert_text = (
            f"Consulta ejecutiva requerida (Excepción en web)\n\n"
            f"Cliente: {customer_name} ({customer_phone})\n"
            f"Solicitud: {details}\n\n"
            f"Por favor responde a este mensaje con 'Aprobar' o 'Rechazar'."
        )

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                await client.post(WHATSAPP_BRIDGE_URL, json={"to": OWNER_PHONE, "message": alert_text})
        except Exception as e:
            log.warning(f"[EnterpriseTools] Error enviando solicitud de visto bueno por WhatsApp: {e}")

        # Despachar webhook
        await webhook_dispatcher.dispatch(
            org_id=org_id,
            event="exception.requested",
            data={
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "details": details,
                "chat_id": chat_id
            }
        )

        return {
            "status": "pending_owner_approval",
            "message": "Solicitud transmitida directamente a gerencia por WhatsApp privado para evaluacion."
        }

    async def _handle_check_availability(self, args: Dict[str, Any], context: Dict[str, Any], db_path: str) -> Dict[str, Any]:
        date_query = args.get("date_query", "").strip()
        try:
            with sqlite3.connect(db_path, timeout=5.0) as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                rows = cur.execute("""
                    SELECT datetime_slot, status FROM appointments
                    WHERE datetime_slot LIKE ? AND status != 'cancelled'
                    LIMIT 10
                """, (f"%{date_query}%",)).fetchall()
                busy_slots = [r["datetime_slot"] for r in rows]
                return {
                    "query": date_query,
                    "busy_slots": busy_slots,
                    "has_conflicts": len(busy_slots) > 0
                }
        except Exception as e:
            return {"query": date_query, "busy_slots": [], "error": str(e)}


# Singleton export
enterprise_tool_registry = EnterpriseToolRegistry()
