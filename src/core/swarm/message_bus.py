# -*- coding: utf-8 -*-
"""
Firby Swarm Message Bus & Inter-Agent Event Engine
==================================================
Canal de mensajería y bus de eventos asíncrono para coordinar la comunicación
entre cientos de agentes autónomos y workers de fondo.
Registra todas las transferencias e interacciones en SQLite para observabilidad completa.
"""

from __future__ import annotations
import asyncio
import json
import logging
import sqlite3
import time
from typing import Dict, Any, List, Optional, Callable
from src.core.swarm.types import AgentMessage, MessageType

log = logging.getLogger("firby.swarm.message_bus")


class SwarmMessageBus:
    """Bus de mensajería distribuido para comunicación entre agentes."""

    def __init__(self, db_path: str = "/home/ubuntu/firby/firby_ultra.db"):
        self.db_path = db_path
        self._subscriptions: Dict[str, List[Callable]] = {}
        self._init_db()

    def _init_db(self):
        """Inicializa las tablas de auditoría y trazas para mensajes entre agentes."""
        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS swarm_inter_agent_messages (
                        id TEXT PRIMARY KEY,
                        conversation_id TEXT,
                        org_id TEXT,
                        sender_id TEXT,
                        recipient_id TEXT,
                        message_type TEXT,
                        payload JSON,
                        created_at TEXT
                    )
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_swarm_msg_conv 
                    ON swarm_inter_agent_messages(conversation_id)
                """)
                conn.commit()
        except Exception as e:
            log.error(f"[SwarmMessageBus] Error inicializando base de datos: {e}")

    def subscribe(self, recipient_pattern: str, handler: Callable):
        """Suscribe un manejador a mensajes dirigidos a un agente o comodín."""
        if recipient_pattern not in self._subscriptions:
            self._subscriptions[recipient_pattern] = []
        self._subscriptions[recipient_pattern].append(handler)

    async def publish(self, message: AgentMessage) -> None:
        """Publica un mensaje en el bus y lo despacha a los suscriptores."""
        # 1. Persistir en SQLite
        try:
            with sqlite3.connect(self.db_path, timeout=3.0) as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO swarm_inter_agent_messages 
                    (id, conversation_id, org_id, sender_id, recipient_id, message_type, payload, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        message.id,
                        message.conversation_id,
                        message.org_id,
                        message.sender_id,
                        message.recipient_id,
                        message.message_type.value if isinstance(message.message_type, MessageType) else str(message.message_type),
                        json.dumps(message.payload, ensure_ascii=False),
                        message.created_at
                    )
                )
                conn.commit()
        except Exception as e:
            log.warning(f"[SwarmMessageBus] Error persistiendo mensaje en SQLite: {e}")

        # 2. Despachar a suscriptores directos y globales ('*')
        handlers = []
        if message.recipient_id in self._subscriptions:
            handlers.extend(self._subscriptions[message.recipient_id])
        if "*" in self._subscriptions:
            handlers.extend(self._subscriptions["*"])

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(message))
                else:
                    handler(message)
            except Exception as e:
                log.error(f"[SwarmMessageBus] Error en handler para {message.recipient_id}: {e}")

    async def dispatch_worker_task(self, worker_id: str, task_name: str, payload: Dict[str, Any], conversation_id: str = "", org_id: str = ""):
        """Despacha una tarea no bloqueante a un agente worker en segundo plano."""
        msg = AgentMessage(
            sender_id="swarm_router",
            recipient_id=worker_id,
            conversation_id=conversation_id,
            org_id=org_id,
            message_type=MessageType.WORKER_TASK,
            payload={"task": task_name, **payload}
        )
        await self.publish(msg)

    def get_conversation_trace(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Recupera la traza completa de mensajes entre agentes para una conversación."""
        try:
            with sqlite3.connect(self.db_path, timeout=3.0) as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                rows = cur.execute(
                    "SELECT * FROM swarm_inter_agent_messages WHERE conversation_id = ? ORDER BY created_at ASC",
                    (conversation_id,)
                ).fetchall()
                result = []
                for r in rows:
                    item = dict(r)
                    if isinstance(item.get("payload"), str):
                        try:
                            item["payload"] = json.loads(item["payload"])
                        except Exception:
                            pass
                    result.append(item)
                return result
        except Exception as e:
            log.error(f"[SwarmMessageBus] Error recuperando traza: {e}")
            return []


# Singleton global
message_bus = SwarmMessageBus()
