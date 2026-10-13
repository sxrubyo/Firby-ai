# -*- coding: utf-8 -*-
"""
Firby Tool Registry (Hermes Tool Call Architecture Port)

Provides a declarative JSON schema tool registry for Firby LLM engines.
Instead of fragile regex pattern matchers, the LLM receives available tool definitions
and natively decides when to invoke integrations (Notion, ElevenLabs, Reminders, Memory Search).
"""

from __future__ import annotations
import json
import logging
from typing import Dict, Any, List, Callable, Optional, Tuple

log = logging.getLogger("firby.tool_registry")


class FirbyToolRegistry:
    """Registro modular de herramientas expuestas al LLM en formato OpenAPI/JSON Schema."""

    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable] = {}

    def register(self, name: str, description: str, parameters: Dict[str, Any], handler: Callable):
        """Registra una herramienta con su esquema JSON y función ejecutora."""
        self._tools[name] = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            }
        }
        self._handlers[name] = handler
        log.info(f"[tool_registry] Registered tool: {name}")

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return list(self._tools.values())

    async def execute_tool(self, name: str, args: Dict[str, Any]) -> Tuple[bool, Any]:
        """Ejecuta la herramienta invocada por el LLM en formato seguro."""
        if name not in self._handlers:
            return False, f"Tool '{name}' not found in registry."
        try:
            handler = self._handlers[name]
            import asyncio
            if asyncio.iscoroutinefunction(handler):
                res = await handler(**args)
            else:
                res = handler(**args)
            return True, res
        except Exception as e:
            log.error(f"[tool_registry] Error executing tool '{name}': {e}")
            return False, str(e)


# Global singleton instance
tool_registry = FirbyToolRegistry()


# ── HANDLERS ESTÁNDAR — HERMES ARCHITECTURE ─────────────────────────────────

async def _handle_schedule_reminder(chat_id: str, text: str, duration: str, db: Any = None) -> str:
    from src.firby.brain.firby_reminders import FirbyReminderEngine
    if not db:
        return "Error: Database connection not available."
    engine = FirbyReminderEngine(db)
    res = engine.schedule_reminder(chat_id, text, duration)
    if res.get("success"):
        return f"Recordatorio programado exitosamente para {res.get('display')}: '{text}'"
    return f"No se pudo programar el recordatorio: {res.get('error')}"

async def _handle_link_notion(token: str, db: Any = None, is_admin: bool = False, is_demo: bool = False) -> str:
    if not (is_admin or is_demo):
        return "Acceso denegado: Los clientes o pacientes en chats de producción no pueden registrar credenciales o APIs de la clínica. Esta acción requiere permisos de administrador."
    from src.firby.channels.onboarding import validate_notion_token
    info = await validate_notion_token(token)
    if not info:
        return "El token de Notion ingresado no es válido o expiró."
    if db and hasattr(db, "add_linked_channel"):
        db.add_linked_channel(
            platform="notion",
            channel_identity=info.get("workspace_name", "Notion"),
            config_json={"token": token, "workspace_name": info.get("workspace_name", "Notion")}
        )
    return f"Espacio de trabajo Notion '{info.get('workspace_name')}' vinculado exitosamente."

async def _handle_link_elevenlabs(token: str, db: Any = None, is_admin: bool = False, is_demo: bool = False) -> str:
    if not (is_admin or is_demo):
        return "Acceso denegado: Los clientes o pacientes en chats de producción no pueden registrar credenciales de voz. Esta acción requiere permisos de administrador."
    if db and hasattr(db, "add_linked_channel"):
        db.add_linked_channel(
            platform="elevenlabs",
            channel_identity="ElevenLabs Voice Engine",
            config_json={"token": token}
        )
    return "Token de ElevenLabs configurado exitosamente para notas de voz."

async def _handle_search_memory(chat_id: str, query: str, db: Any = None) -> str:
    from src.firby.brain.firby_fts5_memory import FTS5MemoryEngine
    if not db:
        return "Sin resultados de memoria."
    engine = FTS5MemoryEngine(db.db_path if hasattr(db, "db_path") else "/home/ubuntu/firby/firby.db")
    results = engine.search_memory(chat_id, query, limit=3)
    if not results:
        return f"No se encontraron antecedentes para la consulta '{query}'."
    return "\n".join([f"- [{r.get('role')}]: {r.get('content')}" for r in results])


