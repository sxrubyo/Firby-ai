# -*- coding: utf-8 -*-
"""
Firby Credential Vault (Hermes Architecture Port)

Unified, hierarchical credential store and API key resolver.
Supports per-tenant/clinic credential isolation, domain-to-key mapping,
and dynamic bearer/header injection for autonomous LLM tool execution.
"""

from __future__ import annotations
import os
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from contextvars import ContextVar

log = logging.getLogger("firby.credential_vault")

# ContextVar for session-isolated credential overrides
_session_creds_var: ContextVar[Dict[str, Any]] = ContextVar("session_creds", default={})


class FirbyCredentialVault:
    """Bóveda unificada de credenciales y llaves de API con resolución jerárquica."""

    def __init__(self, db_manager: Any = None):
        self.db = db_manager
        # Known domain header mappings for autonomous HTTP calls
        self.domain_header_map: Dict[str, Tuple[str, str]] = {
            "api.notion.com": ("Authorization", "Bearer {key}"),
            "api.elevenlabs.io": ("xi-api-key", "{key}"),
            "api.openai.com": ("Authorization", "Bearer {key}"),
            "api.groq.com": ("Authorization", "Bearer {key}"),
            "generativelanguage.googleapis.com": ("x-goog-api-key", "{key}"),
            "openrouter.ai": ("Authorization", "Bearer {key}"),
        }

    def set_session_credential(self, service_or_key: str, value: str) -> None:
        """Establece una credencial aislada para la sesión actual."""
        cur = dict(_session_creds_var.get())
        cur[service_or_key.lower()] = value
        _session_creds_var.set(cur)

    def get_session_credentials(self) -> Dict[str, Any]:
        return _session_creds_var.get()

    def resolve_key(self, service: str, clinic_id: Optional[str] = None) -> Optional[str]:
        """
        Resuelve la llave de API jerárquicamente:
        1. ContextVar de la sesión actual
        2. Canales vinculados en SQLite (`core_memory` / `linked_channels`)
        3. Variables de Entorno del sistema (`.env`)
        """
        service_clean = service.lower().strip()
        
        # 1. Sesión actual
        sess = self.get_session_credentials()
        if service_clean in sess and sess[service_clean]:
            return str(sess[service_clean])

        # 2. SQLite Database (Linked Channels / Core Memory)
        if self.db:
            try:
                # Buscar en linked_channels
                if hasattr(self.db, "get_linked_channels"):
                    channels = self.db.get_linked_channels(platform=service_clean)
                    if channels:
                        first = channels[0]
                        cfg = first.get("config_json") or {}
                        if isinstance(cfg, str):
                            cfg = json.loads(cfg)
                        tok = cfg.get("token") or cfg.get("api_key")
                        if tok:
                            return str(tok)

                # Buscar en recall
                if hasattr(self.db, "recall"):
                    recalled = self.db.recall(f"{service_clean}_api_key") or self.db.recall(f"{service_clean}_token")
                    if recalled:
                        return str(recalled)
            except Exception as e:
                log.warning(f"[vault] Error consultando SQLite para {service_clean}: {e}")

        # 3. Environment Variables (.env)
        env_names = [
            f"{service_clean.upper()}_API_KEY",
            f"{service_clean.upper()}_TOKEN",
            f"{service_clean.upper()}_SECRET",
            service_clean.upper(),
        ]
        for env_name in env_names:
            val = os.getenv(env_name)
            if val and val.strip():
                return val.strip()

        return None

    def inject_auth_headers(self, url: str, headers: Dict[str, str], service_hint: Optional[str] = None) -> Dict[str, str]:
        """
        Inyecta automáticamente los encabezados de autenticación (Bearer/Header)
        según el dominio o servicio indicado.
        """
        headers_out = dict(headers or {})
        
        # 1. Resolver servicio por pista o por dominio
        service = service_hint
        if not service:
            from urllib.parse import urlparse
            netloc = urlparse(url).netloc.lower()
            for dom in self.domain_header_map:
                if dom in netloc:
                    service = dom
                    break

        if not service:
            return headers_out

        # 2. Buscar si ya hay mapeo de cabecera para este dominio/servicio
        from urllib.parse import urlparse
        netloc = urlparse(url).netloc.lower()
        
        target_service = service_hint or netloc
        key = self.resolve_key(target_service)
        
        if not key and service_hint:
            key = self.resolve_key(service_hint)

        if not key:
            return headers_out

        # Inyectar cabecera según el estándar del servicio
        if "notion" in netloc or service_hint == "notion":
            headers_out["Authorization"] = f"Bearer {key}"
            headers_out["Notion-Version"] = "2022-06-08"
        elif "elevenlabs" in netloc or service_hint == "elevenlabs":
            headers_out["xi-api-key"] = key
        elif "openai" in netloc or service_hint == "openai":
            headers_out["Authorization"] = f"Bearer {key}"
        elif "groq" in netloc or service_hint == "groq":
            headers_out["Authorization"] = f"Bearer {key}"
        elif "openrouter" in netloc or service_hint == "openrouter":
            headers_out["Authorization"] = f"Bearer {key}"
        else:
            # Encabezado Bearer genérico por defecto
            if "Authorization" not in headers_out:
                headers_out["Authorization"] = f"Bearer {key}"

        return headers_out


# Global Vault instance
credential_vault = FirbyCredentialVault()
