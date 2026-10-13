# -*- coding: utf-8 -*-
"""
Firby Micro-Agent Spawner (inspired by OpenHands micro-agents & child conversations).
Spawns lightweight, isolated subagents for bounded atomic subtasks.
"""
from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from src.core.sandbox.workspace import SandboxWorkspace
from src.core.governance.budget_guard import BudgetLimits
from .autonomous_loop import AutonomousAgent

logger = logging.getLogger("firby.agent.micro_agent")


class MicroAgent:
    """
    Spawns an isolated subagent in a child workspace directory.
    Executes an atomic sub-task with strict resource bounds,
    then returns its verified output and artifacts to the caller.
    """

    def __init__(self, parent_workspace: SandboxWorkspace, role: str = "coder"):
        self.subagent_id = f"sub_{role}_{uuid.uuid4().hex[:8]}"
        self.role = role
        # Create an isolated child workspace branch
        child_dir = parent_workspace.root_path / "micro_agents" / self.subagent_id
        self.workspace = SandboxWorkspace(base_dir=child_dir.parent, session_id=child_dir.name)
        
        # Tightly bounded micro-budget
        self.budget_limits = BudgetLimits(
            max_steps=8,
            max_duration_seconds=60.0,
            max_tool_calls=12,
        )
        self.agent = AutonomousAgent(
            workspace=self.workspace,
            budget_limits=self.budget_limits,
        )

    def execute_subtask(self, subtask_goal: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Runs the micro-agent on an isolated atomic subtask."""
        logger.info(f"Spawning MicroAgent [{self.subagent_id}] for: {subtask_goal}")
        
        graph = self.agent.plan_goal(subtask_goal)
        if context:
            for task in graph.tasks.values():
                task.context.update(context)

        result = self.agent.run_until_complete(subtask_goal, graph=graph)
        
        return {
            "subagent_id": self.subagent_id,
            "role": self.role,
            "subtask_goal": subtask_goal,
            "status": result.get("status"),
            "duration_seconds": result.get("duration_seconds"),
            "artifacts": self.workspace.list_files(),
            "execution_log": result.get("execution_log", []),
        }
