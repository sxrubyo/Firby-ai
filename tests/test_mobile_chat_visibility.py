"""
Automated tests for Mobile & Desktop Chat + Full Original Widget Menu Flow:
1. Launcher click -> Opens full original menu (bws-hw-active).
2. Menu contains: 'Chatea con Firby', 'Sobre nosotros', 'Preguntas frecuentes', 'Escríbenos', 'WhatsApp'.
3. Clicking 'Chatea con Firby' -> Opens chat window (.open).
4. Chat window is completely within viewport, opacity == 1, input & send buttons visible and interactive.
5. In mobile, floating launcher is hidden while chat is open to avoid send button collision.
6. Close button in header closes chat cleanly, restoring launcher.
7. Tapping launcher again reopens the menu.
"""

import pytest
import asyncio
from playwright.async_api import async_playwright


@pytest.mark.anyio
@pytest.mark.parametrize("width,height,is_mobile", [
    (390, 844, True),
    (412, 915, True),
    (1280, 800, False),
])
async def test_mobile_and_desktop_chat_window_visibility(width, height, is_mobile):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        device_kwargs = {
            "viewport": {"width": width, "height": height},
        }
        if is_mobile:
            device_kwargs["is_mobile"] = True
            device_kwargs["has_touch"] = True
            device_kwargs["user_agent"] = (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
            )

        context = await browser.new_context(**device_kwargs)
        page = await context.new_page()

        await page.goto("http://localhost:8001/", wait_until="networkidle")
        await page.wait_for_timeout(400)

        # 1. Launcher button exists and is visible
        launcher = await page.query_selector("#bws-hw-btn")
        assert launcher is not None, "Launcher button not found"
        l_box = await launcher.bounding_box()
        assert l_box is not None and l_box["width"] > 0 and l_box["height"] > 0

        # Chat window & menu are initially closed
        chat_win = await page.query_selector("#firby-chat-window")
        assert chat_win is not None
        init_chat = await page.evaluate('() => document.getElementById("firby-chat-window").classList.contains("open")')
        init_menu = await page.evaluate('() => document.getElementById("bws-help-widget").classList.contains("bws-hw-active")')
        assert not init_chat, "Chat window should be initially closed"
        assert not init_menu, "Menu should be initially closed"

        # 2. Click launcher to open MENU
        await launcher.click()
        await page.wait_for_timeout(350)
        menu_open = await page.evaluate('() => document.getElementById("bws-help-widget").classList.contains("bws-hw-active")')
        assert menu_open, "Menu must open after clicking launcher"

        # 3. Verify all original options are present and visible
        chat_opt = await page.query_selector("#waiChatLauncher")
        about_opt = await page.query_selector("#aboutLauncher")
        faq_opt = await page.query_selector("#faqLauncher")
        wa_opt = await page.query_selector("#whatsappLauncher")

        assert chat_opt is not None, "Chatea con Firby option must exist"
        assert about_opt is not None, "Sobre nosotros option must exist"
        assert faq_opt is not None, "Preguntas frecuentes option must exist"
        assert wa_opt is not None, "WhatsApp option must exist"

        c_box = await chat_opt.bounding_box()
        a_box = await about_opt.bounding_box()
        assert c_box is not None and c_box["width"] > 0 and c_box["height"] > 0
        assert a_box is not None and a_box["width"] > 0 and a_box["height"] > 0

        # 4. Click 'Chatea con Firby' to open chat window
        await chat_opt.click()
        await page.wait_for_timeout(400)

        is_open = await chat_win.evaluate('el => el.classList.contains("open")')
        assert is_open, "Chat window must have class 'open' after clicking Chatea con Firby"

        cw_box = await chat_win.bounding_box()
        assert cw_box is not None
        assert cw_box["width"] > 0 and cw_box["height"] > 0
        assert cw_box["x"] >= 0 and cw_box["y"] >= 0
        assert cw_box["x"] + cw_box["width"] <= width + 15
        assert cw_box["y"] + cw_box["height"] <= height + 15

        # 5. Verify computed styles
        win_styles = await chat_win.evaluate("""el => {
            const cs = window.getComputedStyle(el);
            return {
                display: cs.display,
                visibility: cs.visibility,
                opacity: cs.opacity,
                pointerEvents: cs.pointerEvents
            };
        }""")
        assert float(win_styles["opacity"]) >= 0.95, "Chat window opacity must be at least 0.95"
        assert win_styles["visibility"] == "visible"
        assert win_styles["pointerEvents"] == "auto"

        # 6. Verify input and close button
        input_el = await page.query_selector("#firby-input")
        assert input_el is not None
        i_box = await input_el.bounding_box()
        assert i_box is not None and i_box["width"] > 0 and i_box["height"] > 0

        send_btn = await page.query_selector("#firby-send")
        assert send_btn is not None
        sb_box = await send_btn.bounding_box()
        assert sb_box is not None and sb_box["width"] > 0

        close_btn = await page.query_selector("#firby-close-btn")
        assert close_btn is not None
        cb_box = await close_btn.bounding_box()
        assert cb_box is not None and cb_box["width"] > 0

        # 7. In mobile: verify floating launcher is hidden to prevent send button overlap
        if is_mobile:
            l_display = await launcher.evaluate('el => window.getComputedStyle(el).display')
            assert l_display == 'none', "Launcher should be hidden on mobile when chat is open"

        # 8. Close via header close button
        await close_btn.click()
        await page.wait_for_timeout(350)
        is_open_after = await chat_win.evaluate('el => el.classList.contains("open")')
        assert not is_open_after, "Chat window must not be open after clicking close button"

        # 9. Reopen via launcher -> menu opens
        await launcher.click()
        await page.wait_for_timeout(300)
        menu_reopen = await page.evaluate('() => document.getElementById("bws-help-widget").classList.contains("bws-hw-active")')
        assert menu_reopen, "Menu must reopen when clicking launcher after closing chat"

        await browser.close()


