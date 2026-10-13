import asyncio
from playwright.async_api import async_playwright

ARTIFACT_DIR = "/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c"

async def test_gradients():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:8003", wait_until="networkidle")

        # Let's test different gradients via evaluate
        recipes = [
            {
                "name": "recipe1_white_lime",
                # Smooth white to firby lime to bright lime to white
                "dark_grad": "linear-gradient(to right, #ffffff 0%, #b8f901 35%, #d9f99d 65%, #ffffff 100%)",
                "light_grad": "linear-gradient(to right, #1a2e05 0%, #65a30d 30%, #b8f901 60%, #1a2e05 100%)"
            },
            {
                "name": "recipe2_lime_white_glow",
                # Vibrant electric lime with white core glint
                "dark_grad": "linear-gradient(to right, #b8f901 0%, #ffffff 40%, #bef264 70%, #b8f901 100%)",
                "light_grad": "linear-gradient(to right, #4d7c0f 0%, #84cc16 35%, #b8f901 65%, #4d7c0f 100%)"
            },
            {
                "name": "recipe3_electric_firby",
                # Pure Firby Lime + White + Cyber Lime
                "dark_grad": "linear-gradient(135deg, #ffffff 0%, #b8f901 30%, #ffffff 60%, #9ae600 85%, #ffffff 100%)",
                "light_grad": "linear-gradient(135deg, #18181b 0%, #4d7c0f 25%, #b8f901 60%, #74cc00 80%, #18181b 100%)"
            }
        ]

        hero_title = page.locator(".hero-title")

        for r in recipes:
            # Apply to just "piloto"
            await page.evaluate(f"""() => {{
                let el = document.querySelector('.gradient-text-piloto');
                if (el) {{
                    el.style.setProperty('background-image', '{r["dark_grad"]}', 'important');
                    el.style.setProperty('background-size', '300% 100%', 'important');
                }}
                document.documentElement.classList.add('dark');
                document.documentElement.setAttribute('data-theme', 'dark');
            }}""")
            await asyncio.sleep(0.3)
            await hero_title.screenshot(path=f"{ARTIFACT_DIR}/{r['name']}_dark_piloto.png")

            # Apply in light mode
            await page.evaluate(f"""() => {{
                let el = document.querySelector('.gradient-text-piloto');
                if (el) {{
                    el.style.setProperty('background-image', '{r["light_grad"]}', 'important');
                }}
                document.documentElement.classList.remove('dark');
                document.documentElement.setAttribute('data-theme', 'light');
            }}""")
            await asyncio.sleep(0.3)
            await hero_title.screenshot(path=f"{ARTIFACT_DIR}/{r['name']}_light_piloto.png")

            # Also test across "piloto automático"
            await page.evaluate(f"""() => {{
                let title = document.querySelector('.hero-title');
                title.innerHTML = 'Su sitio web en<br><span class="gradient-text-piloto">piloto automático</span>';
                let el = title.querySelector('.gradient-text-piloto');
                el.style.setProperty('background-image', '{r["dark_grad"]}', 'important');
                el.style.setProperty('background-size', '300% 100%', 'important');
                document.documentElement.classList.add('dark');
                document.documentElement.setAttribute('data-theme', 'dark');
            }}""")
            await asyncio.sleep(0.3)
            await hero_title.screenshot(path=f"{ARTIFACT_DIR}/{r['name']}_dark_both.png")

            # Reset back to just piloto
            await page.evaluate("""() => {
                let title = document.querySelector('.hero-title');
                title.innerHTML = 'Su sitio web en<br><span class="gradient-text-piloto">piloto</span> automático';
            }""")

        await browser.close()
        print("Done rendering test recipes!")

if __name__ == "__main__":
    asyncio.run(test_gradients())
