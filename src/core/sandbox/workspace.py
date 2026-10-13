# -*- coding: utf-8 -*-
"""
Firby Sandbox Workspace Manager.
Provides directory isolation, path containment validation, and artifact tracking.
"""
from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path
from typing import List, Optional, Union


class PathTraversalError(Exception):
    """Raised when an operation attempts to escape the sandbox directory."""
    pass


class SandboxWorkspace:
    """
    Manages an isolated directory tree for a sandboxed execution session.
    Prevents path traversal vulnerabilities and tracks created artifacts.
    """

    def __init__(
        self,
        base_dir: Optional[Union[str, Path]] = None,
        session_id: Optional[str] = None,
        auto_cleanup: bool = False,
    ):
        self.session_id = session_id or f"sbx_{uuid.uuid4().hex[:12]}"
        if base_dir:
            self.root_path = Path(base_dir).resolve() / self.session_id
        else:
            default_base = Path("/home/ubuntu/firby/sandboxes")
            self.root_path = default_base / self.session_id

        self.auto_cleanup = auto_cleanup
        self.root_path.mkdir(parents=True, exist_ok=True)

    def resolve_safe_path(self, relative_or_absolute: Union[str, Path]) -> Path:
        """
        Resolves a path ensuring it strictly resides inside the sandbox root directory.
        Raises PathTraversalError if attempting to escape.
        """
        raw_path = Path(relative_or_absolute)
        if raw_path.is_absolute():
            # If absolute, must be child of root_path
            resolved = raw_path.resolve()
        else:
            resolved = (self.root_path / raw_path).resolve()

        # Verify boundary
        try:
            resolved.relative_to(self.root_path)
        except ValueError:
            raise PathTraversalError(
                f"Path traversal detected: {relative_or_absolute} escapes sandbox root {self.root_path}"
            )
        return resolved

    def write_file(self, relative_path: Union[str, Path], content: Union[str, bytes]) -> Path:
        """Writes a file inside the isolated sandbox."""
        safe_path = self.resolve_safe_path(relative_path)
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, str):
            safe_path.write_text(content, encoding="utf-8")
        else:
            safe_path.write_bytes(content)
        return safe_path

    def read_file(self, relative_path: Union[str, Path]) -> str:
        """Reads a text file inside the isolated sandbox."""
        safe_path = self.resolve_safe_path(relative_path)
        if not safe_path.exists() or not safe_path.is_file():
            raise FileNotFoundError(f"File not found in sandbox: {relative_path}")
        return safe_path.read_text(encoding="utf-8")

    def exists(self, relative_path: Union[str, Path]) -> bool:
        """Checks if a file or directory exists in the sandbox."""
        try:
            safe_path = self.resolve_safe_path(relative_path)
            return safe_path.exists()
        except PathTraversalError:
            return False

    def list_files(self, sub_dir: str = "", recursive: bool = True) -> List[str]:
        """Lists relative paths of all files in the sandbox."""
        target_dir = self.resolve_safe_path(sub_dir) if sub_dir else self.root_path
        if not target_dir.exists():
            return []

        files: List[str] = []
        if recursive:
            for p in target_dir.rglob("*"):
                if p.is_file():
                    files.append(str(p.relative_to(self.root_path)))
        else:
            for p in target_dir.iterdir():
                if p.is_file():
                    files.append(str(p.relative_to(self.root_path)))
        return sorted(files)

    def cleanup(self) -> None:
        """Removes the sandbox directory and all its files."""
        if self.root_path.exists():
            shutil.rmtree(self.root_path, ignore_errors=True)

    def __enter__(self) -> "SandboxWorkspace":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.auto_cleanup:
            self.cleanup()
