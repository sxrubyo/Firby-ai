/**
 * SplashCursor - Disabled
 * Automatically cleans up any remaining canvas or wrappers from the DOM.
 */
(function cleanupSplashCursor() {
  function cleanup() {
    const oldHeroWrapper = document.querySelector('#hero .splash-cursor-wrapper');
    if (oldHeroWrapper) oldHeroWrapper.remove();
    const oldContainer = document.getElementById('splash-cursor-global-container');
    if (oldContainer) oldContainer.remove();
    document.querySelectorAll('.splash-cursor-section-wrapper').forEach(el => el.remove());
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', cleanup);
  } else {
    cleanup();
  }
})();
