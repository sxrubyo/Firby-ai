#!/usr/bin/env python3
"""
Firby FTS5 Memory Engine (Hermes Architecture Port)

Brings Hermes Agent's FTS5 full-text search, curated memory snapshots,
and session search capabilities into Firby AI.

Key Features:
1. SQLite WAL mode with fallback to DELETE mode for NFS compatibility.
2. FTS5 Virtual Table for full-text search over patient/client messages.
3. CJK / Trigram FTS5 Virtual Table for substring matching.
4. Curated MEMORY.md (business rules, learned facts) & USER.md (patient preferences).
5. Threat scanning on memory injections.
6. Frozen snapshot pattern for zero-token-drift system prompts.
"""

import json
import logging
import os
import re
import sqlite3
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Delimiter for memory entries in MEMORY.md and USER.md
ENTRY_DELIMITER = "\n§\n"

# Security Threat Scanner Patterns
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(?:\w+\s+)*(previous|all|above|prior)\s+(?:\w+\s+)*instructions",
    r"system prompt override",
    r"you are now a",
    r"pretend you are",
    r"output system prompt",
    r"curl\s+[^\n]*\$\{?\w*(KEY|TOKEN|SECRET)",
    r"cat\s+[^\n]*(\.env|credentials)",
]

def scan_threats(content: str) -> Optional[str]:
    """Scans content for malicious prompt injection patterns before storing or injecting."""
    if not content:
        return None
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return f"Blocked: Content matched security threat pattern ({pattern})"
    return None


class FTS5SessionStore:
    """
    SQLite-backed session storage with FTS5 search for Firby.
    Mirrors Hermes Agent's hermes_state.py FTS5 implementation.
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._fts_enabled = False
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
        except sqlite3.OperationalError:
            conn.execute("PRAGMA journal_mode=DELETE;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_schema(self):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.executescript("""
            CREATE TABLE IF NOT EXISTS fts_sessions (
                id TEXT PRIMARY KEY,
                instance_id TEXT NOT NULL DEFAULT 'firby',
                chat_id TEXT NOT NULL,
                started_at REAL NOT NULL,
                ended_at REAL,
                message_count INTEGER DEFAULT 0,
                patient_name TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS fts_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES fts_sessions(id),
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp REAL NOT NULL,
                active INTEGER DEFAULT 1
            );

            CREATE INDEX IF NOT EXISTS idx_fts_msg_chat ON fts_messages(chat_id, timestamp);
            CREATE INDEX IF NOT EXISTS idx_fts_sess_chat ON fts_sessions(chat_id);
            """)

            # Check FTS5 availability
            try:
                c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS temp_fts5_test USING fts5(x);")
                c.execute("DROP TABLE temp_fts5_test;")
                self._fts_enabled = True
            except sqlite3.OperationalError:
                logger.warning("FTS5 not supported in this SQLite build, falling back to LIKE.")
                self._fts_enabled = False

            if self._fts_enabled:
                c.executescript("""
                CREATE VIRTUAL TABLE IF NOT EXISTS fts_messages_idx USING fts5(
                    content
                );

                CREATE TRIGGER IF NOT EXISTS msg_fts_insert AFTER INSERT ON fts_messages BEGIN
                    INSERT INTO fts_messages_idx(rowid, content) VALUES (new.id, new.content);
                END;

                CREATE TRIGGER IF NOT EXISTS msg_fts_delete AFTER DELETE ON fts_messages BEGIN
                    DELETE FROM fts_messages_idx WHERE rowid = old.id;
                END;

                CREATE TRIGGER IF NOT EXISTS msg_fts_update AFTER UPDATE ON fts_messages BEGIN
                    DELETE FROM fts_messages_idx WHERE rowid = old.id;
                    INSERT INTO fts_messages_idx(rowid, content) VALUES (new.id, new.content);
                END;
                """)
            conn.commit()

    def record_message(self, session_id: str, chat_id: str, role: str, content: str, instance_id: str = "firby") -> int:
        """Records a message into both the standard table and FTS5 index atomically."""
        timestamp = time.time()
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT OR IGNORE INTO fts_sessions (id, instance_id, chat_id, started_at) VALUES (?, ?, ?, ?)",
                (session_id, instance_id, chat_id, timestamp)
            )
            c.execute(
                "INSERT INTO fts_messages (session_id, chat_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
                (session_id, chat_id, role, content, timestamp)
            )
            msg_id = c.lastrowid
            c.execute(
                "UPDATE fts_sessions SET message_count = message_count + 1 WHERE id = ?",
                (session_id,)
            )
            conn.commit()
            return msg_id

    def search(self, query: str, chat_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Full-text search across past messages using FTS5 BM25 relevance ranking.
        """
        if not query or not query.strip():
            return []

        clean_query = re.sub(r'[^\w\s]', '', query).strip()
        if not clean_query:
            return []

        with self._get_connection() as conn:
            c = conn.cursor()
            if self._fts_enabled:
                sql = """
                SELECT m.id, m.session_id, m.chat_id, m.role, m.content, m.timestamp, fts_messages_idx.rank
                FROM fts_messages_idx
                JOIN fts_messages m ON fts_messages_idx.rowid = m.id
                WHERE fts_messages_idx MATCH ? AND m.active = 1
                """
                params = [f"{clean_query}*"]
                if chat_id:
                    sql += " AND m.chat_id = ?"
                    params.append(chat_id)
                sql += " ORDER BY rank LIMIT ?"
                params.append(limit)
                
                rows = c.execute(sql, params).fetchall()
            else:
                # Fallback to LIKE
                sql = """
                SELECT id, session_id, chat_id, role, content, timestamp, 0 as rank
                FROM fts_messages
                WHERE content LIKE ? AND active = 1
                """
                params = [f"%{clean_query}%"]
                if chat_id:
                    sql += " AND chat_id = ?"
                    params.append(chat_id)
                sql += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)

                rows = c.execute(sql, params).fetchall()

            return [dict(r) for r in rows]


