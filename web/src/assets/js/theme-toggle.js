'use strict';

/**
 * theme-toggle.js
 * Implementa el toggle de tema (light/dark) para el sitio 11ty.
 * - Persiste la preferencia en localStorage bajo la clave 'theme'.
 * - Respeta prefers-color-scheme cuando no hay preferencia guardada.
 * - Mantiene paridad de comportamiento con Angular ThemeService.
 *
 * Nota: el script inline en <head> ya aplica el tema antes del renderizado
 * para evitar FOUC. Aquí solo conectamos el botón y mantenemos el icono.
 */
(function () {
  var STORAGE_KEY = 'theme';

  function currentTheme() {
    var stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'light' || stored === 'dark') return stored;
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  function applyTheme(theme) {
    var root = document.documentElement;
    root.classList.toggle('dark', theme === 'dark');
    root.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }

  function updateButtonIcon(button, theme) {
    var sun = button.querySelector('[data-theme-icon="sun"]');
    var moon = button.querySelector('[data-theme-icon="moon"]');
    if (sun)  sun.style.display  = theme === 'dark' ? 'inline-flex' : 'none';
    if (moon) moon.style.display = theme === 'dark' ? 'none' : 'inline-flex';
    button.setAttribute(
      'aria-label',
      theme === 'dark' ? 'Activar modo claro' : 'Activar modo oscuro'
    );
  }

  function init() {
    var button = document.querySelector('[data-theme-toggle]');
    if (!button) return;

    updateButtonIcon(button, currentTheme());

    button.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      updateButtonIcon(button, next);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
