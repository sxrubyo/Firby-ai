"""firby_mirroring.py — Perfil social del usuario para espejeo psicológico inconsciente.

Detecta: región, formalidad, energía, ritmo, emojis, tratamiento (tú/vos/usted).
Solo afecta el audio (muletillas regionales) y el hint sutil en el system prompt del LLM.
Nunca fuerza jerga del usuario. Nunca copia abreviaturas.
"""

from __future__ import annotations
import logging
import random
import re
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

log = logging.getLogger("firby.mirroring")

# ─── Perfil social ───────────────────────────────────────────────────────

@dataclass
class SocialProfile:
    region: str = "neutro"
    confidence_region: float = 0.0
    formality: str = "neutral"      # casual | neutral | formal
    energy: str = "neutral"         # low | neutral | high
    rhythm: str = "neutral"         # short (1 burbuja) | balanced (2) | expansive (3+)
    emoji_usage: str = "neutral"    # none | low | high
    address_form: str = "tu"        # tu | vos | usted
    last_updated: float = 0.0
    num_analyses: int = 0

    def is_stale(self, max_age: float = 300.0) -> bool:
        return (time.time() - self.last_updated) > max_age

    def should_refresh(self, msg_count: int) -> bool:
        return self.num_analyses == 0 or (self.num_analyses < 5 and msg_count % 10 == 0)

    def to_hint(self) -> str:
        parts = []
        if self.region != "neutro" and self.confidence_region >= 0.5:
            parts.append(f"region: {self.region}")
        if self.formality != "neutral":
            parts.append(f"formalidad: {self.formality}")
        if self.energy != "neutral":
            parts.append(f"energia: {self.energy}")
        if self.address_form != "tu":
            parts.append(f"tratamiento: {self.address_form}")
        if not parts:
            return ""
        return "Perfil conversacion: " + ", ".join(parts) + "."


# ─── Sets de muletillas regionales (SOLO para audio TTS) ─────────────────

REGIONAL_MULETILLAS: Dict[str, Tuple[List[str], List[str]]] = {
    "colombia": (
        ["Ehh... ", "Mmm... ", "Pues... ", "Ve... ", "O sea... ",
         "Ahh... ", "Este... ", "Mira... ", "Ehh pues... ", "Bueno... ",
         "A ver... ", "Ehh ve... ", "Sabes que... ", "Oye... ", "Mira pues... "],
        ["... o sea, ", "... ehh, ", "... pues, ", "... este, ",
         "... sabes, ", "... ve, ", "... ehh no se, ", "... digamos, ", "... o sea no, "]
    ),
    "mexico": (
        ["Este... ", "Mmm... ", "Pues... ", "O sea... ", "Mira... ",
         "Ah... ", "Bueno... ", "A ver... ", "Es que... ", "Oye... ",
         "Sabes... ", "Mira pues... ", "Déjame ver... ", "Ehh... "],
        ["... este, ", "... o sea, ", "... sabes, ", "... mmh, ",
         "... pues, ", "... ehh, ", "... mira, ", "... digamos, "]
    ),
    "argentina": (
        ["Bueno... ", "Che... ", "Mirá... ", "Dale... ", "Este... ",
         "Mmm... ", "Ehh... ", "O sea... ", "Mira... ", "Viste... ",
         "Sabés... ", "A ver... ", "Claro... "],
        ["... che, ", "... este, ", "... viste, ", "... dale, ",
         "... o sea, ", "... ehh, ", "... sabés, ", "... mirá, "]
    ),
    "chile": (
        ["O sea... ", "Esto... ", "Pues... ", "Mira... ", "Sabís... ",
         "Ehh... ", "Bueno... ", "Mmm... ", "A ver... ", "Dale... ",
         "Cachai... ", "Oye... "],
        ["... cachai, ", "... po, ", "... o sea, ", "... sabís, ",
         "... ehh, ", "... este, ", "... pues, ", "... mira, "]
    ),
    "peru": (
        ["Este... ", "O sea... ", "Mira... ", "Pues... ", "Ah... ",
         "Bueno... ", "Mmm... ", "Ehh... ", "A ver... ", "Oye... ",
         "Sabes... ", "Déjame decirte... "],
        ["... pues, ", "... este, ", "... o sea, ", "... mira, ",
         "... ehh, ", "... sabes, ", "... digamos, "]
    ),
    "espana": (
        ["Bueno... ", "Pues... ", "Este... ", "Mira... ", "A ver... ",
         "Ehh... ", "Mmm... ", "Vale... ", "O sea... ", "Sabes... ",
         "Claro... ", "Hombre... "],
        ["... pues, ", "... este, ", "... sabes, ", "... vale, ",
         "... o sea, ", "... ehh, ", "... digamos, ", "... mira, "]
    ),
}

DEFAULT_REGION = "colombia"


def get_muletillas(region: str = DEFAULT_REGION) -> Tuple[List[str], List[str]]:
    start_fillers, mid_fillers = REGIONAL_MULETILLAS.get(
        region, REGIONAL_MULETILLAS[DEFAULT_REGION]
    )
    return start_fillers, mid_fillers


# ─── Agente de detección (Gemini 3.6 Flash) ────────────────────────────

