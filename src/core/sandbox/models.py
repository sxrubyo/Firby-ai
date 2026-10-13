# -*- coding: utf-8 -*-
"""
Firby Sandbox Execution Models (inspired by E2B).
Data contracts for isolated code and process execution.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ExecutionError:
    """Represents a runtime error or exception in sandboxed execution."""
    name: str
    value: str
    traceback: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "traceback": self.traceback,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class ExecutionResult:
    """Represents the complete result of executing code or commands in a sandbox."""
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    duration_ms: float = 0.0
    error: Optional[ExecutionError] = None
    artifacts: List[str] = field(default_factory=list)
    timed_out: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        return self.exit_code == 0 and self.error is None and not self.timed_out

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.is_success,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
            "timed_out": self.timed_out,
            "error": self.error.to_dict() if self.error else None,
            "artifacts": self.artifacts,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class SandboxConfig:
    """Configuration and guardrails for sandboxed execution."""
    timeout_seconds: float = 30.0
    max_memory_mb: int = 512
    working_dir: Optional[str] = None
    isolated_env: bool = True
    allowed_env_vars: List[str] = field(default_factory=lambda: [
        "PATH", "LANG", "LC_ALL", "HOME", "USER", "TERM"
    ])
