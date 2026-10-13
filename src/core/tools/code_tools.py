# -*- coding: utf-8 -*-
"""
Firby Autonomous Code & Terminal Tools (inspired by OpenCode & SWE-agent).
Provides robust, sandboxed primitives for reading, writing, patching, syntax checking,
and running code and commands.
"""
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from src.core.sandbox.models import ExecutionResult, ExecutionError
from src.core.sandbox.runner import SandboxRunner
from src.core.sandbox.workspace import SandboxWorkspace


class CodeTools:
    """
    Toolkit for autonomous coding, file manipulation, and terminal execution.
    Can operate either within a sandboxed workspace or on allowed directory paths.
    """

    def __init__(
        self,
        workspace: Optional[SandboxWorkspace] = None,
        runner: Optional[SandboxRunner] = None,
    ):
        self.workspace = workspace or SandboxWorkspace()
        self.runner = runner or SandboxRunner(workspace=self.workspace)

    def read_file(
        self,
        file_path: Union[str, Path],
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Reads contents of a file. Supports line slicing (1-indexed).
        """
        try:
            safe_path = self.workspace.resolve_safe_path(file_path)
            if not safe_path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            if safe_path.is_dir():
                return {"success": False, "error": f"Target is a directory, not a file: {file_path}"}

            content = safe_path.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines(keepends=True)
            total_lines = len(lines)

            s = (start_line - 1) if (start_line is not None and start_line > 0) else 0
            e = end_line if (end_line is not None and end_line > 0) else total_lines

            sliced_content = "".join(lines[s:e])
            return {
                "success": True,
                "file_path": str(file_path),
                "total_lines": total_lines,
                "start_line": s + 1,
                "end_line": min(e, total_lines),
                "content": sliced_content,
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def write_file(
        self,
        file_path: Union[str, Path],
        content: str,
        overwrite: bool = True,
    ) -> Dict[str, Any]:
        """
        Creates or updates a file with full content.
        """
        try:
            safe_path = self.workspace.resolve_safe_path(file_path)
            if safe_path.exists() and not overwrite:
                return {
                    "success": False,
                    "error": f"File already exists and overwrite is False: {file_path}",
                }
            self.workspace.write_file(file_path, content)
            return {
                "success": True,
                "file_path": str(file_path),
                "bytes_written": len(content.encode("utf-8")),
                "lines": len(content.splitlines()),
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def patch_file(
        self,
        file_path: Union[str, Path],
        target_content: str,
        replacement_content: str,
    ) -> Dict[str, Any]:
        """
        Replaces a specific block of text in a file (SWE-agent / Aider style surgical edit).
        """
        try:
            read_res = self.read_file(file_path)
            if not read_res["success"]:
                return read_res

            full_content = read_res["content"]
            if target_content not in full_content:
                return {
                    "success": False,
                    "error": f"Target content not found in file {file_path}. Ensure whitespace matches.",
                }

            count = full_content.count(target_content)
            if count > 1:
                return {
                    "success": False,
                    "error": f"Target content occurs {count} times in {file_path}. Must be unique.",
                }

            new_content = full_content.replace(target_content, replacement_content, 1)
            self.workspace.write_file(file_path, new_content)
            return {
                "success": True,
                "file_path": str(file_path),
                "replaced": True,
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def list_dir(self, directory: str = "", recursive: bool = False) -> Dict[str, Any]:
        """
        Lists directory contents.
        """
        try:
            files = self.workspace.list_files(sub_dir=directory, recursive=recursive)
            return {"success": True, "files": files, "count": len(files)}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def check_syntax(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validates the syntax of Python or JS files without executing them.
        """
        try:
            safe_path = self.workspace.resolve_safe_path(file_path)
            if not safe_path.exists():
                return {"success": False, "valid": False, "error": f"File not found: {file_path}"}

            content = safe_path.read_text(encoding="utf-8")
            ext = safe_path.suffix.lower()

            if ext == ".py":
                try:
                    ast.parse(content, filename=str(safe_path))
                    return {"success": True, "valid": True, "language": "python"}
                except SyntaxError as syn_err:
                    return {
                        "success": True,
                        "valid": False,
                        "language": "python",
                        "line": syn_err.lineno,
                        "offset": syn_err.offset,
                        "error": syn_err.msg,
                        "text": syn_err.text,
                    }
            elif ext in (".js", ".mjs"):
                proc = subprocess.run(
                    ["node", "--check", str(safe_path)],
                    capture_output=True,
                    text=True,
                )
                if proc.returncode == 0:
                    return {"success": True, "valid": True, "language": "javascript"}
                return {
                    "success": True,
                    "valid": False,
                    "language": "javascript",
                    "error": proc.stderr.strip(),
                }
            else:
                return {"success": True, "valid": True, "note": f"Syntax check not supported for {ext}"}
        except Exception as exc:
            return {"success": False, "valid": False, "error": str(exc)}

    def execute_script(
        self,
        file_path: Union[str, Path],
        args: Optional[List[str]] = None,
        timeout: Optional[float] = None,
    ) -> ExecutionResult:
        """
        Executes a script inside the isolated sandbox runner.
        """
        safe_path = self.workspace.resolve_safe_path(file_path)
        ext = safe_path.suffix.lower()

        if ext == ".py":
            cmd = [sys.executable, str(safe_path.name)]
        elif ext in (".js", ".mjs"):
            cmd = ["node", str(safe_path.name)]
        elif ext in (".sh", ".bash"):
            cmd = ["bash", str(safe_path.name)]
        else:
            cmd = [str(safe_path.name)]

        if args:
            cmd.extend(args)

        return self.runner.execute_command(
            cmd,
            cwd=safe_path.parent,
            timeout=timeout,
        )

    def run_tests(
        self,
        test_file: str = "test_main.py",
        pytest_args: Optional[List[str]] = None,
        timeout: Optional[float] = 30.0,
    ) -> ExecutionResult:
        """
        Executes pytest inside the sandbox workspace.
        """
        return self.runner.run_python_tests(
            test_file=test_file,
            pytest_args=pytest_args,
            timeout=timeout,
        )
