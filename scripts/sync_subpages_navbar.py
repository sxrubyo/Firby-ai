# -*- coding: utf-8 -*-
"""Synchronize canonical Navbar, Mobile Drawer, and latest Widget v3 across all subpages."""
import os
import re

CANONICAL_NAVBAR_CSS = """/* ==========================================================================
   Top Navigation Floating Glass Capsule (Canonical Navbar & Mobile Drawer)
   ========================================================================== */
.navbar-floating-wrapper {
    position: fixed;
    top: 18px;
    left: 0;
    right: 0;
    z-index: 1000;
    display: flex;
    justify-content: center;
    padding: 0 20px;
    pointer-events: none;
}

.navbar-glass-pill {
    pointer-events: auto;
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 28px;
    width: 100%;
    max-width: 1120px;
    height: 76px;
    padding: 0 16px 0 24px;
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 100px;
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.06), inset 0 1px 1.5px rgba(255, 255, 255, 0.95);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

html.dark .navbar-glass-pill,
html[data-theme="dark"] .navbar-glass-pill {
    background: rgba(15, 23, 42, 0.85);
    border-color: rgba(255, 255, 255, 0.12);
    box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5), inset 0 1px 1.5px rgba(255, 255, 255, 0.1);
}

.navbar-logo {
    display: flex;
    align-items: center;
    margin-left: 12px;
    transition: transform 0.2s ease, opacity 0.2s ease;
}

.navbar-logo:hover {
    transform: scale(1.02);
    opacity: 0.95;
}

.navbar-logo:active {
    transform: scale(0.98);
}

.navbar-logo img {
    height: 30px;
    width: auto;
    display: block;
}

html.dark .navbar-logo img,
html[data-theme="dark"] .navbar-logo img {
    content: url('/assets/figma/firby_brand_logo_white.png') !important;
    filter: brightness(0) invert(1) !important;
}

.footer-brand img,
.footer-logo img,
.footer-logo-img {
    content: url('/assets/figma/firby_brand_logo_dark.png');
}

.navbar-links {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 28px;
}

.navbar-link {
    font-family: var(--font-heading, 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif);
    font-size: 13.5px;
    font-weight: 500;
    color: #334155;
    transition: color 0.2s ease;
    text-decoration: none;
    position: relative;
}

.navbar-link:hover {
    color: var(--text-heading, #09090b);
}

html.dark .navbar-link,
html[data-theme="dark"] .navbar-link {
    color: #94a3b8;
}

html.dark .navbar-link:hover,
html[data-theme="dark"] .navbar-link:hover {
    color: #ffffff;
}

/* Nav Item Dropdown */
.nav-item-dropdown {
    position: relative;
    display: inline-flex;
    align-items: center;
    height: 100%;
}

.nav-dropdown-trigger {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: var(--font-heading, 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif);
    font-size: 13.5px;
    font-weight: 500;
    color: #334155;
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 6px 12px;
    border-radius: 999px;
    transition: all 0.2s ease;
}

.nav-dropdown-trigger:hover,
.nav-item-dropdown:hover .nav-dropdown-trigger {
    color: var(--text-heading, #09090b);
    background: rgba(0, 0, 0, 0.04);
}

.nav-chevron {
    transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    opacity: 0.65;
}

.nav-item-dropdown:hover .nav-chevron {
    transform: rotate(180deg);
    opacity: 1;
}

.nav-dropdown-menu {
    position: absolute;
    top: calc(100% + 14px);
    left: 50%;
    transform: translateX(-50%) translateY(8px);
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    background: rgba(255, 255, 255, 0.94);
    backdrop-filter: blur(28px) saturate(190%);
    -webkit-backdrop-filter: blur(28px) saturate(190%);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 18px;
    box-shadow: 0 20px 48px -10px rgba(0, 0, 0, 0.12), 0 4px 12px rgba(0, 0, 0, 0.03);
    padding: 10px;
    min-width: 290px;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
    z-index: 1100;
}

.nav-dropdown-menu::before {
    content: "";
    position: absolute;
    top: -16px;
    left: 0;
    right: 0;
    height: 16px;
}

.nav-item-dropdown:hover .nav-dropdown-menu {
    opacity: 1;
    visibility: visible;
    pointer-events: auto;
    transform: translateX(-50%) translateY(0);
}

.nav-dropdown-item {
    display: flex;
    flex-direction: column;
    padding: 10px 14px;
    border-radius: 10px;
    text-decoration: none;
    transition: background 0.15s ease;
}

.nav-dropdown-item:hover {
    background: rgba(0, 0, 0, 0.04);
}

.dropdown-item-title {
    font-family: var(--font-heading, 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif);
    font-size: 13.5px;
    font-weight: 700;
    color: var(--text-heading, #09090b);
    line-height: 1.3;
}

.dropdown-item-desc {
    font-family: var(--font-body, 'Inter', system-ui, -apple-system, sans-serif);
    font-size: 11.5px;
    color: var(--text-muted, #64748b);
    line-height: 1.4;
    margin-top: 2px;
}

html.dark .nav-dropdown-trigger,
html[data-theme="dark"] .nav-dropdown-trigger {
    color: #cbd5e1;
}

html.dark .nav-dropdown-trigger:hover,
html[data-theme="dark"] .nav-dropdown-trigger:hover,
html.dark .nav-item-dropdown:hover .nav-dropdown-trigger,
html[data-theme="dark"] .nav-item-dropdown:hover .nav-dropdown-trigger {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.08);
}

html.dark .nav-dropdown-menu,
html[data-theme="dark"] .nav-dropdown-menu {
    background: rgba(18, 18, 21, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 24px 50px -10px rgba(0, 0, 0, 0.8);
}

html.dark .nav-dropdown-item:hover,
html[data-theme="dark"] .nav-dropdown-item:hover {
    background: rgba(255, 255, 255, 0.08);
}

html.dark .dropdown-item-title,
html[data-theme="dark"] .dropdown-item-title {
    color: #f8fafc;
}

html.dark .dropdown-item-desc,
html[data-theme="dark"] .dropdown-item-desc {
    color: #94a3b8;
}

.navbar-actions {
    justify-self: end;
    display: flex;
    align-items: center;
    gap: 10px;
}

.btn-nav-signin {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 8px 18px;
    border-radius: 100px;
    font-family: var(--font-heading, 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif);
    font-size: 13px;
    font-weight: 600;
    color: #09090b;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    text-decoration: none;
    transition: all 0.2s ease;
    cursor: pointer;
}

.btn-nav-signin:hover {
    background: #e2e8f0;
    color: #000000;
}

html.dark .btn-nav-signin,
html[data-theme="dark"] .btn-nav-signin {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.14);
    color: #f8fafc;
}

html.dark .btn-nav-signin:hover,
html[data-theme="dark"] .btn-nav-signin:hover {
    background: rgba(255, 255, 255, 0.14);
    color: #ffffff;
}

/* 1. Navbar CTA (Sin relleno, trazo elegante, chevron) */
.btn-nav-cta {
    background: transparent !important;
    color: #09090b !important;
    border: 1.5px solid #09090b !important;
    font-family: var(--font-heading, 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif) !important;
    font-size: 13.5px !important;
    font-weight: 700 !important;
    box-shadow: none !important;
    padding: 9px 20px !important;
    border-radius: 100px !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    cursor: pointer !important;
    text-decoration: none !important;
    white-space: nowrap !important;
}

.btn-nav-cta:hover {
    background: rgba(0, 0, 0, 0.05) !important;
    border-color: #000000 !important;
    transform: translateY(-1px) !important;
}

.btn-nav-chevron {
    width: 12px;
    height: 12px;
    display: inline-block;
    vertical-align: middle;
    transition: transform 0.2s ease;
}

.btn-nav-cta:hover .btn-nav-chevron {
    transform: translateY(1.5px);
}

html.dark .btn-nav-cta,
html[data-theme="dark"] .btn-nav-cta {
    background: transparent !important;
    border-color: #ffffff !important;
    color: #ffffff !important;
}

html.dark .btn-nav-cta span,
html[data-theme="dark"] .btn-nav-cta span {
    color: #ffffff !important;
}

html.dark .btn-nav-cta svg,
html[data-theme="dark"] .btn-nav-cta svg,
html.dark .btn-nav-chevron,
html[data-theme="dark"] .btn-nav-chevron {
    fill: #ffffff !important;
    color: #ffffff !important;
}

html.dark .btn-nav-cta:hover,
html[data-theme="dark"] .btn-nav-cta:hover {
    background: rgba(255, 255, 255, 0.08) !important;
}

.btn-nav-hamburger {
    display: none !important;
}

/* Mobile Drawer (iOS Sheet) */
.mobile-nav-drawer {
    display: none;
    position: fixed;
    top: 66px;
    left: 10px;
    right: 10px;
    background: rgba(255, 255, 255, 0.98);
    border: 1px solid #e2e8f0;
    border-radius: 24px;
    padding: 20px 18px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
    backdrop-filter: blur(25px);
    -webkit-backdrop-filter: blur(25px);
    transform: translateY(-15px) scale(0.97);
    opacity: 0;
    pointer-events: none;
    transition: transform 0.25s ease, opacity 0.25s ease;
    z-index: 999;
    max-height: calc(100vh - 85px);
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
}

.mobile-nav-drawer.active {
    display: block !important;
    transform: translateY(0) scale(1) !important;
    opacity: 1 !important;
    pointer-events: auto !important;
}

.mobile-nav-links {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.mobile-nav-link {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 14px;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 600;
    color: #0f172a;
    text-decoration: none;
    transition: background 0.15s ease;
}

.mobile-nav-link:hover {
    background: #f1f5f9;
}

.mobile-nav-chevron {
    width: 18px;
    height: 18px;
    stroke: #64748b;
}

.mobile-drawer-bottom-zone {
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid rgba(0, 0, 0, 0.08);
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.btn-mobile-drawer-signin {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    padding: 12px 18px !important;
    border-radius: 9999px !important;
    background: #ffffff !important;
    border: 1px solid rgba(0, 0, 0, 0.12) !important;
    color: #09090b !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    text-decoration: none !important;
    transition: all 0.2s ease !important;
}

.btn-mobile-drawer-signin:hover {
    background: #f8fafc !important;
    border-color: rgba(0, 0, 0, 0.20) !important;
}

/* Mobile Drawer Dark Mode */
html.dark .mobile-nav-drawer,
html[data-theme="dark"] .mobile-nav-drawer {
    background: rgba(13, 17, 23, 0.97) !important;
    background-color: #0d1117 !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    box-shadow: 0 24px 60px -10px rgba(0, 0, 0, 0.85), inset 0 1px 1px rgba(255, 255, 255, 0.12) !important;
    backdrop-filter: blur(32px) saturate(200%) !important;
    -webkit-backdrop-filter: blur(32px) saturate(200%) !important;
}

html.dark .mobile-nav-link,
html[data-theme="dark"] .mobile-nav-link {
    color: #f0f6fc !important;
}

html.dark .mobile-nav-link:hover,
html[data-theme="dark"] .mobile-nav-link:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    color: #ffffff !important;
}

html.dark .mobile-nav-chevron,
html[data-theme="dark"] .mobile-nav-chevron {
    stroke: #8b949e !important;
}

html.dark .mobile-drawer-bottom-zone,
html[data-theme="dark"] .mobile-drawer-bottom-zone {
    border-top: 1px solid rgba(255, 255, 255, 0.12) !important;
}

html.dark .btn-mobile-drawer-signin,
html[data-theme="dark"] .btn-mobile-drawer-signin {
    background: rgba(255, 255, 255, 0.08) !important;
    border-color: rgba(255, 255, 255, 0.16) !important;
    color: #ffffff !important;
}

@media (max-width: 768px) {
    .navbar-floating-wrapper {
        top: 0 !important;
        padding: 0 !important;
    }
    .navbar-glass-pill {
        height: 64px !important;
        padding: 0 16px !important;
        border-radius: 0 !important;
        border-bottom: 1px solid rgba(0, 0, 0, 0.08) !important;
    }
    html.dark .navbar-glass-pill,
    html[data-theme="dark"] .navbar-glass-pill {
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    .navbar-links {
        display: none !important;
    }

    .btn-signin-desktop,
    .btn-nav-signin {
        display: none !important;
    }

    .navbar-logo {
        margin-left: 8px !important;
    }

    .btn-nav-cta {
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        padding: 0 12px !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        height: 34px !important;
        background: transparent !important;
        border: 1.25px solid #000000 !important;
        color: #000000 !important;
        border-radius: 100px !important;
        white-space: nowrap !important;
        flex-shrink: 0 !important;
        gap: 5px !important;
        box-shadow: none !important;
    }

    .btn-nav-cta .btn-nav-chevron {
        display: none !important;
    }

    html.dark .btn-nav-cta,
    html[data-theme="dark"] .btn-nav-cta {
        border-color: #ffffff !important;
        color: #ffffff !important;
    }

    .btn-nav-hamburger {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        flex-direction: column !important;
        gap: 4.5px !important;
        width: 38px !important;
        height: 38px !important;
        background: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        padding: 0 !important;
        margin-left: 6px !important;
        flex-shrink: 0 !important;
        box-sizing: border-box !important;
        -webkit-tap-highlight-color: transparent !important;
    }

    .btn-nav-hamburger .bar {
        display: block !important;
        width: 19px !important;
        height: 2px !important;
        background-color: #09090b !important;
        border-radius: 2px !important;
        transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.2s ease !important;
    }

    html.dark .btn-nav-hamburger .bar,
    html[data-theme="dark"] .btn-nav-hamburger .bar {
        background-color: #ffffff !important;
    }

    .btn-nav-hamburger.active .bar-top {
        transform: translateY(6.5px) rotate(45deg) !important;
    }
    .btn-nav-hamburger.active .bar-mid {
        opacity: 0 !important;
        transform: scaleX(0) !important;
    }
    .btn-nav-hamburger.active .bar-bot {
        transform: translateY(-6.5px) rotate(-45deg) !important;
    }

    .mobile-nav-drawer {
        top: 68px !important;
    }
}"""