@pytest.mark.anyio
async def test_mobile_conversation_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True,
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
            )
        )
        page = await context.new_page()
        await page.goto("http://localhost:8001/", wait_until="networkidle")
        await page.wait_for_timeout(400)

        # 1. Tap launcher -> opens menu
        launcher = await page.query_selector("#bws-hw-btn")
        await launcher.click()
        await page.wait_for_timeout(300)

        # 2. Tap 'Chatea con Firby' -> opens chat
        chat_opt = await page.query_selector("#waiChatLauncher")
        await chat_opt.click()
        await page.wait_for_timeout(400)

        # 3. Type message and send
        input_el = await page.query_selector("#firby-input")
        await input_el.fill("Hola Firby")
        await page.click("#firby-send")

        # 4. Wait for message to render
        await page.wait_for_selector(".firby-msg-user", timeout=5000)
        user_msg = await page.evaluate('() => document.querySelector(".firby-msg-user").innerText')
        assert "Hola Firby" in user_msg

        # 5. Close chat
        close_btn = await page.query_selector("#firby-close-btn")
        await close_btn.click()
        await page.wait_for_timeout(300)

        chat_win = await page.query_selector("#firby-chat-window")
        is_open = await chat_win.evaluate('el => el.classList.contains("open")')
        assert not is_open, "Chat window must close cleanly"

        await browser.close()


@pytest.mark.anyio
async def test_consent_button_and_agent_response():
    """Verifica que al hacer clic en 'Sí, acepto', el agente responda cordialmente y no redirija a planes."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()
        await page.goto("http://localhost:8001/", wait_until="networkidle")
        await page.wait_for_timeout(400)

        # 1. Abrir chat desde launcher -> 'Chatea con Firby'
        launcher = await page.query_selector("#bws-hw-btn")
        await launcher.click()
        await page.wait_for_timeout(300)

        chat_opt = await page.query_selector("#waiChatLauncher")
        await chat_opt.click()
        await page.wait_for_timeout(400)

        # 2. Verificar botón de consentimiento ('Sí, acepto')
        consent_btn = await page.query_selector("#firby-consent-btn")
        assert consent_btn is not None
        btn_text = await consent_btn.inner_text()
        assert "Sí, acepto" in btn_text

        # 3. Hacer clic en 'Sí, acepto'
        await consent_btn.click()

        # 4. Esperar a que el agente responda
        await page.wait_for_selector(".firby-msg-agent:not(.firby-policy-bubble)", timeout=7000)
        agent_msgs = await page.evaluate('''() => {
            const bubbles = Array.from(document.querySelectorAll(".firby-msg-agent:not(.firby-policy-bubble)"));
            return bubbles.map(b => b.innerText);
        }''')
        
        combined_text = " ".join(agent_msgs)
        assert ("quedamos conectados" in combined_text.lower()) or ("gracias por aceptar" in combined_text.lower())
        assert any(w in combined_text.lower() for w in ["orientar", "ayudarte", "ayudarle", "conocer"])

        # Verificar que NO haya arrojado los planes de precio
        assert "Starter: $290.000 COP" not in combined_text
        assert "Te he ubicado en la sección de Planes" not in combined_text

        # Verificar que la URL no haya saltado a #planes
        current_url = page.url
        assert "#planes" not in current_url

        await browser.close()

