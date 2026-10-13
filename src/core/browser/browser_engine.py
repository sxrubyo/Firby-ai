# -*- coding: utf-8 -*-
"""
Firby Browser Automation Engine (inspired by browser-use & browsercode).
Provides real headless browser control: DOM tree extraction with interactive index labeling,
coordinate-free clicking, typing, text extraction, screenshots, cinematic slow scrolling,
and visual framing (halo highlight & strike-through) with shared pool architecture.
"""
from __future__ import annotations

import logging
import threading
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple

from .decision_models import BrowserOperation, DecisionAnswer, ObservedElement

logger = logging.getLogger("firby.browser_engine")

try:
    from playwright.sync_api import sync_playwright, Browser, Page, Playwright, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class PlaywrightBrowserPool:
    """
    Pool de navegador compartido de alta densidad.
    Mantiene un solo proceso Chromium daemon en memoria y genera
    BrowserContexts aislados y efímeros (~15 MB RAM por sesión).
    """
    _instance: Optional["PlaywrightBrowserPool"] = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls, headless: bool = True) -> "PlaywrightBrowserPool":
        with cls._lock:
            if cls._instance is None or cls._instance._browser is None:
                cls._instance = cls(headless=headless)
            return cls._instance

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        if PLAYWRIGHT_AVAILABLE:
            try:
                self._playwright = sync_playwright().start()
                self._browser = self._playwright.chromium.launch(
                    headless=self.headless,
                    args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
                )
            except Exception as e:
                logger.error(f"[BrowserPool] Error iniciando Chromium: {e}")

    def create_context(self) -> Optional[BrowserContext]:
        if not self._browser:
            return None
        return self._browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

    def close(self):
        with PlaywrightBrowserPool._lock:
            if self._browser:
                try:
                    self._browser.close()
                except Exception:
                    pass
                self._browser = None
            if self._playwright:
                try:
                    self._playwright.stop()
                except Exception:
                    pass
                self._playwright = None
            PlaywrightBrowserPool._instance = None


