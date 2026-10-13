"""Visual Ad Creative Renderer for Firby Growth Council.
Takes a campaign dossier JSON and renders an ultra-high quality, high-converting
1080x1350 static ad PNG using Playwright.
"""

import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

DOSSIER_PATH = Path("/home/ubuntu/firby/agents/growth_council/campaign_inmobiliarias.json")
OUTPUT_IMAGE = Path("/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c/ad_creative_inmobiliarias_1080x1350.png")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1080, height=1350, initial-scale=1.0">
  <title>Firby Ad Creative</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      width: 1080px;
      height: 1350px;
      background-color: #08080a;
      background-image: 
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(185, 250, 1, 0.12), transparent),
        radial-gradient(circle at 10% 90%, rgba(250, 204, 21, 0.05), transparent);
      color: #f3f4f6;
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 64px 72px 56px;
      position: relative;
    }

    /* Subdued grid background */
    .grid-pattern {
      position: absolute;
      inset: 0;
      background-size: 40px 40px;
      background-image: linear-gradient(to right, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                        linear-gradient(to bottom, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
      pointer-events: none;
      z-index: 0;
    }

    /* Top Bar Header */
    .header {
      position: relative;
      z-index: 10;
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .brand-icon {
      width: 52px;
      height: 52px;
      background: #000;
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    .brand-name {
      font-size: 32px;
      font-weight: 800;
      letter-spacing: -0.04em;
      color: #ffffff;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(185, 250, 1, 0.1);
      border: 1px solid rgba(185, 250, 1, 0.3);
      color: #b9fa01;
      padding: 8px 18px;
      border-radius: 9999px;
      font-size: 15px;
      font-weight: 700;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }
    .badge-dot {
      width: 8px;
      height: 8px;
      background: #b9fa01;
      border-radius: 50%;
      box-shadow: 0 0 12px #b9fa01;
    }

    /* Main Hook & Headline */
    .hero-copy {
      position: relative;
      z-index: 10;
      margin-top: 10px;
    }
    .problem-callout {
      font-size: 18px;
      font-weight: 700;
      color: #ef4444;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 12px;
    }
    .headline {
      font-size: 58px;
      font-weight: 800;
      line-height: 1.08;
      letter-spacing: -0.04em;
      color: #ffffff;
      margin-bottom: 16px;
    }
    .headline span.accent {
      color: #b9fa01;
      text-shadow: 0 0 40px rgba(185, 250, 1, 0.25);
    }
    .subtext {
      font-size: 20px;
      line-height: 1.45;
      color: #94a3b8;
      max-width: 900px;
      font-weight: 500;
    }

    /* UI Visual Simulation Box: The Dual Engine */
    .split-container {
      position: relative;
      z-index: 10;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin: 16px 0;
    }

    .card {
      background: rgba(18, 19, 23, 0.95);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 24px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
      position: relative;
      overflow: hidden;
    }
    .card-web {
      border-color: rgba(185, 250, 1, 0.25);
    }
    .card-wa {
      border-color: rgba(37, 211, 102, 0.25);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 14px;
      border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .card-label {
      font-size: 14px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .label-web { color: #b9fa01; }
    .label-wa { color: #25d366; }
    
    .card-time {
      font-size: 13px;
      font-weight: 600;
      color: #64748b;
      background: rgba(255,255,255,0.04);
      padding: 4px 10px;
      border-radius: 6px;
    }

    /* Chat bubble simulator */
    .chat-bubble {
      padding: 14px 18px;
      border-radius: 16px;
      font-size: 15px;
      line-height: 1.45;
      margin-bottom: 12px;
      max-width: 90%;
    }
    .bubble-visitor {
      background: rgba(255, 255, 255, 0.06);
      color: #e2e8f0;
      align-self: flex-start;
      border-bottom-left-radius: 4px;
    }
    .bubble-firby {
      background: #1e222d;
      border: 1px solid rgba(185, 250, 1, 0.3);
      color: #ffffff;
      align-self: flex-end;
      border-bottom-right-radius: 4px;
    }
    .bubble-wa {
      background: #005c4b;
      color: #ffffff;
      align-self: flex-start;
      border-radius: 14px;
      font-size: 14px;
      border-bottom-left-radius: 4px;
    }

    .calendar-event {
      margin-top: 8px;
      background: rgba(185, 250, 1, 0.12);
      border: 1px dashed rgba(185, 250, 1, 0.4);
      padding: 12px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .cal-icon {
      font-weight: 800;
      font-size: 20px;
      color: #b9fa01;
    }
    .cal-text {
      font-size: 13px;
      color: #ffffff;
    }
    .cal-text strong {
      display: block;
      color: #b9fa01;
      font-size: 14px;
    }

    /* Bottom Trust & CTA */
    .footer {
      position: relative;
      z-index: 10;
      display: flex;
      flex-direction: column;
      gap: 20px;
      padding-top: 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
    .cta-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .cta-button {
      background: #b9fa01;
      color: #000000;
      font-size: 24px;
      font-weight: 800;
      padding: 22px 42px;
      border-radius: 18px;
      border: none;
      display: inline-flex;
      align-items: center;
      gap: 14px;
      box-shadow: 0 10px 30px rgba(185, 250, 1, 0.35);
      letter-spacing: -0.02em;
    }
    .cta-tagline {
      font-size: 18px;
      color: #94a3b8;
      font-weight: 600;
    }
    .proof-pills {
      display: flex;
      gap: 16px;
    }
    .pill {
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.08);
      padding: 8px 16px;
      border-radius: 10px;
      font-size: 14px;
      font-weight: 600;
      color: #cbd5e1;
    }
  </style>
</head>
<body>
  <div class="grid-pattern"></div>

  <!-- Header -->
  <div class="header">
    <div class="brand">
      <div class="brand-icon">
        <svg width="34" height="34" viewBox="0 0 148 148" fill="none">
          <path d="M42 22H96V42H64V68H90V88H64V126H42V22Z" fill="#b9fa01"/>
          <circle cx="114" cy="32" r="10" fill="#b9fa01"/>
          <path d="M104 68H124V126H104V68Z" fill="#b9fa01"/>
        </svg>
      </div>
      <div class="brand-name">firby</div>
    </div>
    <div class="badge">
      <div class="badge-dot"></div>
      Google Calendar Sync en Vivo
    </div>
  </div>

  <!-- Hero Headline -->
  <div class="hero-copy">
    <div class="problem-callout">El dolor que vacía tu inventario</div>
    <h1 class="headline">Tu inmobiliaria pierde compradores a <span class="accent">medianoche</span></h1>
    <p class="subtext">Un comprador calificado busca visitar un apartamento un domingo a las 11:45 PM. Tu web solo tiene un formulario estático que nadie lee hasta el lunes. Mientras duermes, Firby atiende en vivo y confirma la cita.</p>
  </div>

  <!-- Split Screen Demonstration -->
  <div class="split-container">
    <!-- Web Visitor View -->
    <div class="card card-web">
      <div class="card-header">
        <span class="card-label label-web">En Tu Sitio Web (Visitante)</span>
        <span class="card-time">Domingo 11:45 PM</span>
      </div>
      <div class="chat-bubble bubble-visitor">
        "Hola, me interesa agendar una visita mañana para ver el penthouse de Rosales."
      </div>
      <div class="chat-bubble bubble-firby">
        "Buenas noches. Consultando el calendario del asesor... Tenemos espacio libre mañana a las 10:00 AM o a las 3:30 PM. ¿Cuál prefieres?"
      </div>
      <div class="chat-bubble bubble-visitor">
        "A las 10:00 AM me queda perfecto."
      </div>
      <div class="calendar-event">
        <div class="cal-icon">✓</div>
        <div class="cal-text">
          <strong>Cita Agendada en Google Calendar</strong>
          Lunes 10:00 AM • Visita Penthouse Rosales
        </div>
      </div>
    </div>

    <!-- Owner WhatsApp View -->
    <div class="card card-wa">
      <div class="card-header">
        <span class="card-label label-wa">WhatsApp Privado del Dueño</span>
        <span class="card-time">Instantáneo (11:46 PM)</span>
      </div>
      <div style="font-size: 13px; color: #64748b; margin-bottom: 12px; font-weight: 600;">Línea Ejecutiva Firby (+57 324 369 9856)</div>
      <div class="chat-bubble bubble-wa">
        <strong>Nueva cita confirmada en tu web:</strong><br><br>
        Cliente: Juan Camilo Osorio<br>
        Propiedad: Penthouse Rosales<br>
        Fecha: Lunes 10:00 AM<br>
        Estado: Bloqueado en tu Google Calendar.<br><br>
        El lead ya recibió la confirmación y ubicación.
      </div>
      <div style="margin-top: auto; padding: 12px; background: rgba(37, 211, 102, 0.08); border-radius: 12px; font-size: 13px; color: #86efac; border: 1px solid rgba(37, 211, 102, 0.2);">
        Cero trabajo manual para tu equipo. El cliente quedó atendido y cerrado mientras descansabas.
      </div>
    </div>
  </div>

  <!-- Bottom Action Block -->
  <div class="footer">
    <div class="proof-pills">
      <div class="pill">Cero formularios de contacto</div>
      <div class="pill">Google Calendar 100% Sincronizado</div>
      <div class="pill">Instalación en 1 línea de código</div>
    </div>
    <div class="cta-row">
      <div class="cta-tagline">
        Cancela cuando quieras en 1 clic.<br>
        Sin contratos de permanencia.
      </div>
      <button class="cta-button">
        Prueba 7 días gratis →
      </button>
    </div>
  </div>
</body>
</html>
"""

def render_ad():
    OUTPUT_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    temp_html = OUTPUT_IMAGE.parent / "temp_ad_creative.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE)

    print(f"[*] Renderizando anuncio publicitario de alta resolución (1080x1350)...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        page.goto(f"file://{temp_html.absolute()}")
        page.wait_for_timeout(1000)
        page.screenshot(path=str(OUTPUT_IMAGE), full_page=False)
        browser.close()
    
    temp_html.unlink(missing_ok=True)
    print(f"[OK] Anuncio visual generado exitosamente en: {OUTPUT_IMAGE}")
    return str(OUTPUT_IMAGE)

if __name__ == "__main__":
    render_ad()
