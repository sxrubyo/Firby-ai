# -*- coding: utf-8 -*-
"""
Firby Agent Guardrails (inspired by OpenAI Agents SDK guardrail.py).
Pre-flight input validation for tool arguments and post-execution output sanitization.
"""
from __future__ import annotations

import re
import urllib.parse
from typing import Dict, Any, Tuple, Optional


class GuardrailViolationError(Exception):
    """Raised when an input or output fails strict agent guardrails."""
    pass


class AgentGuardrails:
    """
    Enforces security, policy, and brand safety checks on tool invocations and model responses.
    """

    # Disallowed patterns for tool parameters
    PROHIBITED_COMMAND_PATTERNS = [
        (r"\brm\s+(-[rfRF]+\s+)?(/|~|\$HOME)", "Host root destruction attempt"),
        (r"\b(mkfs|dd\s+if=.*of=/dev/)\b", "Direct block storage mutation"),
        (r":\(\)\{\s*:\|:&\s*\};:", "Fork bomb attempt"),
        (r"\b(nc|netcat)\s+-e\b", "Reverse shell connection attempt"),
    ]

    # Brand safety rules (Firby Core Rules)
    EMOJI_PATTERN = re.compile(
        r"[\U00010000-\U0010ffff]|[\u2600-\u27bf]|[\u2300-\u23ff]",
        flags=re.UNICODE
    )

    @classmethod
    def validate_tool_input(cls, tool_name: str, args: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validates tool arguments before execution.
        Returns (is_valid, violation_reason).
        """
        # 1. Shell command checks
        if tool_name in ("run_command", "execute_command", "bash"):
            cmd = str(args.get("command", "") or args.get("cmd", ""))
            for pat, desc in cls.PROHIBITED_COMMAND_PATTERNS:
                if re.search(pat, cmd, re.IGNORECASE):
                    return False, f"Prohibited command pattern detected: {desc}"

        # 2. File path checks (anti path-traversal)
        if tool_name in ("read_file", "write_file", "patch_file"):
            path_val = str(args.get("file_path", "") or args.get("path", ""))
            if ".." in path_val.split("/") or path_val.startswith("/etc") or path_val.startswith("/proc"):
                return False, f"Dangerous path traversal target: {path_val}"

        # 3. URL checks
        if tool_name in ("web_fetch", "browser_navigate", "fetch_web_page"):
            url = str(args.get("url", ""))
            if url:
                parsed = urllib.parse.urlparse(url if "://" in url else "https://" + url)
                if parsed.scheme not in ("http", "https"):
                    return False, f"Unsupported URL scheme: {parsed.scheme}"
                if parsed.hostname in ("169.254.169.254", "metadata.google.internal"):
                    return False, "Access to cloud instance metadata service is prohibited"

        return True, None

    @classmethod
    def sanitize_output(cls, text: str) -> str:
        """
        Cleans and sanitizes outgoing agent text according to Firby brand rules:
        - Strips emojis
        - Strips mentions of $1.000 COP
        - Redacts accidental API key leaks
        """
        if not text:
            return ""

        # Strip emojis
        clean_text = cls.EMOJI_PATTERN.sub("", text)

        # Redact $1.000 COP mentions
        clean_text = re.sub(r"\$?\s*1\.?000\s*cop", "Prueba 7 días gratis", clean_text, flags=re.IGNORECASE)

        # Redact API keys if accidentally reflected
        clean_text = re.sub(r"sk-[a-zA-Z0-9_-]{20,}", "[REDACTED_API_KEY]", clean_text)
        clean_text = re.sub(r"AIzaSy[a-zA-Z0-9_-]{20,}", "[REDACTED_API_KEY]", clean_text)

        return clean_text.strip()
