import asyncio
from playwright.async_api import async_playwright

ARTIFACT_DIR = "/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c"

async def test_channels_banner():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:8003", wait_until="networkidle")

        # 1. Dark Mode
        await page.evaluate("() => document.documentElement.setAttribute('data-theme', 'dark')")
        await page.evaluate("() => document.documentElement.classList.add('dark')")
        await asyncio.sleep(1.0)

        row1 = page.locator(".channel-editorial-row").first
        await row1.scroll_into_view_if_needed()
        await asyncio.sleep(0.5)

        await row1.screenshot(path=f"{ARTIFACT_DIR}/channel_editorial_row1_banner_dark.png")
        print("Captured channel_editorial_row1_banner_dark.png")

        # 2. Light Mode
        await page.evaluate("() => document.documentElement.setAttribute('data-theme', 'light')")
        await page.evaluate("() => document.documentElement.classList.remove('dark')")
        await asyncio.sleep(1.0)

        await row1.scroll_into_view_if_needed()
        await asyncio.sleep(0.5)

        await row1.screenshot(path=f"{ARTIFACT_DIR}/channel_editorial_row1_banner_light.png")
        print("Captured channel_editorial_row1_banner_light.png")

        # Full section screenshot
        canales_section = page.locator("#canales")
        await canales_section.screenshot(path=f"{ARTIFACT_DIR}/canales_section_banner_light.png")
        print("Captured canales_section_banner_light.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_channels_banner())
