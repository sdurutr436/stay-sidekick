/**
 * form-solicitud.js
 * Sanitización defensiva, validación, construcción del payload y envío.
 *
 * Capas:
 *   1. Sanitización  — limpieza de strings antes de cualquier operación
 *   2. Validación    — reglas de negocio por campo
 *   3. Payload       — construcción del objeto JSON limpio
 *   4. Transporte    — fetch con CSRF token + JWT opcional
 *
 * La sanitización en cliente NO sustituye la del backend; es una primera
 * línea de defensa y garantía de que el payload llega bien formado.
 */

'use strict';

// =============================================================================
// 1. SANITIZACIÓN
// =============================================================================

/**
 * Elimina todas las etiquetas HTML/XML del string.
 * Previene inyección de markup en los campos de texto.
 */
function stripTags(str) {
  return String(str).replace(/<[^>]*>/g, '');
}

/**
 * Elimina caracteres de control (U+0000–U+001F, U+007F) excepto
 * tabulación (\x09) y salto de línea (\x0A, \x0D) para el textarea.
 */
function stripControlChars(str, keepNewlines) {
  if (keepNewlines) {
    return str.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
  }
  return str.replace(/[\x00-\x1F\x7F]/g, '');
}

/** Trim + colapsa múltiples espacios en uno. */
function normalizeWs(str) {
  return str.trim().replace(/[ \t]{2,}/g, ' ');
}

/** Sanitización para campos de texto cortos (nombre, empresa…). */
function sanitizeText(str, maxLen) {
  return normalizeWs(stripControlChars(stripTags(str), false)).slice(0, maxLen);
}

/**
 * Sanitización de email: strip tags, control chars, lowercase, sin espacios.
 * RFC 5321 limita a 254 caracteres.
 */
function sanitizeEmail(str) {
  return stripControlChars(stripTags(str), false)
    .trim()
    .toLowerCase()
    .replace(/\s/g, '')
    .slice(0, 254);
}

/**
 * Sanitización de teléfono: solo dígitos, +, espacios, guiones y paréntesis.
 * Elimina cualquier otro carácter.
 */
function sanitizePhone(str) {
  return stripControlChars(stripTags(str), false)
    .replace(/[^\d\s+\-().]/g, '')
    .trim()
    .slice(0, 20);
}

/**
 * Sanitización para el textarea largo.
 * Conserva saltos de línea (\n) pero elimina etiquetas y control chars.
 */
function sanitizeTextarea(str, maxLen) {
  return stripControlChars(stripTags(str), true).trim().slice(0, maxLen);
}

/**
 * Comprueba que el valor de un radio/select pertenece a la lista blanca.
 * Devuelve el valor si es válido, null si no.
 */
function whitelistEnum(val, allowed) {
  return allowed.includes(val) ? val : null;
}

// =============================================================================
// 2. VALIDACIÓN
// =============================================================================

const _EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
// Teléfono: 7-15 dígitos con separadores opcionales (formato internacional E.164 o local)
const _PHONE_RE = /^\+?[\d][\d\s\-().]{5,18}[\d]$/;

const validators = {
  nombre(val) {
    if (!val)          return 'El nombre de la empresa es obligatorio.';
    if (val.length < 2) return 'El nombre debe tener al menos 2 caracteres.';
    return null;
  },

  correo(val) {
    if (!val)                 return 'El correo de contacto es obligatorio.';
    if (!_EMAIL_RE.test(val)) return 'Introduce un correo electrónico válido.';
    return null;
  },

  telefono(val) {
    if (!val)                 return 'El teléfono de contacto es obligatorio.';
    if (!_PHONE_RE.test(val)) return 'Introduce un teléfono válido (mínimo 7 dígitos).';
    return null;
  },

  tipo(val) {
    if (!val) return 'Selecciona el tipo de solicitud.';
    return null;
  },

  detalle(val, isBeneficiario) {
    if (!isBeneficiario) return null;
    if (!val)            return 'Describe tu situación para que podamos ayudarte.';
    if (val.length < 20) return 'El mensaje debe tener al menos 20 caracteres.';
    return null;
  },

  terminos(checked) {
    if (!checked) return 'Debes aceptar los términos y condiciones para continuar.';
    return null;
  },
};

// =============================================================================
// 3. GESTIÓN DE ERRORES EN UI
// =============================================================================

