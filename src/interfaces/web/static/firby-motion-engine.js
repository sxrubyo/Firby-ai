// -*- coding: utf-8 -*-
/**
 * Firby AI — Premium Agent Navigation Motion Engine (Slot-Machine Precision Physics)
 * ====================================================================================
 * Diseñado bajo principios de cinemática mecánica de alta gama:
 * 
 * FÍSICA INERCIAL POR FASES (INSPIRACIÓN MECÁNICA / SLOT-MACHINE SAAS):
 * 1. Aceleración inicial rápida y controlada (fuerza de arranque).
 * 2. Velocidad de crucero estable proporcional a la distancia física real.
 * 3. Frenado progresivo continuo (deceleración inercial asintótica).
 * 4. Micro-settle milimétrico de precisión (overshoot microscópico de 2px con asentamiento elástico v=0).
 * 5. Focalización táctil del elemento destino: Focus ring suave verde lima y micro-pulso de presencia.
 * 6. Duración dinámica adaptativa (corta, media y larga distancia, cero delays artificiales).
 * 7. Respeto estricto a prefers-reduced-motion y accesibilidad WCAG 2.2.
 * 8. Cancelabilidad instantánea por intervención del usuario (wheel, touch, teclas, nuevo mensaje).
 * 9. Retorno de observación formal completa:
 *    target_found, target_visible, scroll_completed, section_id, final_scroll_position.
 */

