# -*- coding: utf-8 -*-
"""
Firby HTTP Executor (Hermes Autonomous API Execution Port)

Generic, secure HTTP REST API execution tool that empowers the LLM to interact
autonomously with third-party web APIs (Notion, CRM, Stripe, Webhooks, Calendars).
Automatically resolves and injects credentials from FirbyCredentialVault.
"""

from __future__ import annotations
import json
import logging
import httpx
from typing import Dict, Any, Optional, Tuple, Union
from src.firby.brain.firby_credential_vault import credential_vault

log = logging.getLogger("firby.http_executor")

# Security deny-list for sensitive local network addresses
BLOCKED_NETWORKS = ["127.0.0.1", "localhost", "0.0.0.0", "169.254.169.254", "::1"]


class FirbyHTTPExecutor:
    """Ejecutor HTTP autónomo para llamadas a APIs de terceros."""

    def __init__(self, vault=credential_vault):
        self.vault = vault

    async def execute_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Union[Dict[str, Any], List[Any]]] = None,
        service_hint: Optional[str] = None,
        timeout_seconds: float = 15.0
    ) -> Dict[str, Any]:
        """
        Ejecuta una petición HTTP autónoma a cualquier API web REST/JSON.
        Inyecta automáticamente credenciales desde la Bóveda de Credenciales.
        """
        method_upper = method.upper().strip()
        if method_upper not in ("GET", "POST", "PUT", "DELETE", "PATCH"):
            return {"success": False, "error": f"Método HTTP no soportado: {method_upper}"}

        # 1. Seguridad: Prevenir SSRF en redes locales
        from urllib.parse import urlparse
        hostname = urlparse(url).hostname or ""
        if hostname.lower() in BLOCKED_NETWORKS:
            return {"success": False, "error": f"Petición bloqueada por seguridad (host local no permitido: {hostname})"}

        # 2. Autenticación: Inyectar llaves/headers desde la Bóveda
        headers_to_send = self.vault.inject_auth_headers(url, headers or {}, service_hint=service_hint)
        if "Content-Type" not in headers_to_send and method_upper in ("POST", "PUT", "PATCH"):
            headers_to_send["Content-Type"] = "application/json"

        # 3. Petición HTTP Asíncrona
        import time
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
                req_kwargs: Dict[str, Any] = {
                    "headers": headers_to_send,
                    "params": query_params,
                }
                if json_body is not None and method_upper in ("POST", "PUT", "PATCH"):
                    req_kwargs["json"] = json_body

                resp = await client.request(method_upper, url, **req_kwargs)
                
                # Intentar parsear respuesta JSON o texto
                content_type = resp.headers.get("content-type", "")
                is_json = "json" in content_type.lower()
                
                try:
                    payload = resp.json() if is_json else resp.text[:4000]
                except Exception:
                    payload = resp.text[:4000]

                return {
                    "success": resp.is_success,
                    "status_code": resp.status_code,
                    "url": str(resp.url),
                    "headers": dict(resp.headers),
                    "data": payload
                }
        except Exception as e:
            log.warning(f"[http_executor] Error ejecutando {method_upper} {url}: {e}")
            return {"success": False, "error": f"Fallo de red al conectar con API: {e}"}


# Global HTTP Executor instance
http_executor = FirbyHTTPExecutor()
