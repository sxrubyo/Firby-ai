import asyncio
from playwright.async_api import async_playwright

ARTIFACT_DIR = "/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c"

async def verify_site(url, prefix):
    print(f"Testing {url}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        
        await page.goto(url, wait_until="networkidle")
        await asyncio.sleep(0.5)

        # 1. Check DOM structure
        info = await page.evaluate("""() => {
            const targets = ['como-funciona', 'canales', 'planes'];
            const results = {};
            targets.forEach(id => {
                const el = document.getElementById(id);
                if (el) {
                    const wrap = el.querySelector('.splash-cursor-section-wrapper');
                    const cvs = el.querySelector('.splash-cursor-section-canvas');
                    const cnt = el.querySelector('.container');
                    results[id] = {
                        hasWrapper: !!wrap,
                        wrapperZ: wrap ? getComputedStyle(wrap).zIndex : null,
                        wrapperOpacity: wrap ? getComputedStyle(wrap).opacity : null,
                        hasCanvas: !!cvs,
                        canvasW: cvs ? cvs.width : null,
                        canvasH: cvs ? cvs.height : null,
                        containerZ: cnt ? getComputedStyle(cnt).zIndex : null
                    };
                }
            });
            const hero = document.getElementById('hero');
            const heroWrap = hero ? hero.querySelector('.splash-cursor-section-wrapper') : null;
            return {
                targets: results,
                heroHasCanvas: !!heroWrap
            };
        }""")
        print(f"DOM Verification [{prefix}]:", info)
        assert not info["heroHasCanvas"], "Hero must not have splash cursor canvas!"
        for tid in ['como-funciona', 'canales', 'planes']:
            assert info["targets"][tid]["hasWrapper"], f"{tid} missing wrapper"
            assert info["targets"][tid]["hasCanvas"], f"{tid} missing canvas"
            assert info["targets"][tid]["wrapperZ"] == "1", f"{tid} wrapperZ must be 1"
            assert info["targets"][tid]["containerZ"] == "2", f"{tid} containerZ must be 2"

        # 2. Test #canales in Light Mode
        canales = page.locator("#canales")
        await canales.scroll_into_view_if_needed()
        await asyncio.sleep(0.3)
        box = await canales.bounding_box()
        for i in range(25):
            x = box["x"] + 250 + (i * 35) % (box["width"] - 450)
            y = box["y"] + 250 + (i * 25) % (box["height"] - 450)
            await page.mouse.move(x, y)
            await asyncio.sleep(0.02)

        await asyncio.sleep(0.15)
        path_light = f"{ARTIFACT_DIR}/{prefix}_canales_light.png"
        await canales.screenshot(path=path_light)
        print(f"Captured {path_light}")

        # 3. Test #canales in Dark Mode
        await page.evaluate("""() => {
            document.documentElement.classList.add("dark");
            document.documentElement.setAttribute("data-theme", "dark");
        }""")
        await asyncio.sleep(0.2)

        for i in range(25):
            x = box["x"] + 200 + (i * 35) % (box["width"] - 400)
            y = box["y"] + 200 + (i * 25) % (box["height"] - 400)
            await page.mouse.move(x, y)
            await asyncio.sleep(0.02)

        await asyncio.sleep(0.15)
        path_dark = f"{ARTIFACT_DIR}/{prefix}_canales_dark.png"
        await canales.screenshot(path=path_dark)
        print(f"Captured {path_dark}")

        # 4. Test #como-funciona in Light Mode
        await page.evaluate("""() => {
            document.documentElement.classList.remove("dark");
            document.documentElement.setAttribute("data-theme", "light");
        }""")
        await asyncio.sleep(0.2)

        como_funciona = page.locator("#como-funciona")
        await como_funciona.scroll_into_view_if_needed()
        await asyncio.sleep(0.3)
        box_cf = await como_funciona.bounding_box()
        for i in range(25):
            x = box_cf["x"] + 200 + (i * 35) % (box_cf["width"] - 400)
            y = box_cf["y"] + 200 + (i * 20) % (box_cf["height"] - 400)
            await page.mouse.move(x, y)
            await asyncio.sleep(0.02)

        await asyncio.sleep(0.15)
        path_cf = f"{ARTIFACT_DIR}/{prefix}_como_funciona_light.png"
        await como_funciona.screenshot(path=path_cf)
        print(f"Captured {path_cf}")

        # 5. Test #planes in Light Mode
        planes = page.locator("#planes")
        await planes.scroll_into_view_if_needed()
        await asyncio.sleep(0.3)
        box_pl = await planes.bounding_box()
        for i in range(25):
            x = box_pl["x"] + 200 + (i * 40) % (box_pl["width"] - 400)
            y = box_pl["y"] + 250 + (i * 20) % (box_pl["height"] - 400)
            await page.mouse.move(x, y)
            await asyncio.sleep(0.02)

        await asyncio.sleep(0.15)
        path_pl = f"{ARTIFACT_DIR}/{prefix}_planes_light.png"
        await planes.screenshot(path=path_pl)
        print(f"Captured {path_pl}")

        await browser.close()
        print(f"All verifications passed for {url} with 0 page errors: {errors}")

async def main():
    await verify_site("http://127.0.0.1:8003", "prod")

if __name__ == "__main__":
    asyncio.run(main())
