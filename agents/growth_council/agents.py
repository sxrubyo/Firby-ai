"""Implementation of the 8 individual AI agents using Google GenAI SDK and Gemini 3.5 Flash.
"""

import time
import json
from typing import Type, TypeVar
from pydantic import BaseModel
from google import genai
from google.genai.errors import APIError

from .config import client, ACTIVE_MODELS_CASCADE
from .prompts import (
    AGENT_1_HUNTER_PROMPT,
    AGENT_2_COPYWRITER_PROMPT,
    AGENT_3_VISUAL_DIRECTOR_PROMPT,
    AGENT_4_STATIC_DESIGNER_PROMPT,
    AGENT_5_COMPLIANCE_PROMPT,
    AGENT_6_SKEPTIC_PROMPT,
    AGENT_7_MEDIA_BUYER_PROMPT,
    AGENT_8_CRO_PROMPT,
)
from .schemas import (
    Sector1Output,
    AdCopyPack,
    VisualDirectorBrief,
    StaticCreativeSpec,
    ComplianceAudit,
    SkepticCritique,
    MediaPlan,
    ConversionOptimizationPlan,
)

T = TypeVar('T', bound=BaseModel)

def call_gemini_structured(
    system_instruction: str,
    prompt: str,
    schema: Type[T],
    models: list = None,
    max_retries: int = 2
) -> T:
    """Invokes Gemini 3.5 Flash series with strict Pydantic structured output and rapid failover."""
    models_to_try = models or ACTIVE_MODELS_CASCADE
    
    last_err = None
    for target_model in models_to_try:
        for attempt in range(max_retries):
            try:
                res = client.models.generate_content(
                    model=target_model,
                    contents=prompt,
                    config={
                        'response_mime_type': 'application/json',
                        'response_schema': schema,
                        'system_instruction': system_instruction,
                        'temperature': 0.7,
                    }
                )
                raw_text = res.text
                data = json.loads(raw_text)
                return schema.model_validate(data)
            except Exception as e:
                last_err = e
                err_str = str(e)
                # If quota exhausted (429) or high demand (503), do not wait: failover immediately to next model
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "UNAVAILABLE" in err_str or "503" in err_str:
                    break
                time.sleep(1.0 * (attempt + 1))
                continue
    raise RuntimeError(f"All Gemini models in cascade failed. Last error: {last_err}")


# --- AGENT DEFINITIONS ---

class HunterStrategistAgent:
    """Agente 1.1: Hunter de Fricción B2B & Estratega de Ángulos."""
    name = "Hunter de Dolores B2B"
    sector = "Ideación & Ángulos"

    @classmethod
    def generate_angles(cls, sector_name: str, context: str = "") -> Sector1Output:
        prompt = f"Analiza a fondo el sector: '{sector_name}'. Extrae los 3 dolores comerciales y operativos más sangrantes de los dueños de este nicho y genera 3 ángulos de impacto para Firby. Contexto adicional: {context}"
        return call_gemini_structured(AGENT_1_HUNTER_PROMPT, prompt, Sector1Output)


class DirectResponseCopywriterAgent:
    """Agente 1.2: Redactor Publicitario de Respuesta Directa."""
    name = "Direct-Response Copywriter"
    sector = "Ideación & Ángulos"

    @classmethod
    def write_ad_pack(cls, angle_brief: str) -> AdCopyPack:
        prompt = f"Toma el siguiente ángulo de dolor y escribe el paquete completo de copy de alto impacto para Meta Ads y Google Search:\n\n{angle_brief}\n\nRecuerda: Cero emojis, cero lenguaje robótico de IA, oferta estricta de prueba de 7 días gratis cancelable en 1 clic."
        return call_gemini_structured(AGENT_2_COPYWRITER_PROMPT, prompt, AdCopyPack)


