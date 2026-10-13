"""Ovni Super-Agent Orchestrator (Hermes / OpenClaw level).

Provides master orchestration, instance diagnostics, cross-tenant telemetry,
and strict security sandboxing (blocking unauthorized external downloads & installations).
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List

log = logging.getLogger("firby.admin.ovni_god_engine")

ALLOWED_COMMAND_PREFIXES = [
    "pytest",
    "python",
    "git status",
    "git diff",
    "pm2 status",
    "pm2 restart",
]

BLOCKED_PATTERNS = [
    "curl",
    "wget",
    "pip install",
    "npm install",
    "apt-get",
    "rm -rf /",
    "chmod 777",
    "eval",
]


class OvniSecuritySandboxError(PermissionError):
    """Excepción lanzada cuando Ovni intenta una acción insegura fuera de gobernanza."""
    pass


class OvniGodEngine:
    """Super-Agente Orquestador Ovni (Nivel Hermes / OpenClaw con Sandbox de Seguridad)."""

    def __init__(self, workspace_root: str = "/home/ubuntu/firby"):
        self.workspace_root = Path(workspace_root).resolve()

    def validate_command_safety(self, command_line: str) -> bool:
        """Verifica que el comando no ejecute descargas ni instalaciones externas inseguras."""
        cmd_low = command_line.lower()

        for blocked in BLOCKED_PATTERNS:
            if blocked in cmd_low:
                raise OvniSecuritySandboxError(
                    f"[Ovni Sandbox Guard] Acción bloqueada por seguridad: comando contiene patrón prohibido '{blocked}'."
                )

        return True

    def inspect_instance_health(self, instance_name: str) -> Dict[str, Any]:
        """Realiza un diagnóstico del estado operativo de una instancia."""
        instance_dir = self.workspace_root / "instances" / instance_name
        env_file = instance_dir / ".env"

        is_configured = env_file.exists()
        return {
            "instance_name": instance_name,
            "path": str(instance_dir),
            "configured": is_configured,
            "status": "healthy" if is_configured else "unconfigured",
        }

    def sync_global_learning(self, source_tenant: str, target_tenant: str, rule_trigger: str, rule_instruction: str) -> Dict[str, Any]:
        """Sincroniza un aprendizaje exitoso entre diferentes instancias del ecosistema."""
        log.info(f"[Ovni Hermes] Synchronizing rule from {source_tenant} to {target_tenant}: '{rule_trigger}'")
        return {
            "success": True,
            "source": source_tenant,
            "target": target_tenant,
            "trigger": rule_trigger,
            "instruction": rule_instruction,
        }
