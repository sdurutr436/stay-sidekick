/**
 * password-rules.js
 *
 * Fuente de verdad única para la validación de fortaleza de contraseñas
 * en el sitio estático 11ty. Reflejada en:
 *   - backend/app/auth/password_rules.py
 *   - frontend/src/app/validators/password-strength.validator.ts
 *
 * El máximo de 20 caracteres es SECRETO: el criterio `maxLength` no debe
 * mostrarse en la lista de requisitos hasta que el usuario lo supere.
 */
'use strict';

(function (global) {
  var MIN_LENGTH = 8;
  var MAX_LENGTH = 20;
  var SPECIAL_CHARS = '!@#$%^&*-_=+.,;:?';
  var SPECIAL_RE = /[!@#$%^&*\-_=+.,;:?]/;

  var CRITERIA = [
    { id: 'minLength', label: 'Mínimo ' + MIN_LENGTH + ' caracteres',          test: function (v) { return v.length >= MIN_LENGTH; } },
    { id: 'upper',     label: 'Al menos 1 letra mayúscula',                    test: function (v) { return /[A-Z]/.test(v); } },
    { id: 'lower',     label: 'Al menos 1 letra minúscula',                    test: function (v) { return /[a-z]/.test(v); } },
    { id: 'digit',     label: 'Al menos 1 número',                             test: function (v) { return /\d/.test(v); } },
    { id: 'special',   label: 'Al menos 1 carácter especial (' + SPECIAL_CHARS + ')', test: function (v) { return SPECIAL_RE.test(v); } },
  ];

  // Criterio "maxLength" — oculto hasta que el usuario lo supere.
  var MAX_CRITERION = {
    id: 'maxLength',
    label: 'No superar ' + MAX_LENGTH + ' caracteres',
    test: function (v) { return v.length <= MAX_LENGTH; },
  };

  function validate(pwd) {
    var v = String(pwd == null ? '' : pwd);
    if (!v)               return 'La contraseña es obligatoria.';
    if (v.length < MIN_LENGTH) return 'La contraseña debe tener al menos ' + MIN_LENGTH + ' caracteres.';
    if (v.length > MAX_LENGTH) return 'La contraseña no puede superar los ' + MAX_LENGTH + ' caracteres.';
    if (!/[A-Z]/.test(v)) return 'La contraseña debe contener al menos una letra mayúscula.';
    if (!/[a-z]/.test(v)) return 'La contraseña debe contener al menos una letra minúscula.';
    if (!/\d/.test(v))    return 'La contraseña debe contener al menos un número.';
    if (!SPECIAL_RE.test(v)) return 'La contraseña debe contener al menos un carácter especial.';
    return null;
  }

  global.SS_PASSWORD_RULES = {
    MIN_LENGTH: MIN_LENGTH,
    MAX_LENGTH: MAX_LENGTH,
    CRITERIA: CRITERIA,
    MAX_CRITERION: MAX_CRITERION,
    validate: validate,
  };
}(typeof window !== 'undefined' ? window : globalThis));
