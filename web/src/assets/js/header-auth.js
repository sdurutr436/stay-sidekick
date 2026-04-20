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

  function isTokenValid(token) {
    try {
      var payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp > Date.now() / 1000;
    } catch (_) {
      return false;
    }
  }

  function swapHeader() {
    var token = localStorage.getItem(TOKEN_KEY);
    if (!token || !isTokenValid(token)) return;

    // Swap "Iniciar sesión" → "Perfil"
    var loginLink = document.querySelector('.header__actions a[href="/login"]');
    if (loginLink) {
      var perfilLink = document.createElement('a');
      perfilLink.href        = PERFIL_URL;
      perfilLink.className   = loginLink.className;
      perfilLink.textContent = 'Perfil';
      loginLink.parentNode.replaceChild(perfilLink, loginLink);
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
