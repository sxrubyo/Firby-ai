# -*- coding: utf-8 -*-
"""
Firby Tracer Engine (inspired by Langfuse).
Coordinates agent trajectory tracing, span hierarchies, error debugging, and telemetry persistence.
"""
from __future__ import annotations

import json
import logging
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Any, List, Optional

from .models import Trace, Span, SpanType, SpanStatus, TokenUsage

logger = logging.getLogger("firby.telemetry.tracer")


class Tracer:
    """
    Central observability engine for Firby 2.0 autonomous agents.
    Provides execution tracing, tool latency recording, and SQLite persistence.
    """

    def __init__(self, db_path: str = "/home/ubuntu/firby/firby_ultra.db"):
        self.db_path = db_path
        self._traces: Dict[str, Trace] = {}
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self) -> None:
        """Initializes the telemetry traces and spans tables in SQLite."""
        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS agent_traces (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        session_id TEXT,
                        status TEXT NOT NULL,
                        start_time REAL NOT NULL,
                        end_time REAL,
                        duration_ms REAL,
                        span_count INTEGER DEFAULT 0,
                        total_tokens INTEGER DEFAULT 0,
                        total_cost_usd REAL DEFAULT 0.0,
                        data_json TEXT,
                        created_at TEXT DEFAULT (datetime('now'))
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS agent_spans (
                        id TEXT PRIMARY KEY,
                        trace_id TEXT NOT NULL,
                        parent_span_id TEXT,
                        name TEXT NOT NULL,
                        span_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        start_time REAL NOT NULL,
                        end_time REAL,
                        duration_ms REAL,
                        input_json TEXT,
                        output_json TEXT,
                        error_message TEXT,
                        created_at TEXT DEFAULT (datetime('now')),
                        FOREIGN KEY (trace_id) REFERENCES agent_traces(id) ON DELETE CASCADE
                    )
                """)
                conn.commit()
        except Exception as exc:
            logger.warning(f"Failed to initialize telemetry database: {exc}")

    def start_trace(self, name: str, session_id: str = "", metadata: Optional[Dict[str, Any]] = None) -> Trace:
        """Creates and registers a new root trace."""
        trace = Trace(name=name, session_id=session_id, metadata=metadata or {})
        with self._lock:
            self._traces[trace.id] = trace
        return trace

    def finish_trace(self, trace: Trace, status: SpanStatus = SpanStatus.OK) -> None:
        """Finishes the trace and persists it to SQLite."""
        trace.finish(status=status)
        self._persist_trace(trace)

    @contextmanager
    def span(
        self,
        trace: Trace,
        name: str,
        span_type: SpanType = SpanType.AGENT_STEP,
        parent_span_id: Optional[str] = None,
        input_data: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Context manager for automatic span timing and error recording."""
        sp = trace.create_span(
            name=name,
            span_type=span_type,
            parent_span_id=parent_span_id,
            input_data=input_data,
            metadata=metadata,
        )
        try:
            yield sp
            if sp.end_time is None:
                sp.finish(status=SpanStatus.OK)
        except Exception as exc:
            sp.finish(status=SpanStatus.ERROR, error=str(exc))
            raise

    def _persist_trace(self, trace: Trace) -> None:
        """Saves trace and child spans to SQLite."""
        try:
            trace_dict = trace.to_dict()
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT OR REPLACE INTO agent_traces (
                        id, name, session_id, status, start_time, end_time,
                        duration_ms, span_count, total_tokens, total_cost_usd, data_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trace.id,
                    trace.name,
                    trace.session_id,
                    trace.status.value,
                    trace.start_time,
                    trace.end_time,
                    trace.duration_ms,
                    len(trace.spans),
                    trace_dict["total_tokens"],
                    trace_dict["total_cost_usd"],
                    json.dumps(trace_dict),
                ))

                for span in trace.spans:
                    cur.execute("""
                        INSERT OR REPLACE INTO agent_spans (
                            id, trace_id, parent_span_id, name, span_type, status,
                            start_time, end_time, duration_ms, input_json, output_json, error_message
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        span.id,
                        span.trace_id,
                        span.parent_span_id,
                        span.name,
                        span.span_type.value,
                        span.status.value,
                        span.start_time,
                        span.end_time,
                        span.duration_ms,
                        json.dumps(span.input_data) if span.input_data is not None else None,
                        json.dumps(span.output_data) if span.output_data is not None else None,
                        span.error_message,
                    ))
                conn.commit()
        except Exception as exc:
            logger.warning(f"Failed to persist trace {trace.id}: {exc}")

    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a trace from memory or SQLite."""
        with self._lock:
            if trace_id in self._traces:
                return self._traces[trace_id].to_dict()

        try:
            with sqlite3.connect(self.db_path, timeout=3.0) as conn:
                cur = conn.cursor()
                row = cur.execute("SELECT data_json FROM agent_traces WHERE id = ?", (trace_id,)).fetchone()
                if row and row[0]:
                    return json.loads(row[0])
        except Exception:
            pass
        return None

    def list_recent_traces(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Lists recent agent execution traces."""
        try:
            with sqlite3.connect(self.db_path, timeout=3.0) as conn:
                cur = conn.cursor()
                rows = cur.execute("""
                    SELECT id, name, session_id, status, duration_ms, span_count, total_tokens, created_at
                    FROM agent_traces
                    ORDER BY rowid DESC
                    LIMIT ?
                """, (limit,)).fetchall()
                return [
                    {
                        "id": r[0],
                        "name": r[1],
                        "session_id": r[2],
                        "status": r[3],
                        "duration_ms": r[4],
                        "span_count": r[5],
                        "total_tokens": r[6],
                        "created_at": r[7],
                    }
                    for r in rows
                ]
        except Exception:
            return []


# Global tracer singleton
global_tracer = Tracer()
