"""Generates a high-resolution composite of Design_workspace 3
with the requested lime pill button (sin trazo) 'Ver en tu página web'.
"""

from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_IMAGE = Path("/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c/scratch/figma/workspace3_with_button_1672x940.png")
SRC_IMG = Path("/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c/scratch/figma/frame_27_1646_workspace3.png")

HTML_CONTENT = f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@600;700&display=swap" rel="stylesheet">
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      width: 1672px;
      height: 940px;
      position: relative;
      background: #fff;
      overflow: hidden;
    }}
    .bg-img {{
      position: absolute;
      top: 0;
      left: 0;
      width: 1672px;
      height: 940px;
      display: block;
    }}
    /* The button 'sin trazo' requested by Santiago */
    .cta-btn {{
      position: absolute;
      left: 65px;
      top: 642px;
      width: 740px;
      height: 100px;
      background-color: #baf700;
      border-radius: 9999px;
      border: none;
      outline: none;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-family: 'Inter', -apple-system, sans-serif;
      font-size: 42px;
      font-weight: 600;
      color: #222222;
      letter-spacing: -0.01em;
      box-shadow: none;
    }}
  </style>
</head>
<body>
  <img class="bg-img" src="file://{SRC_IMG.absolute()}" alt="Design_workspace 3" />
  <button class="cta-btn">
    Ver en tu página web
  </button>
</body>
</html>
"""

def generate():
    temp_html = OUTPUT_IMAGE.parent / "temp_workspace3_render.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)

    print("[*] Renderizando Design_workspace 3 con botón sin trazo a 1672x940...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1672, "height": 940}, device_scale_factor=1)
        page.goto(f"file://{temp_html.absolute()}")
        page.wait_for_timeout(500)
        page.screenshot(path=str(OUTPUT_IMAGE), full_page=False)
        browser.close()

    temp_html.unlink(missing_ok=True)
    print(f"[OK] Imagen guardada en: {OUTPUT_IMAGE}")

if __name__ == "__main__":
    generate()
