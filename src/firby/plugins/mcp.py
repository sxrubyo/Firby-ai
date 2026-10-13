# -*- coding: utf-8 -*-
"""MCP (Model Context Protocol) plugin system."""
from __future__ import annotations

import logging
import uuid
import httpx
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from typing import Dict, List, Any, Callable

from src.firby.core.proxy import GlobalProxy
from src.firby.core.models import Task, MCPPlugin

log = logging.getLogger("firby.mcp")

db = GlobalProxy("db")
Config = GlobalProxy("Config")


class MCPCapability(Enum):
    """Capacidades de plugins MCP."""
    CALENDAR = "calendar"
    PAYMENTS = "payments"
    REMINDERS = "reminders"
    CRM = "crm"
    ANALYTICS = "analytics"
    NOTIFICATIONS = "notifications"
    INVENTORY = "inventory"
    REVIEWS = "reviews"
    MARKETING = "marketing"


class MCPPluginBase(ABC):
    """Base para plugins MCP."""
    
    @property
    @abstractmethod
    def id(self) -> str:
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> List[MCPCapability]:
        pass
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        pass


class CalendarPlugin(MCPPluginBase):
    """Plugin de calendario integrado."""
    
    @property
    def id(self) -> str:
        return "calendar_v1"
    
    @property
    def name(self) -> str:
        return "Calendario Inteligente"
    
    @property
    def capabilities(self) -> List[MCPCapability]:
        return [MCPCapability.CALENDAR, MCPCapability.REMINDERS]
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        self.config = config
        self.slots_duration = config.get("slot_duration_minutes", 60)
        self.working_hours = config.get("working_hours", {"start": 9, "end": 18})
        return True
    
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action == "get_available_slots":
            return await self._get_available_slots(params)
        elif action == "book_slot":
            return await self._book_slot(params)
        elif action == "cancel_booking":
            return await self._cancel_booking(params)
        elif action == "get_schedule":
            return await self._get_schedule(params)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _get_available_slots(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene slots disponibles."""
        date = params.get("date", datetime.now().strftime("%Y-%m-%d"))
        service = params.get("service")
        
        # Obtener citas existentes
        appointments = db.get_appointments(status="confirmada")
        
        # Generar slots
        slots = []
        start_hour = self.working_hours["start"]
        end_hour = self.working_hours["end"]
        
        for hour in range(start_hour, end_hour):
            for minute in [0, 30]:
                slot_time = f"{hour:02d}:{minute:02d}"
                slot_datetime = f"{date} {slot_time}"
                
                # Verificar si está ocupado
                is_booked = any(
                    apt.get("datetime_slot", "").startswith(slot_datetime)
                    for apt in appointments
                )
                
                if not is_booked:
                    slots.append({
                        "time": slot_time,
                        "datetime": slot_datetime,
                        "available": True
                    })
        
        return {"date": date, "slots": slots}
    
    async def _book_slot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Reserva un slot."""
        apt_id = db.save_appointment(
            params.get("chat_id", ""),
            {
                "patient_name": params.get("name", ""),
                "patient_phone": params.get("phone", ""),
                "service": params.get("service", ""),
                "datetime_slot": params.get("datetime", ""),
                "notes": params.get("notes", "")
            }
        )
        return {"success": True, "appointment_id": apt_id}
    
    async def _cancel_booking(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancela una reserva."""
        apt_id = params.get("appointment_id")
        reason = params.get("reason", "")
        
        db.update_appointment(
            apt_id,
            status="cancelada",
            cancellation_reason=reason,
            cancelled_at=datetime.now().isoformat()
        )
        
        return {"success": True}
    
    async def _get_schedule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene agenda del día."""
        date = params.get("date", datetime.now().strftime("%Y-%m-%d"))
        
        appointments = db.get_appointments()
        day_appointments = [
            apt for apt in appointments
            if apt.get("datetime_slot", "").startswith(date)
            and apt.get("status") != "cancelada"
        ]
        
        return {"date": date, "appointments": day_appointments}
    
    async def health_check(self) -> bool:
        return True


class NotificationsPlugin(MCPPluginBase):
    """Plugin de notificaciones."""
    
    @property
    def id(self) -> str:
        return "notifications_v1"
    
    @property
    def name(self) -> str:
        return "Notificaciones Inteligentes"
    
    @property
    def capabilities(self) -> List[MCPCapability]:
        return [MCPCapability.NOTIFICATIONS, MCPCapability.REMINDERS]
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        self.config = config
        self.telegram_token = Config.TELEGRAM_TOKEN
        return bool(self.telegram_token)
    
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action == "send_notification":
            return await self._send_notification(params)
        elif action == "schedule_reminder":
            return await self._schedule_reminder(params)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _send_notification(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Envía notificación."""
        chat_id = params.get("chat_id")
        message = params.get("message")
        
        if not chat_id or not message:
            return {"error": "chat_id y message requeridos"}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                f"https://api.telegram.org/bot{self.telegram_token}/sendMessage",
                json={"chat_id": chat_id, "text": message}
            )
        
        return {"success": True}
    
    async def _schedule_reminder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Programa recordatorio."""
        task = Task(
            id=str(uuid.uuid4()),
            type="reminder",
            priority=5,
            status="pending",
            data={
                "chat_id": params.get("chat_id"),
                "message": params.get("message"),
                "appointment_id": params.get("appointment_id")
            },
            created_at=datetime.now(),
            scheduled_for=datetime.fromisoformat(params.get("scheduled_for")),
            completed_at=None,
            result=None,
            retries=0
        )
        
        db.create_task(task)
        
        return {"success": True, "task_id": task.id}
    
    async def health_check(self) -> bool:
        return bool(self.telegram_token)


class MCPManager:
    """Gestor de plugins MCP."""
    
    def __init__(self):
        self.plugins: Dict[str, MCPPluginBase] = {}
        self._builtin_plugins = [
            CalendarPlugin(),
            NotificationsPlugin(),
        ]
    
    async def initialize(self):
        """Inicializa plugins."""
        # Registrar plugins builtin
        for plugin in self._builtin_plugins:
            await self.register_plugin(plugin)
        
        # Cargar plugins de BD
        saved_plugins = db.get_plugins(enabled_only=True)
        for p in saved_plugins:
            if p.id in self.plugins:
                # Aplicar configuración guardada
                await self.plugins[p.id].initialize(p.config)
        
        log.info(f"MCP Manager: {len(self.plugins)} plugins activos")
    
    async def register_plugin(self, plugin: MCPPluginBase, config: Dict[str, Any] = None):
        """Registra un plugin."""
        config = config or {}
        
        if await plugin.initialize(config):
            self.plugins[plugin.id] = plugin
            
            # Guardar en BD
            db.install_plugin(MCPPlugin(
                id=plugin.id,
                name=plugin.name,
                description="",
                version="1.0.0",
                enabled=True,
                config=config,
                capabilities=[c.value for c in plugin.capabilities],
                endpoints={},
                health_status="healthy",
                last_check=datetime.now()
            ))
            
            log.info(f"Plugin registrado: {plugin.name}")
    
    async def execute(self, plugin_id: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta acción en plugin."""
        if plugin_id not in self.plugins:
            return {"error": f"Plugin no encontrado: {plugin_id}"}
        
        try:
            result = await self.plugins[plugin_id].execute(action, params)
            return result
        except Exception as e:
            log.error(f"Plugin error [{plugin_id}]: {e}")
            return {"error": str(e)}
    
    def get_capabilities(self) -> Dict[str, List[str]]:
        """Obtiene capacidades de todos los plugins."""
        caps = {}
        for pid, plugin in self.plugins.items():
            caps[pid] = [c.value for c in plugin.capabilities]
        return caps
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Verifica salud de todos los plugins."""
        results = {}
        for pid, plugin in self.plugins.items():
            try:
                results[pid] = await plugin.health_check()
            except Exception:
                results[pid] = False
        return results

# Instancia global
mcp_manager = MCPManager()

async def init_mcp():
    import src.core.globals as g
    g.mcp_manager = mcp_manager
    await mcp_manager.initialize()
