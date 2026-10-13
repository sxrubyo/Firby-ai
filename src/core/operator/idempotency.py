# -*- coding: utf-8 -*-
"""
Firby AI — Tool Idempotency Store (Bloque 3)
============================================
Garantiza que acciones mutantes (citas, mensajes, webhooks) no se ejecuten dos veces
ante reintentos de red, clicks repetidos o reconexiones del usuario.
"""

from __future__ import annotations

import time
import json
import hashlib
import threading
import logging
from typing import Dict, Any, Optional, Tuple

from src.core.operator.tool_contracts import ToolResult

log = logging.getLogger("firby.operator.idempotency")


class IdempotencyStore:
    """
    Almacén de idempotencia en memoria con TTL y hashes deterministas de argumentos.
    Protege contra ejecuciones duplicadas de herramientas mutantes.
    """

    def __init__(self, default_ttl_sec: float = 600.0):
        self.default_ttl_sec = default_ttl_sec
        self._lock = threading.Lock()
        # Clave: f"{tenant_id}:{tool_name}:{idempotency_key}" -> (ToolResult, expiration_timestamp)
        self._cache: Dict[str, Tuple[ToolResult, float]] = {}

    def generate_key(self, tenant_id: str, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Genera un hash determinista SHA256 a partir de los argumentos ordenados."""
        try:
            # Filtrar claves no idempotentes como timestamps efímeros si existieran
            clean_args = {k: v for k, v in arguments.items() if k not in ("timestamp", "now", "time_epoch")}
            canonical_json = json.dumps(clean_args, sort_keys=True, ensure_ascii=False)
        except Exception:
            canonical_json = str(arguments)

        raw_str = f"{tenant_id}:{tool_name}:{canonical_json}"
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]

    def get(self, tenant_id: str, tool_name: str, key: str) -> Optional[ToolResult]:
        """Recupera el resultado previo si no ha expirado el TTL."""
        full_key = f"{tenant_id}:{tool_name}:{key}"
        with self._lock:
            if full_key in self._cache:
                result, exp = self._cache[full_key]
                if time.time() < exp:
                    log.info(f"[IdempotencyStore] Cache HIT para {full_key}. Reutilizando resultado.")
                    return result
                else:
                    del self._cache[full_key]
        return None

    def set(self, tenant_id: str, tool_name: str, key: str, result: ToolResult, ttl_sec: Optional[float] = None) -> None:
        """Almacena el resultado de una herramienta bajo su clave de idempotencia."""
        full_key = f"{tenant_id}:{tool_name}:{key}"
        ttl = ttl_sec if ttl_sec is not None else self.default_ttl_sec
        exp = time.time() + ttl
        with self._lock:
            self._cache[full_key] = (result, exp)
            self._cleanup_expired()

    def _cleanup_expired(self) -> None:
        """Elimina entradas expiradas para prevenir acumulación de memoria."""
        now = time.time()
        expired = [k for k, (_, exp) in self._cache.items() if now >= exp]
        for k in expired:
            del self._cache[k]


# Instancia singleton para el runtime
idempotency_store = IdempotencyStore()
