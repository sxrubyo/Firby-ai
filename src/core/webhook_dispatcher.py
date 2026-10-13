# -*- coding: utf-8 -*-
"""
Firby Enterprise Webhook Dispatcher
===================================
Motor de despacho de webhooks salientes criptográficamente firmados con HMAC-SHA256
(estándar Stripe / GitHub / Shopify) para conectar Firby a servidores y backends de clientes.

Permite a cualquier sistema del cliente (Node.js, Python, Laravel, n8n, Zapier, CRM)
recibir eventos en tiempo real cuando el operador autónomo ejecuta acciones.
"""

from __future__ import annotations
import hmac
import hashlib
import json
import time
import uuid
import logging
import asyncio
import sqlite3
from typing import Dict, Any, Optional
import httpx

log = logging.getLogger("firby.webhook_dispatcher")

DEFAULT_DB_PATH = "/home/ubuntu/firby/firby_ultra.db"


class WebhookDispatcher:
    """Despachador asíncrono y resiliente de eventos hacia servidores de clientes."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS webhook_endpoints (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        org_id TEXT NOT NULL,
                        url TEXT NOT NULL,
                        secret TEXT NOT NULL,
                        events TEXT DEFAULT '["*"]',
                        is_active INTEGER DEFAULT 1,
                        created_at TEXT DEFAULT (datetime('now'))
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_wh_org ON webhook_endpoints(org_id)")

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS webhook_deliveries (
                        id TEXT PRIMARY KEY,
                        org_id TEXT NOT NULL,
                        event TEXT NOT NULL,
                        target_url TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        status_code INTEGER,
                        success INTEGER DEFAULT 0,
                        response_body TEXT,
                        attempt_count INTEGER DEFAULT 1,
                        created_at TEXT DEFAULT (datetime('now')),
                        duration_ms INTEGER
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_wh_del_org ON webhook_deliveries(org_id)")
                conn.commit()
        except Exception as e:
            log.error(f"[WebhookDispatcher] Error inicializando tablas de webhooks: {e}")

    def register_endpoint(self, org_id: str, url: str, secret: Optional[str] = None, events: Optional[list] = None) -> str:
        """Registra o actualiza el webhook endpoint de una organización."""
        if not secret:
            secret = "whsec_" + hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:32]
        events_json = json.dumps(events or ["*"])
        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                cur = conn.cursor()
                # Desactivar endpoints anteriores del mismo org_id
                cur.execute("UPDATE webhook_endpoints SET is_active = 0 WHERE org_id = ?", (org_id,))
                cur.execute("""
                    INSERT INTO webhook_endpoints (org_id, url, secret, events, is_active)
                    VALUES (?, ?, ?, ?, 1)
                """, (org_id, url, secret, events_json))
                conn.commit()
            log.info(f"[WebhookDispatcher] Endpoint registrado para {org_id} -> {url}")
            return secret
        except Exception as e:
            log.error(f"[WebhookDispatcher] Error registrando endpoint: {e}")
            return ""

    def get_active_endpoint(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Recupera la configuración de webhook activa para un org_id."""
        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                row = cur.execute(
                    "SELECT url, secret, events FROM webhook_endpoints WHERE org_id = ? AND is_active = 1 ORDER BY id DESC LIMIT 1",
                    (org_id,)
                ).fetchone()
                if row:
                    return {
                        "url": row["url"],
                        "secret": row["secret"],
                        "events": json.loads(row["events"])
                    }
        except Exception as e:
            log.error(f"[WebhookDispatcher] Error consultando endpoint: {e}")
        return None

    def sign_payload(self, payload_bytes: bytes, secret: str) -> str:
        """Calcula la firma HMAC-SHA256 estándar."""
        mac = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256)
        return f"sha256={mac.hexdigest()}"

    async def dispatch(self, org_id: str, event: str, data: Dict[str, Any]) -> bool:
        """
        Despacha un evento a la URL del cliente de manera asíncrona y no bloqueante.
        Ejecuta reintentos automáticos si el servidor del cliente responde con 5xx.
        """
        endpoint = self.get_active_endpoint(org_id)
        if not endpoint:
            # Si no hay webhook configurado, no es un error
            return False

        url = endpoint["url"]
        secret = endpoint["secret"]
        allowed_events = endpoint["events"]

        if "*" not in allowed_events and event not in allowed_events:
            return False

        delivery_id = f"del_{uuid.uuid4().hex[:16]}"
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        envelope = {
            "id": delivery_id,
            "event": event,
            "org_id": org_id,
            "timestamp": timestamp,
            "data": data
        }

        payload_bytes = json.dumps(envelope, ensure_ascii=False).encode("utf-8")
        signature = self.sign_payload(payload_bytes, secret)

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Firby-Webhook-Engine/1.0",
            "X-Firby-Event": event,
            "X-Firby-Delivery": delivery_id,
            "X-Firby-Signature": signature,
            "X-Firby-Timestamp": timestamp
        }

        # Lanzar tarea en segundo plano para no demorar la respuesta al usuario
        asyncio.create_task(self._send_with_retry(delivery_id, org_id, event, url, payload_bytes, headers))
        return True

    async def _send_with_retry(
        self,
        delivery_id: str,
        org_id: str,
        event: str,
        url: str,
        payload_bytes: bytes,
        headers: Dict[str, str],
        max_attempts: int = 3
    ):
        status_code = None
        response_text = ""
        success = False
        duration_ms = 0

        for attempt in range(1, max_attempts + 1):
            start_t = time.time()
            try:
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                    resp = await client.post(url, content=payload_bytes, headers=headers)
                    duration_ms = int((time.time() - start_t) * 1000)
                    status_code = resp.status_code
                    response_text = resp.text[:1000]

                    if resp.is_success:
                        success = True
                        log.info(f"[WebhookDispatcher] Evento '{event}' entregado a {url} (status: {status_code}) en {duration_ms}ms")
                        break
                    else:
                        log.warning(f"[WebhookDispatcher] Entrega falló para {url} (intento {attempt}/{max_attempts}, status: {status_code})")
            except Exception as e:
                duration_ms = int((time.time() - start_t) * 1000)
                response_text = f"Error de conexión: {str(e)[:500]}"
                log.warning(f"[WebhookDispatcher] Excepción conectando a {url} (intento {attempt}/{max_attempts}): {e}")

            if attempt < max_attempts:
                await asyncio.sleep(2 ** attempt)

        # Registrar entrega en auditoría SQLite
        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT OR REPLACE INTO webhook_deliveries 
                    (id, org_id, event, target_url, payload, status_code, success, response_body, attempt_count, duration_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    delivery_id,
                    org_id,
                    event,
                    url,
                    payload_bytes.decode("utf-8", errors="ignore"),
                    status_code or 0,
                    1 if success else 0,
                    response_text,
                    max_attempts,
                    duration_ms
                ))
                conn.commit()
        except Exception as e:
            log.error(f"[WebhookDispatcher] Error guardando log de auditoría de webhook: {e}")


# Singleton export
webhook_dispatcher = WebhookDispatcher()
