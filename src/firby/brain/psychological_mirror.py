# -*- coding: utf-8 -*-
"""
Firby Psychological Style Mirror & Dynamic Persona Generator

Analiza el patrón psicológico, vocabulario y estilo de tecleo del Administrador
para clonar su estilo e inyectarlo en la personalidad del agente en WhatsApp.
También gestiona la personalización de nombre (ej. "Andrea", "Valentina") y el candado
de seguridad previo al despegue para clientes externos.
"""

from __future__ import annotations
import re
import logging
from typing import Dict, Any, Tuple, Optional

log = logging.getLogger("firby.psychological_mirror")


class PsychologicalStyleMirror:
    """Motor de Espejismo Psicológico y Adaptación de Personalidad."""

    def analyze_owner_style(self, text: str) -> Dict[str, Any]:
        """
        Analiza el texto enviado por el administrador para extraer su perfil psicológico:
        - Formaldad (tuteo vs ustedeo)
        - Longitud y velocidad (conciso vs explicativo)
        - Vocabulario distintivo y regionalismos
        - Tono emocional (directo, cálido, entusiasta)
        """
        if not text:
            return {}

        lower = text.lower()
        words = lower.split()
        
        # 1. Formosidad / Trato
        tuteo_count = sum(1 for w in ["te", "tu", "tus", "tienes", "quieres", "puedes", "mira", "che", "parce"] if w in words)
        ustedeo_count = sum(1 for w in ["usted", "su", "sus", "tiene", "puede", "quiere", "vea"] if w in words)
        formality = "informal" if tuteo_count >= ustedeo_count else "formal"

        # 2. Regionalismos
        region = "general"
        if any(w in lower for w in ["che", "tenés", "querés", "viste", "boludo", "argentino"]):
            region = "argentino"
        elif any(w in lower for w in ["parce", "paisa", "vea pues", "medellin", "medellín"]):
            region = "paisa"
        elif any(w in lower for w in ["wey", "padre", "órale", "mexicano"]):
            region = "mexicano"

        # 3. Concisión
        verbosity = "concise" if len(words) < 12 else "detailed"

        profile = {
            "formality": formality,
            "region": region,
            "verbosity": verbosity,
            "sample_snippet": text[:100]
        }
        log.info(f"[psychological_mirror] Style extracted: {profile}")
        return profile

    def build_custom_persona_prompt(self, persona_name: str, clinic_name: str, style_profile: Dict[str, Any]) -> str:
        """
        Genera el System Prompt de Personalidad Personalizada (ej. "Andrea").
        Inyecta el espejismo psicológico del dueño.
        """
        p_name = persona_name.strip().title() if persona_name else "Firby"
        c_name = clinic_name.strip().title() if clinic_name else "la Clínica"
        
        formality = style_profile.get("formality", "informal")
        region = style_profile.get("region", "general")
        
        formality_instruction = "Trata al paciente de 'tú' con calidez, cercanía y respeto." if formality == "informal" else "Trata al paciente de 'usted' con absoluta cortesía y profesionalismo."

        regional_instruction = ""
        if region == "argentino":
            regional_instruction = "Usa un tono argentino cálido y voseo natural (che, mirá, tenés, querés)."
        elif region == "paisa":
            regional_instruction = "Usa una calidez paisa amable y servicial (con gusto, claro que sí, con mucho gusto)."

        prompt = f"""
ERES {p_name.upper()}, la asesora virtual oficial de {c_name}.
Tus respuestas en WhatsApp deben sentirse 100% como un ser humano real atendiendo desde el celular de la empresa.

INSTRUCCIONES DE IDENTIDAD Y ESTILO:
1. Tu nombre es {p_name}. Preséntate siempre como {p_name} de {c_name}.
2. {formality_instruction}
3. {regional_instruction}
4. Escribe siempre en 1 a 3 burbujas cortas. NUNCA envíes bloques largos de texto.
5. Usa solo signos de cierre ('?' y '!'). Jamás uses signos invertidos ('¿' o '¡') porque delatan un bot.
6. Si el paciente pide hablar con un humano o consulta algo médico complejo, muestra empatía e informa que lo transfieres de inmediato.
"""
        return prompt.strip()


# Global Singleton
psychological_mirror = PsychologicalStyleMirror()