class BrowserEngine:
    """
    Automated Headless Browser Controller.
    Implements index-based interaction patterns from browser-use:
    extracts actionable elements into indexed list `[1] [2]...` so the agent
    can click, fill forms, and navigate without brittle CSS coordinates.
    Supports slow cinematic scrolling, target pre-flight verification, and Jev execution.
    """

    def __init__(self, headless: bool = True, timeout_ms: int = 30000, use_pool: bool = True):
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.use_pool = use_pool
        self._pool: Optional[PlaywrightBrowserPool] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._indexed_elements: Dict[int, Dict[str, Any]] = {}
        self._last_dom_fingerprint: str = ""

        # Fallback para modo sin pool
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None

    def _ensure_browser(self) -> Page:
        """Initializes browser context and page if not already running."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright is not installed in the environment.")

        if self._page is None or self._page.is_closed():
            if self.use_pool:
                self._pool = PlaywrightBrowserPool.get_instance(headless=self.headless)
                self._context = self._pool.create_context()
                if self._context:
                    self._page = self._context.new_page()
                    self._page.set_default_timeout(self.timeout_ms)
                    return self._page

            # Fallback a creación directa si el pool no está activo
            if self._playwright is None:
                self._playwright = sync_playwright().start()
            if self._browser is None:
                self._browser = self._playwright.chromium.launch(
                    headless=self.headless,
                    args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
                )
            self._page = self._browser.new_page(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            self._page.set_default_timeout(self.timeout_ms)

        return self._page

    def navigate(self, url: str) -> Dict[str, Any]:
        """Navigates to the specified URL and returns status and title."""
        try:
            page = self._ensure_browser()
            if not url.startswith(("http://", "https://", "file://")):
                url = "https://" + url

            response = page.goto(url, wait_until="load", timeout=self.timeout_ms)
            status = response.status if response else 200
            title = page.title()

            # Reset indexed elements on navigation
            self._indexed_elements.clear()
            self._last_dom_fingerprint = str(time.time())

            return {
                "success": True,
                "url": page.url,
                "title": title,
                "status": status,
            }
        except Exception as exc:
            return {
                "success": False,
                "url": url,
                "error": str(exc),
            }

    def get_interactive_elements(self) -> Dict[str, Any]:
        """
        Extracts interactive DOM elements (buttons, links, inputs, selects, textareas)
        and indexes them with numbers [1], [2], [3] (browser-use pattern).
        """
        try:
            page = self._ensure_browser()

            js_script = """
            () => {
                const elements = [];
                const selector = 'button, a[href], input, select, textarea, [role="button"], [role="link"], [role="tab"], [onclick]';
                const nodes = document.querySelectorAll(selector);

                let idx = 1;
                for (const node of nodes) {
                    const rect = node.getBoundingClientRect();
                    const style = window.getComputedStyle(node);

                    const isVisible = (
                        rect.width > 0 &&
                        rect.height > 0 &&
                        style.visibility !== 'hidden' &&
                        style.display !== 'none' &&
                        style.opacity !== '0'
                    );

                    if (isVisible) {
                        const tag = node.tagName.toLowerCase();
                        const type = node.getAttribute('type') || '';
                        const text = (node.innerText || node.value || node.getAttribute('placeholder') || node.getAttribute('aria-label') || '').trim();
                        const id = node.id || '';
                        const name = node.getAttribute('name') || '';
                        const href = node.getAttribute('href') || '';
                        const role = node.getAttribute('role') || tag;
                        const value = node.value || '';

                        elements.push({
                            index: idx,
                            tag: tag,
                            type: type,
                            role: role,
                            text: text.slice(0, 100),
                            id: id,
                            name: name,
                            href: href ? href.slice(0, 120) : '',
                            value: value.slice(0, 80)
                        });

                        node.setAttribute('data-firby-index', idx.toString());
                        idx++;
                    }
                }
                return elements;
            }
            """
            elements = page.evaluate(js_script)

            self._indexed_elements = {item["index"]: item for item in elements}

            observed_models = []
            lines = []
            for item in elements[:60]:
                obs = ObservedElement(
                    index=item["index"],
                    tag=item["tag"],
                    role=item.get("role"),
                    text=item.get("text", ""),
                    element_type=item.get("type"),
                    href=item.get("href"),
                    value=item.get("value"),
                    is_interactive=True
                )
                observed_models.append(obs)
                lines.append(obs.to_display_string())

            representation = "\n".join(lines) if lines else "No interactive elements found."
            return {
                "success": True,
                "count": len(elements),
                "interactive_tree": representation,
                "elements": elements[:60],
                "observed_models": observed_models,
            }
        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
            }

    def validate_target_exists(self, target: Union[int, str]) -> Tuple[bool, Optional[str]]:
        """Valida que el elemento objetivo exista y siga visible antes de ejecutar una mutación."""
        try:
            page = self._ensure_browser()
            if isinstance(target, int) or (isinstance(target, str) and target.isdigit()):
                selector = f"[data-firby-index='{int(target)}']"
            else:
                selector = str(target)

            loc = page.locator(selector).first
            if loc.count() > 0 and loc.is_visible():
                return True, selector
            return False, selector
        except Exception:
            return False, None

    def click(self, target: Union[int, str]) -> Dict[str, Any]:
        """Clicks an element either by index (e.g. 1) or by CSS selector with pre-flight check."""
        try:
            page = self._ensure_browser()
            valid, selector = self.validate_target_exists(target)
            if not valid:
                return {
                    "success": False,
                    "action": "click",
                    "target": target,
                    "error": f"Elemento objetivo {target} no existe o no es visible en el DOM actual",
                }

            page.click(selector)
            page.wait_for_timeout(400)

            return {
                "success": True,
                "action": "click",
                "target": target,
                "current_url": page.url,
                "title": page.title(),
            }
        except Exception as exc:
            return {
                "success": False,
                "action": "click",
                "target": target,
                "error": str(exc),
            }

    def type_text(
        self,
        target: Union[int, str],
        text: str,
        clear_first: bool = True,
        press_enter: bool = False,
    ) -> Dict[str, Any]:
        """Types text into an input field with pre-flight validation."""
        try:
            page = self._ensure_browser()
            valid, selector = self.validate_target_exists(target)
            if not valid:
                return {
                    "success": False,
                    "action": "type",
                    "target": target,
                    "error": f"Elemento objetivo {target} no existe o no es editable",
                }

            if clear_first:
                page.fill(selector, "")
            page.type(selector, text, delay=20)

            if press_enter:
                page.press(selector, "Enter")
                page.wait_for_timeout(400)

            return {
                "success": True,
                "action": "type",
                "target": target,
                "text_length": len(text),
                "current_url": page.url,
            }
        except Exception as exc:
            return {
                "success": False,
                "action": "type",
                "target": target,
                "error": str(exc),
            }

    def select_option(self, target: Union[int, str], value: str) -> Dict[str, Any]:
        """Selecciona una opción en un elemento <select>."""
        try:
            page = self._ensure_browser()
            valid, selector = self.validate_target_exists(target)
            if not valid:
                return {"success": False, "action": "select", "target": target, "error": "Target no encontrado"}

            page.select_option(selector, value=value)
            page.wait_for_timeout(300)
            return {"success": True, "action": "select", "target": target, "value": value}
        except Exception as exc:
            return {"success": False, "action": "select", "target": target, "error": str(exc)}

    def scroll_slow(
        self,
        target: Optional[Union[int, str]] = None,
        direction: str = "down",
        pixels: int = 500,
        duration_ms: int = 1500,
    ) -> Dict[str, Any]:
        """
        Ejecuta un scroll cinemático lento y suave por el usuario,
        deslizando la pantalla visiblemente con curva cúbica.
        """
        try:
            page = self._ensure_browser()
            js_scroll = f"""
            () => {{
                return new Promise((resolve) => {{
                    const startY = window.pageYOffset || document.documentElement.scrollTop;
                    let targetY = startY;

                    const targetVal = {repr(str(target) if target is not None else None)};
                    if (targetVal) {{
                        let el = null;
                        if (!isNaN(targetVal)) {{
                            el = document.querySelector(`[data-firby-index='${{targetVal}}']`);
                        }} else {{
                            el = document.querySelector(targetVal) || document.getElementById(targetVal.replace('#', ''));
                        }}
                        if (el) {{
                            const rect = el.getBoundingClientRect();
                            targetY = Math.max(0, startY + rect.top - 84);
                        }} else {{
                            targetY = startY + ({pixels} * ({1 if direction == 'down' else -1}));
                        }}
                    }} else {{
                        targetY = startY + ({pixels} * ({1 if direction == 'down' else -1}));
                    }}

                    const duration = {duration_ms};
                    const startTime = performance.now();

                    function easeInOutCubic(t) {{
                        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
                    }}

                    function step(now) {{
                        const elapsed = now - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        const current = startY + (targetY - startY) * easeInOutCubic(progress);
                        window.scrollTo(0, current);

                        if (progress < 1) {{
                            requestAnimationFrame(step);
                        }} else {{
                            window.scrollTo(0, targetY);
                            resolve({{ startY, targetY, duration }});
                        }}
                    }}

                    requestAnimationFrame(step);
                }});
            }}
            """
            result = page.evaluate(js_scroll)
            return {
                "success": True,
                "action": "scroll_slow",
                "target": target,
                "details": result,
            }
        except Exception as exc:
            return {"success": False, "action": "scroll_slow", "error": str(exc)}

    def highlight_element(self, target: Union[int, str], duration_ms: int = 3000) -> Dict[str, Any]:
        """Ilumina sutilmente el elemento con un halo de foco verde lima respirable."""
        try:
            page = self._ensure_browser()
            valid, selector = self.validate_target_exists(target)
            if not valid:
                return {"success": False, "error": "Target no encontrado"}

            js_highlight = f"""
            () => {{
                const el = document.querySelector({repr(selector)});
                if (!el) return false;
                el.style.outline = '2px solid #b9fa01';
                el.style.outlineOffset = '4px';
                el.style.boxShadow = '0 0 24px rgba(185, 250, 1, 0.4)';
                el.style.transition = 'box-shadow 0.4s ease, outline 0.4s ease';

                setTimeout(() => {{
                    el.style.outline = '';
                    el.style.outlineOffset = '';
                    el.style.boxShadow = '';
                }}, {duration_ms});
                return true;
            }}
            """
            ok = page.evaluate(js_highlight)
            return {"success": bool(ok), "action": "highlight", "target": target}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def strike_word(self, target: Union[int, str], keyword: str) -> Dict[str, Any]:
        """Aplica un tachón animado sobre una palabra clave dentro del elemento."""
        try:
            page = self._ensure_browser()
            valid, selector = self.validate_target_exists(target)
            if not valid:
                return {"success": False, "error": "Target no encontrado"}

            js_strike = f"""
            () => {{
                const el = document.querySelector({repr(selector)});
                if (!el || !{repr(keyword)}) return false;
                const regex = new RegExp(`(${{{repr(keyword)}}})`, 'i');
                const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
                let node;
                while ((node = walker.nextNode())) {{
                    if (regex.test(node.nodeValue)) {{
                        const span = document.createElement('span');
                        span.style.textDecoration = 'line-through';
                        span.style.textDecorationColor = '#ef4444';
                        span.style.textDecorationThickness = '2px';
                        span.innerHTML = node.nodeValue.replace(regex, `<span style="text-decoration: line-through; text-decoration-color: #ef4444; color: #94a3b8;">$1</span>`);
                        if (node.parentNode) {{
                            node.parentNode.replaceChild(span, node);
                            return true;
                        }}
                    }}
                }}
                return false;
            }}
            """
            ok = page.evaluate(js_strike)
            return {"success": bool(ok), "action": "strike_word", "target": target, "keyword": keyword}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def execute_decision(self, decision: DecisionAnswer) -> Dict[str, Any]:
        """Ejecuta una micro-acción tipada emitida por el Decision Engine."""
        op = decision.operation

        if op == BrowserOperation.CLICK:
            return self.click(decision.target or decision.target_selector or 1)
        elif op == BrowserOperation.TYPE_TEXT:
            return self.type_text(decision.target or 1, decision.text_to_type or "")
        elif op == BrowserOperation.SELECT:
            return self.select_option(decision.target or 1, decision.select_value or "")
        elif op == BrowserOperation.SCROLL_SLOW:
            scroll_res = self.scroll_slow(target=decision.target or decision.scroll_target, duration_ms=1400)
            if decision.target:
                self.highlight_element(decision.target)
            if decision.strike_keyword and decision.target:
                self.strike_word(decision.target, decision.strike_keyword)
            return scroll_res
        elif op == BrowserOperation.SCROLL_DOWN:
            return self.scroll_slow(pixels=500, direction="down", duration_ms=1200)
        elif op == BrowserOperation.SCROLL_UP:
            return self.scroll_slow(pixels=500, direction="up", duration_ms=1200)
        elif op == BrowserOperation.HIGHLIGHT:
            return self.highlight_element(decision.target or 1)
        elif op == BrowserOperation.STRIKE_TEXT:
            return self.strike_word(decision.target or 1, decision.strike_keyword or "")
        elif op == BrowserOperation.WAIT:
            time.sleep(0.5)
            return {"success": True, "action": "wait", "duration_ms": 500}
        elif op == BrowserOperation.DONE:
            return {"success": True, "action": "done", "status": "completed"}
        elif op == BrowserOperation.BLOCKED:
            return {"success": False, "action": "blocked", "error": "Operation declared blocked"}
        else:
            return {"success": False, "error": f"Operación no soportada: {op}"}

    def get_aria_snapshot(self) -> Dict[str, Any]:
        """Extracts high-fidelity semantic ARIA accessibility tree from Playwright."""
        try:
            page = self._ensure_browser()
            if hasattr(page, "aria_snapshot"):
                snapshot = page.aria_snapshot()
            else:
                body = page.locator("body")
                snapshot = body.aria_snapshot() if hasattr(body, "aria_snapshot") else ""

            return {
                "success": True,
                "url": page.url,
                "title": page.title(),
                "aria_snapshot": snapshot,
                "length": len(snapshot),
            }
        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
            }

    def extract_text(self, max_chars: int = 10000) -> Dict[str, Any]:
        """Extracts clean inner text of the page body."""
        try:
            page = self._ensure_browser()
            text = page.inner_text("body")
            clean_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
            return {
                "success": True,
                "title": page.title(),
                "url": page.url,
                "content": clean_text[:max_chars],
                "total_chars": len(clean_text),
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def screenshot(self, output_path: Union[str, Path]) -> Dict[str, Any]:
        """Takes a full page screenshot and saves it to output_path."""
        try:
            page = self._ensure_browser()
            path_obj = Path(output_path).resolve()
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(path_obj), full_page=False)
            return {
                "success": True,
                "path": str(path_obj),
                "size_bytes": path_obj.stat().st_size,
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def close(self) -> None:
        """Closes page and context without killing shared browser daemon."""
        if self._page and not self._page.is_closed():
            try:
                self._page.close()
            except Exception:
                pass
            self._page = None

        if self._context:
            try:
                self._context.close()
            except Exception:
                pass
            self._context = None

        # Si se usó navegador no-pool, cerrarlo
        if not self.use_pool:
            if self._browser:
                try:
                    self._browser.close()
                except Exception:
                    pass
                self._browser = None
            if self._playwright:
                try:
                    self._playwright.stop()
                except Exception:
                    pass
                self._playwright = None

        self._indexed_elements.clear()

    def __enter__(self) -> "BrowserEngine":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