# Register default Hermes tools
tool_registry.register(
    name="schedule_reminder",
    description="Programa un recordatorio automático por WhatsApp para el cliente o admin usando tiempo relativo o natural (ej. '30m', '2h', '1d').",
    parameters={
        "type": "object",
        "properties": {
            "chat_id": {"type": "string", "description": "ID del chat o número de teléfono del usuario."},
            "text": {"type": "string", "description": "Texto del recordatorio que se notificará."},
            "duration": {"type": "string", "description": "Duración o tiempo relativo (ej. '30m', '2h', '1d')."}
        },
        "required": ["chat_id", "text", "duration"]
    },
    handler=_handle_schedule_reminder
)

tool_registry.register(
    name="link_notion_channel",
    description="Vincula un espacio de trabajo de Notion usando un token de API de integración (ntn_...).",
    parameters={
        "type": "object",
        "properties": {
            "token": {"type": "string", "description": "Token de API de Notion iniciando con ntn_."}
        },
        "required": ["token"]
    },
    handler=_handle_link_notion
)

tool_registry.register(
    name="link_elevenlabs_channel",
    description="Configura un token de API de ElevenLabs (sk_...) para habilitar notas de voz naturales.",
    parameters={
        "type": "object",
        "properties": {
            "token": {"type": "string", "description": "API Key de ElevenLabs iniciando con sk_."}
        },
        "required": ["token"]
    },
    handler=_handle_link_elevenlabs
)

async def _handle_http_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    query_params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Union[Dict[str, Any], List[Any]]] = None,
    service_hint: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    from src.firby.brain.firby_http_executor import http_executor
    return await http_executor.execute_request(
        method=method,
        url=url,
        headers=headers,
        query_params=query_params,
        json_body=json_body,
        service_hint=service_hint
    )

async def _handle_web_search(query: str, **kwargs) -> str:
    try:
        from src.firby.integrations.search import WebSearchEngine
        engine = WebSearchEngine()
        text, url = await engine.search_business_link(query)
        if not text and not url:
            return f"No se encontraron resultados web para '{query}'."
        res = f"Resultados encontrados para '{query}':\n"
        if url:
            res += f"sitio: {url}\n"
        if text:
            res += f"informacion: {text[:800]}"
        return res
    except Exception as e:
        log.warning(f"[tool_registry] error en web_search: {e}")
        return f"Error al buscar '{query}': {e}"

async def _handle_send_voice_note(text: str, chat_id: str = "", **kwargs) -> str:
    try:
        from src.firby.brain.firby_demo_voice import generate_demo_audio
        audio_path = await generate_demo_audio(text)
        if audio_path:
            return f"[AUDIO_GENERATED:{audio_path}]"
        return "NOTIFICACIÓN DE SISTEMA: El proveedor de voz (ElevenLabs) no tiene cuota/saldo disponible en este momento. INSTRUCCIÓN: Responde amablemente al usuario mediante mensaje de texto explicándole por la propia voz del modelo que por el momento no puedes enviarle notas de voz, pero que le respondes por texto."
    except Exception as e:
        log.warning(f"[tool_registry] error en send_voice_note: {e}")
        return f"NOTIFICACIÓN DE SISTEMA: Ocurrió un error al intentar generar la nota de voz ({e}). Responde al usuario amablemente en texto explicando que no es posible enviar audios por ahora."

tool_registry.register(
    name="web_search",
    description="Busca información pública de un negocio, empresa o clínica en Google (sitio web, servicios, dirección, horario, redes sociales).",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Nombre del negocio o término a buscar (ej. 'Clinica de las americas Medellin')."}
        },
        "required": ["query"]
    },
    handler=_handle_web_search
)

tool_registry.register(
    name="send_voice_note",
    description="Genera y envía una nota de voz natural usando la voz configurada de ElevenLabs en vez de texto plano.",
    parameters={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Texto exacto a pronunciar en la nota de voz."},
            "chat_id": {"type": "string", "description": "ID del chat o número de WhatsApp del destinatario."}
        },
        "required": ["text"]
    },
    handler=_handle_send_voice_note
)

