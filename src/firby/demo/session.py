# -*- coding: utf-8 -*-
"""
DemoSessionManager — Módulo especializado para gestión de estado y persistencia de sesiones Demo.
"""
from __future__ import annotations
import time
import logging
from typing import Dict, Any, Optional

log = logging.getLogger("firby.demo.session")

class DemoSessionManager:
    """Maneja el ciclo de vida, TTL y la persistencia en DB de sesiones demo."""

    def __init__(self, db_manager: Any = None):
        self.db = db_manager
        self._sessions: Dict[str, Any] = {}

    def get_session_key(self, chat_id: str, key: str) -> str:
        return f"demo_{chat_id}_{key}"

    def get(self, chat_id: str, key: str, default: Any = None) -> Any:
        sk = self.get_session_key(chat_id, key)
        if sk in self._sessions:
            return self._sessions[sk]
        
        # Fallback a SQLite si no está en RAM
        if self.db and hasattr(self.db, "recall"):
            try:
                val = self.db.recall(sk)
                if val is not None:
                    if val == "true": parsed = True
                    elif val == "false": parsed = False
                    elif val.isdigit(): parsed = int(val)
                    else: parsed = val
                    self._sessions[sk] = parsed
                    return parsed
            except Exception as e:
                log.warning(f"[demo_session] error en recall({sk}): {e}")

        return default

    def set(self, chat_id: str, key: str, value: Any) -> None:
        sk = self.get_session_key(chat_id, key)
        self._sessions[sk] = value
        
        # Persistir en SQLite
        if self.db and hasattr(self.db, "remember"):
            try:
                if value is not None:
                    val_str = "true" if value is True else ("false" if value is False else str(value))
                    self.db.remember(sk, val_str)
                else:
                    with self.db._conn() as c:
                        c.execute("DELETE FROM core_memory WHERE key=?", (sk,))
            except Exception as e:
                log.warning(f"[demo_session] error en remember({sk}): {e}")

    def touch(self, chat_id: str, ttl_seconds: int = 1800) -> bool:
        """Actualiza el timestamp y verifica si la sesión ha expirado."""
        now = time.time()
        last_seen = self.get(chat_id, "ts", 0)
        
        expired = False
        if last_seen and (now - float(last_seen)) > ttl_seconds:
            expired = True
            log.info(f"[demo_session] Sesión de demo expirada para {chat_id} (TTL: {ttl_seconds}s)")

        self.set(chat_id, "ts", now)
        return expired

    def clear(self, chat_id: str) -> None:
        prefix = f"demo_{chat_id}_"
        keys_to_del = [k for k in self._sessions if k.startswith(prefix)]
        for k in keys_to_del:
            self._sessions.pop(k, None)
            if self.db:
                try:
                    with self.db._conn() as c:
                        c.execute("DELETE FROM core_memory WHERE key=?", (k,))
                except Exception:
                    pass
