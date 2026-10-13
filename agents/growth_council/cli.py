"""CLI interface for Santiago to interact with the Firby Growth Council.
"""

import sys
import json
import argparse
from pathlib import Path
from .council import FirbyGrowthCouncil
from .agents import ComplianceGuardianAgent, SkepticProspectAgent

def main():
    parser = argparse.ArgumentParser(description="Firby Growth Council — Sistema de 8 Agentes de Publicidad B2B")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Command: campaign
    camp_parser = subparsers.add_parser("campaign", help="Ejecutar el pipeline completo de los 8 agentes para un sector")
    camp_parser.add_argument("--sector", required=True, help="Sector o nicho (ej. clinicas, abogados, agencias, inmobiliarias)")
    camp_parser.add_argument("--context", default="", help="Contexto específico u oferta adicional")
    camp_parser.add_argument("--output", default="", help="Ruta de archivo JSON donde guardar el dossier")

    # Command: brainstorm
    brain_parser = subparsers.add_parser("brainstorm", help="Generar 3-5 ángulos de dolor e ideas para un sector")
    brain_parser.add_argument("--sector", required=True, help="Sector o nicho")

    # Command: audit
    audit_parser = subparsers.add_parser("audit", help="Auditar un texto publicitario contra las reglas de Firby")
    audit_parser.add_argument("--text", required=True, help="Texto o copy a auditar")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    print(f"\n=======================================================")
    print(f"FIRBY GROWTH COUNCIL — MOTOR DE ADQUISICIÓN B2B")
    print(f"=======================================================\n")

    if args.command == "brainstorm":
        print(f"-> Agente 1 (Hunter de Dolores) analizando sector: '{args.sector}'...")
        res = FirbyGrowthCouncil.brainstorm_sector(args.sector)
        print(f"\nAnalisis de Mercado:\n{res.market_insight}\n")
        print("Angulos Generados:")
        for idx, idea in enumerate(res.ideas, 1):
            print(f"\n[{idx}] {idea.angle_name} (Avatar: {idea.target_avatar})")
            print(f"    Dolor: {idea.pain_point}")
            print(f"    Hook 3s: \"{idea.hook_3s}\"")
            print(f"    Mecanismo: {idea.mechanism}")
            print(f"    CTA: {idea.offer_cta}")

    elif args.command == "audit":
        print("-> Agente 5 (Auditor de Compliance) analizando material...")
        res = ComplianceGuardianAgent.audit_ad_material(args.text)
        print(f"\nResultado: {'APROBADO' if res.passed else 'RECHAZADO'} (Puntaje: {res.compliance_score}/10)")
        print(f"Emoji Detectado: {res.emoji_detected}")
        print(f"Infraccion de Precios: {res.pricing_violation}")
        print(f"Confusion de Canales: {res.channel_confusion}")
        if res.identified_issues:
            print("\nProblemas identificados:")
            for i in res.identified_issues:
                print(f"  - {i}")
        if res.mandatory_corrections:
            print("\nCorrecciones obligatorias:")
            for c in res.mandatory_corrections:
                print(f"  - {c}")

    elif args.command == "campaign":
        print(f"-> Lanzando sesion de trabajo con los 8 agentes para el sector: '{args.sector}'...\n")
        dossier = FirbyGrowthCouncil.execute_full_campaign(args.sector, args.context)
        
        print("\n-------------------------------------------------------")
        print("1. SECTOR IDEACIÓN & HOOKS (Hunter + Copywriter)")
        print("-------------------------------------------------------")
        print(f"Angulo: {dossier.idea.angle_name}")
        print(f"Avatar: {dossier.idea.target_avatar}")
        print(f"Dolor: {dossier.idea.pain_point}")
        print(f"Hook 3s: \"{dossier.idea.hook_3s}\"")
        print(f"\nTitular Meta/Google: {dossier.copy_pack.headline}")
        print(f"Primary Text:\n{dossier.copy_pack.primary_text}")
        print(f"\nGuion Video 9:16:\n{dossier.copy_pack.video_script_9_16}")

        print("\n-------------------------------------------------------")
        print("2. SECTOR DIRECCIÓN CREATIVA (Video Motion + Craft)")
        print("-------------------------------------------------------")
        print(f"Video: {dossier.visual_spec.video_title} ({dossier.visual_spec.aspect_ratio})")
        print(f"Split Screen Izquierda (Web): {dossier.visual_spec.split_screen_left_web}")
        print(f"Split Screen Derecha (WhatsApp Dueno): {dossier.visual_spec.split_screen_right_whatsapp}")
        print(f"\nEstatico: {dossier.static_spec.creative_type} ({dossier.static_spec.dimensions})")
        print(f"Titular Grafico: {dossier.static_spec.headline_overlay}")
        print(f"Badge: {dossier.static_spec.badge_callout}")

        print("\n-------------------------------------------------------")
        print("3. SECTOR PROBADORES & QA (Compliance + Escéptico)")
        print("-------------------------------------------------------")
        print(f"Compliance: {'APROBADO' if dossier.compliance.passed else 'RECHAZADO'} ({dossier.compliance.compliance_score}/10)")
        print(f"Escéptico ({dossier.skeptic_test.persona_type}): Credibilidad {dossier.skeptic_test.believability_score}/10")
        print(f"Objecion Principal: {dossier.skeptic_test.initial_reaction}")
        print(f"Contraargumento Letal: {dossier.skeptic_test.hardened_counter_argument}")

        print("\n-------------------------------------------------------")
        print("4. SECTOR OPERACIONES & PAUTA (Media Buyer + CRO)")
        print("-------------------------------------------------------")
        print(f"Objetivo: {dossier.media_plan.campaign_objective}")
        print(f"Segmentacion: {', '.join(dossier.media_plan.target_interests_and_behaviors)}")
        print(f"UTM: {dossier.media_plan.utm_structure}")
        print(f"\nLanding Match Score: {dossier.conversion_plan.message_match_score}/10")
        print(f"Hero Recomendado: {dossier.conversion_plan.landing_headline_recommendation}")
        print(f"Saludo Inicial Widget: \"{dossier.conversion_plan.widget_initial_greeting}\"")

        if args.output:
            out_p = Path(args.output)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            with open(out_p, "w", encoding="utf-8") as f:
                f.write(dossier.model_dump_json(indent=2))
            print(f"\nDossier guardado exitosamente en: {args.output}")

if __name__ == "__main__":
    main()