CANONICAL_NAVBAR_HTML = """    <!-- Top Navigation Floating Glass Capsule (Píldora Flotante con Efecto Vidrio) -->
    <div class="navbar-floating-wrapper">
        <header class="navbar-glass-pill" id="navbar">
            <a href="/" class="navbar-logo" aria-label="Firby Inicio">
                <img src="/assets/figma/firby_brand_logo_black.png" alt="Firby" width="96" height="32" fetchpriority="high" decoding="async" />
            </a>

            <nav class="navbar-links">
                <!-- Dropdown 1: Producto -->
                <div class="nav-item-dropdown">
                    <button class="nav-dropdown-trigger" type="button" aria-haspopup="true">
                        <span>Producto</span>
                        <svg class="nav-chevron" width="10" height="6" viewBox="0 0 10 6" fill="none"><path d="M1 1L5 5L9 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    </button>
                    <div class="nav-dropdown-menu">
                        <a href="/como-funciona" class="nav-dropdown-item">
                            <span class="dropdown-item-title">Cómo Funciona</span>
                            <span class="dropdown-item-desc">Arquitectura y los 3 momentos de atención</span>
                        </a>
                        <a href="/integraciones" class="nav-dropdown-item">
                            <span class="dropdown-item-title">Integraciones</span>
                            <span class="dropdown-item-desc">Google Calendar, CMS y webhooks</span>
                        </a>
                        <a href="/calculadora" class="nav-dropdown-item">
                            <span class="dropdown-item-title">Calculadora de ROI</span>
                            <span class="dropdown-item-desc">Estima ingresos y horas ahorradas al mes</span>
                        </a>
                        <a href="/docs" class="nav-dropdown-item">
                            <span class="dropdown-item-title">Documentación</span>
                            <span class="dropdown-item-desc">Guía técnica e integración en 60 segundos</span>
                        </a>
                    </div>
                </div>

                <!-- Dropdown 2: Soluciones -->
                <div class="nav-item-dropdown">
                    <button class="nav-dropdown-trigger" type="button" aria-haspopup="true">
                        <span>Soluciones</span>
                        <svg class="nav-chevron" width="10" height="6" viewBox="0 0 10 6" fill="none"><path d="M1 1L5 5L9 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    </button>
                    <div class="nav-dropdown-menu">
                        <a href="/soluciones" class="nav-dropdown-item">
                            <span class="dropdown-item-title">Por Industria</span>
                            <span class="dropdown-item-desc">Salud, legal, academias y multisede</span>
                        </a>
                        <a href="/casos-de-exito" class="nav-dropdown-item">
                            <span class="dropdown-item-title">Casos de Éxito</span>
                            <span class="dropdown-item-desc">Métricas y resultados operativos auditables</span>
                        </a>
                    </div>
                </div>

                <!-- Item 3: Planes -->
                <a href="/planes" class="navbar-link">Planes</a>

                <!-- Dropdown 4: Empresa -->
                <div class="nav-item-dropdown">
                    <button class="nav-dropdown-trigger" type="button" aria-haspopup="true">
                        <span>Empresa</span>
                        <svg class="nav-chevron" width="10" height="6" viewBox="0 0 10 6" fill="none"><path d="M1 1L5 5L9 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    </button>
                    <div class="nav-dropdown-menu">
                        <a href="/seguridad" class="nav-dropdown-item">
                            <span class="dropdown-item-title">Centro de Seguridad</span>
                            <span class="dropdown-item-desc">Aislamiento de datos y gobernanza</span>
                        </a>
                        <a href="/about-us" class="nav-dropdown-item">
                            <span class="dropdown-item-title">Sobre Nosotros</span>
                            <span class="dropdown-item-desc">Nuestra visión y filosofía operativa</span>
                        </a>
                        <a href="/faq" class="nav-dropdown-item">
                            <span class="dropdown-item-title">Preguntas Frecuentes</span>
                            <span class="dropdown-item-desc">Respuestas a dudas comerciales y técnicas</span>
                        </a>
                    </div>
                </div>
            </nav>

            <div class="navbar-actions">
                <a href="/sign-in" class="btn-signin-desktop btn-nav-signin">Iniciar Sesión</a>
                <button class="btn-nav-cta" onclick="window.location.href='/sign-up';" aria-label="Comencemos">
                    <span>Comencemos</span>
                    <svg class="btn-nav-chevron" width="13" height="13" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                        <path d="M11.1581 6.13499C11.3595 5.94644 11.6763 5.95708 11.8651 6.15843C12.0536 6.3599 12.043 6.67669 11.8416 6.86546L7.84165 10.6155C7.64941 10.7954 7.35029 10.7954 7.15805 10.6155L3.15805 6.86546L3.09165 6.78831C2.95746 6.59859 2.96967 6.33468 3.13461 6.15843C3.29985 5.98217 3.56347 5.95169 3.76157 6.07347L3.84165 6.13499L7.49985 9.5637L11.1581 6.13499Z" fill="currentColor"/>
                    </svg>
                </button>
                <button class="btn-nav-hamburger" id="navHamburger" onclick="toggleMobileNav()" aria-label="Menú">
                    <span class="bar bar-top"></span>
                    <span class="bar bar-mid"></span>
                    <span class="bar bar-bot"></span>
                </button>
            </div>
        </header>

        <!-- Mobile Glass Drawer Menu (Native iOS Sheet Style) -->
        <div class="mobile-nav-drawer" id="mobileDrawer">
            <div class="mobile-nav-inner">
                <div class="ios-sheet-handle"></div>
                <nav class="mobile-nav-links">
                    <a href="/como-funciona" class="mobile-nav-link" onclick="closeMobileNav()">
                        <span class="mobile-nav-text">Cómo Funciona</span>
                        <svg class="mobile-nav-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </a>
                    <a href="/soluciones" class="mobile-nav-link" onclick="closeMobileNav()">
                        <span class="mobile-nav-text">Soluciones</span>
                        <svg class="mobile-nav-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </a>
                    <a href="/integraciones" class="mobile-nav-link" onclick="closeMobileNav()">
                        <span class="mobile-nav-text">Integraciones</span>
                        <svg class="mobile-nav-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </a>
                    <a href="/casos-de-exito" class="mobile-nav-link" onclick="closeMobileNav()">
                        <span class="mobile-nav-text">Casos de Éxito</span>
                        <svg class="mobile-nav-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </a>
                    <a href="/calculadora" class="mobile-nav-link" onclick="closeMobileNav()">
                        <span class="mobile-nav-text">Calculadora de ROI</span>
                        <svg class="mobile-nav-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </a>
                    <a href="/planes" class="mobile-nav-link" onclick="closeMobileNav()">
                        <span class="mobile-nav-text">Planes y Precios</span>
                        <svg class="mobile-nav-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </a>
                    <a href="/seguridad" class="mobile-nav-link" onclick="closeMobileNav()">
                        <span class="mobile-nav-text">Centro de Seguridad</span>
                        <svg class="mobile-nav-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </a>
                    <a href="/docs" class="mobile-nav-link" onclick="closeMobileNav()">
                        <span class="mobile-nav-text">Documentación</span>
                        <svg class="mobile-nav-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </a>
                    <a href="/about-us" class="mobile-nav-link" onclick="closeMobileNav()">
                        <span class="mobile-nav-text">Sobre Nosotros</span>
                        <svg class="mobile-nav-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </a>
                    <a href="/faq" class="mobile-nav-link" onclick="closeMobileNav()">
                        <span class="mobile-nav-text">Preguntas Frecuentes</span>
                        <svg class="mobile-nav-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </a>
                </nav>

                <div class="mobile-drawer-bottom-zone">
                    <a href="/sign-in" class="btn-mobile-drawer-signin">
                        <span>Iniciar Sesión (Portal Clientes)</span>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
                    </a>
                </div>
            </div>
        </div>
    </div>"""