SYSTEM_PROMPT_DETECT = """Eres un analizador de perfil social. Analizas mensajes de WhatsApp y extraes el perfil de QUIEN ESCRIBE.

Devuelve SOLO un JSON con estos campos:
{
  "region": "colombia|mexico|argentina|chile|peru|espana|neutro",
  "confidence_region": 0.0-1.0,
  "formality": "casual|neutral|formal",
  "energy": "low|neutral|high",
  "rhythm": "short|balanced|expansive",
  "emoji_usage": "none|low|high",
  "address_form": "tu|vos|usted"
}

REGLAS:
- Region: detecta por modismos ("parce"=colombia, "wey"=mexico, "che"=argentina, "po/cachai"=chile, "pata/causa"=peru, "vale/tio"=espana). Si no hay suficientes señales, neutro.
- Formality: "formal" si usa usted, saluda con buenos dias/tardes, estructura cuidada. "casual" si abreviado, sin reglas. "neutral" si no hay suficiente senal.
- Energy: "low" si monosilabos (si, no, ok, jaja). "high" si multiples signos, repite letras (holaaaa, siiii), entusiasmo explicito. "neutral" si normal.
- Rhythm: "short" si responde con frases cortas o monosilabos. "expansive" si escribe parrafos o multiples mensajes seguidos desarrollando ideas. "balanced" si normal.
- Emoji_usage: segun frecuencia de emojis en sus mensajes.
- Address_form: detecta si usa "tu", "vos" o "usted" en el texto.

No inventes. Si no hay suficiente informacion, usa "neutro" o "neutral".
Si hay conflictos entre mensajes, prioriza los mas recientes."""


async def detect_social_profile(
    llm_func,
    user_messages: List[str],
    existing_profile: Optional[SocialProfile] = None,
) -> SocialProfile:
    """Analiza los mensajes del usuario y construye/actualiza su perfil social."""
    if not user_messages:
        return existing_profile or SocialProfile()

    sample = "\n---\n".join(user_messages[-6:])
    prompt = f"Mensajes del usuario:\n{sample}\n\n---\nDevuelve el perfil JSON."

    try:
        raw = await llm_func(SYSTEM_PROMPT_DETECT, prompt, temp=0.2, max_t=500, model_tier="fast")
        if not raw:
            return existing_profile or SocialProfile()
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            raw = raw.rsplit("```", 1)[0]
        import json
        data = json.loads(raw.strip())
    except Exception as e:
        log.debug(f"[mirroring] detect parse error: {e}")
        if existing_profile:
            existing_profile.num_analyses += 1
            existing_profile.last_updated = time.time()
            return existing_profile
        return SocialProfile()

    profile = SocialProfile(
        region=data.get("region", "neutro"),
        confidence_region=data.get("confidence_region", 0.0),
        formality=data.get("formality", "neutral"),
        energy=data.get("energy", "neutral"),
        rhythm=data.get("rhythm", "neutral"),
        emoji_usage=data.get("emoji_usage", "neutral"),
        address_form=data.get("address_form", "tu"),
        last_updated=time.time(),
        num_analyses=(existing_profile.num_analyses + 1) if existing_profile else 1,
    )

    # Si confianza baja, mantener perfil anterior si existe
    if existing_profile and profile.confidence_region < 0.4:
        profile.region = existing_profile.region
        profile.confidence_region = existing_profile.confidence_region

    log.info(f"[mirroring] perfil: region={profile.region}({profile.confidence_region:.1f}) "
             f"formal={profile.formality} energia={profile.energy} "
             f"ritmo={profile.rhythm} emoji={profile.emoji_usage} "
             f"trato={profile.address_form}")
    return profile


# ─── Hint para system prompt del LLM ────────────────────────────────────

def build_llm_hint(profile: SocialProfile) -> str:
    """Genera un hint sutil para inyectar en el system prompt del LLM.
    No instruye directamente — solo da contexto para que el LLM calibre naturalmente.
    """
    hints = []

    if profile.formality == "casual" and profile.energy == "high":
        hints.append("El usuario escribe casual y con energia. Responde con calor natural, sin estructuras formales.")
    elif profile.formality == "casual":
        hints.append("El usuario escribe casual. Responde relajado, como con un conocido.")
    elif profile.formality == "formal":
        hints.append("El usuario escribe formal. Responde con respeto manteniendo calidez.")

    if profile.energy == "high":
        hints.append("Muestra entusiasmo sincero en tu tono.")
    elif profile.energy == "low":
        hints.append("Ve al grano, sin rodeos ni excesiva efusividad.")

    if profile.rhythm == "short":
        hints.append("El usuario responde breve. No satures con informacion densa de una — ve al grano.")
    elif profile.rhythm == "expansive":
        hints.append("El usuario se explaya. Puedes desarrollar tus respuestas con naturalidad.")

    if profile.emoji_usage == "none":
        hints.append("Sin emojis.")
    elif profile.emoji_usage == "high":
        hints.append("Usa emojis con naturalidad si aportan calidez.")

    if profile.address_form == "usted":
        hints.append("Trata de usted.")
    elif profile.address_form == "vos":
        hints.append("Trata de vos.")

    if not hints:
        return ""

    return "---\n" + "\n".join(hints) + "\n---"


# ─── Cache por chat_id ─────────────────────────────────────────────────

class ProfileCache:
    """Cache simple de perfiles por chat_id con expiracion."""

    def __init__(self):
        self._profiles: Dict[str, SocialProfile] = {}

    def get(self, chat_id: str) -> Optional[SocialProfile]:
        return self._profiles.get(chat_id)

    def set(self, chat_id: str, profile: SocialProfile):
        self._profiles[chat_id] = profile

    def get_or_create(self, chat_id: str) -> SocialProfile:
        if chat_id not in self._profiles:
            self._profiles[chat_id] = SocialProfile()
        return self._profiles[chat_id]


profile_cache = ProfileCache()
