"""Designer Agent: Real-World References & Architecture Spec for Firby Ideas Workspace.
Produces an elite, non-AI-looking UI design dossier based on Linear, Attio, Raycast, and Cosmos.
"""

import json
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List

from .config import client, ACTIVE_MODELS_CASCADE
from .agents import call_gemini_structured

DESIGNER_SYSTEM_PROMPT = """Eres el Lead Product & UI/UX Designer de Firby.
Tu mentor y estándar estético son las mejores interfaces de software B2B del mundo: Linear.app, Attio.com, Raycast, Vercel, Supabase y Cosmos.so.

REGLA DE ORO DE SANTIAGO (EL FUNDADOR):
"CERO ESTÉTICA DE IA".
¿Qué significa CERO ESTÉTICA DE IA?
- PROHIBIDO: Gradientes violetas/púrpuras genéricos, sombras borrosas gigantes sin sentido, tarjetas idénticas de plantilla barata, ilustraciones 3D hinchadas estilo Dribbble 2021, espacios vacíos sin utilidad, o lenguaje decorativo inútil.
- OBLIGATORIO (CRAFT DE INGENIERÍA REAL):
  1. Alta densidad de información legible (estilo Attio y Linear).
  2. Superficies de obsidiana profunda (#08080a, #0f1015, #14161f) con bordes técnicos de 1px a 6-8% de opacidad y reflejo interior superior sutil (inset 0 1px 0 rgba(255,255,255,0.06)).
  3. Acentos táctiles mínimos: Verde lima neón (#b9fa01) reservado exclusivamente para estados activos, badges de verificación y CTAs primarios.
  4. Tipografía con ritmo suizo y tracking calibrado: Neue Montreal, Inter, Geist Mono para métricas y hashes.
  5. Navegación rápida por teclado (CMD+K, filtros instantáneos).
  6. Drawer lateral (Slide-over) para inspeccionar detalles sin perder el contexto del lienzo.

Tu objetivo: Diseñar la arquitectura visual, interacción, vistas y referencias exactas para el nuevo 'WORKSPACE DE IDEAS' (Laboratorio de Adquisición y Creativos) en el panel de Firby.
"""

class TokenSpec(BaseModel):
    background_obsidian: str = Field(..., description="Color de fondo de obsidiana principal")
    surface_cards: str = Field(..., description="Superficie de tarjetas y paneles")
    border_technical: str = Field(..., description="Borde técnico sutil")
    accent_tactical_lime: str = Field(..., description="Acento verde lima neón para badges y CTAs")
    typography_primary: str = Field(..., description="Tipografía principal y pesos")
    typography_mono: str = Field(..., description="Tipografía monoespaciada para métricas y atajos")

class SlideOverDrawerSpec(BaseModel):
    header_section: str = Field(..., description="Contenido de cabecera con status, selector de etapa y botón de cerrar")
    tabs_or_sections: List[str] = Field(..., description="Pestañas o secciones internas (Copywriting, Assets Visuales, Canary QA, Pauta Meta)")
    visual_asset_preview_layout: str = Field(..., description="Cómo se previsualizan los anuncios estáticos 4:5 y los videos 9:16")
    action_footer: str = Field(..., description="Botones de acción (Exportar a Meta, Re-generar copy, Probar en simulador)")

class QuickActionBarSpec(BaseModel):
    left_controls: List[str] = Field(..., description="Controles de la izquierda (Selector de Nicho/Sector, Filtros de Etapa)")
    center_search: str = Field(..., description="Barra de búsqueda rápida con atajo CMD+K")
    right_actions: List[str] = Field(..., description="Botones de acción (+ Nueva Campaña, Sincronizar con Paperclip, Vista Grid/Table)")

class ReferenceBreakdown(BaseModel):
    product_name: str = Field(..., description="Nombre del producto real (ej. Linear, Attio, Raycast, Cosmos, Vercel)")
    specific_pattern: str = Field(..., description="Patrón de UI exacto analizado")
    why_it_works: str = Field(..., description="Por qué funciona y por qué NO parece IA")
    firby_adaptation: str = Field(..., description="Cómo adaptamos exactamente este patrón al Workspace de Ideas de Firby")

class WorkspaceViewSpec(BaseModel):
    view_name: str = Field(..., description="Nombre de la vista")
    layout_structure: str = Field(..., description="Estructura exacta del layout")
    key_interactions: List[str] = Field(..., description="Interacciones y atajos")
    data_points_per_item: List[str] = Field(..., description="Datos visibles en cada tarjeta/fila")

class IdeasWorkspaceDesignDossier(BaseModel):
    design_manifesto: str = Field(..., description="Manifiesto visual que garantiza cero estética genérica de IA")
    color_and_type_tokens: TokenSpec = Field(..., description="Tokens exactos de color, superficies, bordes y tipografía")
    real_world_references: List[ReferenceBreakdown] = Field(..., description="Referencias de productos reales analizados a fondo")
    three_view_modes: List[WorkspaceViewSpec] = Field(..., description="Especificación de las 3 vistas esenciales del workspace")
    slide_over_drawer_spec: SlideOverDrawerSpec = Field(..., description="Diseño del drawer lateral de inspección de campaña/idea")
    quick_action_bar_spec: QuickActionBarSpec = Field(..., description="Barra superior de acciones rápidas")

def generate_workspace_design_dossier() -> IdeasWorkspaceDesignDossier:
    prompt = """Elabora el dossier definitivo de diseño y arquitectura de UI para el 'WORKSPACE DE IDEAS Y CREATIVOS' de Firby.
Analiza referencias reales de:
1. Linear (el Issue Drawer, los filtros de ciclo y la vista de tablero/lista).
2. Attio (la flexibilidad de atributos personalizados, tags con micro-dots y tabla densa).
3. Raycast (la sobriedad, la barra de comandos y los metadatos contextuales).
4. Cosmos / Midjourney / Krea (cómo estructuran una galería de ideas visuales sin saturar).

Entrega la especificación técnica completa con componentes, tokens de color, estructura de carpetas sugerida para Next.js / Tailwind y comportamiento de interacción."""

    return call_gemini_structured(DESIGNER_SYSTEM_PROMPT, prompt, IdeasWorkspaceDesignDossier)

if __name__ == "__main__":
    print("[*] Diseñador Lead activado. Investigando referencias reales de Linear, Attio, Raycast y Cosmos...")
    dossier = generate_workspace_design_dossier()
    out_file = Path("/home/ubuntu/firby/agents/growth_council/ideas_workspace_design_dossier.json")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(dossier.model_dump_json(indent=2))
    print(f"[OK] Dossier de diseño guardado exitosamente en: {out_file}")