NAVBAR_JS = """    <!-- Mobile Drawer Navigation Script -->
    <script>
        function toggleMobileNav() {
            var drawer = document.getElementById('mobileDrawer');
            var btn = document.getElementById('navHamburger');
            if (!drawer) return;
            var isActive = drawer.classList.toggle('active');
            if (btn) btn.classList.toggle('active');
        }

        function closeMobileNav() {
            var drawer = document.getElementById('mobileDrawer');
            var btn = document.getElementById('navHamburger');
            if (drawer) drawer.classList.remove('active');
            if (btn) btn.classList.remove('active');
        }

        document.addEventListener('click', function(e) {
            var drawer = document.getElementById('mobileDrawer');
            var btn = document.getElementById('navHamburger');
            if (drawer && drawer.classList.contains('active')) {
                if (!drawer.contains(e.target) && !btn.contains(e.target)) {
                    closeMobileNav();
                }
            }
        });
    </script>
"""

WIDGET_TAG = """    <script 
      src="/widget.js?v=20261011_voice_engine_v3" 
      data-site-id="firby_landing" 
      data-primary-color="#ffffff" 
      data-border-color="#00825a"
      data-accent-color="#00825a" 
      async>
    </script>
"""

PAGES = [
    'about-us.html', 'soluciones.html', 'planes.html', 'como-funciona.html',
    'integraciones.html', 'seguridad.html', 'casos-de-exito.html', 'calculadora.html',
    'docs.html', 'faq.html', 'terms.html', 'privacy.html', 'data-agreement.html'
]