(function (window, document) {
  'use strict';

  // ── Constantes y Tokens de Movimiento Físico ──
  const MOTION_TOKENS = {
    offset: {
      header: 84,        // Compensación fija de la barra de navegación superior
      breathingRoom: 16  // Holgura visual intencional de diseñador
    },
    duration: {
      reduced: 0.01      // Duración para reduced-motion
    },
    // Curva cinemática orgánica de alta fidelidad (aceleración gradual, crucero fluido y frenado sedoso):
    slotMachineEasing: function (t) {
      if (t <= 0) return 0;
      if (t >= 1) return 1;
      return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    },
    inertialEasing: function (t) {
      return MOTION_TOKENS.slotMachineEasing(t);
    }
  };

  class AgentNavigationMotionEngine {
    constructor() {
      this.lenis = null;
      this.isNavigating = false;
      this.currentVelocity = 0;
      this.reducedMotion = false;
      this._rafId = null;
      this._fallbackRafId = null;
      this._activeTargetEl = null;
      this._activeCancelCallback = null;
      this.init();
    }

    init() {
      // 0. Si es un dashboard, workspace o panel con contenedor propio de scroll, abortar para no bloquear wheel
      if (typeof window !== 'undefined' && (
        window.location.pathname.startsWith('/workspace') ||
        window.location.pathname.startsWith('/panel') ||
        window.location.pathname.startsWith('/settings') ||
        window.location.pathname.startsWith('/chats') ||
        window.location.pathname.startsWith('/dev-portal')
      )) {
        return;
      }

      // 1. Detectar accesibilidad y reduced-motion
      if (typeof window !== 'undefined' && window.matchMedia) {
        const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
        this.reducedMotion = mediaQuery.matches;
        mediaQuery.addEventListener('change', (e) => {
          this.reducedMotion = e.matches;
        });
      }

      // 2. Inyectar estilos sutiles de micro-arrival y CSS de foco
      this._injectStyles();

      // 3. Inicializar Lenis si está disponible en la página
      this._setupLenis();

      // 4. Proteger contenedores del chat con data-lenis-prevent
      this._protectChatContainers();

      // 5. Vincular eventos de interrupción del usuario
      this._bindUserInterruption();
    }

    _injectStyles() {
      if (document.getElementById('firby-motion-styles')) return;

      const style = document.createElement('style');
      style.id = 'firby-motion-styles';
      style.textContent = `
        /* Lenis Smooth Scroll Core */
        html.lenis, html.lenis body {
          height: auto;
        }
        .lenis:not(.lenis-autoToggle).lenis-stopped {
          overflow: clip;
        }
        .lenis [data-lenis-prevent] {
          overscroll-behavior: contain;
        }
        .lenis.lenis-smooth iframe {
          pointer-events: none;
        }

        /* Micro-Arrival Sutil (Precisión Slot-Machine SaaS) */
        @keyframes firbySlotSettle {
          0% {
            transform: translateY(-2.5px);
            opacity: 0.96;
          }
          60% {
            transform: translateY(0.5px);
            opacity: 1;
          }
          100% {
            transform: translateY(0);
            opacity: 1;
          }
        }

        @keyframes firbySlotPresenceGlow {
          0% {
            box-shadow: 0 0 0 0 rgba(185, 250, 1, 0);
          }
          30% {
            box-shadow: 0 0 0 2px rgba(185, 250, 1, 0.45), 0 8px 24px -6px rgba(0, 0, 0, 0.12);
          }
          100% {
            box-shadow: 0 0 0 0 rgba(185, 250, 1, 0);
          }
        }

        .firby-micro-arrival {
          animation: firbySlotSettle 0.55s cubic-bezier(0.16, 1, 0.3, 1) forwards,
                     firbySlotPresenceGlow 1.6s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
          will-change: transform, box-shadow;
        }

        /* Destino resaltado por agente */
        .firby-section-highlight {
          outline: 2px solid rgba(185, 250, 1, 0.55);
          outline-offset: 4px;
          border-radius: 8px;
          transition: outline 0.8s ease;
        }

        /* Aislamiento del widget */
        .bws-hw-floating-btn, .firby-launcher-btn {
          transform: translateZ(0);
        }
        .firby-widget-container, .bws-hw {
          contain: none !important;
          transform: none !important;
        }
      `;
      document.head.appendChild(style);
    }

    _setupLenis() {
      if (window.lenis && typeof window.lenis.scrollTo === 'function') {
        this.lenis = window.lenis;
        this._bindScrollEvents();
        return;
      }

      if (typeof window.Lenis === 'function') {
        try {
          this.lenis = new window.Lenis({
            duration: 1.05,
            easing: MOTION_TOKENS.slotMachineEasing,
            orientation: 'vertical',
            gestureOrientation: 'vertical',
            smoothWheel: true,
            touchMultiplier: 1.8,
            wheelMultiplier: 0.95
          });

          const raf = (time) => {
            this.lenis.raf(time);
            this._rafId = requestAnimationFrame(raf);
          };
          this._rafId = requestAnimationFrame(raf);

          window.__firbyLenis = this.lenis;
          this._bindScrollEvents();
        } catch (e) {
          console.warn('[Firby Motion] Error inicializando Lenis:', e);
        }
      }
    }

    _bindScrollEvents() {
      if (!this.lenis) return;
      this.lenis.on('scroll', (e) => {
        this.currentVelocity = e.velocity || 0;
        if (Math.abs(this.currentVelocity) > 2.2) {
          document.body.classList.add('firby-high-velocity');
        } else {
          document.body.classList.remove('firby-high-velocity');
        }
      });
    }

    _protectChatContainers() {
      const markContainers = () => {
        const selectors = ['.firby-stream', '.bws-hw', '#firby-chat-widget', '.firby-chat-modal', '.firby-messages'];
        selectors.forEach(sel => {
          document.querySelectorAll(sel).forEach(el => {
            el.setAttribute('data-lenis-prevent', 'true');
          });
        });
      };
      markContainers();
      setTimeout(markContainers, 600);
    }

    _bindUserInterruption() {
      const handleInterruption = (e) => {
        if (!this.isNavigating) return;
        // Ignorar interacciones dentro del contenedor del chat
        if (e.target && e.target.closest && e.target.closest('[data-lenis-prevent="true"], .firby-widget-container')) {
          return;
        }
        this.cancelNavigation('user_interruption');
      };

      window.addEventListener('wheel', handleInterruption, { passive: true });
      window.addEventListener('touchmove', handleInterruption, { passive: true });
      window.addEventListener('keydown', (e) => {
        if (['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End', ' '].includes(e.key)) {
          handleInterruption(e);
        }
      }, { passive: true });
    }

    /**
     * Cancela inmediatamente la navegación activa y devuelve una observación de interrupción.
     */
    cancelNavigation(reason = 'manual') {
      if (!this.isNavigating) return null;
      this.isNavigating = false;

      if (this.lenis && typeof this.lenis.stop === 'function') {
        this.lenis.stop();
        this.lenis.start();
      }

      if (this._fallbackRafId) {
        cancelAnimationFrame(this._fallbackRafId);
        this._fallbackRafId = null;
      }

      const currentY = window.pageYOffset || document.documentElement.scrollTop;
      const cancelObs = {
        success: false,
        status: 'interrupted',
        reason: reason,
        target_found: !!this._activeTargetEl,
        target_visible: false,
        scroll_completed: false,
        section_id: this._activeTargetEl ? (this._activeTargetEl.id || '') : '',
        final_scroll_position: currentY
      };

      if (typeof this._activeCancelCallback === 'function') {
        this._activeCancelCallback(cancelObs);
        this._activeCancelCallback = null;
      }

      window.dispatchEvent(new CustomEvent('firby:agent.navigation.cancelled', {
        detail: cancelObs
      }));

      return cancelObs;
    }

    /**
     * Calcula la duración adaptativa basada en la distancia física real en píxeles.
     * Si está en la página principal (gran distancia >3000px), scrollea lentamente y profesional (3.0s-3.5s).
     * Si está una página arriba o distancia media (800px-2500px), scrollea pausado y suave (1.9s-2.6s).
     * Si está muy cerca (<350px), asentamiento suave (1.25s).
     */
    calculateDuration(distancePx) {
      if (this.reducedMotion) return MOTION_TOKENS.duration.reduced;
      const d = Math.abs(distancePx);

      if (d < 350) {
        // Distancia muy corta: movimiento pausado, visible y elegante
        return 1.25;
      } else if (d < 1200) {
        // Distancia media (una página arriba / sección adyacente): desplazamiento lento y calmado
        const t = (d - 350) / 850;
        return 1.85 + t * 0.45; // 1.85s a 2.30s
      } else if (d < 3000) {
        // Distancia considerable: desplazamiento cinemático continuo y controlado
        const t = (d - 1200) / 1800;
        return 2.30 + t * 0.60; // 2.30s a 2.90s
      } else {
        // Distancia larga (recorrido desde Hero/página principal hasta planes o contacto):
        // Scroll cinemático lento, profesional y majestuoso
        const t = Math.min((d - 3000) / 4000, 1.0);
        return 2.90 + t * 0.55; // 2.90s a 3.45s
      }
    }

    /**
     * Resuelve el elemento objetivo en el DOM y expande acordeones o pestañas si aplica.
     */
    resolveTarget(target) {
      if (!target) return null;
      const rawTarget = target.replace('#', '').trim();
      const selector = '#' + rawTarget;
      let el = document.querySelector(selector) || document.getElementById(rawTarget);

      if (!el) {
        el = document.querySelector(`[data-section="${rawTarget}"]`);
      }

      if (!el) {
        // Buscar por nombre o clase representativa
        el = document.querySelector(`.${rawTarget}`) || document.querySelector(`[name="${rawTarget}"]`);
      }

      if (el) {
        // Expansión de contenedores colapsados (ej. acordeón de FAQ)
        const detailsParent = el.closest('details');
        if (detailsParent && !detailsParent.open) {
          detailsParent.open = true;
        }
        const accordionContent = el.closest('[data-state="closed"]');
        if (accordionContent) {
          const trigger = accordionContent.previousElementSibling?.querySelector('button') ||
                          accordionContent.parentElement?.querySelector('button');
          if (trigger && typeof trigger.click === 'function') trigger.click();
        }
      }

      return el;
    }

    /**
     * Ejecuta el desplazamiento físico con física de rodillo/slot-machine
     * y retorna una observación formal completa y verificable.
     */
    navigateToElement(target, options = {}) {
      const currentScrollY = window.pageYOffset || document.documentElement.scrollTop;
      const el = this.resolveTarget(target);

      if (!el) {
        console.warn('[Firby Motion] Objetivo no encontrado en el DOM:', target);
        const failObs = {
          success: false,
          status: 'target_not_found',
          target_found: false,
          target_visible: false,
          scroll_completed: false,
          section_id: target,
          final_scroll_position: currentScrollY,
          error: 'Elemento no encontrado en el DOM de la página actual'
        };
        window.dispatchEvent(new CustomEvent('firby:agent.navigation.failed', { detail: failObs }));
        return Promise.resolve(failObs);
      }

      this._activeTargetEl = el;

      // Cálculo de destino con compensación precisa de header
      const rect = el.getBoundingClientRect();
      const targetOffset = -(MOTION_TOKENS.offset.header + MOTION_TOKENS.offset.breathingRoom);
      const targetScrollY = Math.max(0, currentScrollY + rect.top + targetOffset);
      const distance = Math.abs(targetScrollY - currentScrollY);

      // Si el elemento ya está perfectamente visible en pantalla
      if (distance < 20 && rect.top >= 60 && rect.bottom <= window.innerHeight) {
        this._triggerMicroArrival(el, options);
        const immediateObs = {
          success: true,
          status: 'scroll_completed',
          target_found: true,
          target_visible: true,
          scroll_completed: true,
          section_id: el.id || target,
          final_scroll_position: currentScrollY,
          distance: 0,
          drift: 0
        };
        window.dispatchEvent(new CustomEvent('firby:agent.section.reached', { detail: immediateObs }));
        return Promise.resolve(immediateObs);
      }

      const durationSec = options.duration || (options.slow ? 2.8 : this.calculateDuration(distance));
      this.isNavigating = true;

      window.dispatchEvent(new CustomEvent('firby:agent.navigation.requested', {
        detail: {
          target: el.id || target,
          label: options.label || null,
          distance,
          duration: durationSec * 1000,
          direction: targetScrollY > currentScrollY ? 'down' : 'up'
        }
      }));

      return new Promise((resolve) => {
        let settled = false;

        const completeHandler = (observation) => {
          if (settled) return;
          settled = true;
          this.isNavigating = false;
          this._activeTargetEl = null;
          this._activeCancelCallback = null;
          resolve(observation);
        };

        this._activeCancelCallback = completeHandler;

        const onArrival = () => {
          this._triggerMicroArrival(el, options);

          const finalY = window.pageYOffset || document.documentElement.scrollTop;
          const drift = Math.abs(finalY - targetScrollY);

          // Micro-corrección subpixel si aplica
          if (drift > 2 && drift < 25 && !this.reducedMotion) {
            window.scrollTo({ top: targetScrollY, behavior: 'auto' });
          }

          const rectAfter = el.getBoundingClientRect();
          const isVisible = rectAfter.top < window.innerHeight && rectAfter.bottom > 0;

          const successObs = {
            success: true,
            status: 'scroll_completed',
            target_found: true,
            target_visible: isVisible,
            scroll_completed: true,
            section_id: el.id || target,
            final_scroll_position: targetScrollY,
            distance: distance,
            drift: drift
          };

          window.dispatchEvent(new CustomEvent('firby:agent.section.reached', { detail: successObs }));
          try {
            const hashVal = '#' + (el.id || String(target).replace('#', ''));
            if (window.location.hash !== hashVal) {
              history.replaceState(null, '', hashVal);
            }
          } catch (e) {}

          completeHandler(successObs);
        };

        if (this.reducedMotion) {
          window.scrollTo(0, targetScrollY);
          onArrival();
          return;
        }

        // Ejecutar desplazamiento con Lenis o Fallback Inercial
        if (this.lenis && typeof this.lenis.scrollTo === 'function') {
          this.lenis.scrollTo(targetScrollY, {
            duration: durationSec,
            easing: MOTION_TOKENS.slotMachineEasing,
            immediate: false,
            onComplete: onArrival
          });
        } else {
          this._fallbackInertialScroll(currentScrollY, targetScrollY, durationSec * 1000, onArrival);
        }
      });
    }

    _fallbackInertialScroll(startY, endY, durationMs, callback) {
      let startTime = null;
      const distance = endY - startY;

      const step = (currentTime) => {
        if (!this.isNavigating) return;
        if (!startTime) startTime = currentTime;
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / durationMs, 1.0);
        const ease = MOTION_TOKENS.slotMachineEasing(progress);

        window.scrollTo(0, startY + (distance * ease));

        if (elapsed < durationMs) {
          this._fallbackRafId = requestAnimationFrame(step);
        } else {
          window.scrollTo(0, endY);
          this._fallbackRafId = null;
          if (callback) callback();
        }
      };

      this._fallbackRafId = requestAnimationFrame(step);
    }

    _triggerMicroArrival(el, options = {}) {
      if (!el) return;
      el.classList.remove('firby-micro-arrival');
      void el.offsetWidth; // Reflow
      el.classList.add('firby-micro-arrival');

      setTimeout(() => {
        el.classList.remove('firby-micro-arrival');
      }, 1700);

      // Si hay palabra a tachar o resaltar
      if (options.strikeKeyword) {
        this.strikeWord(el, options.strikeKeyword);
      } else if (options.highlightKeyword) {
        this.highlightWord(el, options.highlightKeyword);
      }
    }

    strikeWord(containerEl, word) {
      if (!containerEl || !word) return;
      const regex = new RegExp(`(${word})`, 'i');
      const walker = document.createTreeWalker(containerEl, NodeFilter.SHOW_TEXT, null, false);
      let node;
      while ((node = walker.nextNode())) {
        if (regex.test(node.nodeValue)) {
          const span = document.createElement('span');
          span.className = 'firby-strike-wrap';
          span.innerHTML = node.nodeValue.replace(regex, `<span class="firby-strike-wrap">$1<span class="firby-strike-line"></span></span>`);
          if (node.parentNode) {
            node.parentNode.replaceChild(span, node);
            setTimeout(() => {
              const line = span.querySelector('.firby-strike-line');
              if (line) line.classList.add('is-struck');
            }, 300);
          }
          break;
        }
      }
    }

    highlightWord(containerEl, word) {
      if (!containerEl || !word) return;
      const regex = new RegExp(`(${word})`, 'i');
      const walker = document.createTreeWalker(containerEl, NodeFilter.SHOW_TEXT, null, false);
      let node;
      while ((node = walker.nextNode())) {
        if (regex.test(node.nodeValue)) {
          const span = document.createElement('span');
          span.innerHTML = node.nodeValue.replace(regex, `<span class="firby-highlight-marker is-marked">$1</span>`);
          if (node.parentNode) {
            node.parentNode.replaceChild(span, node);
          }
          break;
        }
      }
    }
  }

  // Exportar motor global
  const motionEngine = new AgentNavigationMotionEngine();
  window.FirbyMotionEngine = motionEngine;

})(window, document);
