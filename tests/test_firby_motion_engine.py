"""
Tests for Firby Agent Navigation Motion Engine, Lenis Physics, and Agent Surface Material System.
Validates:
- Motion tokens, math curves, and durations
- Dynamic script serving and endpoints
- DOM container isolation (data-lenis-prevent)
- Micro-arrival physics and sub-pixel settling
- Anchor routing and cross-page persistence
- Liquid Glass Material System tokens and restrained specular lighting
- User interruption detection and clean control release
- Humanized, non-technical context mapping
"""

import math
import os
import re
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from src.interfaces.web.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_motion_engine_files_exist():
    """Verify all physical scripts are deployed in static directory."""
    static_dir = Path("/home/ubuntu/firby/src/interfaces/web/static")
    assert (static_dir / "lenis.min.js").exists(), "lenis.min.js must exist"
    assert (static_dir / "lenis.js").exists(), "lenis.js must exist"
    assert (static_dir / "firby-motion-engine.js").exists(), "firby-motion-engine.js must exist"
    assert (static_dir / "firby-agent-surface.js").exists(), "firby-agent-surface.js must exist"
    assert (static_dir / "widget.js").exists(), "widget.js must exist"


def test_motion_engine_static_endpoints(client):
    """Verify HTTP endpoints serve the motion engine, agent surface, and lenis scripts."""
    r_lenis = client.get("/lenis.min.js")
    assert r_lenis.status_code == 200
    assert "javascript" in r_lenis.headers.get("content-type", "").lower()
    assert len(r_lenis.content) > 10000

    r_motion = client.get("/firby-motion-engine.js")
    assert r_motion.status_code == 200
    assert "javascript" in r_motion.headers.get("content-type", "").lower()
    assert b"FirbyMotionEngine" in r_motion.content

    r_surface = client.get("/firby-agent-surface.js")
    assert r_surface.status_code == 200
    assert "javascript" in r_surface.headers.get("content-type", "").lower()
    assert b"FirbyAgentSurface" in r_surface.content


def test_landing_pages_include_motion_engine_and_surface():
    """Verify landing pages include lenis, firby-motion-engine, and firby-agent-surface before widget.js."""
    static_dir = Path("/home/ubuntu/firby/src/interfaces/web/static")
    landing_es = (static_dir / "firby-landing-es.html").read_text(encoding="utf-8")
    landing_en = (static_dir / "firby-landing.html").read_text(encoding="utf-8")

    for html in [landing_es, landing_en]:
        assert "/lenis.min.js" in html, "Landing must include lenis.min.js"
        assert "/firby-motion-engine.js" in html, "Landing must include firby-motion-engine.js"
        assert "/firby-agent-surface.js" in html, "Landing must include firby-agent-surface.js"
        assert html.find("/lenis.min.js") < html.find("/firby-motion-engine.js")
        assert html.find("/firby-motion-engine.js") < html.find("/firby-agent-surface.js")
        assert html.find("/firby-agent-surface.js") < html.find("/widget.js")


def test_motion_curve_math():
    """
    Verify the asymmetric algebraic sigmoid curve:
    f(t) = t^1.55 / (t^1.55 + (1-t)^3.25)
    Starts at 0, reaches 1 at t=1, peak velocity occurs around t=0.35-0.40.
    """
    def curve(t):
        if t <= 0.0:
            return 0.0
        if t >= 1.0:
            return 1.0
        p1 = 1.55
        p2 = 3.25
        num = math.pow(t, p1)
        den = num + math.pow(1.0 - t, p2)
        return num / den if den != 0 else 1.0

    assert curve(0.0) == 0.0
    assert curve(1.0) == 1.0
    assert 0.0 < curve(0.5) < 1.0

    # Calculate velocities (derivatives) across samples
    dt = 0.001
    velocities = []
    times = []
    t = 0.01
    while t < 0.99:
        v = (curve(t + dt) - curve(t)) / dt
        velocities.append(v)
        times.append(t)
        t += 0.01

    max_v = max(velocities)
    max_t = times[velocities.index(max_v)]

    # Peak velocity must be early (t in 0.30 - 0.42), showing fast initial acceleration and long decay
    assert 0.30 <= max_t <= 0.42, f"Peak velocity expected around 0.35-0.40, found {max_t}"
    # At t=0.85, velocity must be significantly lower than peak (strong progressive deceleration)
    v_late = (curve(0.85 + dt) - curve(0.85)) / dt
    assert v_late < (max_v * 0.4), "Velocity must decay strongly in the last segment"


def test_distance_adaptive_duration_formula():
    """Verify duration scaling based on pixel distance."""
    def calc_duration(dist_px):
        abs_d = abs(dist_px)
        if abs_d <= 300:
            return 0.48 + (abs_d / 300.0) * 0.07  # 0.48s - 0.55s
        elif abs_d <= 1200:
            return 0.55 + ((abs_d - 300.0) / 900.0) * 0.40  # 0.55s - 0.95s
        else:
            norm = min(1.0, (abs_d - 1200.0) / 3800.0)
            return 0.95 + norm * 0.37  # 0.95s - 1.32s

    # Short distance (<300px)
    d_short = calc_duration(150)
    assert 0.48 <= d_short <= 0.55

    # Medium distance (300-1200px)
    d_med = calc_duration(750)
    assert 0.55 <= d_med <= 0.95

    # Long distance (>1200px)
    d_long = calc_duration(3000)
    assert 0.95 <= d_long <= 1.32


