import asyncio
from playwright.async_api import async_playwright

ARTIFACT_DIR = "/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c"

async def test_splashes_in_background():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:8003", wait_until="networkidle")

        # Scroll to #canales
        canales = page.locator("#canales")
        await canales.scroll_into_view_if_needed()
        await asyncio.sleep(0.5)

        # Reparent wrapper into #canales and set transparency
        await page.evaluate("""() => {
            const wrapper = document.getElementById("splash-cursor-global-container");
            const canvas = document.getElementById("splash-cursor-fluid-canvas");
            const canales = document.getElementById("canales");

            canales.style.position = "relative";
            canales.style.overflow = "hidden";

            canales.insertBefore(wrapper, canales.firstChild);
            wrapper.style.position = "absolute";
            wrapper.style.inset = "0";
            wrapper.style.width = "100%";
            wrapper.style.height = "100%";
            wrapper.style.zIndex = "1";
            wrapper.style.opacity = "0.45"; // nice transparency
            wrapper.style.clipPath = "none";
            wrapper.style.pointerEvents = "none";

            canvas.style.width = "100%";
            canvas.style.height = "100%";

            const container = canales.querySelector(".container");
            if (container) {
                container.style.position = "relative";
                container.style.zIndex = "3";
            }
        }""")

        # Move mouse over canales in zig-zag over the text and image
        box = await canales.bounding_box()
        if box:
            for i in range(25):
                x = box["x"] + 150 + (i * 45) % (box["width"] - 300)
                y = box["y"] + 150 + (i * 25) % (box["height"] - 300)
                await page.mouse.move(x, y)
                await asyncio.sleep(0.03)

        await asyncio.sleep(0.3)

        # Take screenshot in dark mode
        await page.evaluate("""() => {
            document.documentElement.classList.add("dark");
            document.documentElement.setAttribute("data-theme", "dark");
        }""")
        await asyncio.sleep(0.2)

        # Trigger more splashes
        if box:
            for i in range(15):
                x = box["x"] + 200 + (i * 50) % (box["width"] - 400)
                y = box["y"] + 200 + (i * 30) % (box["height"] - 400)
                await page.mouse.move(x, y)
                await asyncio.sleep(0.03)

        await asyncio.sleep(0.2)
        await canales.screenshot(path=f"{ARTIFACT_DIR}/splash_bg_dark_test.png")
        print("Saved splash_bg_dark_test.png")

        # Take screenshot in light mode
        await page.evaluate("""() => {
            document.documentElement.classList.remove("dark");
            document.documentElement.setAttribute("data-theme", "light");
        }""")
        await asyncio.sleep(0.2)
        if box:
            for i in range(15):
                x = box["x"] + 200 + (i * 50) % (box["width"] - 400)
                y = box["y"] + 200 + (i * 30) % (box["height"] - 400)
                await page.mouse.move(x, y)
                await asyncio.sleep(0.03)
        await asyncio.sleep(0.2)
        await canales.screenshot(path=f"{ARTIFACT_DIR}/splash_bg_light_test.png")
        print("Saved splash_bg_light_test.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_splashes_in_background())
