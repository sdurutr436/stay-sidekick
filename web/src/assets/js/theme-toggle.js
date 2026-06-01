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

  /**
   * Resuelve el tema vigente con la siguiente prioridad:
   *   1. Valor guardado en localStorage['theme'] (si es 'light' o 'dark').
   *   2. Preferencia del SO vía matchMedia('prefers-color-scheme').
   *   3. Fallback a 'light'.
   * @returns {'light'|'dark'}
   */
  function currentTheme() {
    var stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'light' || stored === 'dark') return stored;
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  /**
   * Aplica un tema al <html> (clase `.dark` + atributo `data-theme`) y lo
   * persiste en localStorage. La persistencia dispara el evento `storage`
   * en otras pestañas/apps del mismo origen para mantenerlas sincronizadas.
   * @param {'light'|'dark'} theme
   */
  function applyTheme(theme) {
    var root = document.documentElement;
    root.classList.toggle('dark', theme === 'dark');
    root.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }

  /**
   * Sincroniza el icono y el `aria-label` del botón con el tema activo.
   * El sol se ve en modo oscuro (acción: pasar a claro) y viceversa.
   * @param {HTMLElement}     button Botón del toggle (`[data-theme-toggle]`).
   * @param {'light'|'dark'}  theme  Tema actualmente aplicado.
   */
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

    if (button) {
      updateButtonIcon(button, currentTheme());
      button.addEventListener('click', function () {
        var next = currentTheme() === 'dark' ? 'light' : 'dark';
        applyTheme(next);
        updateButtonIcon(button, next);
      });
    }

    // Sincronización entre pestañas/apps del mismo origen (11ty ↔ Angular).
    // 'storage' solo se dispara en pestañas DISTINTAS a la que escribió, por
    // lo que reflejamos el cambio sin generar bucles.
    window.addEventListener('storage', function (event) {
      if (event.key !== STORAGE_KEY) return;
      var next = event.newValue === 'dark' ? 'dark' : 'light';
      var root = document.documentElement;
      root.classList.toggle('dark', next === 'dark');
      root.setAttribute('data-theme', next);
      if (button) updateButtonIcon(button, next);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
