/**
 * BorderGlow Runtime - React Bits
 * Integrates interactive dynamic border glow on target elements:
 * "El costo real de depender solo de atención manual" (4 spotlight cards)
 */

(function initBorderGlow() {
  function parseHSL(hslStr) {
    var match = hslStr.match(/([\d.]+)\s*([\d.]+)%?\s*([\d.]+)%?/);
    if (!match) return { h: 40, s: 80, l: 80 };
    return { h: parseFloat(match[1]), s: parseFloat(match[2]), l: parseFloat(match[3]) };
  }

  function buildGlowVars(glowColor, intensity) {
    var parsed = parseHSL(glowColor);
    var base = parsed.h + "deg " + parsed.s + "% " + parsed.l + "%";
    var opacities = [100, 60, 50, 40, 30, 20, 10];
    var keys = ['', '-60', '-50', '-40', '-30', '-20', '-10'];
    var vars = {};
    for (var i = 0; i < opacities.length; i++) {
      vars['--glow-color' + keys[i]] = 'hsl(' + base + ' / ' + Math.min(opacities[i] * intensity, 100) + '%)';
    }
    return vars;
  }

  var GRADIENT_POSITIONS = ['80% 55%', '69% 34%', '8% 6%', '41% 38%', '86% 85%', '82% 18%', '51% 4%'];
  var GRADIENT_KEYS = ['--gradient-one', '--gradient-two', '--gradient-three', '--gradient-four', '--gradient-five', '--gradient-six', '--gradient-seven'];
  var COLOR_MAP = [0, 1, 2, 0, 1, 2, 1];

  function buildGradientVars(colors) {
    var vars = {};
    for (var i = 0; i < 7; i++) {
      var c = colors[Math.min(COLOR_MAP[i], colors.length - 1)];
      vars[GRADIENT_KEYS[i]] = 'radial-gradient(at ' + GRADIENT_POSITIONS[i] + ', ' + c + ' 0px, transparent 50%)';
    }
    vars['--gradient-base'] = 'linear-gradient(' + colors[0] + ' 0 100%)';
    return vars;
  }

  function isLightColor(color) {
    var value = color.trim().replace('#', '');
    if (!/^[\da-f]{3}([\da-f]{3})?$/i.test(value)) return false;
    var hex = value.length === 3 ? value.split('').map(function (c) { return c + c; }).join('') : value;
    var red = parseInt(hex.slice(0, 2), 16);
    var green = parseInt(hex.slice(2, 4), 16);
    var blue = parseInt(hex.slice(4, 6), 16);
    return red * 0.2126 + green * 0.7152 + blue * 0.0722 > 180;
  }

  var THEME_CARD_PALETTES = {
    'card-emerald': {
      colors: ['#34d399', '#b9fa01', '#2dd4bf'],
      glowColor: '150 85 70'
    },
    'card-blue': {
      colors: ['#38bdf8', '#60a5fa', '#818cf8'],
      glowColor: '215 85 75'
    },
    'card-purple': {
      colors: ['#c084fc', '#f472b6', '#e879f9'],
      glowColor: '285 85 75'
    },
    'card-amber': {
      colors: ['#fbbf24', '#f97316', '#facc15'],
      glowColor: '40 90 70'
    }
  };

  function setupCard(card) {
    if (card.dataset.borderGlowReady) return;
    card.dataset.borderGlowReady = 'true';

    card.classList.add('border-glow-card');

    // Detect theme palette from classes
    var palette = {
      colors: ['#c084fc', '#f472b6', '#38bdf8'],
      glowColor: '40 80 80'
    };

    if (card.classList.contains('card-emerald')) palette = THEME_CARD_PALETTES['card-emerald'];
    else if (card.classList.contains('card-blue')) palette = THEME_CARD_PALETTES['card-blue'];
    else if (card.classList.contains('card-purple')) palette = THEME_CARD_PALETTES['card-purple'];
    else if (card.classList.contains('card-amber')) palette = THEME_CARD_PALETTES['card-amber'];

    var isDark = document.documentElement.classList.contains('dark') || document.documentElement.getAttribute('data-theme') === 'dark';
    var bg = isDark ? '#161b22' : '#ffffff';

    if (isLightColor(bg)) {
      card.classList.add('border-glow-card--light');
    } else {
      card.classList.remove('border-glow-card--light');
    }

    // Set configuration variables
    card.style.setProperty('--card-bg', bg);
    card.style.setProperty('--edge-sensitivity', '30');
    card.style.setProperty('--border-radius', '24px');
    card.style.setProperty('--glow-padding', '38px');
    card.style.setProperty('--cone-spread', '25');
    card.style.setProperty('--fill-opacity', '0.45');

    var glowVars = buildGlowVars(palette.glowColor, 1.0);
    for (var k in glowVars) {
      card.style.setProperty(k, glowVars[k]);
    }

    var gradVars = buildGradientVars(palette.colors);
    for (var gk in gradVars) {
      card.style.setProperty(gk, gradVars[gk]);
    }

    // Ensure edge-light span exists
    if (!card.querySelector('.edge-light')) {
      var edgeLight = document.createElement('span');
      edgeLight.className = 'edge-light';
      card.insertBefore(edgeLight, card.firstChild);
    }

    // Ensure inner content wrapper
    var content = card.querySelector('.spotlight-card-content');
    if (content && !content.classList.contains('border-glow-inner')) {
      content.classList.add('border-glow-inner');
    }

    // Math geometry handlers
    function getCenter(el) {
      var rect = el.getBoundingClientRect();
      return [rect.width / 2, rect.height / 2];
    }

    function getEdgeProximity(el, x, y) {
      var c = getCenter(el);
      var dx = x - c[0];
      var dy = y - c[1];
      var kx = Infinity;
      var ky = Infinity;
      if (dx !== 0) kx = c[0] / Math.abs(dx);
      if (dy !== 0) ky = c[1] / Math.abs(dy);
      return Math.min(Math.max(1 / Math.min(kx, ky), 0), 1);
    }

    function getCursorAngle(el, x, y) {
      var c = getCenter(el);
      var dx = x - c[0];
      var dy = y - c[1];
      if (dx === 0 && dy === 0) return 0;
      var rad = Math.atan2(dy, dx);
      var deg = rad * (180 / Math.PI) + 90;
      if (deg < 0) deg += 360;
      return deg;
    }

    card.addEventListener('pointermove', function (e) {
      var rect = card.getBoundingClientRect();
      var x = e.clientX - rect.left;
      var y = e.clientY - rect.top;

      var edge = getEdgeProximity(card, x, y);
      var angle = getCursorAngle(card, x, y);

      card.style.setProperty('--edge-proximity', (edge * 100).toFixed(3));
      card.style.setProperty('--cursor-angle', angle.toFixed(3) + 'deg');
    }, { passive: true });

    card.addEventListener('pointerleave', function () {
      card.style.setProperty('--edge-proximity', '0');
    });
  }

  function start() {
    var cards = document.querySelectorAll('#sub-costo-oculto .problem-spotlight-card, [data-border-glow="true"]');
    cards.forEach(setupCard);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }

  // Theme observer
  var observer = new MutationObserver(function () {
    var cards = document.querySelectorAll('.border-glow-card');
    var isDark = document.documentElement.classList.contains('dark') || document.documentElement.getAttribute('data-theme') === 'dark';
    var bg = isDark ? '#161b22' : '#ffffff';
    cards.forEach(function (card) {
      card.style.setProperty('--card-bg', bg);
      if (isLightColor(bg)) {
        card.classList.add('border-glow-card--light');
      } else {
        card.classList.remove('border-glow-card--light');
      }
    });
  });

  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme'] });
})();
