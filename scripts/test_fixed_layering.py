import asyncio
from playwright.async_api import async_playwright

ARTIFACT_DIR = "/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c"

async def test_fixed_layering():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:8003", wait_until="networkidle")

        canales = page.locator("#canales")
        await canales.scroll_into_view_if_needed()
        await asyncio.sleep(0.5)

        # Apply z-index 5 on wrapper and z-index 20 on container
        await page.evaluate("""() => {
            const wrapper = document.getElementById("splash-cursor-global-container");
            if (wrapper) {
                wrapper.style.zIndex = "5";
                wrapper.style.opacity = "0.35"; // more transparency
            }

            const style = document.createElement("style");
            style.id = "test-fixed-layering-css";
            style.textContent = `
                /* Section backgrounds at level 0 */
                #canales, #como-funciona, #planes {
                    position: relative;
                    z-index: auto !important;
                }

                /* Content at level 20 */
                #canales .container,
                #como-funciona .container,
                #planes .container {
                    position: relative !important;
                    z-index: 20 !important;
                }

                /* Text and image columns */
                .channel-editorial-col-text,
                .channel-editorial-col-widget,
                .channel-editorial-col-widget picture,
                .channel-editorial-col-widget img {
                    position: relative !important;
                    z-index: 21 !important;
                }
            `;
            document.head.appendChild(style);
        }""")

        # Move mouse across the section in dark mode
        await page.evaluate("""() => {
            document.documentElement.classList.add("dark");
            document.documentElement.setAttribute("data-theme", "dark");
        }""")
        await asyncio.sleep(0.2)

        box = await canales.bounding_box()
        if box:
            # Move mouse across the text column and image column
            for i in range(30):
                x = box["x"] + 200 + (i * 35) % (box["width"] - 350)
                y = box["y"] + 250 + (i * 20) % (box["height"] - 350)
                await page.mouse.move(x, y)
                await asyncio.sleep(0.02)

        await asyncio.sleep(0.15)
        await canales.screenshot(path=f"{ARTIFACT_DIR}/fixed_layering_dark.png")
        print("Captured fixed_layering_dark.png")

        # Now test in light mode
        await page.evaluate("""() => {
            document.documentElement.classList.remove("dark");
            document.documentElement.setAttribute("data-theme", "light");
        }""")
        await asyncio.sleep(0.2)

        if box:
            for i in range(30):
                x = box["x"] + 250 + (i * 35) % (box["width"] - 400)
                y = box["y"] + 200 + (i * 25) % (box["height"] - 400)
                await page.mouse.move(x, y)
                await asyncio.sleep(0.02)

        await asyncio.sleep(0.15)
        await canales.screenshot(path=f"{ARTIFACT_DIR}/fixed_layering_light.png")
        print("Captured fixed_layering_light.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_fixed_layering())
