"""Orchestrator for the Firby Growth Council.
Assembles the 8 agents in an autonomous, cohesive pipeline.
"""

import json
from .agents import (
    HunterStrategistAgent,
    DirectResponseCopywriterAgent,
    VideoScreenplayDirectorAgent,
    StaticCraftDesignerAgent,
    ComplianceGuardianAgent,
    SkepticProspectAgent,
    MediaBuyingArchitectAgent,
    ConversionRateOptimizerAgent,
)
from .schemas import FullCampaignDossier, Sector1Output, ComplianceAudit, SkepticCritique

class FirbyGrowthCouncil:
    """Consejo de Crecimiento y Publicidad de Firby compuesto por 8 agentes de IA especializados."""

    @classmethod
    def brainstorm_sector(cls, sector_name: str, context: str = "") -> Sector1Output:
        """Fase 1: El Hunter investiga dolores y genera los ángulos iniciales."""
        return HunterStrategistAgent.generate_angles(sector_name, context)

    @classmethod
    def execute_full_campaign(cls, sector_name: str, context: str = "") -> FullCampaignDossier:
        """Ejecuta el pipeline completo de los 8 agentes en cadena con retroalimentacion en vivo."""
        import sys
        
        # 1. Ideación & Ángulos
        print("[1/8] Agente 1 (IdeaHunter): Analizando friccion y dolores del mercado...", flush=True)
        sector1 = HunterStrategistAgent.generate_angles(sector_name, context)
        if not sector1.ideas:
            raise ValueError(f"No se pudieron generar ideas para el sector {sector_name}")
        top_idea = sector1.ideas[0]
        print(f"      -> Angulo seleccionado: '{top_idea.angle_name}'", flush=True)

        # 2. Redacción de Copy
        print("[2/8] Agente 2 (CopyChief): Redactando titulares, copies y guion...", flush=True)
        angle_summary = f"Ángulo: {top_idea.angle_name}\nAvatar: {top_idea.target_avatar}\nDolor: {top_idea.pain_point}\nHook: {top_idea.hook_3s}\nMecanismo: {top_idea.mechanism}\nOferta: {top_idea.offer_cta}"
        copy_pack = DirectResponseCopywriterAgent.write_ad_pack(angle_summary)
        print(f"      -> Titular principal: '{copy_pack.headline}'", flush=True)

        # 3. Dirección de Arte & Video
        print("[3/8] Agente 3 (VisualDirector): Diseñando storyboard 9:16 y split-screen...", flush=True)
        visual_spec = VideoScreenplayDirectorAgent.plan_video_ad(copy_pack.model_dump_json(indent=2))
        print(f"      -> Concepto de video: '{visual_spec.video_title}'", flush=True)

        # 4. Diseño Estático
        print("[4/8] Agente 4 (AssetBuilder): Especificando creativos estaticos y UI craft...", flush=True)
        static_spec = StaticCraftDesignerAgent.design_static_spec(f"{angle_summary}\nTitular: {copy_pack.headline}\nTexto: {copy_pack.primary_text}")
        print(f"      -> Tipo de creativo: '{static_spec.creative_type}'", flush=True)

        # 5. Auditoría de Compliance (Canary Rules)
        print("[5/8] Agente 5 (BrandAuditor): Auditando reglas inquebrantables de marca...", flush=True)
        raw_material = f"TITULAR: {copy_pack.headline}\nTEXTO: {copy_pack.primary_text}\nGUIÓN VIDEO: {visual_spec.split_screen_left_web} | {visual_spec.split_screen_right_whatsapp}\nESTÁTICO: {static_spec.headline_overlay}"
        compliance = ComplianceGuardianAgent.audit_ad_material(raw_material)
        print(f"      -> Compliance: {'APROBADO' if compliance.passed else 'OBSERVADO'} (Score: {compliance.compliance_score}/10)", flush=True)

        # 6. Prueba con Prospecto Escéptico
        print("[6/8] Agente 6 (Skeptic): Ejecutando prueba de estres con comprador real...", flush=True)
        skeptic_test = SkepticProspectAgent.stress_test_ad(raw_material, persona_type=f"Dueño de negocio de {sector_name}")
        print(f"      -> Credibilidad percibida: {skeptic_test.believability_score}/10", flush=True)

        # 7. Media Buying & Tráfico
        print("[7/8] Agente 7 (MediaPlanner): Diseñando plan de medios y segmentacion B2B...", flush=True)
        media_plan = MediaBuyingArchitectAgent.create_media_plan(sector_name, copy_pack.headline)
        print(f"      -> Audiencia objetivo: {len(media_plan.target_interests_and_behaviors)} segmentos", flush=True)

        # 8. CRO & Match de Mensaje
        print("[8/8] Agente 8 (FunnelOptimizer): Alineando landing page y widget web...", flush=True)
        conversion_plan = ConversionRateOptimizerAgent.optimize_landing_match(copy_pack.headline, sector_name)
        print(f"      -> Message-Match Score: {conversion_plan.message_match_score}/10", flush=True)
        print("[OK] Sesión completa del Consejo finalizada con éxito.", flush=True)

        return FullCampaignDossier(
            sector_name=sector_name,
            idea=top_idea,
            copy_pack=copy_pack,
            visual_spec=visual_spec,
            static_spec=static_spec,
            compliance=compliance,
            skeptic_test=skeptic_test,
            media_plan=media_plan,
            conversion_plan=conversion_plan,
        )
