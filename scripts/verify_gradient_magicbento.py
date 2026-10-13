import os
import asyncio
from playwright.async_api import async_playwright

ARTIFACT_DIR = "/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c"

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        # 1. Dark Mode Verification (Santi's primary view)
        print("Testing Dark Mode on http://127.0.0.1:8003...")
        await page.goto("http://127.0.0.1:8003", wait_until="networkidle")
        await page.evaluate("() => document.documentElement.setAttribute('data-theme', 'dark')")
        await page.evaluate("() => document.documentElement.classList.add('dark')")
        await asyncio.sleep(1.2)

        # Hero Title Dark
        hero_title = page.locator(".hero-title")
        await hero_title.wait_for(state="visible")
        await hero_title.screenshot(path=os.path.join(ARTIFACT_DIR, "hero_title_verdelima_dark.png"))
        print("Captured hero_title_verdelima_dark.png")

        # Scroll to Final CTA card Dark
        cta_card = page.locator(".cta-final-card")
        await cta_card.scroll_into_view_if_needed()
        await asyncio.sleep(0.8)

        # Move mouse over CTA card
        box = await cta_card.bounding_box()
        if box:
            await page.mouse.move(box["x"] + box["width"] * 0.45, box["y"] + box["height"] * 0.5)
        await asyncio.sleep(0.6)

        await cta_card.screenshot(path=os.path.join(ARTIFACT_DIR, "cta_iridescence_bento_dark.png"))
        print("Captured cta_iridescence_bento_dark.png")

        cta_section = page.locator("#contacto")
        await cta_section.screenshot(path=os.path.join(ARTIFACT_DIR, "cta_section_iridescence_bento_dark.png"))
        print("Captured cta_section_iridescence_bento_dark.png")

        # 2. Light Mode Verification
        print("Testing Light Mode...")
        await page.evaluate("() => document.documentElement.setAttribute('data-theme', 'light')")
        await page.evaluate("() => document.documentElement.classList.remove('dark')")
        await asyncio.sleep(1.0)

        # Hero Title Light
        await hero_title.scroll_into_view_if_needed()
        await asyncio.sleep(0.5)
        await hero_title.screenshot(path=os.path.join(ARTIFACT_DIR, "hero_title_verdelima_light.png"))
        print("Captured hero_title_verdelima_light.png")

        # CTA Light
        await cta_card.scroll_into_view_if_needed()
        if box:
            await page.mouse.move(box["x"] + box["width"] * 0.45, box["y"] + box["height"] * 0.5)
        await asyncio.sleep(0.6)

        await cta_card.screenshot(path=os.path.join(ARTIFACT_DIR, "cta_iridescence_bento_light.png"))
        print("Captured cta_iridescence_bento_light.png")

        await browser.close()
        print("All screenshots successfully captured!")

if __name__ == "__main__":
    asyncio.run(capture())
