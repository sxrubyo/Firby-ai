"""Renders a high-resolution 1920x1080 UI mockup of the Firby Ideas Workspace
based on the Linear + Attio + Raycast design spec.
"""

from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_PATH = Path("/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c/ideas_workspace_ui_preview.png")

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Firby Ideas Workspace — UI Preview</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      width: 1920px;
      height: 1080px;
      background-color: #08080a;
      color: #f1f5f9;
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      overflow: hidden;
      display: flex;
    }

    /* Left Sidebar */
    .sidebar {
      width: 260px;
      height: 100%;
      background: #0b0c10;
      border-right: 1px solid rgba(255, 255, 255, 0.07);
      display: flex;
      flex-direction: column;
      padding: 24px 16px;
      flex-shrink: 0;
    }
    .brand-row {
      display: flex;
      align-items: center;
      gap: 12px;
      padding-bottom: 24px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      margin-bottom: 20px;
    }
    .brand-badge {
      width: 38px;
      height: 38px;
      background: #000;
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .brand-title {
      font-size: 19px;
      font-weight: 800;
      letter-spacing: -0.03em;
      color: #fff;
    }
    .nav-group-title {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #64748b;
      margin: 16px 8px 8px;
    }
    .nav-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 12px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      color: #94a3b8;
      cursor: pointer;
    }
    .nav-item.active {
      background: rgba(185, 250, 1, 0.08);
      color: #b9fa01;
      font-weight: 600;
      border-left: 2px solid #b9fa01;
    }
    .nav-pill {
      margin-left: auto;
      font-size: 11px;
      background: rgba(255,255,255,0.06);
      padding: 2px 7px;
      border-radius: 10px;
      color: #cbd5e1;
      font-family: 'JetBrains Mono', monospace;
    }

    /* Main Content Area */
    .main {
      flex: 1;
      height: 100%;
      display: flex;
      flex-direction: column;
      background: #08080a;
      overflow: hidden;
      position: relative;
    }

    /* Top Command Header */
    .top-header {
      height: 64px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.07);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 28px;
      background: rgba(11, 12, 16, 0.7);
      backdrop-filter: blur(12px);
      flex-shrink: 0;
    }
    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .sector-badge {
      display: flex;
      align-items: center;
      gap: 8px;
      background: #14161f;
      border: 1px solid rgba(255,255,255,0.1);
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      color: #f1f5f9;
    }
    .sector-dot {
      width: 7px;
      height: 7px;
      background: #b9fa01;
      border-radius: 50%;
    }
    .search-bar {
      display: flex;
      align-items: center;
      gap: 10px;
      background: #121319;
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 8px;
      padding: 7px 14px;
      width: 320px;
      font-size: 13px;
      color: #64748b;
    }
    .cmd-badge {
      margin-left: auto;
      background: rgba(255,255,255,0.08);
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 10px;
      font-family: 'JetBrains Mono', monospace;
      color: #94a3b8;
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .view-toggle {
      display: flex;
      background: #121319;
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 8px;
      padding: 3px;
    }
    .view-btn {
      padding: 5px 12px;
      font-size: 12px;
      font-weight: 600;
      border-radius: 6px;
      color: #94a3b8;
    }
    .view-btn.active {
      background: rgba(255,255,255,0.08);
      color: #fff;
    }
    .btn-create {
      background: #b9fa01;
      color: #000;
      border: none;
      padding: 8px 16px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    /* Workspace Content: Board + Slide-Over Drawer */
    .workspace-body {
      flex: 1;
      display: flex;
      overflow: hidden;
    }

    /* Kanban Board Columns */
    .kanban-board {
      flex: 1;
      display: flex;
      gap: 16px;
      padding: 24px;
      overflow-x: auto;
    }
    .column {
      width: 290px;
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .column-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 4px 8px;
    }
    .column-title {
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #94a3b8;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .column-count {
      background: rgba(255,255,255,0.06);
      padding: 2px 7px;
      border-radius: 6px;
      font-size: 11px;
      font-family: 'JetBrains Mono', monospace;
      color: #cbd5e1;
    }

    /* Card Item (Craft B2B) */
    .card {
      background: #0f1015;
      border: 1px solid rgba(255, 255, 255, 0.07);
      border-radius: 12px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      cursor: pointer;
      position: relative;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .card.selected {
      border-color: #b9fa01;
      box-shadow: 0 0 0 1px #b9fa01, 0 8px 24px rgba(0,0,0,0.5);
    }
    .card-meta-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .card-id {
      font-size: 11px;
      font-family: 'JetBrains Mono', monospace;
      color: #64748b;
    }
    .card-priority {
      font-size: 10px;
      font-weight: 700;
      background: rgba(185, 250, 1, 0.1);
      color: #b9fa01;
      padding: 2px 6px;
      border-radius: 4px;
      letter-spacing: 0.04em;
    }
    .card-headline {
      font-size: 14px;
      font-weight: 700;
      color: #f8fafc;
      line-height: 1.35;
    }
    .card-hook {
      font-size: 12px;
      color: #94a3b8;
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    .card-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 10px;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      margin-top: 4px;
    }
    .card-tag {
      font-size: 11px;
      color: #cbd5e1;
      background: rgba(255,255,255,0.04);
      padding: 3px 8px;
      border-radius: 6px;
    }
    .card-score {
      font-size: 11px;
      font-weight: 700;
      color: #b9fa01;
      font-family: 'JetBrains Mono', monospace;
    }

    /* Linear Style Slide-Over Drawer */
    .drawer {
      width: 480px;
      height: 100%;
      background: #0d0e14;
      border-left: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      box-shadow: -10px 0 30px rgba(0,0,0,0.5);
    }
    .drawer-header {
      padding: 20px 24px;
      border-bottom: 1px solid rgba(255,255,255,0.07);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .drawer-id {
      font-size: 13px;
      font-family: 'JetBrains Mono', monospace;
      color: #94a3b8;
    }
    .drawer-status {
      font-size: 12px;
      font-weight: 700;
      color: #b9fa01;
      background: rgba(185, 250, 1, 0.1);
      border: 1px solid rgba(185, 250, 1, 0.25);
      padding: 4px 10px;
      border-radius: 9999px;
    }
    .drawer-body {
      flex: 1;
      padding: 24px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .drawer-title {
      font-size: 20px;
      font-weight: 800;
      color: #fff;
      line-height: 1.25;
    }
    .drawer-section-title {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #64748b;
      margin-bottom: 8px;
    }
    .drawer-box {
      background: #12141c;
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 10px;
      padding: 14px;
      font-size: 13px;
      line-height: 1.5;
      color: #cbd5e1;
    }
    .checklist-row {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 12px;
      color: #e2e8f0;
      margin-bottom: 6px;
    }
    .check-icon {
      color: #b9fa01;
      font-weight: 800;
      font-size: 13px;
    }
    .drawer-preview-img {
      width: 100%;
      height: 240px;
      border-radius: 10px;
      object-fit: cover;
      border: 1px solid rgba(255,255,255,0.1);
    }
    .drawer-footer {
      padding: 16px 24px;
      border-top: 1px solid rgba(255,255,255,0.07);
      background: #0a0b10;
      display: flex;
      gap: 12px;
    }
    .btn-export {
      flex: 1;
      background: #b9fa01;
      color: #000;
      font-weight: 700;
      font-size: 13px;
      padding: 12px;
      border-radius: 8px;
      border: none;
      cursor: pointer;
      text-align: center;
    }
    .btn-secondary {
      background: #151822;
      border: 1px solid rgba(255,255,255,0.08);
      color: #f1f5f9;
      font-weight: 600;
      font-size: 13px;
      padding: 12px 18px;
      border-radius: 8px;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="brand-row">
      <div class="brand-badge">
        <svg width="22" height="22" viewBox="0 0 148 148" fill="none">
          <path d="M42 22H96V42H64V68H90V88H64V126H42V22Z" fill="#b9fa01"/>
          <circle cx="114" cy="32" r="10" fill="#b9fa01"/>
          <path d="M104 68H124V126H104V68Z" fill="#b9fa01"/>
        </svg>
      </div>
      <div class="brand-title">firby</div>
    </div>

    <div class="nav-group-title">Consejo de Agentes</div>
    <div class="nav-item active">
      <span>Ideas & Creativos</span>
      <span class="nav-pill">8 Activas</span>
    </div>
    <div class="nav-item">
      <span>Flujos & N8N</span>
    </div>
    <div class="nav-item">
      <span>Base de Conocimiento</span>
    </div>
    <div class="nav-item">
      <span>Laboratorio de Pruebas</span>
    </div>

    <div class="nav-group-title" style="margin-top: auto;">Gobernanza</div>
    <div class="nav-item">
      <span>Paperclip Council</span>
      <span class="nav-pill" style="color: #b9fa01;">8 Agentes</span>
    </div>
    <div class="nav-item">
      <span>Ajustes de Marca</span>
    </div>
  </aside>

  <!-- Main View -->
  <main class="main">
    <!-- Top Command Header -->
    <header class="top-header">
      <div class="header-left">
        <div class="sector-badge">
          <div class="sector-dot"></div>
          Sector: Inmobiliarias & Corretaje
        </div>
        <div class="search-bar">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          Buscar ideas, ángulos, UTMs...
          <span class="cmd-badge">⌘K</span>
        </div>
      </div>

      <div class="header-right">
        <div class="view-toggle">
          <div class="view-btn active">Tablero</div>
          <div class="view-btn">Tabla</div>
          <div class="view-btn">Galería</div>
        </div>
        <button class="btn-create">
          + Nuevo Ángulo
        </button>
      </div>
    </header>

    <!-- Workspace Body -->
    <div class="workspace-body">
      <!-- Kanban Columns -->
      <div class="kanban-board">
        <!-- Col 1 -->
        <div class="column">
          <div class="column-header">
            <span class="column-title">1. Fricción & Dolor</span>
            <span class="column-count">3</span>
          </div>
          <div class="card selected">
            <div class="card-meta-row">
              <span class="card-id">#FIR-104</span>
              <span class="card-priority">ALTO IMPACTO</span>
            </div>
            <div class="card-headline">Tu inmobiliaria pierde compradores a medianoche</div>
            <div class="card-hook">"Prospectos calientes visitan tu web un domingo a las 11:45 PM y solo encuentran un formulario estático..."</div>
            <div class="card-footer">
              <span class="card-tag">Inmobiliarias</span>
              <span class="card-score">Score: 9.8</span>
            </div>
          </div>

          <div class="card">
            <div class="card-meta-row">
              <span class="card-id">#FIR-105</span>
              <span class="card-priority">MEDIA</span>
            </div>
            <div class="card-headline">La recepcionista que no trabaja sábados</div>
            <div class="card-hook">"El 62% de las solicitudes de visita a penthouse ocurren en fin de semana sin atención inmediata."</div>
            <div class="card-footer">
              <span class="card-tag">Bienes Raíces</span>
              <span class="card-score">Score: 8.5</span>
            </div>
          </div>
        </div>

        <!-- Col 2 -->
        <div class="column">
          <div class="column-header">
            <span class="column-title">2. Copy & Guión</span>
            <span class="column-count">2</span>
          </div>
          <div class="card">
            <div class="card-meta-row">
              <span class="card-id">#FIR-098</span>
              <span class="card-priority">LISTO</span>
            </div>
            <div class="card-headline">Clínicas: Pacientes perdidos el domingo</div>
            <div class="card-hook">"Un dolor de muela no espera al lunes a las 8 AM. Firby agenda la urgencia en tu calendario."</div>
            <div class="card-footer">
              <span class="card-tag">Odontología</span>
              <span class="card-score">Score: 9.4</span>
            </div>
          </div>
        </div>

        <!-- Col 3 -->
        <div class="column">
          <div class="column-header">
            <span class="column-title">3. Creativos Listos</span>
            <span class="column-count">2</span>
          </div>
          <div class="card">
            <div class="card-meta-row">
              <span class="card-id">#FIR-091</span>
              <span class="card-priority">ASSET 4:5</span>
            </div>
            <div class="card-headline">Comparativa Antes / Después Recepción</div>
            <div class="card-hook">"Split screen demostrando la diferencia entre un formulario muerto y Firby en vivo."</div>
            <div class="card-footer">
              <span class="card-tag">Estático + Reel</span>
              <span class="card-score">1080x1350</span>
            </div>
          </div>
        </div>

        <!-- Col 4 -->
        <div class="column">
          <div class="column-header">
            <span class="column-title">4. Canary QA 10/10</span>
            <span class="column-count">1</span>
          </div>
          <div class="card">
            <div class="card-meta-row">
              <span class="card-id">#FIR-104</span>
              <span class="card-priority" style="background: rgba(37,211,102,0.1); color: #25d366;">CERTIFICADO</span>
            </div>
            <div class="card-headline">Auditoría Aprobada: El comprador de medianoche</div>
            <div class="card-hook">"Cero emojis. Cero $1.000 COP. Canales 100% exactos (Web para clientes, WhatsApp para dueño)."</div>
            <div class="card-footer">
              <span class="card-tag">BrandAuditor</span>
              <span class="card-score">10/10</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Slide-Over Drawer (Linear Style Inspector) -->
      <aside class="drawer">
        <div class="drawer-header">
          <span class="drawer-id">CAMPAÑA #FIR-104</span>
          <span class="drawer-status">LISTO PARA META ADS</span>
        </div>

        <div class="drawer-body">
          <h2 class="drawer-title">Tu inmobiliaria pierde compradores a medianoche</h2>

          <div>
            <div class="drawer-section-title">Visual Creativo Generado (1080x1350)</div>
            <img class="drawer-preview-img" src="/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c/ad_creative_inmobiliarias_1080x1350.png" alt="Anuncio Preview" />
          </div>

          <div>
            <div class="drawer-section-title">Copy Principal (Respuesta Directa)</div>
            <div class="drawer-box">
              Un cliente busca ver un inmueble un domingo a las diez de la noche en tu web y solo encuentra un formulario estático que nadie lee hasta el lunes. Para ese momento, ya firmó con tu competencia. Firby atiende en tiempo real, consulta tu Google Calendar, agenda la visita y te avisa directo a tu WhatsApp. Prueba 7 días gratis. Cancela cuando quieras en 1 clic.
            </div>
          </div>

          <div>
            <div class="drawer-section-title">Auditoría de Políticas de Marca (Canary Rule)</div>
            <div class="drawer-box">
              <div class="checklist-row"><span class="check-icon">✓</span> Cero emojis en titular, copy y botón</div>
              <div class="checklist-row"><span class="check-icon">✓</span> Cero mención a $1.000 COP (Oferta oficial 7 días gratis)</div>
              <div class="checklist-row"><span class="check-icon">✓</span> Canales verificados: Web atiende al visitante; WhatsApp privado solo con el dueño</div>
              <div class="checklist-row"><span class="check-icon">✓</span> Español directo de negocios sin clichés de IA</div>
            </div>
          </div>

          <div>
            <div class="drawer-section-title">Parámetros UTM & Segmentación Meta</div>
            <div class="drawer-box" style="font-family: 'JetBrains Mono', monospace; font-size: 11px;">
              utm_source=meta&utm_medium=cpc<br>
              utm_campaign=tof_inmobiliarias_medianoche<br>
              Audience: Administradores inmobiliarios, Bienes Raíces comerciales, Dueños de agencias.
            </div>
          </div>
        </div>

        <div class="drawer-footer">
          <button class="btn-secondary">Descargar PNG</button>
          <button class="btn-export">Publicar en Meta Ads →</button>
        </div>
      </aside>
    </div>
  </main>
</body>
</html>
"""

def render_preview():
    temp_html = Path("/home/ubuntu/firby/agents/growth_council/temp_workspace_ui.html")
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)

    print("[*] Renderizando maqueta visual del Ideas Workspace a 1920x1080...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(f"file://{temp_html.absolute()}")
        page.wait_for_timeout(1000)
        page.screenshot(path=str(OUTPUT_PATH), full_page=False)
        browser.close()

    temp_html.unlink(missing_ok=True)
    print(f"[OK] Maqueta UI renderizada en: {OUTPUT_PATH}")

if __name__ == "__main__":
    render_preview()
