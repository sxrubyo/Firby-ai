/**
 * Firby AI — Unified Theme Controller
 * Detecta, aplica y sincroniza el modo oscuro en todas las páginas.
 */
(function() {
  'use strict';

  function getStoredTheme() {
    try {
      var saved = localStorage.getItem('theme_v4');
      if (saved === 'dark') return 'dark';
      if (saved === 'light') return 'light';
    } catch (_) {}
    return 'light';
  }

  function applyTheme(theme) {
    var isDark = (theme === 'dark');
    if (isDark) {
      document.documentElement.classList.add('dark');
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.setAttribute('data-theme', 'light');
    }
    try {
      localStorage.setItem('theme_v4', theme);
      localStorage.setItem('theme_v3', theme);
      localStorage.setItem('theme_v2', theme);
      localStorage.setItem('theme', theme);
    } catch (_) {}
  }

  // 1. Aplicación inmediata síncrona para evitar cualquier flash blanco
  var currentTheme = getStoredTheme();
  applyTheme(currentTheme);

  // 2. Vincular listeners a los botones de toggle una vez cargado el DOM
  function bindToggleButtons() {
    var buttons = document.querySelectorAll('#theme-toggle-btn, .theme-toggle-btn, .nav-theme-toggle-btn');
    buttons.forEach(function(btn) {
      if (btn._themeBound) return;
      btn._themeBound = true;
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        var next = document.documentElement.classList.contains('dark') ? 'light' : 'dark';
        applyTheme(next);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindToggleButtons);
  } else {
    bindToggleButtons();
  }
})();
