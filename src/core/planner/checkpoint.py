# -*- coding: utf-8 -*-
"""
Firby Workflow Checkpoint Manager (inspired by DeerFlow long workflow checkpoints).
Persists task DAG snapshots, artifact indexes, and notebooks to SQLite for interruption recovery.
"""
from __future__ import annotations

import json
import logging
import sqlite3
import time
import uuid
from typing import Dict, Any, List, Optional

from .task_graph import TaskGraph, TaskNode, TaskStatus
from .task_notebook import TaskNotebook

logger = logging.getLogger("firby.planner.checkpoint")


class WorkflowCheckpointManager:
    """
    Manages snapshotting and restoration of long-running agent workflows.
    Enables pause, recovery after reboot, and backtracking.
    """

    def __init__(self, db_path: str = "/home/ubuntu/firby/firby_ultra.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS workflow_checkpoints (
                        checkpoint_id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        goal TEXT NOT NULL,
                        task_count INTEGER NOT NULL,
                        completed_count INTEGER NOT NULL,
                        graph_json TEXT NOT NULL,
                        notebook_json TEXT,
                        artifacts_json TEXT,
                        created_at REAL NOT NULL,
                        timestamp TEXT DEFAULT (datetime('now'))
                    )
                """)
                conn.commit()
        except Exception as exc:
            logger.warning(f"Failed to initialize checkpoint database: {exc}")

    def save_checkpoint(
        self,
        session_id: str,
        graph: TaskGraph,
        notebook: Optional[TaskNotebook] = None,
        artifacts: Optional[List[str]] = None,
    ) -> str:
        """Saves an atomic checkpoint of the workflow."""
        cid = f"chk_{uuid.uuid4().hex[:10]}"
        completed_count = sum(1 for t in graph.tasks.values() if t.status == TaskStatus.COMPLETED)
        now = time.time()

        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO workflow_checkpoints (
                        checkpoint_id, session_id, goal, task_count, completed_count,
                        graph_json, notebook_json, artifacts_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cid,
                    session_id,
                    graph.goal,
                    len(graph.tasks),
                    completed_count,
                    json.dumps(graph.to_dict()),
                    json.dumps(notebook.to_dict()) if notebook else None,
                    json.dumps(artifacts or []),
                    now,
                ))
                conn.commit()
        except Exception as exc:
            logger.error(f"Failed to save checkpoint: {exc}")
        return cid

    def restore_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Loads a checkpoint and restores the TaskGraph and TaskNotebook."""
        try:
            with sqlite3.connect(self.db_path, timeout=3.0) as conn:
                cur = conn.cursor()
                row = cur.execute("""
                    SELECT session_id, goal, graph_json, notebook_json, artifacts_json
                    FROM workflow_checkpoints
                    WHERE checkpoint_id = ?
                """, (checkpoint_id,)).fetchone()
                if not row:
                    return None

                session_id, goal, graph_json, notebook_json, artifacts_json = row
                graph_data = json.loads(graph_json)

                # Reconstruct TaskGraph
                graph = TaskGraph(goal=goal)
                for td in graph_data.get("tasks", []):
                    node = TaskNode.from_dict(td)
                    graph.tasks[node.id] = node

                # Reconstruct Notebook
                notebook = TaskNotebook()
                if notebook_json:
                    nb_data = json.loads(notebook_json)
                    for k, nd in nb_data.get("notes", {}).items():
                        notebook.set_note(k, nd.get("content", ""), category=nd.get("category", "general"))

                return {
                    "checkpoint_id": checkpoint_id,
                    "session_id": session_id,
                    "goal": goal,
                    "graph": graph,
                    "notebook": notebook,
                    "artifacts": json.loads(artifacts_json) if artifacts_json else [],
                }
        except Exception as exc:
            logger.error(f"Failed to restore checkpoint: {exc}")
            return None

    def list_checkpoints_for_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Lists all checkpoints for a given session."""
        try:
            with sqlite3.connect(self.db_path, timeout=3.0) as conn:
                cur = conn.cursor()
                rows = cur.execute("""
                    SELECT checkpoint_id, goal, task_count, completed_count, created_at, timestamp
                    FROM workflow_checkpoints
                    WHERE session_id = ?
                    ORDER BY created_at DESC
                """, (session_id,)).fetchall()
                return [
                    {
                        "checkpoint_id": r[0],
                        "goal": r[1],
                        "task_count": r[2],
                        "completed_count": r[3],
                        "created_at": r[4],
                        "timestamp": r[5],
                    }
                    for r in rows
                ]
        except Exception:
            return []
