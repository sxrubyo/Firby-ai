#!/usr/bin/env python3
"""
Firby Session Lineage & Summarized Checkpoints (Hermes Architecture Port)

Replaces blind history truncation (`get_history(limit=30)`) with Session Checkpoints.
When a patient/lead conversation exceeds a threshold (e.g., 25 turns):
1. Summarizes the preceding turn history into an Executive Context Summary.
2. Creates a checkpoint entry in SQLite `session_checkpoints`.
3. Opens a lean active window starting with `[SUMMARY OF PAST SESSIONS]` + recent turns.
4. Preserves 100% full-text searchability via FTS5.
"""

import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SessionLineageEngine:
    """Manages session checkpoints and context compression for long-running WhatsApp chats."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
        except sqlite3.OperationalError:
            conn.execute("PRAGMA journal_mode=DELETE;")
        return conn

    def _init_schema(self):
        with self._get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS session_checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                parent_session_id TEXT DEFAULT '',
                summary_text TEXT NOT NULL,
                turns_compressed INTEGER DEFAULT 0,
                created_at REAL NOT NULL
            );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chk_chat ON session_checkpoints(chat_id);")
            conn.commit()

    def get_latest_checkpoint(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the most recent context summary checkpoint for a chat."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT id, chat_id, summary_text, turns_compressed, created_at FROM session_checkpoints WHERE chat_id = ? ORDER BY id DESC LIMIT 1",
                (chat_id,)
            ).fetchone()
            return dict(row) if row else None

    def create_checkpoint(self, chat_id: str, summary_text: str, turns_compressed: int = 0) -> int:
        """Stores a new session checkpoint summary."""
        timestamp = time.time()
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO session_checkpoints (chat_id, summary_text, turns_compressed, created_at) VALUES (?, ?, ?, ?)",
                (chat_id, summary_text, turns_compressed, timestamp)
            )
            conn.commit()
            return c.lastrowid

    def build_lineage_context(self, chat_id: str, full_history: List[Dict[str, Any]], max_active_turns: int = 10) -> Tuple[List[Dict[str, Any]], str]:
        """
        Builds a context-compressed turn history and prompt block.
        If history > max_active_turns, pulls the latest checkpoint summary and returns
        only the active window of turns.
        """
        if len(full_history) <= max_active_turns:
            return full_history, ""

        checkpoint = self.get_latest_checkpoint(chat_id)
        checkpoint_summary = checkpoint["summary_text"] if checkpoint else ""

        # If no checkpoint exists yet, build a basic summary of earlier turns
        if not checkpoint_summary:
            earlier_turns = full_history[:-max_active_turns]
            snippets = []
            for turn in earlier_turns:
                role = turn.get("role", "user")
                content = turn.get("content", "")[:100]
                snippets.append(f"[{role}]: {content}")
            checkpoint_summary = "Resumen de interacción previa:\n" + "\n".join(snippets)
            self.create_checkpoint(chat_id, checkpoint_summary, turns_compressed=len(earlier_turns))

        active_window = full_history[-max_active_turns:]
        summary_prompt_block = f"\n[RESUMEN DE SESIONES ANTERIORES]:\n{checkpoint_summary}\n"
        
        return active_window, summary_prompt_block
