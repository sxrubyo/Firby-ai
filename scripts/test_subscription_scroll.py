# -*- coding: utf-8 -*-
"""
Auditoría y Verificación de Flujo de Suscripción, Scroll Cinemático y Cero Bold.
Valida en vivo sobre http://127.0.0.1:8003:
1. Posición inicial en Hero (scrollY = 0).
2. Detección y scroll real fluido con física cinemática hacia #planes.
3. Muestreo en vivo de scrollY cada 200ms para certificar la curva y velocidad.
4. Respuesta del agente:
   - NO texto hardcodeado recitando los 3 planes de memoria.
   - Explicación de los pasos reales para suscribirse (elegir plan, clic en Comenzar prueba gratis, registro en 1 minuto).
   - CERO BOLD (cero asteriscos dobles **).
   - Espaciado con doble salto de línea (\\n\\n) y guiones (-).
5. Capturas PNG de alta resolución.
"""
import os
import sys
import time
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = "/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c"

def run_test():
    url = "http://127.0.0.1:8003/"
    print(f"[*] Iniciando prueba en {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = browser.new_context(viewport={"width": 1280, "height": 850}, device_scale_factor=2)
        page = context.new_page()

        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(1)

        # 1. Asegurar scroll en la parte superior (Hero)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.5)
        initial_scroll = page.evaluate("window.scrollY")
        print(f"[1] Scroll inicial en Hero: {initial_scroll}px")

        # 2. Abrir el widget
        page.evaluate("() => { const b = document.getElementById('waiChatLauncher'); if (b) b.click(); else if (typeof openChat === 'function') openChat(); else { const main = document.getElementById('bws-hw-btn'); if (main) main.click(); } }")
        time.sleep(1)
        page.evaluate("() => { const b = document.getElementById('waiChatLauncher'); if (b) b.click(); }")
        time.sleep(1)

        # 3. Aceptar términos si aparece el botón de consent
        page.wait_for_timeout(1000)
        has_consent = page.evaluate("() => { const b = document.getElementById('firby-consent-btn'); return !!b; }")
        if has_consent:
            print("[*] Botón de consentimiento detectado, aceptando términos con JS...")
            page.evaluate("() => { const b = document.getElementById('firby-consent-btn'); if (b) b.click(); }")
            page.wait_for_timeout(2500)
            print("[*] Términos aceptados.")

        # 4. Enviar "Me gustaria ver como me suscribo"
        user_query = "Me gustaria ver como me suscribo"
        print(f"[2] Enviando mensaje de usuario: '{user_query}'")
        page.evaluate(f"""() => {{
            const input = document.getElementById('firby-input') || document.querySelector('#firby-chat-input, input[type="text"]');
            if (input) {{
                input.value = '{user_query}';
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
            const form = document.getElementById('firby-input-form');
            if (form) {{
                form.dispatchEvent(new Event('submit', {{ bubbles: true, cancelable: true }}));
            }} else {{
                const btn = document.getElementById('firby-send');
                if (btn) btn.click();
            }}
        }}""")

        # 5. Muestrear scrollY en vivo cada 200ms durante 5 segundos
        samples = []
        start_time = time.time()
        print("[3] Registrando cinemática de scroll en vivo...")
        while time.time() - start_time < 5.0:
            current_y = page.evaluate("window.scrollY")
            elapsed = round(time.time() - start_time, 2)
            samples.append((elapsed, current_y))
            time.sleep(0.2)

        # 6. Esperar la respuesta del agente
        try:
            page.wait_for_selector(".firby-msg-agent, .firby-bubble-agent", timeout=10000)
            time.sleep(2)
        except Exception:
            pass

        final_scroll = page.evaluate("window.scrollY")
        final_hash = page.evaluate("window.location.hash")
        planes_top = page.evaluate("() => { const el = document.getElementById('planes'); return el ? el.getBoundingClientRect().top : null; }")

        print(f"[4] Scroll final: {final_scroll}px | Hash: {final_hash} | Distancia al top de #planes: {planes_top}px")
        print("    Muestras de cinemática (tiempo, scrollY):")
        for t_s, y_s in samples[::2]: # cada 400ms
            print(f"      {t_s}s -> {y_s}px")

        # 7. Extraer texto del último mensaje del agente
        agent_bubbles = page.evaluate("""() => {
            const bubbles = Array.from(document.querySelectorAll('.firby-msg-agent, .firby-bubble-agent'));
            return bubbles.map(b => b.innerText || b.textContent);
        }""")

        last_reply = agent_bubbles[-1] if agent_bubbles else ""
        print(f"[5] Respuesta del agente:\n---\n{last_reply}\n---")

        # 8. Validaciones
        has_hardcoded_catalog = "Nuestros planes oficiales son:" in last_reply and "Starter: $290.000 COP" in last_reply and "Pro: $490.000 COP" in last_reply and "Equipos: $890.000 COP" in last_reply
        has_subscription_guide = any(k in last_reply.lower() for k in ["suscrib", "prueba gratis", "registro", "1 minuto", "cancel"])
        has_bold = "**" in last_reply or "<strong>" in page.evaluate("""() => {
            const bubbles = Array.from(document.querySelectorAll('.firby-msg-agent, .firby-bubble-agent'));
            const last = bubbles[bubbles.length - 1];
            return last ? last.innerHTML : '';
        }""")
        has_bullets = "-" in last_reply or page.evaluate("""() => {
            const b = document.querySelectorAll('.firby-bullet-item');
            return b.length > 0;
        }""")

        print("\n=== RESULTADOS DE VERIFICACIÓN ===")
        print(f"Scroll ejecutado hacia #planes: {'SÍ' if final_scroll > 2000 else 'NO'} ({final_scroll}px)")
        print(f"Texto hardcodeado de catálogo eliminado: {'SÍ (CORRECTO)' if not has_hardcoded_catalog else 'NO (FALLÓ)'}")
        print(f"Guía de suscripción presente: {'SÍ (CORRECTO)' if has_subscription_guide else 'NO'}")
        print(f"Cero bold (** / <strong>): {'SÍ (CORRECTO: CERO BOLD)' if not has_bold else 'NO (DETECTÓ BOLD)'}")
        print(f"Formato con viñetas / guiones: {'SÍ (CORRECTO)' if has_bullets else 'NO'}")

        # 8. Asegurar que los mensajes del chat se desplacen hasta abajo para mostrar la respuesta completa
        page.evaluate("""() => {
            const pill = document.getElementById('firby-scroll-bottom-pill');
            if (pill) pill.click();
            const container = document.getElementById('firby-messages') || document.querySelector('.firby-messages');
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        }""")
        time.sleep(1)

        # 9. Tomar capturas de pantalla de alta resolución
        full_png = os.path.join(ARTIFACT_DIR, "subscription_scroll_verified_full.png")
        page.screenshot(path=full_png, full_page=False)
        print(f"[6] Captura de viewport guardada: {full_png}")

        # Zoom al widget
        chat_modal = page.query_selector("#firby-chat-window, .firby-chat-window")
        zoom_png = os.path.join(ARTIFACT_DIR, "subscription_scroll_verified_widget.png")
        if chat_modal:
            chat_modal.screenshot(path=zoom_png)
            print(f"[7] Captura de zoom guardada: {zoom_png}")

        browser.close()

if __name__ == "__main__":
    run_test()
