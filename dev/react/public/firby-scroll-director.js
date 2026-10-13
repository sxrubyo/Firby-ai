// -*- coding: utf-8 -*-
/**
 * Firby AI — Cinematic Slow Scroll & Visual Framing Director
 * ==========================================================
 * Motor de desplazamiento visual cinemático y acompañamiento en tiempo real.
 * Permite que Firby guíe físicamente al usuario en la página:
 * 
 * CARACTERÍSTICAS PRINCIPALES:
 * 1. Scroll Lento y Orgánico: Desplazamiento visible por rAF con curva armónica
 *    (duración 1.2s - 1.8s) que simula a un copiloto humano deslizando la pantalla.
 * 2. Cancelación Inteligente por Usuario: Si el usuario toca el mouse o la pantalla,
 *    el scroll se detiene suavemente sin bloquear su interacción.
 * 3. Enmarcado Visual de Foco: Iluminación perimetral respirable sobre el elemento destino.
 * 4. Animación de Tachón y Marcado: Línea animada SVG sobre palabras clave a enmarcar o descartar.
 * 5. Sincronización con la Superficie Líquida: Comunica a FirbyAgentSurface cada fase del viaje.
 */

(function (window, document) {
  'use strict';

  if (window.FirbyScrollDirector) return;

  const SCROLL_CONFIG = {
    minDuration: 1200,   // Duración mínima en ms para recorridos cortos
    maxDuration: 1800,   // Duración máxima en ms para recorridos de toda la página
    headerOffset: 84,    // Margen superior para no tapar contenido bajo navbars
    haloColorDark: 'rgba(185, 250, 1, 0.45)',
    haloColorLight: 'rgba(0, 130, 90, 0.40)',
    haloBorderDark: '#b9fa01',
    haloBorderLight: '#00825a'
  };

  // Curva armónica cúbica de alta suavidad: aceleración calmada y desaceleración elegante
  function easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  class ScrollDirector {
    constructor() {
      this.isScrolling = false;
      this.currentAnimation = null;
      this.activeHaloElement = null;
      this._injectStyles();
      this._bindUserInterruption();
    }

    _injectStyles() {
      if (document.getElementById('firby-scroll-director-styles')) return;
      const style = document.createElement('style');
      style.id = 'firby-scroll-director-styles';
      style.textContent = `
        /* Enmarcado Visual de Foco (Halo Respirable) */
        .firby-focus-target {
          position: relative !important;
          transition: box-shadow 0.4s ease, outline 0.4s ease !important;
          outline: 2px solid transparent !important;
        }

        .firby-focus-target.firby-halo-active {
          outline: 2px solid var(--firby-halo-border, #b9fa01) !important;
          outline-offset: 4px !important;
          box-shadow: 0 0 28px -2px var(--firby-halo-color, rgba(185, 250, 1, 0.35)) !important;
          animation: firbyHaloBreathe 2.4s ease-in-out infinite !important;
        }

        @keyframes firbyHaloBreathe {
          0%, 100% {
            box-shadow: 0 0 20px -2px var(--firby-halo-color, rgba(185, 250, 1, 0.25));
          }
          50% {
            box-shadow: 0 0 36px 4px var(--firby-halo-color, rgba(185, 250, 1, 0.45));
          }
        }

        /* Efecto Tachón Animado sobre palabras */
        .firby-strike-wrap {
          position: relative;
          display: inline-block;
          white-space: nowrap;
        }

        .firby-strike-line {
          position: absolute;
          left: -4%;
          top: 50%;
          width: 108%;
          height: 2.5px;
          background: #ef4444;
          transform: translateY(-50%) scaleX(0);
          transform-origin: left center;
          transition: transform 0.45s cubic-bezier(0.16, 1, 0.3, 1);
          border-radius: 2px;
          pointer-events: none;
        }

        .firby-strike-line.is-struck {
          transform: translateY(-50%) scaleX(1);
        }

        /* Efecto Resaltador Sutil */
        .firby-highlight-marker {
          background: linear-gradient(120deg, rgba(185, 250, 1, 0.28) 0%, rgba(185, 250, 1, 0) 100%);
          background-size: 0% 100%;
          background-repeat: no-repeat;
          border-radius: 3px;
          padding: 1px 4px;
          transition: background-size 0.5s ease-out;
        }

        .firby-highlight-marker.is-marked {
          background-size: 100% 100%;
        }
      `;
      document.head.appendChild(style);
    }

    _bindUserInterruption() {
      const stopOnUserAction = () => {
        if (this.isScrolling) {
          this.cancel();
          window.dispatchEvent(new CustomEvent('firby:agent.navigation.cancelled', {
            detail: { reason: 'user_interruption' }
          }));
        }
      };

      window.addEventListener('wheel', stopOnUserAction, { passive: true });
      window.addEventListener('touchstart', stopOnUserAction, { passive: true });
      window.addEventListener('keydown', (e) => {
        if (['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Space'].includes(e.code)) {
          stopOnUserAction();
        }
      }, { passive: true });
    }

    /**
     * Resuelve el elemento objetivo a partir de selector, hash o elemento directo.
     */
    resolveElement(target) {
      if (!target) return null;
      if (typeof target === 'string') {
        const clean = target.trim();
        try {
          if (clean.startsWith('#') || clean.startsWith('.') || clean.startsWith('[')) {
            const found = document.querySelector(clean);
            if (found) return found;
          }
          const byId = document.getElementById(clean.replace(/^#/, ''));
          if (byId) return byId;
          const bySelector = document.querySelector(`[data-section="${clean}"], [data-firby-index="${clean}"]`);
          if (bySelector) return bySelector;
        } catch (e) {
          // Selector no válido
        }
      } else if (target instanceof HTMLElement) {
        return target;
      }
      return null;
    }

    /**
     * Ejecuta el desplazamiento cinemático lento guiando la vista del usuario.
     */
    scrollTo(target, options = {}) {
      const element = this.resolveElement(target);
      if (!element) {
        console.warn('[FirbyScrollDirector] Elemento no encontrado:', target);
        return Promise.reject(new Error('Element not found'));
      }

      // Cancelar cualquier scroll previo
      this.cancel();

      return new Promise((resolve) => {
        const startY = window.pageYOffset || document.documentElement.scrollTop;
        const rect = element.getBoundingClientRect();
        const offset = options.headerOffset !== undefined ? options.headerOffset : SCROLL_CONFIG.headerOffset;
        const targetY = Math.max(0, startY + rect.top - offset);
        const distance = Math.abs(targetY - startY);

        // Si ya estamos prácticamente en la posición, solo enfocar
        if (distance < 15) {
          this._applyVisualFocus(element, options);
          resolve();
          return;
        }

        // Calcular duración adaptativa proporcional a la distancia (1.2s a 1.8s)
        const duration = options.duration || Math.min(
          SCROLL_CONFIG.maxDuration,
          Math.max(SCROLL_CONFIG.minDuration, 1000 + (distance / window.innerHeight) * 400)
        );

        this.isScrolling = true;
        const startTime = performance.now();

        // Notificar a la superficie líquida que el scroll ha comenzado
        window.dispatchEvent(new CustomEvent('firby:agent.navigation.requested', {
          detail: {
            target: target,
            label: options.label || null,
            duration: duration
          }
        }));

        const animateScroll = (currentTime) => {
          if (!this.isScrolling) return;

          const elapsed = currentTime - startTime;
          const progress = Math.min(elapsed / duration, 1);
          const easeProgress = easeInOutCubic(progress);

          const currentY = startY + (targetY - startY) * easeProgress;
          window.scrollTo(0, currentY);

          if (progress < 1) {
            this.currentAnimation = requestAnimationFrame(animateScroll);
          } else {
            // Scroll finalizado con éxito
            window.scrollTo(0, targetY);
            this.isScrolling = false;
            this.currentAnimation = null;

            // Aplicar enmarcado visual y notificar
            this._applyVisualFocus(element, options);

            window.dispatchEvent(new CustomEvent('firby:agent.section.reached', {
              detail: { target: target, element: element }
            }));

            resolve();
          }
        };

        this.currentAnimation = requestAnimationFrame(animateScroll);
      });
    }

    /**
     * Aplica el halo respirable y opcionalmente el tachón animado.
     */
    _applyVisualFocus(element, options = {}) {
      if (!element) return;

      // Limpiar halo anterior si existe
      if (this.activeHaloElement && this.activeHaloElement !== element) {
        this.activeHaloElement.classList.remove('firby-halo-active', 'firby-focus-target');
      }

      const isDark = document.documentElement.classList.contains('dark') || 
                     document.body.classList.contains('dark') ||
                     window.matchMedia('(prefers-color-scheme: dark)').matches;

      element.style.setProperty('--firby-halo-color', isDark ? SCROLL_CONFIG.haloColorDark : SCROLL_CONFIG.haloColorLight);
      element.style.setProperty('--firby-halo-border', isDark ? SCROLL_CONFIG.haloBorderDark : SCROLL_CONFIG.haloBorderLight);

      element.classList.add('firby-focus-target', 'firby-halo-active');
      this.activeHaloElement = element;

      // Quitar el halo suavemente tras 3 segundos
      setTimeout(() => {
        if (element && element.classList.contains('firby-halo-active')) {
          element.classList.remove('firby-halo-active');
        }
      }, options.haloDuration || 3200);

      // Si se especificó una palabra para tachar/enmarcar
      if (options.strikeKeyword) {
        this.strikeWord(element, options.strikeKeyword);
      } else if (options.highlightKeyword) {
        this.highlightWord(element, options.highlightKeyword);
      }
    }

    /**
     * Dibuja una línea de tachón animada sobre una palabra específica dentro del elemento.
     */
    strikeWord(containerElement, word) {
      if (!containerElement || !word) return;
      const regex = new RegExp(`(${word})`, 'i');

      const walker = document.createTreeWalker(containerElement, NodeFilter.SHOW_TEXT, null, false);
      let node;
      while ((node = walker.nextNode())) {
        if (regex.test(node.nodeValue)) {
          const span = document.createElement('span');
          span.className = 'firby-strike-wrap';
          span.innerHTML = node.nodeValue.replace(regex, `<span class="firby-strike-wrap">$1<span class="firby-strike-line"></span></span>`);
          
          if (node.parentNode) {
            node.parentNode.replaceChild(span, node);
            // Animar el trazo
            setTimeout(() => {
              const line = span.querySelector('.firby-strike-line');
              if (line) line.classList.add('is-struck');
            }, 300);
          }
          break;
        }
      }
    }

    /**
     * Aplica resaltador suave tipo marcador sobre una palabra clave.
     */
    highlightWord(containerElement, word) {
      if (!containerElement || !word) return;
      const regex = new RegExp(`(${word})`, 'i');

      const walker = document.createTreeWalker(containerElement, NodeFilter.SHOW_TEXT, null, false);
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

    /**
     * Cancela cualquier animación de scroll en curso.
     */
    cancel() {
      if (this.currentAnimation) {
        cancelAnimationFrame(this.currentAnimation);
        this.currentAnimation = null;
      }
      this.isScrolling = false;
    }
  }

  // Exportar singleton global
  window.FirbyScrollDirector = new ScrollDirector();

})(window, document);
