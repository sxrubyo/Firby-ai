"""
Firby V7.0 — Agente de Captación (Actualizado)
=====================================
Primer contacto. Responde con calidez humana y entrega información o recursos multimedia (menú, imágenes, audios) cuando el cliente los solicita.
"""

from __future__ import annotations
from firby_core.identity_policy import compact_identity_rule
from v7.agents.base import AgentBase, AgentContext, AgentResponse


class AgenteCaptacion(AgentBase):

    agent_id     = "captacion"
    context_keys = ["patient_name", "visits", "funnel_state", "clinic_tone", "servicios_clinica"]

    def _build_prompt(self, ctx: AgentContext) -> str:
        usted = ctx.usted
        nombre_bloque = f"Su nombre es {ctx.patient_name}." if usted and ctx.patient_name else \
                        f"Se llama {ctx.patient_name}." if ctx.patient_name else ""
        agent_name = (ctx.metadata.get("agent_name") if ctx.metadata else "") or "Firby"

        return f"""Eres {agent_name}, la recepcionista principal de {ctx.clinic_name or "la clínica"}.
{compact_identity_rule(agent_name)}
{self._tone_header(ctx)}
{nombre_bloque}

MISIÓN:
Atender a la persona con calidez, cercanía y agilidad en 2 burbujas cortas separadas con |||.
- Al primer contacto, saluda siempre de forma cordial y fresca (ej: 'Hola! Cómo estás?' o 'Hola! Qué gusto saludarte').
- En la segunda burbuja, pregunta con naturalidad cómo le puedes colaborar o qué servicio / consulta necesita.
- Si pide información, precios o citas, responde de inmediato con claridad y amabilidad.
- Si el mensaje coincide con algún recurso de la BIBLIOTECA MEDIA, responde en texto cálido e incluye la etiqueta [MEDIA:id] correspondiente al final.
- PROHIBIDO TERMINANTEMENTE: 'Bienvenido a la clínica', 'En qué podemos ayudarle hoy', 'Soy una asesora virtual'.

{self._writing_rules()}
{self._patient_block(ctx)}"""

    def _parse_response(self, raw: str, ctx: AgentContext) -> AgentResponse:
        from v7.postprocess import postprocess, split_bubbles
        clean   = postprocess(raw, is_premium=ctx.is_premium)
        bubbles = split_bubbles(clean)
        return AgentResponse(
            bubbles=bubbles or [clean],
            funnel_update="explorando" if ctx.funnel_stage == "primer_contacto" else None,
        )
