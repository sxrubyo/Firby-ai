// -*- coding: utf-8 -*-
/**
 * Firby AI — Agent Surface Material System (Liquid Glass & Presence Layer)
 * =========================================================================
 * Capa flotante ultra-ligera, táctil y refinada que comunica la presencia activa
 * del agente digital sobre la interfaz web, siguiendo estándares SaaS de alta gama
 * (Linear, Stripe, Vercel, Apple):
 *
 * MATERIAL SYSTEM & REFINAMIENTO ÓPTICO:
 * - Liquid Glass moderado con refracción y filtrado selectivo (backdrop-filter).
 * - Restrained specular lighting (bisel superior y brillo ambiental sutil).
 * - Cero efectos neon, cyberpunk o destellos estridentes.
 * - Transición de bordes tipo menisco óptico (inner highlight + borde sub-pixel).
 * - Fondo desenfocado, suavizado y ligeramente levantado pero completamente reconocible.
 * - Micro-interacción de vida (punto de presencia que respira suavemente a 2.4s).
 * - Duración y físicas spring: cubic-bezier(0.16, 1, 0.3, 1).
 * - Desvanecimiento calmado al terminar la acción (permanece visible solo durante la acción).
 * - Soporte adaptativo para modo claro / oscuro y degradación accesible a sólidos.
 */