class VideoScreenplayDirectorAgent:
    """Agente 2.1: Director Audiovisual & Pantalla Dividida."""
    name = "Director de Motion & Video Screenplay"
    sector = "Diseño & Creatividad"

    @classmethod
    def plan_video_ad(cls, copy_pack_json: str) -> VisualDirectorBrief:
        prompt = f"Basado en este copy de anuncio:\n{copy_pack_json}\n\nDiseña el guión visual y storyboard técnico de pantalla dividida (Split Screen) para un video vertical 9:16 de 35 segundos. En la izquierda el visitante agendando en la web, en la derecha el dueño recibiendo la alerta en WhatsApp."
        return call_gemini_structured(AGENT_3_VISUAL_DIRECTOR_PROMPT, prompt, VisualDirectorBrief)


class StaticCraftDesignerAgent:
    """Agente 2.2: Diseñador de Creativos Estáticos & UI Craft."""
    name = "Diseñador de Creativos Estáticos B2B"
    sector = "Diseño & Creatividad"

    @classmethod
    def design_static_spec(cls, angle_and_copy: str) -> StaticCreativeSpec:
        prompt = f"Basado en este ángulo y copy:\n{angle_and_copy}\n\nDiseña la especificación visual para un anuncio estático de alta conversión (1080x1080 o 1080x1350) con la estética refinada de Firby (obsidiana, verde lima neón, badges táctiles, Neue Montreal). Cero emojis."
        return call_gemini_structured(AGENT_4_STATIC_DESIGNER_PROMPT, prompt, StaticCreativeSpec)


class ComplianceGuardianAgent:
    """Agente 3.1: Auditor de Reglas Inquebrantables de Marca."""
    name = "Auditor de Compliance & Políticas"
    sector = "Pruebas & Auditoría"

    @classmethod
    def audit_ad_material(cls, material_text: str) -> ComplianceAudit:
        prompt = f"Audita con máxima rigurosidad el siguiente material publicitario de Firby contra nuestras 4 reglas inquebrantables:\n\n{material_text}\n\nVerifica: Cero emojis, cero $1.000 COP, canales exactos (web para visitante, WhatsApp solo para el dueño), español directo de negocios sin clichés de IA."
        return call_gemini_structured(AGENT_5_COMPLIANCE_PROMPT, prompt, ComplianceAudit)


class SkepticProspectAgent:
    """Agente 3.2: Simulador de Prospecto Escéptico & Cazador de Objeciones."""
    name = "Simulador de Prospecto Escéptico"
    sector = "Pruebas & Auditoría"

    @classmethod
    def stress_test_ad(cls, material_text: str, persona_type: str = "Dueño de Clínica de Especialidades") -> SkepticCritique:
        prompt = f"Actúa como un {persona_type} desconfiado y lee este anuncio:\n\n{material_text}\n\nDestruye las promesas débiles, señala qué no te crees y define qué argumento exacto te convencería de probar los 7 días."
        return call_gemini_structured(AGENT_6_SKEPTIC_PROMPT, prompt, SkepticCritique)


class MediaBuyingArchitectAgent:
    """Agente 4.1: Media Buyer & Arquitecto de Campañas."""
    name = "Media Buyer & Estratega de Pauta"
    sector = "Tráfico & Conversión"

    @classmethod
    def create_media_plan(cls, sector_name: str, ad_copy_title: str) -> MediaPlan:
        prompt = f"Crea la estructura de pauta para Meta Ads y Google Search para el sector '{sector_name}' con el ángulo '{ad_copy_title}'. Define segmentación B2B precisa, distribución de presupuesto y nomenclatura UTM limpia."
        return call_gemini_structured(AGENT_7_MEDIA_BUYER_PROMPT, prompt, MediaPlan)


class ConversionRateOptimizerAgent:
    """Agente 4.2: Optimizador de Conversión & Match de Mensaje."""
    name = "Optimizador de Conversión & CRO"
    sector = "Tráfico & Conversión"

    @classmethod
    def optimize_landing_match(cls, ad_copy_headline: str, sector_name: str) -> ConversionOptimizationPlan:
        prompt = f"El usuario hace clic en un anuncio con el titular: '{ad_copy_headline}' dirigido al sector '{sector_name}'. Diseña la experiencia de aterrizaje perfecta en la web de Firby: titular de recepción, mensaje inicial contextual del widget de Firby y eliminación de fricción para activar los 7 días gratis."
        return call_gemini_structured(AGENT_8_CRO_PROMPT, prompt, ConversionOptimizationPlan)
