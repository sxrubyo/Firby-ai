#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visual Verification Script for Workspace Control Center (/workspace/knowledge)
Captures screenshots of all 6 tabs in high definition.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ARTIFACTS_DIR = Path("/home/ubuntu/.gemini/antigravity-cli/brain/d0e3b6ce-d865-4719-b5ba-e05a69a8ee6c")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

async def capture_workspace():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 950},
            device_scale_factor=2
        )
        
        # Inject login/master token in localStorage before navigation
        await context.add_init_script("""() => {
            localStorage.setItem("firby_master_key", "dev_master_key_firby_2026");
            localStorage.setItem("firby_user_email", "dev@firbyai.lat");
            localStorage.setItem("firby_user_name", "Santiago Rubio Parra");
            localStorage.setItem("firby_onboarding_done", "true");
            localStorage.setItem("firby_dev_bypass", "true");
            localStorage.setItem("firby_dev_mode", "true");
        }""")
        page = await context.new_page()
        await page.goto("http://127.0.0.1:8001/workspace/knowledge", wait_until="networkidle", timeout=20000)
        await asyncio.sleep(2)

        # 1. Capture Roles Tab
        roles_path = ARTIFACTS_DIR / "workspace_control_center_roles.png"
        await page.screenshot(path=str(roles_path), full_page=False)
        print(f"Captured: {roles_path}")

        # 2. Click Directivas & Tono tab
        btn_prompt = page.locator("button:has-text('Directivas & Tono')")
        if await btn_prompt.count() > 0:
            await btn_prompt.first.click()
            await asyncio.sleep(1)
            prompt_path = ARTIFACTS_DIR / "workspace_control_center_prompt.png"
            await page.screenshot(path=str(prompt_path), full_page=False)
            print(f"Captured: {prompt_path}")

        # 3. Click Memoria FTS5 tab
        btn_memory = page.locator("button:has-text('Memoria FTS5')")
        if await btn_memory.count() > 0:
            await btn_memory.first.click()
            await asyncio.sleep(1)
            # Type search query
            input_search = page.locator("input[placeholder*='Escribe términos a buscar']")
            if await input_search.count() > 0:
                await input_search.first.fill("horario")
                btn_search = page.locator("button:has-text('Buscar en FTS5')")
                if await btn_search.count() > 0:
                    await btn_search.first.click()
                    await asyncio.sleep(1.5)
            memory_path = ARTIFACTS_DIR / "workspace_control_center_memory.png"
            await page.screenshot(path=str(memory_path), full_page=False)
            print(f"Captured: {memory_path}")

        # 4. Click Growth & Leads tab
        btn_growth = page.locator("button:has-text('Growth & Leads')")
        if await btn_growth.count() > 0:
            await btn_growth.first.click()
            await asyncio.sleep(1.5)
            # Click preview campaign
            btn_prev = page.locator("button:has-text('Previsualizar Campaña')")
            if await btn_prev.count() > 0:
                await btn_prev.first.click()
                await asyncio.sleep(1.5)
            growth_path = ARTIFACTS_DIR / "workspace_control_center_growth.png"
            await page.screenshot(path=str(growth_path), full_page=False)
            print(f"Captured: {growth_path}")

        # 5. Click Bóveda de APIs tab
        btn_vault = page.locator("button:has-text('Bóveda de APIs')")
        if await btn_vault.count() > 0:
            await btn_vault.first.click()
            await asyncio.sleep(1)
            vault_path = ARTIFACTS_DIR / "workspace_control_center_vault.png"
            await page.screenshot(path=str(vault_path), full_page=False)
            print(f"Captured: {vault_path}")

        # 6. Click Auditor de Voz tab
        btn_voice = page.locator("button:has-text('Auditor de Voz')")
        if await btn_voice.count() > 0:
            await btn_voice.first.click()
            await asyncio.sleep(1)
            btn_audit = page.locator("button:has-text('Auditar y Refinar Guion')")
            if await btn_audit.count() > 0:
                await btn_audit.first.click()
                await asyncio.sleep(1.5)
            voice_path = ARTIFACTS_DIR / "workspace_control_center_voice.png"
            await page.screenshot(path=str(voice_path), full_page=False)
            print(f"Captured: {voice_path}")

        await browser.close()
        print("All tabs captured successfully!")

if __name__ == "__main__":
    asyncio.run(capture_workspace())
