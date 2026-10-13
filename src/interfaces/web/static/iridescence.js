/**
 * Iridescence Shader Runtime - Disabled
 * Cleans up any remaining canvas and styles.
 */
(function cleanupIridescence() {
  function cleanup() {
    var ctaCard = document.querySelector('.cta-final-card, #contacto .cta-final-card');
    if (ctaCard) {
      var canvases = ctaCard.querySelectorAll('.iridescence-canvas');
      canvases.forEach(function(c) { c.remove(); });
    }
    var style = document.getElementById('iridescence-css');
    if (style) style.remove();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', cleanup);
  } else {
    cleanup();
  }
})();
