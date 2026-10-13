/**
 * MagicBento Runtime - React Bits
 * Applied exclusively to the 3 Pricing Cards (Plan Starter, Plan Pro, Plan Equipos).
 */

(function initMagicBento() {
  function setup() {
    // Clean up any remaining bento-active from CTA card
    document.querySelectorAll('.cta-final-card').forEach(function(el) {
      el.classList.remove('bento-active');
      el.style.transform = '';
    });

    var cards = document.querySelectorAll(
      '.pricing-section .pricing-card, #planes .pricing-card, main .pricing-card'
    );
    if (!cards || cards.length === 0) return;

    var styleId = 'magic-bento-pricing-css';
    if (!document.getElementById(styleId)) {
      var style = document.createElement('style');
      style.id = styleId;
      style.textContent = `
        /* MagicBento Perspective Containers */
        .pricing-section .pricing-grid,
        #planes .pricing-grid,
        main .pricing-grid {
          perspective: 1200px;
        }

        .pricing-card.bento-active::after {
          display: none !important;
        }

        .pricing-card.bento-active {
          position: relative !important;
          overflow: hidden !important;
          transform-style: preserve-3d !important;
          transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s ease, border-color 0.25s ease !important;
          --bento-glow-x: 50%;
          --bento-glow-y: 50%;
          --bento-glow-intensity: 0;
          --bento-radius: 280px;
          --bento-color-light: 45, 52, 65;
          --bento-color-dark: 90, 100, 115;
        }

        /* Perimeter hairline border glow following cursor */
        .pricing-card.bento-active::before {
          content: '' !important;
          position: absolute !important;
          inset: 0 !important;
          padding: 1.5px !important;
          border-radius: inherit !important;
          background: radial-gradient(
            var(--bento-radius) circle at var(--bento-glow-x) var(--bento-glow-y),
            rgba(var(--bento-color-light), calc(var(--bento-glow-intensity) * 0.45)) 0%,
            rgba(var(--bento-color-light), calc(var(--bento-glow-intensity) * 0.15)) 35%,
            transparent 65%
          ) !important;
          -webkit-mask:
            linear-gradient(#fff 0 0) content-box,
            linear-gradient(#fff 0 0) !important;
          -webkit-mask-composite: xor !important;
          mask:
            linear-gradient(#fff 0 0) content-box,
            linear-gradient(#fff 0 0) !important;
          mask-composite: exclude !important;
          pointer-events: none !important;
          opacity: 1 !important;
          transition: opacity 0.3s ease !important;
          z-index: 4 !important;
        }

        html.dark .pricing-card.bento-active::before,
        html[data-theme="dark"] .pricing-card.bento-active::before {
          background: radial-gradient(
            var(--bento-radius) circle at var(--bento-glow-x) var(--bento-glow-y),
            rgba(var(--bento-color-dark), calc(var(--bento-glow-intensity) * 0.35)) 0%,
            rgba(var(--bento-color-dark), calc(var(--bento-glow-intensity) * 0.12)) 35%,
            transparent 65%
          ) !important;
        }

        /* Subtle dark elevation on hover */
        .pricing-card.bento-active:hover {
          box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.08), 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        }

        html.dark .pricing-card.bento-active:hover,
        html[data-theme="dark"] .pricing-card.bento-active:hover {
          box-shadow: 0 18px 40px -10px rgba(0, 0, 0, 0.45), 0 0 25px rgba(255, 255, 255, 0.03) !important;
        }

        /* Tactile ripple on click */
        .bento-ripple-el {
          position: absolute;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(45, 52, 65, 0.22) 0%, rgba(45, 52, 65, 0.08) 35%, transparent 70%);
          pointer-events: none;
          z-index: 10;
          transform: translate(-50%, -50%) scale(0);
          animation: bento-ripple-expand 0.65s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        html.dark .bento-ripple-el,
        html[data-theme="dark"] .bento-ripple-el {
          background: radial-gradient(circle, rgba(140, 150, 165, 0.25) 0%, rgba(140, 150, 165, 0.08) 35%, transparent 70%);
        }

        @keyframes bento-ripple-expand {
          to {
            transform: translate(-50%, -50%) scale(2.2);
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }

    var isFinePointer = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;

    cards.forEach(function(card) {
      if (card.classList.contains('bento-active')) return;
      card.classList.add('bento-active');

      if (!isFinePointer) return;

      var maxTilt = 3.5;
      var maxMagnet = 2.5;
      var rafId = null;

      function onMouseMove(e) {
        if (rafId) cancelAnimationFrame(rafId);
        rafId = requestAnimationFrame(function() {
          var rect = card.getBoundingClientRect();
          var x = e.clientX - rect.left;
          var y = e.clientY - rect.top;
          var centerX = rect.width / 2;
          var centerY = rect.height / 2;

          // 3D Tilt: Subtle calibrated angles
          var rotateX = ((y - centerY) / centerY) * -maxTilt;
          var rotateY = ((x - centerX) / centerX) * maxTilt;

          // Subtle Magnetism
          var magnetX = ((x - centerX) / centerX) * maxMagnet;
          var magnetY = ((y - centerY) / centerY) * maxMagnet;

          card.style.transform =
            'perspective(1000px) rotateX(' +
            rotateX.toFixed(2) +
            'deg) rotateY(' +
            rotateY.toFixed(2) +
            'deg) translate(' +
            magnetX.toFixed(1) +
            'px, ' +
            (magnetY - 4).toFixed(1) +
            'px)';
          card.style.setProperty('--bento-glow-x', ((x / rect.width) * 100).toFixed(1) + '%');
          card.style.setProperty('--bento-glow-y', ((y / rect.height) * 100).toFixed(1) + '%');
          card.style.setProperty('--bento-glow-intensity', '1');
        });
      }

      function onMouseLeave() {
        if (rafId) cancelAnimationFrame(rafId);
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translate(0px, 0px)';
        card.style.setProperty('--bento-glow-intensity', '0');
      }

      function onClick(e) {
        // Don't intercept button or link clicks
        if (e.target.closest('button, a, input')) return;
        var rect = card.getBoundingClientRect();
        var ripple = document.createElement('span');
        ripple.className = 'bento-ripple-el';
        var size = Math.max(rect.width, rect.height) * 1.6;
        ripple.style.width = size + 'px';
        ripple.style.height = size + 'px';
        ripple.style.left = (e.clientX - rect.left) + 'px';
        ripple.style.top = (e.clientY - rect.top) + 'px';
        card.appendChild(ripple);
        setTimeout(function() {
          if (ripple && ripple.parentNode) ripple.parentNode.removeChild(ripple);
        }, 700);
      }

      card.addEventListener('mousemove', onMouseMove, { passive: true });
      card.addEventListener('mouseleave', onMouseLeave, { passive: true });
      card.addEventListener('click', onClick, { passive: true });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setup);
  } else {
    setup();
  }
})();