CLEAN_PATTERN = r'(?:\n\s*(?:html(?:\.dark|\[data-theme=\"dark\"\])\s+)?(?:\.(?:navbar|btn-nav|btn-signin)[^{,]*,\s*)*(?:\.(?:navbar|btn-nav|btn-signin)[^{]*)\{[^}]*\})+'

def sync_page(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Locate and replace navbar CSS
    start_css = content.find('.navbar-floating-wrapper')
    idx_hover = content.find('.btn-nav-cta:hover', start_css)
    end_css = content.find('}', idx_hover) + 1
    if start_css == -1 or idx_hover == -1:
        raise ValueError(f"Could not locate navbar CSS in {path}")

    pre_css = content[:start_css]
    post_css = content[end_css:]

    # Clean residual navbar rules in post_css
    cleaned_post = re.sub(CLEAN_PATTERN, '', post_css)
    content = pre_css + CANONICAL_NAVBAR_CSS + cleaned_post

    # 2. Locate and replace navbar HTML
    start_html = content.find('<div class="navbar-floating-wrapper"')
    m_html = re.search(r'</header>\s*</div>', content[start_html:])
    if start_html == -1 or not m_html:
        raise ValueError(f"Could not locate navbar HTML in {path}")
    end_html = start_html + m_html.end()

    pre_html = content[:start_html]
    post_html = content[end_html:]
    content = pre_html + CANONICAL_NAVBAR_HTML + post_html

    # 3. Update widget.js if present, or add it if not
    if 'widget.js' in content:
        # replace any widget.js script block
        content = re.sub(
            r'<script\s+[^>]*src=[\"\']/widget\.js[^\"]*[\"\'][^>]*>.*?</script>',
            WIDGET_TAG.strip(),
            content,
            flags=re.DOTALL
        )
    else:
        # insert widget before </body>
        idx_body = content.rfind('</body>')
        if idx_body != -1:
            content = content[:idx_body] + WIDGET_TAG + content[idx_body:]

    # 4. Add NAVBAR_JS before </body> if not present
    if 'function toggleMobileNav' not in content:
        idx_body = content.rfind('</body>')
        if idx_body != -1:
            content = content[:idx_body] + NAVBAR_JS + content[idx_body:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully synced: {path}")

def main():
    base_dirs = [
        'src/interfaces/web/static',
        'instances/production/src/interfaces/web/static'
    ]
    for b in base_dirs:
        for p in PAGES:
            target = os.path.join(b, p)
            if os.path.exists(target):
                sync_page(target)
            else:
                print(f"Warning: {target} not found")

        # Also update firby-landing-en.html widget.js
        en_target = os.path.join(b, 'firby-landing-en.html')
        if os.path.exists(en_target):
            with open(en_target, 'r', encoding='utf-8') as f:
                en_content = f.read()
            en_content = re.sub(
                r'widget\.js\?v=[^\"]+',
                'widget.js?v=20261011_voice_engine_v3',
                en_content
            )
            with open(en_target, 'w', encoding='utf-8') as f:
                f.write(en_content)
            print(f"Updated widget version in: {en_target}")

if __name__ == '__main__':
    main()
