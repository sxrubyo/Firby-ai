#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firby Preflight & Instruction Refinement Pipeline
================================================
Orquestador que:
1. Toma una instrucción de Santiago (Santi).
2. Refina el objetivo, componentes afectados y reglas críticas.
3. Genera el mapa mental visual técnico en PNG (firby_mindmap.py).
4. Si la instrucción afecta la interfaz, renderiza un mockup/preflight visual
   en sandbox o inyección en memoria (firby_visual_preflight.py).
5. Devuelve las rutas de los artefactos visuales para revisión previa.
"""
import os
import sys
import json
import time
import argparse
from pathlib import Path

ARTIFACT_DIR = "/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c"
SCRIPTS_DIR = "/home/ubuntu/firby/scripts"

sys.path.insert(0, SCRIPTS_DIR)
import firby_mindmap
import firby_visual_preflight

def run_pipeline(title: str, objective: str, components: list, rules: list, preview_url: str = None, preview_css: str = None, preview_selector: str = None, preview_click: str = None) -> dict:
    """Ejecuta el ciclo de mapa mental + preflight visual antes de aplicar cambios."""
    ts = int(time.time() * 1000)
    
    # 1. Generar Mapa Mental
    mindmap_path = os.path.join(ARTIFACT_DIR, f"mindmap_{ts}.png")
    firby_mindmap.create_instruction_mindmap(
        title=title,
        objective=objective,
        components=components,
        rules=rules,
        output_path=mindmap_path
    )
    
    # 2. Generar Preflight Visual si aplica
    preview_path = None
    if preview_url:
        preview_path = os.path.join(ARTIFACT_DIR, f"preflight_preview_{ts}.png")
        firby_visual_preflight.render_live_injection(
            url=preview_url,
            css=preview_css,
            selector=preview_selector,
            click=preview_click,
            output_path=preview_path
        )
        
    return {
        "status": "success",
        "mindmap_path": mindmap_path,
        "preview_path": preview_path,
        "timestamp": ts
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Firby Instruction & Preflight Pipeline")
    parser.add_argument("--title", required=True, help="Título del requerimiento")
    parser.add_argument("--objective", required=True, help="Objetivo técnico refinado")
    parser.add_argument("--components", nargs="+", required=True, help="Componentes a modificar")
    parser.add_argument("--rules", nargs="+", default=["Canario Santi", "Cero Emojis", "Cero 1000 COP"], help="Reglas invariantes")
    parser.add_argument("--preview-url", help="URL viva para renderizar sandbox preflight")
    parser.add_argument("--preview-css", help="CSS de prueba a inyectar en memoria")
    parser.add_argument("--preview-selector", help="Selector CSS del elemento a previsualizar")
    parser.add_argument("--preview-click", help="Selector a clickear antes del snapshot")
    
    args = parser.parse_args()
    res = run_pipeline(
        title=args.title,
        objective=args.objective,
        components=args.components,
        rules=args.rules,
        preview_url=args.preview_url,
        preview_css=args.preview_css,
        preview_selector=args.preview_selector,
        preview_click=args.preview_click
    )
    print(json.dumps(res, indent=2))
