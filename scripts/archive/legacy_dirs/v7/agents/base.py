"""
Firby V7.0 — AgentBase
=========================
Contrato que todos los agentes implementan.
El orquestador siempre llama agent.run(ctx) sin saber qué agente es.
"""

from __future__ import annotations
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

log = logging.getLogger(__name__)


# ── Contexto de entrada ───────────────────────────────────────────────────────

@dataclass
class AgentContext:
    """
    Todo lo que un agente necesita para generar su respuesta.
    El orquestador ensambla esto desde la memoria ANTES de llamar al agente,
    pasando SOLO los campos que el agente declaró necesitar.
    """
    # Mensaje actual
    chat_id:       str
    text:          str
    platform:      str = "whatsapp"

    # Perfil del paciente (solo campos solicitados)
    patient_summary: str = ""          # texto compacto del perfil
    funnel_stage:    str = "primer_contacto"
    patient_name:    Optional[str] = None
    visits:          int = 0
    objeciones_pasadas: List[str] = field(default_factory=list)

    # Clínica
    clinic_name:   str = ""
    clinic_tone:   str = "SALUD"       # SALUD | SALUD PREMIUM | GENERAL | RETAIL
    clinic_kb:     str = ""            # fragmento relevante de KB
    servicios:     str = ""
    precios:       str = ""
    horarios:      str = ""

    # Historial reciente (últimos N mensajes para coherencia)
    history:       List[Dict] = field(default_factory=list)

    # Contexto adicional
    search_context: str = ""
    calendar_info:  str = ""
    teachings:      str = ""            # Enseñanzas y datos confirmados por el dueño
    owner_style:    str = ""            # Reglas de estilo de redacción del dueño
    metadata:       Dict[str, Any] = field(default_factory=dict)

    @property
    def is_premium(self) -> bool:
        return self.clinic_tone in ("SALUD PREMIUM", "PREMIUM")

    @property
    def usted(self) -> bool:
        return self.is_premium

    def greeting_name(self) -> str:
        return self.patient_name or ""

    @property
    def funnel_state(self) -> str:
        return self.funnel_stage

    @property
    def servicios_clinica(self) -> str:
        return self.servicios

    @property
    def clinic_kb_excerpt(self) -> str:
        return self.clinic_kb

    @property
    def calendar_available(self) -> bool:
        return bool(self.calendar_info)


# ── Respuesta del agente ──────────────────────────────────────────────────────

@dataclass
class AgentResponse:
    """
    Lo que el agente devuelve al orquestador.
    """
    bubbles:         List[str]              # burbujas ya listas para enviar
    next_agent:      Optional[str] = None  # si el agente quiere escalar a otro
    funnel_update:   Optional[str] = None  # nuevo estado del funnel (si cambió)
    new_objecion:    Optional[str] = None  # objeción detectada para registrar
    learned_name:    Optional[str] = None  # nombre detectado en el mensaje
    learned_zona:    Optional[str] = None  # zona de interés detectada
    confidence:      float = 1.0
    latency_ms:      float = 0.0
    agent_id:        str = "unknown"

    @property
    def text(self) -> str:
        return " ||| ".join(self.bubbles)


# ── Clase base ────────────────────────────────────────────────────────────────

