"""
Firby V7.0 — Agente de Objeciones
=====================================
Maneja toda resistencia del paciente.
La objeción dicha raramente es la objeción real.
Prompt: ~580 tokens.
"""

from __future__ import annotations
import re
from v7.agents.base import AgentBase, AgentContext, AgentResponse


# Mapa objeción detectada → clave para guardar en perfil
_OBJECION_MAP = [
    (r"\b(caro|costoso|precio|plata|presupuesto)\b",                     "precio"),
    (r"\b(pensar|pensarlo|consultar|socio|después|luego)\b",             "indecision"),
    (r"\b(difícil|dificil|complicado|no sé programar|no se programar|código)\b", "complejidad"),
    (r"\b(seguro|seguridad|alucina|inventa|datos falsos|confianza)\b",   "seguridad"),
    (r"\b(chatbot|es un bot|es como chatgpt|otro bot|convencional)\b",   "diferenciacion_bot"),
    (r"\b(no funciona|no sirve|carreta|esceptic|no creo)\b",             "escepticismo"),
    (r"\b(tiempo|ocupad|trabajo)\b",                                     "tiempo"),
]

def _detect_objecion(text: str) -> str:
    for pattern, key in _OBJECION_MAP:
        if re.search(pattern, text, re.IGNORECASE):
            return key
    return "otra"


class AgenteObjeciones(AgentBase):

    agent_id     = "objeciones"
    context_keys = ["patient_name", "objeciones_pasadas", "funnel_state",
                    "clinic_tone", "servicios_relevantes"]

    def _build_prompt(self, ctx: AgentContext) -> str:
        agent_name = (ctx.metadata.get("agent_name") if ctx.metadata else "") or "Firby"

        return f"""Eres {agent_name}, el operador digital de Firby AI en WhatsApp.
{self._tone_header(ctx)}

MISIÓN:
Resolver cualquier duda, objeción o escepticismo sobre Firby AI con empatía, claridad técnica y enfoque de negocio.
Escribe en 2 o 3 burbujas orgánicas usando ||| como separador.

CÓMO RESPONDER SEGÚN LA OBJECIÓN:

1. "Está caro / no tengo presupuesto":
- Valida la inversión: el 58% de las consultas a un negocio llegan por fuera del horario laboral. Firby atiende esas noches y fines de semana sin turnos extra ni nóminas.
- Recuerda que todos los planes tienen prueba de 7 días gratis con cancelación en 1 clic sin permanencia en https://firbyai.lat/sign-up.

2. "Es muy difícil / no sé de programación / no tengo desarrollador":
- La instalación toma menos de 1 minuto: es copiar y pegar una sola línea de código en tu sitio web. No tienes que configurar servidores ni saber programación.

3. "Me da miedo que invente cosas o alucine (seguridad)":
- Firby no es un bot sin control: opera con gobernanza estricta sobre tus políticas comerciales oficiales.
- Si un cliente pide algo fuera de política o un trámite sensible, Firby se detiene y te pide autorización por WhatsApp antes de proceder.

4. "Es solo otro chatbot más / ya tengo un chat":
- Los chatbots tradicionales solo sueltan texto plano o mandan a formularios externos que la gente abandona.
- Firby ejecuta el proceso completo en tu web: se desplaza por las secciones, scrollea en pantalla para el usuario, revisa Google Calendar en vivo y confirma la cita directamente.

5. "Lo voy a pensar / no sé si me sirva":
- Invítale a probarlo en su propia web sin riesgo con los 7 días de prueba gratis en https://firbyai.lat/sign-up.

{self._writing_rules()}"""

    def _parse_response(self, raw: str, ctx: AgentContext) -> AgentResponse:
        from v7.postprocess import postprocess, split_bubbles
        clean    = postprocess(raw, is_premium=ctx.is_premium)
        bubbles  = split_bubbles(clean)
        objecion = _detect_objecion(ctx.text)
        return AgentResponse(
            bubbles=bubbles or [clean],
            new_objecion=objecion,
        )
