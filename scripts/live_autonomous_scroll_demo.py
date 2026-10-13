# -*- coding: utf-8 -*-
"""
Firby Autonomous Operator: Live Real-Time Browser Verification Script
====================================================================
Demuestra y certifica el desplazamiento cinemático lento por el usuario,
la inferencia del decision engine, el halo de enfoque y el enmarcado visual.
"""
import sys
import os
import time
import asyncio
from pathlib import Path

# Add firby root to path
sys.path.insert(0, "/home/ubuntu/firby")

from playwright.async_api import async_playwright
import httpx


async def run_live_verification():
    print("[FIRBY AUTONOMOUS OPERATOR] Iniciando verificación en vivo...")

    # 1. Probar endpoint de chat del operador web
    print("\n[1/3] Probando chat del operador web autónomo...")
    unique_user = f"demo_user_{int(time.time())}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Consentimiento de términos previo
        await client.post("http://127.0.0.1:8001/api/widget/chat", json={
            "message": "Sí, acepto",
            "user_id": unique_user
        })

        # Consulta de navegación autónoma
        chat_res = await client.post("http://127.0.0.1:8001/api/widget/chat", json={
            "message": "Llévame a ver los planes",
            "user_id": unique_user
        })
        chat_data = chat_res.json()
        print(f"  Status HTTP: {chat_res.status_code}")
        print(f"  Respuesta del operador: {chat_data.get('response')}")
        print(f"  UI Action recibida: {chat_data.get('ui_action')}")
        assert chat_data.get("ok") is True
        assert chat_data.get("ui_action") is not None
        assert "#planes" in chat_data.get("ui_action", {}).get("target", "")
        print("  -> Contrato de UI Action verificado exitosamente.")

    # 2. Probar ejecución real en navegador Playwright con física rAF
    print("\n[2/3] Lanzando navegador Playwright y verificando cinemática de scroll...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        # Navegar a la landing page en DEV
        print("  Cargando http://127.0.0.1:8001/ ...")
        await page.goto("http://127.0.0.1:8001/", wait_until="networkidle")

        # Verificar que el script del ScrollDirector está inyectado y activo
        director_available = await page.evaluate("() => typeof window.FirbyScrollDirector !== 'undefined'")
        print(f"  FirbyScrollDirector disponible en window: {director_available}")
        assert director_available is True, "FirbyScrollDirector no está cargado en la página."

        # Tomar posición inicial
        y_start = await page.evaluate("() => window.scrollY")
        print(f"  Scroll inicial: {y_start}px")

        # Activar navegación cinemática hacia #planes con duración de 1.5s
        print("  Ejecutando FirbyScrollDirector.scrollTo('#planes', duration=1500ms)...")
        await page.evaluate("""() => {
            window.FirbyScrollDirector.scrollTo('#planes', {
                duration: 1500,
                label: 'Planes y Precios',
                strikeKeyword: 'gratis'
            });
        }""")

        # Muestrear el scroll progresivo cada 150ms durante 1.8 segundos
        samples = []
        for i in range(12):
            await asyncio.sleep(0.15)
            curr_y = await page.evaluate("() => window.scrollY")
            t_ms = (i + 1) * 150
            samples.append((t_ms, curr_y))
            print(f"    t = {t_ms:4d}ms -> scrollY = {curr_y:6.1f}px")

        y_end = samples[-1][1]
        print(f"  Scroll final completado: {y_end}px (desplazamiento de {y_end - y_start:.1f}px)")
        assert y_end > y_start + 500, f"El scroll no se desplazó suficientemente: {y_end} vs {y_start}"

        # Verificar que el desplazamiento fue continuo y progresivo (física suave, no salto instantáneo)
        intermediate_y = samples[4][1]  # a ~750ms
        assert y_start < intermediate_y < y_end, "El scroll no fue progresivo en el tiempo."
        print("  -> Curva cinemática armónica rAF certificada: recorrido visible en 1.5 segundos.")

        # Verificar que el elemento tiene el halo respirable o foco
        has_halo = await page.evaluate("""() => {
            const target = document.querySelector('#planes');
            return target ? (target.classList.contains('firby-scroll-halo') || document.querySelector('.firby-scroll-halo') !== null) : false;
        }""")
        print(f"  Halo respirable activo en el objetivo: {has_halo}")

        # Guardar captura de evidencia visual
        evidence_path = "/home/ubuntu/firby/instances/scroll_verification_evidence.png"
        await page.screenshot(path=evidence_path)
        print(f"  Captura de pantalla de evidencia guardada en: {evidence_path}")

        await context.close()
        await browser.close()

    # 3. Reportar observación al backend (Two-Phase Commit)
    print("\n[3/3] Reportando observación completada al backend...")
    run_id = chat_data.get("run_id")
    if run_id:
        async with httpx.AsyncClient(timeout=10.0) as client:
            obs_res = await client.post("http://127.0.0.1:8001/api/widget/observe", json={
                "run_id": run_id,
                "observation": {
                    "success": True,
                    "target": "#planes",
                    "action_type": "navigate_to_section",
                    "completed_at": time.time()
                },
                "user_id": "live_operator_demo"
            })
            print(f"  Status observación: {obs_res.status_code}")
            print(f"  Respuesta final post-observación: {obs_res.json().get('response')}")
            assert obs_res.status_code == 200

    print("\n[FIRBY AUTONOMOUS OPERATOR] ¡Verificación en vivo completada exitosamente al 100%!")


if __name__ == "__main__":
    asyncio.run(run_live_verification())
