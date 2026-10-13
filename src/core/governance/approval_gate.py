# -*- coding: utf-8 -*-
"""
Firby Human Approval Gate & Risk Evaluator (inspired by Paperclip governance).
Evaluates planned actions for high-risk operations (e.g. destructive commands,
production mutation, database deletion) and intercepts them for explicit authorization.
"""
from __future__ import annotations

import re
import uuid
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class ApprovalRequest:
    id: str
    action_type: str
    target: str
    description: str
    risk_level: str               # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    status: str = "PENDING"       # "PENDING" | "APPROVED" | "REJECTED"
    created_at: float = field(default_factory=time.time)
    resolved_at: Optional[float] = None
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action_type": self.action_type,
            "target": self.target,
            "description": self.description,
            "risk_level": self.risk_level,
            "status": self.status,
            "created_at": self.created_at,
            "resolved_at": self.resolved_at,
            "approved_by": self.approved_by,
            "rejection_reason": self.rejection_reason,
        }


class ApprovalGate:
    """
    Manages risk assessment and gates high-risk operations behind human approval.
    """

    # Critical patterns that require strict human authorization
    CRITICAL_PATTERNS = [
        (r"\brm\s+(-[rfRF]+\s+)?(/|~|\$HOME)", "Destructive file system deletion"),
        (r"\bgit\s+push\s+.*--force", "Forced Git push"),
        (r"\b(drop\s+database|truncate\s+table|drop\s+table)\b", "Destructive SQL database mutation"),
        (r"\b(8003|firbyai\.lat)\b", "Direct production environment modification (strictly restricted to DEV 8001)"),
        (r"\b(shutdown|reboot|poweroff|init\s+0)\b", "System shutdown or reboot attempt"),
    ]

    def __init__(self):
        self.pending_requests: Dict[str, ApprovalRequest] = {}
        self.history: List[ApprovalRequest] = []

    def assess_risk(self, action_type: str, command_or_target: str) -> tuple[str, str]:
        """
        Assesses risk of an action. Returns (risk_level, reason).
        """
        target_str = str(command_or_target).lower()

        for pattern, reason in self.CRITICAL_PATTERNS:
            if re.search(pattern, target_str, re.IGNORECASE):
                return "CRITICAL", f"Detected critical risk: {reason}"

        # Medium risk checks
        if any(w in target_str for w in ["drop", "truncate", "pm2 delete", "kill -9", "rm "]):
            return "HIGH", "Potentially destructive deletion command"

        return "LOW", "Standard operational command"

    def requires_approval(self, action_type: str, command_or_target: str) -> bool:
        """Determines if an action must be paused for human approval."""
        risk, _ = self.assess_risk(action_type, command_or_target)
        return risk in ("HIGH", "CRITICAL")

    def create_request(
        self,
        action_type: str,
        target: str,
        description: str,
    ) -> ApprovalRequest:
        """Creates a pending human approval request."""
        risk, reason = self.assess_risk(action_type, target)
        req_id = f"apr_{uuid.uuid4().hex[:8]}"
        req = ApprovalRequest(
            id=req_id,
            action_type=action_type,
            target=target,
            description=f"{description} ({reason})",
            risk_level=risk,
            status="PENDING",
        )
        self.pending_requests[req_id] = req
        return req

    def approve(self, request_id: str, approver: str = "human_operator") -> bool:
        """Approves a pending request."""
        if request_id not in self.pending_requests:
            return False
        req = self.pending_requests.pop(request_id)
        req.status = "APPROVED"
        req.approved_by = approver
        req.resolved_at = time.time()
        self.history.append(req)
        return True

    def reject(self, request_id: str, reason: str = "Declined by operator") -> bool:
        """Rejects a pending request."""
        if request_id not in self.pending_requests:
            return False
        req = self.pending_requests.pop(request_id)
        req.status = "REJECTED"
        req.rejection_reason = reason
        req.resolved_at = time.time()
        self.history.append(req)
        return True
