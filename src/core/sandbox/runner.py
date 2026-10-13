# -*- coding: utf-8 -*-
"""
Firby Isolated Sandbox Runner (inspired by E2B).
Executes code and commands safely with environment scrubbing, timeouts, and structured error diagnostics.
"""
from __future__ import annotations

import os
import re
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, Optional, List, Union

from .models import ExecutionResult, ExecutionError, SandboxConfig
from .workspace import SandboxWorkspace


class SandboxRunner:
    """
    Executes commands and code inside a controlled, isolated sandbox.
    Prevents secret exfiltration by sanitizing environment variables.
    """

    # Keys that must NEVER leak into the sandbox process
    BLOCKED_ENV_PREFIXES = (
        "OPENAI_", "GEMINI_", "GROQ_", "ANTHROPIC_", "AWS_",
        "DATABASE_", "DB_", "SECRET_", "PASSWORD_", "TOKEN_",
        "PRIVATE_", "SSH_", "GITHUB_TOKEN", "GIT_ASKPASS"
    )

    def __init__(
        self,
        workspace: Optional[SandboxWorkspace] = None,
        config: Optional[SandboxConfig] = None
    ):
        self.workspace = workspace or SandboxWorkspace()
        self.config = config or SandboxConfig()

    def _build_safe_env(self, custom_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Builds a sanitized environment dictionary.
        Strips host API keys, tokens, and sensitive database URLs.
        """
        if not self.config.isolated_env:
            base_env = dict(os.environ)
        else:
            base_env = {}
            for key in self.config.allowed_env_vars:
                if key in os.environ:
                    base_env[key] = os.environ[key]

        # Explicitly remove any sensitive variables if they crept in
        for k in list(base_env.keys()):
            for blocked in self.BLOCKED_ENV_PREFIXES:
                if k.upper().startswith(blocked):
                    base_env.pop(k, None)

        # Set sandbox specific standard variables
        base_env["PYTHONUNBUFFERED"] = "1"
        base_env["PYTHONDONTWRITEBYTECODE"] = "1"
        base_env["FIRBY_SANDBOX"] = "1"
        base_env["HOME"] = str(self.workspace.root_path)

        if custom_env:
            for k, v in custom_env.items():
                # Disallow setting blocked keys even from custom_env
                if not any(k.upper().startswith(b) for b in self.BLOCKED_ENV_PREFIXES):
                    base_env[k] = str(v)

        return base_env

    def _parse_error_from_stderr(self, stderr: str) -> Optional[ExecutionError]:
        """
        Extracts structured Python or general runtime error information from stderr.
        """
        if not stderr:
            return None

        # Look for standard Python traceback: "Traceback (most recent call last):"
        if "Traceback (most recent call last):" in stderr:
            tb_match = re.search(
                r"(Traceback \(most recent call last\):[\s\S]+)", stderr
            )
            raw_tb = tb_match.group(1).strip() if tb_match else stderr.strip()
            
            # Find the last line containing the Exception type and message
            last_line = raw_tb.splitlines()[-1]
            if ":" in last_line:
                name, _, value = last_line.partition(":")
                return ExecutionError(
                    name=name.strip(),
                    value=value.strip(),
                    traceback=raw_tb
                )
            return ExecutionError(name="RuntimeError", value=last_line.strip(), traceback=raw_tb)

        # Syntax error
        if "SyntaxError:" in stderr or "IndentationError:" in stderr:
            lines = stderr.strip().splitlines()
            err_line = next((l for l in reversed(lines) if "Error:" in l), lines[-1])
            name, _, value = err_line.partition(":")
            return ExecutionError(name=name.strip(), value=value.strip(), traceback=stderr.strip())

        # General non-zero error indicator
        if "Error:" in stderr or "Exception:" in stderr:
            lines = stderr.strip().splitlines()
            err_line = next((l for l in reversed(lines) if "Error" in l or "Exception" in l), lines[-1])
            name, _, val = err_line.partition(":")
            return ExecutionError(name=name.strip() or "ExecutionFailed", value=val.strip() or err_line, traceback=stderr)

        return None

    def execute_command(
        self,
        command: Union[str, List[str]],
        cwd: Optional[Union[str, Path]] = None,
        timeout: Optional[float] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> ExecutionResult:
        """
        Executes a command inside the sandbox workspace directory.
        """
        start_time = time.perf_counter()
        target_cwd = self.workspace.resolve_safe_path(cwd) if cwd else self.workspace.root_path
        target_cwd.mkdir(parents=True, exist_ok=True)

        exec_env = self._build_safe_env(env)
        actual_timeout = timeout or self.config.timeout_seconds

        shell = isinstance(command, str)

        try:
            proc = subprocess.run(
                command,
                cwd=str(target_cwd),
                env=exec_env,
                capture_output=True,
                text=True,
                shell=shell,
                timeout=actual_timeout,
            )
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            error = None
            if proc.returncode != 0:
                error = self._parse_error_from_stderr(proc.stderr)

            # Discover generated artifacts in sandbox root
            artifacts = self.workspace.list_files()

            return ExecutionResult(
                exit_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                duration_ms=duration_ms,
                error=error,
                artifacts=artifacts,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResult(
                exit_code=-1,
                stdout=exc.stdout or "",
                stderr=exc.stderr or f"Execution timed out after {actual_timeout}s",
                duration_ms=duration_ms,
                error=ExecutionError(
                    name="TimeoutError",
                    value=f"Command exceeded {actual_timeout}s timeout limit",
                    traceback=f"TimeoutExpired: {command}"
                ),
                artifacts=self.workspace.list_files(),
                timed_out=True,
            )
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=str(exc),
                duration_ms=duration_ms,
                error=ExecutionError(
                    name=type(exc).__name__,
                    value=str(exc),
                    traceback=str(exc)
                ),
                artifacts=self.workspace.list_files(),
                timed_out=False,
            )

    def run_python_code(
        self,
        code: str,
        filename: str = "main.py",
        python_bin: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> ExecutionResult:
        """
        Writes Python code to a file in the workspace and executes it in isolation.
        """
        self.workspace.write_file(filename, code)
        py_exec = python_bin or sys.executable
        return self.execute_command(
            [py_exec, filename],
            timeout=timeout,
        )

    def run_python_tests(
        self,
        test_file: str = "test_main.py",
        pytest_args: Optional[List[str]] = None,
        timeout: Optional[float] = None,
    ) -> ExecutionResult:
        """
        Executes pytest on the specified test file within the sandbox.
        """
        py_exec = sys.executable
        cmd = [py_exec, "-m", "pytest", test_file, "-v"]
        if pytest_args:
            cmd.extend(pytest_args)
        return self.execute_command(cmd, timeout=timeout)
