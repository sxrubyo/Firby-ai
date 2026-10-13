# -*- coding: utf-8 -*-
"""
Firby Task Graph & DAG Planner (inspired by Paperclip & OpenClaw).
Manages goal decomposition into task nodes, dependency resolution,
atomic task checkouts, and state tracking.
"""
from __future__ import annotations

import json
import uuid
import time
from enum import Enum
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field


class TaskStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class TaskNode:
    """Represents a single atomic step in an autonomous plan."""
    id: str
    title: str
    description: str
    assigned_role: str = "general"       # researcher | browser | coder | verifier
    tool: Optional[str] = None           # Optional specific tool target
    dependencies: List[str] = field(default_factory=list)  # IDs of prerequisites
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3
    requires_human_approval: bool = False
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "assigned_role": self.assigned_role,
            "tool": self.tool,
            "dependencies": self.dependencies,
            "status": self.status.value if isinstance(self.status, TaskStatus) else str(self.status),
            "result": self.result,
            "error": self.error,
            "retries": self.retries,
            "max_retries": self.max_retries,
            "requires_human_approval": self.requires_human_approval,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TaskNode:
        return cls(
            id=data["id"],
            title=data.get("title", ""),
            description=data.get("description", ""),
            assigned_role=data.get("assigned_role", "general"),
            tool=data.get("tool"),
            dependencies=data.get("dependencies", []),
            status=TaskStatus(data.get("status", "pending")),
            result=data.get("result"),
            error=data.get("error"),
            retries=data.get("retries", 0),
            max_retries=data.get("max_retries", 3),
            requires_human_approval=data.get("requires_human_approval", False),
            created_at=data.get("created_at", time.time()),
            completed_at=data.get("completed_at"),
        )


class TaskGraph:
    """
    Directed Acyclic Graph (DAG) of tasks.
    Coordinates dependencies, detects cycles, and provides atomic ready checkouts.
    """

    def __init__(self, goal: str = ""):
        self.goal = goal
        self.tasks: Dict[str, TaskNode] = {}
        self.created_at = time.time()

    def add_task(
        self,
        title: str,
        description: str,
        task_id: Optional[str] = None,
        assigned_role: str = "general",
        tool: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        requires_human_approval: bool = False,
    ) -> TaskNode:
        """Adds a task to the DAG."""
        tid = task_id or f"task_{len(self.tasks) + 1}_{uuid.uuid4().hex[:6]}"
        deps = dependencies or []

        node = TaskNode(
            id=tid,
            title=title,
            description=description,
            assigned_role=assigned_role,
            tool=tool,
            dependencies=deps,
            requires_human_approval=requires_human_approval,
        )
        self.tasks[tid] = node
        self._refresh_readiness()
        return node

    def add_dependency(self, child_id: str, parent_id: str) -> bool:
        """Adds a prerequisite dependency: child depends on parent."""
        if child_id not in self.tasks or parent_id not in self.tasks:
            return False
        if parent_id not in self.tasks[child_id].dependencies:
            self.tasks[child_id].dependencies.append(parent_id)
        
        # Verify no cycle was introduced
        if self.detect_cycles():
            self.tasks[child_id].dependencies.remove(parent_id)
            raise ValueError(f"Cycle detected! Cannot add dependency {parent_id} -> {child_id}")

        self._refresh_readiness()
        return True

    def _refresh_readiness(self) -> None:
        """Updates tasks status from PENDING to READY if dependencies are satisfied."""
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                deps_met = True
                dep_failed = False
                for dep_id in task.dependencies:
                    dep_task = self.tasks.get(dep_id)
                    if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                        deps_met = False
                    if dep_task and dep_task.status == TaskStatus.FAILED:
                        dep_failed = True

                if dep_failed:
                    task.status = TaskStatus.BLOCKED
                    task.error = "Prerequisite dependency failed."
                elif deps_met:
                    if task.requires_human_approval:
                        task.status = TaskStatus.WAITING_APPROVAL
                    else:
                        task.status = TaskStatus.READY

    def get_ready_tasks(self) -> List[TaskNode]:
        """Returns all tasks ready to be executed (checkout pattern)."""
        self._refresh_readiness()
        return [
            task for task in self.tasks.values()
            if task.status == TaskStatus.READY
        ]

    def checkout_task(self) -> Optional[TaskNode]:
        """Atomically checks out the next available ready task."""
        ready = self.get_ready_tasks()
        if not ready:
            return None
        selected = ready[0]
        selected.status = TaskStatus.IN_PROGRESS
        return selected

    def mark_completed(self, task_id: str, result: Any = None) -> bool:
        """Marks a task as successfully completed and cascades readiness."""
        if task_id not in self.tasks:
            return False
        task = self.tasks[task_id]
        task.status = TaskStatus.COMPLETED
        task.result = result
        task.completed_at = time.time()
        self._refresh_readiness()
        return True

    def mark_failed(self, task_id: str, error: str = "") -> bool:
        """Marks a task as failed. Increments retries if under limit."""
        if task_id not in self.tasks:
            return False
        task = self.tasks[task_id]
        task.retries += 1
        task.error = error

        if task.retries < task.max_retries:
            # Put back to READY for retry
            task.status = TaskStatus.READY
        else:
            task.status = TaskStatus.FAILED
            self._refresh_readiness()
        return True

    def approve_task(self, task_id: str) -> bool:
        """Approves a task waiting for human approval."""
        if task_id not in self.tasks:
            return False
        task = self.tasks[task_id]
        if task.status == TaskStatus.WAITING_APPROVAL:
            task.status = TaskStatus.READY
            return True
        return False

    def is_complete(self) -> bool:
        """Returns True if all tasks in the DAG are COMPLETED."""
        if not self.tasks:
            return False
        return all(t.status == TaskStatus.COMPLETED for t in self.tasks.values())

    def has_failed(self) -> bool:
        """Returns True if any task has permanently FAILED or BLOCKED."""
        return any(t.status in (TaskStatus.FAILED, TaskStatus.BLOCKED) for t in self.tasks.values())

    def detect_cycles(self) -> bool:
        """Detects whether the task dependencies contain a cycle using DFS."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def _dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            node = self.tasks.get(node_id)
            if node:
                for dep in node.dependencies:
                    if dep not in visited:
                        if _dfs(dep):
                            return True
                    elif dep in rec_stack:
                        return True

            rec_stack.remove(node_id)
            return False

        for tid in self.tasks:
            if tid not in visited:
                if _dfs(tid):
                    return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "created_at": self.created_at,
            "is_complete": self.is_complete(),
            "has_failed": self.has_failed(),
            "tasks": [t.to_dict() for t in self.tasks.values()],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
