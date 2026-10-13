"""
Firby V7.0 — Agente de Agenda
==================================
Gestiona la valoración/cita. Propone UN día concreto.
Nunca inventa disponibilidad. Cierra hacia el micro-compromiso.
Prompt: ~320 tokens.
"""

from __future__ import annotations
import re
from v7.agents.base import AgentBase, AgentContext, AgentResponse


class AgenteAgenda(AgentBase):

    agent_id     = "agenda"
    context_keys = ["patient_name", "funnel_state", "ultima_cita",
                    "calendar_available", "clinic_tone"]

    def _build_prompt(self, ctx: AgentContext) -> str:
        agent_name = (ctx.metadata.get("agent_name") if ctx.metadata else "") or "Firby"

        return f"""Eres {agent_name}, el operador digital de Firby AI en WhatsApp.
{self._tone_header(ctx)}

MISIÓN DE DEMO Y ACTIVACIÓN:
Guiar al usuario para que active su cuenta o pruebe la experiencia de Firby AI en vivo.
Escribe en 2 o 3 burbujas orgánicas usando ||| como separador.

ACCIONES PRINCIPALES:
1. Si quiere registrarse, suscribirse o probar:
   - Comparte el enlace directo oficial: https://firbyai.lat/sign-up
   - Recuerda la garantía: prueba 7 días gratis con cancelación en 1 clic sin permanencia ni cobros automáticos sorpresa.

2. Si quiere ver una demostración en vivo:
   - Puede probar a Firby ahora mismo interactuando en pantalla en https://firbyai.lat
   - O si prefiere una sesión guiada con el equipo técnico, propón un día específico (por ejemplo: "te podemos agendar una demo técnica este jueves, qué horario te conviene").

3. CERO texto quemado o rígido. Habla fluido, empático y resolutivo.

{self._writing_rules()}"""

    def _parse_response(self, raw: str, ctx: AgentContext) -> AgentResponse:
        from v7.postprocess import postprocess, split_bubbles
        clean   = postprocess(raw, is_premium=ctx.is_premium)
        bubbles = split_bubbles(clean)

        # Detectar si se confirmó una cita en la respuesta
        cita_confirmada = bool(re.search(
            r"\b(agend[oé]|confirm[oé]|anot[oé]|queda para|quedaste para)\b",
            raw, re.IGNORECASE
        ))

        return AgentResponse(
            bubbles=bubbles or [clean],
            funnel_update="cita_agendada" if cita_confirmada else None,
        )
