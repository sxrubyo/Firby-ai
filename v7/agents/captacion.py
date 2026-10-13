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
        agent_name = (ctx.metadata.get("agent_name") if ctx.metadata else "") or "Firby"
        
        text_clean = (ctx.text or "").lower().strip().replace("¿", "").replace("?", "").replace("¡", "").replace("!", "").strip()
        greeting_words = [
            "hola", "holaa", "holaaa", "buenas", "buenos dias", "buenos días",
            "buenas tardes", "buenas noches", "hey", "saludos", "hi", "hello",
            "que tal", "qué tal", "que mas", "qué más", "quiubo"
        ]
        is_just_greeting = (
            text_clean in greeting_words or
            (len(text_clean.split()) <= 3 and any(text_clean.startswith(gw) for gw in greeting_words))
        )

        if is_just_greeting:
            return f"""Eres {agent_name}, el operador digital de atención de Firby AI.
{compact_identity_rule(agent_name)}
{self._tone_header(ctx)}

REGLA ESTRICTA DE SALUDO INICIAL:
El usuario acaba de iniciar la conversación con un saludo ("{ctx.text.strip()}").
PROHIBIDO TERMINANTEMENTE SOBRE-EXPLICAR:
NO lances discursos largos, NO hables de características del producto, ni de cómo funciona, ni de widgets, ni de planes de precios. No te adelantes a preguntas que el usuario no ha hecho.
Responde OBLIGATORIAMENTE en una respuesta breve y sobria:
"Hola, bienvenido. ¿En qué le puedo orientar hoy?"

EJEMPLO EXACTO DE RESPUESTA:
Hola, bienvenido. ¿En qué le puedo orientar hoy?

{self._writing_rules()}"""

        return f"""Eres {agent_name}, el operador digital de atención de Firby AI.
{compact_identity_rule(agent_name)}
{self._tone_header(ctx)}

MISIÓN DE CAPTACIÓN:
El usuario pregunta o tiene curiosidad inicial sobre Firby.
Responde con cercanía, agilidad y tono ejecutivo.
PROHIBIDO SOBRE-EXPLICAR: No abrumes con listas eternas ni párrafos gigantes.
Responde en 2 burbujas cortas separadas con |||:
- Burbuja 1: Saludo y explicación concisa (Firby es un operador digital autónomo 24/7 que vive en tu sitio web, atiende visitantes y agenda citas en tiempo real).
- Burbuja 2: Pregunta amable sobre su caso o cómo le puedes colaborar (ej: "Cómo te puedo ayudar hoy?" o "En qué tipo de negocio te gustaría implementarlo?").

{self._writing_rules()}"""

    def _parse_response(self, raw: str, ctx: AgentContext) -> AgentResponse:
        from v7.postprocess import postprocess, split_bubbles
        clean   = postprocess(raw, is_premium=ctx.is_premium)
        text_clean = (ctx.text or "").lower().strip().replace("¿", "").replace("?", "").replace("¡", "").replace("!", "").strip()
        greeting_words = [
            "hola", "holaa", "buenas", "buenos dias", "buenos días", "buenas tardes",
            "buenas noches", "hey", "saludos", "hi", "que tal", "qué tal", "que mas", "qué más"
        ]
        is_greeting = (
            text_clean in greeting_words or
            (len(text_clean.split()) <= 3 and any(text_clean.startswith(gw) for gw in greeting_words))
        )
        max_b = 2 if is_greeting else 3
        bubbles = split_bubbles(clean, max_bubbles=max_b)
        return AgentResponse(
            bubbles=bubbles or [clean],
            funnel_update="explorando" if ctx.funnel_stage == "primer_contacto" else None,
        )
