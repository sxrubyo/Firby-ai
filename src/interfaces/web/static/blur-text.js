/**
 * BlurText Runtime - React Bits
 * Replicates <BlurText /> component behavior for HTML elements:
 * - Word or letter tokenization
 * - Progressive blur + opacity + translate reveal
 * - IntersectionObserver activation
 */
(function initBlurText() {
  function setup() {
    var elements = document.querySelectorAll('[data-blur-text="true"]');
    if (!elements || elements.length === 0) return;

    var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    elements.forEach(function (el) {
      if (el.dataset.blurInitialized === "true") return;
      el.dataset.blurInitialized = "true";

      var text = el.textContent ? el.textContent.trim() : "";
      if (!text) return;

      var animateBy = el.getAttribute('data-blur-animate') || 'words';
      var delayMs = parseInt(el.getAttribute('data-blur-delay') || '110', 10);
      var threshold = parseFloat(el.getAttribute('data-blur-threshold') || '0.1');

      var tokens = animateBy === 'letters' ? text.split('') : text.split(/\s+/);

      el.innerHTML = '';
      var container = document.createElement('span');
      container.className = 'blur-text-container';

      var itemSpans = [];

      tokens.forEach(function (token, idx) {
        var item = document.createElement('span');
        item.className = 'blur-text-item';
        item.textContent = token;

        container.appendChild(item);
        itemSpans.push(item);

        if (idx < tokens.length - 1) {
          var space = document.createTextNode('\u00A0');
          container.appendChild(space);
        }
      });

      el.appendChild(container);

      if (reduceMotion) {
        itemSpans.forEach(function (s) { s.classList.add('blur-text-in'); });
        return;
      }

      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            itemSpans.forEach(function (item, idx) {
              setTimeout(function () {
                item.classList.add('blur-text-in');
              }, idx * delayMs);
            });
            observer.unobserve(el);
          }
        });
      }, { threshold: threshold });

      observer.observe(el);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setup);
  } else {
    setup();
  }
})();
