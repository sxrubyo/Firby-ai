# -*- coding: utf-8 -*-
"""
Firby Tool Calling Engine
==========================
Maneja la ejecución nativa de herramientas (búsqueda web, notas de voz, recordatorios, etc.)
sin romper el System Prompt ni la personalidad del agente.

Inspirado en la arquitectura de herramientas de Hermes y OpenClaw:
1. El agente recibe el mensaje y la lista de herramientas disponibles.
2. Si detecta la necesidad de buscar en la web, enviar voz, etc., emite una llamada a la herramienta.
3. El resultado se inyecta en el historial de conversación.
4. El agente genera su respuesta final manteniendo intacto su personaje, tono y estructura de burbujas.
"""

from __future__ import annotations
import json
import re
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple

from src.firby.brain.firby_tool_registry import tool_registry

log = logging.getLogger("firby.tool_engine")


class FirbyToolEngine:
    """Orquestador de herramientas nativas para Firby."""

    def __init__(self, llm_engine: Any, db: Any = None):
        self.llm = llm_engine
        self.db = db

    async def execute_tool_call(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Ejecuta una herramienta registrada y devuelve el resultado formateado."""
        log.info(f"[tool_engine] Ejecutando herramienta '{tool_name}' con args: {args}")
        success, result = await tool_registry.execute_tool(tool_name, args)
        if success:
            log.info(f"[tool_engine] Herramienta '{tool_name}' OK")
            return str(result)
        else:
            log.warning(f"[tool_engine] Herramienta '{tool_name}' falló: {result}")
            return f"Error ejecutando {tool_name}: {result}"

    def build_tool_system_prompt(self, base_system_prompt: str) -> str:
        """Enriquece el System Prompt con las herramientas disponibles en formato JSON Schema."""
        schemas = tool_registry.get_tool_schemas()
        if not schemas:
            return base_system_prompt

        tools_desc = []
        for t in schemas:
            fn = t.get("function", {})
            name = fn.get("name")
            desc = fn.get("description")
            params = json.dumps(fn.get("parameters", {}), ensure_ascii=False)
            tools_desc.append(f"- {name}: {desc}\n  Parámetros: {params}")

        tools_str = "\n".join(tools_desc)

        tool_instruction = f"""

HERRAMIENTAS DISPONIBLES:
Puedes invocar herramientas cuando lo necesites. Si requieres buscar información de un negocio, enviar una nota de voz o agendar un recordatorio, emite una llamada a la herramienta usando la sintaxis:
```tool_call
{{"name": "nombre_herramienta", "arguments": {{...}}}}
```

Herramientas soportadas:
{tools_str}

REGLA DE CONTINUIDAD:
Cuando recibas el resultado de una herramienta (```tool_result ... ```), NUNCA saludes de nuevo ni rompas personaje. Usa la información obtenida para responder de inmediato en 2-3 burbujas (|||) manteniendo tu misma personalidad.
"""
        return base_system_prompt + tool_instruction

    def parse_tool_call(self, llm_response: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Parsea si el LLM emitió una llamada a herramienta en su respuesta."""
        if not llm_response:
            return None

        # Patrón 1: ```tool_call {"name": "...", "arguments": {...}} ```
        match = re.search(r"```tool_call\s*(\{.*?\})\s*```", llm_response, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                return data.get("name"), data.get("arguments", {})
            except Exception as e:
                log.warning(f"[tool_engine] Error parseando JSON de tool_call: {e}")

        # Patrón 2: {"name": "...", "arguments": {...}}
        match_json = re.search(r"\{\s*\"name\"\s*:\s*\"([^\"]+)\"\s*,\s*\"arguments\"\s*:\s*(\{.*?\})\s*\}", llm_response, re.DOTALL)
        if match_json:
            try:
                name = match_json.group(1)
                args = json.loads(match_json.group(2))
                return name, args
            except Exception:
                pass

        return None

    async def run_react_loop(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        max_steps: int = 3,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Bucle ReAct verdadero (Think -> Act -> Observe -> Answer) al estilo Hermes / OpenClaw.
        Ejecuta hasta `max_steps` interacciones de herramientas antes de devolver la respuesta final al usuario.
        """
        enriched_system = self.build_tool_system_prompt(system_prompt)
        conversation = [{"role": "system", "content": enriched_system}] + list(messages)
        executed_tools = []

        step = 0
        while step < max_steps:
            step += 1
            log.info(f"[react_loop] Paso {step}/{max_steps}")
            response, meta = await self.llm.complete(
                conversation,
                model_tier="fast",
                temperature=temperature,
                max_tokens=max_tokens,
                use_cache=False,
            )

            if not response:
                break

            parsed_call = self.parse_tool_call(response)
            if not parsed_call:
                log.info(f"[react_loop] Respuesta final obtenida en paso {step}")
                return response, executed_tools

            tool_name, tool_args = parsed_call
            log.info(f"[react_loop] Tool Call detectada: {tool_name}({tool_args})")

            tool_result = await self.execute_tool_call(tool_name, tool_args)
            executed_tools.append({"name": tool_name, "args": tool_args, "result": tool_result[:200]})

            conversation.append({"role": "assistant", "content": f"```tool_call\n{{\"name\": \"{tool_name}\", \"arguments\": {json.dumps(tool_args, ensure_ascii=False)}}}\n```"})
            conversation.append({"role": "user", "content": f"```tool_result\n{tool_result}\n```"})

        return conversation[-1]["content"] if conversation else "", executed_tools