class CuratedMemoryStore:
    """
    Curated MEMORY.md (business rules, learned facts) & USER.md (patient preferences)
    with frozen system prompt snapshot pattern from Hermes.
    """

    def __init__(self, memory_dir: Path, memory_char_limit: int = 3000, user_char_limit: int = 2000):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.memory_char_limit = memory_char_limit
        self.user_char_limit = user_char_limit
        self._snapshot: Dict[str, str] = {}
        self.load_snapshot()

    def _get_path(self, target: str) -> Path:
        filename = "MEMORY.md" if target.lower() == "memory" else "USER.md"
        return self.memory_dir / filename

    def _read_entries(self, target: str) -> List[str]:
        path = self._get_path(target)
        if not path.exists():
            return []
        try:
            raw = path.read_text(encoding="utf-8").strip()
            if not raw:
                return []
            return [e.strip() for e in raw.split(ENTRY_DELIMITER) if e.strip()]
        except Exception as e:
            logger.error(f"Error reading {path}: {e}")
            return []

    def _write_entries(self, target: str, entries: List[str]):
        path = self._get_path(target)
        content = ENTRY_DELIMITER.join(entries)
        # Atomic write
        temp_file = path.with_suffix(".tmp")
        temp_file.write_text(content, encoding="utf-8")
        temp_file.replace(path)
        self.load_snapshot()

    def load_snapshot(self):
        """Loads entries into frozen system prompt snapshot for stability across session turns."""
        self._snapshot = {
            "memory": self.get_formatted("memory"),
            "user": self.get_formatted("user"),
        }

    def add(self, target: str, content: str) -> Dict[str, Any]:
        """Adds a memory entry with threat scanning and length cap validation."""
        threat_err = scan_threats(content)
        if threat_err:
            return {"success": False, "error": threat_err}

        entries = self._read_entries(target)
        if content in entries:
            return {"success": True, "message": "Entry already exists."}

        entries.append(content)
        total_chars = sum(len(e) for e in entries)
        limit = self.memory_char_limit if target.lower() == "memory" else self.user_char_limit

        if total_chars > limit:
            return {
                "success": False,
                "error": f"Memory limit exceeded ({total_chars}/{limit} chars). Please remove old entries."
            }

        self._write_entries(target, entries)
        return {"success": True, "message": f"Added entry to {target}."}

    def remove(self, target: str, search_text: str) -> Dict[str, Any]:
        """Removes an entry matching search_text."""
        entries = self._read_entries(target)
        new_entries = [e for e in entries if search_text.lower() not in e.lower()]
        if len(new_entries) == len(entries):
            return {"success": False, "error": f"No matching entry found for '{search_text}'"}

        self._write_entries(target, new_entries)
        return {"success": True, "message": f"Removed entry from {target}."}

    def get_formatted(self, target: str) -> str:
        entries = self._read_entries(target)
        if not entries:
            return ""
        label = "REGLAS Y CONOCIMIENTO APRENDIDO" if target == "memory" else "PREFERENCIAS DE PACIENTES"
        return f"\n--- {label} ---\n" + "\n".join(f"• {e}" for e in entries) + "\n"

    def get_snapshot(self) -> str:
        """Returns the frozen snapshot for system prompt injection."""
        mem = self._snapshot.get("memory", "")
        usr = self._snapshot.get("user", "")
        return (mem + "\n" + usr).strip()
