import asyncio
from playwright.async_api import async_playwright

ARTIFACT_DIR = "/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c"

async def test_layering():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:8003", wait_until="networkidle")

        # Scroll to #canales
        canales = page.locator("#canales")
        await canales.scroll_into_view_if_needed()
        await asyncio.sleep(0.5)

        # Apply CSS and wrapper adjustments via evaluate
        await page.evaluate("""() => {
            const wrapper = document.getElementById('splash-cursor-global-container');
            if (wrapper) {
                wrapper.style.zIndex = '1';
                wrapper.style.opacity = '0.38';
            }

            const style = document.createElement('style');
            style.id = 'splash-cursor-layering-test';
            style.textContent = `
                #canales, #como-funciona, #planes {
                    position: relative;
                    z-index: auto !important;
                }
                #canales .container,
                #como-funciona .container,
                #planes .container,
                .channel-editorial-col-text,
                .channel-editorial-col-widget,
                .channel-editorial-col-widget img,
                .channel-editorial-col-widget picture {
                    position: relative !important;
                    z-index: 4 !important;
                }
            `;
            document.head.appendChild(style);
        }""")

        # Move mouse violently over #canales to generate fluid
        box = await canales.bounding_box()
        if box:
            for i in range(10):
                await page.mouse.move(box["x"] + 200 + i * 40, box["y"] + 200 + (i % 3) * 60)
                await asyncio.sleep(0.04)

        await asyncio.sleep(0.2)

        # Check if wrapper is visible and what z-index elements have
        info = await page.evaluate("""() => {
            const wrapper = document.getElementById('splash-cursor-global-container');
            const colText = document.querySelector('.channel-editorial-col-text');
            const img = document.querySelector('.channel-editorial-col-widget img');
            return {
                wrapperZIndex: wrapper ? window.getComputedStyle(wrapper).zIndex : null,
                wrapperOpacity: wrapper ? window.getComputedStyle(wrapper).opacity : null,
                colTextZIndex: colText ? window.getComputedStyle(colText).zIndex : null,
                imgZIndex: img ? window.getComputedStyle(img).zIndex : null,
            };
        }""")
        print("Computed styling info:", info)

        # Screenshot #canales
        await canales.screenshot(path=f"{ARTIFACT_DIR}/splash_layering_test.png")
        print("Saved splash_layering_test.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_layering())
