'use strict';

/**
 * cookie-banner.js
 * Muestra el aviso de cookies técnicas la primera vez que el usuario visita
 * el sitio. Una vez aceptado, persiste la decisión en localStorage y no
 * vuelve a aparecer en futuras visitas.
 *
 * No hay tracking ni cookies analíticas — el sitio solo usa la cookie de
 * sesión técnica, por lo que el banner es informativo y no bloqueante.
 */
(function () {
  var STORAGE_KEY = 'cookie-consent';
  var ACCEPTED_VALUE = 'accepted';

  function alreadyAccepted() {
    try {
      return localStorage.getItem(STORAGE_KEY) === ACCEPTED_VALUE;
    } catch (e) {
      // localStorage puede no estar disponible (modo privado restrictivo).
      // En ese caso simplemente no mostramos el banner para no molestar.
      return true;
    }
  }

  function accept() {
    try {
      localStorage.setItem(STORAGE_KEY, ACCEPTED_VALUE);
    } catch (e) {
      // Si no se puede persistir, al menos lo ocultamos en esta sesión.
    }
  }

  function init() {
    var banner = document.querySelector('[data-cookie-banner]');
    if (!banner) return;

    if (alreadyAccepted()) {
      banner.remove();
      return;
    }

    banner.hidden = false;

    var acceptBtn = banner.querySelector('[data-cookie-banner-accept]');
    if (acceptBtn) {
      acceptBtn.addEventListener('click', function () {
        accept();
        banner.remove();
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
