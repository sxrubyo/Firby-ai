# -*- coding: utf-8 -*-
"""
Firby Budget Guard (inspired by Paperclip).
Tracks resource utilization, execution steps, tool invocations, and wall-clock time
to prevent runaway agent loops and cost overruns.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Any, List


class BudgetExceededError(Exception):
    """Raised when an autonomous agent exceeds its allowed resource budget."""
    pass


@dataclass
class BudgetLimits:
    max_steps: int = 30
    max_duration_seconds: float = 300.0
    max_tool_calls: int = 50
    max_retries_per_task: int = 3


@dataclass
class BudgetTracker:
    limits: BudgetLimits = field(default_factory=BudgetLimits)
    steps_taken: int = 0
    tool_calls_taken: int = 0
    start_time: float = field(default_factory=time.time)
    events: List[Dict[str, Any]] = field(default_factory=list)

    def record_step(self, step_name: str = "") -> None:
        """Records an agent step and validates against budget limits."""
        self.steps_taken += 1
        elapsed = time.time() - self.start_time

        self.events.append({
            "type": "step",
            "name": step_name,
            "step_index": self.steps_taken,
            "elapsed_seconds": round(elapsed, 2),
        })

        if self.steps_taken > self.limits.max_steps:
            raise BudgetExceededError(
                f"Agent step limit exceeded: {self.steps_taken} > {self.limits.max_steps}"
            )

        if elapsed > self.limits.max_duration_seconds:
            raise BudgetExceededError(
                f"Agent time budget exceeded: {round(elapsed, 1)}s > {self.limits.max_duration_seconds}s"
            )

    def record_tool_call(self, tool_name: str) -> None:
        """Records a tool invocation and checks limits."""
        self.tool_calls_taken += 1
        elapsed = time.time() - self.start_time

        self.events.append({
            "type": "tool_call",
            "tool": tool_name,
            "call_index": self.tool_calls_taken,
            "elapsed_seconds": round(elapsed, 2),
        })

        if self.tool_calls_taken > self.limits.max_tool_calls:
            raise BudgetExceededError(
                f"Tool invocation limit exceeded: {self.tool_calls_taken} > {self.limits.max_tool_calls}"
            )

    def get_summary(self) -> Dict[str, Any]:
        return {
            "steps_taken": self.steps_taken,
            "max_steps": self.limits.max_steps,
            "tool_calls": self.tool_calls_taken,
            "max_tool_calls": self.limits.max_tool_calls,
            "elapsed_seconds": round(time.time() - self.start_time, 2),
            "max_duration_seconds": self.limits.max_duration_seconds,
        }
