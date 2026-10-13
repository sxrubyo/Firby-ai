#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firby Mindmap Engine
====================
Genera mapas mentales visuales de alta resolución (PNG/SVG) a partir de instrucciones
del usuario utilizando Mermaid CLI y Puppeteer en modo oscuro (#0B0F12).
Permite visualizar la descomposición técnica y las reglas antes de ejecutar código.
"""
import os
import sys
import time
import argparse
import subprocess
from pathlib import Path

DEFAULT_ARTIFACT_DIR = "/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c"
PUPPETEER_CONFIG = "/home/ubuntu/.puppeteer.json"

def ensure_puppeteer_config():
    if not os.path.exists(PUPPETEER_CONFIG):
        with open(PUPPETEER_CONFIG, "w") as f:
            f.write('{"args": ["--no-sandbox", "--disable-setuid-sandbox"]}\n')

def generate_mindmap(mermaid_content: str, output_path: str = None) -> str:
    """Renderiza contenido Mermaid (mindmap o graph) a PNG."""
    ensure_puppeteer_config()
    
    if not output_path:
        ts = int(time.time() * 1000)
        output_path = os.path.join(DEFAULT_ARTIFACT_DIR, f"mindmap_{ts}.png")
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    tmp_mmd = f"/tmp/mindmap_{int(time.time())}.mmd"
    with open(tmp_mmd, "w", encoding="utf-8") as f:
        f.write(mermaid_content)
        
    cmd = [
        "mmdc",
        "-p", PUPPETEER_CONFIG,
        "-i", tmp_mmd,
        "-o", output_path,
        "-b", "#0B0F12",
        "-t", "dark",
        "--size", "1200",
        "-s", "2"
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(tmp_mmd):
        try:
            os.unlink(tmp_mmd)
        except Exception:
            pass
            
    if res.returncode == 0 and os.path.exists(output_path):
        return output_path
    else:
        raise RuntimeError(f"Error generando mindmap con mmdc: {res.stderr or res.stdout}")

def create_instruction_mindmap(title: str, objective: str, components: list, rules: list, output_path: str = None) -> str:
    """Genera un mapa mental estandarizado para una instrucción de usuario."""
    clean_title = title.replace('(', '').replace(')', '').replace('"', '').replace("'", "")
    lines = ["mindmap", f"  root(({clean_title}))"]
    
    lines.append("    Objetivo")
    clean_obj = objective.replace('(', '').replace(')', '').replace('"', '').replace("'", "")
    lines.append(f"      {clean_obj}")
    
    lines.append("    Componentes")
    for comp in components:
        clean_c = comp.replace('(', '').replace(')', '').replace('"', '').replace("'", "")
        lines.append(f"      {clean_c}")
        
    lines.append("    Reglas")
    for rule in rules:
        clean_r = rule.replace('(', '').replace(')', '').replace('"', '').replace("'", "")
        lines.append(f"      {clean_r}")
        
    lines.append("    Verificacion")
    lines.append("      Playwright Real Browser")
    lines.append("      Evidencia Visual PNG")
    
    mermaid_text = "\n".join(lines) + "\n"
    return generate_mindmap(mermaid_text, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Firby Mindmap Engine CLI")
    parser.add_argument("--mermaid", help="Ruta a archivo .mmd o string raw mermaid")
    parser.add_argument("--title", default="Instrucción de Usuario", help="Título central del mapa mental")
    parser.add_argument("--objective", default="Ejecución precisa sin suposiciones", help="Objetivo principal")
    parser.add_argument("--components", nargs="+", default=["Frontend Widget", "Backend API"], help="Componentes afectados")
    parser.add_argument("--rules", nargs="+", default=["Canario Santi", "Cero Emojis", "Cero Suposiciones"], help="Reglas aplicables")
    parser.add_argument("--out", default=None, help="Ruta de salida del archivo PNG")
    
    args = parser.parse_args()
    if args.mermaid:
        if os.path.exists(args.mermaid):
            with open(args.mermaid, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = args.mermaid
        path = generate_mindmap(content, args.out)
    else:
        path = create_instruction_mindmap(args.title, args.objective, args.components, args.rules, args.out)
    print(f"Mindmap generado exitosamente en: {path}")
