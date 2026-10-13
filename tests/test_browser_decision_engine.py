# -*- coding: utf-8 -*-
"""
Tests for Firby Decision Engine & High-Density Browser Engine.
Verifies:
- Typed Decision Space (BrowserOperation: CLICK, TYPE_TEXT, SCROLL_SLOW, DONE, etc.)
- In-memory Decision Latency (<35ms on CPU)
- Circuit Breaker against repetitive actions
- PlaywrightBrowserPool Context Isolation (~15MB/context)
- Pre-flight target validation and stale DOM prevention
- Cinematic slow scroll and visual framing (halo & strike-through)
- AutonomousAgent interactive browser loop execution
"""
import pytest
import time
from src.core.browser.decision_models import (
    BrowserOperation,
    ObservedElement,
    DecisionRequest,
    DecisionAnswer,
)
from src.core.browser.decision_engine import DecisionEngine
from src.core.browser.browser_engine import BrowserEngine, PlaywrightBrowserPool
from src.core.agent.autonomous_loop import AutonomousAgent


class TestFirbyDecisionEngine:
    def test_decision_engine_typed_choice_and_latency(self):
        """Verifies that decisions are typed, structured, and execute in under 35ms on CPU."""
        engine = DecisionEngine()
        elements = [
            ObservedElement(index=1, tag="button", text="Ver Planes", is_interactive=True),
            ObservedElement(index=2, tag="input", element_type="text", text="Correo Electrónico", is_interactive=True),
            ObservedElement(index=3, tag="a", href="/como-funciona", text="Cómo Funciona", is_interactive=True),
        ]

        # 1. Scroll request
        req1 = DecisionRequest(goal="Muéstrame los planes", current_url="/", elements=elements)
        ans1 = engine.decide(req1)
        assert ans1.operation == BrowserOperation.SCROLL_SLOW
        assert ans1.target == 1
        assert ans1.confidence >= 0.70
        assert ans1.latency_ms < 35.0  # Ultra-fast threshold

        # 2. Type text request
        req2 = DecisionRequest(goal="Mi correo es contacto@firbyai.lat", current_url="/", elements=elements)
        ans2 = engine.decide(req2)
        assert ans2.operation == BrowserOperation.TYPE_TEXT
        assert ans2.target == 2
        assert "contacto@firbyai.lat" in ans2.text_to_type
        assert ans2.latency_ms < 35.0

    def test_decision_engine_circuit_breaker(self):
        """Verifies that repeating identical failing actions trips the circuit breaker."""
        engine = DecisionEngine(circuit_breaker_limit=3)
        elements = [ObservedElement(index=1, tag="button", text="Comprar", is_interactive=True)]

        repeated_history = [
            {"operation": "CLICK", "target": 1},
            {"operation": "CLICK", "target": 1},
            {"operation": "CLICK", "target": 1},
        ]
        req = DecisionRequest(goal="Comprar producto", current_url="/", elements=elements, history=repeated_history)
        ans = engine.decide(req)

        assert ans.operation == BrowserOperation.BLOCKED
        assert ans.requires_human_escalation is True
        assert "Circuit breaker" in ans.reasoning_summary

    def test_browser_pool_context_isolation(self):
        """Verifies shared browser pool generates multiple isolated contexts."""
        pool = PlaywrightBrowserPool.get_instance(headless=True)
        ctx1 = pool.create_context()
        ctx2 = pool.create_context()

        assert ctx1 is not None
        assert ctx2 is not None
        assert ctx1 != ctx2

        p1 = ctx1.new_page()
        p2 = ctx2.new_page()

        p1.set_content("<html><body><h1>Session 1</h1></body></html>")
        p2.set_content("<html><body><h1>Session 2</h1></body></html>")

        assert "Session 1" in p1.inner_text("body")
        assert "Session 2" in p2.inner_text("body")

        ctx1.close()
        ctx2.close()

    def test_browser_engine_preflight_target_validation(self):
        """Verifies pre-flight validation prevents clicking non-existent targets."""
        with BrowserEngine(headless=True) as engine:
            page = engine._ensure_browser()
            page.set_content("<html><body><button data-firby-index='1'>Enviar</button></body></html>")

            # Valid target
            valid, sel = engine.validate_target_exists(1)
            assert valid is True
            assert sel == "[data-firby-index='1']"

            # Invalid target
            invalid, _ = engine.validate_target_exists(99)
            assert invalid is False

            # Click on invalid target must fail cleanly without throwing uncaught exceptions
            res = engine.click(99)
            assert res["success"] is False
            assert "no existe" in res["error"]

    def test_browser_engine_cinematic_scroll_and_framing(self):
        """Verifies slow cinematic scroll, halo focus, and text strike-through."""
        with BrowserEngine(headless=True) as engine:
            page = engine._ensure_browser()
            page.set_content("""
            <html>
              <body style="min-height: 2000px; padding-top: 50px;">
                <div id="hero">Inicio</div>
                <div id="pricing" data-firby-index="1" style="margin-top: 1200px;">
                  <h2>Planes y Tarifas</h2>
                  <p id="desc">Antes 5 horas de soporte manual</p>
                </div>
              </body>
            </html>
            """)

            # 1. Slow scroll
            scroll_res = engine.scroll_slow(target=1, duration_ms=400)
            assert scroll_res["success"] is True

            # 2. Highlight element
            hl_res = engine.highlight_element(1, duration_ms=1000)
            assert hl_res["success"] is True

            # 3. Strike word
            strike_res = engine.strike_word(1, "Antes")
            assert strike_res["success"] is True

    def test_autonomous_agent_interactive_decision_loop(self):
        """Verifies AutonomousAgent executes multi-step interactive loop with DecisionEngine."""
        agent = AutonomousAgent()
        # Seed an interactive page in browser
        page = agent.browser_engine._ensure_browser()
        page.set_content("""
        <html>
          <body>
            <h1>Portal de Servicios</h1>
            <button data-firby-index="1">Ver Planes</button>
            <input data-firby-index="2" placeholder="Tu Correo" value="" />
          </body>
        </html>
        """)

        # Execute interactive loop directly
        steps = agent._run_interactive_browser_loop(goal="Muéstrame los planes", max_steps=3)
        assert len(steps) >= 1
        assert steps[0]["operation"] == "SCROLL_SLOW"
        assert steps[0]["target"] == 1
        assert steps[0]["latency_ms"] < 35.0

        agent.browser_engine.close()
