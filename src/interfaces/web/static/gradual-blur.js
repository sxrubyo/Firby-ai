/**
 * GradualBlur - Stacked progressive blur layers from React Bits
 * Adapted for Firby Landing Page scroll dynamics.
 */
(function initGradualBlur() {
  const CURVE_FUNCTIONS = {
    linear: p => p,
    bezier: p => p * p * (3 - 2 * p),
    'ease-in': p => p * p,
    'ease-out': p => 1 - Math.pow(1 - p, 2),
    'ease-in-out': p => (p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2)
  };

  const getGradientDirection = position =>
    ({
      top: 'to top',
      bottom: 'to bottom',
      left: 'to left',
      right: 'to right'
    })[position] || 'to bottom';

  function createGradualBlurElement(options = {}) {
    const config = Object.assign(
      {
        position: 'bottom',
        strength: 2,
        height: '6rem',
        divCount: 5,
        exponential: true,
        curve: 'bezier',
        opacity: 1,
        target: 'page', // 'page' or 'parent'
        zIndex: 40,
        className: ''
      },
      options
    );

    const container = document.createElement('div');
    container.className = `gradual-blur ${config.target === 'page' ? 'gradual-blur-fixed' : 'gradual-blur-parent'} ${config.className}`;
    container.style.position = config.target === 'page' ? 'fixed' : 'absolute';
    container.style.pointerEvents = 'none';
    container.style.zIndex = String(config.zIndex);
    container.style.opacity = '1';
    container.style.transition = 'opacity 0.4s ease-out';

    if (config.position === 'bottom') {
      container.style.bottom = '0';
      container.style.left = '0';
      container.style.right = '0';
      container.style.height = config.height;
    } else if (config.position === 'top') {
      container.style.top = '0';
      container.style.left = '0';
      container.style.right = '0';
      container.style.height = config.height;
    }

    const inner = document.createElement('div');
    inner.className = 'gradual-blur-inner';
    inner.style.position = 'relative';
    inner.style.width = '100%';
    inner.style.height = '100%';

    const increment = 100 / config.divCount;
    const curveFunc = CURVE_FUNCTIONS[config.curve] || CURVE_FUNCTIONS.linear;
    const direction = getGradientDirection(config.position);

    for (let i = 1; i <= config.divCount; i++) {
      let progress = i / config.divCount;
      progress = curveFunc(progress);

      let blurValue;
      if (config.exponential) {
        blurValue = Math.pow(2, progress * 4) * 0.0625 * config.strength;
      } else {
        blurValue = 0.0625 * (progress * config.divCount + 1) * config.strength;
      }

      const p1 = Math.round((increment * i - increment) * 10) / 10;
      const p2 = Math.round(increment * i * 10) / 10;
      const p3 = Math.round((increment * i + increment) * 10) / 10;
      const p4 = Math.round((increment * i + increment * 2) * 10) / 10;

      let gradient = `transparent ${p1}%, black ${p2}%`;
      if (p3 <= 100) gradient += `, black ${p3}%`;
      if (p4 <= 100) gradient += `, transparent ${p4}%`;

      const div = document.createElement('div');
      div.style.position = 'absolute';
      div.style.inset = '0';
      div.style.maskImage = `linear-gradient(${direction}, ${gradient})`;
      div.style.webkitMaskImage = `linear-gradient(${direction}, ${gradient})`;
      div.style.backdropFilter = `blur(${blurValue.toFixed(3)}rem)`;
      div.style.webkitBackdropFilter = `blur(${blurValue.toFixed(3)}rem)`;
      div.style.opacity = String(config.opacity);

      inner.appendChild(div);
    }

    container.appendChild(inner);
    return container;
  }

  function start() {
    // Evitar duplicados
    const existing = document.getElementById('firby-landing-gradual-blur');
    if (existing) existing.remove();

    // Crear GradualBlur para scroll de la landing
    const blurElement = createGradualBlurElement({
      position: 'bottom',
      height: '6.5rem',
      strength: 2.2,
      divCount: 5,
      curve: 'bezier',
      exponential: true,
      opacity: 1,
      target: 'page',
      zIndex: 35
    });
    blurElement.id = 'firby-landing-gradual-blur';
    document.body.appendChild(blurElement);

    // Ocultar al llegar a los planes (#planes) y viñetas finales (#experiencia-conversacional, #contacto)
    const planesSection = document.getElementById('planes');
    
    function updateVisibility() {
      if (!planesSection) return;
      const rect = planesSection.getBoundingClientRect();
      const windowHeight = window.innerHeight || document.documentElement.clientHeight;

      // Si la sección de planes entra en el viewport (o el usuario llega abajo a las viñetas finales)
      if (rect.top <= windowHeight * 0.85) {
        blurElement.style.opacity = '0';
      } else {
        blurElement.style.opacity = '1';
      }
    }

    window.addEventListener('scroll', updateVisibility, { passive: true });
    window.addEventListener('resize', updateVisibility, { passive: true });
    updateVisibility();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
