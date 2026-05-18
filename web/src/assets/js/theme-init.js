'use strict';

/**
 * theme-init.js — script anti-FOUC.
 *
 * IMPORTANTE: debe cargarse SÍNCRONAMENTE en <head>, antes del CSS, y como
 * archivo externo (NO inline) para cumplir con `Content-Security-Policy:
 * script-src 'self'`. Un inline requeriría incluir su sha256 en la cabecera,
 * algo que se desincroniza al modificar el script.
 *
 * - Lee `localStorage['theme']` o, en su defecto, `prefers-color-scheme`.
 * - Aplica la clase `.dark` y el atributo `data-theme` en <html> antes del
 *   primer paint, evitando el flash de tema incorrecto.
 */
(function () {
  try {
    var stored = localStorage.getItem('theme');
    var theme = (stored === 'light' || stored === 'dark')
      ? stored
      : (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    var root = document.documentElement;
    root.classList.toggle('dark', theme === 'dark');
    root.setAttribute('data-theme', theme);
  } catch (_) { /* no-op */ }
}());
