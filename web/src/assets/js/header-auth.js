'use strict';

/**
 * header-auth.js
 * Detecta si el usuario tiene sesión activa (JWT en localStorage) y:
 *  - Reemplaza "Iniciar sesión" por "Perfil" (→ /menu/perfil)
 *  - Reemplaza el logo (→ /) por un enlace al menú (→ /menu)
 */
(function () {
  var TOKEN_KEY  = 'ss_token';
  var MENU_URL   = '/menu';
  var PERFIL_URL = '/menu/perfil';

  /**
   * Normaliza un path para comparar igual `/login`, `/login/` y `/login//`.
   * Devuelve el path con barras finales eliminadas; conserva `/` raíz.
   * @param {string|null} value
   * @returns {string}
   */
  function normalizePath(value) {
    if (!value) return '/';
    return value.length > 1 ? value.replace(/\/+$/, '') : value;
  }

  /**
   * Valida un JWT de forma LIGERA en cliente: decodifica el payload y
   * comprueba `exp`. NO valida firma — eso es responsabilidad del backend.
   * El propósito aquí es decidir UI (mostrar "Perfil" vs "Iniciar sesión"),
   * no autorizar acceso; cualquier request real al backend lo verificará.
   * @param {string} token
   * @returns {boolean} true si el payload es decodificable y no ha expirado.
   */
  function isTokenValid(token) {
    try {
      var payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp > Date.now() / 1000;
    } catch (_) {
      return false;
    }
  }

  /**
   * Reemplaza el CTA de "Iniciar sesión" por "Perfil" y el logo por enlace al
   * panel cuando hay sesión activa. Si no hay token o está expirado, no hace nada
   * (los enlaces por defecto del Njk apuntan a /login y / respectivamente).
   */
  function swapHeader() {
    var token = localStorage.getItem(TOKEN_KEY);
    if (!token || !isTokenValid(token)) return;

    // Swap "Iniciar sesión" → "Perfil" preservando icono y estructura BEM
    var loginLink = Array.prototype.find.call(
      document.querySelectorAll('.header__actions a[href]'),
      function (link) {
        return normalizePath(link.getAttribute('href')) === '/login';
      }
    );
    if (loginLink) {
      loginLink.setAttribute('href', PERFIL_URL);
      var label = loginLink.querySelector('.btn__label');
      if (label) {
        label.textContent = 'Perfil';
      } else {
        loginLink.textContent = 'Perfil';
      }
    }

    // Swap logo → /menu
    var logoLink = document.querySelector('.header__brand');
    if (logoLink && logoLink.getAttribute('href') === '/') {
      logoLink.setAttribute('href', MENU_URL);
      logoLink.setAttribute('aria-label', logoLink.getAttribute('aria-label').replace('Inicio', 'Menú'));
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', swapHeader);
  } else {
    swapHeader();
  }
}());