class AgentBase(ABC):
    """
    Todos los agentes heredan de aquí.
    Implementar solo: agent_id, context_keys, _build_prompt, y opcionalmente _parse_response.
    """

    agent_id:     str          # identificador único
    context_keys: List[str]    # qué campos de AgentContext necesita

    # Máximo de tokens que este agente puede usar en su prompt de sistema
    max_system_tokens: int = 600

    def __init__(self, llm_engine):
        self._llm = llm_engine

    async def run(self, ctx: AgentContext) -> AgentResponse:
        """
        Punto de entrada único. El orquestador siempre llama esto.
        No se sobreescribe (salvo casos muy específicos).
        """
        t0 = time.perf_counter()
        try:
            system_prompt = self._build_prompt(ctx)
            messages      = self._build_messages(ctx, system_prompt)
            raw, meta     = await self._llm.complete(
                messages,
                model_tier="fast",
                temperature=0.82,
                max_tokens=200,   # agentes responden corto
            )
            log.info(
                "[%s] %s provider=%s model=%s",
                self.agent_id,
                ctx.chat_id[:8],
                meta.get("provider", "?"),
                meta.get("model", "?")[:25],
            )
            response = self._parse_response(raw, ctx)
            response.latency_ms = (time.perf_counter() - t0) * 1000
            response.agent_id   = self.agent_id
            return response
        except Exception as e:
            log.error("[%s] error: %s", self.agent_id, e, exc_info=True)
            return AgentResponse(
                bubbles=["un momento, déjame revisar eso"],
                agent_id=self.agent_id,
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

    @abstractmethod
    def _build_prompt(self, ctx: AgentContext) -> str:
        """Construye el system prompt especializado para este agente."""

    def _build_messages(self, ctx: AgentContext, system_prompt: str) -> List[Dict]:
        """Arma el array de mensajes para el LLM con catálogo de Biblioteca Media."""
        import json
        from pathlib import Path
        
        lib_path = Path("/home/ubuntu/firby/instances/clinica-de-las-americas/library.json")
        if not lib_path.exists():
            lib_path = Path("/home/ubuntu/firby/library.json")
            
        media_catalog = ""
        if lib_path.exists():
            try:
                items = json.loads(lib_path.read_text())
                if items:
                    entries = []
                    for item in items:
                        asset_id = item.get("id", "")
                        asset_type = item.get("asset_type", "foto")
                        name = item.get("name", "")
                        trigger = item.get("trigger_prompt", "")
                        type_label = {"photo": "📷 Foto", "audio": "🎙️ Audio de voz", "pdf": "📄 Documento PDF"}.get(asset_type, "📎 Archivo")
                        entries.append(f"  • [MEDIA:{asset_id}] → {type_label}: \"{name}\". Enviar cuando: {trigger}")
                    media_catalog = (
                        "\n\nBIBLIOTECA MEDIA — Recursos reales que puedes enviar:\n"
                        + "\n".join(entries) +
                        "\n\nPara enviar un recurso, escribe la etiqueta [MEDIA:id] en tu respuesta."
                        "\nEl sistema lo convierte automáticamente en foto, nota de voz o documento real por WhatsApp/Telegram."
                        "\n\nREGLA PRIORITARIA DE BIBLIOTECA:"
                        "\nSi el mensaje del usuario coincide o se relaciona con el detonante ('Enviar cuando') de algún recurso:"
                        "\n1. DEBES incluir la etiqueta [MEDIA:id] correspondiente al final de tu respuesta."
                        "\n2. NO digas que no tienes acceso ni que no sabes, si existe un recurso para esa consulta."
                        "\n3. Para audios (🎙️ Audio de voz), responde el contenido directamente de forma natural y hablada sin anteponer frases de plantilla."
                        "\n4. Para fotos (📷 Foto), responde brevemente y pon [MEDIA:id] al final."
                    )
            except Exception:
                pass

        teachings_block = f"\n\nDATOS Y ENSEÑANZAS CONFIRMADAS POR EL DUEÑO (Responde con estos datos sin dudar):\n{ctx.teachings}" if ctx.teachings else ""
        owner_style_block = f"\n\nREGLAS DE ESTILO DEL DUEÑO:\n{ctx.owner_style}" if ctx.owner_style else ""

        full_system = system_prompt + teachings_block + owner_style_block + media_catalog
        messages = [{"role": "system", "content": full_system}]
        for turn in ctx.history[-8:]:
            messages.append({
                "role":    turn.get("role", "user"),
                "content": turn.get("content", ""),
            })
        messages.append({"role": "user", "content": ctx.text})
        return messages

    def _parse_response(self, raw: str, ctx: AgentContext) -> AgentResponse:
        """
        Post-procesa la respuesta cruda del LLM.
        Los agentes pueden sobreescribir esto para extraer acciones (citas, nombres, etc.).
        """
        from v7.postprocess import postprocess
        clean   = postprocess(raw, is_premium=ctx.is_premium)
        bubbles = [b.strip() for b in clean.split("|||") if b.strip()]
        return AgentResponse(bubbles=bubbles or [clean])

    # ── Helpers comunes ────────────────────────────────────────────────────────

    def _tone_header(self, ctx: AgentContext) -> str:
        """Instrucción de tono ultra-humano y natural."""
        name = (ctx.metadata.get("agent_name") if ctx.metadata else "") or "Firby"
        return (
            "IDENTIDAD Y TONO DE ATENCIÓN:\n"
            f"Eres {name}, la recepcionista principal de {ctx.clinic_name or 'la clínica'}. "
            "Hablas por WhatsApp con calidez humana, empatía y amabilidad en español latino / colombiano.\n"
            "SIEMPRE saluda cordialmente al iniciar (ej: 'Hola! Cómo estás?' o 'Hola! Qué gusto saludarte').\n"
            "PROHIBIDO TERMINANTEMENTE: Frases robóticas de conmutador como 'Bienvenido a la clínica' o 'En qué podemos ayudarle'. Escribe como una persona real y atenta."
        )

    def _writing_rules(self) -> str:
        return (
            "REGLAS DE FORMATO Y WHATSAPP:\n"
            "• Escribe en 2 burbujas cortas y orgánicas usando ||| como separador obligatorio.\n"
            "• CERO signos de apertura (¿ ni ¡). Escribe siempre 'Hola, cómo estás?' o 'Hola! Claro que sí'.\n"
            "• CERO puntos finales (.) en preguntas sueltas o frases cortas.\n"
            "• Sé clara, empática y servicial."
        )

    def _patient_block(self, ctx: AgentContext) -> str:
        if ctx.patient_summary:
            return f"PACIENTE:\n{ctx.patient_summary}"
        return ""

    def _clinic_block(self, ctx: AgentContext) -> str:
        parts = [f"Clínica: {ctx.clinic_name}"]
        if ctx.servicios:
            parts.append(f"Servicios: {ctx.servicios[:200]}")
        if ctx.clinic_kb:
            parts.append(f"KB: {ctx.clinic_kb[:400]}")
        return "\n".join(parts)
