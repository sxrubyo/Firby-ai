"""Pydantic schemas for typed, structured outputs across all 8 agents.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

# --- SECTOR 1: IDEAS & HOOKS ---
class IdeaBrief(BaseModel):
    angle_name: str = Field(description="Nombre clave del ángulo (ej. Citas Nocturnas Perdidas)")
    target_avatar: str = Field(description="Nicho exacto: médicos, clínicas odontológicas, abogados, agencias, consultores")
    pain_point: str = Field(description="Dolor financiero u operativo exacto y visceral del dueño del negocio")
    hook_3s: str = Field(description="Gancho de apertura de los primeros 3 segundos para detener el scroll")
    mechanism: str = Field(description="Cómo Firby resuelve el dolor: agenda en Google Calendar en la web y notifica por WhatsApp al dueño")
    offer_cta: str = Field(description="Llamado a la acción con la oferta: Prueba 7 días gratis. Cancela en 1 clic")

class Sector1Output(BaseModel):
    market_insight: str = Field(description="Análisis del estado del mercado y por qué los bots tradicionales fallan")
    ideas: List[IdeaBrief] = Field(description="Lista de 3 a 5 ángulos de alta conversión")

# --- SECTOR 2: DIRECT-RESPONSE COPYWRITING ---
class AdCopyPack(BaseModel):
    angle_reference: str = Field(description="Ángulo al que responde este copy")
    headline: str = Field(description="Titular principal para Meta Ads o Google Search (máx 60 caracteres)")
    primary_text: str = Field(description="Texto principal del anuncio en español de negocios directo, sin clichés ni emojis")
    description_line: str = Field(description="Línea secundaria visible debajo del titular")
    video_script_9_16: str = Field(description="Guión paso a paso para video vertical de 30-45 segundos")
    carousel_slides: List[str] = Field(description="Textos de 3 a 5 tarjetas para formato carrusel de alta retención")

# --- SECTOR 3: DIRECCIÓN DE ARTE Y VIDEO MOTION ---
class VisualDirectorBrief(BaseModel):
    video_title: str = Field(description="Título del concepto visual")
    aspect_ratio: str = Field(description="Formato: 9:16 vertical (Reels/TikTok/Stories) o 1:1 cuadrado")
    split_screen_left_web: str = Field(description="Qué ocurre en pantalla izquierda: visitante interactuando con Firby en la web")
    split_screen_right_whatsapp: str = Field(description="Qué ocurre en pantalla derecha: WhatsApp del dueño recibiendo la alerta en vivo")
    motion_timeline: List[str] = Field(description="Hitos de la animación segundo a segundo (0-3s, 3-10s, 10-25s, 25-35s)")
    on_screen_text_overlays: List[str] = Field(description="Textos en pantalla de alto contraste (Neue Montreal, blanco y verde neón #b9fa01)")

# --- SECTOR 4: DISEÑO ESTÁTICO Y BANNERS ---
class StaticCreativeSpec(BaseModel):
    creative_type: str = Field(description="Tipo: Banner B2B, Infografía comparativa o Captura de producto con anotaciones")
    dimensions: str = Field(description="1080x1080 (1:1) o 1080x1350 (4:5)")
    background_treatment: str = Field(description="Tratamiento de fondo: Obsidiana #0f0f11 con sutil gradiente radial")
    headline_overlay: str = Field(description="Titular gráfico en la imagen sin emojis")
    badge_callout: str = Field(description="Badge táctil de producto (ej. Google Calendar Sync en Vivo)")
    proof_metric: str = Field(description="Métrica o elemento de prueba visual")
    visual_layout_description: str = Field(description="Descripción detallada para el diseñador gráfico o generador")

# --- SECTOR 5: AUDITORÍA Y COMPLIANCE ---
class ComplianceAudit(BaseModel):
    passed: bool = Field(description="True si cumple el 100% de las reglas inquebrantables")
    compliance_score: int = Field(description="Puntuación de 1 a 10")
    emoji_detected: bool = Field(description="True si se detectó algún emoji prohibido")
    pricing_violation: bool = Field(description="True si se mencionó $1.000 COP o tarifas no oficiales")
    channel_confusion: bool = Field(description="True si insinúa que el visitante habla por WhatsApp")
    identified_issues: List[str] = Field(description="Lista de fallos detectados")
    mandatory_corrections: List[str] = Field(description="Correcciones obligatorias aplicadas")

# --- SECTOR 6: SIMULADOR DE PROSPECTO ESCÉPTICO ---
class SkepticCritique(BaseModel):
    persona_type: str = Field(description="Arquetipo: Dueño de clínica, socio de agencia, abogado senior o comerciante")
    initial_reaction: str = Field(description="Primera reacción visceral y desconfiada ante el anuncio")
    unanswered_objections: List[str] = Field(description="Dudas o huecos que el anuncio no resolvió")
    believability_score: int = Field(description="Nivel de credibilidad del 1 al 10")
    hardened_counter_argument: str = Field(description="Cómo blindar el anuncio para aniquilar esta objeción")

# --- SECTOR 7: MEDIA BUYING & ARQUITECTURA DE TRÁFICO ---
class MediaPlan(BaseModel):
    campaign_objective: str = Field(description="Objetivo de campaña en Meta Ads: Clientes potenciales o Conversiones")
    target_interests_and_behaviors: List[str] = Field(description="Segmentación sugerida en Meta/Instagram")
    suggested_budget_distribution: str = Field(description="Distribución de pauta: 60% Prospección, 30% Retargeting, 10% Testing")
    utm_structure: str = Field(description="Nomenclatura limpia de UTMs para tracking")
    bidding_strategy: str = Field(description="Estrategia de puja recomendada")

# --- SECTOR 8: OPTIMIZACIÓN DE CONVERSIÓN & MATCH ---
class ConversionOptimizationPlan(BaseModel):
    message_match_score: int = Field(description="Coherencia entre anuncio y landing page (1 a 10)")
    landing_headline_recommendation: str = Field(description="Titular exacto que debe recibir al usuario en la web")
    widget_initial_greeting: str = Field(description="Saludo contextual con el que Firby debe abrir automáticamente")
    friction_elimination_tips: List[str] = Field(description="Puntos de fricción a eliminar en el flujo de registro")

# --- DOSSIER CONSOLIDADO DE CAMPAÑA ---
class FullCampaignDossier(BaseModel):
    sector_name: str = Field(description="Sector o nicho objetivo de la campaña")
    idea: IdeaBrief
    copy_pack: AdCopyPack
    visual_spec: VisualDirectorBrief
    static_spec: StaticCreativeSpec
    compliance: ComplianceAudit
    skeptic_test: SkepticCritique
    media_plan: MediaPlan
    conversion_plan: ConversionOptimizationPlan