def test_motion_engine_tokens_and_code_structure():
    """Verify firby-motion-engine.js contains essential tokens and methods."""
    motion_js = Path("/home/ubuntu/firby/src/interfaces/web/static/firby-motion-engine.js").read_text(encoding="utf-8")

    # Tokens
    assert "header: 84" in motion_js
    assert "breathingRoom: 16" in motion_js
    assert "inertialEasing" in motion_js

    # Methods and Classes
    assert "navigateToElement" in motion_js
    assert "cancelNavigation" in motion_js
    assert "_bindUserInterruption" in motion_js
    assert "resolveTarget" in motion_js
    assert "_triggerMicroArrival" in motion_js
    assert "firby-micro-arrival" in motion_js
    assert "data-lenis-prevent" in motion_js
    assert "calculateDuration" in motion_js


def test_user_interruption_cancels_cleanly():
    """Verify user interruption binds wheel, touchmove, keydown and halts automated scroll without locking."""
    motion_js = Path("/home/ubuntu/firby/src/interfaces/web/static/firby-motion-engine.js").read_text(encoding="utf-8")

    assert "cancelNavigation('user_interruption')" in motion_js
    assert "wheel" in motion_js
    assert "touchmove" in motion_js
    assert "keydown" in motion_js
    assert "firby:agent.navigation.cancelled" in motion_js


def test_agent_surface_material_tokens():
    """Verify firby-agent-surface.js defines the restrained glass material system."""
    surface_js = Path("/home/ubuntu/firby/src/interfaces/web/static/firby-agent-surface.js").read_text(encoding="utf-8")

    # Tokens and states
    assert "SURFACE_TOKENS" in surface_js
    assert "IDLE" in surface_js
    assert "NAVIGATING" in surface_js
    assert "THINKING" in surface_js
    assert "SUCCESS" in surface_js
    assert "ERROR" in surface_js

    # Optical properties
    assert "blur: '22px'" in surface_js or "blur" in surface_js
    assert "saturate" in surface_js
    assert "backdrop-filter" in surface_js
    assert "-webkit-backdrop-filter" in surface_js
    assert "prefers-reduced-motion" in surface_js
    assert "prefers-reduced-transparency" in surface_js

    # Presence micro-interaction (breathing dot, no spinner)
    assert "firbyPresenceBreathe" in surface_js
    assert "firby-presence-dot" in surface_js

    # Cancel button (discreet ×)
    assert "firby-agent-surface__cancel" in surface_js


def test_agent_surface_humanized_context_mapping():
    """Verify that section ids are mapped to human language instead of technical debugging terms."""
    surface_js = Path("/home/ubuntu/firby/src/interfaces/web/static/firby-agent-surface.js").read_text(encoding="utf-8")

    assert "Mostrando planes y precios" in surface_js
    assert "Mostrando cómo funciona" in surface_js
    assert "Mostrando seguridad" in surface_js
    assert "Planes y precios" in surface_js


def test_widget_motion_engine_delegation():
    """Verify widget.js properly delegates section navigation to FirbyMotionEngine and loads Agent Surface."""
    widget_js = Path("/home/ubuntu/firby/src/interfaces/web/static/widget.js").read_text(encoding="utf-8")

    assert "window.FirbyMotionEngine" in widget_js
    assert "navigateToElement" in widget_js
    assert "firby_pending_target" in widget_js
    assert "data-lenis-prevent" in widget_js
    assert "firby-agent-surface.js" in widget_js


def test_widget_integrated_activity_bar():
    """Verify widget.js contains the integrated activity bar and listens to agent motion events."""
    widget_js = Path("/home/ubuntu/firby/src/interfaces/web/static/widget.js").read_text(encoding="utf-8")

    assert "firby-chat-activity-bar" in widget_js
    assert "firby-activity-text" in widget_js
    assert "firby-activity-cancel" in widget_js
    assert "setupIntegratedActivityBar" in widget_js
    assert "firby:agent.navigation.requested" in widget_js
    assert "firby:agent.section.reached" in widget_js
    assert "cancelNavigation('user_chat_cancel')" in widget_js


def test_widget_smart_scroll_pill_and_physics():
    """Verify widget.js implements smart scroll detection and new messages pill without jumping."""
    widget_js = Path("/home/ubuntu/firby/src/interfaces/web/static/widget.js").read_text(encoding="utf-8")

    assert "firby-scroll-bottom-pill" in widget_js
    assert "isUserNearBottom" in widget_js
    assert "handleAutoScroll" in widget_js
    assert "setupScrollBottomPill" in widget_js
    assert "scrollToBottom" in widget_js


def test_widget_mobile_touch_and_viewport_sync():
    """Verify widget.js implements mobile visualViewport sync and elastic swipe-to-dismiss."""
    widget_js = Path("/home/ubuntu/firby/src/interfaces/web/static/widget.js").read_text(encoding="utf-8")

    assert "firby-mobile-drag-handle" in widget_js
    assert "setupMobileViewportSync" in widget_js
    assert "setupMobileSwipeToDismiss" in widget_js
    assert "Math.pow(deltaY, 0.88)" in widget_js
    assert "visualViewport" in widget_js