function _getField(input) {
  return input.closest('.form-field');
}

function clearFieldError(input) {
  const field = _getField(input);
  if (!field) return;
  field.classList.remove('form-field--error');
  field.querySelector('.form-field__error')?.remove();
}

function showFieldError(input, message) {
  const field = _getField(input);
  if (!field) return;
  clearFieldError(input);
  field.classList.add('form-field--error');
  const msg = document.createElement('p');
  msg.className = 'form-field__error';
  msg.setAttribute('role', 'alert');
  msg.textContent = message;
  field.appendChild(msg);
}

function clearGroupError(group) {
  group.classList.remove('form-group--error');
  group.querySelector('.form-group__error')?.remove();
}

function showGroupError(group, message) {
  clearGroupError(group);
  group.classList.add('form-group--error');
  const msg = document.createElement('p');
  msg.className = 'form-group__error';
  msg.setAttribute('role', 'alert');
  msg.textContent = message;
  group.appendChild(msg);
}

function clearAllErrors(form) {
  form.querySelectorAll('.form-field--error').forEach(el => el.classList.remove('form-field--error'));
  form.querySelectorAll('.form-field__error').forEach(el => el.remove());
  form.querySelectorAll('.form-group--error').forEach(el => el.classList.remove('form-group--error'));
  form.querySelectorAll('.form-group__error').forEach(el => el.remove());
}

// =============================================================================
// 4. CSRF + JWT
// =============================================================================

/**
 * Obtiene el token CSRF del backend.
 * El backend expone GET /api/csrf-token → { csrf_token: "..." }
 */
async function fetchCsrfToken() {
  try {
    const res = await fetch('/api/csrf-token', {
      method: 'GET',
      credentials: 'same-origin',
      headers: { 'Accept': 'application/json' },
    });
    if (!res.ok) return null;
    const data = await res.json();
    return (typeof data.csrf_token === 'string' && data.csrf_token) ? data.csrf_token : null;
  } catch {
    return null;
  }
}

/**
 * Lee el JWT almacenado por la app Angular tras el login.
 * Clave: 'ss_token' en localStorage del mismo origen.
 */
function getJwt() {
  try {
    const token = localStorage.getItem('ss_token');
    // Validación mínima de estructura JWT (tres segmentos base64url)
    if (token && /^[\w-]+\.[\w-]+\.[\w-]+$/.test(token)) return token;
    return null;
  } catch {
    return null;
  }
}

// =============================================================================
// 5. CONSTRUCCIÓN DEL PAYLOAD
// =============================================================================

/**
 * Construye el objeto JSON limpio listo para enviar al backend.
 * Campo solicitud_detalle solo incluido si tipo === 'beneficiario'.
 *
 * @param {{ nombre, correo, telefono, tipo, detalle }} fields
 * @returns {object}
 */
function buildPayload(fields) {
  const isBeneficiario = fields.tipo === 'beneficiario';
  return {
    empresa_nombre:    fields.nombre,
    empresa_correo:    fields.correo,
    empresa_telefono:  fields.telefono,
    tipo_solicitud:    fields.tipo,
    solicitud_detalle: isBeneficiario ? (fields.detalle || null) : null,
    acepta_terminos:   true,
    origen:            'web',
  };
}

// =============================================================================
// 6. TRANSPORTE
// =============================================================================

/**
 * Envía el payload al backend.
 * Incluye CSRF token en cabecera X-CSRF-Token y JWT en Authorization si
 * está disponible.
 *
 * @param {object} payload
 * @param {string|null} csrfToken
 * @param {string|null} jwt
 */
