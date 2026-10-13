# -*- coding: utf-8 -*-
"""
Firby Typed Agent Handoff Protocol (inspired by OpenAI Agents SDK handoffs).
Formalizes delegation of conversation and execution contexts between specialized agents.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class AgentHandoff:
    id: str = field(default_factory=lambda: f"hnd_{uuid.uuid4().hex[:8]}")
    from_agent: str = ""
    to_agent: str = ""
    reason: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "reason": self.reason,
            "context": self.context,
            "artifacts": self.artifacts,
            "created_at": self.created_at,
        }


class HandoffRouter:
    """
    Coordinates and validates agent-to-agent transfers.
    Ensures that handoffs only occur between authorized specialist roles.
    """

    def __init__(self):
        self.history: List[AgentHandoff] = []

    def execute_handoff(
        self,
        from_agent: str,
        to_agent: str,
        reason: str,
        context: Optional[Dict[str, Any]] = None,
        artifacts: Optional[List[str]] = None,
        allowed_targets: Optional[List[str]] = None,
    ) -> AgentHandoff:
        """Executes and records a validated handoff."""
        if allowed_targets and "*" not in allowed_targets and to_agent not in allowed_targets:
            raise PermissionError(
                f"Agent '{from_agent}' is not authorized to hand off to '{to_agent}'. Allowed: {allowed_targets}"
            )

        handoff = AgentHandoff(
            from_agent=from_agent,
            to_agent=to_agent,
            reason=reason,
            context=context or {},
            artifacts=artifacts or [],
        )
        self.history.append(handoff)
        return handoff

    def get_recent_handoffs(self, limit: int = 10) -> List[Dict[str, Any]]:
        return [h.to_dict() for h in self.history[-limit:]]