(function (window, document) {
  'use strict';

  if (window.FirbyAgentSurface) return;

  // ── 1. Tokens Centralizados del Sistema de Material ──
  const SURFACE_TOKENS = {
    themes: {
      light: {
        bg: 'rgba(255, 255, 255, 0.70)',
        bgHover: 'rgba(255, 255, 255, 0.82)',
        border: 'rgba(0, 0, 0, 0.08)',
        rim: 'rgba(255, 255, 255, 0.65)',
        shadow: '0 16px 36px -8px rgba(0, 0, 0, 0.08), 0 4px 12px -2px rgba(0, 0, 0, 0.03)',
        text: '#0f172a',
        muted: '#64748b',
        brand: '#00825a',
        ring: 'rgba(0, 130, 90, 0.22)',
        divider: 'rgba(0, 0, 0, 0.07)',
        btnHover: 'rgba(0, 0, 0, 0.05)'
      },
      dark: {
        bg: 'rgba(18, 24, 28, 0.74)',
        bgHover: 'rgba(24, 32, 38, 0.85)',
        border: 'rgba(255, 255, 255, 0.12)',
        rim: 'rgba(255, 255, 255, 0.20)',
        shadow: '0 20px 48px -8px rgba(0, 0, 0, 0.55), 0 6px 16px -2px rgba(0, 0, 0, 0.35)',
        text: '#f8fafc',
        muted: '#94a3b8',
        brand: '#b9fa01',
        ring: 'rgba(185, 250, 1, 0.25)',
        divider: 'rgba(255, 255, 255, 0.10)',
        btnHover: 'rgba(255, 255, 255, 0.08)'
      }
    },
    glass: {
      blur: '22px',
      saturate: '140%',
      brightness: '104%',
      radiusPill: '9999px',
      elevation: '10000',
      springEase: 'cubic-bezier(0.16, 1, 0.3, 1)',
      enterMs: 260,
      exitMs: 240
    },
    states: {
      IDLE: 'idle',
      THINKING: 'thinking',
      ACTING: 'acting',
      NAVIGATING: 'navigating',
      WAITING: 'waiting',
      SUCCESS: 'success',
      NEEDS_INPUT: 'needs_input',
      ERROR: 'error'
    }
  };

  // Mapeo amigable de secciones a lenguaje humano sobrio
  function humanizeSection(target) {
    if (!target) return 'Navegando';
    const clean = String(target).replace(/^[#/]+/, '').toLowerCase();
    const map = {
      'planes': 'Mostrando planes y precios',
      'pricing': 'Mostrando planes y precios',
      'precios': 'Mostrando planes y precios',
      'como-funciona': 'Mostrando cómo funciona',
      'how-it-works': 'Mostrando cómo funciona',
      'seguridad-cumplimiento': 'Mostrando seguridad',
      'seguridad': 'Mostrando seguridad',
      'security': 'Mostrando seguridad',
      'canales': 'Mostrando canales de atención',
      'channels': 'Mostrando canales de atención',
      'faq': 'Mostrando preguntas frecuentes',
      'preguntas': 'Mostrando preguntas frecuentes',
      'sobre-nosotros': 'Abriendo Sobre Nosotros',
      'about': 'Abriendo Sobre Nosotros',
      'hero': 'Mostrando inicio'
    };
    if (map[clean]) return map[clean];
    const readable = clean.replace(/[-_]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
    return 'Mostrando ' + readable;
  }

  function humanizeSuccess(target) {
    if (!target) return 'Listo';
    const clean = String(target).replace(/^[#/]+/, '').toLowerCase();
    const map = {
      'planes': 'Planes y precios',
      'pricing': 'Planes y precios',
      'precios': 'Planes y precios',
      'como-funciona': 'Cómo funciona',
      'how-it-works': 'Cómo funciona',
      'seguridad-cumplimiento': 'Seguridad y cumplimiento',
      'seguridad': 'Seguridad',
      'security': 'Seguridad',
      'canales': 'Canales de atención',
      'channels': 'Canales de atención',
      'faq': 'Preguntas frecuentes',
      'preguntas': 'Preguntas frecuentes',
      'sobre-nosotros': 'Sobre Nosotros',
      'hero': 'Inicio'
    };
    if (map[clean]) return map[clean];
    return clean.replace(/[-_]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  class AgentSurfaceEngine {
    constructor() {
      this.state = SURFACE_TOKENS.states.IDLE;
      this.container = null;
      this.capsuleEl = null;
      this.textEl = null;
      this.dotEl = null;
      this.cancelBtn = null;
      this.hideTimer = null;
      this.isReducedMotion = false;
      this.isReducedTransparency = false;
      this.init();
    }

    init() {
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => this._bootstrap());
      } else {
        this._bootstrap();
      }
    }

    _bootstrap() {
      this._checkAccessibility();
      this._injectStyles();
      this._mountDOM();
      this._bindEvents();
    }

    _checkAccessibility() {
      if (typeof window !== 'undefined' && window.matchMedia) {
        const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
        this.isReducedMotion = motionQuery.matches;
        motionQuery.addEventListener('change', (e) => {
          this.isReducedMotion = e.matches;
        });

        const transQuery = window.matchMedia('(prefers-reduced-transparency: reduce)');
        this.isReducedTransparency = transQuery.matches;
        transQuery.addEventListener('change', (e) => {
          this.isReducedTransparency = e.matches;
        });
      }
    }

    _injectStyles() {
      if (document.getElementById('firby-agent-surface-styles')) return;

      const style = document.createElement('style');
      style.id = 'firby-agent-surface-styles';
      style.textContent = `
        :root {
          --firby-surface-bg: ${SURFACE_TOKENS.themes.light.bg};
          --firby-surface-bg-hover: ${SURFACE_TOKENS.themes.light.bgHover};
          --firby-surface-border: ${SURFACE_TOKENS.themes.light.border};
          --firby-surface-rim: ${SURFACE_TOKENS.themes.light.rim};
          --firby-surface-shadow: ${SURFACE_TOKENS.themes.light.shadow};
          --firby-surface-text: ${SURFACE_TOKENS.themes.light.text};
          --firby-surface-muted: ${SURFACE_TOKENS.themes.light.muted};
          --firby-surface-brand: ${SURFACE_TOKENS.themes.light.brand};
          --firby-surface-ring: ${SURFACE_TOKENS.themes.light.ring};
          --firby-surface-divider: ${SURFACE_TOKENS.themes.light.divider};
          --firby-surface-btn-hover: ${SURFACE_TOKENS.themes.light.btnHover};
          --firby-surface-blur: ${SURFACE_TOKENS.glass.blur};
          --firby-surface-saturate: ${SURFACE_TOKENS.glass.saturate};
          --firby-surface-brightness: ${SURFACE_TOKENS.glass.brightness};
        }

        /* Modo Oscuro Adaptativo */
        html.dark, html[data-theme="dark"], body.dark, [data-theme="dark"] {
          --firby-surface-bg: ${SURFACE_TOKENS.themes.dark.bg};
          --firby-surface-bg-hover: ${SURFACE_TOKENS.themes.dark.bgHover};
          --firby-surface-border: ${SURFACE_TOKENS.themes.dark.border};
          --firby-surface-rim: ${SURFACE_TOKENS.themes.dark.rim};
          --firby-surface-shadow: ${SURFACE_TOKENS.themes.dark.shadow};
          --firby-surface-text: ${SURFACE_TOKENS.themes.dark.text};
          --firby-surface-muted: ${SURFACE_TOKENS.themes.dark.muted};
          --firby-surface-brand: ${SURFACE_TOKENS.themes.dark.brand};
          --firby-surface-ring: ${SURFACE_TOKENS.themes.dark.ring};
          --firby-surface-divider: ${SURFACE_TOKENS.themes.dark.divider};
          --firby-surface-btn-hover: ${SURFACE_TOKENS.themes.dark.btnHover};
          --firby-surface-blur: 24px;
          --firby-surface-saturate: 145%;
          --firby-surface-brightness: 108%;
        }

        /* Degradación accesible a transparencia reducida */
        @media (prefers-reduced-transparency: reduce) {
          :root {
            --firby-surface-bg: #ffffff !important;
            --firby-surface-blur: 0px !important;
          }
          html.dark, html[data-theme="dark"], body.dark, [data-theme="dark"] {
            --firby-surface-bg: #161b22 !important;
            --firby-surface-blur: 0px !important;
          }
        }

        /* Contenedor Flotante Central */
        .firby-agent-surface {
          position: fixed;
          top: 24px;
          left: 50%;
          transform: translateX(-50%) translateY(8px) scale(0.97);
          opacity: 0;
          pointer-events: none;
          z-index: ${SURFACE_TOKENS.glass.elevation};
          user-select: none;
          -webkit-user-select: none;
          contain: layout style;
          transition: transform 0.26s ${SURFACE_TOKENS.glass.springEase},
                      opacity 0.22s ${SURFACE_TOKENS.glass.springEase};
          will-change: transform, opacity;
        }

        .firby-agent-surface.is-visible {
          transform: translateX(-50%) translateY(0) scale(1);
          opacity: 1;
          pointer-events: auto;
        }

        .firby-agent-surface.is-exiting {
          transform: translateX(-50%) translateY(-6px) scale(0.96);
          opacity: 0;
          pointer-events: none;
          transition: transform 0.22s ${SURFACE_TOKENS.glass.springEase},
                      opacity 0.20s ${SURFACE_TOKENS.glass.springEase};
        }

        /* Cápsula de Material Liquid Glass */
        .firby-agent-surface__capsule {
          display: inline-flex;
          align-items: center;
          gap: 9px;
          height: 38px;
          padding: 0 12px 0 10px;
          border-radius: ${SURFACE_TOKENS.glass.radiusPill};
          background: linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0) 100%), var(--firby-surface-bg);
          border: 1px solid var(--firby-surface-border);
          box-shadow: inset 0 1px 0.5px 0 var(--firby-surface-rim), var(--firby-surface-shadow);
          backdrop-filter: blur(var(--firby-surface-blur)) saturate(var(--firby-surface-saturate)) brightness(var(--firby-surface-brightness));
          -webkit-backdrop-filter: blur(var(--firby-surface-blur)) saturate(var(--firby-surface-saturate)) brightness(var(--firby-surface-brightness));
          color: var(--firby-surface-text);
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, -apple-system-font, "Helvetica Neue", Arial, sans-serif;
          font-size: 13px;
          font-weight: 500;
          letter-spacing: -0.012em;
          line-height: 1;
          white-space: nowrap;
          transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        }

        .firby-agent-surface:hover .firby-agent-surface__capsule {
          background: linear-gradient(180deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0) 100%), var(--firby-surface-bg-hover);
        }

        /* Indicador de Presencia y Vida (Cero Spinners) */
        .firby-agent-surface__presence {
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .firby-presence-dot {
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: var(--firby-surface-brand);
          box-shadow: 0 0 0 0 var(--firby-surface-ring);
          display: inline-block;
          flex-shrink: 0;
          transition: background-color 0.3s ease, transform 0.3s ease;
        }

        .firby-agent-surface.is-navigating .firby-presence-dot,
        .firby-agent-surface.is-thinking .firby-presence-dot,
        .firby-agent-surface.is-acting .firby-presence-dot {
          animation: firbyPresenceBreathe 2.4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        }

        @keyframes firbyPresenceBreathe {
          0%, 100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 var(--firby-surface-ring);
          }
          50% {
            transform: scale(1.18);
            box-shadow: 0 0 0 4.5px var(--firby-surface-ring);
          }
        }

        .firby-presence-name {
          font-size: 12.5px;
          font-weight: 600;
          color: var(--firby-surface-text);
          letter-spacing: -0.02em;
          opacity: 0.92;
        }

        /* Divisor Vertical Sutil */
        .firby-agent-surface__divider {
          width: 1px;
          height: 14px;
          background: var(--firby-surface-divider);
          margin: 0 1px;
        }

        /* Texto de Contexto Humano */
        .firby-agent-surface__text {
          color: var(--firby-surface-muted);
          font-size: 12.5px;
          font-weight: 450;
          letter-spacing: -0.01em;
          max-width: 280px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          transition: color 0.2s ease;
        }

        /* Estado SUCCESS */
        .firby-agent-surface.is-success .firby-presence-dot {
          background: #10b981;
          box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
          animation: none;
          transform: scale(1.05);
        }
        .firby-agent-surface.is-success .firby-agent-surface__text {
          color: var(--firby-surface-text);
          font-weight: 500;
        }

        /* Estado ERROR / Fallback Calmado (Sin dramatismo) */
        .firby-agent-surface.is-error .firby-presence-dot {
          background: #94a3b8;
          box-shadow: none;
          animation: none;
        }

        /* Botón de Cancelación Sutil (×) */
        .firby-agent-surface__cancel {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 18px;
          height: 18px;
          padding: 0;
          margin-left: 2px;
          background: transparent;
          border: none;
          border-radius: 50%;
          color: var(--firby-surface-muted);
          cursor: pointer;
          opacity: 0.65;
          transition: opacity 0.15s ease, background-color 0.15s ease, color 0.15s ease;
        }

        .firby-agent-surface__cancel:hover {
          opacity: 1;
          color: var(--firby-surface-text);
          background-color: var(--firby-surface-btn-hover);
        }

        /* Responsive Móvil */
        @media (max-width: 768px) {
          .firby-agent-surface {
            top: 14px;
            max-width: calc(100vw - 32px);
          }
          .firby-agent-surface__text {
            max-width: 190px;
          }
        }

        /* Modo Accesible: Reducción de Movimiento */
        @media (prefers-reduced-motion: reduce) {
          .firby-agent-surface {
            transition: opacity 0.05s ease !important;
            transform: translateX(-50%) translateY(0) scale(1) !important;
          }
          .firby-presence-dot {
            animation: none !important;
          }
        }
      `;
      document.head.appendChild(style);
    }

    _mountDOM() {
      if (document.getElementById('firby-agent-surface')) {
        this.container = document.getElementById('firby-agent-surface');
        this.capsuleEl = this.container.querySelector('.firby-agent-surface__capsule');
        this.textEl = this.container.querySelector('.firby-agent-surface__text');
        this.dotEl = this.container.querySelector('.firby-presence-dot');
        this.cancelBtn = this.container.querySelector('.firby-agent-surface__cancel');
        return;
      }

      const container = document.createElement('div');
      container.id = 'firby-agent-surface';
      container.className = 'firby-agent-surface';
      container.setAttribute('role', 'status');
      container.setAttribute('aria-live', 'polite');
      container.setAttribute('aria-atomic', 'true');
      container.setAttribute('data-lenis-prevent', 'true');

      container.innerHTML = `
        <div class="firby-agent-surface__capsule">
          <div class="firby-agent-surface__presence">
            <span class="firby-presence-dot" aria-hidden="true"></span>
            <span class="firby-presence-name">Firby</span>
          </div>
          <div class="firby-agent-surface__divider" aria-hidden="true"></div>
          <span class="firby-agent-surface__text"></span>
          <button type="button" class="firby-agent-surface__cancel" aria-label="Detener acción" title="Detener">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      `;

      document.body.appendChild(container);

      this.container = container;
      this.capsuleEl = container.querySelector('.firby-agent-surface__capsule');
      this.textEl = container.querySelector('.firby-agent-surface__text');
      this.dotEl = container.querySelector('.firby-presence-dot');
      this.cancelBtn = container.querySelector('.firby-agent-surface__cancel');

      // Botón cancelar detiene el movimiento de forma limpia
      if (this.cancelBtn) {
        this.cancelBtn.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          this.cancel('user_button');
        });
      }
    }

    _bindEvents() {
      // Sincronización transparente con eventos del motor de navegación inercial
      window.addEventListener('firby:agent.navigation.requested', (e) => {
        const detail = e.detail || {};
        const msg = detail.label || humanizeSection(detail.target);
        this.show({
          state: SURFACE_TOKENS.states.NAVIGATING,
          message: msg,
          cancellable: true
        });
      });

      window.addEventListener('firby:agent.section.reached', (e) => {
        const detail = e.detail || {};
        const successTitle = humanizeSuccess(detail.target);
        this.success(successTitle, 750);
      });

      window.addEventListener('firby:agent.navigation.cancelled', () => {
        this.hide();
      });

      window.addEventListener('firby:agent.navigation.failed', () => {
        this.show({
          state: SURFACE_TOKENS.states.ERROR,
          message: 'Sección no disponible',
          autoHideMs: 1400
        });
      });
    }

    /**
     * Muestra la superficie flotante con entrada spring controlada.
     */
    show(options = {}) {
      if (this.hideTimer) {
        clearTimeout(this.hideTimer);
        this.hideTimer = null;
      }

      // Si la ventana de chat está abierta, el estado se integra dentro del propio chat
      const chatWin = document.getElementById('firby-chat-window');
      if (chatWin && chatWin.classList.contains('open')) {
        return;
      }

      this._mountDOM();
      const state = options.state || SURFACE_TOKENS.states.ACTING;
      const message = options.message || 'Operando';

      this.state = state;
      if (this.textEl) this.textEl.textContent = message;

      // Limpiar clases de estado previas
      this.container.classList.remove('is-navigating', 'is-thinking', 'is-acting', 'is-success', 'is-error', 'is-exiting');
      this.container.classList.add(`is-${state}`);

      if (options.cancellable && this.cancelBtn) {
        this.cancelBtn.style.display = 'inline-flex';
      } else if (this.cancelBtn) {
        this.cancelBtn.style.display = 'none';
      }

      // Forzar reflow para asegurar animación de entrada
      void this.container.offsetWidth;
      this.container.classList.add('is-visible');

      if (options.autoHideMs) {
        this.hideTimer = setTimeout(() => this.hide(), options.autoHideMs);
      }
    }

    /**
     * Presenta navegación con texto humano sobrio.
     */
    presentNavigation(target, label = null) {
      const msg = label || humanizeSection(target);
      this.show({
        state: SURFACE_TOKENS.states.NAVIGATING,
        message: msg,
        cancellable: true
      });
    }

    /**
     * Actualiza el texto en vivo.
     */
    updateText(message) {
      if (this.textEl) this.textEl.textContent = message;
    }

    /**
     * Micro-confirmación visual de éxito y disolución suave.
     */
    success(message = null, hideDelayMs = 700) {
      if (this.hideTimer) {
        clearTimeout(this.hideTimer);
        this.hideTimer = null;
      }

      this.state = SURFACE_TOKENS.states.SUCCESS;
      this.container.classList.remove('is-navigating', 'is-thinking', 'is-acting', 'is-error');
      this.container.classList.add('is-success');

      if (message && this.textEl) {
        this.textEl.textContent = message;
      }

      if (this.cancelBtn) {
        this.cancelBtn.style.display = 'none';
      }

      this.hideTimer = setTimeout(() => {
        this.hide();
      }, hideDelayMs);
    }

    /**
     * Salida suave con spring desacelerado.
     */
    hide() {
      if (this.hideTimer) {
        clearTimeout(this.hideTimer);
        this.hideTimer = null;
      }

      if (!this.container || !this.container.classList.contains('is-visible')) {
        return;
      }

      this.container.classList.remove('is-visible');
      this.container.classList.add('is-exiting');

      const exitDuration = this.isReducedMotion ? 50 : SURFACE_TOKENS.glass.exitMs;
      setTimeout(() => {
        if (this.container.classList.contains('is-exiting')) {
          this.container.classList.remove('is-exiting', 'is-success', 'is-navigating', 'is-thinking', 'is-acting', 'is-error');
          this.state = SURFACE_TOKENS.states.IDLE;
        }
      }, exitDuration + 30);
    }

    /**
     * Cancela la acción actual sin pelear con el usuario.
     */
    cancel(reason = 'manual') {
      if (window.FirbyMotionEngine && typeof window.FirbyMotionEngine.cancelNavigation === 'function') {
        window.FirbyMotionEngine.cancelNavigation(reason);
      } else {
        this.hide();
      }
    }

    getState() {
      return this.state;
    }
  }

  // Instancia global en window
  const surfaceEngine = new AgentSurfaceEngine();
  window.FirbyAgentSurface = surfaceEngine;

})(window, document);
