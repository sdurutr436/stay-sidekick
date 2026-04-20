'use strict';

/**
 * header-auth.js
 * Detecta si el usuario tiene sesión activa (JWT en localStorage)
 * y reemplaza el botón de "Iniciar sesión" por el enlace "Perfil".
 */
(function () {
  var TOKEN_KEY  = 'ss_token';
  var PERFIL_URL = '/app/menu/perfil';

  function isTokenValid(token) {
    try {
      var payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp > Date.now() / 1000;
    } catch (_) {
      return false;
    }
  }

  function swapLoginButton() {
    var token = localStorage.getItem(TOKEN_KEY);
    if (!token || !isTokenValid(token)) return;

    var loginLink = document.querySelector('.header__actions a[href="/login"]');
    if (!loginLink) return;

    var perfilLink = document.createElement('a');
    perfilLink.href      = PERFIL_URL;
    perfilLink.className = loginLink.className;
    perfilLink.textContent = 'Perfil';
    loginLink.parentNode.replaceChild(perfilLink, loginLink);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', swapLoginButton);
  } else {
    swapLoginButton();
  }
}());
