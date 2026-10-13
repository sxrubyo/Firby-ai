# -*- coding: utf-8 -*-
"""
Firby Verification Evidence Engine (inspired by Hermes-Agent verification_evidence.py).
Ensures tasks cannot be marked COMPLETED without verifiable, concrete proof of success
(e.g., passing tests, verified files, HTTP 200, clean syntax).
"""
from __future__ import annotations

import re
import time
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union

from src.core.sandbox.workspace import SandboxWorkspace


class EvidenceType(str, Enum):
    TEST_PASS = "test_pass"
    FILE_EXISTS = "file_exists"
    SYNTAX_VALID = "syntax_valid"
    HTTP_SUCCESS = "http_success"
    DOM_VERIFIED = "dom_verified"


class InsufficientEvidenceError(Exception):
    """Raised when an agent attempts to complete a task without required verification evidence."""
    pass


@dataclass
class VerificationEvidence:
    id: str
    task_id: str
    evidence_type: EvidenceType
    proof: str
    verified_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "evidence_type": self.evidence_type.value,
            "proof": self.proof,
            "verified_at": self.verified_at,
            "metadata": self.metadata,
        }


class VerificationEvidenceCollector:
    """
    Collects and validates concrete evidence of successful task execution
    before allowing a task to transition to COMPLETED.
    """

    def __init__(self, workspace: Optional[SandboxWorkspace] = None):
        self.workspace = workspace
        self.evidence_ledger: List[VerificationEvidence] = []

    def verify_test_output(self, task_id: str, stdout: str, exit_code: int) -> VerificationEvidence:
        """Verifies that automated tests actually ran and passed with 0 failures."""
        if exit_code != 0:
            raise InsufficientEvidenceError(f"Tests failed with exit code {exit_code}")

        # Look for pytest pass patterns: "X passed" and no "failed"
        passed_match = re.search(r"(\d+)\s+passed", stdout)
        failed_match = re.search(r"(\d+)\s+failed", stdout)

        if not passed_match:
            raise InsufficientEvidenceError("No test pass confirmation found in test output")
        if failed_match and int(failed_match.group(1)) > 0:
            raise InsufficientEvidenceError(f"{failed_match.group(1)} test(s) failed")

        ev = VerificationEvidence(
            id=f"ev_test_{len(self.evidence_ledger) + 1}",
            task_id=task_id,
            evidence_type=EvidenceType.TEST_PASS,
            proof=f"Exit code 0, {passed_match.group(0)}",
            metadata={"passed_count": int(passed_match.group(1))},
        )
        self.evidence_ledger.append(ev)
        return ev

    def verify_file_created(self, task_id: str, file_path: Union[str, Path], min_bytes: int = 1) -> VerificationEvidence:
        """Verifies that a specified file was created and is non-empty."""
        if not self.workspace:
            raise RuntimeError("Workspace required to verify file evidence")

        safe_path = self.workspace.resolve_safe_path(file_path)
        if not safe_path.exists() or not safe_path.is_file():
            raise InsufficientEvidenceError(f"Required artifact file does not exist: {file_path}")

        size = safe_path.stat().st_size
        if size < min_bytes:
            raise InsufficientEvidenceError(f"Artifact file is empty: {file_path} ({size} bytes)")

        ev = VerificationEvidence(
            id=f"ev_file_{len(self.evidence_ledger) + 1}",
            task_id=task_id,
            evidence_type=EvidenceType.FILE_EXISTS,
            proof=f"File {file_path} verified ({size} bytes)",
            metadata={"file_path": str(file_path), "size_bytes": size},
        )
        self.evidence_ledger.append(ev)
        return ev

    def verify_syntax_valid(self, task_id: str, syntax_result: Dict[str, Any]) -> VerificationEvidence:
        """Verifies that syntax checking succeeded with zero syntax errors."""
        if not syntax_result.get("valid", False):
            raise InsufficientEvidenceError(f"Syntax validation failed: {syntax_result.get('error')}")

        ev = VerificationEvidence(
            id=f"ev_syn_{len(self.evidence_ledger) + 1}",
            task_id=task_id,
            evidence_type=EvidenceType.SYNTAX_VALID,
            proof=f"Syntax verified valid for {syntax_result.get('language')}",
            metadata=syntax_result,
        )
        self.evidence_ledger.append(ev)
        return ev

    def get_evidence_for_task(self, task_id: str) -> List[VerificationEvidence]:
        return [e for e in self.evidence_ledger if e.task_id == task_id]

    def has_evidence(self, task_id: str) -> bool:
        return any(e.task_id == task_id for e in self.evidence_ledger)
