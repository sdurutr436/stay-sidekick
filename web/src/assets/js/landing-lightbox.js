'use strict';

/**
 * landing-lightbox.js
 * Lightbox de la landing: al pulsar una miniatura del showcase, abre la
 * captura en su variante "big" sobre un backdrop con blur. El selector de
 * tema (clase .dark en <html>) gobierna qué <picture> es visible vía CSS,
 * por lo que aquí solo inyectamos ambas (light/dark) en el slot.
 */
(function () {
  var BASE_PATH = '/assets/img/paginas/';

  function buildPictures(folder, name, caption) {
    function pictureFor(variant, modeId) {
      var base = BASE_PATH + folder + '/stay-sidekick-' + name + '-' + variant + '-';
      var webpSet = base + 'small.webp 640w, ' + base + 'medium.webp 1280w, ' + base + 'big.webp 2560w';
      var pngSet  = base + 'small.png 640w, '  + base + 'medium.png 1280w, '  + base + 'big.png 2560w';
      var imgSrc  = base + 'big.png';
      var isLight = modeId === 'light';
      var altAttr = isLight ? caption : '';
      var ariaHidden = isLight ? '' : ' aria-hidden="true"';
      return (
        '<picture class="lightbox__pic lightbox__pic--' + modeId + '">' +
          '<source type="image/webp" srcset="' + webpSet + '">' +
          '<source type="image/png" srcset="'  + pngSet  + '">' +
          '<img src="' + imgSrc + '" alt="' + altAttr + '"' + ariaHidden + ' decoding="async">' +
        '</picture>'
      );
    }
    return pictureFor('light-mode', 'light') + pictureFor('dark', 'dark');
  }

  function init() {
    var lightbox    = document.querySelector('[data-lightbox]');
    if (!lightbox) return;

    var slot        = lightbox.querySelector('[data-lightbox-slot]');
    var captionEl   = lightbox.querySelector('[data-lightbox-caption]');
    var closeBtn    = lightbox.querySelector('[data-lightbox-close]');
    var thumbs      = document.querySelectorAll('[data-tool-thumb]');
    var lastTrigger = null;

    function open(trigger) {
      var folder  = trigger.getAttribute('data-tool-folder');
      var name    = trigger.getAttribute('data-tool-name');
      var caption = trigger.getAttribute('data-tool-caption') || '';

      slot.innerHTML       = buildPictures(folder, name, caption);
      captionEl.textContent = caption;

      lastTrigger = trigger;
      lightbox.hidden = false;
      document.documentElement.classList.add('lightbox-open');
      // Foco al botón de cierre por accesibilidad
      closeBtn.focus();
    }

    function close() {
      lightbox.hidden = true;
      slot.innerHTML = '';
      captionEl.textContent = '';
      document.documentElement.classList.remove('lightbox-open');
      if (lastTrigger && typeof lastTrigger.focus === 'function') {
        lastTrigger.focus();
      }
      lastTrigger = null;
    }

    thumbs.forEach(function (btn) {
      btn.addEventListener('click', function () { open(btn); });
    });

    closeBtn.addEventListener('click', close);

    // Clic fuera del contenido cierra el modal
    lightbox.addEventListener('click', function (event) {
      if (event.target === lightbox) close();
    });

    // Tecla Escape cierra el modal
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && !lightbox.hidden) close();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