async function submitPayload(payload, csrfToken, jwt) {
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  if (csrfToken) headers['X-CSRF-Token'] = csrfToken;
  if (jwt)       headers['Authorization'] = `Bearer ${jwt}`;

  const res = await fetch('/api/solicitud', {
    method: 'POST',
    credentials: 'same-origin',
    headers,
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    let errMsg = `Error ${res.status}`;
    try {
      const errBody = await res.json();
      if (errBody.message) errMsg = errBody.message;
    } catch { /* noop */ }
    throw new Error(errMsg);
  }

  return res.json();
}

// =============================================================================
// 7. INICIALIZACIÓN
// =============================================================================

(function init() {
  const form = document.getElementById('form-solicitud');
  if (!form) return;

  const conditional = document.getElementById('solicitud-mensaje');

  // ── Toggle del área condicional (beneficiario) ──────────────────────────
  form.querySelectorAll('input[name="tipo_solicitud"]').forEach(function (radio) {
    radio.addEventListener('change', function () {
      const visible = this.value === 'beneficiario';
      conditional.classList.toggle('form-solicitud__conditional--visible', visible);
      conditional.setAttribute('aria-hidden', String(!visible));
    });
  });

  // ── Validación en blur (feedback inmediato por campo) ───────────────────
  const inputNombre   = form.querySelector('#empresa-nombre');
  const inputCorreo   = form.querySelector('#empresa-correo');
  const inputTelefono = form.querySelector('#empresa-telefono');

  inputNombre.addEventListener('blur', function () {
    const val = sanitizeText(this.value, 200);
    const err = validators.nombre(val);
    err ? showFieldError(this, err) : clearFieldError(this);
  });

  inputCorreo.addEventListener('blur', function () {
    const val = sanitizeEmail(this.value);
    const err = validators.correo(val);
    err ? showFieldError(this, err) : clearFieldError(this);
  });

  inputTelefono.addEventListener('blur', function () {
    const val = sanitizePhone(this.value);
    const err = validators.telefono(val);
    err ? showFieldError(this, err) : clearFieldError(this);
  });

  // ── Submit ──────────────────────────────────────────────────────────────
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    clearAllErrors(form);

    // 1 — Sanitizar
    const nombre   = sanitizeText(inputNombre.value, 200);
    const correo   = sanitizeEmail(inputCorreo.value);
    const telefono = sanitizePhone(inputTelefono.value);
    const tipoEl   = form.querySelector('input[name="tipo_solicitud"]:checked');
    const tipoRaw  = tipoEl ? tipoEl.value : '';
    const tipo     = whitelistEnum(tipoRaw, ['beneficiario', 'empresa']);
    const detalle  = sanitizeTextarea(
      form.querySelector('#solicitud-detalle')?.value ?? '', 5000
    );
    const terminos = form.querySelector('#acepta-terminos').checked;

    // 2 — Validar (acumula todos los errores antes de mostrar)
    let hasErrors = false;

    const errNombre = validators.nombre(nombre);
    if (errNombre) { showFieldError(inputNombre, errNombre); hasErrors = true; }

    const errCorreo = validators.correo(correo);
    if (errCorreo) { showFieldError(inputCorreo, errCorreo); hasErrors = true; }

    const errTelefono = validators.telefono(telefono);
    if (errTelefono) { showFieldError(inputTelefono, errTelefono); hasErrors = true; }

    const errTipo = validators.tipo(tipo);
    if (errTipo) {
      const radioGroup = form.querySelector('[role="radiogroup"]');
      if (radioGroup) showGroupError(radioGroup, errTipo);
      hasErrors = true;
    }

    const errDetalle = validators.detalle(detalle, tipo === 'beneficiario');
    if (errDetalle) {
      const textareaEl = form.querySelector('#solicitud-detalle');
      if (textareaEl) showFieldError(textareaEl, errDetalle);
      hasErrors = true;
    }

    const errTerminos = validators.terminos(terminos);
    if (errTerminos) {
      showFieldError(form.querySelector('#acepta-terminos'), errTerminos);
      hasErrors = true;
    }

    if (hasErrors) {
      const firstErrInput = form.querySelector(
        '.form-field--error input, .form-field--error textarea, .form-group--error input'
      );
      firstErrInput?.focus();
      return;
    }

    // 3 — Obtener CSRF y JWT en paralelo
    const [csrfToken, jwt] = await Promise.all([
      fetchCsrfToken(),
      Promise.resolve(getJwt()),
    ]);

    // 4 — Construir payload
    const payload = buildPayload({ nombre, correo, telefono, tipo, detalle });

    // 5 — Enviar
    const submitBtn = form.querySelector('[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Enviando…';

    try {
      await submitPayload(payload, csrfToken, jwt);
      form.reset();
      conditional.classList.remove('form-solicitud__conditional--visible');
      conditional.setAttribute('aria-hidden', 'true');
      // TODO: mostrar mensaje de confirmación en lugar de alert
    } catch (err) {
      // TODO: sustituir por un mensaje en UI cuando se implemente el estado global
      console.error('[form-solicitud] Error al enviar:', err.message);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Enviar formulario';
    }
  });
}());
