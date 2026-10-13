#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firby Visual Preflight Engine
=============================
Renderiza vistas previas visuales (mockups/sandboxes) antes de modificar código
en producción o desarrollo.
Soporta:
1. Renderizado de snippets HTML/CSS aislados (Tailwind, dark glass, componentes).
2. Inyección no destructiva de CSS/JS en páginas locales vivas (http://127.0.0.1:8001/8003).
3. Capturas de selectores específicos o vista completa con escala de retina (2x).
"""
import os
import sys
import time
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = "/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c"

def get_default_output(prefix="preflight_preview"):
    ts = int(time.time() * 1000)
    return os.path.join(ARTIFACT_DIR, f"{prefix}_{ts}.png")

def render_snippet(html: str, output_path: str = None, selector: str = None, width: int = 1200, height: int = 800) -> str:
    """Renderiza un fragmento HTML completo en sandbox."""
    if not output_path:
        output_path = get_default_output("snippet")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=2)
        page = context.new_page()
        page.set_content(html, wait_until="networkidle")

        if selector:
            element = page.wait_for_selector(selector, timeout=5000)
            if element:
                element.screenshot(path=output_path)
            else:
                page.screenshot(path=output_path)
        else:
            page.screenshot(path=output_path)
        browser.close()

    return output_path

def render_live_injection(url: str, css: str = None, js: str = None, selector: str = None, click: str = None, hover: str = None, output_path: str = None, width: int = 1280, height: int = 850) -> str:
    """Carga una URL viva e inyecta CSS/JS en memoria antes de capturar el elemento."""
    if not output_path:
        output_path = get_default_output("live_injection")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=2)
        page = context.new_page()
        page.goto(url, wait_until="networkidle", timeout=15000)

        if click:
            try:
                page.wait_for_selector(click, timeout=4000)
                page.click(click)
                page.wait_for_timeout(600)
            except Exception as e:
                print(f"Aviso click: {e}")

        if css:
            page.add_style_tag(content=css)

        if js:
            page.evaluate(js)

        page.wait_for_timeout(400)

        if hover:
            try:
                page.wait_for_selector(hover, timeout=4000)
                page.hover(hover)
                page.wait_for_timeout(300)
            except Exception as e:
                print(f"Aviso hover: {e}")

        if selector:
            element = page.wait_for_selector(selector, timeout=5000)
            if element:
                element.screenshot(path=output_path)
            else:
                page.screenshot(path=output_path)
        else:
            page.screenshot(path=output_path)

        browser.close()

    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Firby Visual Preflight Engine")
    parser.add_argument("--url", help="URL viva a inspeccionar (ej: http://127.0.0.1:8001)")
    parser.add_argument("--snippet-file", help="Ruta de archivo HTML a renderizar en sandbox")
    parser.add_argument("--css", help="CSS arbitrario a inyectar en memoria")
    parser.add_argument("--js", help="JS arbitrario a evaluar en memoria")
    parser.add_argument("--selector", help="Selector CSS del elemento exacto a capturar")
    parser.add_argument("--click", help="Selector a clickear antes de capturar (ej: abrir widget)")
    parser.add_argument("--hover", help="Selector sobre el cual hacer hover")
    parser.add_argument("--out", help="Ruta de destino del PNG")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=850)

    args = parser.parse_args()

    if args.snippet_file:
        with open(args.snippet_file, "r", encoding="utf-8") as f:
            content = f.read()
        res = render_snippet(content, args.out, args.selector, args.width, args.height)
        print(f"Sandbox preview generado: {res}")
    elif args.url:
        res = render_live_injection(args.url, args.css, args.js, args.selector, args.click, args.hover, args.out, args.width, args.height)
        print(f"Live injection preview generado: {res}")
    else:
        print("Error: debe especificar --url o --snippet-file")
        sys.exit(1)
